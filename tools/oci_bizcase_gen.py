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
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE


# ============================================================
# Oracle Redwood Design System Colors
# ============================================================

class Colors:
    DARK_BG = RGBColor(0x31, 0x2D, 0x2A)
    PRIMARY_TEXT = RGBColor(0x31, 0x2D, 0x2A)
    SECONDARY_TEXT = RGBColor(0x6F, 0x69, 0x64)
    WHITE = RGBColor(0xFF, 0xFF, 0xFF)
    WARM_BG = RGBColor(0xFC, 0xFB, 0xFA)
    ORACLE_RED = RGBColor(0xC7, 0x46, 0x34)
    GOLD = RGBColor(0xFA, 0xCD, 0x62)
    TEAL = RGBColor(0x2C, 0x59, 0x67)
    SAGE = RGBColor(0x75, 0x9C, 0x6C)
    FOREST = RGBColor(0x2B, 0x62, 0x42)
    MUTED_TEAL = RGBColor(0x94, 0xAF, 0xAF)
    BURNT_ORANGE = RGBColor(0xAE, 0x56, 0x2C)
    TABLE_ALT_ROW = RGBColor(0xF5, 0xF4, 0xF2)
    TABLE_HEADER_BG = RGBColor(0x2C, 0x59, 0x67)
    SUCCESS = RGBColor(0x2B, 0x62, 0x42)
    WARNING = RGBColor(0xAE, 0x56, 0x2C)
    ERROR = RGBColor(0xC7, 0x46, 0x34)


# ============================================================
# Oracle FY26 Template Layout Indices
# ============================================================

class Layouts:
    """Layout indices from Oracle_PPT-template_FY26.pptx (104 layouts)."""
    COVER_DARK = 0              # Dark - Title_Pillar
    COVER_LIGHT = 1             # Light - Title_Pillar
    DIVIDER_LIGHT = 16          # Light - Divider
    DIVIDER_DARK = 17           # Dark - Divider
    IMPACT_DARK = 26            # Dark - Impact Statement
    IMPACT_LIGHT = 27           # Light - Impact Statement
    METRIC_DARK = 32            # Dark - Single metric
    METRIC_LIGHT = 33           # Light - Single metric
    MULTI_STATEMENT_DARK = 47   # Multi Statement – Dark
    MULTI_STATEMENT_LIGHT = 48  # Multi Statement – Light
    TWO_COL_LIGHT = 66          # Light - Title/Subtitle 2 Column
    TWO_COL_DARK = 67           # Dark - Title/Subtitle 2 Column
    FOUR_ICONS_LIGHT = 82       # Light - 4 Icons, Subhead and text
    BLANK_DARK = 84             # Dark - Blank
    BLANK_LIGHT = 85            # Light - Blank
    SAFE_HARBOR_LIGHT = 96      # Light - Safe harbor - short (if exists)


# ============================================================
# Business Case Deck Generator
# ============================================================

class BusinessCaseDeckGenerator:
    """Generate business case decks using Oracle FY26 template layouts."""

    TEMPLATE_PATH = Path(__file__).parent.parent / "templates" / "Oracle_PPT-template_FY26.pptx"
    FONT = "Oracle Sans"
    FONT_HEADING = "Georgia"

    def __init__(self, template: Optional[str] = None):
        tmpl = template or str(self.TEMPLATE_PATH)
        if not Path(tmpl).is_file():
            raise FileNotFoundError(f"Template not found: {tmpl}")
        self.prs = Presentation(tmpl)
        self._clear_slides()

    def _clear_slides(self):
        """Remove all existing slides from the template (keep layouts/masters)."""
        while len(self.prs.slides) > 0:
            rId = self.prs.slides._sldIdLst[0].get(
                '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'
            )
            self.prs.part.drop_rel(rId)
            self.prs.slides._sldIdLst.remove(self.prs.slides._sldIdLst[0])
        # Clean sections
        from lxml import etree
        ns_p14 = 'http://schemas.microsoft.com/office/powerpoint/2010/main'
        for sectionLst in self.prs.part._element.findall(f'.//{{{ns_p14}}}sectionLst'):
            sectionLst.getparent().remove(sectionLst)

    def _add_layout_slide(self, layout_index: int):
        """Add a slide using a specific template layout."""
        layout = self.prs.slide_layouts[layout_index]
        return self.prs.slides.add_slide(layout)

    def _set_placeholder(self, slide, idx: int, text: str):
        """Set text in a placeholder by index. Silently skips if not found."""
        for ph in slide.placeholders:
            if ph.placeholder_format.idx == idx:
                ph.text = text
                return ph
        return None

    def _style_placeholder(self, slide, idx: int, text: str,
                           font_size: int = None, bold: bool = None,
                           color: RGBColor = None):
        """Set text and style a placeholder."""
        ph = self._set_placeholder(slide, idx, text)
        if ph and ph.text_frame.paragraphs:
            for p in ph.text_frame.paragraphs:
                if font_size:
                    p.font.size = Pt(font_size)
                if bold is not None:
                    p.font.bold = bold
                if color:
                    p.font.color.rgb = color
        return ph

    def _add_blank_slide(self, dark: bool = False):
        """Add a blank slide (light or dark)."""
        idx = Layouts.BLANK_DARK if dark else Layouts.BLANK_LIGHT
        return self._add_layout_slide(idx)

    def _add_textbox(self, slide, left, top, width, height,
                     text="", font_size=12, bold=False, italic=False,
                     color=None, alignment=PP_ALIGN.LEFT, font_name=None):
        """Add a text box to a slide."""
        txBox = slide.shapes.add_textbox(left, top, width, height)
        tf = txBox.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = text
        p.font.size = Pt(font_size)
        p.font.bold = bold
        p.font.italic = italic
        p.font.name = font_name or self.FONT
        p.font.color.rgb = color or Colors.PRIMARY_TEXT
        p.alignment = alignment
        return txBox

    def _add_paragraph(self, text_frame, text="", font_size=12,
                       bold=False, color=None, space_before=0):
        """Add a paragraph to an existing text frame."""
        p = text_frame.add_paragraph()
        p.text = text
        p.font.size = Pt(font_size)
        p.font.bold = bold
        p.font.name = self.FONT
        p.font.color.rgb = color or Colors.PRIMARY_TEXT
        if space_before:
            p.space_before = Pt(space_before)
        return p

    def _add_table(self, slide, rows, cols, left, top, width, height):
        """Add a table to a slide."""
        return slide.shapes.add_table(rows, cols, left, top, width, height).table

    def _style_cell(self, cell, text, font_size=10, bold=False,
                    color=None, bg_color=None, alignment=PP_ALIGN.LEFT):
        """Style a table cell."""
        cell.text = text
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(font_size)
            p.font.bold = bold
            p.font.name = self.FONT
            p.font.color.rgb = color or Colors.PRIMARY_TEXT
            p.alignment = alignment
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        if bg_color:
            cell.fill.solid()
            cell.fill.fore_color.rgb = bg_color

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
        """Slide 2: Executive Summary — bold impact statement."""
        slide = self._add_layout_slide(Layouts.IMPACT_LIGHT)
        self._set_placeholder(slide, 0, statement)

    def add_business_drivers_slide(self, drivers: list):
        """Slide 3: Business Drivers — 3 key statements.

        drivers: list of up to 3 strings, each a driver statement.
        """
        slide = self._add_layout_slide(Layouts.MULTI_STATEMENT_LIGHT)
        # Multi Statement layout has placeholders idx 17, 18, 19 for 3 text blocks
        for i, driver in enumerate(drivers[:3]):
            self._set_placeholder(slide, 17 + i, driver)

    def add_tco_slide(self, tco: dict):
        """Slide 4: TCO Comparison — table on blank slide.

        tco: dict from business-case.yaml with current_state and proposed_oci.
        """
        slide = self._add_blank_slide()

        # Title
        self._add_textbox(
            slide, Inches(0.8), Inches(0.4), Inches(11), Inches(0.7),
            text="Total Cost of Ownership", font_size=24, bold=True,
            font_name=self.FONT_HEADING,
        )
        # Subtitle
        horizon = tco.get("horizon_years", 3)
        self._add_textbox(
            slide, Inches(0.8), Inches(1.0), Inches(11), Inches(0.4),
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
            self._style_cell(
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
            self._style_cell(table.cell(row, 0), name, font_size=10, bg_color=bg)
            self._style_cell(table.cell(row, 1), f"${curr_val:,.0f}", font_size=10, bg_color=bg, alignment=PP_ALIGN.RIGHT)
            self._style_cell(table.cell(row, 2), f"${oci_val:,.0f}", font_size=10, bg_color=bg, alignment=PP_ALIGN.RIGHT)
            save_color = Colors.SUCCESS if save_val > 0 else Colors.ERROR
            self._style_cell(table.cell(row, 3), f"${save_val:,.0f}", font_size=10, bold=True, color=save_color, bg_color=bg, alignment=PP_ALIGN.RIGHT)

        # Annual total row
        total_row = len(rows_data) + 1
        ann_current = current.get("total_annual", 0) or sum(r[1] for r in rows_data if isinstance(r[1], (int, float)))
        ann_oci = proposed.get("total_annual", 0) or sum(r[2] for r in rows_data if isinstance(r[2], (int, float)))
        ann_savings = savings.get("annual", 0) or (ann_current - ann_oci)
        self._style_cell(table.cell(total_row, 0), "TOTAL ANNUAL", font_size=11, bold=True, color=Colors.WHITE, bg_color=Colors.TEAL)
        self._style_cell(table.cell(total_row, 1), f"${ann_current:,.0f}", font_size=11, bold=True, color=Colors.WHITE, bg_color=Colors.TEAL, alignment=PP_ALIGN.RIGHT)
        self._style_cell(table.cell(total_row, 2), f"${ann_oci:,.0f}", font_size=11, bold=True, color=Colors.WHITE, bg_color=Colors.TEAL, alignment=PP_ALIGN.RIGHT)
        self._style_cell(table.cell(total_row, 3), f"${ann_savings:,.0f}", font_size=11, bold=True, color=Colors.WHITE, bg_color=Colors.TEAL, alignment=PP_ALIGN.RIGHT)

        # Horizon total row
        h_row = total_row + 1
        h_current = current.get("total_over_horizon", 0) or (ann_current * horizon)
        h_oci = proposed.get("total_over_horizon", 0) or (ann_oci * horizon + migration)
        h_savings = savings.get("over_horizon", 0) or (h_current - h_oci)
        pct = savings.get("percentage", 0) or (h_savings / h_current * 100 if h_current else 0)
        self._style_cell(table.cell(h_row, 0), f"TOTAL {horizon}-YEAR", font_size=11, bold=True, color=Colors.WHITE, bg_color=Colors.DARK_BG)
        self._style_cell(table.cell(h_row, 1), f"${h_current:,.0f}", font_size=11, bold=True, color=Colors.WHITE, bg_color=Colors.DARK_BG, alignment=PP_ALIGN.RIGHT)
        self._style_cell(table.cell(h_row, 2), f"${h_oci:,.0f}", font_size=11, bold=True, color=Colors.WHITE, bg_color=Colors.DARK_BG, alignment=PP_ALIGN.RIGHT)
        self._style_cell(table.cell(h_row, 3), f"${h_savings:,.0f} ({pct:.0f}%)", font_size=11, bold=True, color=Colors.GOLD, bg_color=Colors.DARK_BG, alignment=PP_ALIGN.RIGHT)

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

        # Title
        self._add_textbox(
            slide, Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.6),
            text="Return on Investment", font_size=24, bold=True,
            font_name=self.FONT_HEADING,
        )

        # Teal accent bar under title
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.05), Inches(11.7), Inches(0.05))
        bar.fill.solid()
        bar.fill.fore_color.rgb = Colors.TEAL
        bar.line.fill.background()

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

        self._add_textbox(
            slide, Inches(0.8), Inches(0.4), Inches(11), Inches(0.7),
            text="Value Drivers", font_size=24, bold=True,
            font_name=self.FONT_HEADING,
        )

        # 4 value cards in a 2x2 grid
        card_colors = [Colors.TEAL, Colors.FOREST, Colors.BURNT_ORANGE, Colors.ORACLE_RED]
        icons = {"cost_reduction": "$", "risk_reduction": "!", "agility": ">", "innovation": "*"}
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

        # Title
        self._add_textbox(
            slide, Inches(0.8), Inches(0.35), Inches(11.7), Inches(0.6),
            text="Risk Assessment", font_size=24, bold=True,
            font_name=self.FONT_HEADING,
        )

        col_w = Inches(5.6)
        col_gap = Inches(0.5)
        left_x = Inches(0.8)
        right_x = left_x + col_w + col_gap
        header_y = Inches(1.1)
        content_start_y = Inches(1.65)
        row_h = Inches(0.8)          # height per risk block (title + detail)
        slide_h = Inches(7.1)

        # Calculate available rows based on the tallest list
        n_rows = max(len(migration_risks[:5]), len(do_nothing_risks[:5]))
        # Stretch rows to fill slide
        if n_rows > 0:
            available = slide_h - content_start_y
            row_h = min(Inches(1.2), available / n_rows)

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
                    text=f"Mitigation: {mitigation}", font_size=10,
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
        """Slide 8: Implementation Roadmap — timeline bars."""
        slide = self._add_blank_slide()

        title = "Implementation Roadmap"
        if total_duration:
            title += f"  ({total_duration})"
        self._add_textbox(
            slide, Inches(0.8), Inches(0.4), Inches(11), Inches(0.7),
            text=title, font_size=24, bold=True,
            font_name=self.FONT_HEADING,
        )

        phase_colors = [Colors.TEAL, Colors.BURNT_ORANGE, Colors.FOREST, Colors.ORACLE_RED]
        y = Inches(1.6)
        bar_left = Inches(3.5)
        bar_max_width = Inches(9.0)

        for i, phase in enumerate(phases[:4]):
            color = phase_colors[i % len(phase_colors)]
            name = phase.get("name", f"Phase {i+1}")
            duration = phase.get("duration", "")
            deliverables = phase.get("deliverables", [])
            quick_wins = phase.get("quick_wins", [])

            # Phase label
            self._add_textbox(
                slide, Inches(0.8), y, Inches(2.5), Inches(0.5),
                text=name, font_size=13, bold=True,
            )

            # Duration bar
            bar = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                bar_left, y + Inches(0.05), bar_max_width * 0.85, Inches(0.4),
            )
            bar.fill.solid()
            bar.fill.fore_color.rgb = color
            bar.line.fill.background()
            bar.text_frame.paragraphs[0].text = duration
            bar.text_frame.paragraphs[0].font.size = Pt(10)
            bar.text_frame.paragraphs[0].font.color.rgb = Colors.WHITE
            bar.text_frame.paragraphs[0].font.name = self.FONT
            bar.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

            # Deliverables
            items = quick_wins + deliverables
            if items:
                items_text = " • ".join(items[:4])
                self._add_textbox(
                    slide, bar_left, y + Inches(0.5),
                    bar_max_width, Inches(0.3),
                    text=items_text, font_size=9, italic=True,
                    color=Colors.SECONDARY_TEXT,
                )

            y += Inches(1.1)

    def add_recommendation_slide(self, summary: str, next_steps: list = None):
        """Slide 9: Recommendation — bold ask on dark background."""
        slide = self._add_layout_slide(Layouts.IMPACT_DARK)
        self._set_placeholder(slide, 0, summary)

        # Add next steps as textbox if provided
        if next_steps:
            y = Inches(4.5)
            for i, step in enumerate(next_steps[:4]):
                action = step.get("action", str(step)) if isinstance(step, dict) else str(step)
                owner = step.get("owner", "") if isinstance(step, dict) else ""
                text = f"{i+1}. {action}"
                if owner:
                    text += f"  [{owner}]"
                self._add_textbox(
                    slide, Inches(0.8), y, Inches(11), Inches(0.4),
                    text=text, font_size=14, color=Colors.WHITE,
                )
                y += Inches(0.45)

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
            customer=bc.get("customer_name", ""),
            subtitle="Business Case for Oracle Cloud Infrastructure",
            prepared_by=bc.get("prepared_by", ""),
            date=bc.get("date", ""),
        )

        # Slide 2: Executive Summary
        exec_summary = bc.get("executive_summary", "")
        if exec_summary:
            gen.add_executive_summary_slide(exec_summary)

        # Slide 3: Business Drivers
        drivers_data = bc.get("drivers", {})
        if drivers_data:
            driver_statements = []
            primary = drivers_data.get("primary", "")
            urgency = drivers_data.get("urgency", "")
            coi = drivers_data.get("cost_of_inaction", {})

            if primary:
                driver_statements.append(f"Primary Driver: {primary.replace('_', ' ').title()}\n{urgency}" if urgency else primary.replace('_', ' ').title())
            if coi.get("financial"):
                driver_statements.append(f"Financial Impact of Inaction\n{coi['financial']}")
            if coi.get("operational"):
                driver_statements.append(f"Operational Impact\n{coi['operational']}")
            elif coi.get("strategic"):
                driver_statements.append(f"Strategic Risk\n{coi['strategic']}")

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
        migration_risks = risks.get("migration_risks", [])
        do_nothing_risks = risks.get("do_nothing_risks", [])
        if migration_risks or do_nothing_risks:
            gen.add_risk_slide(migration_risks, do_nothing_risks)

        # Slide 8: Roadmap
        roadmap = bc.get("roadmap", {})
        if roadmap.get("phases"):
            gen.add_roadmap_slide(
                phases=roadmap["phases"],
                total_duration=roadmap.get("total_duration", ""),
            )

        # Slide 9: Recommendation
        rec = bc.get("recommendation", {})
        if rec:
            summary = rec.get("summary", "")
            if not summary and rec.get("commitment_amount"):
                summary = f"Recommended: {rec['commitment_amount']} {rec.get('commitment_type', 'UCM')} commitment"
            if summary:
                gen.add_recommendation_slide(
                    summary=summary,
                    next_steps=rec.get("next_steps", []),
                )

        return gen

    # ================================================================
    # Save
    # ================================================================

    def save(self, filepath: str):
        """Save the presentation to a .pptx file."""
        self.prs.save(filepath)

    @property
    def slide_count(self):
        return len(self.prs.slides)


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
