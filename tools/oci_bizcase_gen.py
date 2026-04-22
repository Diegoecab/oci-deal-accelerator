#!/usr/bin/env python3
"""
OCI Deal Accelerator — Business Case Deck Generator (.pptx)

Produces an 8-10 slide business case deck using the Oracle FY26 official
PowerPoint template layouts. Target audience: customer CxO / decision-makers.

Usage:
    python oci_bizcase_gen.py --spec business-case.yaml --output business-case.pptx

Or import and use programmatically:
    from oci_bizcase_gen import BusinessCaseDeckGenerator
    gen = BusinessCaseDeckGenerator.from_spec(spec)
    gen.save("business-case.pptx")
"""

import yaml
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

from oci_pptx_base import Colors, Layouts, OraclePresBase


# ============================================================
# Defensive input helpers
# ============================================================

def pick(mapping: dict, *keys, default=""):
    """Return the first non-empty value for any of the provided keys."""
    if not isinstance(mapping, dict):
        return default
    for key in keys:
        if key in mapping:
            value = mapping.get(key)
            if value is not None:
                return value
    return default


def pick_list(mapping: dict, *keys):
    """Return the first list-like field normalized to a list."""
    if not isinstance(mapping, dict):
        return []
    for key in keys:
        if key in mapping:
            value = mapping.get(key)
            if value is None:
                return []
            if isinstance(value, list):
                return value
            return [value]
    return []


# ============================================================
# Business Case Deck Generator
# ============================================================

class BusinessCaseDeckGenerator(OraclePresBase):
    """Generate business case decks using Oracle FY26 template layouts."""

    # Use Teal accent for business case slides (finance / CxO audience)
    TITLE_ACCENT_COLOR = Colors.TEAL

    # ================================================================
    # Slide Methods
    # ================================================================

    def add_cover_slide(self, customer: str, subtitle: str = "",
                        prepared_by: str = "", date: str = ""):
        """Slide 1: Cover using Dark Title_Pillar layout."""
        slide = self._add_layout_slide(Layouts.COVER_DARK)
        self._set_placeholder(slide, 0, customer)  # Title
        self._set_placeholder(slide, 33, subtitle or "Business Case for Oracle Cloud Infrastructure")
        date_str = date or datetime.now().strftime("%B %Y")
        self._set_placeholder(slide, 35, date_str)
        if prepared_by:
            self._set_placeholder(slide, 34, f"Prepared by: {prepared_by}")

    def add_executive_summary_slide(self, statement: str):
        """Slide 2: Executive Summary — controlled typography on blank slide."""
        slide = self._add_blank_slide()

        self._add_title_bar(slide, "Executive Summary")

        # Body — large enough to read, small enough to fit the paragraph
        body_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.7), Inches(4.5))
        tf = body_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = statement
        p.font.size = Pt(18)
        p.font.name = self.FONT
        p.font.color.rgb = Colors.PRIMARY_TEXT
        p.space_after = Pt(6)

    def add_business_drivers_slide(self, drivers: list):
        """Slide 3: Business Drivers — numbered cards on blank slide.

        drivers: list of up to 3 strings, each a driver statement (may include newline
        separating a bold headline from detail text).
        """
        slide = self._add_blank_slide()

        self._add_title_bar(slide, "Business Drivers")

        card_colors = [Colors.TEAL, Colors.BURNT_ORANGE, Colors.FOREST]
        card_y_start = Inches(1.3)
        available_h = Inches(5.8)
        n = min(len(drivers), 3)
        card_h = available_h / n if n else available_h
        card_h = min(card_h, Inches(2.1))

        for i, driver in enumerate(drivers[:3]):
            color = card_colors[i % len(card_colors)]
            y = card_y_start + i * card_h

            # Left accent bar
            accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), y + Inches(0.1), Inches(0.08), card_h - Inches(0.2))
            accent.fill.solid()
            accent.fill.fore_color.rgb = color
            accent.line.fill.background()

            # Number badge
            self._add_textbox(
                slide, Inches(1.05), y + Inches(0.12), Inches(0.5), Inches(0.45),
                text=f"0{i+1}", font_size=18, bold=True, color=color,
            )

            # Split driver into headline + detail (split on \n if present)
            parts = driver.split("\n", 1)
            headline = parts[0].strip()
            detail = parts[1].strip() if len(parts) > 1 else ""

            # Headline
            self._add_textbox(
                slide, Inches(1.6), y + Inches(0.1), Inches(11.0), Inches(0.5),
                text=headline, font_size=15, bold=True, color=Colors.PRIMARY_TEXT,
            )
            # Detail
            if detail:
                self._add_textbox(
                    slide, Inches(1.6), y + Inches(0.6), Inches(11.0), card_h - Inches(0.75),
                    text=detail, font_size=13, color=Colors.SECONDARY_TEXT,
                )

    def add_tco_slide(self, tco: dict):
        """Slide 4: TCO Comparison — table on blank slide.

        tco: dict from business-case.yaml with current_state and proposed_oci.
        """
        slide = self._add_blank_slide()

        self._add_title_bar(slide, "Total Cost of Ownership")

        # Subtitle
        horizon = tco.get("horizon_years", 3)
        self._add_textbox(
            slide, Inches(0.8), Inches(1.1), Inches(11), Inches(0.4),
            text=f"{horizon}-Year Comparison  |  Current State vs Oracle Cloud Infrastructure",
            font_size=13, color=Colors.TEAL, bold=True,
        )

        current = tco.get("current_state", {})
        proposed = tco.get("proposed_oci", {})
        savings = tco.get("savings", {})

        rows_data = [
            ("Infrastructure", current.get("annual_infrastructure", 0), proposed.get("annual_cloud_consumption", 0)),
            ("Licensing / Support", current.get("annual_licensing", 0), proposed.get("annual_licensing", 0)),
            ("Operations (People)", current.get("annual_operations", 0), proposed.get("annual_operations", 0)),
            ("Downtime Cost", current.get("annual_downtime_cost", 0), proposed.get("annual_downtime_cost", 0)),
            ("Compliance", current.get("annual_compliance_cost", 0), proposed.get("annual_compliance_cost", 0)),
        ]
        # Filter out zero rows
        rows_data = [(n, c, o) for n, c, o in rows_data if c or o]

        # Add migration one-time
        migration = proposed.get("migration_one_time", 0)

        num_rows = len(rows_data) + 3  # header + rows + annual total + horizon total
        table = self._add_table(
            slide, num_rows, 4,
            Inches(0.8), Inches(1.6),
            Inches(11.7), Inches(0.42 * num_rows),
        )
        table.columns[0].width = Inches(3.5)
        table.columns[1].width = Inches(2.7)
        table.columns[2].width = Inches(2.7)
        table.columns[3].width = Inches(2.8)

        # Header
        for j, h in enumerate(["Cost Category", "Current (Annual)", "OCI (Annual)", "Savings"]):
            self._style_table_cell(
                table.cell(0, j), h, font_size=11, bold=True,
                color=Colors.WHITE, bg_color=Colors.TEAL,
                alignment=PP_ALIGN.CENTER if j > 0 else PP_ALIGN.LEFT,
            )

        # Data rows
        for i, (name, curr, oci) in enumerate(rows_data):
            row = i + 1
            bg = Colors.TABLE_ALT_ROW if row % 2 == 0 else None
            curr_val = curr if isinstance(curr, (int, float)) else 0
            oci_val = oci if isinstance(oci, (int, float)) else 0
            save_val = curr_val - oci_val
            self._style_table_cell(table.cell(row, 0), name, font_size=10, bg_color=bg)
            self._style_table_cell(table.cell(row, 1), f"${curr_val:,.0f}", font_size=10, bg_color=bg, alignment=PP_ALIGN.RIGHT)
            self._style_table_cell(table.cell(row, 2), f"${oci_val:,.0f}", font_size=10, bg_color=bg, alignment=PP_ALIGN.RIGHT)
            save_color = Colors.SUCCESS if save_val > 0 else Colors.ERROR
            self._style_table_cell(table.cell(row, 3), f"${save_val:,.0f}", font_size=10, bold=True, color=save_color, bg_color=bg, alignment=PP_ALIGN.RIGHT)

        # Annual total row
        total_row = len(rows_data) + 1
        ann_current = current.get("total_annual", 0) or sum(r[1] for r in rows_data if isinstance(r[1], (int, float)))
        ann_oci = proposed.get("total_annual", 0) or sum(r[2] for r in rows_data if isinstance(r[2], (int, float)))
        ann_savings = savings.get("annual", 0) or (ann_current - ann_oci)
        self._style_table_cell(table.cell(total_row, 0), "TOTAL ANNUAL", font_size=11, bold=True, color=Colors.WHITE, bg_color=Colors.TEAL)
        self._style_table_cell(table.cell(total_row, 1), f"${ann_current:,.0f}", font_size=11, bold=True, color=Colors.WHITE, bg_color=Colors.TEAL, alignment=PP_ALIGN.RIGHT)
        self._style_table_cell(table.cell(total_row, 2), f"${ann_oci:,.0f}", font_size=11, bold=True, color=Colors.WHITE, bg_color=Colors.TEAL, alignment=PP_ALIGN.RIGHT)
        self._style_table_cell(table.cell(total_row, 3), f"${ann_savings:,.0f}", font_size=11, bold=True, color=Colors.WHITE, bg_color=Colors.TEAL, alignment=PP_ALIGN.RIGHT)

        # Horizon total row
        h_row = total_row + 1
        h_current = current.get("total_over_horizon", 0) or (ann_current * horizon)
        h_oci = proposed.get("total_over_horizon", 0) or (ann_oci * horizon + migration)
        h_savings = savings.get("over_horizon", 0) or (h_current - h_oci)
        pct = savings.get("percentage", 0) or (h_savings / h_current * 100 if h_current else 0)
        self._style_table_cell(table.cell(h_row, 0), f"TOTAL {horizon}-YEAR", font_size=11, bold=True, color=Colors.WHITE, bg_color=Colors.DARK_BG)
        self._style_table_cell(table.cell(h_row, 1), f"${h_current:,.0f}", font_size=11, bold=True, color=Colors.WHITE, bg_color=Colors.DARK_BG, alignment=PP_ALIGN.RIGHT)
        self._style_table_cell(table.cell(h_row, 2), f"${h_oci:,.0f}", font_size=11, bold=True, color=Colors.WHITE, bg_color=Colors.DARK_BG, alignment=PP_ALIGN.RIGHT)
        self._style_table_cell(table.cell(h_row, 3), f"${h_savings:,.0f} ({pct:.0f}%)", font_size=11, bold=True, color=Colors.GOLD, bg_color=Colors.DARK_BG, alignment=PP_ALIGN.RIGHT)

        # Migration note
        if migration:
            note_y = Inches(1.6) + Inches(0.42 * num_rows) + Inches(0.15)
            self._add_textbox(
                slide, Inches(0.8), note_y, Inches(11), Inches(0.3),
                text=f"* Includes one-time migration investment of ${migration:,.0f} in Year 1",
                font_size=9, italic=True, color=Colors.SECONDARY_TEXT,
            )

        # Assumptions
        assumptions = tco.get("assumptions", [])
        if assumptions:
            a_y = Inches(1.6) + Inches(0.42 * num_rows) + Inches(0.45)
            self._add_textbox(
                slide, Inches(0.8), a_y, Inches(11), Inches(0.25),
                text="Assumptions:", font_size=9, bold=True, color=Colors.SECONDARY_TEXT,
            )
            for idx, a in enumerate(assumptions[:4]):
                self._add_textbox(
                    slide, Inches(1.0), a_y + Inches(0.25 + idx * 0.22),
                    Inches(11), Inches(0.22),
                    text=f"• {a}", font_size=8, italic=True, color=Colors.SECONDARY_TEXT,
                )

    def add_roi_slide(self, roi: dict, headline: str = ""):
        """Slide 5: ROI — centered big number + 3 supporting metrics."""
        slide = self._add_blank_slide()

        self._add_title_bar(slide, "Return on Investment")

        # Big centered ROI number
        pct = roi.get("three_year_roi_pct", 0)
        metric_text = headline or (f"{pct:.0f}%" if pct else "—")
        big_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.7), Inches(2.4))
        big_box.text_frame.word_wrap = False
        p = big_box.text_frame.paragraphs[0]
        p.text = metric_text
        p.font.size = Pt(96)
        p.font.bold = True
        p.font.name = self.FONT_HEADING
        p.font.color.rgb = Colors.TEAL
        p.alignment = PP_ALIGN.CENTER

        # Label under big number
        self._add_textbox(
            slide, Inches(0.8), Inches(3.75), Inches(11.7), Inches(0.4),
            text="3-Year Return on Investment", font_size=16,
            color=Colors.SECONDARY_TEXT, alignment=PP_ALIGN.CENTER,
        )

        # 3 supporting metric boxes
        payback = roi.get("payback_months", 0)
        investment = roi.get("total_investment", 0)
        benefit = roi.get("annual_net_benefit", 0)
        metrics = []
        if payback:
            metrics.append((f"{payback} months", "Payback Period"))
        if investment:
            metrics.append((f"${investment:,.0f}", "Total Investment"))
        if benefit:
            metrics.append((f"${benefit:,.0f}/yr", "Annual Net Benefit"))

        box_w = Inches(3.5)
        gap = Inches(0.45)
        total_w = box_w * len(metrics) + gap * (len(metrics) - 1)
        x_start = (Inches(13.33) - total_w) / 2
        y_box = Inches(4.4)

        for j, (value, label) in enumerate(metrics):
            x = x_start + j * (box_w + gap)
            # Background
            bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y_box, box_w, Inches(1.4))
            bg.fill.solid()
            bg.fill.fore_color.rgb = Colors.TABLE_ALT_ROW
            bg.line.color.rgb = Colors.MUTED_TEAL

            # Value
            self._add_textbox(
                slide, x, y_box + Inches(0.15), box_w, Inches(0.7),
                text=value, font_size=26, bold=True, color=Colors.TEAL,
                alignment=PP_ALIGN.CENTER,
            )
            # Label
            self._add_textbox(
                slide, x, y_box + Inches(0.85), box_w, Inches(0.45),
                text=label, font_size=11, color=Colors.SECONDARY_TEXT,
                alignment=PP_ALIGN.CENTER,
            )

    def add_value_drivers_slide(self, drivers: list):
        """Slide 6: Value Drivers — 4 categories on blank slide.

        drivers: list of {"category": str, "title": str, "description": str, "quantified": str}
        """
        slide = self._add_blank_slide()

        self._add_title_bar(slide, "Value Drivers")

        # 4 value cards in a 2x2 grid
        card_colors = [Colors.TEAL, Colors.FOREST, Colors.BURNT_ORANGE, Colors.ORACLE_RED]
        positions = [
            (Inches(0.8), Inches(1.5)),   # top-left
            (Inches(6.8), Inches(1.5)),   # top-right
            (Inches(0.8), Inches(4.3)),   # bottom-left
            (Inches(6.8), Inches(4.3)),   # bottom-right
        ]
        card_w, card_h = Inches(5.5), Inches(2.5)

        for i, driver in enumerate(drivers[:4]):
            x, y = positions[i]
            color = card_colors[i % len(card_colors)]

            # Color accent bar
            bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, Inches(0.08), card_h)
            bar.fill.solid()
            bar.fill.fore_color.rgb = color
            bar.line.fill.background()

            # Title
            title = driver.get("title", driver.get("category", "").replace("_", " ").title())
            self._add_textbox(
                slide, x + Inches(0.25), y + Inches(0.1),
                card_w - Inches(0.3), Inches(0.4),
                text=title, font_size=16, bold=True, color=color,
            )

            # Quantified value (big)
            quantified = driver.get("quantified", "")
            if quantified:
                self._add_textbox(
                    slide, x + Inches(0.25), y + Inches(0.55),
                    card_w - Inches(0.3), Inches(0.5),
                    text=quantified, font_size=22, bold=True, color=Colors.PRIMARY_TEXT,
                )

            # Description
            desc = driver.get("description", "")
            if desc:
                self._add_textbox(
                    slide, x + Inches(0.25), y + Inches(1.2),
                    card_w - Inches(0.3), Inches(1.0),
                    text=desc, font_size=11, color=Colors.SECONDARY_TEXT,
                )

    def add_risk_slide(self, migration_risks: list, do_nothing_risks: list):
        """Slide 7: Risk Assessment — two-column table layout."""
        slide = self._add_blank_slide()

        self._add_title_bar(slide, "Risk Assessment")

        col_w = Inches(5.6)
        col_gap = Inches(0.5)
        left_x = Inches(0.8)
        right_x = left_x + col_w + col_gap
        header_y = Inches(1.2)
        content_start_y = Inches(1.75)
        row_h = Inches(0.8)          # height per risk block (title + detail)
        slide_h = Inches(7.1)

        # Stretch rows to fill available slide height
        n_rows = max(len(migration_risks[:5]), len(do_nothing_risks[:5]))
        if n_rows > 0:
            available = slide_h - content_start_y
            row_h = min(Inches(1.8), available / n_rows)

        # Column header backgrounds
        for x, color, label in [
            (left_x,  Colors.TEAL,  "✓  Migration Risks (Mitigated)"),
            (right_x, Colors.ERROR, "⚠  Risks of Inaction"),
        ]:
            bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, header_y, col_w, Inches(0.45))
            bg.fill.solid()
            bg.fill.fore_color.rgb = color
            bg.line.fill.background()
            self._add_textbox(
                slide, x + Inches(0.15), header_y + Inches(0.05), col_w - Inches(0.2), Inches(0.38),
                text=label, font_size=13, bold=True, color=Colors.WHITE,
            )

        # Left column: migration risks
        for i, risk in enumerate(migration_risks[:5]):
            r_text = risk.get("risk", str(risk)) if isinstance(risk, dict) else str(risk)
            mitigation = risk.get("mitigation", "") if isinstance(risk, dict) else ""
            y = content_start_y + i * row_h

            # Alternating row background
            if i % 2 == 0:
                row_bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left_x, y, col_w, row_h)
                row_bg.fill.solid()
                row_bg.fill.fore_color.rgb = Colors.TABLE_ALT_ROW
                row_bg.line.fill.background()

            self._add_textbox(
                slide, left_x + Inches(0.15), y + Inches(0.07), col_w - Inches(0.25), Inches(0.4),
                text=f"• {r_text}", font_size=12, bold=True, color=Colors.PRIMARY_TEXT,
            )
            if mitigation:
                self._add_textbox(
                    slide, left_x + Inches(0.25), y + Inches(0.45), col_w - Inches(0.35), row_h - Inches(0.48),
                    text=f"Mitigation: {mitigation}", font_size=11,
                    italic=True, color=Colors.SECONDARY_TEXT,
                )

        # Right column: do-nothing risks
        for i, risk in enumerate(do_nothing_risks[:5]):
            r_text = risk.get("risk", str(risk)) if isinstance(risk, dict) else str(risk)
            impact = risk.get("impact", "") if isinstance(risk, dict) else ""
            timeline = risk.get("timeline", "") if isinstance(risk, dict) else ""
            y = content_start_y + i * row_h

            if i % 2 == 0:
                row_bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, right_x, y, col_w, row_h)
                row_bg.fill.solid()
                row_bg.fill.fore_color.rgb = RGBColor(0xFF, 0xF3, 0xF3)
                row_bg.line.fill.background()

            self._add_textbox(
                slide, right_x + Inches(0.15), y + Inches(0.07), col_w - Inches(0.25), Inches(0.4),
                text=f"• {r_text}", font_size=12, bold=True, color=Colors.ERROR,
            )
            detail_parts = []
            if impact:
                detail_parts.append(f"Impact: {impact}")
            if timeline:
                detail_parts.append(f"By: {timeline}")
            if detail_parts:
                self._add_textbox(
                    slide, right_x + Inches(0.25), y + Inches(0.45), col_w - Inches(0.35), row_h - Inches(0.48),
                    text="  |  ".join(detail_parts), font_size=10,
                    italic=True, color=Colors.SECONDARY_TEXT,
                )

    def add_roadmap_slide(self, phases: list, total_duration: str = ""):
        """Slide 8: Implementation Roadmap — timeline bars filling the slide."""
        slide = self._add_blank_slide()

        title = "Implementation Roadmap"
        if total_duration:
            title += f"  —  {total_duration}"
        self._add_title_bar(slide, title)

        phase_colors = [Colors.TEAL, Colors.BURNT_ORANGE, Colors.FOREST, Colors.ORACLE_RED]
        content_start = Inches(1.25)
        available_h = Inches(5.9)
        n = min(len(phases), 4)
        row_h = available_h / n if n else available_h

        bar_left = Inches(3.6)
        bar_w = Inches(9.1)
        label_w = Inches(2.6)

        for i, phase in enumerate(phases[:4]):
            color = phase_colors[i % len(phase_colors)]
            y = content_start + i * row_h
            name = pick(phase, "name", "title", default=f"Phase {i+1}")
            duration = pick(phase, "duration", "weeks")
            deliverables = pick_list(phase, "deliverables", "outputs")
            quick_wins = pick_list(phase, "quick_wins", "milestones")

            # Alternating row background
            if i % 2 == 0:
                bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), y, Inches(12.0), row_h - Inches(0.08))
                bg.fill.solid()
                bg.fill.fore_color.rgb = Colors.TABLE_ALT_ROW
                bg.line.fill.background()

            # Phase number circle accent
            dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.82), y + (row_h - Inches(0.38)) / 2, Inches(0.38), Inches(0.38))
            dot.fill.solid()
            dot.fill.fore_color.rgb = color
            dot.line.fill.background()
            dot.text_frame.paragraphs[0].text = str(i + 1)
            dot.text_frame.paragraphs[0].font.size = Pt(11)
            dot.text_frame.paragraphs[0].font.bold = True
            dot.text_frame.paragraphs[0].font.color.rgb = Colors.WHITE
            dot.text_frame.paragraphs[0].font.name = self.FONT
            dot.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

            # Phase name
            self._add_textbox(
                slide, Inches(1.35), y + Inches(0.08), label_w, Inches(0.45),
                text=name, font_size=14, bold=True, color=color,
            )

            # Duration bar
            bar_h = Inches(0.42)
            bar_y = y + (row_h - bar_h) / 2
            bar = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, bar_left, bar_y, bar_w * 0.55, bar_h)
            bar.fill.solid()
            bar.fill.fore_color.rgb = color
            bar.line.fill.background()
            bar.text_frame.paragraphs[0].text = duration
            bar.text_frame.paragraphs[0].font.size = Pt(12)
            bar.text_frame.paragraphs[0].font.bold = True
            bar.text_frame.paragraphs[0].font.color.rgb = Colors.WHITE
            bar.text_frame.paragraphs[0].font.name = self.FONT
            bar.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

            # Deliverables — listed to the right of the bar
            items = quick_wins + deliverables
            if items:
                items_text = "  •  ".join(items[:3])
                self._add_textbox(
                    slide, bar_left + bar_w * 0.57, bar_y - Inches(0.02),
                    bar_w * 0.43, bar_h + Inches(0.05),
                    text=items_text, font_size=11, color=Colors.SECONDARY_TEXT,
                )

    def add_recommendation_slide(self, summary: str, next_steps: list = None):
        """Slide 9: Recommendation — dark blank slide with controlled fonts."""
        slide = self._add_blank_slide(dark=True)

        # "Recommendation" label in gold
        self._add_textbox(
            slide, Inches(0.8), Inches(0.45), Inches(11.7), Inches(0.5),
            text="Our Recommendation", font_size=13, bold=True,
            color=Colors.GOLD, font_name=self.FONT,
        )

        # Gold accent bar
        acc = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.0), Inches(11.7), Inches(0.05))
        acc.fill.solid()
        acc.fill.fore_color.rgb = Colors.GOLD
        acc.line.fill.background()

        # Main recommendation statement — 20pt, white, readable
        rec_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.2), Inches(11.7), Inches(2.2))
        tf = rec_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = summary
        p.font.size = Pt(20)
        p.font.bold = True
        p.font.name = self.FONT_HEADING
        p.font.color.rgb = Colors.WHITE

        # Next steps section
        if next_steps:
            self._add_textbox(
                slide, Inches(0.8), Inches(3.6), Inches(4.0), Inches(0.4),
                text="NEXT STEPS", font_size=11, bold=True,
                color=Colors.GOLD,
            )
            # Divider
            div = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(4.05), Inches(11.7), Inches(0.03))
            div.fill.solid()
            div.fill.fore_color.rgb = RGBColor(0x55, 0x50, 0x4C)
            div.line.fill.background()

            y = Inches(4.15)
            for i, step in enumerate(next_steps[:4]):
                action = step.get("action", str(step)) if isinstance(step, dict) else str(step)
                owner = step.get("owner", "") if isinstance(step, dict) else ""
                deadline = step.get("deadline", "") if isinstance(step, dict) else ""

                # Number
                self._add_textbox(
                    slide, Inches(0.8), y, Inches(0.4), Inches(0.5),
                    text=str(i + 1), font_size=13, bold=True, color=Colors.GOLD,
                )
                # Action text
                action_text = action
                meta_parts = []
                if owner:
                    meta_parts.append(owner)
                if deadline:
                    meta_parts.append(deadline)
                meta = f"  [{' · '.join(meta_parts)}]" if meta_parts else ""
                self._add_textbox(
                    slide, Inches(1.25), y, Inches(11.2), Inches(0.5),
                    text=action_text + meta, font_size=13, color=Colors.WHITE,
                )
                y += Inches(0.6)

    # ================================================================
    # Build from YAML spec
    # ================================================================

    @classmethod
    def from_spec(cls, spec: dict, template: Optional[str] = None) -> "BusinessCaseDeckGenerator":
        """Build a complete business case deck from a YAML specification."""
        bc = spec.get("business_case", spec)  # Support both wrapped and unwrapped
        gen = cls(template=template)

        # Slide 1: Cover
        gen.add_cover_slide(
            customer=pick(bc, "customer_name", "customer"),
            subtitle="Business Case for Oracle Cloud Infrastructure",
            prepared_by=pick(bc, "prepared_by", "author"),
            date=pick(bc, "date", "generated_on"),
        )

        # Slide 2: Executive Summary
        exec_summary = bc.get("executive_summary", "")
        if exec_summary:
            gen.add_executive_summary_slide(exec_summary)

        # Slide 3: Business Drivers
        drivers_data = bc.get("drivers", {})
        # Accept primary_driver at the top level as well (common user shape)
        top_primary = pick(bc, "primary_driver", "main_driver")
        # Accept a plain string or list for drivers
        if isinstance(drivers_data, str):
            drivers_data = {"primary": drivers_data}
        elif isinstance(drivers_data, list):
            drivers_data = {"items": drivers_data}
        elif not isinstance(drivers_data, dict):
            drivers_data = {}

        if drivers_data or top_primary:
            driver_statements = []
            primary = pick(drivers_data, "primary", "primary_driver", "main_driver") or top_primary
            urgency = pick(drivers_data, "urgency", "why_now")
            coi = drivers_data.get("cost_of_inaction", {}) or {}

            if primary:
                primary_text = primary if isinstance(primary, str) else str(primary)
                # Only rewrite snake_case enum tokens ("compliance_driven"); leave natural
                # language intact so values like "Soberanía de datos + compliance regulatorio"
                # render verbatim.
                if "_" in primary_text and " " not in primary_text and len(primary_text) <= 40:
                    headline = f"Primary Driver: {primary_text.replace('_', ' ').title()}"
                else:
                    headline = primary_text
                driver_statements.append(f"{headline}\n{urgency}" if urgency else headline)

            # Spec-provided additional cards take precedence over the inaction fallback
            extra_items = pick_list(drivers_data, "items", "additional", "secondary", "cards")
            for item in extra_items:
                if isinstance(item, str) and item.strip():
                    driver_statements.append(item.strip())
                elif isinstance(item, dict):
                    label = pick(item, "label", "headline", "title", "name")
                    desc = pick(item, "detail", "description", "text", "body")
                    if label and desc:
                        driver_statements.append(f"{label}\n{desc}")
                    elif label or desc:
                        driver_statements.append(label or desc)

            if not extra_items:
                financial = pick(coi, "financial")
                operational = pick(coi, "operational")
                strategic = pick(coi, "strategic")
                if financial:
                    driver_statements.append(f"Financial Impact of Inaction\n{financial}")
                if operational:
                    driver_statements.append(f"Operational Impact\n{operational}")
                elif strategic:
                    driver_statements.append(f"Strategic Risk\n{strategic}")

            if driver_statements:
                gen.add_business_drivers_slide(driver_statements)

        # Slide 4: TCO Comparison
        tco = bc.get("tco", {})
        if tco and (tco.get("current_state") or tco.get("proposed_oci")):
            gen.add_tco_slide(tco)

        # Slide 5: ROI
        roi = bc.get("roi", {})
        if roi and any(roi.get(k) for k in ["three_year_roi_pct", "payback_months", "total_investment"]):
            gen.add_roi_slide(roi)

        # Slide 6: Value Drivers
        value_drivers = bc.get("value_drivers", [])
        if value_drivers:
            gen.add_value_drivers_slide(value_drivers)

        # Slide 7: Risk Assessment
        risks = bc.get("risks", {})
        migration_risks = pick_list(risks, "migration_risks")
        do_nothing_risks = pick_list(risks, "do_nothing_risks")
        if migration_risks or do_nothing_risks:
            gen.add_risk_slide(migration_risks, do_nothing_risks)

        # Slide 8: Roadmap
        roadmap = bc.get("roadmap", {})
        if roadmap.get("phases"):
            gen.add_roadmap_slide(
                phases=pick_list(roadmap, "phases"),
                total_duration=pick(roadmap, "total_duration"),
            )

        # Slide 9: Recommendation
        rec = bc.get("recommendation", {})
        if rec:
            summary = pick(rec, "summary")
            if not summary and rec.get("commitment_amount"):
                summary = f"Recommended: {rec['commitment_amount']} {rec.get('commitment_type', 'UCM')} commitment"
            if summary:
                gen.add_recommendation_slide(
                    summary=summary,
                    next_steps=pick_list(rec, "next_steps"),
                )

        return gen


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate OCI business case slide deck (.pptx)"
    )
    parser.add_argument(
        "--spec", required=True,
        help="Path to YAML business case spec file",
    )
    parser.add_argument(
        "--output", default="business-case.pptx",
        help="Output .pptx file path",
    )
    parser.add_argument(
        "--template",
        help="Path to Oracle FY26 .pptx template (default: templates/Oracle_PPT-template_FY26.pptx)",
    )
    args = parser.parse_args()

    with open(args.spec, 'r') as f:
        spec = yaml.safe_load(f)

    gen = BusinessCaseDeckGenerator.from_spec(spec, template=args.template)
    gen.save(args.output)

    print(f"Generated: {args.output}")
    print(f"  Slides: {gen.slide_count}")
    print(f"  Template: Oracle FY26")
    customer = spec.get("business_case", spec).get("customer_name", "")
    if customer:
        print(f"  Customer: {customer}")


if __name__ == "__main__":
    main()
