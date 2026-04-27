#!/usr/bin/env python3
"""
Build MELI Fraud As-Is and To-Be .drawio files by cloning and editing
examples/output-meli-fraud-adbd-migration/adbsplusadbd.drawio — the ADB
(ATP-S / ATP-D) reference Diego already accepted visually.

Strategy:
  1. Load the source file.
  2. Partition cells into AS-IS (x < 4630) and TO-BE (x >= 4630) panels;
     edges are assigned to a panel based on their source/target cell.
  3. For each output, delete the panel we don't need.
  4. Relabel the title banner, notes, and trade-offs text for MELI.
  5. Clone the ATP-S / ATP-D icon cells (single-cell stencils) to add a
     second workload row (Transactional) and a Clone column (As-Is only).
  6. Add a Montreal DR region panel to the right.
  7. Save.

Constraint: interior labels like "OCI Ashburn" / "AD 3" / "AD 2" / "R/W Pool"
are plain mxCell values we CAN edit — so we rename AD 3 → AD-X, AD 2 → AD-Y,
adjust R/W Pool label, etc.
"""

from __future__ import annotations

import copy
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drawio_template_transform import DrawioTemplate  # noqa: E402


SRC = Path("examples/output-meli-fraud-adbd-migration/adbsplusadbd.drawio")
OUT_DIR = Path("examples/output-meli-fraud-adbd-migration")


# Oracle palette
ORACLE_RED   = "#C74634"
ORACLE_GREEN = "#00875A"
SLATE_BLUE   = "#6E89AD"
AMBER        = "#E8A92F"
MUTED_GREY   = "#70665E"
CHARCOAL     = "#312D2A"


# ---------------------------------------------------------------------------
# Panel partitioning
# ---------------------------------------------------------------------------

def partition_panels(t: DrawioTemplate, split_x: float = 4630):
    """Return (as_is_ids, to_be_ids) — both sets cover all vertex cells.
    Edges are classified by their source/target positions.
    """
    as_is, to_be = set(), set()

    def cell_x(cid: str) -> float | None:
        c = t.cells.get(cid)
        if c is None:
            return None
        geo = c.find("mxGeometry")
        if geo is None:
            return None
        try:
            return float(geo.get("x") or 0)
        except ValueError:
            return None

    # Vertices first: classify by absolute x (walk parents to get absolute x)
    def abs_x(cid: str) -> float:
        x = 0.0
        cur = cid
        guard = 0
        while cur and cur in t.cells and guard < 30:
            geo = t.cells[cur].find("mxGeometry")
            if geo is not None:
                try:
                    x += float(geo.get("x") or 0)
                except ValueError:
                    pass
            parent = t.cells[cur].get("parent") or ""
            if parent in ("0", "1", ""):
                break
            cur = parent
            guard += 1
        return x

    for cid, c in t.cells.items():
        if cid in ("0", "1"):
            continue
        if c.get("edge") == "1":
            continue
        ax = abs_x(cid)
        if ax >= split_x:
            to_be.add(cid)
        else:
            as_is.add(cid)

    # Edges follow their source/target
    for cid, c in t.cells.items():
        if c.get("edge") != "1":
            continue
        src = c.get("source")
        tgt = c.get("target")
        in_tobe = any(ref and ref in to_be for ref in (src, tgt))
        in_asis = any(ref and ref in as_is for ref in (src, tgt))
        if in_tobe and not in_asis:
            to_be.add(cid)
        elif in_asis and not in_tobe:
            as_is.add(cid)
        else:
            # Ambiguous — keep with TO BE by default
            to_be.add(cid)

    return as_is, to_be


def delete_cells(t: DrawioTemplate, cell_ids: set[str]) -> None:
    for cid in list(cell_ids):
        c = t.cells.get(cid)
        if c is not None:
            try:
                t.model_root.remove(c)
            except ValueError:
                pass
    t.reindex()


# ---------------------------------------------------------------------------
# Text helpers — Oracle templates often store rich-HTML values
# ---------------------------------------------------------------------------

def replace_rich_label(t: DrawioTemplate, cell_id: str, plain_text: str,
                       color: str = CHARCOAL, bold: bool = True,
                       size: int = 16) -> None:
    """Replace a cell's <value> with simple HTML — keeps drawio rendering happy."""
    weight = "bold" if bold else "normal"
    html = (
        f'<h1 style="color: {color}; text-align: left; '
        f'line-height: 1.1; margin: 0; font-size: {size}px; font-weight: {weight};">'
        f'{plain_text}</h1>'
    )
    t.cells[cell_id].set("value", html)


def add_pill(t: DrawioTemplate, text: str, x: float, y: float,
             fill: str, stroke: str, font_color: str = "#FCFBFA",
             w: float = 130, h: float = 22) -> str:
    style = (
        f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};"
        f"strokeColor={stroke};strokeWidth=1;fontColor={font_color};"
        f"fontSize=10;fontStyle=1;fontFamily=Oracle Sans;"
        f"align=center;verticalAlign=middle;arcSize=30;"
    )
    return t.add_cell(text, style, "1", x, y, w, h)


def add_soft_box(t: DrawioTemplate, label: str, x: float, y: float,
                 w: float, h: float, fill: str, stroke: str,
                 font_color: str = CHARCOAL) -> str:
    style = (
        f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};"
        f"strokeColor={stroke};strokeWidth=1;dashed=1;dashPattern=6 4;"
        f"fontColor={font_color};fontSize=12;fontStyle=1;"
        f"fontFamily=Oracle Sans;align=left;verticalAlign=top;"
        f"spacingLeft=8;spacingTop=6;arcSize=4;"
    )
    return t.add_cell(label, style, "1", x, y, w, h)


# ---------------------------------------------------------------------------
# As-Is builder — left panel of adbsplusadbd, ATP-S icons
# ---------------------------------------------------------------------------

def build_as_is() -> None:
    t = DrawioTemplate(SRC)
    as_is, to_be = partition_panels(t)
    delete_cells(t, to_be)

    P = "GVNBTaRQvtpjXlJZoCOU"  # id prefix used in the source

    # Title: cell 87 holds the AS IS title banner text
    replace_rich_label(t, f"{P}-87", "MELI Fraud — As-Is (ADB-S)",
                       color="#FCFBFA", bold=True, size=22)
    # Make the banner red + solid
    t.patch_style(f"{P}-87",
                  fillColor=ORACLE_RED,
                  strokeColor="none",
                  fontColor="#FCFBFA",
                  align="center",
                  verticalAlign="middle")

    # Remove the notes and trade-offs text boxes — not needed in the simple view
    for cid in (f"{P}-88", f"{P}-89", f"{P}-86"):
        if cid in t.cells:
            t.delete_subtree(cid)

    # Relabel AD 3 → AD-X, AD 2 → AD-Y to match the prompt
    if f"{P}-93" in t.cells:
        t.set_label(f"{P}-93", "AD-X")
    if f"{P}-94" in t.cells:
        t.set_label(f"{P}-94", "AD-Y")

    # Rename R/W Pool → Fraude (it holds Fraude's primary + standby)
    # Cell 95 is the R/W Pool container in AS IS.
    if f"{P}-95" in t.cells:
        t.set_label(f"{P}-95", "Fraude (19c · ADB-S)")

    # Relabel the ATP-S icons: 100 = primary, 99 = L-SBY. Replace their
    # rich HTML values with simple labels.
    if f"{P}-100" in t.cells:
        replace_rich_label(t, f"{P}-100", "Fraude — Primary", color=ORACLE_RED,
                           size=11)
    if f"{P}-99" in t.cells:
        replace_rich_label(t, f"{P}-99", "Fraude — Local Standby (ADG)",
                           color=SLATE_BLUE, size=11)
    # Cell 112 is an extra ATP-S icon floating; reuse as Fraude Clone (amber)
    if f"{P}-112" in t.cells:
        replace_rich_label(t, f"{P}-112", "Fraude — Clone (R/O)",
                           color="#7A5510", size=11)
        # No tone override on the stencil itself — keep the OCI teal icon but
        # wrap an amber dashed pill around it.
        geo = t.cells[f"{P}-112"].find("mxGeometry")
        if geo is not None:
            gx = float(geo.get("x") or 0)
            gy = float(geo.get("y") or 0)
            gw = float(geo.get("width") or 60)
            gh = float(geo.get("height") or 50)
            t.add_cell(
                "", style=(
                    f"rounded=1;whiteSpace=wrap;html=1;fillColor=none;"
                    f"strokeColor={AMBER};strokeWidth=2;dashed=1;dashPattern=6 4;"
                    f"arcSize=8;"
                ),
                parent="1", x=gx - 6, y=gy - 6, w=gw + 12, h=gh + 14,
            )

    # Delete notes cell 111 if present (the "A) Allow L-SBY..." side note)
    if f"{P}-111" in t.cells:
        t.delete_subtree(f"{P}-111")

    # ── Second workload row (Transactional) — clone the pool + icons ────
    # Clone the pool container (95), primary stencil (100), standby (99),
    # and the small customer icon group (101) with a y-offset of ~290 so
    # they sit below the existing row.
    dy = 290
    clone_map = {}
    for src_id in (f"{P}-95", f"{P}-100", f"{P}-99"):
        if src_id not in t.cells:
            continue
        m = t.clone_subtree(src_id, dx=0, dy=dy,
                            id_prefix=f"txn_{src_id.split('-')[-1]}_")
        clone_map.update(m)

    # Label the cloned pool
    cloned_pool = clone_map.get(f"{P}-95")
    if cloned_pool:
        t.set_label(cloned_pool, "Transactional — Fraude Team (26ai · ADB-S)")

    cloned_primary = clone_map.get(f"{P}-100")
    if cloned_primary:
        replace_rich_label(t, cloned_primary, "Transactional — Primary",
                           color=ORACLE_RED, size=11)

    cloned_sby = clone_map.get(f"{P}-99")
    if cloned_sby:
        replace_rich_label(t, cloned_sby, "Transactional — Local Standby (ADG)",
                           color=SLATE_BLUE, size=11)

    # Transactional Refreshable Clone — clone the ATP-S icon (cell 112) and
    # place it below the Fraude clone
    if f"{P}-112" in t.cells:
        m = t.clone_subtree(f"{P}-112", dx=0, dy=dy,
                            id_prefix="txn_clone_")
        cloned_clone = m.get(f"{P}-112")
        if cloned_clone:
            replace_rich_label(t, cloned_clone,
                               "Transactional — Refreshable Clone",
                               color="#7A5510", size=11)

    # ── Montreal DR region ──────────────────────────────────────────────
    # Place a new gray dashed region to the right of the primary OCI region.
    # OCI Ashburn in source is at x=4155, w=344 → right edge ≈ 4499.
    # The panel backdrop (85) ends at x=3543+1101=4644. Push Montreal to the
    # right, extending the panel size if needed.
    MTL_X = 4660
    MTL_Y = 5925
    MTL_W = 340
    MTL_H = 570
    add_soft_box(t, "Region — ca-montreal-1 (DR)",
                 MTL_X, MTL_Y, MTL_W, MTL_H,
                 fill="#FFFFFF", stroke=MUTED_GREY)

    add_pill(t, "Fraude — Cross-region Standby",
             MTL_X + 30, MTL_Y + 80, SLATE_BLUE, "#2E4A78", w=280, h=32)
    add_pill(t, "Transactional — Cross-region Standby",
             MTL_X + 30, MTL_Y + 200, SLATE_BLUE, "#2E4A78", w=280, h=32)

    # Extend the big panel backdrop (cell 85) to accommodate Montreal
    panel = t.cells.get(f"{P}-85")
    if panel is not None:
        geo = panel.find("mxGeometry")
        if geo is not None:
            # Widen from 1101 to ~1500
            geo.set("width", "1530")
            geo.set("height", "870")

    # Footer line
    t.add_text(
        "Out of scope: Mexico · Catálogo · Attribution.",
        x=3561, y=6600, w=900, h=22,
        font_size=11, font_color=MUTED_GREY, bold=False,
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "fraud-as-is.drawio"
    t.save(out)
    print(f"✓ wrote {out}")


# ---------------------------------------------------------------------------
# To-Be builder — right panel of adbsplusadbd, ATP-D icons
# ---------------------------------------------------------------------------

def build_to_be() -> None:
    t = DrawioTemplate(SRC)
    as_is, to_be = partition_panels(t)
    delete_cells(t, as_is)

    P = "GVNBTaRQvtpjXlJZoCOU"

    # Title: cell 4 holds the TO BE title in the source
    replace_rich_label(t, f"{P}-4",
                       "MELI Fraud — To-Be (ADB-D Dedicated)",
                       color="#FCFBFA", bold=True, size=22)
    t.patch_style(f"{P}-4",
                  fillColor=ORACLE_RED,
                  strokeColor="none",
                  fontColor="#FCFBFA",
                  align="center",
                  verticalAlign="middle")

    # Remove notes + trade-offs + RPO/RTO floating labels
    for cid in (f"{P}-5", f"{P}-36", f"{P}-3"):
        if cid in t.cells:
            t.delete_subtree(cid)

    # Rename AD 3 → AD-X, AD 2 → AD-Y
    if f"{P}-40" in t.cells:
        t.set_label(f"{P}-40", "AD-X — Primary  ·  Quarter Rack X11M")
    if f"{P}-41" in t.cells:
        t.set_label(f"{P}-41", "AD-Y — Local ADG Standby  ·  Quarter Rack X11M")

    # Pools: 43 = R/O Pool, 42 = R/W Pool. Rename to AVMC-per-workload framing.
    if f"{P}-43" in t.cells:
        t.set_label(f"{P}-43", "AVMC · CDB-FRAUDE / CDB-TRANSACTIONAL — Primary")
    if f"{P}-42" in t.cells:
        t.set_label(f"{P}-42",
                    "AVMC · CDB-FRAUDE-RO / CDB-TRANSACTIONAL-RO — Read-only Standby")

    # Relabel ATP-D icons: cell 47 (L-SBY R/O), 48 (primary)
    if f"{P}-47" in t.cells:
        replace_rich_label(t, f"{P}-47", "Fraude — Read-only Standby",
                           color=ORACLE_GREEN, size=11)
    if f"{P}-48" in t.cells:
        replace_rich_label(t, f"{P}-48", "Fraude — Primary",
                           color=ORACLE_RED, size=11)

    # ── Second workload row (Transactional) — clone ATP-D icons ─────────
    dy = 80  # place below the existing icons inside the same pool areas
    clone_map = {}
    for src_id in (f"{P}-47", f"{P}-48"):
        if src_id not in t.cells:
            continue
        m = t.clone_subtree(src_id, dx=0, dy=dy,
                            id_prefix=f"txn_{src_id.split('-')[-1]}_")
        clone_map.update(m)

    cloned_ro = clone_map.get(f"{P}-47")
    if cloned_ro:
        replace_rich_label(t, cloned_ro, "Transactional — Read-only Standby",
                           color=ORACLE_GREEN, size=11)
    cloned_primary = clone_map.get(f"{P}-48")
    if cloned_primary:
        replace_rich_label(t, cloned_primary, "Transactional — Primary",
                           color=ORACLE_RED, size=11)

    # ── Montreal DR region ──────────────────────────────────────────────
    MTL_X = 5860
    MTL_Y = 6004
    MTL_W = 340
    MTL_H = 600
    add_soft_box(t,
                 "Region — ca-montreal-1 (DR)\nQuarter Rack X11M",
                 MTL_X, MTL_Y, MTL_W, MTL_H,
                 fill="#FFFFFF", stroke=MUTED_GREY)
    t.add_text(
        "AVMC · CDB-FRAUDE-DR / CDB-TRANSACTIONAL-DR",
        x=MTL_X + 15, y=MTL_Y + 60, w=MTL_W - 30, h=20,
        font_size=10, font_color=MUTED_GREY, bold=True,
    )
    add_pill(t, "Fraude — DR Standby",
             MTL_X + 30, MTL_Y + 110, SLATE_BLUE, "#2E4A78", w=280, h=32)
    add_pill(t, "Transactional — DR Standby",
             MTL_X + 30, MTL_Y + 240, SLATE_BLUE, "#2E4A78", w=280, h=32)

    # Extend the TO BE panel backdrops (cells 1, 2) to fit Montreal
    for cid in (f"{P}-1", f"{P}-2"):
        panel = t.cells.get(cid)
        if panel is None:
            continue
        geo = panel.find("mxGeometry")
        if geo is not None:
            geo.set("width", "1540")
            geo.set("height", "870")

    # Footer
    t.add_text(
        "Three Quarter Rack X11M total (2 in Ashburn + 1 in Montreal). "
        "Active Data Guard in-region · Cross-region DG to Montreal.",
        x=4708, y=6675, w=1500, h=22,
        font_size=11, font_color=MUTED_GREY, bold=False,
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "fraud-to-be.drawio"
    t.save(out)
    print(f"✓ wrote {out}")


def main() -> None:
    build_as_is()
    build_to_be()


if __name__ == "__main__":
    main()
