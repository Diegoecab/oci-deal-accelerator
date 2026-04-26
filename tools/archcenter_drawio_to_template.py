#!/usr/bin/env python3
"""
archcenter_drawio_to_template — extract an ``absolute_layout`` YAML
template from a cached Oracle Architecture Center ``.drawio`` so the
agent (Claude / Codex) has a ready-to-extend scaffold instead of
falling back to ``examples/`` for YAML structure.

Why: ``archcenter_pattern_lookup`` returns the canonical ``.drawio``
as the geometry source, but the agent has to reverse-engineer it. The
cached drawios use Oracle's official ``shape=stencil(<base64>)``
style — the icon TYPE is encoded in vector bytes, not metadata, so we
can't auto-classify services. We CAN copy:

  - canvas dimensions
  - containers (region / vcn / ad / subnet) inferred from stroke/fill
    style and dashed flag
  - service bounding boxes (with ``type: TODO`` for the agent to fill)
  - edges (source/target ids, waypoints)

The template lands at ``<slug>/_template.yaml`` next to the .drawio.
``archcenter_pattern_lookup`` surfaces the path so the lookup result
includes a YAML scaffold the agent can copy and adapt.

Usage:
  python tools/archcenter_drawio_to_template.py                  # all cached
  python tools/archcenter_drawio_to_template.py --slug deploy-ords-ha-oci
  python tools/archcenter_drawio_to_template.py --force          # overwrite
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import sys
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path
from urllib.parse import unquote

import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = PROJECT_ROOT / "kb" / "diagram" / "assets" / "archcenter-refs"


# Container type inference — Oracle's drawio style markers.
# strokeColor + dashed=1 + fillColor=none → orange-dashed VCN/Subnet
# fillColor=#F5F4F2 (light gray) → region
# fillColor=#DFDCD8 (darker gray) → AD column
CONTAINER_HINTS = [
    # (predicate(style, value), container_type)
    (lambda s, v: "fillColor=#F5F4F2" in s, "region"),
    (lambda s, v: "fillColor=#DFDCD8" in s, "ad"),
    (lambda s, v: ("strokeColor=#aa643b" in s.lower() or "strokeColor=#AE562C" in s)
                  and "dashed=1" in s,
     "vcn_or_subnet"),  # disambiguated by size below
    (lambda s, v: "fillColor=none" in s and "dashed=1" in s, "subnet"),
]


def _load_drawio(path: Path) -> ET.Element:
    """Load both plain and zlib-deflated drawio payloads."""
    tree = ET.parse(path)
    root = tree.getroot()
    if any(True for _ in root.iter("mxCell")):
        return root
    diagram = root.find("diagram")
    if diagram is None:
        return root
    payload = (diagram.text or "").strip()
    if not payload:
        return root
    try:
        xml = unquote(zlib.decompress(base64.b64decode(payload), -15).decode("utf-8"))
        return ET.fromstring(xml)
    except Exception:
        return root


def _strip_html(value: str) -> str:
    return re.sub(r"<[^>]+>", "", (value or "")).strip()


def _classify_container(style: str, w: float, h: float) -> str | None:
    """Return container type or None if not a container."""
    style_low = style.lower()
    if "fillColor=#F5F4F2".lower() in style_low:
        return "region"
    if "fillColor=#DFDCD8".lower() in style_low:
        return "ad"
    has_orange = "strokeColor=#aa643b" in style_low or "strokeColor=#ae562c" in style_low
    if has_orange and "dashed=1" in style_low:
        # VCNs are taller / wider than subnets in Oracle's convention.
        # Subnets are usually thin horizontal bands (height < width / 3)
        # OR they're nested narrower than the VCN.
        return "vcn" if h > 200 and w > 400 else "subnet"
    if "fillColor=none" in style_low and "dashed=1" in style_low:
        return "subnet"
    # Last resort: any rounded bordered rect with fontStyle bold and
    # large (>200x200) is probably a container.
    if "rounded=1" in style_low and w >= 200 and h >= 200:
        return "container"
    return None


def _is_edge(cell: ET.Element) -> bool:
    return cell.get("edge") == "1"


def _is_vertex(cell: ET.Element) -> bool:
    return cell.get("vertex") == "1"


def _bbox(geom: ET.Element) -> tuple[float, float, float, float] | None:
    if geom is None:
        return None
    try:
        x = float(geom.get("x", 0) or 0)
        y = float(geom.get("y", 0) or 0)
        w = float(geom.get("width", 0) or 0)
        h = float(geom.get("height", 0) or 0)
    except ValueError:
        return None
    if w <= 0 or h <= 0:
        return None
    return (x, y, w, h)


def extract_template(drawio_path: Path) -> dict:
    """Return an ``absolute_layout`` dict extracted from the drawio."""
    root = _load_drawio(drawio_path)
    model = root if root.tag == "mxGraphModel" else root.find(".//mxGraphModel")
    page_w = float((model.get("pageWidth") if model is not None else 1240) or 1240)
    page_h = float((model.get("pageHeight") if model is not None else 720) or 720)

    containers: list[dict] = []
    services: list[dict] = []
    edges: list[dict] = []
    cells_by_id: dict[str, ET.Element] = {}

    for cell in root.iter("mxCell"):
        cid = cell.get("id") or ""
        if cid:
            cells_by_id[cid] = cell

    counter = 0

    def _next_id(prefix: str) -> str:
        nonlocal counter
        counter += 1
        return f"{prefix}{counter}"

    for cell in root.iter("mxCell"):
        style = cell.get("style", "") or ""
        value = _strip_html(cell.get("value", "") or "")
        geom = cell.find("mxGeometry")

        if _is_edge(cell):
            edge_geom = cell.find("mxGeometry")
            points = []
            if edge_geom is not None:
                array = edge_geom.find("Array")
                if array is not None:
                    for pt in array.findall("mxPoint"):
                        try:
                            points.append([
                                int(round(float(pt.get("x", 0) or 0))),
                                int(round(float(pt.get("y", 0) or 0))),
                            ])
                        except ValueError:
                            continue
            edges.append({
                "id": cell.get("id") or _next_id("e"),
                "from": cell.get("source", ""),
                "to": cell.get("target", ""),
                "type": "standard",
                "points": points,
            })
            continue

        if not _is_vertex(cell):
            continue

        bbox = _bbox(geom)
        if bbox is None:
            continue
        x, y, w, h = bbox

        # Resolve absolute coords if cell has a parent that is also a vertex
        # (drawio stores child coords relative to parent group).
        parent_id = cell.get("parent")
        ax, ay = x, y
        cur = parent_id
        while cur and cur in cells_by_id:
            parent_cell = cells_by_id[cur]
            if parent_cell.get("vertex") != "1":
                break
            pgeom = parent_cell.find("mxGeometry")
            pbbox = _bbox(pgeom)
            if not pbbox:
                break
            ax += pbbox[0]
            ay += pbbox[1]
            cur = parent_cell.get("parent")

        ctype = _classify_container(style, w, h)
        if ctype:
            containers.append({
                "id": cell.get("id") or _next_id("c"),
                "type": ctype,
                "label": value,
                "x": int(round(ax)),
                "y": int(round(ay)),
                "w": int(round(w)),
                "h": int(round(h)),
            })
        else:
            # Treat anything else with reasonable bbox as a service.
            # Skip very large rects (probably a container we missed) and
            # very small ones (probably labels or arrowheads).
            if 24 <= w <= 220 and 24 <= h <= 220:
                services.append({
                    "id": cell.get("id") or _next_id("s"),
                    "type": "TODO_identify",  # agent fills this
                    "label": value,
                    "x": int(round(ax)),
                    "y": int(round(ay)),
                    "w": int(round(w)),
                    "h": int(round(h)),
                })

    # Sort containers by area descending so the largest (region) comes
    # first and nested ones follow — easier for the agent to read.
    containers.sort(key=lambda c: -(c["w"] * c["h"]))
    services.sort(key=lambda s: (s["y"], s["x"]))

    return {
        "absolute_layout": {
            "canvas": {"width": int(page_w), "height": int(page_h)},
            "containers": containers,
            "services": services,
            "labels": [],
            "connections": edges,
        }
    }


def _slug_dirs() -> list[Path]:
    if not CACHE_DIR.exists():
        return []
    return [p for p in CACHE_DIR.iterdir() if p.is_dir()]


def _drawio_for_slug(slug_dir: Path) -> Path | None:
    hits = list(slug_dir.rglob("*.drawio"))
    return hits[0] if hits else None


def write_template(slug_dir: Path, force: bool = False) -> dict:
    drawio = _drawio_for_slug(slug_dir)
    if not drawio:
        return {"slug": slug_dir.name, "status": "no_drawio"}
    target = slug_dir / "_template.yaml"
    if target.exists() and not force:
        return {"slug": slug_dir.name, "status": "cached"}
    try:
        template = extract_template(drawio)
    except Exception as exc:
        return {"slug": slug_dir.name, "status": "error", "error": str(exc)}
    counts = {
        "containers": len(template["absolute_layout"]["containers"]),
        "services": len(template["absolute_layout"]["services"]),
        "connections": len(template["absolute_layout"]["connections"]),
    }
    if not (counts["containers"] or counts["services"]):
        return {"slug": slug_dir.name, "status": "empty", **counts}

    header = (
        "# Auto-extracted absolute_layout template from\n"
        f"#   {drawio.relative_to(PROJECT_ROOT)}\n"
        "# Source: Oracle Architecture Center reference (canonical geometry).\n"
        "# Use this as the starting scaffold for a new spec — copy, rename ids,\n"
        "# and replace `type: TODO_identify` on services with the right OCI\n"
        "# type alias (adb_s, drg, fastconnect, etc.). Container coords and\n"
        "# edge waypoints are Oracle's canonical layout; preserve unless the\n"
        "# customer's topology requires a change.\n"
    )
    target.write_text(
        header + yaml.safe_dump(template, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return {"slug": slug_dir.name, "status": "written", **counts}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", default=None,
                        help="Process only one slug folder. If omitted, processes all.")
    parser.add_argument("--force", action="store_true",
                        help="Re-extract even if _template.yaml already exists.")
    parser.add_argument("--report", type=Path,
                        default=PROJECT_ROOT / "tmp" / "_template-extract-report.json")
    args = parser.parse_args()

    targets = _slug_dirs()
    if args.slug:
        targets = [p for p in targets if p.name == args.slug]
        if not targets:
            print(f"No cached slug folder named '{args.slug}'", file=sys.stderr)
            return 1

    results = []
    counts: dict[str, int] = {}
    for d in targets:
        r = write_template(d, force=args.force)
        results.append(r)
        counts[r["status"]] = counts.get(r["status"], 0) + 1
        flag = {"written": "✓", "cached": "·", "no_drawio": "—",
                "empty": "?", "error": "✗"}.get(r["status"], "?")
        print(f"  {flag} {d.name}", file=sys.stderr)

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps({"counts": counts, "results": results}, indent=2),
                           encoding="utf-8")
    print("", file=sys.stderr)
    for s, n in sorted(counts.items()):
        print(f"  {s:15s}  {n}", file=sys.stderr)

    # Bump CACHE_DIR mtime so the lookup index invalidates and picks up
    # the new _template.yaml files on its next run.
    if counts.get("written"):
        try:
            CACHE_DIR.touch(exist_ok=True)
        except OSError:
            pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
