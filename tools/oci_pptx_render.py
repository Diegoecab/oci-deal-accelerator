#!/usr/bin/env python3
"""
Rasterize native OCI PPTX slides without LibreOffice.

This renderer supports the subset emitted by `tools/oci_pptx_diagram_gen.py`
plus the OCI icon groups cloned from `OCI_Icons.pptx`. It is purposely scoped
to benchmark/editable architecture slides rather than being a generic
PowerPoint renderer.
"""

from __future__ import annotations

import argparse
import io
import json
import math
import posixpath
import zipfile
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path, PurePosixPath

import cairosvg
from lxml import etree
from PIL import Image, ImageColor, ImageDraw, ImageFont


PROJECT_ROOT = Path(__file__).resolve().parent.parent
EMU_PER_INCH = 914400

P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"p": P_NS, "a": A_NS, "r": R_NS}

DEFAULT_MARKER = "Coordinate-faithful reconstruction"


def _local_name(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def _font(size_px: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, max(size_px, 8))
    return ImageFont.load_default()


def _color(value: str | None, default: str = "#000000") -> tuple[int, int, int, int]:
    if not value:
        return ImageColor.getrgb(default) + (255,)
    if not value.startswith("#"):
        value = f"#{value}"
    return ImageColor.getrgb(value) + (255,)


def _safe_int(value: str | None, default: int = 0) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class Transform:
    sx: float = 1.0
    sy: float = 1.0
    tx: float = 0.0
    ty: float = 0.0

    def map_point(self, x: float, y: float) -> tuple[float, float]:
        return (self.tx + x * self.sx, self.ty + y * self.sy)

    def map_rect(self, x: float, y: float, cx: float, cy: float) -> tuple[float, float, float, float]:
        x1, y1 = self.map_point(x, y)
        x2, y2 = self.map_point(x + cx, y + cy)
        return x1, y1, x2, y2

    def compose_group(self, xfrm: etree._Element | None) -> "Transform":
        if xfrm is None:
            return self
        off = xfrm.find("a:off", namespaces=NS)
        ext = xfrm.find("a:ext", namespaces=NS)
        ch_off = xfrm.find("a:chOff", namespaces=NS)
        ch_ext = xfrm.find("a:chExt", namespaces=NS)
        off_x = _safe_int(off.get("x") if off is not None else None)
        off_y = _safe_int(off.get("y") if off is not None else None)
        ext_x = max(_safe_int(ext.get("cx") if ext is not None else None, 1), 1)
        ext_y = max(_safe_int(ext.get("cy") if ext is not None else None, 1), 1)
        ch_off_x = _safe_int(ch_off.get("x") if ch_off is not None else None)
        ch_off_y = _safe_int(ch_off.get("y") if ch_off is not None else None)
        ch_ext_x = max(_safe_int(ch_ext.get("cx") if ch_ext is not None else None, ext_x), 1)
        ch_ext_y = max(_safe_int(ch_ext.get("cy") if ch_ext is not None else None, ext_y), 1)
        child_sx = self.sx * (ext_x / ch_ext_x)
        child_sy = self.sy * (ext_y / ch_ext_y)
        child_tx = self.tx + self.sx * (off_x - ch_off_x * (ext_x / ch_ext_x))
        child_ty = self.ty + self.sy * (off_y - ch_off_y * (ext_y / ch_ext_y))
        return Transform(sx=child_sx, sy=child_sy, tx=child_tx, ty=child_ty)


def _extract_slide_list(archive: zipfile.ZipFile) -> list[dict]:
    presentation = etree.fromstring(archive.read("ppt/presentation.xml"))
    rels = etree.fromstring(archive.read("ppt/_rels/presentation.xml.rels"))
    rel_map = {
        rel.get("Id"): rel.get("Target")
        for rel in rels.findall(f"{{{PKG_REL_NS}}}Relationship")
    }
    slide_ids = presentation.find("p:sldIdLst", namespaces=NS)
    if slide_ids is None:
        return []
    slides = []
    for display_number, slide_id in enumerate(slide_ids.findall("p:sldId", namespaces=NS), start=1):
        rel_id = slide_id.get(f"{{{R_NS}}}id")
        target = rel_map.get(rel_id or "")
        if not target:
            continue
        slides.append({
            "display_number": display_number,
            "slide_path": f"ppt/{target}",
        })
    return slides


def _slide_size(archive: zipfile.ZipFile) -> tuple[int, int]:
    presentation = etree.fromstring(archive.read("ppt/presentation.xml"))
    sld_sz = presentation.find("p:sldSz", namespaces=NS)
    if sld_sz is None:
        return (12192000, 6858000)
    return (
        _safe_int(sld_sz.get("cx"), 12192000),
        _safe_int(sld_sz.get("cy"), 6858000),
    )


def _slide_rels_map(archive: zipfile.ZipFile, slide_path: str) -> dict[str, str]:
    slide_name = Path(slide_path).name
    rels_path = f"ppt/slides/_rels/{slide_name}.rels"
    try:
        root = etree.fromstring(archive.read(rels_path))
    except KeyError:
        return {}
    rels = {}
    for rel in root.findall(f"{{{PKG_REL_NS}}}Relationship"):
        rels[rel.get("Id")] = rel.get("Target")
    return rels


def _resolve_rel_path(slide_path: str, rel_target: str) -> str:
    base = PurePosixPath(slide_path).parent
    target = posixpath.normpath((base / rel_target).as_posix())
    while target.startswith("../"):
        target = target[3:]
    if not target.startswith("ppt/"):
        target = posixpath.normpath(f"ppt/{target}")
    return target


def _shape_counts(sp_tree: etree._Element) -> dict[str, int]:
    counts: dict[str, int] = {}
    for child in sp_tree:
        tag = _local_name(child.tag)
        counts[tag] = counts.get(tag, 0) + 1
    return counts


def _slide_text(root: etree._Element) -> str:
    return " ".join(
        (node.text or "").strip()
        for node in root.findall(".//a:t", namespaces=NS)
        if (node.text or "").strip()
    )


def _pick_slide(archive: zipfile.ZipFile, requested: str, marker: str) -> dict:
    slides = _extract_slide_list(archive)
    if requested != "auto":
        wanted = int(requested)
        for slide in slides:
            if slide["display_number"] == wanted:
                return slide
        raise ValueError(f"Slide {wanted} not found in PPTX")

    best: dict | None = None
    best_score = -1.0
    marker_norm = marker.lower().strip()
    for slide in slides:
        root = etree.fromstring(archive.read(slide["slide_path"]))
        sp_tree = root.find(".//p:spTree", namespaces=NS)
        if sp_tree is None:
            continue
        text = _slide_text(root).lower()
        counts = _shape_counts(sp_tree)
        score = 0.0
        if marker_norm and marker_norm in text:
            score += 100.0
        if "coordinate-faithful reconstruction" in text:
            score += 60.0
        if "oci region" in text:
            score += 25.0
        if "availability domain" in text:
            score += 10.0
        score += counts.get("grpSp", 0) * 2.0
        score += counts.get("pic", 0) * 2.5
        score += counts.get("cxnSp", 0) * 1.5
        score += min(counts.get("sp", 0), 60) * 0.1
        if score > best_score:
            best = slide
            best_score = score
    if best is None:
        raise ValueError("Could not detect an architecture slide")
    return best


class PPTXSlideRenderer:
    def __init__(self, pptx_path: Path, output_width: int | None = None):
        self.pptx_path = Path(pptx_path)
        self.output_width = output_width
        self.archive = zipfile.ZipFile(self.pptx_path)
        self.slide_cx, self.slide_cy = _slide_size(self.archive)
        self.width_px = output_width or 1600
        self.height_px = max(1, int(round(self.width_px * self.slide_cy / self.slide_cx)))
        self.scale_x = self.width_px / self.slide_cx
        self.scale_y = self.height_px / self.slide_cy
        self.image = Image.new("RGBA", (self.width_px, self.height_px), (255, 255, 255, 255))
        self.draw = ImageDraw.Draw(self.image)
        self._media_cache: dict[str, Image.Image] = {}
        self.skipped_media: list[str] = []

    def close(self) -> None:
        self.archive.close()

    def render(self, slide_number: str = "auto", marker: str = DEFAULT_MARKER) -> dict:
        slide = _pick_slide(self.archive, slide_number, marker)
        slide_root = etree.fromstring(self.archive.read(slide["slide_path"]))
        sp_tree = slide_root.find(".//p:spTree", namespaces=NS)
        if sp_tree is None:
            raise ValueError(f"{slide['slide_path']} has no shape tree")
        rel_map = _slide_rels_map(self.archive, slide["slide_path"])
        slide["shape_counts"] = _shape_counts(sp_tree)
        slide["text_sample"] = _slide_text(slide_root)[:800]
        slide["skipped_media"] = []
        for child in sp_tree:
            self._render_node(child, Transform(sx=self.scale_x, sy=self.scale_y), rel_map, slide["slide_path"])
        slide["skipped_media"] = list(self.skipped_media)
        slide["output_size"] = [self.width_px, self.height_px]
        return slide

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.image.convert("RGB").save(path)

    def _render_node(self, node: etree._Element, transform: Transform, rel_map: dict[str, str], slide_path: str) -> None:
        tag = _local_name(node.tag)
        if tag == "grpSp":
            group_xfrm = node.find("p:grpSpPr/a:xfrm", namespaces=NS)
            child_transform = transform.compose_group(group_xfrm)
            for child in node:
                if _local_name(child.tag) in {"grpSpPr", "nvGrpSpPr"}:
                    continue
                self._render_node(child, child_transform, rel_map, slide_path)
            return
        if tag == "sp":
            self._render_shape(node, transform)
            return
        if tag == "pic":
            self._render_picture(node, transform, rel_map, slide_path)
            return
        if tag == "cxnSp":
            self._render_connector(node, transform)

    def _shape_rect(self, xfrm: etree._Element | None, transform: Transform) -> tuple[int, int, int, int] | None:
        if xfrm is None:
            return None
        off = xfrm.find("a:off", namespaces=NS)
        ext = xfrm.find("a:ext", namespaces=NS)
        if off is None or ext is None:
            return None
        x1, y1, x2, y2 = transform.map_rect(
            _safe_int(off.get("x")),
            _safe_int(off.get("y")),
            _safe_int(ext.get("cx")),
            _safe_int(ext.get("cy")),
        )
        return (
            int(round(min(x1, x2))),
            int(round(min(y1, y2))),
            int(round(max(x1, x2))),
            int(round(max(y1, y2))),
        )

    def _render_shape(self, node: etree._Element, transform: Transform) -> None:
        sp_pr = node.find("p:spPr", namespaces=NS)
        if sp_pr is None:
            return
        xfrm = sp_pr.find("a:xfrm", namespaces=NS)
        rect = self._shape_rect(xfrm, transform)
        if rect is None:
            return
        geom = sp_pr.find("a:prstGeom", namespaces=NS)
        geom_type = geom.get("prst") if geom is not None else "rect"
        fill = self._fill_color(sp_pr)
        line = self._line_style(sp_pr)
        if geom_type == "ellipse":
            if fill:
                self.draw.ellipse(rect, fill=fill)
            if line:
                self.draw.ellipse(rect, outline=line["color"], width=line["width"])
        elif geom_type == "roundRect":
            radius = max(4, int(min(rect[2] - rect[0], rect[3] - rect[1]) * 0.08))
            if fill:
                self.draw.rounded_rectangle(rect, radius=radius, fill=fill)
            if line:
                self.draw.rounded_rectangle(rect, radius=radius, outline=line["color"], width=line["width"])
        elif geom_type == "line":
            self._render_line_like(xfrm, transform, line or {"color": _color("312D2A"), "width": 2, "dashed": False}, arrow=False)
        else:
            if fill:
                self.draw.rectangle(rect, fill=fill)
            if line:
                self.draw.rectangle(rect, outline=line["color"], width=line["width"])
        self._render_text(node, rect)

    def _render_picture(self, node: etree._Element, transform: Transform, rel_map: dict[str, str], slide_path: str) -> None:
        xfrm = node.find("p:spPr/a:xfrm", namespaces=NS)
        rect = self._shape_rect(xfrm, transform)
        if rect is None:
            return
        blip = node.find(".//a:blip", namespaces=NS)
        rid = blip.get(f"{{{R_NS}}}embed") if blip is not None else None
        target = rel_map.get(rid or "")
        if not target:
            return
        media_path = _resolve_rel_path(slide_path, target)
        image = self._media(media_path)
        if image is None:
            return
        width = max(rect[2] - rect[0], 1)
        height = max(rect[3] - rect[1], 1)
        resized = image.resize((width, height), Image.Resampling.LANCZOS)
        self.image.alpha_composite(resized, (rect[0], rect[1]))

    def _render_connector(self, node: etree._Element, transform: Transform) -> None:
        sp_pr = node.find("p:spPr", namespaces=NS)
        if sp_pr is None:
            return
        line = self._line_style(sp_pr)
        if not line:
            return
        xfrm = sp_pr.find("a:xfrm", namespaces=NS)
        geom = sp_pr.find("a:prstGeom", namespaces=NS)
        prst = geom.get("prst") if geom is not None else "line"
        # bentConnectorN: PowerPoint draws an elbow path inside the
        # bbox. Approximate visually so the rasterizer preview matches
        # what real PowerPoint shows. (The previous code rendered every
        # connector as a single diagonal which hid bent elbows during
        # local visual review — Diego flagged 2026-04-25.)
        if prst.startswith("bentConnector"):
            self._render_bent_connector(xfrm, transform, line, prst)
            return
        self._render_line_like(xfrm, transform, line, arrow=True)

    def _render_bent_connector(self, xfrm: etree._Element | None, transform: Transform,
                               line: dict, prst: str) -> None:
        if xfrm is None:
            return
        off = xfrm.find("a:off", namespaces=NS)
        ext = xfrm.find("a:ext", namespaces=NS)
        if off is None or ext is None:
            return
        x = _safe_int(off.get("x"))
        y = _safe_int(off.get("y"))
        cx = _safe_int(ext.get("cx"))
        cy = _safe_int(ext.get("cy"))
        flip_h = xfrm.get("flipH") == "1"
        flip_v = xfrm.get("flipV") == "1"
        start_local = (cx if flip_h else 0, cy if flip_v else 0)
        end_local = (0 if flip_h else cx, 0 if flip_v else cy)
        sx_, sy_ = transform.map_point(x + start_local[0], y + start_local[1])
        ex, ey = transform.map_point(x + end_local[0], y + end_local[1])
        # Build the elbow waypoints. bentConnector2 = single bend at
        # the source's projection on the target. bentConnector3 = two
        # bends (S-shape). bentConnector5 = four bends.
        if prst == "bentConnector2":
            mid = (ex, sy_)
            pts = [(sx_, sy_), mid, (ex, ey)]
        elif prst == "bentConnector3":
            half_x = (sx_ + ex) / 2
            pts = [(sx_, sy_), (half_x, sy_), (half_x, ey), (ex, ey)]
        else:  # bentConnector5 or anything larger
            half_x = (sx_ + ex) / 2
            half_y = (sy_ + ey) / 2
            pts = [(sx_, sy_), (half_x, sy_), (half_x, half_y),
                   (ex, half_y), (ex, ey)]
        ipts = [(int(round(p[0])), int(round(p[1]))) for p in pts]
        for i in range(len(ipts) - 1):
            a, b = ipts[i], ipts[i + 1]
            if line.get("dashed"):
                self._draw_dashed_line(a, b, line["color"], line["width"])
            else:
                self.draw.line([a, b], fill=line["color"], width=line["width"])
        if line.get("arrow"):
            self._draw_arrowhead(ipts[-2], ipts[-1], line["color"], line["width"])

    def _render_line_like(self, xfrm: etree._Element | None, transform: Transform, line: dict, arrow: bool) -> None:
        if xfrm is None:
            return
        off = xfrm.find("a:off", namespaces=NS)
        ext = xfrm.find("a:ext", namespaces=NS)
        if off is None or ext is None:
            return
        x = _safe_int(off.get("x"))
        y = _safe_int(off.get("y"))
        cx = _safe_int(ext.get("cx"))
        cy = _safe_int(ext.get("cy"))
        flip_h = xfrm.get("flipH") == "1"
        flip_v = xfrm.get("flipV") == "1"
        start_local = [0, 0]
        end_local = [cx, cy]
        if flip_h:
            start_local[0], end_local[0] = cx, 0
        if flip_v:
            start_local[1], end_local[1] = cy, 0
        start = transform.map_point(x + start_local[0], y + start_local[1])
        end = transform.map_point(x + end_local[0], y + end_local[1])
        start_xy = (int(round(start[0])), int(round(start[1])))
        end_xy = (int(round(end[0])), int(round(end[1])))
        if line.get("dashed"):
            self._draw_dashed_line(start_xy, end_xy, line["color"], line["width"])
        else:
            self.draw.line([start_xy, end_xy], fill=line["color"], width=line["width"])
        if arrow and line.get("arrow"):
            self._draw_arrowhead(start_xy, end_xy, line["color"], line["width"])

    def _draw_dashed_line(self, start: tuple[int, int], end: tuple[int, int], color, width: int) -> None:
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        distance = math.hypot(dx, dy)
        if distance < 1:
            return
        dash = 12
        gap = 7
        vx = dx / distance
        vy = dy / distance
        pos = 0.0
        while pos < distance:
            seg_end = min(pos + dash, distance)
            p1 = (int(round(start[0] + vx * pos)), int(round(start[1] + vy * pos)))
            p2 = (int(round(start[0] + vx * seg_end)), int(round(start[1] + vy * seg_end)))
            self.draw.line([p1, p2], fill=color, width=width)
            pos += dash + gap

    def _draw_arrowhead(self, start: tuple[int, int], end: tuple[int, int], color, width: int) -> None:
        angle = math.atan2(end[1] - start[1], end[0] - start[0])
        size = max(8, width * 3)
        left = (
            end[0] - size * math.cos(angle - math.pi / 6),
            end[1] - size * math.sin(angle - math.pi / 6),
        )
        right = (
            end[0] - size * math.cos(angle + math.pi / 6),
            end[1] - size * math.sin(angle + math.pi / 6),
        )
        self.draw.polygon([end, left, right], fill=color)

    def _fill_color(self, sp_pr: etree._Element):
        fill = sp_pr.find("a:solidFill", namespaces=NS)
        if fill is None or fill.find("a:srgbClr", namespaces=NS) is None:
            return None
        return _color(fill.find("a:srgbClr", namespaces=NS).get("val"))

    def _line_style(self, sp_pr: etree._Element):
        line = sp_pr.find("a:ln", namespaces=NS)
        if line is None or line.find("a:noFill", namespaces=NS) is not None:
            return None
        solid = line.find("a:solidFill/a:srgbClr", namespaces=NS)
        color = _color(solid.get("val") if solid is not None else None, "#312D2A")
        width = max(1, int(round(_safe_int(line.get("w"), 12700) * self.scale_x / 12700)))
        dash = line.find("a:prstDash", namespaces=NS)
        return {
            "color": color,
            "width": width,
            "dashed": dash is not None and dash.get("val") not in {None, "solid"},
            "arrow": line.find("a:tailEnd", namespaces=NS) is not None or line.find("a:headEnd", namespaces=NS) is not None,
        }

    def _render_text(self, node: etree._Element, rect: tuple[int, int, int, int]) -> None:
        tx_body = node.find("p:txBody", namespaces=NS)
        if tx_body is None:
            return
        body_pr = tx_body.find("a:bodyPr", namespaces=NS)
        paragraphs = []
        for paragraph in tx_body.findall("a:p", namespaces=NS):
            parts = []
            run_pr = None
            for child in paragraph:
                tag = _local_name(child.tag)
                if tag in {"r", "fld"}:
                    if run_pr is None:
                        run_pr = child.find("a:rPr", namespaces=NS)
                    text_parts = [
                        (node.text or "")
                        for node in child.findall(".//a:t", namespaces=NS)
                    ]
                    parts.append("".join(text_parts))
                elif tag == "br":
                    parts.append("\n")
            text = "".join(parts).strip()
            if not text:
                continue
            p_pr = paragraph.find("a:pPr", namespaces=NS)
            align = (p_pr.get("algn") if p_pr is not None else None) or "l"
            font_size = _safe_int(run_pr.get("sz") if run_pr is not None else None, 1100)
            fill = run_pr.find("a:solidFill/a:srgbClr", namespaces=NS) if run_pr is not None else None
            color = _color(fill.get("val") if fill is not None else None, "#312D2A")
            paragraphs.append({
                "text": text,
                "align": align,
                "size_px": max(8, int(round((font_size / 100.0) * self.height_px / ((self.slide_cy / EMU_PER_INCH) * 72)))),
                "bold": run_pr is not None and run_pr.get("b") == "1",
                "color": color,
            })
        if not paragraphs:
            return
        inset_l = int(round(_safe_int(body_pr.get("lIns") if body_pr is not None else None, 18000) * self.scale_x))
        inset_r = int(round(_safe_int(body_pr.get("rIns") if body_pr is not None else None, 18000) * self.scale_x))
        inset_t = int(round(_safe_int(body_pr.get("tIns") if body_pr is not None else None, 0) * self.scale_y))
        inset_b = int(round(_safe_int(body_pr.get("bIns") if body_pr is not None else None, 0) * self.scale_y))
        anchor = (body_pr.get("anchor") if body_pr is not None else None) or "t"
        text_left = rect[0] + inset_l
        text_top = rect[1] + inset_t
        text_right = rect[2] - inset_r
        text_bottom = rect[3] - inset_b
        box_w = max(text_right - text_left, 1)
        layouts = []
        total_h = 0
        for paragraph in paragraphs:
            font = _font(paragraph["size_px"], paragraph["bold"])
            bbox = self.draw.multiline_textbbox((0, 0), paragraph["text"], font=font, spacing=2, align="left")
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            layouts.append((paragraph, font, width, height))
            total_h += height
        total_h += max(0, len(layouts) - 1) * 2
        if anchor == "ctr":
            cursor_y = text_top + max((text_bottom - text_top - total_h) // 2, 0)
        elif anchor == "b":
            cursor_y = max(text_bottom - total_h, text_top)
        else:
            cursor_y = text_top
        for paragraph, font, text_w, text_h in layouts:
            if paragraph["align"] == "ctr":
                cursor_x = text_left + max((box_w - text_w) // 2, 0)
            elif paragraph["align"] == "r":
                cursor_x = max(text_right - text_w, text_left)
            else:
                cursor_x = text_left
            self.draw.multiline_text(
                (cursor_x, cursor_y),
                paragraph["text"],
                fill=paragraph["color"],
                font=font,
                spacing=2,
                align="left",
            )
            cursor_y += text_h + 2

    @lru_cache(maxsize=256)
    def _media(self, media_path: str) -> Image.Image | None:
        try:
            media_bytes = self.archive.read(media_path)
        except KeyError:
            return None
        suffix = Path(media_path).suffix.lower()
        try:
            if suffix == ".svg":
                media_bytes = cairosvg.svg2png(bytestring=media_bytes)
            image = Image.open(io.BytesIO(media_bytes))
            image.load()
            return image.convert("RGBA")
        except Exception:
            self.skipped_media.append(media_path)
            return None


def render_pptx_to_png(
    pptx_path: Path,
    output_path: Path,
    slide_number: str = "auto",
    marker: str = DEFAULT_MARKER,
    width: int | None = None,
) -> dict:
    renderer = PPTXSlideRenderer(Path(pptx_path), output_width=width)
    try:
        meta = renderer.render(slide_number=slide_number, marker=marker)
        renderer.save(output_path)
        meta["output_path"] = str(output_path)
        return meta
    finally:
        renderer.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a PPTX slide to PNG without LibreOffice.")
    parser.add_argument("--pptx", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--slide-number", default="auto", help="'auto' or a 1-based slide number")
    parser.add_argument("--marker", default=DEFAULT_MARKER)
    parser.add_argument("--width", type=int, default=None)
    parser.add_argument("--json", type=Path, default=None)
    args = parser.parse_args()

    meta = render_pptx_to_png(
        args.pptx,
        args.output,
        slide_number=args.slide_number,
        marker=args.marker,
        width=args.width,
    )
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
