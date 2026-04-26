#!/usr/bin/env python3
"""
harvest_drawio_icon — extract a multi-cell stencil from any Oracle
Architecture Center .drawio and add it to ``kb/diagram/oci-icons.json``
in the schema the rest of the harness expects.

Why this is a real tool, not a one-off script: the drawio renderer in
``oci_diagram_gen.py`` consumes harvested icons by re-parenting them
under a synthetic group at the spec's ``(x, y, w, h)``. If the harvested
cells carry their original whole-page absolute coordinates, the icon
renders at the harvested position on the new page (typically far below
the spec's container) — a bug we've seen and fixed once. Centralising
the extraction here ensures every harvest is normalised the same way.

Usage:
  python tools/harvest_drawio_icon.py \
    --source kb/diagram/assets/archcenter-refs/.../some.drawio \
    --anchor 205 152 64 84 \
    --type oracle_exadata_database_service \
    --title "Database - Oracle Exadata Database Service"

The ``--anchor`` argument identifies the icon's wrapper cell by its
absolute (x, y, w, h) in the source file. The harvester:

  1. Walks both ``mxCell`` and ``UserObject`` so wrapper ids are
     addressable (Oracle stores most cells inside ``UserObject``).
  2. Collects the wrapper + every descendant in the parent chain.
  3. Renumbers ids so they don't collide with other entries.
  4. Sets the wrapper's geometry to ``(0, 0, w, h)`` — the renderer
     re-positions the group from the spec; carrying absolute coords
     here would shift the rendered icon off-canvas.
"""

from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path


def _build_lookup(root: ET.Element) -> dict[str, ET.Element]:
    cells_by_id: dict[str, ET.Element] = {}
    for el in root.iter():
        if el.tag == "mxCell":
            cid = el.get("id")
            if cid:
                cells_by_id[cid] = el
        elif el.tag == "UserObject":
            cid = el.get("id")
            inner = el.find("mxCell")
            if cid and inner is not None:
                cells_by_id[cid] = inner
    return cells_by_id


def _find_anchor_at(cells: dict[str, ET.Element], target: tuple[int, int, int, int]) -> str | None:
    tx, ty, tw, th = target
    for cid, cell in cells.items():
        style = (cell.get("style") or "").lower()
        if "fillcolor=none" not in style or "strokecolor=none" not in style:
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
        if (abs(x - tx) <= 2 and abs(y - ty) <= 2
                and abs(w - tw) <= 2 and abs(h - th) <= 2):
            return cid
    return None


def _descendants(cells: dict[str, ET.Element], root_id: str) -> list[str]:
    out = [root_id]
    queue = [root_id]
    while queue:
        cur = queue.pop(0)
        for cid, cell in cells.items():
            if cell.get("parent") == cur and cid not in out:
                out.append(cid)
                queue.append(cid)
    return out


def harvest(source: Path, anchor: tuple[int, int, int, int], title: str) -> dict:
    tree = ET.parse(source)
    root = tree.getroot()
    cells = _build_lookup(root)
    anchor_id = _find_anchor_at(cells, anchor)
    if anchor_id is None:
        raise SystemExit(f"No anchor found at {anchor} in {source}")

    nodes = _descendants(cells, anchor_id)
    id_map = {nodes[0]: "2"}
    for i, n in enumerate(nodes[1:], start=3):
        id_map[n] = str(i)

    serialized: list[str] = []
    target_w, target_h = anchor[2], anchor[3]
    for n in nodes:
        cell = cells[n]
        copy = ET.fromstring(ET.tostring(cell))
        copy.set("id", id_map[n])
        old_parent = copy.get("parent") or ""
        copy.set("parent", id_map.get(old_parent, "1"))
        if n == anchor_id:
            geom = copy.find("mxGeometry")
            if geom is not None:
                # CRITICAL: normalize wrapper to (0,0,w,h). The renderer
                # re-positions the group from the spec. See module docstring.
                geom.set("x", "0")
                geom.set("y", "0")
                geom.set("width", str(target_w))
                geom.set("height", str(target_h))
        serialized.append(ET.tostring(copy, encoding="unicode"))

    return {
        "title": title,
        "w": float(target_w),
        "h": float(target_h),
        "cells": serialized,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path,
                        help="Path to the Oracle .drawio source file.")
    parser.add_argument("--anchor", required=True, nargs=4, type=int, metavar=("X", "Y", "W", "H"),
                        help="Anchor coordinates of the icon wrapper in the source.")
    parser.add_argument("--type", required=True,
                        help="Icon type key under which to register the entry (e.g. policies).")
    parser.add_argument("--title", default="",
                        help="Human-readable title (defaults to the type key).")
    parser.add_argument("--alias", action="append", default=[],
                        help="Additional keys to alias to the same entry (repeatable).")
    parser.add_argument("--icons-json", type=Path,
                        default=Path(__file__).resolve().parent.parent / "kb" / "diagram" / "oci-icons.json")
    args = parser.parse_args()

    entry = harvest(args.source, tuple(args.anchor), args.title or args.type.replace("_", " ").title())
    icons = json.loads(args.icons_json.read_text(encoding="utf-8")) if args.icons_json.exists() else {}
    icons[args.type] = entry
    for alias in args.alias:
        icons[alias] = entry
    args.icons_json.write_text(json.dumps(icons, indent=2), encoding="utf-8")
    print(f"wrote {args.type}"
          + (f" + aliases {args.alias}" if args.alias else "")
          + f" → {args.icons_json}")


if __name__ == "__main__":
    main()
