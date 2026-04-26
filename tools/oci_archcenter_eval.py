#!/usr/bin/env python3
"""
Evaluate an Architecture Center reconstruction against an official PNG asset.

The evaluator consumes the `absolute_layout` used by the editable draw.io and
native PPTX renderers, creates a comparable raster view, and records objective
image metrics plus structural coverage. It is a benchmark aid, not a substitute
for human review in draw.io/PowerPoint.
"""

import argparse
import json
import math
from pathlib import Path

import yaml
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps


PALETTE = {
    "bark": "#312D2A",
    "teal": "#2D5967",
    "gray": "#9E9892",
    "region": "#F5F4F2",
    "ad": "#DFDCD8",
    "orange": "#AA643B",
    "white": "#FFFFFF",
    "badge": "#70665E",
}


def _font(size: int, bold: bool = False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def _text(draw, xy, text, fill=PALETTE["bark"], size=13, bold=False, anchor="mm", align="center"):
    draw.multiline_text(xy, text or "", fill=fill, font=_font(size, bold), anchor=anchor, align=align, spacing=2)


def _dashed_rect(draw, box, outline, width=2, dash=8, gap=5):
    x1, y1, x2, y2 = box
    for x in range(x1, x2, dash + gap):
        draw.line([(x, y1), (min(x + dash, x2), y1)], fill=outline, width=width)
        draw.line([(x, y2), (min(x + dash, x2), y2)], fill=outline, width=width)
    for y in range(y1, y2, dash + gap):
        draw.line([(x1, y), (x1, min(y + dash, y2))], fill=outline, width=width)
        draw.line([(x2, y), (x2, min(y + dash, y2))], fill=outline, width=width)


def _arrow(draw, points, fill=PALETTE["bark"], width=2):
    if len(points) < 2:
        return
    draw.line(points, fill=fill, width=width, joint="curve")
    x1, y1 = points[-2]
    x2, y2 = points[-1]
    angle = math.atan2(y2 - y1, x2 - x1)
    size = 8
    left = (x2 - size * math.cos(angle - math.pi / 6), y2 - size * math.sin(angle - math.pi / 6))
    right = (x2 - size * math.cos(angle + math.pi / 6), y2 - size * math.sin(angle + math.pi / 6))
    draw.polygon([(x2, y2), left, right], fill=fill)


def _service(draw, item):
    x, y = int(item["x"]), int(item["y"])
    w, h = int(item.get("w", 60)), int(item.get("h", 70))
    icon_h = max(30, min(48, h - 22))
    cx = x + w // 2
    icon_top = y + 2
    draw.rounded_rectangle(
        [cx - icon_h // 2, icon_top, cx + icon_h // 2, icon_top + icon_h],
        radius=3, outline=PALETTE["teal"], width=2, fill=PALETTE["white"],
    )
    kind = item.get("type", "")
    if kind in {"load_balancer", "internet_gateway"}:
        draw.line([(cx - 14, icon_top + icon_h // 2), (cx + 14, icon_top + icon_h // 2)], fill=PALETTE["teal"], width=3)
        draw.line([(cx, icon_top + 8), (cx, icon_top + icon_h - 8)], fill=PALETTE["teal"], width=3)
    elif kind in {"compute", "network_firewall"}:
        for dx in (-10, 0, 10):
            for dy in (10, 20, 30):
                draw.rectangle([cx + dx - 3, icon_top + dy - 3, cx + dx + 3, icon_top + dy + 3], outline=PALETTE["teal"], width=1)
    elif kind in {"monitoring", "notifications"}:
        draw.line([(cx - 16, icon_top + 30), (cx - 4, icon_top + 18), (cx + 6, icon_top + 26), (cx + 15, icon_top + 12)], fill=PALETTE["teal"], width=2)
    elif kind in {"functions", "object_storage"}:
        draw.rectangle([cx - 15, icon_top + 13, cx + 15, icon_top + 30], outline=PALETTE["teal"], width=2)
        draw.line([(cx - 10, icon_top + 22), (cx + 10, icon_top + 22)], fill=PALETTE["teal"], width=2)
    label = str(item.get("label", "")).replace("\\n", "\n")
    if label:
        _text(draw, (cx, y + h - 12), label, size=13, bold=False)


def render_layout(spec_path: Path, output_path: Path) -> dict:
    spec = yaml.safe_load(spec_path.read_text())
    layout = spec["absolute_layout"]
    canvas = layout.get("canvas") or {}
    width = int(canvas.get("width", 850))
    height = int(canvas.get("height", 770))
    image = Image.new("RGB", (width, height), PALETTE["white"])
    draw = ImageDraw.Draw(image)

    for item in layout.get("containers") or []:
        x, y = int(item["x"]), int(item["y"])
        w, h = int(item["w"]), int(item["h"])
        kind = item.get("type")
        box = [x, y, x + w, y + h]
        if kind == "region":
            draw.rounded_rectangle(box, radius=3, outline=PALETTE["gray"], fill=PALETTE["region"], width=1)
        elif kind == "ad":
            draw.rounded_rectangle(box, radius=3, outline=PALETTE["gray"], fill=PALETTE["ad"], width=1)
        elif kind in {"vcn", "subnet"}:
            _dashed_rect(draw, box, PALETTE["orange"], width=2)
        label = str(item.get("label", "")).replace("\\n", "\n")
        if label:
            color = PALETTE["orange"] if kind in {"vcn", "subnet"} else PALETTE["bark"]
            _text(draw, (x + w // 2 if item.get("align") == "ctr" else x + 12, y + 16), label, fill=color, size=13, bold=bool(item.get("bold", True)), anchor="mm" if item.get("align") == "ctr" else "lm")

    for item in layout.get("external") or []:
        x, y = int(item["x"]), int(item["y"])
        cx = x + int(item.get("w", 70)) // 2
        draw.ellipse([cx - 18, y + 6, cx - 6, y + 18], outline=PALETTE["teal"], width=2)
        draw.arc([cx - 24, y + 18, cx, y + 44], 200, 340, fill=PALETTE["teal"], width=2)
        draw.ellipse([cx + 6, y + 4, cx + 20, y + 18], outline=PALETTE["teal"], width=2)
        draw.arc([cx, y + 18, cx + 28, y + 46], 200, 340, fill=PALETTE["teal"], width=2)
        _text(draw, (x + int(item.get("w", 70)) // 2, y + 54), item.get("label", ""), size=13)

    services = {item["id"]: item for item in layout.get("services") or []}
    services.update({item["id"]: item for item in layout.get("external") or []})
    for item in layout.get("services") or []:
        _service(draw, item)

    for conn in layout.get("connections") or []:
        points = conn.get("points") or conn.get("waypoints")
        if not points:
            continue
        pts = [(int(x), int(y)) for x, y in points]
        _arrow(draw, pts)
        if conn.get("flow_order"):
            bx = int(pts[0][0] + (pts[-1][0] - pts[0][0]) * float(conn.get("badge_t", 0.25)))
            by = int(pts[0][1] + (pts[-1][1] - pts[0][1]) * float(conn.get("badge_t", 0.25)))
            draw.ellipse([bx - 10, by - 10, bx + 10, by + 10], fill=PALETTE["badge"])
            _text(draw, (bx, by), str(conn["flow_order"]), fill=PALETTE["white"], size=12, bold=True)

    for item in layout.get("labels") or []:
        _text(
            draw,
            (int(item["x"]) + int(item.get("w", 100)) // 2, int(item["y"]) + int(item.get("h", 24)) // 2),
            str(item.get("text", "")).replace("\\n", "\n"),
            size=max(9, int(item.get("fontSize", 760)) // 70),
            bold=bool(item.get("bold", False)),
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)
    return {
        "canvas": [width, height],
        "containers": len(layout.get("containers") or []),
        "services": len(layout.get("services") or []),
        "external": len(layout.get("external") or []),
        "connections": len(layout.get("connections") or []),
        "labels": len(layout.get("labels") or []),
    }


def _dhash(image: Image.Image, hash_size: int = 8) -> int:
    gray = ImageOps.grayscale(image).resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
    pixels = list(gray.getdata())
    value = 0
    for row in range(hash_size):
        for col in range(hash_size):
            left = pixels[row * (hash_size + 1) + col]
            right = pixels[row * (hash_size + 1) + col + 1]
            value = (value << 1) | int(left > right)
    return value


def compare(reference_path: Path, candidate_path: Path, diff_path: Path) -> dict:
    reference = Image.open(reference_path).convert("RGB")
    candidate = Image.open(candidate_path).convert("RGB").resize(reference.size, Image.Resampling.LANCZOS)
    diff = ImageChops.difference(reference, candidate)
    diff_path.parent.mkdir(parents=True, exist_ok=True)
    ImageOps.autocontrast(diff).save(diff_path)
    hist = diff.histogram()
    sq = sum(value * ((idx % 256) ** 2) for idx, value in enumerate(hist))
    rms = math.sqrt(sq / float(reference.size[0] * reference.size[1] * 3))
    similarity = max(0.0, 1.0 - (rms / 255.0))
    h1 = _dhash(reference)
    h2 = _dhash(candidate)
    hamming = (h1 ^ h2).bit_count()
    return {
        "reference_size": list(reference.size),
        "candidate_size": list(candidate.size),
        "rms_diff": round(rms, 3),
        "pixel_similarity": round(similarity, 4),
        "dhash_hamming": hamming,
        "diff_path": str(diff_path),
    }


def write_report(report_path: Path, payload: dict) -> None:
    status = "PASS" if payload["comparison"]["pixel_similarity"] >= payload["threshold"] else "FAIL"
    lines = [
        f"# Architecture Center Diagram Evaluation",
        "",
        f"- Status: **{status}**",
        f"- Threshold: {payload['threshold']}",
        f"- Pixel similarity: {payload['comparison']['pixel_similarity']}",
        f"- RMS diff: {payload['comparison']['rms_diff']}",
        f"- dHash hamming distance: {payload['comparison']['dhash_hamming']}",
        f"- Structural counts: {json.dumps(payload['structure'], sort_keys=True)}",
        "",
        "## Notes",
        "",
        "This raster is generated from the same absolute layout consumed by the editable draw.io and native PPTX renderers. Use it as automated regression evidence; final visual approval still requires opening the editable artifacts.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Evaluate an Architecture Center reconstruction.")
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--reference", required=True, type=Path)
    parser.add_argument("--render", required=True, type=Path)
    parser.add_argument("--diff", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--json", required=True, type=Path)
    parser.add_argument("--threshold", type=float, default=0.82)
    args = parser.parse_args()

    structure = render_layout(args.spec, args.render)
    comparison = compare(args.reference, args.render, args.diff)
    payload = {
        "threshold": args.threshold,
        "structure": structure,
        "comparison": comparison,
    }
    args.json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_report(args.report, payload)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
