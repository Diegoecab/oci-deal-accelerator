# OCI Deal Accelerator

An AI-powered skill that acts as a **force multiplier for OCI Solutions Architects**. Feed it raw discovery notes from a customer call and get back a complete, defensible architecture proposal — ready to present.

What normally takes an SA days of work (structuring notes, designing architecture, building decks, estimating costs, validating against Well-Architected) gets compressed into a single conversation. The skill doesn't just generate documents — it applies field-tested patterns, real pricing data, and lessons learned from actual OCI engagements to produce artifacts you can confidently put in front of a customer.

**Fully aligned with Oracle's ECAL 3.1 framework** — covers all 9 steps (Ideate → Validate → Plan → Current → Future → Confirm → Adopt → Operate → Improve) with a catalog of 60 artefacts, engagement RACIs for 10 roles, and an ECAL Readiness Scorecard to track engagement completeness.

### Key differentiators

- **ECAL 3.1 native** — engagement RACI, artefact catalog, readiness scoring, and lessons learned per step baked into the workflow
- **Field knowledge, beyond the docs** — built-in KB with real gotchas, workarounds, and sizing lessons from production OCI deployments
- **Honest about trade-offs** — flags OCI limitations and competitive gaps instead of overselling
- **Multi-cloud aware** — supports hybrid/multi-cloud diagrams (AWS, Azure, GCP, plus external brand icons such as Slack and Jira) and considers options like ADB Multicloud before recommending full migration
- **MCP-tolerant inputs** — deck, diagram, BOM, and business-case generators accept flat MCP payloads and common field aliases instead of requiring one rigid schema
- **End-to-end coverage** — from discovery notes to go-live checklist, not just the architecture slide

## New user? Start here

The skill runs as a hosted MCP server. Connect once from your LLM client, sign in with Oracle SSO, and the tools are ready.

Fastest path: open AI Factory Hub at `https://ai-lad.com/`, search for `OCI Deal Accelerator`, and install it from there. If you prefer manual setup, use the MCP client instructions below.

**1. Add the MCP server to your client (manual setup):**

| Client | How |
|---|---|
| **Claude Code** | `claude mcp add --transport http oci-deal-accelerator "https://mcp.tech-lad.com/deal-accelerator/mcp/"` |
| **Codex** | `codex mcp add oci-deal-accelerator --url "https://mcp.tech-lad.com/deal-accelerator/mcp/"` |
| **Cursor** | Settings (Ctrl+Shift+J) → MCP → Add new MCP server → Name: `oci-deal-accelerator`, Type: `streamable-http`, URL: `https://mcp.tech-lad.com/deal-accelerator/mcp/` |
| **Claude Desktop** | Add to `claude_desktop_config.json`: `{ "mcpServers": { "oci-deal-accelerator": { "transport": "http", "url": "https://mcp.tech-lad.com/deal-accelerator/mcp/" } } }` |
| **Windsurf** | Settings → Cascade → MCP → Manual config: `{ "oci-deal-accelerator": { "serverUrl": "https://mcp.tech-lad.com/deal-accelerator/sse/" } }` |

**2. Trigger the connection** — type `/mcp` in Claude Code or Codex, or open any tool in Cursor / Claude Desktop / Windsurf. Your browser opens automatically.

**3. Pick one of two options in the browser:**
- **Sign in with Oracle SSO** — for existing users
- **Create a new account** — for new users (see step 4)

**4. New users — create an account** by clicking "Create a new account". This opens an OCI self-registration form (oracle.com emails only). Tips:
- Use your full Oracle email as User ID (e.g. `name@oracle.com`)
- Password must be 12+ chars, with an uppercase letter, a number, and a special character
- Password must NOT contain your name or username

**5. Verify your email**, then return to the browser and click **Sign in with Oracle SSO**.

**6. Done.** The MCP tools are now available in your client.

### Connection URLs

- **AI Factory Hub:** `https://ai-lad.com/`
- **MCP (HTTP streamable):** `https://mcp.tech-lad.com/deal-accelerator/mcp/`
- **SSE (Windsurf only):** `https://mcp.tech-lad.com/deal-accelerator/sse/`

## What It Produces

From unstructured input (meeting notes, emails, Slack threads), the skill generates:

| Artifact | Format | ECAL Phase | ECAL Step |
|---|---|---|---|
| **Customer Profile** — strategic goals, Oracle footprint, industry analysis | YAML | Define | Ideate |
| **Strategy Map** — goals → strategies → capabilities → enablers | YAML | Define | Ideate |
| **Workload Profile** — structured discovery capture | YAML | Define | Ideate |
| **Value Story** — business hypothesis linked to OCI outcomes | YAML | Define | Ideate |
| **Business Case** — TCO, ROI, value drivers, risk assessment | .pptx | Define | Ideate |
| **Joint Engagement Plan** — scope, resources, timeline | YAML | Define | Plan |
| **Discovery Questionnaire** — structured IT landscape collection | YAML | Design | Current |
| **Architecture Diagram** — Oracle reference-architecture geometry, multi-cloud + external brand support | .drawio / .pptx | Design | Future |
| **Slide Deck** — 6-15 slides scaled to engagement complexity | .pptx | Design | Confirm |
| **Customer PDF** — branded, no internal KB references | .pdf | Design | Confirm |
| **Cost Estimate** — BYOL vs PAYG breakdown with assumptions | YAML | Design | Future |
| **Bill of Materials (BOM)** — requested SKUs only, formula-driven totals, discount-aware workbook | .xlsx | Design | Future |
| **AppCA-ready BOM** — AppCA import sheet plus full BOM workbook detail | .xlsx | Design | Future |
| **Well-Architected Scorecard** — 5-pillar automated validation | YAML | Design | Future |
| **Operations Model** — day-2 monitoring, patching, incident response | YAML | Design | Future |
| **ECAL Readiness Scorecard** — 60-artefact gap analysis per phase | Text | All | All |
| **Delivery Artifacts** — handover, go-live checklist, success criteria | YAML | Deliver | Adopt |

## Quick Start

Feed `SKILL.md` as a system prompt to any LLM (Claude, GPT-4o, Gemini Pro). Then give it your discovery notes:

```
Here are my notes from the discovery call with Acme Corp:

- 3 Oracle 19c databases on Exadata X8M on-prem, largest is 4TB OLTP
- Using GoldenGate for replication to reporting DB
- Need 99.95% availability, PCI compliance
- Seasonal peaks 3x normal during Black Friday
- Want to reduce costs, current Oracle licensing is $2M/year
- Team has 2 Oracle DBAs, no cloud experience
- CTO wants to move to cloud in 6 months
- Comparing with AWS
```

The skill follows the ECAL workflow automatically: DEFINE (value story) → DESIGN (architecture) → DELIVER (handover).

## Output Formats

```
deck              ← default (.pptx)
deck + drawio     ← + editable diagram
deck + doc        ← + technical document
deck + xlsx       ← + cost spreadsheet
deck + pdf        ← + customer-facing PDF (branded, no internal refs)
pdf               ← customer PDF only
bizcase           ← business case deck for customer approval
full              ← everything (pptx + drawio + docx + xlsx + pdf)
bom               ← bill of materials (.xlsx)
deliver           ← handover + go-live checklist + success criteria
```

Standalone architecture diagrams can be generated as editable `.drawio` files or as native Oracle-style `.pptx` diagrams/slides, depending on the workflow you trigger.

## Example Prompts

These copy/paste prompts are good demo asks for the newest user-visible features, especially when using Codex or another MCP client.

### Native PowerPoint diagram (.pptx)

```text
Generame un diagrama nativo en .pptx, simple y prolijo, de esta arquitectura: usuarios externos -> load balancer público -> 2 VMs de aplicación en subnet privada -> Autonomous Database Serverless. Quiero que quede presentable para mostrar directo en PowerPoint. No me pidas YAML ni setup adicional.
```

### Brand icons + OIC + dual output

```text
Generate a simple high-level integration diagram for this flow: Slack -> Oracle Integration Cloud (OIC) -> Jira Service Management -> My Oracle Support. Add clear Client, Oracle, and External layers. Use brand icons for Slack and Jira Service Management, and deliver both .drawio and .pptx.
```

### Real multicloud topology

```text
Generate a high-level architecture diagram for this scenario: 1 PostgreSQL in OCI Ashburn, accessed from GCP Virginia through interconnect. PostgreSQL connects internally to 1 Autonomous Database Serverless, which also has 1 refreshable clone in the same region but in a different AD. Deliver both .drawio and .pptx. Keep it simple, executive-friendly, and technically correct.
```

### Discount-aware BOM

```text
Gere um BOM em USD para este cenário: PostgreSQL no OCI com 4 OCPU e 500 GB, ADB-S com 200 ECPU e 1 TB BYOL, 1 refreshable clone com o mesmo sizing e FastConnect de 1 Gbps. Aplique 11% de desconto, 12 meses, 24 horas por dia. Quero o arquivo .xlsx e um resumo claro do custo mensal e anual.
```

## Knowledge Base

The KB is the moat — field experience, not documentation regurgitation.

### Contributing to the KB

Any SA can contribute knowledge to the skill. The KB lives in `kb/` as editable YAML files. Here's where each type of contribution goes:

| What you want to contribute | Where it goes | How |
|---|---|---|
| **Field caveat or workaround** | `kb/field-findings/tracker.yaml` | Menu option 11, or `python tools/findings_cli.py add` |
| **Lesson learned** | `kb/field-knowledge/lessons-learned.yaml` | Edit YAML directly |
| **Undocumented real-world limit** | `kb/field-knowledge/real-world-limits.yaml` | Edit YAML directly |
| **Service caveat** | `kb/field-knowledge/gotchas.yaml` | Edit YAML directly |
| **OCI service info** | `kb/services/<service>.yaml` | Create or edit the service YAML |
| **Architecture pattern** | `kb/patterns/` | Add YAML following existing format |
| **Architecture Center reference** | `kb/architecture-center/catalog.yaml` | `python tools/refresh_arch_catalog.py --url <url>` |
| **Updated pricing** | `kb/pricing/oci-sku-catalog.yaml` (SKUs) or `kb/pricing/compute.yaml` (shapes) | `python tools/refresh_sku_catalog.py --refresh` (SKUs) or `--refresh-domain compute` (shapes). Both auto-pull from the Oracle public pricing API. |
| **Feature compatibility** | `kb/compatibility/adb-feature-matrix.yaml` | Edit the matrix, mark `verified_in_field: true` |
| **Competitive comparison** | `kb/competitive/` | Add or edit YAML with real pros AND cons |

**Fastest path**: if you hit something in an engagement that another SA should know about, use menu option 11 (Report a field finding) — the skill walks you through the format and adds it to the tracker automatically.

### OCI Pricing

All pricing is auto-refreshed from the [Oracle public pricing API](https://apexapps.oracle.com/pls/apex/cetools/api/v1/products/?currencyCode=USD). No manually maintained pricing files.

```
kb/pricing/
├── oci-sku-catalog.yaml    # 200+ SKUs across 20 categories — single source of truth
│                             Refresh: python tools/refresh_sku_catalog.py --refresh
└── compute.yaml            # Shape-level estimation pricing (VMs, BM, GPU)
                              Refresh: python tools/refresh_sku_catalog.py --refresh-domain compute

kb/field-knowledge/pricing-knowledge.yaml
                            # Stable pricing context: billing models, BYOL rules,
                              free tiers, service nuances, hyperscaler comparisons.
                              Non-numeric — no refresh needed.
```

### DBExpert Database Services Catalog

35 Oracle Database services with full capabilities, multicloud availability (Azure/GCP/AWS locations), SLAs, MAA medals, compliance certifications, and certified Oracle applications. Sourced from the [Oracle DBExpert API](https://oracle-dbexpert.github.io/swagger/).

```
kb/services/dbexpert-catalog.yaml        # 35 services, queryable by capability
kb/services/dbexpert-api-reference.yaml  # API endpoints and refresh procedure
```

### Architecture Center Catalog

**123 Oracle Architecture Center reference architectures** (`kb/architecture-center/catalog.yaml`) covering Database@Azure/AWS/Google Cloud, networking, security, AI/ML, migration, HA/DR, and more. Each entry includes title, URL, tags, services, and a 1-line summary; **121 also have a cached `_description.md`** with the full "About this architecture" text fetched from docs.oracle.com.

Cached locally under `kb/diagram/assets/archcenter-refs/<slug>/`:
- `_description.md` — Oracle's architecture rationale (used by both the lookup tool and SKILL.md option 10 "Reference architecture lookup")
- `*.drawio` — official editable source for ~110 references (where Oracle ships a zip)
- `_template.yaml` — extracted `absolute_layout` scaffold so new diagrams can start from Oracle geometry instead of from scratch
- `*.svg` / `*.png` — raster fallback for the rest

During **Phase 2 (DESIGN)**, the skill automatically matches the proposed architecture against the catalog:

- **STRONG MATCH** (≥2 service + ≥1 tag) — cited in the Architecture Decisions slide
- **MODERATE MATCH** (≥1 service + ≥2 tag) — referenced in the technical document

```bash
python tools/refresh_arch_catalog.py --whats-new      # crawl What's New pages
python tools/refresh_arch_catalog.py --url <url>       # add a single entry
python tools/refresh_arch_catalog.py --validate        # validate catalog integrity
python tools/refresh_arch_catalog.py --check-links     # check for broken URLs (404s, redirects)

# Topology lookup — base your diagram on the closest Oracle reference
python tools/archcenter_pattern_lookup.py "mysql heatwave high availability load balancer"
python tools/archcenter_pattern_lookup.py "fastconnect exacs cross region" --top 10

# Re-fetch description text after a catalog refresh
python tools/archcenter_description_fetcher.py --limit 200

# Re-download cached drawio/svg/png assets after a catalog refresh
python tools/archcenter_zip_downloader.py    # idempotent; skips slugs whose folder already has a .drawio
```

The cached assets under `kb/diagram/assets/archcenter-refs/` (~83MB) are committed so the skill works offline. Lookup uses a local index for near-instant matches, and can be rebuilt manually when needed. Refresh quarterly or when `refresh_arch_catalog.py --whats-new` adds entries — both downloader and description fetcher are idempotent and only fetch what's missing.

### KB Health & Freshness

The KB is automatically monitored for staleness and broken links:

| Check | How | When |
|---|---|---|
| **Broken links** | `python tools/refresh_arch_catalog.py --check-links` | Weekly (CI), or on demand |
| **Stale prices** | `python tools/refresh_sku_catalog.py --validate` | Weekly (CI), or on demand |
| **KB freshness** | `python tools/kb_freshness.py --check` | On skill startup (pre-flight) |
| **Diagram spec geometry** | `python tools/diagram_spec_validator.py --spec <spec.yaml>` | Auto, before every drawio/PPTX render |
| **Diagram XML output** | `python tools/drawio_visual_validator.py <file.drawio>` | Auto, after `oci_diagram_gen.py` saves |

**Automated CI/CD:**
- **Deploy workflow** (`.gitea/workflows/deploy.yaml`) — auto-deploys to MCP server on every push to `main`
- **KB health workflow** (`.gitea/workflows/kb-health.yaml`) — runs every Monday 8am UTC, checks all catalog URLs and SKU freshness, reports broken links as artifacts

To run KB health manually:
```bash
# Check all 123 Architecture Center URLs for 404s
python tools/refresh_arch_catalog.py --check-links

# Fix broken links: re-crawl What's New for updated URLs
python tools/refresh_arch_catalog.py --whats-new

# Refresh stale pricing from Oracle API
python tools/refresh_sku_catalog.py --refresh --diff
```

### Feature Compatibility Matrix

Before recommending a deployment type, the skill checks `kb/compatibility/adb-feature-matrix.yaml` — a field-verified matrix of what works, what doesn't, and what has caveats the docs don't mention.

```bash
python tools/feature_matrix_cli.py check "Auto Scaling" adb_s 23ai
python tools/feature_matrix_cli.py compare adb_s exacs 23ai
python tools/feature_matrix_cli.py gaps dbcs_ee 23ai
```

### Field Findings Tracker

Real issues, limitations, and workarounds encountered during customer engagements.

```bash
python tools/findings_cli.py search "maintenance window"
python tools/findings_cli.py add
python tools/findings_cli.py stats
```

### Competitive Positioning

Honest AWS/Azure/GCP comparisons (`kb/competitive/`) that cover genuine advantages AND genuine gaps. No marketing — only field-verified facts.

## ECAL Readiness Score

Option 12 in the menu scores an engagement against the complete ECAL 3.1 framework:

```
══════════════════════════════════════════
📊 ECAL READINESS SCORECARD
══════════════════════════════════════════
Customer: Acme Corp
Current Phase: DESIGN
Overall Readiness: 62% 🟡

── DEFINE ──────────────────── 85% 🟢
✅ Value Story
✅ Workload Profile
🟡 Customer Profile (missing Oracle footprint)
❌ Strategy Map
✅ Joint Engagement Plan

── DESIGN ──────────────────── 55% 🟠
✅ Future State Architecture
✅ Cost Estimate
🟡 Discovery Questionnaire (partial)
❌ Operational RACI
❌ Recovery Model
...

── TOP 5 GAPS ──
1. ❌ Strategy Map — links solution to business goals
2. ❌ Operational RACI — who runs what post go-live
...
══════════════════════════════════════════
```

The scorecard evaluates each of the **60 ECAL artefacts** from `kb/patterns/ecal-artefacts-catalog.yaml`, weighted by phase (DEFINE 25%, DESIGN 50%, DELIVER 25%). Readiness levels: 🟢 80%+ | 🟡 60-79% | 🟠 40-59% | 🔴 <40%.

After scoring, the skill offers to generate missing artefacts, fix the top gap, or export the scorecard as a slide.

## ECAL 3.1 Coverage

The KB includes comprehensive ECAL 3.1 process knowledge:

| KB File | What it covers |
|---|---|
| `kb/patterns/ecal-artefacts-catalog.yaml` | All 60 ECAL artefacts with description, purpose, and skill support level |
| `kb/patterns/engagement-raci.yaml` | RACI matrices for 10 roles across all 9 ECAL steps + lessons learned |
| `kb/patterns/business-drivers.yaml` | 4-pillar framework (Strategic/Financial/BizOps/ITOps) + hypothesis families |
| `kb/patterns/architecture-principles.yaml` | Design, Deployment, and Service principles from ECAL |
| `kb/patterns/operational-raci.yaml` | 3 operational models (fully managed, co-managed, self-managed) |
| `kb/patterns/service-tiering.yaml` | Platinum/Gold/Silver/Bronze service tier definitions |
| `kb/patterns/environment-catalogue.yaml` | Environment templates per tier (prod, pre-prod, dev, DR) |
| `templates/customer-profile.yaml` | Strategic customer profiling (goals, footprint, industry) |
| `templates/strategy-map.yaml` | Goals → Strategies → Capabilities → Enablers mapping |
| `templates/discovery-questionnaire.yaml` | Structured IT landscape collection with prioritization matrix |

## Business Case Builder

Option 8 in the menu generates a business case deck for customer internal approval:

| Slide | Layout | Content |
|-------|--------|---------|
| Cover | Dark - Title_Pillar | Customer name + subtitle |
| Executive Summary | Impact Statement | Bold 1-sentence opportunity |
| Business Drivers | Multi Statement | 3 key drivers: Why now |
| TCO Comparison | Blank + Table | Current/as-is run-rate vs target/to-be run-rate |
| BOM + Operations Breakdown | Blank + Tables | Cloud services, storage/infra, GoldenGate, operations, one-time bridge |
| Forecasted TCO | Blank + Table | 24M/36M annual run-rate snapshots, not cumulative totals |
| TCO Crossover | Native shapes | ADB-S vs ADB-D annual TCO and first cheaper period |
| Business Value Model | Blank + Table | Financial baseline, architecture benefit, risk-adjusted value, KPIs |
| Value Drivers | Blank + Cards | 4 categories: Cost, Risk, Agility, Innovation |
| Risk Assessment | Blank + 2-Column | Migration risks vs Do-nothing risks |
| Roadmap | Blank + Timeline | Implementation phases |
| Recommendation | Dark Impact | Clear ask with next steps |

Uses the **Oracle FY26 official PowerPoint template** with Redwood design system.

For ADB-S to ADB-D cases, the generator keeps workload ECPU demand separate
from ADB-D physical capacity. Dedicated footprint is modeled as fixed DB server
and storage server infrastructure; projected BOMs are annual run-rate snapshots
at the horizon. Risk-reduction value is converted to USD only when the customer
provides business impact per degraded/outage hour.

```bash
python tools/oci_bizcase_gen.py --spec business-case.yaml --output business-case.pptx
```

## Welcome Flow

When you start a conversation without discovery notes, the skill presents an interactive menu:

```
🏗️ OCI Deal Accelerator
━━━━━━━━━━━━━━━━━━━━━━━

Compresses your SA cycle from discovery to proposal — days to hours.
Aligned with Oracle's ECAL framework (Define → Design → Deliver).

What do you want to do?

 DESIGN & PROPOSE
 ─────────────────
 1. 📋 Full proposal — notes → architecture + deck + diagram + costs
 2. 📐 Architecture diagram — YAML or description → .drawio
 3. 📊 Slide deck — architecture → .pptx
 4. 💰 Cost estimate — services + sizing → PAYG vs BYOL

 VALIDATE & CHECK
 ─────────────────
 5. ✅ Well-Architected review — 5-pillar scoring + gaps
 6. 🔍 Feature compatibility — "does ADB-S support X?"
 7. 🆚 Competitive comparison — honest pros & cons vs AWS/Azure/GCP

 STRATEGY & BUSINESS
 ─────────────────
 8. 💼 Business case — TCO, ROI, value drivers → exec deck

 KNOWLEDGE BASE
 ─────────────────
  9. 🔎 Field findings — real issues + workarounds
 10. 📚 Reference architecture — Architecture Center lookup
 11. ➕ Report finding — log a gotcha from your engagement

 ECAL GOVERNANCE
 ─────────────────
 12. 📊 ECAL readiness score — 60-artefact gap analysis

━━━━━━━━━━━━━━━━━━━━━━━
Pick a number, or just describe what you need.
```

If you paste discovery notes directly, the skill skips the menu and goes straight to the full proposal flow.

## Tools

All major generators accept either the canonical nested YAML specs or the flatter MCP payload aliases used by hosted clients.

```bash
# Slide deck generation (technical proposal)
python tools/oci_deck_gen.py --spec examples/proposal-spec.yaml --output proposal.pptx

# Customer-facing PDF (branded, no internal KB refs)
python tools/oci_pdf_gen.py --spec examples/proposal-spec.yaml --output proposal.pdf
python tools/oci_pdf_gen.py --spec examples/proposal-spec.yaml --output proposal.pdf --diagram arch.png

# Business case deck
python tools/oci_bizcase_gen.py --spec business-case.yaml --output business-case.pptx

# Architecture diagram — see docs/skill/output-formats.md
# § "Standard diagram-generation procedure (MANDATORY)" for the full
# workflow: ref-arch lookup → pre-generation review → spec authoring
# → automatic spec validator → render → visual verification.
# Supports OCI fallback aliases for services whose official toolkit icons
# are still missing (for example PostgreSQL/Redis) plus `brand_icon` for
# third-party systems such as Slack and Jira in both drawio and PPTX.
python tools/archcenter_pattern_lookup.py "<topology keywords>"   # 1. find canonical Oracle reference
python tools/oci_diagram_gen.py --spec examples/diagram-spec.yaml --output arch.drawio  # 2. render (validators run automatically)
python tools/oci_pptx_render.py --pptx arch.pptx --output arch.png --width 1600         # 3. rasterize PPTX for visual review

# Pre-render geometry validator (auto-invoked by both renderers; CLI for ad-hoc spec checks)
python tools/diagram_spec_validator.py --spec examples/diagram-spec.yaml --strict

# Post-render XML validator (auto-invoked inside OCIDiagramGenerator.save())
python tools/drawio_visual_validator.py arch.drawio

# Output orchestrator (multiple formats at once)
python tools/oci_output.py --spec examples/proposal-spec.yaml --format full --output-dir output/
python tools/oci_output.py --spec examples/exacs-bom-spec.yaml --format bom --output-dir output/

# BOM / AppCA workbook
python tools/oci_bom_gen.py --spec examples/exacs-bom-spec.yaml --output customer-bom.xlsx
python tools/oci_bom_gen.py --spec examples/exacs-bom-spec.yaml --output customer-appca.xlsx --appca

# Architecture Center catalog
python tools/refresh_arch_catalog.py --validate
python tools/refresh_arch_catalog.py --whats-new
python tools/refresh_arch_catalog.py --check-links
python tools/archcenter_pattern_lookup.py "adb gcp fastconnect" --rebuild-index

# Feature compatibility
python tools/feature_matrix_cli.py check "Auto Scaling" adb_s 23ai
python tools/feature_matrix_cli.py compare adb_s exacs 23ai

# Field findings
python tools/findings_cli.py search "maintenance window"
python tools/findings_cli.py stats

# KB governance
python tools/kb_cli.py health

# WA validation
python scripts/validate-architecture.py \
  --profile examples/sample-workload-profile.yaml \
  --architecture examples/sample-architecture.yaml \
  --output scorecard.yaml

# Build automation
make help
```

## Multi-LLM Support

The skill is LLM-agnostic. The same KB and templates work across platforms:

| Platform | How to use |
|----------|-----------|
| **Claude Code** | Uses `SKILL.md` + `CLAUDE.md` natively |
| **OpenAI Codex** | Uses `AGENTS.md` + `.agents/skills/` (see below) |
| **ChatGPT / GPT-4o** | Paste SKILL.md as system prompt |
| **Gemini Pro** | Paste SKILL.md as system instruction |

### OpenAI Codex Setup

The repo is 100% compatible with [Codex CLI](https://github.com/openai/codex). Codex auto-discovers the skill on startup:

```
├── AGENTS.md                                        # Project instructions (Codex reads automatically)
├── .agents/skills/oci-deal-accelerator/
│   └── SKILL.md                                     # Full skill definition (YAML frontmatter + instructions)
└── codex/
    └── README.md                                    # Detailed setup guide
```

```bash
# Just run Codex from the project root — auto-discovers everything
cd oci-deal-accelerator
codex

# Or load the skill explicitly
codex --skill oci-deal-accelerator
```

For temporary overrides (e.g., focusing on a specific customer), create `AGENTS.override.md` at the project root — it takes highest priority.

Full setup details: [`codex/README.md`](codex/README.md)

#### Keeping the Claude and Codex skills in sync

The root `SKILL.md` (read by Claude Code) and `.agents/skills/oci-deal-accelerator/SKILL.md` (read by Codex) MUST stay byte-aligned modulo an auto-generated banner. If they drift, the two agents give the user different instructions.

Three layers of defense, run from least to most enforcement:

1. **Local pre-commit hook (recommended once per clone):**
   ```bash
   make install-hooks
   ```
   Sets `core.hooksPath = .githooks`. From then on, any commit that touches `SKILL.md` auto-runs `scripts/sync-skill.py` and stages the regenerated `.agents/` copy in the same commit. No manual step required.

2. **Manual sync (anytime):**
   ```bash
   make sync-skill          # write the .agents/ copy from SKILL.md
   make lint                # check (also runs sync --check)
   ```

3. **CI gate (`.gitea/workflows/skill-sync.yaml`):** every push/PR runs `python scripts/sync-skill.py --check` and fails the build if the two files have drifted. Catches anyone who skipped the hook.

**Direction is always root → `.agents/`.** The `.agents/` copy is auto-generated; do NOT edit it directly — the next sync will silently overwrite your changes. Both the local pre-commit hook and the CI gate REJECT a commit/PR that stages `.agents/skills/oci-deal-accelerator/SKILL.md` without a matching root `SKILL.md` change. If you find yourself wanting to tweak the Codex side specifically, that signal belongs in `AGENTS.md` (Codex-only project instructions) — `SKILL.md` content stays unified across both agents.

## Roadmap

### ECAL Completeness (see `docs/ecal-gaps-backlog.md` for full list)
- Integration Catalog template — detailed integration mapping with data flows
- Cloud Operating Framework — 52-week operational plan (9 capability areas)
- OCI Operationalization Framework — 5-milestone deployment methodology
- POD (Pool of Databases) pattern — large-scale DB consolidation
- Banking/Financial compliance pattern — EBA/FCA/PRA mapped to OCI services
- ExaCC managed service pattern — complete ExaCC + ZDLRA/ZFS/OEM/OKV

### Platform
- Interactive what-if cost simulator (adjust ECPU/storage/commitment live)
- Automated migration complexity scoring from discovery notes
- Multi-region DR cost optimizer
- Engagement timeline generator (Gantt-style from Joint Engagement Plan)
- DBExpert API auto-refresh for database service catalog
- KB vectorizada en base de datos (RAG) — almacenar knowledge base en OCI 23ai con embeddings para busqueda semantica en lugar de lookup estatico por YAML

## Requirements

- Python 3.8+
- `pip install pyyaml python-pptx drawpyo requests beautifulsoup4 lxml reportlab`
- No OCI CLI or SDK needed (the skill designs, it doesn't deploy)

## License

Internal use. Not for distribution.
