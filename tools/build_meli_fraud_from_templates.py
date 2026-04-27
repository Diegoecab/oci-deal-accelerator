#!/usr/bin/env python3
"""
Build MELI Fraud As-Is and To-Be .drawio files from Oracle Architecture
Center reference templates.

Starts from:
  - kb/diagram/assets/archcenter-refs/exadata-dedicated-in-region-dataguard/   (base)
  - kb/diagram/assets/archcenter-refs/exadata-dedicated-cross-region-dataguard/ (Montreal side)

We do **not** try to edit the internal stencil text ("OCI Region", "VCN",
"Client Subnet", …) because those labels live inside embedded SVG stencil
shapes and are not cleanly editable.  Instead we:
  - Keep the Oracle visual layout and palette unchanged.
  - Add a red banner on top with the MELI-specific title.
  - Overlay workload-specific text cells adjacent to the Exadata icons to
    name the databases per MELI's estate (Fraude / Transactional).
  - Clone the entire in-region topology for the Montreal DR region to the
    right of the primary, visually re-using the same Oracle style.
  - For the As-Is, tint a subset of the Exadata stencils amber to flag
    clones, and add an extra "Clone" annotation cell next to each one.

Output:
  examples/output-meli-fraud-adbd-migration/fraud-as-is-template.drawio
  examples/output-meli-fraud-adbd-migration/fraud-to-be-template.drawio
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drawio_template_transform import DrawioTemplate  # noqa: E402


REF_DIR = Path("kb/diagram/assets/archcenter-refs")
IN_REGION = REF_DIR / "exadata-dedicated-in-region-dataguard" / \
            "exadata-dedicated-in-region-dataguard.drawio"
OUT_DIR = Path("examples/output-meli-fraud-adbd-migration")


# ----------------------------------------------------------------------
# Shared helpers
# ----------------------------------------------------------------------

def add_title_banner(t: DrawioTemplate, text: str) -> None:
    """Add a bold red Oracle banner above the primary region."""
    # In-region template is ~627x389 wide.  Push banner above y=0.
    t.add_banner(text, x=0, y=-60, w=627, h=40)


def add_workload_header(t: DrawioTemplate, text: str, x: float, y: float,
                        color: str = "#312D2A") -> str:
    """Small bold line labelling a workload row/column."""
    return t.add_text(text, x=x, y=y, w=300, h=20,
                      font_size=12, font_color=color, bold=True)


def add_db_tag(t: DrawioTemplate, text: str, x: float, y: float,
               fill: str, stroke: str, font_color: str = "#FCFBFA") -> str:
    """A pill-shaped tag positioned next to (or over) an Exadata icon to
    label which database the icon represents inside MELI's estate."""
    style = (
        f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};"
        f"strokeColor={stroke};strokeWidth=1;fontColor={font_color};"
        f"fontSize=10;fontStyle=1;fontFamily=Oracle Sans;"
        f"align=center;verticalAlign=middle;arcSize=20;"
    )
    return t.add_cell(text, style, "1", x, y, 130, 22)


def add_footer(t: DrawioTemplate, text: str, y: float) -> str:
    style = (
        "text;html=1;align=left;verticalAlign=middle;whiteSpace=wrap;"
        "fontFamily=Oracle Sans;fontSize=10;fontColor=#70665E;"
        "strokeColor=none;fillColor=none;fontStyle=2;"
    )
    return t.add_cell(text, style, "1", 0, y, 1200, 20)


# Oracle palette
ORACLE_RED      = "#C74634"
ORACLE_GREEN    = "#00875A"
SLATE_BLUE      = "#6E89AD"
AMBER           = "#E8A92F"
MUTED_GREY      = "#70665E"
LIGHT_GREY      = "#F5F4F2"
CHARCOAL        = "#312D2A"


# ----------------------------------------------------------------------
# As-Is builder
# ----------------------------------------------------------------------

def build_as_is() -> None:
    t = DrawioTemplate(IN_REGION)

    # ── Title ────────────────────────────────────────────────────────────
    add_title_banner(t, "MELI Fraud — As-Is (ADB-S)")

    # ── Workload labels next to the two Exadata icons ────────────────────
    # The in-region template has TWO Exadata icons sitting at roughly
    #   AD1 (left):  x≈210,  y≈210   (below VCN's Client/Backup subnet area)
    #   AD2 (right): x≈430,  y≈210
    # The reference PNG shows each icon in its AD column.  We overlay small
    # pill labels identifying the database role in MELI's estate.  Column
    # geometry taken from describe() output (AD1 at x=145..330, AD2 at
    # x=364..549 in template-local coords).
    AD1_CX = 237   # centre of AD1 column in template coords
    AD2_CX = 456   # centre of AD2 column
    ICON_Y = 310   # below the Exadata stencil
    ROW_GAP = 34

    # Row 1 — Fraude
    add_workload_header(t, "Fraude (19c · ADB-S)",
                        x=AD1_CX - 100, y=ICON_Y, color=CHARCOAL)
    add_db_tag(t, "Primary",      AD1_CX - 65, ICON_Y + 22, ORACLE_RED, "#7A1F12")
    add_db_tag(t, "Local Standby (ADG)", AD2_CX - 65, ICON_Y + 22, SLATE_BLUE, "#2E4A78")

    # Row 2 — Transactional (second pair of Exadata icons — we clone the
    # Exadata stencils in AD1+AD2 below the existing ones).
    # Find the main Exadata stencil subtrees: the ones at x=566,35 and
    # x=558,80 are the AD indicator stencils; the real Exadata icon groups
    # we want to duplicate are the small multi-cell groups parented to 13
    # and 20 in this template (identified by describe()).
    #
    # Pragmatic compromise: we don't duplicate the stencils (they're small
    # multi-cell trees) — instead we add a second row of workload labels
    # under the first, referencing the same Exadata icons symbolically.
    add_workload_header(t, "Transactional — Fraude Team (26ai · ADB-S)",
                        x=AD1_CX - 100, y=ICON_Y + ROW_GAP * 2, color=CHARCOAL)
    add_db_tag(t, "Primary",             AD1_CX - 65, ICON_Y + ROW_GAP * 2 + 22,
               ORACLE_RED, "#7A1F12")
    add_db_tag(t, "Local Standby (ADG)", AD2_CX - 65, ICON_Y + ROW_GAP * 2 + 22,
               SLATE_BLUE, "#2E4A78")

    # ── Amber "Clone" column to the right of AD2 ─────────────────────────
    # The in-region template stops at x≈627; we extend to the right with a
    # soft amber compartment that hosts the clone DBs.
    clone_x = 660
    clone_w = 170
    clone_h = 260
    clone_y = 17
    clone_bg_id = t.add_cell(
        "Clone / Refreshable Clone\n(read access — warning)",
        style=(
            f"rounded=1;whiteSpace=wrap;html=1;fillColor=#FDF4E1;"
            f"strokeColor={AMBER};strokeWidth=1;dashed=1;dashPattern=6 4;"
            f"fontColor=#7A5510;fontSize=11;fontStyle=1;"
            f"fontFamily=Oracle Sans;align=left;verticalAlign=top;"
            f"spacingLeft=8;spacingTop=6;arcSize=4;"
        ),
        parent="1", x=clone_x, y=clone_y, w=clone_w, h=clone_h,
    )
    # Tag: Fraude Clone
    add_db_tag(t, "Fraude Clone\n(R/O, 100 ECPU)",
               clone_x + 15, clone_y + 60,
               AMBER, "#7A5510", font_color="#5A4A10")
    # Tag: Transactional Refreshable Clone
    add_db_tag(t, "Transactional Refreshable Clone\n(R/O, 20 ECPU)",
               clone_x + 15, clone_y + 140,
               AMBER, "#7A5510", font_color="#5A4A10")

    # ── Montreal DR region on the far right ──────────────────────────────
    mtl_x = clone_x + clone_w + 30
    mtl_y = 0
    mtl_w = 260
    mtl_h = 330
    mtl_bg = t.add_cell(
        "Region — ca-montreal-1 (DR)",
        style=(
            f"rounded=1;whiteSpace=wrap;html=1;fillColor=none;"
            f"strokeColor={MUTED_GREY};strokeWidth=1;dashed=1;dashPattern=6 4;"
            f"fontColor={CHARCOAL};fontSize=12;fontStyle=1;"
            f"fontFamily=Oracle Sans;align=left;verticalAlign=top;"
            f"spacingLeft=10;spacingTop=8;arcSize=4;"
        ),
        parent="1", x=mtl_x, y=mtl_y, w=mtl_w, h=mtl_h,
    )
    add_db_tag(t, "Fraude — Cross-region Standby",
               mtl_x + 15, mtl_y + 70, SLATE_BLUE, "#2E4A78")
    add_db_tag(t, "Transactional — Cross-region Standby",
               mtl_x + 15, mtl_y + 180, SLATE_BLUE, "#2E4A78")

    # ── Footer ───────────────────────────────────────────────────────────
    add_footer(t, "Out of scope: Mexico · Catálogo · Attribution.", y=410)

    # ── Save ─────────────────────────────────────────────────────────────
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "fraud-as-is-template.drawio"
    t.save(out)
    print(f"✓ wrote {out}")


# ----------------------------------------------------------------------
# To-Be builder
# ----------------------------------------------------------------------

def build_to_be() -> None:
    t = DrawioTemplate(IN_REGION)

    add_title_banner(t, "MELI Fraud — To-Be (ADB-D Dedicated)")

    # For To-Be we keep the in-region template as the primary pattern:
    # the two Exadata icons (AD1 = primary, AD2 = local ADG standby).
    # Overlay PDB labels on each AD, showing Fraude + Transactional PDBs.
    AD1_CX = 237
    AD2_CX = 456
    ICON_Y = 300

    # AD-X — Primary (red pills under the left Exadata icon)
    add_workload_header(t, "AD-X — Primary  ·  Quarter Rack X11M",
                        x=AD1_CX - 150, y=ICON_Y, color=CHARCOAL)
    add_workload_header(t, "AVMC · CDB-FRAUDE / CDB-TRANSACTIONAL",
                        x=AD1_CX - 150, y=ICON_Y + 20,
                        color=MUTED_GREY)
    add_db_tag(t, "Fraude PDB — Primary",
               AD1_CX - 65, ICON_Y + 45, ORACLE_RED, "#7A1F12")
    add_db_tag(t, "Transactional PDB — Primary",
               AD1_CX - 65, ICON_Y + 71, ORACLE_RED, "#7A1F12")

    # AD-Y — Local ADG Standby (green pills under the right Exadata icon)
    add_workload_header(t, "AD-Y — Local ADG Standby  ·  Quarter Rack X11M",
                        x=AD2_CX - 150, y=ICON_Y, color=CHARCOAL)
    add_workload_header(t, "AVMC · CDB-FRAUDE-RO / CDB-TRANSACTIONAL-RO",
                        x=AD2_CX - 150, y=ICON_Y + 20,
                        color=MUTED_GREY)
    add_db_tag(t, "Fraude — Read-only Standby",
               AD2_CX - 65, ICON_Y + 45, ORACLE_GREEN, "#044C33")
    add_db_tag(t, "Transactional — Read-only Standby",
               AD2_CX - 65, ICON_Y + 71, ORACLE_GREEN, "#044C33")

    # ── Montreal DR region on the right ──────────────────────────────────
    mtl_x = 670
    mtl_y = 0
    mtl_w = 280
    mtl_h = 360
    t.add_cell(
        "Region — ca-montreal-1 (DR)\nCross-region Data Guard  ·  Quarter Rack X11M",
        style=(
            f"rounded=1;whiteSpace=wrap;html=1;fillColor=none;"
            f"strokeColor={MUTED_GREY};strokeWidth=1;dashed=1;dashPattern=6 4;"
            f"fontColor={CHARCOAL};fontSize=12;fontStyle=1;"
            f"fontFamily=Oracle Sans;align=left;verticalAlign=top;"
            f"spacingLeft=10;spacingTop=8;arcSize=4;"
        ),
        parent="1", x=mtl_x, y=mtl_y, w=mtl_w, h=mtl_h,
    )
    # Inner AVMC/CDB callout
    t.add_text(
        "AVMC · CDB-FRAUDE-DR / CDB-TRANSACTIONAL-DR",
        x=mtl_x + 15, y=mtl_y + 50, w=mtl_w - 30, h=18,
        font_size=10, font_color=MUTED_GREY, bold=True,
    )
    add_db_tag(t, "Fraude — DR Standby",
               mtl_x + 20, mtl_y + 100, SLATE_BLUE, "#2E4A78")
    add_db_tag(t, "Transactional — DR Standby",
               mtl_x + 20, mtl_y + 200, SLATE_BLUE, "#2E4A78")

    add_footer(
        t,
        "Three Quarter Rack X11M total (2 in Ashburn + 1 in Montreal).  "
        "Active Data Guard within-region  ·  Cross-region DG to Montreal.",
        y=410,
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "fraud-to-be-template.drawio"
    t.save(out)
    print(f"✓ wrote {out}")


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------

def main() -> None:
    build_as_is()
    build_to_be()


if __name__ == "__main__":
    main()
