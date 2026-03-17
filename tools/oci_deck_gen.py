#!/usr/bin/env python3
"""
OCI Deal Accelerator — Slide Deck Generator (.pptx)

Produces a 10-12 slide architecture proposal deck using the Oracle Redwood
design system colors and typography. Supports an optional --template flag
to inherit theme/fonts from an external .pptx (e.g. Oracle Icon Library).

Usage:
    python oci_deck_gen.py --spec proposal-data.yaml --output proposal.pptx
    python oci_deck_gen.py --spec proposal-data.yaml --output proposal.pptx \\
        --template "path/to/Oracle Database Icon Library.pptx"

Or import and use programmatically:
    from oci_deck_gen import OCIDeckGenerator
    gen = OCIDeckGenerator(customer="Acme Corp", project="DB Migration")
    gen.add_summary_slide(...)
    gen.save("proposal.pptx")
"""

import yaml
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE


# ============================================================
# Oracle Redwood Design System Colors
# Source: Oracle Database Icon Library [July 2024] — theme RMIL_Master
# Color scheme: "Oracle Redwood"
# ============================================================

class Colors:
    # Primary text — never pure black
    DARK_BG = RGBColor(0x31, 0x2D, 0x2A)       # #312D2A — dk1
    PRIMARY_TEXT = RGBColor(0x31, 0x2D, 0x2A)    # #312D2A — dk1
    SECONDARY_TEXT = RGBColor(0x6F, 0x69, 0x64)  # #6F6964 — Neutral 60
    WHITE = RGBColor(0xFF, 0xFF, 0xFF)
    WARM_BG = RGBColor(0xFC, 0xFB, 0xFA)         # #FCFBFA — lt1, content bg

    # Oracle Redwood accent palette
    ORACLE_RED = RGBColor(0xC7, 0x46, 0x34)      # #C74634 — accent1, primary brand
    GOLD = RGBColor(0xFA, 0xCD, 0x62)            # #FACD62 — accent2
    TEAL = RGBColor(0x2C, 0x59, 0x67)            # #2C5967 — hlink, tables/links
    SAGE = RGBColor(0x75, 0x9C, 0x6C)            # #759C6C — accent6
    FOREST = RGBColor(0x2B, 0x62, 0x42)          # #2B6242 — accent4
    MUTED_TEAL = RGBColor(0x94, 0xAF, 0xAF)      # #94AFAF — accent3
    BURNT_ORANGE = RGBColor(0xAE, 0x56, 0x2C)    # #AE562C — accent5

    # OCI service category colors (unchanged from architecture diagrams)
    COPPER = RGBColor(0xAA, 0x64, 0x3B)          # #AA643B — database
    PURPLE = RGBColor(0x80, 0x49, 0x98)          # #804998 — integration

    # Status
    SUCCESS = RGBColor(0x2B, 0x62, 0x42)         # #2B6242 — forest green
    WARNING = RGBColor(0xAE, 0x56, 0x2C)         # #AE562C — burnt orange
    ERROR = RGBColor(0xC7, 0x46, 0x34)           # #C74634 — Oracle red

    # Table
    TABLE_ALT_ROW = RGBColor(0xF5, 0xF4, 0xF2)  # #F5F4F2 — Neutral 10
    TABLE_HEADER_BG = RGBColor(0x2C, 0x59, 0x67) # teal


# ============================================================
# Slide Generator
# ============================================================

class OCIDeckGenerator:
    """Generate Oracle Redwood-styled architecture proposal slide decks."""

    SLIDE_WIDTH = Inches(13.333)   # Widescreen 16:9
    SLIDE_HEIGHT = Inches(7.5)
    MARGIN = Inches(0.5)
    # Oracle Redwood typography
    FONT_HEADING = "Georgia"
    FONT_BODY = "Oracle Sans"
    # Fallback chain: if Oracle Sans not installed, degrade gracefully
    FONT_BODY_FALLBACK = "Segoe UI"
    FONT = "Oracle Sans"  # default used by helpers

    def __init__(self, customer: str = "", project: str = "",
                 architect: str = "", firm: str = "",
                 template: Optional[str] = None):
        if template and Path(template).is_file():
            self.prs = Presentation(template)
            # Remove all existing slides (keep theme/masters)
            while len(self.prs.slides) > 0:
                rId = self.prs.slides._sldIdLst[0].get(
                    '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'
                )
                self.prs.part.drop_rel(rId)
                self.prs.slides._sldIdLst.remove(self.prs.slides._sldIdLst[0])
            # Remove inherited sections (e.g. "HCM", "Health", "CX icons"
            # from icon library templates)
            from lxml import etree
            prs_elem = self.prs.part._element
            ns_p14 = 'http://schemas.microsoft.com/office/powerpoint/2010/main'
            for sectionLst in prs_elem.findall(f'.//{{{ns_p14}}}sectionLst'):
                sectionLst.getparent().remove(sectionLst)
        else:
            self.prs = Presentation()
        self.prs.slide_width = self.SLIDE_WIDTH
        self.prs.slide_height = self.SLIDE_HEIGHT
        self.customer = customer
        self.project = project
        self.architect = architect
        self.firm = firm
        self._using_template = template and Path(template).is_file()

    # ---- Helpers ----

    def _find_blank_layout(self):
        """Find a blank or minimal slide layout."""
        # Try known blank layout names first
        for layout in self.prs.slide_layouts:
            if layout.name.lower() in ("blank", "blank slide"):
                return layout
        # For template-based: pick layout with fewest placeholders
        if self._using_template:
            best = min(self.prs.slide_layouts,
                       key=lambda l: len(list(l.placeholders)))
            return best
        # Default: layout index 6 (standard blank in python-pptx default)
        if len(self.prs.slide_layouts) > 6:
            return self.prs.slide_layouts[6]
        return self.prs.slide_layouts[-1]

    def _add_blank_slide(self, warm_bg: bool = True):
        """Add a blank slide with optional warm off-white background."""
        layout = self._find_blank_layout()
        slide = self.prs.slides.add_slide(layout)
        # Remove all inherited placeholder shapes (template layouts may
        # carry icon grids, footer fields, etc. that clutter the slide)
        if self._using_template:
            ns_p = 'http://schemas.openxmlformats.org/presentationml/2006/main'
            spTree = slide.shapes._spTree
            for sp in list(spTree):
                # Find <p:ph> anywhere inside the shape — marks it as a
                # layout-inherited placeholder (title, picture, body, etc.)
                if sp.find(f'.//{{{ns_p}}}ph') is not None:
                    spTree.remove(sp)
        if warm_bg:
            bg = slide.background
            fill = bg.fill
            fill.solid()
            fill.fore_color.rgb = Colors.WARM_BG
        return slide

    def _resolve_font(self, font_name=None, is_heading=False):
        """Resolve font name with fallback chain."""
        if font_name:
            return font_name
        return self.FONT_HEADING if is_heading else self.FONT

    def _add_textbox(self, slide, left, top, width, height,
                     text="", font_size=12, bold=False, italic=False,
                     color=None, alignment=PP_ALIGN.LEFT,
                     font_name=None, is_heading=False):
        """Add a text box to a slide."""
        txBox = slide.shapes.add_textbox(left, top, width, height)
        tf = txBox.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = text
        p.font.size = Pt(font_size)
        p.font.bold = bold
        p.font.italic = italic
        p.font.name = self._resolve_font(font_name, is_heading)
        p.font.color.rgb = color or Colors.PRIMARY_TEXT
        p.alignment = alignment
        return txBox

    def _add_paragraph(self, text_frame, text="", font_size=12,
                       bold=False, italic=False, color=None,
                       alignment=PP_ALIGN.LEFT, space_before=0,
                       space_after=0, bullet=False):
        """Add a paragraph to an existing text frame."""
        p = text_frame.add_paragraph()
        p.text = text
        p.font.size = Pt(font_size)
        p.font.bold = bold
        p.font.italic = italic
        p.font.name = self.FONT
        p.font.color.rgb = color or Colors.PRIMARY_TEXT
        p.alignment = alignment
        if space_before:
            p.space_before = Pt(space_before)
        if space_after:
            p.space_after = Pt(space_after)
        if bullet:
            p.level = 0
        return p

    def _add_rect(self, slide, left, top, width, height,
                  fill_color=None, border_color=None):
        """Add a rectangle shape."""
        shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, left, top, width, height
        )
        if fill_color:
            shape.fill.solid()
            shape.fill.fore_color.rgb = fill_color
        else:
            shape.fill.background()
        if border_color:
            shape.line.color.rgb = border_color
        else:
            shape.line.fill.background()
        return shape

    def _add_table(self, slide, rows, cols, left, top, width, height):
        """Add a table to a slide."""
        table_shape = slide.shapes.add_table(rows, cols, left, top, width, height)
        table = table_shape.table
        return table

    def _style_table_cell(self, cell, text, font_size=10, bold=False,
                          color=None, bg_color=None, alignment=PP_ALIGN.LEFT):
        """Style a table cell."""
        cell.text = text
        for paragraph in cell.text_frame.paragraphs:
            paragraph.font.size = Pt(font_size)
            paragraph.font.bold = bold
            paragraph.font.name = self.FONT
            paragraph.font.color.rgb = color or Colors.PRIMARY_TEXT
            paragraph.alignment = alignment
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        if bg_color:
            cell.fill.solid()
            cell.fill.fore_color.rgb = bg_color

    def _add_title_bar(self, slide, title_text):
        """Add a consistent title bar at top of content slides."""
        # Title text — Georgia heading font
        self._add_textbox(
            slide, self.MARGIN, Inches(0.3),
            Inches(10), Inches(0.6),
            text=title_text, font_size=24, bold=True,
            color=Colors.PRIMARY_TEXT, is_heading=True,
        )
        # Oracle Red accent line under title
        self._add_rect(
            slide, self.MARGIN, Inches(0.85),
            Inches(2), Inches(0.04),
            fill_color=Colors.ORACLE_RED,
        )

    # ---- Slide Methods ----

    def add_title_slide(self, subtitle: str = ""):
        """Slide 1: Title slide with dark background."""
        slide = self._add_blank_slide(warm_bg=False)

        # Dark background
        self._add_rect(
            slide, Inches(0), Inches(0),
            self.SLIDE_WIDTH, self.SLIDE_HEIGHT,
            fill_color=Colors.DARK_BG,
        )

        # Oracle Red accent bar (vertical)
        self._add_rect(
            slide, Inches(0.8), Inches(2.2),
            Inches(0.08), Inches(2.5),
            fill_color=Colors.ORACLE_RED,
        )

        # Customer name — Georgia heading
        title = f"{self.customer}" if self.customer else "Architecture Proposal"
        self._add_textbox(
            slide, Inches(1.2), Inches(2.2),
            Inches(10), Inches(0.7),
            text=title, font_size=32, bold=True,
            color=Colors.WHITE, is_heading=True,
        )

        # Project name — body font
        if self.project:
            self._add_textbox(
                slide, Inches(1.2), Inches(2.9),
                Inches(10), Inches(0.6),
                text=self.project, font_size=22,
                color=Colors.WHITE,
            )

        # Subtitle
        date_str = datetime.now().strftime("%B %Y")
        sub = subtitle or f"Architecture Proposal — {date_str}"
        self._add_textbox(
            slide, Inches(1.2), Inches(3.6),
            Inches(10), Inches(0.5),
            text=sub, font_size=16,
            color=RGBColor(0x9E, 0x98, 0x92),  # muted gray
        )

        # Architect / Firm
        if self.architect or self.firm:
            info = f"{self.architect}"
            if self.firm:
                info += f"  |  {self.firm}" if self.architect else self.firm
            self._add_textbox(
                slide, Inches(1.2), Inches(5.5),
                Inches(10), Inches(0.4),
                text=info, font_size=12,
                color=RGBColor(0x9E, 0x98, 0x92),
            )

        # "Prepared with OCI Deal Accelerator"
        self._add_textbox(
            slide, Inches(1.2), Inches(6.2),
            Inches(10), Inches(0.3),
            text="Prepared with OCI Deal Accelerator", font_size=9,
            italic=True, color=RGBColor(0x6F, 0x69, 0x64),
        )

    def add_summary_slide(self, why: str, current_state: list,
                          target_state: str, timeline: str):
        """Slide 2: Engagement Summary."""
        slide = self._add_blank_slide()
        self._add_title_bar(slide, "Engagement Summary")

        y = Inches(1.2)

        # Why — teal for emphasis
        box = self._add_textbox(
            slide, self.MARGIN, y, Inches(11), Inches(0.5),
            text=why, font_size=14, color=Colors.TEAL, bold=True,
            is_heading=True,
        )
        y += Inches(0.7)

        # Current state
        self._add_textbox(
            slide, self.MARGIN, y, Inches(5), Inches(0.4),
            text="Current State", font_size=14, bold=True,
        )
        y += Inches(0.45)

        for item in current_state:
            self._add_textbox(
                slide, Inches(0.7), y, Inches(10), Inches(0.35),
                text=f"•  {item}", font_size=12,
            )
            y += Inches(0.35)

        y += Inches(0.3)

        # Target state
        self._add_textbox(
            slide, self.MARGIN, y, Inches(5), Inches(0.4),
            text="Target State", font_size=14, bold=True,
        )
        y += Inches(0.45)
        self._add_textbox(
            slide, Inches(0.7), y, Inches(10), Inches(0.4),
            text=target_state, font_size=12, color=Colors.TEAL,
        )
        y += Inches(0.5)

        # Timeline
        self._add_textbox(
            slide, self.MARGIN, y, Inches(10), Inches(0.4),
            text=f"Timeline: {timeline}", font_size=12, bold=True,
        )

    # ---- Architecture visual helpers ----

    def _add_service_block(self, slide, left, top, width, height,
                           label, fill_color):
        """Add a colored service block with white text label."""
        shape = self._add_rect(
            slide, left, top, width, height, fill_color=fill_color,
        )
        shape.text_frame.word_wrap = True
        p = shape.text_frame.paragraphs[0]
        p.text = label
        p.font.size = Pt(8)
        p.font.bold = True
        p.font.color.rgb = Colors.WHITE
        p.font.name = self.FONT
        p.alignment = PP_ALIGN.CENTER
        shape.text_frame.paragraphs[0].space_before = Pt(0)
        shape.text_frame.paragraphs[0].space_after = Pt(0)
        return shape

    def _add_container(self, slide, left, top, width, height,
                       label, border_color, fill_color=None,
                       dashed=True, label_size=10):
        """Add a container outline (region, VCN, subnet)."""
        shape = self._add_rect(
            slide, left, top, width, height,
            fill_color=fill_color, border_color=border_color,
        )
        if not fill_color:
            shape.fill.background()
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1.5)
        if dashed:
            shape.line.dash_style = 2  # MSO_LINE_DASH_STYLE.DASH
        # Label at top-left inside container
        self._add_textbox(
            slide, left + Inches(0.1), top + Inches(0.05),
            width - Inches(0.2), Inches(0.3),
            text=label, font_size=label_size, bold=True,
            color=border_color, is_heading=False,
        )
        return shape

    def _add_arrow(self, slide, start_x, start_y, end_x, end_y,
                   color=None, dashed=False, label=""):
        """Add a connector arrow between two points."""
        from pptx.enum.shapes import MSO_SHAPE
        # Use a line shape (thin rectangle as proxy)
        connector = slide.shapes.add_connector(
            1,  # MSO_CONNECTOR.STRAIGHT
            start_x, start_y, end_x, end_y,
        )
        connector.line.color.rgb = color or RGBColor(0x70, 0x6E, 0x6F)
        connector.line.width = Pt(1.5)
        if dashed:
            connector.line.dash_style = 2
        return connector

    def add_architecture_slide(self, diagram_path: Optional[str] = None,
                                description: str = "",
                                visual: Optional[dict] = None):
        """Slide 3: Architecture Overview with diagram or visual layout.

        visual: optional dict with structured architecture data for rendering
                as colored blocks. Keys: regions, on_prem, security_footer.
        """
        slide = self._add_blank_slide()
        self._add_title_bar(slide, "Architecture Overview")

        if diagram_path:
            try:
                slide.shapes.add_picture(
                    diagram_path,
                    Inches(0.5), Inches(1.1),
                    Inches(12.3), Inches(6),
                )
            except Exception:
                self._add_textbox(
                    slide, Inches(1), Inches(2.5),
                    Inches(10), Inches(2),
                    text=f"[Diagram: {diagram_path}]\n\n{description}",
                    font_size=14, color=Colors.SECONDARY_TEXT,
                )
        elif visual:
            self._render_architecture_visual(slide, visual)
        else:
            self._add_textbox(
                slide, Inches(1), Inches(2),
                Inches(11), Inches(4),
                text=description or "[Insert architecture diagram — export from .drawio file]",
                font_size=14, color=Colors.SECONDARY_TEXT, italic=True,
                alignment=PP_ALIGN.CENTER,
            )

    def _render_architecture_visual(self, slide, visual: dict):
        """Render a visual architecture diagram from structured data."""
        regions = visual.get("regions", [])
        on_prem = visual.get("on_prem")
        security = visual.get("security_footer", "")

        # Category colors for service blocks
        cat_colors = {
            "infrastructure": Colors.TEAL,
            "database": Colors.COPPER,
            "integration": Colors.PURPLE,
            "security": Colors.FOREST,
            "dormant": RGBColor(0xDF, 0xDC, 0xD8),
        }

        y_cursor = Inches(1.15)

        for reg_idx, region in enumerate(regions):
            is_primary = region.get("primary", reg_idx == 0)
            region_name = region.get("name", f"Region {reg_idx+1}")
            region_label = region.get("label", "PRIMARY" if is_primary else "DR STANDBY")

            # Region dimensions — primary gets more space
            if is_primary:
                reg_left = Inches(0.4)
                reg_width = Inches(8.2)
                reg_height = Inches(4.8)
                reg_top = y_cursor
            else:
                reg_left = Inches(8.9)
                reg_width = Inches(4.1)
                reg_height = Inches(4.8)
                reg_top = y_cursor

            # Region container — solid border, light fill
            self._add_container(
                slide, reg_left, reg_top, reg_width, reg_height,
                label=f"{region_name}  [{region_label}]",
                border_color=RGBColor(0x9E, 0x98, 0x92),
                fill_color=RGBColor(0xF5, 0xF4, 0xF2),
                dashed=False, label_size=10,
            )

            inner_left = reg_left + Inches(0.15)
            inner_top = reg_top + Inches(0.45)
            inner_width = reg_width - Inches(0.3)

            # VCN container if present
            vcn = region.get("vcn")
            if vcn:
                vcn_name = vcn.get("name", "VCN")
                vcn_cidr = vcn.get("cidr", "")
                vcn_label = f"{vcn_name} {vcn_cidr}" if vcn_cidr else vcn_name
                vcn_height = reg_height - Inches(0.6)

                self._add_container(
                    slide, inner_left, inner_top, inner_width, vcn_height,
                    label=vcn_label,
                    border_color=Colors.BURNT_ORANGE,
                    dashed=True, label_size=9,
                )

                # Render subnets
                subnets = vcn.get("subnets", [])
                sub_top = inner_top + Inches(0.4)
                sub_left = inner_left + Inches(0.15)
                sub_width = inner_width - Inches(0.3)

                for sub_idx, subnet in enumerate(subnets):
                    sub_name = subnet.get("name", f"Subnet {sub_idx+1}")
                    sub_type = subnet.get("type", "private")
                    sub_border = Colors.BURNT_ORANGE
                    sub_h = Inches(0.95) if is_primary else Inches(0.7)

                    self._add_container(
                        slide, sub_left, sub_top, sub_width, sub_h,
                        label=sub_name,
                        border_color=sub_border,
                        fill_color=Colors.WARM_BG,
                        dashed=True, label_size=8,
                    )

                    # Service blocks inside subnet
                    services = subnet.get("services", [])
                    svc_left = sub_left + Inches(0.1)
                    svc_top = sub_top + Inches(0.3)
                    svc_spacing = Inches(0.08)
                    # Calculate service block width to fit
                    if services:
                        avail_width = sub_width - Inches(0.2)
                        svc_w = min(
                            Inches(2.2),
                            (avail_width - svc_spacing * (len(services) - 1)) / len(services)
                        )
                        svc_h = Inches(0.5)
                        for svc in services:
                            svc_name = svc.get("name", "Service")
                            svc_cat = svc.get("category", "infrastructure")
                            svc_color = cat_colors.get(svc_cat, Colors.TEAL)
                            self._add_service_block(
                                slide, svc_left, svc_top, svc_w, svc_h,
                                label=svc_name, fill_color=svc_color,
                            )
                            svc_left += svc_w + svc_spacing

                    sub_top += sub_h + Inches(0.1)

                # Gateways bar at bottom of VCN
                gateways = vcn.get("gateways", [])
                if gateways:
                    gw_top = inner_top + vcn_height - Inches(0.55)
                    gw_left = inner_left + Inches(0.15)
                    gw_text = "  |  ".join(gateways)
                    self._add_textbox(
                        slide, gw_left, gw_top,
                        inner_width - Inches(0.3), Inches(0.35),
                        text=gw_text, font_size=8, bold=True,
                        color=Colors.TEAL,
                        alignment=PP_ALIGN.CENTER,
                    )

            else:
                # No VCN — render services directly (e.g. DR standby)
                services = region.get("services", [])
                svc_top = inner_top + Inches(0.3)
                for svc in services:
                    svc_name = svc.get("name", "Service")
                    svc_cat = svc.get("category", "database")
                    svc_color = cat_colors.get(svc_cat, Colors.TEAL)
                    self._add_service_block(
                        slide, inner_left + Inches(0.3), svc_top,
                        inner_width - Inches(0.6), Inches(0.6),
                        label=svc_name, fill_color=svc_color,
                    )
                    svc_top += Inches(0.75)

                # DR details text
                dr_details = region.get("details", "")
                if dr_details:
                    self._add_textbox(
                        slide, inner_left + Inches(0.1), svc_top + Inches(0.1),
                        inner_width - Inches(0.2), Inches(0.6),
                        text=dr_details, font_size=8, italic=True,
                        color=Colors.SECONDARY_TEXT,
                        alignment=PP_ALIGN.CENTER,
                    )

        # On-prem block
        if on_prem:
            op_left = Inches(0.4)
            op_top = Inches(6.15)
            op_width = Inches(3.5)
            self._add_rect(
                slide, op_left, op_top, op_width, Inches(0.45),
                fill_color=RGBColor(0x70, 0x66, 0x5E),
            )
            op_shape = slide.shapes[-1]
            p = op_shape.text_frame.paragraphs[0]
            p.text = on_prem.get("name", "On-Premises")
            p.font.size = Pt(9)
            p.font.bold = True
            p.font.color.rgb = Colors.WHITE
            p.font.name = self.FONT
            p.alignment = PP_ALIGN.CENTER

            # Connection label
            conn_label = on_prem.get("connection", "IPSec VPN")
            self._add_textbox(
                slide, op_left + op_width + Inches(0.15), op_top,
                Inches(3), Inches(0.45),
                text=f"--- {conn_label} ---",
                font_size=8, italic=True, color=Colors.SECONDARY_TEXT,
                alignment=PP_ALIGN.LEFT,
            )

        # Security footer
        if security:
            self._add_textbox(
                slide, Inches(0.4), Inches(6.7),
                Inches(12.5), Inches(0.35),
                text=security, font_size=8, bold=True,
                color=Colors.TEAL,
                alignment=PP_ALIGN.LEFT,
            )

    def add_service_tiering_slide(self, workloads: list):
        """Service Tiering slide — maps workloads to Platinum/Gold/Silver/Bronze.

        workloads: list of {"name": str, "tier": str, "uptime": str,
                           "rto": str, "rpo": str}
        """
        slide = self._add_blank_slide()
        self._add_title_bar(slide, "Service Tiering")

        # Subtitle
        self._add_textbox(
            slide, self.MARGIN, Inches(1.1),
            Inches(12), Inches(0.4),
            text="Each tier drives: HA/DR topology, backup strategy, isolation model, support level.",
            font_size=11, italic=True, color=Colors.SECONDARY_TEXT,
        )

        rows = len(workloads) + 1
        table = self._add_table(
            slide, rows, 5,
            self.MARGIN, Inches(1.7),
            Inches(12), Inches(0.45 * rows),
        )

        table.columns[0].width = Inches(3.0)
        table.columns[1].width = Inches(2.5)
        table.columns[2].width = Inches(2.0)
        table.columns[3].width = Inches(2.25)
        table.columns[4].width = Inches(2.25)

        headers = ["Workload", "Tier", "Uptime", "RTO", "RPO"]
        for j, h in enumerate(headers):
            self._style_table_cell(
                table.cell(0, j), h, font_size=11, bold=True,
                color=Colors.WHITE, bg_color=Colors.TEAL,
                alignment=PP_ALIGN.CENTER,
            )

        tier_colors = {
            "platinum": Colors.ORACLE_RED,
            "gold": Colors.BURNT_ORANGE,
            "silver": Colors.SECONDARY_TEXT,
            "bronze": Colors.MUTED_TEAL,
        }

        for i, wl in enumerate(workloads):
            row_idx = i + 1
            bg = Colors.TABLE_ALT_ROW if row_idx % 2 == 0 else None
            self._style_table_cell(table.cell(row_idx, 0), wl["name"], font_size=10, bold=True, bg_color=bg)
            tier_label = wl.get("tier", "Silver")
            tier_color = tier_colors.get(tier_label.lower(), Colors.SECONDARY_TEXT)
            self._style_table_cell(
                table.cell(row_idx, 1), tier_label.title(),
                font_size=10, bold=True, color=tier_color, bg_color=bg,
                alignment=PP_ALIGN.CENTER,
            )
            self._style_table_cell(table.cell(row_idx, 2), wl.get("uptime", ""), font_size=10, bg_color=bg, alignment=PP_ALIGN.CENTER)
            self._style_table_cell(table.cell(row_idx, 3), wl.get("rto", ""), font_size=10, bg_color=bg, alignment=PP_ALIGN.CENTER)
            self._style_table_cell(table.cell(row_idx, 4), wl.get("rpo", ""), font_size=10, bg_color=bg, alignment=PP_ALIGN.CENTER)

    def add_architecture_principles_slide(self, principles: dict):
        """Architecture Principles slide — ECAL Design/Deployment/Service categories.

        principles: {"design": [{"id": str, "name": str, "summary": str}],
                     "deployment": [...], "service": [...]}
        """
        slide = self._add_blank_slide()
        self._add_title_bar(slide, "Architecture Principles")

        y = Inches(1.2)
        col_x = self.MARGIN
        col_width = Inches(4)

        for category in ["design", "deployment", "service"]:
            items = principles.get(category, [])
            if not items:
                continue

            # Category heading
            self._add_textbox(
                slide, col_x, y, col_width, Inches(0.35),
                text=category.upper(), font_size=13, bold=True,
                color=Colors.TEAL,
            )

            item_y = y + Inches(0.4)
            for item in items:
                pid = item.get("id", "")
                name = item.get("name", "")
                summary = item.get("summary", "")
                label = f"{pid}  {name}" if pid else name
                if summary:
                    label += f" — {summary}"
                self._add_textbox(
                    slide, col_x + Inches(0.1), item_y,
                    col_width - Inches(0.1), Inches(0.3),
                    text=f"• {label}", font_size=9,
                )
                item_y += Inches(0.3)

            col_x += Inches(4.2)

    def add_decisions_slide(self, decisions: list):
        """Slide 4: Architecture Decisions table.

        decisions: list of {"decision": str, "rationale": str}
        """
        slide = self._add_blank_slide()
        self._add_title_bar(slide, "Architecture Decisions")

        rows = len(decisions) + 1
        table = self._add_table(
            slide, rows, 2,
            self.MARGIN, Inches(1.2),
            Inches(12), Inches(0.5 * rows),
        )

        # Set column widths
        table.columns[0].width = Inches(4.5)
        table.columns[1].width = Inches(7.5)

        # Header row
        self._style_table_cell(
            table.cell(0, 0), "Decision", font_size=11, bold=True,
            color=Colors.WHITE, bg_color=Colors.TEAL,
        )
        self._style_table_cell(
            table.cell(0, 1), "Rationale", font_size=11, bold=True,
            color=Colors.WHITE, bg_color=Colors.TEAL,
        )

        # Data rows
        for i, dec in enumerate(decisions):
            row_idx = i + 1
            bg = Colors.TABLE_ALT_ROW if row_idx % 2 == 0 else None
            self._style_table_cell(
                table.cell(row_idx, 0), dec["decision"],
                font_size=11, bold=True, bg_color=bg,
            )
            self._style_table_cell(
                table.cell(row_idx, 1), dec["rationale"],
                font_size=10, bg_color=bg,
            )

    def add_ha_dr_slide(self, tiers: list, description: str = ""):
        """Slide 5: HA/DR table.

        tiers: list of {"tier": str, "technology": str, "rto": str, "rpo": str}
        """
        slide = self._add_blank_slide()
        self._add_title_bar(slide, "High Availability & Disaster Recovery")

        if description:
            self._add_textbox(
                slide, self.MARGIN, Inches(1.2),
                Inches(12), Inches(0.5),
                text=description, font_size=12,
            )

        rows = len(tiers) + 1
        table = self._add_table(
            slide, rows, 4,
            self.MARGIN, Inches(1.9),
            Inches(12), Inches(0.45 * rows),
        )

        table.columns[0].width = Inches(2.5)
        table.columns[1].width = Inches(4.5)
        table.columns[2].width = Inches(2.5)
        table.columns[3].width = Inches(2.5)

        headers = ["Tier", "Technology", "RTO", "RPO"]
        for j, h in enumerate(headers):
            self._style_table_cell(
                table.cell(0, j), h, font_size=11, bold=True,
                color=Colors.WHITE, bg_color=Colors.TEAL,
                alignment=PP_ALIGN.CENTER,
            )

        for i, tier in enumerate(tiers):
            row_idx = i + 1
            bg = Colors.TABLE_ALT_ROW if row_idx % 2 == 0 else None
            self._style_table_cell(table.cell(row_idx, 0), tier["tier"], font_size=10, bold=True, bg_color=bg)
            self._style_table_cell(table.cell(row_idx, 1), tier["technology"], font_size=10, bg_color=bg)
            self._style_table_cell(table.cell(row_idx, 2), tier["rto"], font_size=10, bg_color=bg, alignment=PP_ALIGN.CENTER)
            self._style_table_cell(table.cell(row_idx, 3), tier["rpo"], font_size=10, bg_color=bg, alignment=PP_ALIGN.CENTER)

    def add_security_slide(self, controls: dict, compliance: list = None):
        """Slide 6: Security & Compliance.

        controls: {"identity": [...], "network": [...], "database": [...], "monitoring": [...]}
        compliance: ["PCI-DSS", "SOC2", ...] or None
        """
        slide = self._add_blank_slide()
        self._add_title_bar(slide, "Security & Compliance")

        y = Inches(1.2)

        # Compliance badges
        if compliance:
            x = self.MARGIN
            for framework in compliance:
                shape = self._add_rect(
                    slide, x, y, Inches(1.5), Inches(0.4),
                    fill_color=Colors.SUCCESS,
                )
                shape.text_frame.paragraphs[0].text = f"✓ {framework}"
                shape.text_frame.paragraphs[0].font.size = Pt(10)
                shape.text_frame.paragraphs[0].font.bold = True
                shape.text_frame.paragraphs[0].font.color.rgb = Colors.WHITE
                shape.text_frame.paragraphs[0].font.name = self.FONT
                shape.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
                x += Inches(1.7)
            y += Inches(0.7)

        # Controls in columns
        col_x = self.MARGIN
        col_width = Inches(3)
        for area, items in controls.items():
            area_title = area.replace("_", " ").title()
            self._add_textbox(
                slide, col_x, y, col_width, Inches(0.35),
                text=area_title, font_size=12, bold=True,
                color=Colors.TEAL,
            )
            item_y = y + Inches(0.4)
            for item in items:
                self._add_textbox(
                    slide, col_x + Inches(0.1), item_y,
                    col_width - Inches(0.1), Inches(0.3),
                    text=f"• {item}", font_size=10,
                )
                item_y += Inches(0.3)
            col_x += Inches(3.2)

    def add_environment_catalogue_slide(self, environments: list,
                                       cost_notes: list = None):
        """Environment Catalogue slide — Prod/Pre-Prod/Dev-Test/DR per workload.

        environments: list of {"environment": str, "tier": str,
                              "databases": str, "ocpus": str, "isolation": str}
        cost_notes: optional list of cost optimization notes
        """
        slide = self._add_blank_slide()
        self._add_title_bar(slide, "Environment Catalogue")

        rows = len(environments) + 1
        table = self._add_table(
            slide, rows, 5,
            self.MARGIN, Inches(1.2),
            Inches(12), Inches(0.4 * rows),
        )

        table.columns[0].width = Inches(2.2)
        table.columns[1].width = Inches(1.8)
        table.columns[2].width = Inches(2.5)
        table.columns[3].width = Inches(1.5)
        table.columns[4].width = Inches(4.0)

        headers = ["Environment", "Tier", "Databases", "OCPUs", "Isolation"]
        for j, h in enumerate(headers):
            self._style_table_cell(
                table.cell(0, j), h, font_size=11, bold=True,
                color=Colors.WHITE, bg_color=Colors.TEAL,
                alignment=PP_ALIGN.CENTER,
            )

        for i, env in enumerate(environments):
            row_idx = i + 1
            bg = Colors.TABLE_ALT_ROW if row_idx % 2 == 0 else None
            self._style_table_cell(table.cell(row_idx, 0), env.get("environment", ""), font_size=10, bold=True, bg_color=bg)
            self._style_table_cell(table.cell(row_idx, 1), env.get("tier", ""), font_size=10, bg_color=bg, alignment=PP_ALIGN.CENTER)
            self._style_table_cell(table.cell(row_idx, 2), env.get("databases", ""), font_size=10, bg_color=bg)
            self._style_table_cell(table.cell(row_idx, 3), env.get("ocpus", ""), font_size=10, bg_color=bg, alignment=PP_ALIGN.CENTER)
            self._style_table_cell(table.cell(row_idx, 4), env.get("isolation", ""), font_size=10, bg_color=bg)

        if cost_notes:
            notes_y = Inches(1.2) + Inches(0.4 * rows) + Inches(0.3)
            self._add_textbox(
                slide, self.MARGIN, notes_y,
                Inches(12), Inches(0.35),
                text="Cost Optimization", font_size=12, bold=True,
                color=Colors.TEAL,
            )
            note_y = notes_y + Inches(0.35)
            for note in cost_notes:
                self._add_textbox(
                    slide, self.MARGIN + Inches(0.1), note_y,
                    Inches(11.5), Inches(0.25),
                    text=f"• {note}", font_size=9,
                )
                note_y += Inches(0.25)

    def add_cost_slide(self, line_items: list, assumptions: list = None,
                       show_byol: bool = True):
        """Slide 7: Cost Estimate.

        line_items: list of {"component": str, "monthly_payg": str,
                            "monthly_byol": str (optional), "notes": str}
        """
        slide = self._add_blank_slide()
        self._add_title_bar(slide, "Cost Estimate")

        cols = 4 if show_byol else 3
        rows = len(line_items) + 1
        table = self._add_table(
            slide, rows, cols,
            self.MARGIN, Inches(1.2),
            Inches(12), Inches(0.4 * rows),
        )

        if show_byol:
            table.columns[0].width = Inches(3.5)
            table.columns[1].width = Inches(2.5)
            table.columns[2].width = Inches(2.5)
            table.columns[3].width = Inches(3.5)
            headers = ["Component", "Monthly (PAYG)", "Monthly (BYOL)", "Notes"]
        else:
            table.columns[0].width = Inches(4)
            table.columns[1].width = Inches(3)
            table.columns[2].width = Inches(5)
            headers = ["Component", "Monthly", "Notes"]

        for j, h in enumerate(headers):
            self._style_table_cell(
                table.cell(0, j), h, font_size=11, bold=True,
                color=Colors.WHITE, bg_color=Colors.TEAL,
                alignment=PP_ALIGN.CENTER if j > 0 else PP_ALIGN.LEFT,
            )

        for i, item in enumerate(line_items):
            row_idx = i + 1
            is_total = "total" in item.get("component", "").lower()
            bg = Colors.TABLE_ALT_ROW if row_idx % 2 == 0 and not is_total else None
            if is_total:
                bg = Colors.TEAL

            self._style_table_cell(
                table.cell(row_idx, 0), item["component"],
                font_size=10, bold=is_total,
                color=Colors.WHITE if is_total else None,
                bg_color=bg,
            )
            self._style_table_cell(
                table.cell(row_idx, 1), item.get("monthly_payg", ""),
                font_size=10, bold=is_total,
                color=Colors.WHITE if is_total else None,
                bg_color=bg, alignment=PP_ALIGN.RIGHT,
            )
            if show_byol:
                self._style_table_cell(
                    table.cell(row_idx, 2), item.get("monthly_byol", ""),
                    font_size=10, bold=is_total,
                    color=Colors.WHITE if is_total else None,
                    bg_color=bg, alignment=PP_ALIGN.RIGHT,
                )
                self._style_table_cell(
                    table.cell(row_idx, 3), item.get("notes", ""),
                    font_size=9, bg_color=bg,
                    color=Colors.WHITE if is_total else Colors.SECONDARY_TEXT,
                )
            else:
                self._style_table_cell(
                    table.cell(row_idx, 2), item.get("notes", ""),
                    font_size=9, bg_color=bg,
                    color=Colors.WHITE if is_total else Colors.SECONDARY_TEXT,
                )

        # Assumptions
        if assumptions:
            table_bottom = Inches(1.2) + Inches(0.4 * rows) + Inches(0.3)
            self._add_textbox(
                slide, self.MARGIN, table_bottom,
                Inches(12), Inches(0.3),
                text="Assumptions:", font_size=9, bold=True,
                color=Colors.SECONDARY_TEXT, italic=True,
            )
            for idx, assumption in enumerate(assumptions):
                self._add_textbox(
                    slide, Inches(0.7), table_bottom + Inches(0.3 + idx * 0.25),
                    Inches(11), Inches(0.25),
                    text=f"• {assumption}", font_size=8, italic=True,
                    color=Colors.SECONDARY_TEXT,
                )

    def add_cost_comparison_slide(self, rows: list, title: str = "Cost Comparison",
                                  col_headers: list = None):
        """Slide 8: Cost Comparison (optional).

        rows: list of {"item": str, "current": str, "oci": str, "savings": str}
        col_headers: custom column headers (default: ["Component", "Current", "OCI", "Savings"])
        """
        slide = self._add_blank_slide()
        self._add_title_bar(slide, title)

        headers = col_headers or ["Component", "Current", "OCI", "Savings"]
        num_rows = len(rows) + 1
        table = self._add_table(
            slide, num_rows, len(headers),
            self.MARGIN, Inches(1.2),
            Inches(12), Inches(0.45 * num_rows),
        )

        col_widths = [Inches(4), Inches(2.5), Inches(2.5), Inches(3)]
        for j, w in enumerate(col_widths[:len(headers)]):
            table.columns[j].width = w

        for j, h in enumerate(headers):
            self._style_table_cell(
                table.cell(0, j), h, font_size=11, bold=True,
                color=Colors.WHITE, bg_color=Colors.TEAL,
                alignment=PP_ALIGN.CENTER if j > 0 else PP_ALIGN.LEFT,
            )

        for i, row in enumerate(rows):
            row_idx = i + 1
            is_total = "total" in row.get("item", "").lower()
            bg = Colors.TEAL if is_total else (Colors.TABLE_ALT_ROW if row_idx % 2 == 0 else None)
            txt_color = Colors.WHITE if is_total else None

            self._style_table_cell(
                table.cell(row_idx, 0), row.get("item", ""),
                font_size=10, bold=is_total, color=txt_color, bg_color=bg,
            )
            self._style_table_cell(
                table.cell(row_idx, 1), row.get("current", ""),
                font_size=10, bold=is_total, color=txt_color, bg_color=bg,
                alignment=PP_ALIGN.RIGHT,
            )
            self._style_table_cell(
                table.cell(row_idx, 2), row.get("oci", ""),
                font_size=10, bold=is_total, color=txt_color, bg_color=bg,
                alignment=PP_ALIGN.RIGHT,
            )
            if len(headers) > 3:
                savings_color = Colors.SUCCESS if not is_total else txt_color
                self._style_table_cell(
                    table.cell(row_idx, 3), row.get("savings", ""),
                    font_size=10, bold=True, color=savings_color, bg_color=bg,
                    alignment=PP_ALIGN.CENTER,
                )

    def add_migration_slide(self, phases: list, tools: list = None,
                            downtime: str = ""):
        """Slide 9: Migration Approach.

        phases: list of {"name": str, "weeks": str, "tasks": [...]}
        """
        slide = self._add_blank_slide()
        self._add_title_bar(slide, "Migration Approach")

        y = Inches(1.3)
        phase_colors = [Colors.TEAL, Colors.ORACLE_RED, Colors.BURNT_ORANGE, Colors.FOREST]

        # Phase timeline bars
        bar_left = Inches(2.5)
        bar_width = Inches(9.5)
        for i, phase in enumerate(phases):
            color = phase_colors[i % len(phase_colors)]

            # Phase label
            self._add_textbox(
                slide, self.MARGIN, y,
                Inches(2), Inches(0.45),
                text=phase["name"], font_size=11, bold=True,
            )

            # Phase bar
            bar = self._add_rect(
                slide, bar_left, y + Inches(0.05),
                bar_width * 0.9, Inches(0.35),
                fill_color=color,
            )
            bar.text_frame.paragraphs[0].text = phase.get("weeks", "")
            bar.text_frame.paragraphs[0].font.size = Pt(9)
            bar.text_frame.paragraphs[0].font.color.rgb = Colors.WHITE
            bar.text_frame.paragraphs[0].font.name = self.FONT
            bar.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

            # Tasks below bar
            if phase.get("tasks"):
                tasks_text = " | ".join(phase["tasks"][:4])
                self._add_textbox(
                    slide, bar_left, y + Inches(0.4),
                    bar_width, Inches(0.3),
                    text=tasks_text, font_size=8, italic=True,
                    color=Colors.SECONDARY_TEXT,
                )

            y += Inches(0.9)

        # Tools
        if tools:
            y += Inches(0.2)
            self._add_textbox(
                slide, self.MARGIN, y,
                Inches(12), Inches(0.35),
                text=f"Migration Tools: {', '.join(tools)}",
                font_size=11, bold=True, color=Colors.TEAL,
            )

        # Downtime approach
        if downtime:
            y += Inches(0.5)
            self._add_textbox(
                slide, self.MARGIN, y,
                Inches(12), Inches(0.35),
                text=f"Downtime Approach: {downtime}",
                font_size=11, color=Colors.PRIMARY_TEXT,
            )

    def add_operational_raci_slide(self, raci_items: list,
                                   model: str = "co_managed"):
        """Operational RACI slide — responsibility matrix.

        raci_items: list of {"activity": str, "customer": str, "oracle": str}
        model: "fully_managed", "co_managed", or "self_managed"
        """
        slide = self._add_blank_slide()
        model_label = model.replace("_", "-").title()
        self._add_title_bar(slide, f"Operational Responsibilities ({model_label})")

        rows = len(raci_items) + 1
        table = self._add_table(
            slide, rows, 3,
            self.MARGIN, Inches(1.2),
            Inches(10), Inches(0.38 * rows),
        )

        table.columns[0].width = Inches(5.0)
        table.columns[1].width = Inches(2.5)
        table.columns[2].width = Inches(2.5)

        headers = ["Activity", "Customer", "Oracle / Partner"]
        for j, h in enumerate(headers):
            self._style_table_cell(
                table.cell(0, j), h, font_size=11, bold=True,
                color=Colors.WHITE, bg_color=Colors.TEAL,
                alignment=PP_ALIGN.CENTER,
            )

        for i, item in enumerate(raci_items):
            row_idx = i + 1
            bg = Colors.TABLE_ALT_ROW if row_idx % 2 == 0 else None
            self._style_table_cell(table.cell(row_idx, 0), item.get("activity", ""), font_size=10, bg_color=bg)
            self._style_table_cell(table.cell(row_idx, 1), item.get("customer", ""), font_size=10, bg_color=bg, alignment=PP_ALIGN.CENTER)
            self._style_table_cell(table.cell(row_idx, 2), item.get("oracle", ""), font_size=10, bg_color=bg, alignment=PP_ALIGN.CENTER)

        # Legend
        legend_y = Inches(1.2) + Inches(0.38 * rows) + Inches(0.2)
        self._add_textbox(
            slide, self.MARGIN, legend_y,
            Inches(10), Inches(0.3),
            text="R = Responsible    A = Accountable    C = Consulted    I = Informed",
            font_size=9, italic=True, color=Colors.SECONDARY_TEXT,
        )

    def add_risk_slide(self, risks: list):
        """Slide 10: Risk Register.

        risks: list of {"risk": str, "severity": "HIGH"|"MEDIUM"|"LOW", "mitigation": str}
        """
        slide = self._add_blank_slide()
        self._add_title_bar(slide, "Risk Register")

        rows = len(risks) + 1
        table = self._add_table(
            slide, rows, 3,
            self.MARGIN, Inches(1.2),
            Inches(12), Inches(0.5 * rows),
        )

        table.columns[0].width = Inches(4.5)
        table.columns[1].width = Inches(1.5)
        table.columns[2].width = Inches(6)

        headers = ["Risk", "Severity", "Mitigation"]
        for j, h in enumerate(headers):
            self._style_table_cell(
                table.cell(0, j), h, font_size=11, bold=True,
                color=Colors.WHITE, bg_color=Colors.TEAL,
                alignment=PP_ALIGN.CENTER if j == 1 else PP_ALIGN.LEFT,
            )

        severity_colors = {
            "HIGH": Colors.ERROR,
            "MEDIUM": Colors.WARNING,
            "LOW": Colors.SUCCESS,
        }

        for i, risk in enumerate(risks):
            row_idx = i + 1
            bg = Colors.TABLE_ALT_ROW if row_idx % 2 == 0 else None
            self._style_table_cell(
                table.cell(row_idx, 0), risk["risk"],
                font_size=10, bg_color=bg,
            )
            sev = risk.get("severity", "MEDIUM").upper()
            self._style_table_cell(
                table.cell(row_idx, 1), sev,
                font_size=10, bold=True,
                color=severity_colors.get(sev, Colors.WARNING),
                bg_color=bg, alignment=PP_ALIGN.CENTER,
            )
            self._style_table_cell(
                table.cell(row_idx, 2), risk["mitigation"],
                font_size=10, bg_color=bg,
            )

    def add_scorecard_slide(self, pillars: list, recommendations: list = None):
        """Slide 11: Well-Architected Scorecard.

        pillars: list of {"name": str, "status": "PASS"|"PASS_WITH_RECOMMENDATIONS"|"GAPS_IDENTIFIED"|"NOT_APPLICABLE",
                         "passed": int, "total": int}
        """
        slide = self._add_blank_slide()
        self._add_title_bar(slide, "Well-Architected Scorecard")

        status_styles = {
            "PASS": {"icon": "✓", "color": Colors.SUCCESS, "label": "PASS"},
            "PASS_WITH_RECOMMENDATIONS": {"icon": "⚠", "color": Colors.WARNING, "label": "PASS WITH RECOMMENDATIONS"},
            "GAPS_IDENTIFIED": {"icon": "✗", "color": Colors.ERROR, "label": "GAPS IDENTIFIED"},
            "NOT_APPLICABLE": {"icon": "—", "color": Colors.SECONDARY_TEXT, "label": "N/A"},
        }

        y = Inches(1.4)
        for pillar in pillars:
            style = status_styles.get(pillar["status"], status_styles["PASS"])

            # Status indicator pill
            pill = self._add_rect(
                slide, self.MARGIN, y,
                Inches(0.5), Inches(0.45),
                fill_color=style["color"],
            )
            pill.text_frame.paragraphs[0].text = style["icon"]
            pill.text_frame.paragraphs[0].font.size = Pt(14)
            pill.text_frame.paragraphs[0].font.color.rgb = Colors.WHITE
            pill.text_frame.paragraphs[0].font.name = self.FONT
            pill.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

            # Pillar name
            self._add_textbox(
                slide, Inches(1.2), y,
                Inches(4), Inches(0.45),
                text=pillar["name"], font_size=13, bold=True,
            )

            # Score
            score_text = f"{pillar['passed']}/{pillar['total']}" if pillar['total'] > 0 else "—"
            self._add_textbox(
                slide, Inches(5.5), y,
                Inches(1.5), Inches(0.45),
                text=score_text, font_size=13,
                color=Colors.SECONDARY_TEXT, alignment=PP_ALIGN.CENTER,
            )

            # Status label
            self._add_textbox(
                slide, Inches(7), y,
                Inches(5), Inches(0.45),
                text=style["label"], font_size=11,
                color=style["color"], bold=True,
            )

            y += Inches(0.6)

        # Recommendations
        if recommendations:
            y += Inches(0.3)
            self._add_textbox(
                slide, self.MARGIN, y,
                Inches(12), Inches(0.35),
                text="Top Recommendations:", font_size=12, bold=True,
                color=Colors.TEAL,
            )
            y += Inches(0.4)
            for rec in recommendations[:4]:
                self._add_textbox(
                    slide, Inches(0.7), y,
                    Inches(11), Inches(0.3),
                    text=f"→ {rec}", font_size=10,
                )
                y += Inches(0.3)

        # Reference
        self._add_textbox(
            slide, self.MARGIN, Inches(6.5),
            Inches(12), Inches(0.3),
            text="Validated against Oracle Well-Architected Framework — docs.oracle.com/en/solutions/oci-best-practices/",
            font_size=8, italic=True, color=Colors.SECONDARY_TEXT,
        )

    def add_next_steps_slide(self, steps: list, contact_info: str = ""):
        """Slide 12: Next Steps."""
        slide = self._add_blank_slide()
        self._add_title_bar(slide, "Next Steps")

        y = Inches(1.5)
        for i, step in enumerate(steps):
            # Number circle
            circle = slide.shapes.add_shape(
                MSO_SHAPE.OVAL,
                self.MARGIN, y,
                Inches(0.4), Inches(0.4),
            )
            circle.fill.solid()
            circle.fill.fore_color.rgb = Colors.TEAL
            circle.line.fill.background()
            circle.text_frame.paragraphs[0].text = str(i + 1)
            circle.text_frame.paragraphs[0].font.size = Pt(12)
            circle.text_frame.paragraphs[0].font.bold = True
            circle.text_frame.paragraphs[0].font.color.rgb = Colors.WHITE
            circle.text_frame.paragraphs[0].font.name = self.FONT
            circle.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

            # Step text
            self._add_textbox(
                slide, Inches(1.1), y,
                Inches(10), Inches(0.4),
                text=step, font_size=13,
            )
            y += Inches(0.65)

        if contact_info:
            self._add_textbox(
                slide, self.MARGIN, Inches(6),
                Inches(12), Inches(0.4),
                text=contact_info, font_size=11,
                color=Colors.SECONDARY_TEXT,
            )

    # ---- Build from YAML spec ----

    @classmethod
    def from_spec(cls, spec: dict, template: Optional[str] = None) -> "OCIDeckGenerator":
        """Build a complete deck from a YAML specification."""
        meta = spec.get("metadata", {})
        gen = cls(
            customer=meta.get("customer", ""),
            project=meta.get("project", ""),
            architect=meta.get("architect", ""),
            firm=meta.get("firm", ""),
            template=template,
        )

        # Slide 1: Title
        gen.add_title_slide(subtitle=meta.get("subtitle", ""))

        # Slide 2: Summary
        if "summary" in spec:
            s = spec["summary"]
            gen.add_summary_slide(
                why=s.get("why", ""),
                current_state=s.get("current_state", []),
                target_state=s.get("target_state", ""),
                timeline=s.get("timeline", ""),
            )

        # Slide 3: Service Tiering (NEW — ECAL)
        if "service_tiering" in spec:
            gen.add_service_tiering_slide(spec["service_tiering"])

        # Slide 4: Architecture Principles (NEW — ECAL)
        if "architecture_principles" in spec:
            gen.add_architecture_principles_slide(spec["architecture_principles"])

        # Slide 5: Architecture
        if "architecture" in spec:
            a = spec["architecture"]
            gen.add_architecture_slide(
                diagram_path=a.get("diagram_path"),
                description=a.get("description", ""),
                visual=a.get("visual"),
            )

        # Slide 6: Decisions
        if "decisions" in spec:
            gen.add_decisions_slide(spec["decisions"])

        # Slide 7: HA/DR
        if "ha_dr" in spec:
            h = spec["ha_dr"]
            gen.add_ha_dr_slide(
                tiers=h.get("tiers", []),
                description=h.get("description", ""),
            )

        # Slide 8: Security
        if "security" in spec:
            s = spec["security"]
            gen.add_security_slide(
                controls=s.get("controls", {}),
                compliance=s.get("compliance", []),
            )

        # Slide 9: Environment Catalogue (NEW — ECAL)
        if "environment_catalogue" in spec:
            ec = spec["environment_catalogue"]
            gen.add_environment_catalogue_slide(
                environments=ec.get("environments", []),
                cost_notes=ec.get("cost_notes"),
            )

        # Slide 10: Cost
        if "cost" in spec:
            c = spec["cost"]
            gen.add_cost_slide(
                line_items=c.get("line_items", []),
                assumptions=c.get("assumptions", []),
                show_byol=c.get("show_byol", True),
            )

        # Slide 11: Cost Comparison (optional)
        if "cost_comparison" in spec:
            cc = spec["cost_comparison"]
            gen.add_cost_comparison_slide(
                rows=cc.get("rows", []),
                title=cc.get("title", "Cost Comparison"),
                col_headers=cc.get("col_headers"),
            )

        # Slide 12: Migration
        if "migration" in spec:
            m = spec["migration"]
            gen.add_migration_slide(
                phases=m.get("phases", []),
                tools=m.get("tools", []),
                downtime=m.get("downtime", ""),
            )

        # Slide 13: Operational RACI (NEW — ECAL)
        if "operational_raci" in spec:
            r = spec["operational_raci"]
            gen.add_operational_raci_slide(
                raci_items=r.get("raci_items", []),
                model=r.get("model", "co_managed"),
            )

        # Slide 14: Risks
        if "risks" in spec:
            gen.add_risk_slide(spec["risks"])

        # Slide 15: WA Scorecard
        if "scorecard" in spec:
            sc = spec["scorecard"]
            gen.add_scorecard_slide(
                pillars=sc.get("pillars", []),
                recommendations=sc.get("recommendations", []),
            )

        # Slide 16: Next Steps
        if "next_steps" in spec:
            ns = spec["next_steps"]
            gen.add_next_steps_slide(
                steps=ns.get("steps", []),
                contact_info=ns.get("contact_info", ""),
            )

        return gen

    # ---- Save ----

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
        description="Generate OCI architecture proposal slide deck (.pptx)"
    )
    parser.add_argument(
        "--spec", required=True,
        help="Path to YAML spec file with proposal data",
    )
    parser.add_argument(
        "--output", default="architecture-proposal.pptx",
        help="Output .pptx file path",
    )
    parser.add_argument(
        "--template",
        help="Path to a .pptx template to inherit theme/fonts from "
             "(e.g. Oracle Database Icon Library .pptx)",
    )
    args = parser.parse_args()

    with open(args.spec, 'r') as f:
        spec = yaml.safe_load(f)

    gen = OCIDeckGenerator.from_spec(spec, template=args.template)
    gen.save(args.output)

    print(f"Generated: {args.output}")
    print(f"  Slides: {gen.slide_count}")
    print(f"  Theme: Oracle Redwood")
    if args.template:
        print(f"  Template: {args.template}")
    customer = spec.get("metadata", {}).get("customer", "")
    if customer:
        print(f"  Customer: {customer}")


if __name__ == "__main__":
    main()
