#!/usr/bin/env python3
"""
Alternate MELI Fraud diagrams — built on top of the Oracle
`exadata-dedicated-cross-region-dataguard` reference architecture as chassis.

Why this chassis:
  It ships with exactly the layout both prompts want — two OCI regions
  side-by-side, each with a VCN (Client Subnet + Backup Subnet), a Database
  Service icon, DRG + Remote Peering, Service Gateway, and Oracle Services
  Network (DNS + Object Storage) — with the Oracle Data Guard arrow drawn
  between the two regions.

We keep the chassis largely untouched and overlay MELI-specific pills +
region rename + title banner, per Diego's earlier feedback that preserving
Oracle's official polish is the goal.  The Exadata stencil stays (it is an
Oracle shape representing the database infrastructure) but the pills
identify the specific databases layered on top of it for MELI's estate.

Output:
  examples/output-meli-fraud-adbd-migration/fraud-as-is-alt.drawio
  examples/output-meli-fraud-adbd-migration/fraud-to-be-alt.drawio
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drawio_template_transform import DrawioTemplate  # noqa: E402

SRC = Path(
    "kb/diagram/assets/archcenter-refs/exadata-dedicated-cross-region-dataguard/"
    "exadata-dedicated-cross-region-dataguard-uncompressed.drawio"
)
OUT_DIR = Path("examples/output-meli-fraud-adbd-migration")

ORACLE_RED   = "#C74634"
ORACLE_GREEN = "#00875A"
SLATE_BLUE   = "#6E89AD"
AMBER        = "#E8A92F"
MUTED_GREY   = "#70665E"
CHARCOAL     = "#312D2A"


def add_banner(t: DrawioTemplate, text: str, x: float, y: float, w: float,
               h: float = 36, color: str = ORACLE_RED,
               font_color: str = "#FCFBFA") -> str:
    style = (
        f"rounded=1;whiteSpace=wrap;html=1;fillColor={color};strokeColor=none;"
        f"fontColor={font_color};fontSize=16;fontStyle=1;fontFamily=Oracle Sans;"
        f"align=center;verticalAlign=middle;arcSize=4;"
    )
    return t.add_cell(text, style, "1", x, y, w, h)


def add_pill(t: DrawioTemplate, text: str, x: float, y: float,
             fill: str, stroke: str, font_color: str = "#FCFBFA",
             w: float = 170, h: float = 22) -> str:
    style = (
        f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};"
        f"strokeColor={stroke};strokeWidth=1;fontColor={font_color};"
        f"fontSize=10;fontStyle=1;fontFamily=Oracle Sans;"
        f"align=center;verticalAlign=middle;arcSize=30;"
    )
    return t.add_cell(text, style, "1", x, y, w, h)


def add_region_label(t: DrawioTemplate, text: str, x: float, y: float,
                     color: str = CHARCOAL) -> str:
    style = (
        f"text;html=1;align=left;verticalAlign=middle;whiteSpace=wrap;"
        f"fontFamily=Oracle Sans;fontSize=12;fontStyle=1;fontColor={color};"
        f"strokeColor=none;fillColor=none;"
    )
    return t.add_cell(text, style, "1", x, y, 340, 20)


def add_footer(t: DrawioTemplate, text: str, x: float, y: float,
               w: float = 1000) -> str:
    style = (
        f"text;html=1;align=left;verticalAlign=middle;whiteSpace=wrap;"
        f"fontFamily=Oracle Sans;fontSize=10;fontColor={MUTED_GREY};"
        f"strokeColor=none;fillColor=none;fontStyle=2;"
    )
    return t.add_cell(text, style, "1", x, y, w, 20)


# ---------------------------------------------------------------------------
# Geometry landmarks in the cross-region-dataguard template
# ---------------------------------------------------------------------------
# Tenancy chassis: ~1054x624 canvas
# Left region ("OCI Region"):  x ≈ 10,  y ≈ 34,  w ≈ 454, h ≈ 579
# Right region ("OCI Region"): x ≈ 590, y ≈ 34,  w ≈ 454, h ≈ 579
# Exadata icon boxes centered inside each region at y ≈ 210
#   left icon cluster centre around x=220
#   right icon cluster centre around x=820

LEFT_REGION_X  = 10
LEFT_REGION_Y  = 34
LEFT_REGION_W  = 454
RIGHT_REGION_X = 590
RIGHT_REGION_W = 454
EXA_CLUSTER_Y  = 220    # vertical centre of Exadata icon in each region
PILL_W         = 200


# ---------------------------------------------------------------------------
# As-Is builder
# ---------------------------------------------------------------------------

def build_as_is() -> None:
    t = DrawioTemplate(SRC)

    # ── Title banner (sits above the canvas) ────────────────────────────
    add_banner(t, "MELI Fraud — As-Is (ADB-S)",
               x=0, y=-46, w=1054, h=36)

    # ── Region labels override the stencil's "OCI Region" text with a
    # clearer "us-ashburn-1 (Primary)" / "ca-montreal-1 (DR)" heading ─────
    add_region_label(t, "us-ashburn-1  ·  Primary",
                     x=LEFT_REGION_X + 40, y=LEFT_REGION_Y + 4)
    add_region_label(t, "ca-montreal-1  ·  DR",
                     x=RIGHT_REGION_X + 40, y=LEFT_REGION_Y + 4)

    # ── Left region: overlay 2 workload rows with 3 DBs each ────────────
    # Exadata icon of the left region is centred around x=220, y=220.  We
    # place pills below it identifying the databases MELI has on ADB-S.
    lx = LEFT_REGION_X + 30
    row_y = 260
    row_h = 120

    # Row 1 — Fraude
    add_region_label(t, "Fraude (19c · ADB-S)",
                     x=lx, y=row_y - 20)
    add_pill(t, "Primary", lx, row_y, ORACLE_RED, "#7A1F12",
             w=120, h=22)
    add_pill(t, "Local Standby (ADG)", lx + 130, row_y, SLATE_BLUE,
             "#2E4A78", w=160, h=22)
    add_pill(t, "Clone (R/O)", lx + 300, row_y, AMBER, "#7A5510",
             font_color="#5A4A10", w=100, h=22)

    # Row 2 — Transactional
    add_region_label(t, "Transactional — Fraude Team (26ai · ADB-S)",
                     x=lx, y=row_y + row_h - 20)
    add_pill(t, "Primary", lx, row_y + row_h, ORACLE_RED, "#7A1F12",
             w=120, h=22)
    add_pill(t, "Local Standby (ADG)", lx + 130, row_y + row_h, SLATE_BLUE,
             "#2E4A78", w=160, h=22)
    add_pill(t, "Refreshable Clone (R/O)", lx + 300, row_y + row_h, AMBER,
             "#7A5510", font_color="#5A4A10", w=140, h=22)

    # ── Right region: Montreal — cross-region standbys ──────────────────
    rx = RIGHT_REGION_X + 30
    add_region_label(t, "Fraude — Cross-region Standby",
                     x=rx, y=row_y - 20)
    add_pill(t, "Fraude — DR Standby", rx, row_y, SLATE_BLUE, "#2E4A78",
             w=250, h=22)
    add_region_label(t, "Transactional — Cross-region Standby",
                     x=rx, y=row_y + row_h - 20)
    add_pill(t, "Transactional — DR Standby", rx, row_y + row_h, SLATE_BLUE,
             "#2E4A78", w=250, h=22)

    add_footer(t, "Out of scope: Mexico · Catálogo · Attribution.",
               x=10, y=635, w=1000)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "fraud-as-is-alt.drawio"
    t.save(out)
    print(f"✓ wrote {out}")


# ---------------------------------------------------------------------------
# To-Be builder
# ---------------------------------------------------------------------------

def build_to_be() -> None:
    t = DrawioTemplate(SRC)

    add_banner(t, "MELI Fraud — To-Be (ADB-D Dedicated)",
               x=0, y=-46, w=1054, h=36)

    add_region_label(t, "us-ashburn-1  ·  Primary  ·  AD-X + AD-Y",
                     x=LEFT_REGION_X + 40, y=LEFT_REGION_Y + 4)
    add_region_label(t, "ca-montreal-1  ·  DR",
                     x=RIGHT_REGION_X + 40, y=LEFT_REGION_Y + 4)

    # ── Left region: 2 ADs, each with AVMC → CDB → PDB ──────────────────
    lx = LEFT_REGION_X + 30
    ad_y = 260
    row_h = 120

    add_region_label(t,
                     "AD-X — Primary  ·  Quarter Rack X11M  ·  AVMC",
                     x=lx, y=ad_y - 20)
    add_pill(t, "CDB-FRAUDE · Fraude PDB — Primary",
             lx, ad_y, ORACLE_RED, "#7A1F12", w=320, h=22)
    add_pill(t, "CDB-TRANSACTIONAL · Transactional PDB — Primary",
             lx, ad_y + 28, ORACLE_RED, "#7A1F12", w=380, h=22)

    add_region_label(t,
                     "AD-Y — Local ADG Standby  ·  Quarter Rack X11M  ·  AVMC",
                     x=lx, y=ad_y + row_h - 20)
    add_pill(t, "CDB-FRAUDE-RO · Fraude — Read-only Standby",
             lx, ad_y + row_h, ORACLE_GREEN, "#044C33", w=340, h=22)
    add_pill(t, "CDB-TRANSACTIONAL-RO · Transactional — Read-only Standby",
             lx, ad_y + row_h + 28, ORACLE_GREEN, "#044C33", w=400, h=22)

    # ── Right region: Montreal DR — Quarter Rack X11M, AVMC ─────────────
    rx = RIGHT_REGION_X + 30
    add_region_label(t,
                     "Cross-region DR  ·  Quarter Rack X11M  ·  AVMC",
                     x=rx, y=ad_y - 20)
    add_pill(t, "CDB-FRAUDE-DR · Fraude — DR Standby",
             rx, ad_y, SLATE_BLUE, "#2E4A78", w=310, h=22)
    add_pill(t, "CDB-TRANSACTIONAL-DR · Transactional — DR Standby",
             rx, ad_y + 28, SLATE_BLUE, "#2E4A78", w=370, h=22)

    add_footer(
        t,
        "Three Quarter Rack X11M total (2 in Ashburn + 1 in Montreal).  "
        "Active Data Guard in-region  ·  Cross-region DG to Montreal.",
        x=10, y=635, w=1040,
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "fraud-to-be-alt.drawio"
    t.save(out)
    print(f"✓ wrote {out}")


def main() -> None:
    build_as_is()
    build_to_be()


if __name__ == "__main__":
    main()
