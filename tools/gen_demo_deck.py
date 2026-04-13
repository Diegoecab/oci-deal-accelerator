#!/usr/bin/env python3
"""
OCI Deal Accelerator — Demo Presentation Generator

10-minute technical demo deck: AI-powered SA workflow acceleration.
Uses Oracle FY26 template via OraclePresBase.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

from oci_pptx_base import Colors, Layouts, OraclePresBase


class DemoDeckGenerator(OraclePresBase):
    TITLE_ACCENT_COLOR = Colors.TEAL
    MARGIN = Inches(0.5)
    SLIDE_WIDTH = Inches(13.333)

    def add_cover(self):
        """Slide 1: Cover — dark, high impact."""
        slide = self._add_layout_slide(Layouts.COVER_DARK)
        self._set_placeholder(slide, 0, "OCI Deal Accelerator")
        self._set_placeholder(slide, 1,
            "AI-Powered Architecture Proposals in Hours, Not Days")
        return slide

    def add_impact_slide(self, metric, statement, detail=""):
        """Big metric slide — dark background, single number."""
        slide = self._add_layout_slide(Layouts.IMPACT_DARK)
        self._set_placeholder(slide, 0, metric)
        self._set_placeholder(slide, 1, statement)
        if detail:
            self._set_placeholder(slide, 37, detail)
        return slide

    def add_content_slide(self, title, bullets, note=""):
        """Standard content slide with title bar + bullet list."""
        slide = self._add_blank_slide()
        self._add_title_bar(slide, title, margin=self.MARGIN)

        y = Inches(1.4)
        txBox = self._add_textbox(
            slide, self.MARGIN + Inches(0.1), y,
            Inches(12), Inches(5),
            text="", font_size=15,
        )
        tf = txBox.text_frame
        tf.word_wrap = True
        # First paragraph already exists
        tf.paragraphs[0].text = bullets[0] if bullets else ""
        tf.paragraphs[0].font.size = Pt(15)
        tf.paragraphs[0].font.name = self.FONT
        tf.paragraphs[0].font.color.rgb = Colors.PRIMARY_TEXT
        tf.paragraphs[0].space_after = Pt(6)

        for b in bullets[1:]:
            self._add_paragraph(tf, b, font_size=15, space_after=6)

        if note:
            self._add_textbox(
                slide, self.MARGIN, Inches(6.5),
                Inches(12), Inches(0.5),
                text=note, font_size=11, italic=True,
                color=Colors.SECONDARY_TEXT,
            )
        return slide

    def add_prompt_table_slide(self, title, rows):
        """Slide with a table of option # | prompt example."""
        slide = self._add_blank_slide()
        self._add_title_bar(slide, title, margin=self.MARGIN)

        n = len(rows) + 1
        row_h = min(0.52, 5.2 / max(n, 1))
        table = self._add_table(
            slide, n, 3,
            self.MARGIN, Inches(1.3),
            Inches(12.3), Inches(row_h * n),
        )
        table.columns[0].width = Inches(0.6)
        table.columns[1].width = Inches(3.0)
        table.columns[2].width = Inches(8.7)

        for j, h in enumerate(["#", "Capability", "Live Prompt"]):
            self._style_table_cell(
                table.cell(0, j), h, font_size=10, bold=True,
                color=Colors.WHITE, bg_color=Colors.TEAL,
                alignment=PP_ALIGN.CENTER if j == 0 else PP_ALIGN.LEFT,
            )

        for i, (num, cap, prompt) in enumerate(rows):
            ri = i + 1
            bg = Colors.TABLE_ALT_ROW if ri % 2 == 0 else None
            self._style_table_cell(table.cell(ri, 0), str(num), font_size=10,
                                   bold=True, bg_color=bg, alignment=PP_ALIGN.CENTER)
            self._style_table_cell(table.cell(ri, 1), cap, font_size=10,
                                   bold=True, bg_color=bg)
            self._style_table_cell(table.cell(ri, 2), prompt, font_size=9,
                                   bg_color=bg)

        return slide

    def add_before_after_slide(self):
        """Before/After comparison slide."""
        slide = self._add_blank_slide()
        self._add_title_bar(slide, "Before vs After: SA Workflow", margin=self.MARGIN)

        # BEFORE column
        self._add_rect(slide, self.MARGIN, Inches(1.4),
                        Inches(5.8), Inches(0.5), fill_color=Colors.ORACLE_RED)
        self._add_textbox(slide, self.MARGIN + Inches(0.2), Inches(1.45),
                          Inches(5.4), Inches(0.4),
                          text="BEFORE — Manual SA Workflow",
                          font_size=14, bold=True, color=Colors.WHITE)

        before = [
            ("Discovery call", "1h"),
            ("Research services + sizing", "2-4h"),
            ("Build architecture diagram", "1-2h"),
            ("Write proposal deck", "3-5h"),
            ("Cost estimate + BOM", "1-2h"),
            ("WA review (if time permits)", "2-3h"),
            ("Internal review + revisions", "1-2h"),
            ("TOTAL", "11-19 hours (2-3 days)"),
        ]

        y = Inches(2.0)
        for task, time in before:
            bold = task == "TOTAL"
            color = Colors.ORACLE_RED if bold else Colors.PRIMARY_TEXT
            self._add_textbox(slide, Inches(0.7), y, Inches(3.8), Inches(0.32),
                              text=task, font_size=11, bold=bold, color=color)
            self._add_textbox(slide, Inches(4.6), y, Inches(1.5), Inches(0.32),
                              text=time, font_size=11, bold=bold, color=color,
                              alignment=PP_ALIGN.RIGHT)
            y += Inches(0.35)

        # AFTER column
        self._add_rect(slide, Inches(6.8), Inches(1.4),
                        Inches(5.8), Inches(0.5), fill_color=Colors.FOREST)
        self._add_textbox(slide, Inches(7.0), Inches(1.45),
                          Inches(5.4), Inches(0.4),
                          text="AFTER — AI-Assisted Workflow",
                          font_size=14, bold=True, color=Colors.WHITE)

        after = [
            ("Discovery call", "1h"),
            ("Paste notes → Full proposal", "3-5 min"),
            ("Architecture diagram", "included"),
            ("Slide deck (18 slides)", "included"),
            ("Cost estimate + BOM", "included"),
            ("WA review (5-pillar)", "included"),
            ("SA reviews AI output", "30-60 min"),
            ("TOTAL", "1.5-2 hours (same day)"),
        ]

        y = Inches(2.0)
        for task, time in after:
            bold = task == "TOTAL"
            color = Colors.FOREST if bold else Colors.PRIMARY_TEXT
            self._add_textbox(slide, Inches(7.0), y, Inches(3.8), Inches(0.32),
                              text=task, font_size=11, bold=bold, color=color)
            self._add_textbox(slide, Inches(11.0), y, Inches(1.5), Inches(0.32),
                              text=time, font_size=11, bold=bold, color=color,
                              alignment=PP_ALIGN.RIGHT)
            y += Inches(0.35)

        # Savings callout
        self._add_rect(slide, Inches(3.5), Inches(5.3),
                        Inches(6.3), Inches(0.7), fill_color=Colors.TEAL)
        self._add_textbox(slide, Inches(3.6), Inches(5.35),
                          Inches(6.1), Inches(0.6),
                          text="85% time reduction  |  Same day delivery  |  Higher quality (WA-validated)",
                          font_size=14, bold=True, color=Colors.WHITE,
                          alignment=PP_ALIGN.CENTER)

        return slide

    def add_divider(self, text):
        slide = self._add_layout_slide(Layouts.DIVIDER_DARK)
        self._set_placeholder(slide, 0, text)
        return slide


def build_demo_deck(output_path):
    gen = DemoDeckGenerator()

    # ── SLIDE 1: Cover (0:00-0:15) ──
    gen.add_cover()

    # ── SLIDE 2: The Problem — impact (0:15-1:00) ──
    gen.add_impact_slide(
        "11-19h",
        "Time an SA spends per proposal",
        "Research + diagram + deck + costs + review — repeated for every deal"
    )

    # ── SLIDE 3: The Aha Moment (1:00-2:00) ──
    gen.add_before_after_slide()

    # ── SLIDE 4: What Is It (2:00-3:00) ──
    gen.add_content_slide(
        "OCI Deal Accelerator — What Is It?",
        [
            "An AI skill (system prompt + knowledge base + tools) for any LLM with tool-use and 100K+ context",
            "Works on Claude, Codex, GPT, Gemini — any model that can read files + run Python",
            "Aligned with ECAL framework: Define > Design > Deliver",
            "40+ YAML files of field knowledge (services, sizing, pricing, patterns, gotchas)",
            "7 Python generators: .pptx, .drawio, .pdf, .xlsx, WA scorecard, BOM, AppCA",
            "14 capabilities accessible via natural language — not a chatbot, a domain-specific SA tool",
        ],
    )

    # ── SLIDE 5: Divider — Live Demo (3:00) ──
    gen.add_divider("Live Demo: 14 Capabilities")

    # ── SLIDE 6: Prompts 1-7 (3:00-6:00) ──
    gen.add_prompt_table_slide(
        "Design, Validate & Compare (Options 1-7)",
        [
            ("1", "Full proposal",
             "Cliente farmaceutico en Mexico, 3 Oracle DBs (EBS R12 prod, SAP, DW) en "
             "Exadata X6 on-prem. HW refresh vence en 6 meses. Quieren migrar a OCI, "
             "RPO<15min, RTO<1h, necesitan compliance SOX. 200 usuarios concurrentes, "
             "2TB data, pico en cierre fiscal. Budget: reducir 30% vs renovar HW."),
            ("2", "Architecture diagram",
             "Diagrama: ExaCS en Queretaro (prod) + Standby con Data Guard en Sao Paulo, "
             "Hub-Spoke networking con DRG, FastConnect 10Gbps dual desde Mexico City, "
             "bastion en public subnet, WAF para apps web, Vault para TDE keys."),
            ("3", "Slide deck",
             "Genera el deck para la propuesta del cliente farmaceutico."),
            ("4", "Cost estimate",
             "ExaCS X11M Quarter Rack BYOL, 2 DB servers, 3 storage servers, "
             "400GB RAM, 10TB usable + ADB-S 16 ECPU + FastConnect 1Gbps dual + "
             "50TB Object Storage + OCI Vault. 12 meses, 40% descuento."),
            ("5", "WA review",
             "Review: ADB-S 23ai en Sao Paulo region unica, IAM con admin por defecto, "
             "sin encryption at rest explicita, sin WAF, monitoring con scripts custom, "
             "patching manual mensual, backup solo local, sin network segmentation."),
            ("6", "Feature check",
             "Does ADB-S Dedicated Elastic Pool support Auto Indexing on 23ai? "
             "And what about AI Vector Search with HNSW indexes at 100M+ vectors?"),
            ("7", "Competitive",
             "Customer comparing ADB-S vs AWS Aurora PostgreSQL for a mixed OLTP+analytics "
             "workload, 500GB, needs partitioning, RAC equivalent, and BYOL licensing. "
             "They think Aurora is cheaper. Give me honest pros and cons."),
        ],
    )

    # ── SLIDE 7: Prompts 8-14 (6:00-8:30) ──
    gen.add_prompt_table_slide(
        "Strategy, KB, Governance & SA Tools (Options 8-14)",
        [
            ("8", "Business case",
             "Business case: 5 Oracle DBs on-prem (EBS, Siebel, DW, 2 custom), "
             "$1.2M/yr infra (HW refresh vence Q3). CTO quiere cloud, CFO quiere "
             "numeros. Necesito TCO 3 anos, ROI, risk of doing nothing, y que pasa "
             "si renuevan HW por 5 anos mas. Audience: board de directores."),
            ("9", "Field findings",
             "What real issues has the field team found with ADB-S Dedicated Elastic "
             "Pool? Include DEP provisioning times, maintenance windows, and ADG."),
            ("10", "Reference arch",
             "Reference architectures for cross-region DR with Exadata and Data Guard. "
             "Need options for both ExaCS and ADB-S with automatic failover."),
            ("11", "Report finding",
             "New finding: ExaCS iormcal fails silently when storage server count < 3. "
             "Product: ExaCS, Version: 23ai, Severity: MEDIUM, found during pharma "
             "engagement in Mexico. Workaround: validate IORM plan output after apply, "
             "check v$iorm_plans for actual vs requested shares."),
            ("12", "ECAL readiness",
             "Score this engagement: tenemos discovery notes, workload profile, y un "
             "diagrama de arquitectura. No hay business case, no value story, no "
             "handover plan, no operations model. Customer es farmaceutica en Mexico, "
             "engagement tier standard, estamos en la fase Design."),
            ("13", "BOM generator",
             "BOM: ExaCS X11M Half Rack BYOL, 4 DB servers 128 ECPUs each, "
             "6 storage servers, ADB-S 32 ECPU, 50TB block storage, "
             "FastConnect 10Gbps dual, OCI Vault, 12 months, 45% discount."),
            ("14", "BOM for AppCA",
             "Same BOM as 13 but in AppCA import format for deal approval."),
        ],
    )

    # ── SLIDE 8: Architecture (8:30-9:00) ──
    gen.add_content_slide(
        "How It Works — Under the Hood",
        [
            "SKILL.md: 400-line system prompt with ECAL-aligned workflow rules",
            "kb/: 40+ YAML files — services, sizing, pricing (auto-refreshed), patterns, gotchas",
            "tools/: 7 Python generators that produce real files, not markdown",
            "Oracle FY26 .pptx template with Redwood design system colors",
            "scripts/: WA validation engine against 5-pillar framework (80+ checks)",
            "Field findings tracker with contributor attribution + confidence levels",
            "SKU catalog refreshed from Oracle public pricing API",
        ],
        note="Everything is composable: patterns combine, KB is the moat, field experience > documentation"
    )

    # ── SLIDE 9: Key Takeaways (9:00-9:30) ──
    gen.add_content_slide(
        "Key Takeaways",
        [
            "85% time reduction: from 2-3 days to 2 hours per proposal",
            "Higher quality: every proposal is WA-validated with 5-pillar scoring",
            "Field knowledge compounds: gotchas and findings feed back into the KB",
            "ECAL-aligned: Define > Design > Deliver with artefact tracking",
            "Real deliverables: .pptx, .drawio, .pdf, .xlsx — not chat summaries",
            "SA stays in control: AI generates, architect reviews and refines",
        ],
    )

    # ── SLIDE 10: Closing ──
    gen.add_closing_slide(
        name="OCI Deal Accelerator",
        title="github.com/your-org/oci-deal-accelerator",
    )

    gen.save(output_path)
    print(f"Generated: {output_path}")
    print(f"  Slides: {gen.slide_count}")
    print(f"  Duration: ~10 minutes")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "demo-presentation.pptx"
    build_demo_deck(out)
