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

try:
    from oci_pptx_base import Colors, Layouts, OraclePresBase
except ModuleNotFoundError:
    from tools.oci_pptx_base import Colors, Layouts, OraclePresBase


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

    def add_comparison_table_slide(self, title, rows):
        """Two-column comparison: Generic LLM vs This Skill."""
        slide = self._add_blank_slide()
        self._add_title_bar(slide, title, margin=self.MARGIN)

        n = len(rows) + 1
        row_h = min(0.58, 5.0 / max(n, 1))
        table = self._add_table(
            slide, n, 3,
            self.MARGIN, Inches(1.35),
            Inches(12.3), Inches(row_h * n),
        )
        table.columns[0].width = Inches(2.8)
        table.columns[1].width = Inches(4.75)
        table.columns[2].width = Inches(4.75)

        headers = ["", "Generic LLM (ChatGPT, etc.)", "OCI Deal Accelerator"]
        header_colors = [Colors.TEAL, Colors.ORACLE_RED, Colors.FOREST]
        for j, (h, hc) in enumerate(zip(headers, header_colors)):
            self._style_table_cell(
                table.cell(0, j), h, font_size=10, bold=True,
                color=Colors.WHITE, bg_color=hc,
                alignment=PP_ALIGN.CENTER,
            )

        for i, (aspect, generic, skill) in enumerate(rows):
            ri = i + 1
            bg = Colors.TABLE_ALT_ROW if ri % 2 == 0 else None
            self._style_table_cell(table.cell(ri, 0), aspect, font_size=10,
                                   bold=True, bg_color=bg)
            self._style_table_cell(table.cell(ri, 1), generic, font_size=9,
                                   bg_color=bg)
            self._style_table_cell(table.cell(ri, 2), skill, font_size=9,
                                   bg_color=bg)

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

    # ── SLIDE 4: Why Not Just Use ChatGPT? (2:00-3:30) ──
    gen.add_comparison_table_slide(
        '"Can\'t I Just Ask ChatGPT to Make Me a Deck?"',
        [
            ("Pricing",
             "Training data from 2024. Invents SKUs. No discount calc. Can't generate a BOM.",
             "160+ SKUs auto-refreshed from Oracle API. Real PAYG/BYOL. BOM + AppCA export."),
            ("Architecture",
             "Generic diagrams. Suggests services that don't exist or don't apply.",
             "Patterns from real deployments. Knows ExaCS needs 3+ storage for IORM."),
            ("Field gotchas",
             "Doesn't know DEP takes 3 weeks to provision, or that ADG must be disabled first.",
             "8+ validated findings from real engagements, with workarounds and SR refs."),
            ("Competitive",
             "Tends to be either biased or generic. No real cost comparison data.",
             "Honest pros/cons per service. BYOL 50-75% cheaper data. Knows where AWS wins."),
            ("WA validation",
             "Gives generic 'best practices' list. No scoring, no gap analysis.",
             "80+ checks across 5 pillars. Automated scoring. Actionable gap report."),
            ("Compliance",
             "Generic SOX/PCI advice. Doesn't know OCI-specific controls.",
             "OCI Vault for TDE, Unified Auditing, compartment isolation — mapped to frameworks."),
            ("Output format",
             "Markdown or basic text. Manual copy-paste to slides.",
             "Oracle FY26 .pptx template, .drawio, branded .pdf, .xlsx — ready to present."),
            ("Improves over time",
             "Frozen at training cutoff. Learns nothing from your engagements.",
             "Every SA adds findings. Pricing refreshes. KB compounds with every deal."),
        ],
    )

    # ── SLIDE 5: What Is It (3:30-4:00) ──
    gen.add_content_slide(
        "OCI Deal Accelerator — What Is It?",
        [
            "An AI skill (system prompt + knowledge base + tools) for any LLM with tool-use and 100K+ context",
            "Works on Claude, Codex, GPT, Gemini — any model that can read files + run Python",
            "The LLM is the engine. The KB + tools are the fuel. The SA is the driver.",
            "Aligned with ECAL framework: Define > Design > Deliver",
            "7 Python generators: .pptx, .drawio, .pdf, .xlsx, WA scorecard, BOM, AppCA",
            "14 capabilities accessible via natural language — not a chatbot, a domain-specific SA tool",
        ],
    )

    # ── SLIDE 6: Divider — Live Demo (4:00) ──
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

    # ── SLIDE 8: The KB Is the Moat (7:30-8:15) ──
    gen.add_content_slide(
        "The Knowledge Base Is the Moat",
        [
            "40+ YAML files of FIELD knowledge — not regurgitated docs, real experience",
            "Services: what each OCI service does, when to use it, gotchas, sizing rules",
            "Patterns: composable architecture blocks (HA, DR, networking, security baselines)",
            "Pricing: 160+ SKUs auto-refreshed from Oracle public API (refresh_sku_catalog.py)",
            "Field findings: production issues with workarounds, contributor attribution, confidence levels",
            "Competitive: honest AWS/Azure mapping with real advantage/disadvantage per service",
            "Architecture Center: 123 curated reference architectures with service + tag filtering",
            "",
            "Without the KB, the AI is just another chatbot. With it, it's a domain expert.",
        ],
    )

    # ── SLIDE 9: Auto-refresh + Collaborative Model (8:15-9:00) ──
    gen.add_content_slide(
        "Self-Updating KB + Collaborative Field Intelligence",
        [
            "AUTO-REFRESH — pricing stays current without manual intervention:",
            "   python refresh_sku_catalog.py --refresh --diff   # updates 160+ SKUs from Oracle API",
            "   python refresh_arch_catalog.py --whats-new       # crawls Architecture Center for new entries",
            "",
            "COLLABORATIVE — every SA contributes, everyone benefits:",
            "   findings_cli.py add --product ExaCS --severity HIGH --summary '...'",
            "   Each finding has: contributor, team, client, confidence, confirmations[]",
            "   Other SAs can confirm: findings_cli.py confirm FF-202603-001 --name '...'",
            "",
            "GOVERNANCE — quality stays high as the KB grows:",
            "   kb_cli.py health      # freshness dashboard: 63 files, stale detection",
            "   kb_cli.py stats stale # reports files older than review cadence",
            "   Every file has last_verified date + domain owner in kb-owners.yaml",
            "",
            "The KB compounds: every engagement makes the next one faster and better.",
        ],
    )

    # ── SLIDE 10: MCP Server — Zero Setup (8:30-9:00) ──
    gen.add_content_slide(
        "MCP Server: Use It From Any Client — Zero Code Setup",
        [
            "The skill also runs as an MCP (Model Context Protocol) server.",
            "14 tools exposed over HTTP — same capabilities, no local repo needed.",
            "",
            "SUPPORTED CLIENTS — connect once, use forever:",
            "   Claude Code / Claude Desktop (OAuth)  |  Cursor (OAuth)",
            "   Codex - OpenAI (Bearer token)         |  Windsurf (SSE)",
            "   Any MCP-compliant client",
            "",
            "SETUP — 1 command, done:",
            "   claude mcp add --transport http oci-deal-accelerator \\",
            '       "https://mcp.tech-lad.com/deal-accelerator/mcp/"',
            "",
            "HOW IT WORKS:",
            "   Your IDE / Claude  -->  MCP Server (Docker)  -->  KB + Tools + Generators",
            "   You type a prompt  -->  Server runs the tool  -->  You get .pptx, .xlsx, .json",
            "",
            "Zero Python setup. Zero repo cloning. Zero dependency management.",
            "The SA opens their IDE, connects to the MCP, and starts working.",
        ],
    )

    # ── SLIDE 11: Key Takeaways (9:00-9:30) ──
    gen.add_content_slide(
        "Key Takeaways",
        [
            "85% time reduction: from 2-3 days to 2 hours per proposal",
            "Higher quality: every proposal is WA-validated with 5-pillar scoring",
            "The KB is the moat: field experience > documentation > AI hallucination",
            "Self-updating: pricing + architectures refresh automatically",
            "Collaborative: every SA's gotcha becomes everyone's advantage",
            "MCP server: zero setup, use from any AI client (Claude, Codex, Cursor...)",
            "Real deliverables: .pptx, .drawio, .pdf, .xlsx, BOM, AppCA — not chat summaries",
            "SA stays in control: AI generates, architect reviews and refines",
        ],
    )

    # ── SLIDE 12: Get Started ──
    gen.add_content_slide(
        "Get Started Right Now",
        [
            "OPTION A — MCP Server (recommended, zero setup):",
            "   claude mcp add --transport http oci-deal-accelerator \\",
            '       "https://mcp.tech-lad.com/deal-accelerator/mcp/"',
            "",
            "OPTION B — Clone the skill repo (full access to KB + tools):",
            "   git clone https://git.tech-lad.com.br/diegoecab/oci-deal-accelerator.git",
            "",
            "MCP Server repo (deploy your own instance):",
            "   github.com/Diegoecab/arch-mcp-oracle",
            "",
            "Skill repo (KB + tools + generators):",
            "   git.tech-lad.com.br/diegoecab/oci-deal-accelerator",
            "",
            "",
            "Skill repo: git.tech-lad.com.br/diegoecab/oci-deal-accelerator    MCP repo: github.com/Diegoecab/arch-mcp-oracle",
        ],
        note="Scan the QR or visit the link above to get started in 30 seconds"
    )

    # ── SLIDE 13: Closing ──
    gen.add_closing_slide(
        name="OCI Deal Accelerator",
        title="git.tech-lad.com.br/diegoecab/oci-deal-accelerator  |  github.com/Diegoecab/arch-mcp-oracle",
    )

    gen.save(output_path)
    print(f"Generated: {output_path}")
    print(f"  Slides: {gen.slide_count}")
    print(f"  Duration: ~10 minutes")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "demo-presentation.pptx"
    build_demo_deck(out)
