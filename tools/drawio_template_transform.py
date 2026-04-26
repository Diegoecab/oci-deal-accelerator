#!/usr/bin/env python3
"""
drawio template transform — surgical edits on Oracle reference architecture
.drawio files so we can reshape them into customer-specific diagrams without
losing Oracle's visual polish (multi-cell stencils, palette, proper layout).

Typical workflow:

    t = DrawioTemplate("kb/diagram/assets/archcenter-refs/.../in-region-dataguard.drawio")
    # relabel the title
    title_id = t.find_label("Oracle Exadata")[0]
    t.set_label(title_id, "MELI Fraud — As-Is")
    # clone an Exadata-box subtree to add a third DB
    new_ids = t.clone_subtree(exa_box_id, dx=300)
    t.save("out.drawio")

Key ops:
  - clone_subtree(cell_id, dx, dy) — deep copy with fresh IDs; dx/dy shifts
    the copy and every descendant's absolute geometry.
  - delete_subtree(cell_id) — remove a cell and every descendant.
  - set_label / set_style / move / set_geometry — surgical edits.
  - add_cell — inject a new raw cell (text block, rectangle, edge).

Cells without explicit ``id`` in Oracle's exports keep auto-generated integer
ids once loaded; clones always get prefixed globally-unique ids.
"""

from __future__ import annotations

import copy
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterable, Optional
from uuid import uuid4


class DrawioTemplate:
    """A loaded .drawio file with surgical edit helpers."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.tree = ET.parse(self.path)
        self.root = self.tree.getroot()
        self.model_root = self.root.find(".//root")
        if self.model_root is None:
            raise ValueError(f"No <root> element in {path}")
        self._next_synth = 10000
        self._ensure_ids()
        self._index()

    # ------------------------------------------------------------------
    # Index / ID management
    # ------------------------------------------------------------------

    def _ensure_ids(self):
        """Oracle exports often omit ``id`` on ordinary cells (only the root
        0/1 cells carry ids).  For surgical work we need every cell to be
        addressable, so we assign synthetic ids to anything missing one."""
        for c in self.model_root.iter("mxCell"):
            if not c.get("id"):
                c.set("id", f"syn{self._next_synth}")
                self._next_synth += 1

    def _index(self):
        self.cells: dict[str, ET.Element] = {
            c.get("id"): c for c in self.model_root.iter("mxCell")
        }
        # Reverse index: parent -> [children]
        self.children: dict[str, list[str]] = {}
        for cid, c in self.cells.items():
            p = c.get("parent") or ""
            self.children.setdefault(p, []).append(cid)

    def reindex(self):
        self._index()

    # ------------------------------------------------------------------
    # Lookup helpers
    # ------------------------------------------------------------------

    def find_label(self, contains: str, case_sensitive: bool = False) -> list[str]:
        """Return ids of cells whose `value` text contains `contains`
        (HTML tags stripped)."""
        hits = []
        needle = contains if case_sensitive else contains.lower()
        for cid, c in self.cells.items():
            raw = c.get("value") or ""
            clean = re.sub(r"<[^>]+>", " ", raw)
            clean = re.sub(r"&[a-z]+;", " ", clean)
            clean = re.sub(r"\s+", " ", clean).strip()
            hay = clean if case_sensitive else clean.lower()
            if needle in hay:
                hits.append(cid)
        return hits

    def find_style(self, contains: str) -> list[str]:
        return [cid for cid, c in self.cells.items()
                if contains in (c.get("style") or "")]

    def descendants(self, cell_id: str, include_self: bool = True) -> list[str]:
        """Return cell_id and every descendant (BFS) — ordered so that
        parents appear before their children."""
        order: list[str] = []
        if include_self:
            order.append(cell_id)
        queue = [cell_id]
        seen = {cell_id}
        while queue:
            cur = queue.pop(0)
            for child in self.children.get(cur, []):
                if child not in seen:
                    seen.add(child)
                    order.append(child)
                    queue.append(child)
        return order

    def subtree_bbox(self, cell_id: str) -> tuple[float, float, float, float]:
        """Absolute bounding box (x, y, right, bottom) of a subtree.
        Assumes drawio's relative-to-parent coordinates; walks up to get
        absolute positions."""
        def abs_xy(cid: str) -> tuple[float, float]:
            x = y = 0.0
            cur = cid
            while cur and cur in self.cells:
                c = self.cells[cur]
                geo = c.find("mxGeometry")
                if geo is not None:
                    try:
                        x += float(geo.get("x") or 0)
                        y += float(geo.get("y") or 0)
                    except ValueError:
                        pass
                parent = c.get("parent") or ""
                if parent in ("0", "1", ""):
                    break
                cur = parent
            return x, y

        xs = []
        ys = []
        rxs = []
        bys = []
        for cid in self.descendants(cell_id):
            c = self.cells[cid]
            geo = c.find("mxGeometry")
            if geo is None:
                continue
            x, y = abs_xy(cid)
            try:
                w = float(geo.get("width") or 0)
                h = float(geo.get("height") or 0)
            except ValueError:
                w = h = 0
            xs.append(x); ys.append(y); rxs.append(x + w); bys.append(y + h)
        if not xs:
            return 0, 0, 0, 0
        return min(xs), min(ys), max(rxs), max(bys)

    # ------------------------------------------------------------------
    # Mutation: clone / delete
    # ------------------------------------------------------------------

    def clone_subtree(
        self,
        cell_id: str,
        dx: float = 0,
        dy: float = 0,
        id_prefix: Optional[str] = None,
    ) -> dict[str, str]:
        """Deep-copy a subtree, assign fresh ids, shift top-level geometry by
        (dx, dy). Returns a map old_id → new_id so callers can address the
        clone afterwards."""
        if id_prefix is None:
            id_prefix = f"c{uuid4().hex[:6]}_"
        old_ids = self.descendants(cell_id)
        id_map = {old: f"{id_prefix}{old}" for old in old_ids}

        new_cells: list[ET.Element] = []
        for old in old_ids:
            src = self.cells[old]
            dup = copy.deepcopy(src)
            dup.set("id", id_map[old])
            # Rewrite parent / source / target if they point into the subtree
            for attr in ("parent", "source", "target"):
                val = dup.get(attr)
                if val in id_map:
                    dup.set(attr, id_map[val])
            new_cells.append(dup)

        # Shift the top-level (root of the clone) geometry so the copy
        # doesn't overlap the original.
        if new_cells and (dx or dy):
            top = new_cells[0]
            geo = top.find("mxGeometry")
            if geo is not None:
                try:
                    gx = float(geo.get("x") or 0)
                    gy = float(geo.get("y") or 0)
                    geo.set("x", str(gx + dx))
                    geo.set("y", str(gy + dy))
                except ValueError:
                    pass

        for nc in new_cells:
            self.model_root.append(nc)
        self._index()
        return id_map

    def delete_subtree(self, cell_id: str):
        doomed = set(self.descendants(cell_id))
        for cid in list(doomed):
            cell = self.cells.get(cid)
            if cell is not None:
                self.model_root.remove(cell)
        self._index()

    # ------------------------------------------------------------------
    # Mutation: attributes
    # ------------------------------------------------------------------

    def set_label(self, cell_id: str, text: str):
        self.cells[cell_id].set("value", text)

    def set_style(self, cell_id: str, style: str):
        self.cells[cell_id].set("style", style)

    def patch_style(self, cell_id: str, **kv):
        """Merge key=value pairs into the cell's style string (overwriting
        any existing key)."""
        cell = self.cells[cell_id]
        style = cell.get("style") or ""
        for k, v in kv.items():
            if re.search(rf"{re.escape(k)}=[^;]+", style):
                style = re.sub(rf"{re.escape(k)}=[^;]+", f"{k}={v}", style)
            else:
                if style and not style.endswith(";"):
                    style += ";"
                style += f"{k}={v};"
        cell.set("style", style)

    def move(self, cell_id: str, dx: float, dy: float):
        geo = self.cells[cell_id].find("mxGeometry")
        if geo is None:
            return
        try:
            gx = float(geo.get("x") or 0)
            gy = float(geo.get("y") or 0)
        except ValueError:
            return
        geo.set("x", str(gx + dx))
        geo.set("y", str(gy + dy))

    def set_geometry(
        self,
        cell_id: str,
        x: Optional[float] = None,
        y: Optional[float] = None,
        w: Optional[float] = None,
        h: Optional[float] = None,
    ):
        geo = self.cells[cell_id].find("mxGeometry")
        if geo is None:
            return
        if x is not None: geo.set("x", str(x))
        if y is not None: geo.set("y", str(y))
        if w is not None: geo.set("width", str(w))
        if h is not None: geo.set("height", str(h))

    # ------------------------------------------------------------------
    # Additions
    # ------------------------------------------------------------------

    def add_cell(
        self,
        value: str = "",
        style: str = "",
        parent: str = "1",
        x: float = 0,
        y: float = 0,
        w: float = 120,
        h: float = 40,
        vertex: bool = True,
        edge: bool = False,
        source: Optional[str] = None,
        target: Optional[str] = None,
    ) -> str:
        cid = f"add_{uuid4().hex[:10]}"
        cell = ET.SubElement(self.model_root, "mxCell")
        cell.set("id", cid)
        cell.set("value", value)
        cell.set("style", style)
        cell.set("parent", parent)
        if vertex and not edge:
            cell.set("vertex", "1")
        if edge:
            cell.set("edge", "1")
            if source: cell.set("source", source)
            if target: cell.set("target", target)
        geo = ET.SubElement(cell, "mxGeometry")
        if edge:
            geo.set("relative", "1")
        else:
            geo.set("x", str(x))
            geo.set("y", str(y))
            geo.set("width", str(w))
            geo.set("height", str(h))
        geo.set("as", "geometry")
        self._index()
        return cid

    def add_text(self, text: str, x: float, y: float, w: float, h: float,
                 font_size: int = 14, font_color: str = "#312D2A",
                 bold: bool = False, parent: str = "1") -> str:
        style = (
            f"text;html=1;align=left;verticalAlign=middle;whiteSpace=wrap;"
            f"fontFamily=Oracle Sans;fontSize={font_size};fontColor={font_color};"
            f"{'fontStyle=1;' if bold else ''}"
            f"strokeColor=none;fillColor=none;"
        )
        return self.add_cell(text, style, parent, x, y, w, h)

    def add_banner(self, text: str, x: float, y: float, w: float, h: float = 36,
                   color: str = "#C74634", font_color: str = "#FCFBFA") -> str:
        style = (
            f"rounded=1;whiteSpace=wrap;html=1;fillColor={color};strokeColor=none;"
            f"fontColor={font_color};fontSize=16;fontStyle=1;fontFamily=Oracle Sans;"
            f"align=center;verticalAlign=middle;arcSize=4;"
        )
        return self.add_cell(text, style, "1", x, y, w, h)

    def add_edge(self, source: str, target: str, label: str = "",
                 stroke: str = "#312D2A", dashed: bool = False) -> str:
        style = (
            f"endArrow=open;endFill=0;startArrow=none;html=1;"
            f"strokeColor={stroke};strokeWidth=1.5;rounded=1;"
            f"edgeStyle=orthogonalEdgeStyle;endSize=8;"
            f"fontFamily=Oracle Sans;fontSize=11;fontColor={stroke};"
            f"labelBackgroundColor=#FFFFFF;"
            f"{'dashed=1;dashPattern=8 4;' if dashed else ''}"
        )
        return self.add_cell(label, style, "1", 0, 0, 0, 0,
                             vertex=False, edge=True,
                             source=source, target=target)

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def save(self, path: str | Path):
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        self.tree.write(out, encoding="unicode", xml_declaration=False)


# ----------------------------------------------------------------------
# Convenience: list the cells in a template for exploration.
# ----------------------------------------------------------------------

def describe(path: str | Path, max_cells: int = 200) -> None:
    t = DrawioTemplate(path)
    print(f"{path}: {len(t.cells)} cells")
    for i, (cid, c) in enumerate(t.cells.items()):
        if i >= max_cells:
            print(f"  ... (+{len(t.cells)-i} more)")
            break
        val = (c.get("value") or "").strip()
        val_clean = re.sub(r"<[^>]+>", " ", val)
        val_clean = re.sub(r"\s+", " ", val_clean).strip()
        style = c.get("style") or ""
        style_short = (
            "stencil" if "shape=stencil" in style else
            "mxgraph" if "shape=mxgraph" in style else
            "image"   if "shape=image"   in style else
            "edge"    if c.get("edge") == "1" else
            "cont"    if "container=1"  in style else
            "text"    if "text;" in style or "align=" in style else
            "v"       if c.get("vertex") == "1" else
            "-"
        )
        geo = c.find("mxGeometry")
        xy = ""
        if geo is not None:
            xy = f"x={geo.get('x','-')} y={geo.get('y','-')} w={geo.get('width','-')} h={geo.get('height','-')}"
        print(f"  {cid:>8}  p={c.get('parent','-'):<8} {style_short:<7} {val_clean[:48]:<50} {xy}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        describe(sys.argv[1])
    else:
        print("Usage: python tools/drawio_template_transform.py <path-to-template.drawio>")
