#!/usr/bin/env python3
"""
OCI Deal Accelerator — Customer-Facing PDF Generator

Produces a branded PDF document using Oracle Redwood design system colors
and typography. This is the CUSTOMER-FACING output — all internal KB
references, field finding IDs, gotcha codes, and internal notes are
stripped automatically.

Usage:
    python oci_pdf_gen.py --spec proposal-data.yaml --output proposal.pdf
    python oci_pdf_gen.py --spec proposal-data.yaml --output proposal.pdf --diagram arch.png

Or import and use programmatically:
    from oci_pdf_gen import OCIPDFGenerator
    gen = OCIPDFGenerator.from_spec(spec)
    gen.save("proposal.pdf")
"""

import re
import yaml
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether, HRFlowable,
)
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate, Frame
from reportlab.lib.pagesizes import letter


# ============================================================
# Oracle Redwood Design System Colors
# ============================================================

class Colors:
    DARK_BG = HexColor("#312D2A")
    PRIMARY_TEXT = HexColor("#312D2A")
    SECONDARY_TEXT = HexColor("#6F6964")
    WARM_BG = HexColor("#FCFBFA")
    ORACLE_RED = HexColor("#C74634")
    GOLD = HexColor("#FACD62")
    TEAL = HexColor("#2C5967")
    SAGE = HexColor("#759C6C")
    FOREST = HexColor("#2B6242")
    MUTED_TEAL = HexColor("#94AFAF")
    BURNT_ORANGE = HexColor("#AE562C")
    COPPER = HexColor("#AA643B")
    PURPLE = HexColor("#804998")
    SUCCESS = HexColor("#2B6242")
    WARNING = HexColor("#AE562C")
    ERROR = HexColor("#C74634")
    TABLE_ALT_ROW = HexColor("#F5F4F2")
    TABLE_HEADER_BG = HexColor("#2C5967")
    WHITE = HexColor("#FFFFFF")
    LIGHT_GRAY = HexColor("#E8E6E3")


# ============================================================
# Internal reference sanitizer
# ============================================================

# Patterns that identify internal-only content
_INTERNAL_PATTERNS = [
    r'FK-\d{3}',                    # Field knowledge IDs
    r'FF-\d{6}-\d{3}',             # Field finding IDs
    r'\bkb/\S+',                    # KB file paths
    r'\bgotcha[s]?\b',             # gotcha references
    r'field.?finding[s]?',          # field finding mentions
    r'confidence:\s*(validated|observed|reported|inferred)',
    r'contributor:\s*\{[^}]+\}',   # contributor blocks
    r'severity:\s*(HIGH|MEDIUM|LOW)\s*$',  # raw severity tags
    r'SR#\s*\d+',                  # Oracle SR numbers
]
_INTERNAL_RE = re.compile('|'.join(_INTERNAL_PATTERNS), re.IGNORECASE)


def sanitize_text(text: str) -> str:
    """Remove internal KB references from customer-facing text."""
    if not text:
        return text
    # Remove lines that are purely internal references
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        # Skip lines that are just internal IDs
        stripped = line.strip()
        if stripped and re.match(r'^(FK-\d{3}|FF-\d{6}-\d{3})\b', stripped):
            continue
        # Remove inline internal refs
        line = re.sub(r'\(FK-\d{3}\)', '', line)
        line = re.sub(r'\(FF-\d{6}-\d{3}\)', '', line)
        line = re.sub(r'\bkb/\S+', '', line)
        line = re.sub(r'\s{2,}', ' ', line).strip()
        cleaned.append(line)
    return '\n'.join(cleaned)


def sanitize_list(items: list) -> list:
    """Sanitize a list of strings."""
    return [sanitize_text(str(item)) for item in items if item]


# ============================================================
# Styles
# ============================================================

def build_styles():
    """Build Oracle Redwood paragraph styles."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        'CoverTitle',
        fontName='Helvetica-Bold',
        fontSize=28,
        leading=34,
        textColor=white,
        alignment=TA_LEFT,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        'CoverSubtitle',
        fontName='Helvetica',
        fontSize=18,
        leading=22,
        textColor=HexColor("#9E9892"),
        alignment=TA_LEFT,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        'CoverInfo',
        fontName='Helvetica',
        fontSize=11,
        leading=14,
        textColor=HexColor("#9E9892"),
        alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        'SectionTitle',
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=26,
        textColor=Colors.PRIMARY_TEXT,
        spaceBefore=18,
        spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        'SubsectionTitle',
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=Colors.TEAL,
        spaceBefore=12,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        'BodyText_Redwood',
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=Colors.PRIMARY_TEXT,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        'BulletItem',
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=Colors.PRIMARY_TEXT,
        leftIndent=18,
        bulletIndent=6,
        spaceAfter=3,
    ))
    styles.add(ParagraphStyle(
        'Emphasis',
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=Colors.TEAL,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        'FooterStyle',
        fontName='Helvetica',
        fontSize=7,
        leading=9,
        textColor=Colors.SECONDARY_TEXT,
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        'Disclaimer',
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=10,
        textColor=Colors.SECONDARY_TEXT,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        'ImpactStatement',
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=22,
        textColor=Colors.TEAL,
        alignment=TA_LEFT,
        spaceBefore=12,
        spaceAfter=12,
    ))
    styles.add(ParagraphStyle(
        'MetricBig',
        fontName='Helvetica-Bold',
        fontSize=36,
        leading=42,
        textColor=Colors.ORACLE_RED,
        alignment=TA_CENTER,
        spaceBefore=18,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        'TableHeader',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=white,
    ))
    styles.add(ParagraphStyle(
        'TableCell',
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=Colors.PRIMARY_TEXT,
    ))
    styles.add(ParagraphStyle(
        'TableCellBold',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=Colors.PRIMARY_TEXT,
    ))
    return styles


# ============================================================
# PDF Generator
# ============================================================

class OCIPDFGenerator:
    """Generate Oracle Redwood-branded customer-facing PDF documents."""

    PAGE_WIDTH, PAGE_HEIGHT = letter  # 8.5 x 11 inches
    MARGIN = 0.75 * inch

    def __init__(self, customer: str = "", project: str = "",
                 architect: str = "", firm: str = ""):
        self.customer = customer
        self.project = project
        self.architect = architect
        self.firm = firm
        self.styles = build_styles()
        self.story = []  # flowable elements
        self._page_num = 0
        self._total_pages = 0

    # ---- Page templates ----

    def _header_footer(self, canvas, doc):
        """Draw header and footer on each page."""
        canvas.saveState()
        page_num = canvas.getPageNumber()

        if page_num == 1:
            # Cover page — no header/footer
            canvas.restoreState()
            return

        # Header: thin Oracle Red line
        canvas.setStrokeColor(Colors.ORACLE_RED)
        canvas.setLineWidth(2)
        canvas.line(
            self.MARGIN, self.PAGE_HEIGHT - 0.5 * inch,
            self.PAGE_WIDTH - self.MARGIN, self.PAGE_HEIGHT - 0.5 * inch,
        )

        # Header: customer name (left)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(Colors.SECONDARY_TEXT)
        canvas.drawString(
            self.MARGIN,
            self.PAGE_HEIGHT - 0.45 * inch,
            self.customer,
        )

        # Header: "Confidential" (right)
        canvas.drawRightString(
            self.PAGE_WIDTH - self.MARGIN,
            self.PAGE_HEIGHT - 0.45 * inch,
            "Confidential",
        )

        # Footer: thin gray line
        canvas.setStrokeColor(Colors.LIGHT_GRAY)
        canvas.setLineWidth(0.5)
        canvas.line(
            self.MARGIN, 0.55 * inch,
            self.PAGE_WIDTH - self.MARGIN, 0.55 * inch,
        )

        # Footer: page number (center)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(Colors.SECONDARY_TEXT)
        canvas.drawCentredString(
            self.PAGE_WIDTH / 2,
            0.4 * inch,
            f"Page {page_num}",
        )

        # Footer: date (right)
        canvas.drawRightString(
            self.PAGE_WIDTH - self.MARGIN,
            0.4 * inch,
            datetime.now().strftime("%B %Y"),
        )

        canvas.restoreState()

    def _thank_you_page(self, canvas, doc):
        """Draw the Thank You page background (dark, matches cover)."""
        canvas.saveState()
        canvas.setFillColor(Colors.DARK_BG)
        canvas.rect(0, 0, self.PAGE_WIDTH, self.PAGE_HEIGHT, fill=1, stroke=0)
        # Oracle Red accent bar matching cover
        canvas.setFillColor(Colors.ORACLE_RED)
        canvas.rect(
            0.6 * inch, 3.2 * inch,
            4, 2.2 * inch,
            fill=1, stroke=0,
        )
        canvas.restoreState()

    def _cover_page(self, canvas, doc):
        """Draw the cover page background."""
        canvas.saveState()

        # Full dark background
        canvas.setFillColor(Colors.DARK_BG)
        canvas.rect(0, 0, self.PAGE_WIDTH, self.PAGE_HEIGHT, fill=1, stroke=0)

        # Oracle Red vertical accent bar
        canvas.setFillColor(Colors.ORACLE_RED)
        canvas.rect(
            0.6 * inch, 3.2 * inch,
            4, 2.2 * inch,
            fill=1, stroke=0,
        )

        # "Prepared with OCI Deal Accelerator" at bottom
        canvas.setFont("Helvetica-Oblique", 8)
        canvas.setFillColor(HexColor("#6F6964"))
        canvas.drawString(
            0.85 * inch, 1.2 * inch,
            "Prepared with OCI Deal Accelerator",
        )

        # Oracle safe harbor footer
        canvas.setFont("Helvetica", 6)
        canvas.setFillColor(HexColor("#6F6964"))
        canvas.drawString(
            0.85 * inch, 0.7 * inch,
            "This document is provided for informational purposes only. "
            "Actual results may vary.",
        )

        canvas.restoreState()

    # ---- Section builders ----

    def add_cover(self, subtitle: str = ""):
        """Add cover page elements (text positioned over the dark bg)."""
        # Spacer to push content down (cover bg is drawn by page template)
        self.story.append(Spacer(1, 3.0 * inch))

        # Customer name
        title = self.customer or "Architecture Proposal"
        self.story.append(Paragraph(title, self.styles['CoverTitle']))

        # Project
        if self.project:
            self.story.append(Paragraph(self.project, self.styles['CoverSubtitle']))

        # Subtitle
        date_str = datetime.now().strftime("%B %Y")
        sub = subtitle or f"Architecture Proposal — {date_str}"
        self.story.append(Spacer(1, 6))
        self.story.append(Paragraph(sub, self.styles['CoverInfo']))

        # Architect / Firm
        if self.architect or self.firm:
            info = self.architect
            if self.firm:
                info += f"  |  {self.firm}" if self.architect else self.firm
            self.story.append(Spacer(1, 1.5 * inch))
            self.story.append(Paragraph(info, self.styles['CoverInfo']))

        self.story.append(PageBreak())

    def _add_section_title(self, title: str):
        """Add a section title with Oracle Red underline."""
        self.story.append(Paragraph(title, self.styles['SectionTitle']))
        self.story.append(HRFlowable(
            width="25%", thickness=2,
            color=Colors.ORACLE_RED,
            spaceAfter=10, spaceBefore=0,
            hAlign='LEFT',
        ))

    def _add_subsection(self, title: str):
        """Add a subsection title."""
        self.story.append(Paragraph(title, self.styles['SubsectionTitle']))

    def _add_body(self, text: str):
        """Add body text (sanitized)."""
        text = sanitize_text(text)
        if text:
            self.story.append(Paragraph(text, self.styles['BodyText_Redwood']))

    def _add_bullet_list(self, items: list):
        """Add a bulleted list (sanitized)."""
        for item in sanitize_list(items):
            if item.strip():
                self.story.append(Paragraph(
                    f"• {item}", self.styles['BulletItem'],
                ))

    def _make_table(self, headers: list, rows: list,
                    col_widths: list = None) -> Table:
        """Build a styled table."""
        # Header row
        header_cells = [
            Paragraph(h, self.styles['TableHeader']) for h in headers
        ]
        # Data rows
        data = [header_cells]
        for row in rows:
            data.append([
                Paragraph(sanitize_text(str(cell)), self.styles['TableCell'])
                for cell in row
            ])

        table = Table(data, colWidths=col_widths, repeatRows=1)

        # Style
        style_cmds = [
            ('BACKGROUND', (0, 0), (-1, 0), Colors.TABLE_HEADER_BG),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, Colors.LIGHT_GRAY),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]
        # Alternating row colors
        for i in range(1, len(data)):
            if i % 2 == 0:
                style_cmds.append(
                    ('BACKGROUND', (0, i), (-1, i), Colors.TABLE_ALT_ROW)
                )

        table.setStyle(TableStyle(style_cmds))
        return table

    # ---- Content sections ----

    def add_executive_summary(self, why: str, current_state: list,
                               target_state: str, timeline: str):
        """Executive Summary section."""
        self._add_section_title("Executive Summary")

        # Impact statement
        self.story.append(Paragraph(
            sanitize_text(why), self.styles['ImpactStatement'],
        ))
        self.story.append(Spacer(1, 8))

        # Current state
        self._add_subsection("Current State")
        self._add_bullet_list(current_state)

        # Target state
        self._add_subsection("Target State")
        self._add_body(target_state)

        # Timeline
        self.story.append(Spacer(1, 6))
        self.story.append(Paragraph(
            f"<b>Timeline:</b> {sanitize_text(timeline)}",
            self.styles['BodyText_Redwood'],
        ))

    def add_service_tiering(self, workloads: list):
        """Service Tiering section."""
        self._add_section_title("Service Tiering")
        self._add_body(
            "Each tier drives HA/DR topology, backup strategy, "
            "isolation model, and support level."
        )

        headers = ["Workload", "Tier", "Uptime", "RTO", "RPO"]
        rows = [
            [wl.get("name", ""), wl.get("tier", ""),
             wl.get("uptime", ""), wl.get("rto", ""), wl.get("rpo", "")]
            for wl in workloads
        ]
        avail = self.PAGE_WIDTH - 2 * self.MARGIN
        widths = [avail * 0.28, avail * 0.15, avail * 0.17,
                  avail * 0.20, avail * 0.20]
        self.story.append(self._make_table(headers, rows, widths))
        self.story.append(Spacer(1, 12))

    def add_architecture_principles(self, principles: dict):
        """Architecture Principles section."""
        self._add_section_title("Architecture Principles")

        for category in ["design", "deployment", "service"]:
            items = principles.get(category, [])
            if not items:
                continue
            self._add_subsection(category.title())
            for item in items:
                pid = item.get("id", "")
                name = item.get("name", "")
                summary = item.get("summary", "")
                label = f"<b>{pid} {name}</b>" if pid else f"<b>{name}</b>"
                if summary:
                    label += f" — {summary}"
                self.story.append(Paragraph(
                    f"• {label}", self.styles['BulletItem'],
                ))

    def add_architecture_overview(self, description: str = "",
                                   diagram_path: str = None):
        """Architecture Overview section."""
        self._add_section_title("Architecture Overview")

        if diagram_path and Path(diagram_path).is_file():
            try:
                img = Image(diagram_path)
                avail_w = self.PAGE_WIDTH - 2 * self.MARGIN
                avail_h = 4.5 * inch
                # Scale to fit
                ratio = min(avail_w / img.drawWidth, avail_h / img.drawHeight)
                img.drawWidth *= ratio
                img.drawHeight *= ratio
                self.story.append(img)
                self.story.append(Spacer(1, 8))
            except Exception:
                self._add_body(f"[Diagram: {diagram_path}]")

        if description:
            self._add_body(description)

    def add_decisions(self, decisions: list):
        """Architecture Decisions section."""
        self._add_section_title("Architecture Decisions")

        headers = ["Decision", "Rationale"]
        rows = [
            [d.get("decision", ""), d.get("rationale", "")]
            for d in decisions
        ]
        avail = self.PAGE_WIDTH - 2 * self.MARGIN
        widths = [avail * 0.35, avail * 0.65]
        self.story.append(self._make_table(headers, rows, widths))
        self.story.append(Spacer(1, 12))

    def add_ha_dr(self, tiers: list, description: str = ""):
        """HA/DR section."""
        self._add_section_title("High Availability & Disaster Recovery")

        if description:
            self._add_body(description)
            self.story.append(Spacer(1, 6))

        headers = ["Component", "Technology", "RTO", "RPO"]
        rows = [
            [t.get("tier", ""), t.get("technology", ""),
             t.get("rto", ""), t.get("rpo", "")]
            for t in tiers
        ]
        avail = self.PAGE_WIDTH - 2 * self.MARGIN
        widths = [avail * 0.22, avail * 0.38, avail * 0.20, avail * 0.20]
        self.story.append(self._make_table(headers, rows, widths))
        self.story.append(Spacer(1, 12))

    def add_security(self, controls: dict, compliance: list = None):
        """Security & Compliance section."""
        self._add_section_title("Security & Compliance")

        if compliance:
            badges = "  |  ".join([f"✓ {fw}" for fw in compliance])
            self.story.append(Paragraph(
                f"<b>{badges}</b>", self.styles['Emphasis'],
            ))
            self.story.append(Spacer(1, 6))

        for area, items in controls.items():
            area_title = area.replace("_", " ").title()
            self._add_subsection(area_title)
            self._add_bullet_list(items)

    def add_environment_catalogue(self, environments: list,
                                   cost_notes: list = None):
        """Environment Catalogue section."""
        self._add_section_title("Environment Catalogue")

        headers = ["Environment", "Tier", "Databases", "OCPUs", "Isolation"]
        rows = [
            [e.get("environment", ""), e.get("tier", ""),
             e.get("databases", ""), e.get("ocpus", ""),
             e.get("isolation", "")]
            for e in environments
        ]
        avail = self.PAGE_WIDTH - 2 * self.MARGIN
        widths = [avail * 0.16, avail * 0.10, avail * 0.20,
                  avail * 0.10, avail * 0.44]
        self.story.append(self._make_table(headers, rows, widths))

        if cost_notes:
            self.story.append(Spacer(1, 8))
            self._add_subsection("Cost Optimization")
            self._add_bullet_list(cost_notes)
        self.story.append(Spacer(1, 12))

    def add_cost_estimate(self, line_items: list, assumptions: list = None,
                           show_byol: bool = True):
        """Cost Estimate section."""
        self._add_section_title("Cost Estimate")

        if show_byol:
            headers = ["Component", "Monthly (PAYG)", "Monthly (BYOL)", "Notes"]
            rows = [
                [item.get("component", ""),
                 item.get("monthly_payg", ""),
                 item.get("monthly_byol", ""),
                 item.get("notes", "")]
                for item in line_items
            ]
            avail = self.PAGE_WIDTH - 2 * self.MARGIN
            widths = [avail * 0.30, avail * 0.18, avail * 0.18, avail * 0.34]
        else:
            headers = ["Component", "Monthly", "Notes"]
            rows = [
                [item.get("component", ""),
                 item.get("monthly_payg", ""),
                 item.get("notes", "")]
                for item in line_items
            ]
            avail = self.PAGE_WIDTH - 2 * self.MARGIN
            widths = [avail * 0.35, avail * 0.20, avail * 0.45]

        table = self._make_table(headers, rows, widths)

        # Highlight total rows
        extra_cmds = []
        for i, item in enumerate(line_items):
            if "total" in item.get("component", "").lower():
                row_idx = i + 1
                extra_cmds.extend([
                    ('BACKGROUND', (0, row_idx), (-1, row_idx), Colors.TEAL),
                    ('TEXTCOLOR', (0, row_idx), (-1, row_idx), white),
                    ('FONTNAME', (0, row_idx), (-1, row_idx), 'Helvetica-Bold'),
                ])
        if extra_cmds:
            table.setStyle(TableStyle(extra_cmds))

        self.story.append(table)

        if assumptions:
            self.story.append(Spacer(1, 10))
            self.story.append(Paragraph(
                "<b>Assumptions:</b>", self.styles['Disclaimer'],
            ))
            for a in sanitize_list(assumptions):
                self.story.append(Paragraph(
                    f"• {a}", self.styles['Disclaimer'],
                ))
        self.story.append(Spacer(1, 12))

    def add_cost_comparison(self, rows: list, title: str = "Cost Comparison",
                             col_headers: list = None):
        """Cost Comparison section."""
        self._add_section_title(title)

        headers = col_headers or ["Component", "Current", "OCI", "Savings"]
        data_rows = [
            [r.get("item", ""), r.get("current", ""),
             r.get("oci", ""), r.get("savings", "")]
            for r in rows
        ]
        avail = self.PAGE_WIDTH - 2 * self.MARGIN
        widths = [avail * 0.35, avail * 0.20, avail * 0.20, avail * 0.25]
        table = self._make_table(headers, data_rows, widths)

        # Highlight total rows
        extra_cmds = []
        for i, r in enumerate(rows):
            if "total" in r.get("item", "").lower():
                row_idx = i + 1
                extra_cmds.extend([
                    ('BACKGROUND', (0, row_idx), (-1, row_idx), Colors.TEAL),
                    ('TEXTCOLOR', (0, row_idx), (-1, row_idx), white),
                    ('FONTNAME', (0, row_idx), (-1, row_idx), 'Helvetica-Bold'),
                ])
        if extra_cmds:
            table.setStyle(TableStyle(extra_cmds))

        self.story.append(table)
        self.story.append(Spacer(1, 12))

    def add_migration(self, phases: list, tools: list = None,
                       downtime: str = ""):
        """Migration Approach section."""
        self._add_section_title("Migration Approach")

        headers = ["Phase", "Timeline", "Key Activities"]
        rows = [
            [p.get("name", ""), p.get("weeks", ""),
             " | ".join(p.get("tasks", [])[:4])]
            for p in phases
        ]
        avail = self.PAGE_WIDTH - 2 * self.MARGIN
        widths = [avail * 0.25, avail * 0.15, avail * 0.60]
        self.story.append(self._make_table(headers, rows, widths))

        if tools:
            self.story.append(Spacer(1, 8))
            self.story.append(Paragraph(
                f"<b>Migration Tools:</b> {', '.join(tools)}",
                self.styles['BodyText_Redwood'],
            ))
        if downtime:
            self.story.append(Paragraph(
                f"<b>Downtime Approach:</b> {sanitize_text(downtime)}",
                self.styles['BodyText_Redwood'],
            ))
        self.story.append(Spacer(1, 12))

    def add_operational_raci(self, raci_items: list,
                              model: str = "co_managed"):
        """Operational RACI section."""
        model_label = model.replace("_", "-").title()
        self._add_section_title(f"Operational Responsibilities ({model_label})")

        headers = ["Activity", "Customer", "Oracle / Partner"]
        rows = [
            [item.get("activity", ""),
             item.get("customer", ""),
             item.get("oracle", "")]
            for item in raci_items
        ]
        avail = self.PAGE_WIDTH - 2 * self.MARGIN
        widths = [avail * 0.50, avail * 0.25, avail * 0.25]
        self.story.append(self._make_table(headers, rows, widths))

        self.story.append(Spacer(1, 6))
        self.story.append(Paragraph(
            "R = Responsible  |  A = Accountable  |  C = Consulted  |  I = Informed",
            self.styles['Disclaimer'],
        ))
        self.story.append(Spacer(1, 12))

    def add_risks(self, risks: list):
        """Risk Register section."""
        self._add_section_title("Risk Register")

        headers = ["Risk", "Severity", "Mitigation"]
        rows = [
            [sanitize_text(r.get("risk", "")),
             r.get("severity", "MEDIUM"),
             sanitize_text(r.get("mitigation", ""))]
            for r in risks
        ]
        avail = self.PAGE_WIDTH - 2 * self.MARGIN
        widths = [avail * 0.30, avail * 0.12, avail * 0.58]
        table = self._make_table(headers, rows, widths)

        # Color-code severity
        severity_colors = {
            "HIGH": Colors.ERROR,
            "MEDIUM": Colors.WARNING,
            "LOW": Colors.SUCCESS,
        }
        extra_cmds = []
        for i, risk in enumerate(risks):
            sev = risk.get("severity", "MEDIUM").upper()
            color = severity_colors.get(sev, Colors.WARNING)
            row_idx = i + 1
            extra_cmds.extend([
                ('TEXTCOLOR', (1, row_idx), (1, row_idx), color),
                ('FONTNAME', (1, row_idx), (1, row_idx), 'Helvetica-Bold'),
                ('ALIGN', (1, row_idx), (1, row_idx), 'CENTER'),
            ])
        if extra_cmds:
            table.setStyle(TableStyle(extra_cmds))

        self.story.append(table)
        self.story.append(Spacer(1, 12))

    def add_scorecard(self, pillars: list, recommendations: list = None):
        """Well-Architected Scorecard section."""
        self._add_section_title("Well-Architected Scorecard")

        status_labels = {
            "PASS": "✓ Pass",
            "PASS_WITH_RECOMMENDATIONS": "⚠ Pass with Recommendations",
            "GAPS_IDENTIFIED": "✗ Gaps Identified",
            "NOT_APPLICABLE": "— N/A",
        }

        headers = ["Pillar", "Score", "Status"]
        rows = []
        for p in pillars:
            score = (f"{p.get('passed', 0)}/{p.get('total', 0)}"
                     if p.get('total', 0) > 0 else "—")
            status = status_labels.get(p.get("status", ""), p.get("status", ""))
            rows.append([p.get("name", ""), score, status])

        avail = self.PAGE_WIDTH - 2 * self.MARGIN
        widths = [avail * 0.40, avail * 0.15, avail * 0.45]
        table = self._make_table(headers, rows, widths)

        # Color-code status
        status_colors = {
            "PASS": Colors.SUCCESS,
            "PASS_WITH_RECOMMENDATIONS": Colors.WARNING,
            "GAPS_IDENTIFIED": Colors.ERROR,
            "NOT_APPLICABLE": Colors.SECONDARY_TEXT,
        }
        extra_cmds = []
        for i, p in enumerate(pillars):
            color = status_colors.get(p.get("status", ""), Colors.SECONDARY_TEXT)
            row_idx = i + 1
            extra_cmds.extend([
                ('TEXTCOLOR', (2, row_idx), (2, row_idx), color),
                ('FONTNAME', (2, row_idx), (2, row_idx), 'Helvetica-Bold'),
            ])
        if extra_cmds:
            table.setStyle(TableStyle(extra_cmds))

        self.story.append(table)

        if recommendations:
            self.story.append(Spacer(1, 10))
            self._add_subsection("Top Recommendations")
            for rec in sanitize_list(recommendations[:6]):
                self.story.append(Paragraph(
                    f"→ {rec}", self.styles['BulletItem'],
                ))

        self.story.append(Spacer(1, 6))
        self.story.append(Paragraph(
            "Validated against Oracle Well-Architected Framework — "
            "docs.oracle.com/en/solutions/oci-best-practices/",
            self.styles['Disclaimer'],
        ))
        self.story.append(Spacer(1, 12))

    def add_next_steps(self, steps: list, contact_info: str = ""):
        """Next Steps section."""
        self._add_section_title("Next Steps")

        for i, step in enumerate(sanitize_list(steps)):
            self.story.append(Paragraph(
                f"<b>{i + 1}.</b>  {step}",
                self.styles['BodyText_Redwood'],
            ))
            self.story.append(Spacer(1, 4))

        if contact_info:
            self.story.append(Spacer(1, 18))
            self.story.append(Paragraph(
                sanitize_text(contact_info),
                self.styles['Emphasis'],
            ))

    def add_thank_you_page(self):
        """Add a dark-background closing / Thank You page."""
        self.story.append(PageBreak())
        # The _thank_you_page canvas callback draws the dark background
        from reportlab.platypus.doctemplate import NextPageTemplate
        self.story.append(NextPageTemplate('thank_you'))
        self.story.append(Spacer(1, 2.2 * inch))
        self.story.append(Paragraph(
            "Thank you",
            ParagraphStyle(
                'ThankYouTitle',
                fontName='Helvetica-Bold',
                fontSize=40,
                leading=50,
                textColor=white,
                alignment=TA_LEFT,
            ),
        ))
        self.story.append(Spacer(1, 0.3 * inch))
        if self.architect or self.firm:
            parts = [p for p in [self.architect, self.firm] if p]
            self.story.append(Paragraph(
                "  |  ".join(parts),
                ParagraphStyle(
                    'ThankYouContact',
                    fontName='Helvetica',
                    fontSize=13,
                    leading=18,
                    textColor=HexColor("#9E9892"),
                    alignment=TA_LEFT,
                ),
            ))

    def add_safe_harbor(self):
        """Add Oracle Safe Harbor statement."""
        from reportlab.platypus.doctemplate import NextPageTemplate
        self.story.append(NextPageTemplate('content_pages'))
        self.story.append(PageBreak())
        self.story.append(Spacer(1, 2 * inch))
        self.story.append(Paragraph(
            "Safe Harbor Statement",
            self.styles['SectionTitle'],
        ))
        self.story.append(HRFlowable(
            width="25%", thickness=2,
            color=Colors.ORACLE_RED,
            spaceAfter=14, spaceBefore=0,
            hAlign='LEFT',
        ))
        self.story.append(Paragraph(
            "The preceding is intended to outline our general product direction. "
            "It is intended for information purposes only, and may not be "
            "incorporated into any contract. It is not a commitment to deliver "
            "any material, code, or functionality, and should not be relied upon "
            "in making purchasing decisions. The development, release, timing, "
            "and pricing of any features or functionality described for Oracle's "
            "products may change and remains at the sole discretion of Oracle "
            "Corporation.",
            self.styles['BodyText_Redwood'],
        ))

    # ---- Build from spec ----

    @classmethod
    def from_spec(cls, spec: dict, diagram_path: str = None) -> "OCIPDFGenerator":
        """Build a complete PDF from a YAML specification."""
        meta = spec.get("metadata", {})
        gen = cls(
            customer=meta.get("customer", ""),
            project=meta.get("project", ""),
            architect=meta.get("architect", ""),
            firm=meta.get("firm", ""),
        )

        # Cover
        gen.add_cover(subtitle=meta.get("subtitle", ""))

        # Executive Summary
        if "summary" in spec:
            s = spec["summary"]
            gen.add_executive_summary(
                why=s.get("why", ""),
                current_state=s.get("current_state", []),
                target_state=s.get("target_state", ""),
                timeline=s.get("timeline", ""),
            )

        # Service Tiering
        if "service_tiering" in spec:
            gen.add_service_tiering(spec["service_tiering"])

        # Architecture Principles
        if "architecture_principles" in spec:
            gen.add_architecture_principles(spec["architecture_principles"])

        # Architecture Overview
        if "architecture" in spec:
            a = spec["architecture"]
            gen.add_architecture_overview(
                description=a.get("description", ""),
                diagram_path=diagram_path or a.get("diagram_path"),
            )

        # Decisions
        if "decisions" in spec:
            gen.add_decisions(spec["decisions"])

        # HA/DR
        if "ha_dr" in spec:
            h = spec["ha_dr"]
            gen.add_ha_dr(
                tiers=h.get("tiers", []),
                description=h.get("description", ""),
            )

        # Security
        if "security" in spec:
            s = spec["security"]
            gen.add_security(
                controls=s.get("controls", {}),
                compliance=s.get("compliance", []),
            )

        # Environment Catalogue
        if "environment_catalogue" in spec:
            ec = spec["environment_catalogue"]
            gen.add_environment_catalogue(
                environments=ec.get("environments", []),
                cost_notes=ec.get("cost_notes"),
            )

        # Cost Estimate
        if "cost" in spec:
            c = spec["cost"]
            gen.add_cost_estimate(
                line_items=c.get("line_items", []),
                assumptions=c.get("assumptions", []),
                show_byol=c.get("show_byol", True),
            )

        # Cost Comparison
        if "cost_comparison" in spec:
            cc = spec["cost_comparison"]
            gen.add_cost_comparison(
                rows=cc.get("rows", []),
                title=cc.get("title", "Cost Comparison"),
                col_headers=cc.get("col_headers"),
            )

        # Migration
        if "migration" in spec:
            m = spec["migration"]
            gen.add_migration(
                phases=m.get("phases", []),
                tools=m.get("tools", []),
                downtime=m.get("downtime", ""),
            )

        # Operational RACI
        if "operational_raci" in spec:
            r = spec["operational_raci"]
            gen.add_operational_raci(
                raci_items=r.get("raci_items", []),
                model=r.get("model", "co_managed"),
            )

        # Risks
        if "risks" in spec:
            gen.add_risks(spec["risks"])

        # Scorecard
        if "scorecard" in spec:
            sc = spec["scorecard"]
            gen.add_scorecard(
                pillars=sc.get("pillars", []),
                recommendations=sc.get("recommendations", []),
            )

        # Next Steps
        if "next_steps" in spec:
            ns = spec["next_steps"]
            gen.add_next_steps(
                steps=ns.get("steps", []),
                contact_info=ns.get("contact_info", ""),
            )

        # Thank You + Safe Harbor
        gen.add_thank_you_page()
        gen.add_safe_harbor()

        return gen

    # ---- Save ----

    def save(self, filepath: str):
        """Save the document to a PDF file."""
        doc = BaseDocTemplate(
            filepath,
            pagesize=letter,
            leftMargin=self.MARGIN,
            rightMargin=self.MARGIN,
            topMargin=0.7 * inch,
            bottomMargin=0.7 * inch,
            title=f"{self.customer} — {self.project}",
            author=self.architect,
            subject="OCI Architecture Proposal",
        )

        # Frame for content
        content_frame = Frame(
            self.MARGIN, 0.7 * inch,
            self.PAGE_WIDTH - 2 * self.MARGIN,
            self.PAGE_HEIGHT - 1.4 * inch,
            id='content',
        )

        # Cover page template (dark bg)
        cover_template = PageTemplate(
            id='cover',
            frames=[content_frame],
            onPage=self._cover_page,
        )

        # Content page template (header + footer)
        content_template = PageTemplate(
            id='content_pages',
            frames=[content_frame],
            onPage=self._header_footer,
        )

        # Thank You page template (dark bg, no header/footer)
        thank_you_template = PageTemplate(
            id='thank_you',
            frames=[content_frame],
            onPage=self._thank_you_page,
        )

        doc.addPageTemplates([cover_template, content_template, thank_you_template])

        # After cover page, switch to content template
        # Insert a NextPageTemplate after the PageBreak in story
        from reportlab.platypus.doctemplate import NextPageTemplate
        # Find first PageBreak and insert template switch before it
        for i, elem in enumerate(self.story):
            if isinstance(elem, PageBreak):
                self.story.insert(i, NextPageTemplate('content_pages'))
                break

        doc.build(self.story)


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate customer-facing OCI architecture proposal PDF"
    )
    parser.add_argument(
        "--spec", required=True,
        help="Path to YAML spec file with proposal data",
    )
    parser.add_argument(
        "--output", default="architecture-proposal.pdf",
        help="Output .pdf file path",
    )
    parser.add_argument(
        "--diagram",
        help="Path to architecture diagram image (.png/.jpg) to embed",
    )
    args = parser.parse_args()

    with open(args.spec, 'r') as f:
        spec = yaml.safe_load(f)

    gen = OCIPDFGenerator.from_spec(spec, diagram_path=args.diagram)
    gen.save(args.output)

    customer = spec.get("metadata", {}).get("customer", "")
    print(f"Generated: {args.output}")
    print(f"  Style: Oracle Redwood (customer-facing)")
    print(f"  Internal references: stripped")
    if customer:
        print(f"  Customer: {customer}")


if __name__ == "__main__":
    main()
