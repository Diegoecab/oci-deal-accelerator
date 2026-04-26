#!/usr/bin/env python3
"""
drawio_visual_validator — schema/sanity checks on a generated .drawio
file. Catches the bugs that pixel-similarity comparisons miss:
oversized fonts, off-canvas geometry, duplicate IDs, and orphan edges.

Why this exists: the PIL raster evaluator in oci_archcenter_eval.py
draws boxes only — it does not render font sizes, so it silently
accepted a `fontSize=700` regression that produced 700-point text
in the rebuilt drawio. This validator is a structural gate that runs
*before* the raster eval and surfaces those bugs explicitly.

Returns a dict with:
  - status: "pass" | "fail"
  - issues: list of {"severity", "code", "message", "cell_id"}
"""
from __future__ import annotations

import argparse
import base64
import json
import re
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path
from urllib.parse import unquote


# Hard limits derived from Oracle Architecture Center exports we have
# inspected. Anything above these caps is almost certainly a bug.
MAX_FONT_SIZE_PT = 30        # >30pt is suspicious in a tech diagram
MAX_REASONABLE_FONT = 24     # warn above this
MIN_FONT_SIZE_PT = 6         # <6pt is illegible
HARD_FONT_FAIL_PT = 50       # 50pt+ is a definite layout bug


def _font_size(style: str) -> int | None:
    m = re.search(r"fontSize=(\d+)", style or "")
    if not m:
        return None
    try:
        return int(m.group(1))
    except ValueError:
        return None


def _load_root(path: Path) -> ET.Element:
    """Load both plain and compressed draw.io payloads.

    Oracle Architecture Center often ships `.drawio` files where the
    `<diagram>` payload is base64 + raw-deflate XML. The validator must
    understand that format too, otherwise it silently reports `cell_count=0`
    and misses structural regressions in the official source.
    """
    tree = ET.parse(path)
    root = tree.getroot()
    if any(True for _ in root.iter("mxCell")):
        return root
    diagram = root.find("diagram")
    payload = (diagram.text or "").strip() if diagram is not None else ""
    if not payload:
        return root
    try:
        xml_bytes = zlib.decompress(base64.b64decode(payload), -15)
        return ET.fromstring(unquote(xml_bytes.decode("utf-8")))
    except Exception:
        if payload.startswith("<mxGraphModel"):
            return ET.fromstring(payload)
        return root


def validate_drawio(path: Path) -> dict:
    root = _load_root(path)
    issues: list[dict] = []

    # Determine canvas bounds from <mxGraphModel pageWidth/pageHeight>
    model = root if root.tag == "mxGraphModel" else root.find(".//mxGraphModel")
    page_w = int(model.get("pageWidth") or 1200) if model is not None else 1200
    page_h = int(model.get("pageHeight") or 800) if model is not None else 800

    seen_ids: dict[str, int] = {}
    cells = list(root.iter("mxCell")) + list(root.iter("UserObject"))
    known_ids = {cid for cell in cells if (cid := cell.get("id"))}
    edges_unrooted: list[str] = []

    # Collect container label zones — approximate the rendered TEXT bbox,
    # not the full container-edge band. A container with align=center has
    # its label text occupying the middle ~50% of the width; align=left
    # ~40% from the left edge (with spacingLeft). Approximating the
    # actual text bbox (instead of the full top-band) avoids false
    # positives on lines that pass through whitespace next to the text.
    def _label_zone(x: float, y: float, w: float, h: float, style: str, value: str) -> tuple[float, float, float, float]:
        align = "left"
        if "align=center" in style or "align=ctr" in style:
            align = "center"
        if "align=right" in style:
            align = "right"
        # Pixel-rough character width at fontSize=12 (Oracle Sans): ~7px.
        char_w = 7
        text_w = min(w - 12, max(40, len(value) * char_w))
        if align == "center":
            zx1 = x + (w - text_w) / 2
        elif align == "right":
            zx1 = x + w - text_w - 6
        else:
            zx1 = x + 6
        zx2 = zx1 + text_w
        # Vertical: 4..24 within container top band.
        return zx1, y + 4, zx2, y + 24

    container_label_zones: list[tuple[float, float, float, float, str]] = []
    # Track every container's full bbox so we can flag CONTAINER_PADDING_VIOLATION
    # — a child container whose bottom edge sits within 12px of its parent's
    # bottom edge visually merges its dashed border with the parent's,
    # which Diego flagged on the AS-IS DB Subnet vs VCN.
    containers: list[tuple[float, float, float, float, str]] = []
    for cell in cells:
        if cell.get("vertex") != "1":
            continue
        style = cell.get("style") or ""
        value = cell.get("value") or ""
        if not value or "shape=stencil" in style:
            continue
        # Look for the container family by stylistic markers (orange dashed
        # for VCN/subnet, gray fills for region/AD).
        is_container = any(s in style for s in (
            "fillColor=#F5F4F2", "fillColor=#DFDCD8",
            "fillColor=none;strokeColor=#aa643b", "fillColor=none;strokeColor=#AE562C",
        ))
        if not is_container:
            continue
        geom = cell.find("mxGeometry")
        if geom is None:
            continue
        try:
            x = float(geom.get("x") or 0)
            y = float(geom.get("y") or 0)
            w = float(geom.get("width") or 0)
            h = float(geom.get("height") or 0)
        except ValueError:
            continue
        if w < 60 or h < 30:
            continue
        zx1, zy1, zx2, zy2 = _label_zone(x, y, w, h, style, value)
        container_label_zones.append((zx1, zy1, zx2, zy2, value[:40]))
        containers.append((x, y, x + w, y + h, value[:40]))

    # CONTAINER_PADDING_VIOLATION: any container whose bottom edge sits
    # within 12px of an enclosing container's bottom is flagged. This is
    # the rule that catches "DB Subnet bottom too close to VCN bottom"
    # without us having to hand-author each spec's heights.
    PAD_MIN_PX = 12
    for cx1, cy1, cx2, cy2, clabel in containers:
        for px1, py1, px2, py2, plabel in containers:
            if (cx1, cy1, cx2, cy2) == (px1, py1, px2, py2):
                continue
            # `cell` (cx) must be strictly inside `parent` (px)
            if cx1 < px1 or cy1 < py1 or cx2 > px2 or cy2 > py2:
                continue
            gap = py2 - cy2
            if 0 <= gap < PAD_MIN_PX:
                issues.append({
                    "severity": "warn",
                    "code": "CONTAINER_PADDING_VIOLATION",
                    "message": (
                        f"'{clabel}' bottom (y={cy2:.0f}) is only {gap:.0f}px from "
                        f"its parent '{plabel}' bottom — borders will visually merge. "
                        f"Minimum recommended: {PAD_MIN_PX}px."
                    ),
                    "cell_id": "",
                })

    for cell in cells:
        cid = cell.get("id") or ""
        if cid:
            seen_ids[cid] = seen_ids.get(cid, 0) + 1
        style = cell.get("style") or ""
        # 1) Font sizes
        fs = _font_size(style)
        if fs is not None:
            if fs >= HARD_FONT_FAIL_PT:
                issues.append({
                    "severity": "error",
                    "code": "FONT_GIANT",
                    "message": f"fontSize={fs} is gigantic (≥{HARD_FONT_FAIL_PT}pt). Likely a 1/100 pt → pt unit confusion.",
                    "cell_id": cid,
                })
            elif fs > MAX_FONT_SIZE_PT:
                issues.append({
                    "severity": "warn",
                    "code": "FONT_LARGE",
                    "message": f"fontSize={fs} is unusually large (>{MAX_FONT_SIZE_PT}pt).",
                    "cell_id": cid,
                })
            elif fs < MIN_FONT_SIZE_PT:
                issues.append({
                    "severity": "warn",
                    "code": "FONT_TINY",
                    "message": f"fontSize={fs} is illegible (<{MIN_FONT_SIZE_PT}pt).",
                    "cell_id": cid,
                })
        # 2) Geometry within canvas (best-effort; vertex cells)
        geom = cell.find("mxGeometry")
        if geom is not None and cell.get("vertex") == "1":
            try:
                x = float(geom.get("x") or 0)
                y = float(geom.get("y") or 0)
                w = float(geom.get("width") or 0)
                h = float(geom.get("height") or 0)
            except ValueError:
                continue
            if w < 0 or h < 0:
                issues.append({
                    "severity": "error",
                    "code": "GEOMETRY_NEGATIVE",
                    "message": f"negative size w={w} h={h}",
                    "cell_id": cid,
                })
            # x/y can legitimately be negative (e.g. external actors), so
            # we only flag geometry that exits the page on the far side.
            if x + w > page_w + 200 or y + h > page_h + 200:
                issues.append({
                    "severity": "warn",
                    "code": "OFF_CANVAS",
                    "message": f"vertex extends past canvas: ({x},{y},{w},{h}) vs ({page_w},{page_h})",
                    "cell_id": cid,
                })
        # 3) Edge endpoints
        if cell.get("edge") == "1":
            for attr in ("source", "target"):
                ref = cell.get(attr)
                if ref and ref not in known_ids:
                    edges_unrooted.append(f"{cid}:{attr}={ref}")
            # Detect connectors crossing through container label zones.
            # We approximate the routed polyline by source endpoint +
            # mxPoint waypoints + target endpoint. Any horizontal segment
            # passing through a label zone is flagged.
            geom_e = cell.find("mxGeometry")
            if geom_e is not None and container_label_zones:
                pts: list[tuple[float, float]] = []
                src = geom_e.find("mxPoint[@as='sourcePoint']")
                tgt = geom_e.find("mxPoint[@as='targetPoint']")
                if src is not None:
                    try: pts.append((float(src.get("x") or 0), float(src.get("y") or 0)))
                    except ValueError: pass
                arr = geom_e.find("Array[@as='points']")
                if arr is not None:
                    for p in arr.findall("mxPoint"):
                        try: pts.append((float(p.get("x") or 0), float(p.get("y") or 0)))
                        except ValueError: pass
                if tgt is not None:
                    try: pts.append((float(tgt.get("x") or 0), float(tgt.get("y") or 0)))
                    except ValueError: pass
                for i in range(len(pts) - 1):
                    x1, y1 = pts[i]; x2, y2 = pts[i + 1]
                    # Horizontal segment check
                    if abs(y1 - y2) < 4:
                        for zx1, zy1, zx2, zy2, label in container_label_zones:
                            if zy1 <= y1 <= zy2 and not (max(x1, x2) < zx1 or min(x1, x2) > zx2):
                                issues.append({
                                    "severity": "warn",
                                    "code": "CONNECTOR_OVER_LABEL",
                                    "message": (f"horizontal segment y={y1:.0f} crosses "
                                                f"label zone of '{label}' (y={zy1:.0f}..{zy2:.0f})"),
                                    "cell_id": cid,
                                })
                                break
                    # Vertical segment check — added 2026-04-25 after Diego flagged
                    # LBaaS lines crossing AD label bands during the vertical drop.
                    elif abs(x1 - x2) < 4:
                        sy1, sy2 = min(y1, y2), max(y1, y2)
                        for zx1, zy1, zx2, zy2, label in container_label_zones:
                            if zx1 <= x1 <= zx2 and not (sy2 < zy1 or sy1 > zy2):
                                issues.append({
                                    "severity": "warn",
                                    "code": "CONNECTOR_OVER_LABEL",
                                    "message": (f"vertical segment x={x1:.0f} crosses "
                                                f"label zone of '{label}' (x={zx1:.0f}..{zx2:.0f}, "
                                                f"y={zy1:.0f}..{zy2:.0f})"),
                                    "cell_id": cid,
                                })
                                break

    # 4) Duplicate IDs
    for cid, count in seen_ids.items():
        if count > 1:
            issues.append({
                "severity": "error",
                "code": "DUPLICATE_ID",
                "message": f"id '{cid}' appears {count} times",
                "cell_id": cid,
            })

    if edges_unrooted:
        for entry in edges_unrooted[:20]:
            issues.append({
                "severity": "warn",
                "code": "EDGE_DANGLING",
                "message": f"edge endpoint not found: {entry}",
                "cell_id": entry.split(":")[0],
            })

    # EXCESSIVE_CORNER_MARKERS: per OCI Toolkit slide 18 the route-table /
    # security-list mini-icon is "optional, if it adds clarity". One
    # marker per VCN is the canonical use; one per subnet duplicates the
    # information and clutters the diagram. Diego flagged 2026-04-25
    # ("parecen route tables duplicados, hay muchas superposiciones").
    # We approximate the marker count by looking for stencil cells whose
    # bbox matches the half-size convention (15-30 px wide and tall).
    # Look for TOP-LEVEL stencil group anchors (parent='1') sized
    # 16-26 px square — that's the "half-size marker" convention.
    # Internal stencil sub-cells are usually parented to a group, not
    # to '1', so this filter excludes them and avoids false positives.
    marker_count = 0
    for cell in cells:
        if cell.get("vertex") != "1":
            continue
        if cell.get("parent") != "1":
            continue
        style = cell.get("style") or ""
        if "group;" not in style and "shape=stencil" not in style:
            continue
        if (cell.get("value") or "").strip():
            continue
        geom = cell.find("mxGeometry")
        if geom is None:
            continue
        try:
            w = float(geom.get("width") or 0)
            h = float(geom.get("height") or 0)
        except ValueError:
            continue
        if 16 <= w <= 26 and 16 <= h <= 26:
            marker_count += 1
    # Practical threshold: 4+ markers in a single diagram is over the
    # toolkit-stated guidance ("if they add clarity"); 6+ is clutter.
    if marker_count >= 6:
        issues.append({
            "severity": "warn",
            "code": "EXCESSIVE_CORNER_MARKERS",
            "message": (
                f"diagram has {marker_count} half-size corner markers "
                f"(route-table/security-list icons). OCI Toolkit slide 18 "
                f"says these are 'optional, if they add clarity' — keep "
                f"one per VCN at most for a clean read."
            ),
            "cell_id": "",
        })

    # FONT_TOO_SMALL_FOR_CANVAS: a wide canvas (>1000 px) compressed into
    # a slide's content_box makes small fonts hard to read. Flag any
    # text-like cell with effective fontSize < 11pt on canvases ≥1000.
    if page_w >= 1000:
        for cell in cells:
            if cell.get("vertex") != "1":
                continue
            style = cell.get("style") or ""
            value = (cell.get("value") or "").strip()
            if not value or "shape=stencil" in style:
                continue
            fs = _font_size(style)
            if fs is None:
                continue
            # Convert if value looks like 1/100 pt (≥80 → divide by 100)
            effective = fs / 100 if fs >= 80 else fs
            if effective < 11:
                issues.append({
                    "severity": "warn",
                    "code": "FONT_TOO_SMALL_FOR_CANVAS",
                    "message": (f"label fontSize={effective:.1f}pt on a {page_w}px-wide canvas "
                                "is hard to read once compressed into the slide. "
                                "Bump to ≥11pt for visibility."),
                    "cell_id": cell.get("id") or "",
                })

    has_error = any(i["severity"] == "error" for i in issues)
    return {
        "status": "fail" if has_error else "pass",
        "page": {"width": page_w, "height": page_h},
        "cell_count": len(cells),
        "issue_count": len(issues),
        "issues": issues,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Sanity-validate a .drawio file.")
    parser.add_argument("--drawio", required=True, type=Path)
    parser.add_argument("--json", type=Path, default=None)
    args = parser.parse_args()
    report = validate_drawio(args.drawio)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
