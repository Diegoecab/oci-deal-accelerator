#!/usr/bin/env python3
"""
OCI Side-by-Side Comparison Diagram Generator.

Produces .drawio files with the AS IS / TO BE panel layout used for
ADB-S vs ADB-D, Active Data Guard mode, refreshable-clone variants, etc.

Each panel contains:
  - A gray rounded container
  - A title banner at top (e.g., "AS IS | ADB-S for low-criticality production")
  - An optional Notes box (cream/yellow background) at top-right
  - An OCI region with side-by-side Availability Domains,
    each AD containing one or more "pools" (R/W Pool, R/O Pool, ...),
    each pool containing ADB/ATP icons
  - An AWS cloud container with App Layer + named services
  - An optional Trade-offs box at bottom

Connections are routed between services using stable user-provided ids.

CLI:
    python3 tools/oci_compare_diagram_gen.py \
        --spec examples/.../adbs-vs-adbd-compare-spec.yaml \
        --output out.drawio
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Optional

import yaml

# Reuse icon cache + per-service category styles from the main generator.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from oci_diagram_gen import (  # noqa: E402
    OCIDiagramGenerator,
    STYLES as BASE_STYLES,
    SVC_CATEGORY,
    _aws_icon_style,
)

# ---------------------------------------------------------------------------
# Panel-specific styles
# ---------------------------------------------------------------------------
# Oracle palette (see oci_diagram_gen.STYLES header for the full palette).
# Panels are rendered with the same warm grays as region containers so that
# the AS IS / TO BE scenarios read as peer artefacts on the canvas.

PANEL_STYLE = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#F5F4F2;strokeColor=#9E9892;"
    "fontColor=#312D2A;strokeWidth=1;arcSize=2;align=left;verticalAlign=top;"
    "fontFamily=Oracle Sans;fontSize=13;fontStyle=1;spacingLeft=12;spacingTop=8;"
)

# Title banner variants — tone selects the color used for the banner fill.
# 'as_is' uses muted slate (current state), 'to_be' uses teal (target state).
TITLE_BANNER_STYLES = {
    "as_is": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#70665E;strokeColor=none;"
        "fontColor=#FCFBFA;fontSize=13;fontStyle=1;fontFamily=Oracle Sans;"
        "align=left;verticalAlign=middle;spacingLeft=14;arcSize=8;"
    ),
    "to_be": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#2D5967;strokeColor=none;"
        "fontColor=#FCFBFA;fontSize=13;fontStyle=1;fontFamily=Oracle Sans;"
        "align=left;verticalAlign=middle;spacingLeft=14;arcSize=8;"
    ),
    "neutral": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#312D2A;strokeColor=none;"
        "fontColor=#FCFBFA;fontSize=13;fontStyle=1;fontFamily=Oracle Sans;"
        "align=left;verticalAlign=middle;spacingLeft=14;arcSize=8;"
    ),
}

NOTES_STYLE = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF9E6;strokeColor=#D4B84A;"
    "strokeWidth=1;fontColor=#312D2A;fontSize=10;fontFamily=Oracle Sans;"
    "align=left;verticalAlign=top;spacingLeft=10;spacingTop=8;spacingRight=8;"
    "spacingBottom=8;arcSize=6;"
)

TRADEOFFS_STYLE = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#FDF4EA;strokeColor=#AA643B;"
    "strokeWidth=1;fontColor=#AA643B;fontSize=10;fontFamily=Oracle Sans;"
    "align=left;verticalAlign=top;spacingLeft=10;spacingTop=8;spacingRight=8;"
    "spacingBottom=8;arcSize=6;fontStyle=0;"
)

OCI_REGION_STYLE = BASE_STYLES["region"]
AD_STYLE = BASE_STYLES["ad"]
POOL_STYLE = BASE_STYLES["compartment"]

# Pool tones mirror the reference adbsplusadbd.drawio: green for R/W,
# blue for R/O, neutral warm gray for anything else.
POOL_TONE_STYLES = {
    "rw": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#E6F0E0;strokeColor=#4E7A3F;"
        "strokeWidth=1;fontColor=#2F5A28;fontSize=11;fontStyle=1;"
        "fontFamily=Oracle Sans;align=left;verticalAlign=top;"
        "spacingLeft=10;spacingTop=6;arcSize=4;"
    ),
    "ro": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#E6EEF6;strokeColor=#3B5B82;"
        "strokeWidth=1;fontColor=#24405F;fontSize=11;fontStyle=1;"
        "fontFamily=Oracle Sans;align=left;verticalAlign=top;"
        "spacingLeft=10;spacingTop=6;arcSize=4;"
    ),
    "neutral": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#F2EFEA;strokeColor=#9E9892;"
        "strokeWidth=1;fontColor=#312D2A;fontSize=11;fontStyle=1;"
        "fontFamily=Oracle Sans;align=left;verticalAlign=top;"
        "spacingLeft=10;spacingTop=6;arcSize=4;"
    ),
}

# A data-guard annotation bubble: white pill with a subtle drop shadow-ish
# border that sits on top of the replication arrow.
DG_LABEL_STYLES = {
    "rw": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#4E7A3F;strokeColor=#2F5A28;"
        "strokeWidth=1;fontColor=#FCFBFA;fontSize=10;fontStyle=1;"
        "fontFamily=Oracle Sans;align=center;verticalAlign=middle;arcSize=20;"
    ),
    "ro": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#3B5B82;strokeColor=#24405F;"
        "strokeWidth=1;fontColor=#FCFBFA;fontSize=10;fontStyle=1;"
        "fontFamily=Oracle Sans;align=center;verticalAlign=middle;arcSize=20;"
    ),
    "neutral": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#2D5967;strokeColor=#1F3F48;"
        "strokeWidth=1;fontColor=#FCFBFA;fontSize=10;fontStyle=1;"
        "fontFamily=Oracle Sans;align=center;verticalAlign=middle;arcSize=20;"
    ),
}

SIDE_NOTE_STYLE = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF4D6;strokeColor=#D4B84A;"
    "strokeWidth=1;fontColor=#5A4A10;fontSize=9;fontStyle=0;"
    "fontFamily=Oracle Sans;align=left;verticalAlign=top;spacingLeft=6;"
    "spacingTop=4;arcSize=4;"
)

AWS_CLOUD_STYLE = (
    "rounded=1;whiteSpace=wrap;html=1;strokeWidth=2;dashed=1;dashPattern=6 4;"
    "fillColor=none;fontColor=#232F3E;strokeColor=#232F3E;"
    "fontFamily=Oracle Sans;fontSize=12;fontStyle=1;align=left;"
    "verticalAlign=top;spacingLeft=8;spacingTop=6;arcSize=6;"
)

APP_LAYER_STYLE = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#FCFBFA;strokeColor=#70665E;"
    "strokeWidth=1;fontColor=#312D2A;fontSize=11;fontStyle=1;"
    "fontFamily=Oracle Sans;align=center;verticalAlign=top;spacingTop=6;"
    "arcSize=6;"
)

SERVICE_PILL_STYLE = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#FCFBFA;strokeColor=#2D5967;"
    "strokeWidth=1;fontColor=#2D5967;fontSize=11;fontStyle=1;"
    "fontFamily=Oracle Sans;align=center;verticalAlign=middle;arcSize=10;"
)

STANDBY_PILL_STYLE = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#FCFBFA;strokeColor=#9E9892;"
    "strokeWidth=1;fontColor=#70665E;fontSize=11;fontStyle=2;"
    "fontFamily=Oracle Sans;align=center;verticalAlign=middle;arcSize=10;"
)

CLONE_PILL_STYLE = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#FCFBFA;strokeColor=#804998;"
    "strokeWidth=1;fontColor=#804998;fontSize=11;fontStyle=1;"
    "fontFamily=Oracle Sans;align=center;verticalAlign=middle;arcSize=10;"
)

TITLE_STYLE = (
    "text;html=1;fontSize=18;fontColor=#312D2A;fontFamily=Oracle Sans;"
    "align=center;verticalAlign=middle;fontStyle=1;"
)


def _pill_style(kind: str) -> str:
    kind = (kind or "").lower()
    if kind in ("standby", "passive", "dormant"):
        return STANDBY_PILL_STYLE
    if kind in ("clone", "refreshable_clone", "refreshable-clone", "refreshable"):
        return CLONE_PILL_STYLE
    return SERVICE_PILL_STYLE


# ---------------------------------------------------------------------------
# Layout constants (pixels)
# ---------------------------------------------------------------------------
PANEL_W = 1080
PANEL_H = 620
PANEL_GAP = 40
TITLE_BANNER_H = 30
NOTES_BOX_H = 70
TRADEOFFS_BOX_H = 56
TITLE_BANNER_Y = 10      # title banner sits 10px from panel top
CONTENT_TOP_Y = 130      # y where OCI+AWS content starts (below title+notes)
CONTENT_BOTTOM_PAD = 80  # room reserved at bottom for trade-offs box
AWS_CLOUD_W = 240
AD_GAP = 14
POOL_GAP = 10
SERVICE_PILL_W = 150
SERVICE_PILL_H = 50


class CompareDiagram:
    """Build and serialize a side-by-side comparison diagram."""

    def __init__(self):
        self.gen = OCIDiagramGenerator()
        # OCIDiagramGenerator creates a drawpyo File + Page in __init__.
        # We'll use its helpers (add_service, add_connection, icon cache) and
        # add raw panel / AD / pool containers via internal _create_object.

    # -------------------- primitive emitters --------------------

    def _text_block(
        self,
        cell_id: str,
        label: str,
        style: str,
        parent: str,
        x: int,
        y: int,
        w: int,
        h: int,
    ):
        self.gen._create_object(cell_id, label, style, parent, x, y, w, h)

    # -------------------- high-level panel build --------------------

    def build_panel(self, panel: dict, panel_x: int):
        panel_id = panel["id"]
        tone = panel.get("tone", "as_is")
        banner_style = TITLE_BANNER_STYLES.get(tone, TITLE_BANNER_STYLES["neutral"])
        panel_w = panel.get("w", PANEL_W)

        # Pre-compute panel height from the OCI region's matrix content so
        # the trade-offs box lands just below the region instead of floating
        # in dead space.
        oci_spec_pre = panel.get("oci") or {}
        pools_pre = oci_spec_pre.get("pools", []) or []
        pool_total = sum(
            p.get("h", 22 + 150 + 16) for p in pools_pre
        ) + POOL_GAP * max(0, len(pools_pre) - 1)
        content_needed = 44 + 30 + pool_total + 30  # region top + AD header + pool rows + bottom
        auto_panel_h = CONTENT_TOP_Y + content_needed + 18 + TRADEOFFS_BOX_H + 18
        panel_h = panel.get("h", auto_panel_h)

        # --- Panel container ---
        self._text_block(
            panel_id, "", PANEL_STYLE, None,
            panel_x, panel.get("y", 70), panel_w, panel_h,
        )

        # --- Title banner at top, sized to leave room for notes on the right ---
        notes_text = panel.get("notes")
        notes_w = panel.get("notes_w", 460) if notes_text else 0
        title_right_pad = notes_w + 28 if notes_w else 28
        self._text_block(
            f"{panel_id}__title",
            panel.get("title", ""),
            banner_style,
            panel_id,
            14,
            TITLE_BANNER_Y,
            panel_w - title_right_pad - 8,
            TITLE_BANNER_H,
        )

        # --- Notes box on the right, aligned with the title row ---
        if notes_text:
            self._text_block(
                f"{panel_id}__notes",
                notes_text,
                NOTES_STYLE,
                panel_id,
                panel_w - notes_w - 14,
                TITLE_BANNER_Y,
                notes_w,
                NOTES_BOX_H,
            )

        # --- Content zone positions ---
        content_top = CONTENT_TOP_Y
        content_bottom = panel_h - CONTENT_BOTTOM_PAD
        content_h = content_bottom - content_top

        aws_spec = panel.get("aws") or {}
        oci_spec = panel.get("oci") or {}
        dr_spec = panel.get("dr") or {}

        # Left margin starts at 16; AWS (if any) goes first, then OCI primary,
        # then optional DR region.
        cursor_x = 16
        if aws_spec:
            aws_w = aws_spec.get("w", AWS_CLOUD_W)
            aws_x = aws_spec.get("x", cursor_x)
            aws_h = aws_spec.get("h", content_h)
            self._build_aws_cloud(panel_id, aws_spec, aws_x, content_top,
                                  aws_w, aws_h)
            cursor_x = aws_x + aws_w + 20

        # OCI primary region.
        if dr_spec:
            # Reserve space for the DR region on the right.
            dr_w = dr_spec.get("w", max(260, int(panel_w * 0.22)))
        else:
            dr_w = 0
        oci_x = oci_spec.get("x", cursor_x)
        oci_w = oci_spec.get("w",
                             panel_w - oci_x - 16 - (dr_w + 20 if dr_spec else 0))
        oci_h = oci_spec.get("h", content_h)
        self._build_oci_region(panel_id, oci_spec, oci_x, content_top,
                               oci_w, oci_h)

        # DR region on the right (cross-region standbys).
        if dr_spec:
            dr_x = dr_spec.get("x", oci_x + oci_w + 20)
            dr_h = dr_spec.get("h", oci_h)
            self._build_oci_region(panel_id, dr_spec, dr_x, content_top,
                                   dr_w, dr_h)

        # --- Trade-offs box at bottom ---
        tradeoffs = panel.get("trade_offs") or panel.get("tradeoffs")
        if tradeoffs:
            self._text_block(
                f"{panel_id}__tradeoffs",
                tradeoffs,
                TRADEOFFS_STYLE,
                panel_id,
                14,
                panel_h - TRADEOFFS_BOX_H - 10,
                panel_w - 28,
                TRADEOFFS_BOX_H,
            )

        # --- Inter-panel connections (contained within this panel) ---
        for conn in panel.get("connections", []) or []:
            self._emit_connection(conn)

    # -------------------- AWS cloud side --------------------

    def _build_aws_cloud(
        self,
        panel_id: str,
        aws_spec: dict,
        x: int,
        y: int,
        w: int,
        h: int,
    ):
        if not aws_spec:
            return
        svcs = aws_spec.get("services", []) or []
        pill_gap = 30
        app_h = 50
        # Auto-shrink the cloud to match the content stack height, so the
        # container isn't a tall empty column when there are only a couple
        # of services.
        content_h = 38 + app_h + 20 + len(svcs) * (SERVICE_PILL_H + pill_gap) + 24
        h = min(h, max(200, content_h))

        cloud_id = aws_spec.get("id", f"{panel_id}__aws")
        self._text_block(
            cloud_id,
            aws_spec.get("label", "AWS Cloud"),
            AWS_CLOUD_STYLE,
            panel_id,
            x, y, w, h,
        )

        # App Layer header box at top
        app_label = aws_spec.get("app_label", "App Layer")
        app_w = max(80, w - 40)
        app_x = (w - app_w) // 2
        app_y = 38
        self._text_block(
            f"{cloud_id}__app",
            app_label,
            APP_LAYER_STYLE,
            cloud_id,
            app_x, app_y, app_w, app_h,
        )

        # Named service pills stacked below the App Layer header.
        sy = app_y + app_h + 20
        for svc in svcs:
            svc_id = svc["id"]
            label = svc.get("label", svc_id).replace("\\n", "\n")
            pill_w = svc.get("w", min(w - 40, 180))
            pill_h = svc.get("h", SERVICE_PILL_H)
            pill_x = (w - pill_w) // 2
            style = _pill_style(svc.get("kind", "service"))
            self._text_block(svc_id, label, style, cloud_id,
                             pill_x, sy, pill_w, pill_h)
            sy += pill_h + pill_gap

    # -------------------- OCI region + ADs + pools --------------------

    def _build_oci_region(
        self,
        panel_id: str,
        oci_spec: dict,
        x: int,
        y: int,
        w: int,
        h: int,
    ):
        """Matrix layout: AD columns + pool rows that span them.

        Layout matches the adbsplusadbd.drawio reference:
        - ADs are narrow side-by-side columns that span the full region
          content height (acting as swim lanes / column headers).
        - Pools (R/W, R/O, ...) are horizontal rows stacked vertically
          inside the region, each spanning both AD columns so the pool is
          visually cross-AD.
        - Databases (services) are placed inside a pool at an x-offset that
          aligns with the AD column they belong to, based on ``svc.ad``.
        """
        if not oci_spec:
            return
        ads = oci_spec.get("ads", []) or []
        pools = oci_spec.get("pools", []) or []
        # Databases directly inside the region (no pool/AD) — used for the
        # Montreal DR column in the simple diagrams where we just want a
        # stacked list of standbys under the region label.
        direct_dbs = oci_spec.get("databases", []) or []

        AD_HEADER_H = 30 if ads else 0
        pool_heights = []
        for pool in pools:
            n_svcs = len(pool.get("services", []) or [])
            pool_h = pool.get("h", 22 + 150 + 16)
            pool_heights.append(pool_h)
        direct_dbs_h = (150 * len(direct_dbs) + 20) if direct_dbs else 0
        region_content_h = (
            AD_HEADER_H + sum(pool_heights)
            + POOL_GAP * max(0, len(pool_heights) - 1)
            + direct_dbs_h + 20
        )
        auto_region_h = 44 + region_content_h
        h = min(h, max(240, auto_region_h))

        region_id = oci_spec.get("id", f"{panel_id}__oci")
        self._text_block(
            region_id,
            oci_spec.get("label", "OCI Region"),
            OCI_REGION_STYLE,
            panel_id,
            x, y, w, h,
        )

        # ── Direct databases (no AD/pool) ──
        # Stack vertically inside the region. Used for Montreal DR.
        if direct_dbs:
            dy = 52
            for db in direct_dbs:
                db_id = db["id"]
                label = db.get("label", db_id).replace("\\n", "\n")
                db_type = db.get("type", "adb_s")
                tone = db.get("tone")
                db_w = db.get("w", min(w - 40, 180))
                db_h = db.get("h", 140)
                db_x = (w - db_w) // 2
                self.gen.add_service(
                    db_id, label, db_type, region_id,
                    db_x, dy, db_w, db_h,
                    font_size=db.get("fontSize", 10),
                    tone=tone,
                )
                dy += db_h + 20

        if not pools:
            return

        # --- Compute AD column geometry (may be empty) ---
        ad_content_left = 20
        ad_content_right = w - 20
        ad_content_top = 44
        ad_content_bottom = h - 16
        ad_area_w = ad_content_right - ad_content_left
        ad_cols: dict[str, tuple[int, int]] = {}

        if ads:
            total_gap_w = AD_GAP * max(0, len(ads) - 1)
            ad_col_w = max(150, (ad_area_w - total_gap_w) // len(ads))
            ax = ad_content_left
            for ad in ads:
                ad_id = ad["id"]
                self._text_block(
                    ad_id,
                    ad.get("label", ad_id),
                    AD_STYLE,
                    region_id,
                    ax, ad_content_top, ad_col_w, ad_content_bottom - ad_content_top,
                )
                ad_cols[ad_id] = (ax, ad_col_w)
                ax += ad_col_w + AD_GAP
            pool_right_edge = ax - AD_GAP
        else:
            pool_right_edge = ad_content_right

        # --- Lay out pool rows ---
        pool_x = ad_content_left + 4
        pool_w = pool_right_edge - pool_x
        py = ad_content_top + AD_HEADER_H + 4
        for pool, pool_h in zip(pools, pool_heights):
            pool_id = pool["id"]
            tone = (pool.get("tone") or "neutral").lower()
            style = POOL_TONE_STYLES.get(tone, POOL_TONE_STYLES["neutral"])
            self._text_block(
                pool_id,
                pool.get("label", ""),
                style,
                region_id,
                pool_x, py, pool_w, pool_h,
            )

            # Services inside the pool.  If any service references an ad (and
            # ads are defined), use the matrix layout; otherwise distribute
            # services evenly in a horizontal row inside the pool.
            svcs = pool.get("services", []) or []
            any_ad_ref = any(svc.get("ad") for svc in svcs) and ad_cols
            if not any_ad_ref and svcs:
                n = len(svcs)
                gap = 16
                default_w = max(130, (pool_w - 30 - gap * (n - 1)) // n)
                sx = 15
                for svc in svcs:
                    svc_id = svc["id"]
                    label = svc.get("label", svc_id).replace("\\n", "\n")
                    svc_type = svc.get("type", "adb_s")
                    tone_s = svc.get("tone")
                    svc_w = svc.get("w", default_w)
                    svc_h = svc.get("h", pool_h - 36)
                    self.gen.add_service(
                        svc_id, label, svc_type, pool_id,
                        sx, 24, svc_w, svc_h,
                        font_size=svc.get("fontSize", 10),
                        tone=tone_s,
                    )
                    sx += svc_w + gap
            else:
                for svc in svcs:
                    svc_id = svc["id"]
                    label = svc.get("label", svc_id).replace("\\n", "\n")
                    svc_type = svc.get("type", "adb_s")
                    tone_s = svc.get("tone")
                    ad_ref = svc.get("ad")
                    if ad_ref and ad_ref in ad_cols:
                        col_x, col_w = ad_cols[ad_ref]
                        svc_w = svc.get("w", min(col_w - 20, 140))
                        svc_h = svc.get("h", pool_h - 36)
                        svc_cx = col_x + col_w // 2
                        svc_x_in_pool = svc_cx - svc_w // 2 - pool_x
                    else:
                        svc_w = svc.get("w", 140)
                        svc_h = svc.get("h", pool_h - 36)
                        svc_x_in_pool = 16
                    svc_y_in_pool = svc.get("y", 24)
                    self.gen.add_service(
                        svc_id, label, svc_type, pool_id,
                        svc_x_in_pool, svc_y_in_pool, svc_w, svc_h,
                        font_size=svc.get("fontSize", 10),
                        tone=tone_s,
                    )

            # Optional side-note attached to a pool (e.g., "A) Allow L-SBY...")
            side_note = pool.get("side_note")
            if side_note:
                note_w = pool.get("side_note_w", 160)
                note_h = pool.get("side_note_h", 40)
                # Anchor it to the top-right of the pool, above any DB icons.
                self._text_block(
                    f"{pool_id}__note",
                    side_note,
                    SIDE_NOTE_STYLE,
                    pool_id,
                    pool_w - note_w - 8, 2, note_w, note_h,
                )

            py += pool_h + POOL_GAP

    # The old per-AD pool helper is no longer used under the matrix layout.
    # Kept for backward-compat with any old spec that nests pools under ADs.
    def _build_pools(self, ad_id, ad_spec, ad_w, ad_h):
        pass

    def _build_pools(self, ad_id: str, ad_spec: dict, ad_w: int, ad_h: int):
        pools = ad_spec.get("pools", []) or []
        if not pools:
            return

        # Stack pools vertically inside the AD.  Each pool auto-sizes to its
        # service content (one DB slot ≈ 150px), with a small cushion for the
        # pool's own label row. We avoid stretching pools to fill the AD so
        # the icons remain visually prominent instead of floating in empty
        # space.
        pool_top = 30
        py = pool_top
        for pool in pools:
            n_svcs = len(pool.get("services", []) or [])
            auto_h = 26 + max(n_svcs, 1) * 150 + 10  # label row + slots
            pool_h = pool.get("h", auto_h)
            pool_id = pool["id"]
            self._text_block(
                pool_id,
                pool.get("label", ""),
                POOL_STYLE,
                ad_id,
                10, py, ad_w - 20, pool_h,
            )
            self._build_pool_services(pool_id, pool, ad_w - 20, pool_h)
            py += pool_h + POOL_GAP

    def _build_pool_services(
        self,
        pool_id: str,
        pool_spec: dict,
        pool_w: int,
        pool_h: int,
    ):
        svcs = pool_spec.get("services", []) or []
        if not svcs:
            return
        # Stack DB icons vertically inside the pool.  add_service() renders
        # the icon group + a sibling label text block, and the Oracle toolkit
        # targets a 63px icon height — we reserve ~140px per service so icon
        # + 2-line label fit cleanly without overlap.
        n = len(svcs)
        slot_h = max(140, (pool_h - 40) // n) if n else 0
        sy = 28
        for svc in svcs:
            svc_id = svc["id"]
            label = svc.get("label", svc_id).replace("\\n", "\n")
            svc_type = svc.get("type", "adb_s")
            svc_w = svc.get("w", min(pool_w - 20, 170))
            svc_h = svc.get("h", slot_h - 6)
            svc_x = (pool_w - svc_w) // 2
            font_size = svc.get("fontSize") or 10
            self.gen.add_service(
                svc_id, label, svc_type, pool_id,
                svc_x, sy, svc_w, svc_h, font_size=font_size,
            )
            sy += slot_h

    # -------------------- connections --------------------

    def _emit_connection(self, conn: dict):
        self.gen.add_connection(
            conn.get("id") or f"{conn['from']}_{conn['to']}",
            conn.get("label"),
            conn.get("type", "data"),
            conn["from"],
            conn["to"],
            waypoints=conn.get("waypoints"),
            flow_order=conn.get("flow_order"),
        )

    # -------------------- top-level build --------------------

    @classmethod
    def from_spec(cls, spec: dict) -> "CompareDiagram":
        self = cls()
        panels = spec.get("panels", []) or []

        # Pre-compute every panel's auto-height so we can level all panels
        # to the tallest one — visually balanced side-by-side comparison.
        def _panel_auto_h(panel: dict) -> int:
            pools = (panel.get("oci") or {}).get("pools", []) or []
            pool_total = sum(
                p.get("h", 22 + 150 + 16) for p in pools
            ) + POOL_GAP * max(0, len(pools) - 1)
            content_needed = 44 + 30 + pool_total + 30
            return CONTENT_TOP_Y + content_needed + 18 + TRADEOFFS_BOX_H + 18

        max_h = max((_panel_auto_h(p) for p in panels), default=PANEL_H)

        # Auto x layout if panel.x not provided.
        cursor_x = 30
        for panel in panels:
            panel = dict(panel)
            if "x" not in panel:
                panel["x"] = cursor_x
            # Force uniform height across panels.
            panel["h"] = panel.get("h", max_h)
            self.build_panel(panel, panel["x"])
            cursor_x = panel["x"] + panel.get("w", PANEL_W) + PANEL_GAP

        # Title across the top.
        if spec.get("title"):
            total_w = max(cursor_x, PANEL_W * 2 + PANEL_GAP)
            self.gen._create_object("title", spec["title"], TITLE_STYLE,
                                    None, 0, 14, total_w, 32)

        # Cross-panel connections (e.g., narrate deltas) go at spec level.
        for conn in spec.get("connections", []) or []:
            self._emit_connection(conn)
        return self

    def save(self, output_path: str):
        self.gen.save(output_path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--spec", required=True, help="YAML spec file")
    p.add_argument("--output", default="comparison.drawio",
                   help="Output .drawio path")
    args = p.parse_args()

    with open(args.spec, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)

    diagram = CompareDiagram.from_spec(spec)
    diagram.save(args.output)

    print(f"Generated: {args.output}")
    print(f"  Panels: {len(spec.get('panels', []))}")
    print(f"  Containers: {diagram.gen._container_count}")
    print(f"  Services: {diagram.gen._service_count}")
    print(f"  Connections: {diagram.gen._connection_count}")


if __name__ == "__main__":
    main()
