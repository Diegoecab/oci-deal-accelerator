# OCI Deal Accelerator

An AI-powered skill that acts as a **force multiplier for OCI Solutions Architects**. Feed it raw discovery notes from a customer call and get back a complete, defensible architecture proposal — ready to present.

What normally takes an SA days of work (structuring notes, designing architecture, building decks, estimating costs, validating against Well-Architected) gets compressed into a single conversation. The skill doesn't just generate documents — it applies field-tested patterns, real pricing data, and lessons learned from actual OCI engagements to produce artifacts you can confidently put in front of a customer.

**Fully aligned with Oracle's ECAL 3.1 framework** — covers all 9 steps (Ideate → Validate → Plan → Current → Future → Confirm → Adopt → Operate → Improve) with a catalog of 60 artefacts, engagement RACIs for 10 roles, and an ECAL Readiness Scorecard to track engagement completeness.

### Key differentiators

- **ECAL 3.1 native** — engagement RACI, artefact catalog, readiness scoring, and lessons learned per step baked into the workflow
- **Field knowledge, not docs regurgitation** — built-in KB with real gotchas, workarounds, and sizing lessons from production OCI deployments
- **Honest about trade-offs** — flags OCI limitations and competitive gaps instead of overselling
- **Multi-cloud aware** — supports hybrid/multi-cloud diagrams (AWS, Azure, GCP icons) and considers options like ADB Multicloud before recommending full migration
- **End-to-end coverage** — from discovery notes to go-live checklist, not just the architecture slide

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
| **Architecture Diagram** — official Oracle visual style, multi-cloud support | .drawio | Design | Future |
| **Slide Deck** — 6-15 slides scaled to engagement complexity | .pptx | Design | Confirm |
| **Customer PDF** — branded, no internal KB references | .pdf | Design | Confirm |
| **Cost Estimate** — BYOL vs PAYG breakdown with assumptions | YAML | Design | Future |
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
deliver           ← handover + go-live checklist + success criteria
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
| **Updated pricing** | `kb/pricing/<category>.yaml` | Edit with data from [OCI Price List](https://www.oracle.com/cloud/price-list/) |
| **Feature compatibility** | `kb/compatibility/adb-feature-matrix.yaml` | Edit the matrix, mark `verified_in_field: true` |
| **Competitive comparison** | `kb/competitive/` | Add or edit YAML with real pros AND cons |

**Fastest path**: if you hit something in an engagement that another SA should know about, use menu option 11 (Report a field finding) — the skill walks you through the format and adds it to the tracker automatically.

### OCI Pricing (13 categories)

Comprehensive pricing from the [OCI Price List](https://www.oracle.com/cloud/price-list/) covering compute, database, storage, networking, AI/ML, containers, integration, observability, developer, analytics, hybrid/VMware, and security services. Source date: 2025-09-11.

```
kb/pricing/
├── compute.yaml            # VMs, bare metal, GPU (B200/B300/H200/H100/A100/L40S)
├── database.yaml           # ADB (ECPU), DBCS, ExaCS, MySQL, PostgreSQL, NoSQL, Redis
├── storage.yaml            # Block, object, file, data transfer
├── networking.yaml         # LB, NLB, FastConnect, DNS, egress
├── ai-ml.yaml              # GenAI, Data Science, Vision, Speech, Digital Assistant
├── containers-serverless.yaml  # OKE, Functions, Container Instances
├── integration.yaml        # OIC, API Mgmt, Streaming, Queue, GoldenGate
├── observability.yaml      # Monitoring, Logging, APM, DR, Email
├── developer.yaml          # APEX, Visual Builder, DevOps, Blockchain
├── analytics.yaml          # OAC, Essbase, Big Data, Data Flow
├── hybrid-vmware.yaml      # OCVS, Compute C@C, Managed Mac, Roving Edge
├── security.yaml           # Access Governance, Vault, Cloud Guard
└── pricing-models.yaml     # PAYG, UCM, Reserved, BYOL
```

### DBExpert Database Services Catalog

35 Oracle Database services with full capabilities, multicloud availability (Azure/GCP/AWS locations), SLAs, MAA medals, compliance certifications, and certified Oracle applications. Sourced from the [Oracle DBExpert API](https://oracle-dbexpert.github.io/swagger/).

```
kb/services/dbexpert-catalog.yaml        # 35 services, queryable by capability
kb/services/dbexpert-api-reference.yaml  # API endpoints and refresh procedure
```

### Architecture Center Catalog

**123 Oracle Architecture Center reference architectures** (`kb/architecture-center/catalog.yaml`) covering Database@Azure/AWS/Google Cloud, networking, security, AI/ML, migration, HA/DR, and more.

During **Phase 2 (DESIGN)**, the skill automatically matches the proposed architecture against the catalog:

- **STRONG MATCH** (≥2 service + ≥1 tag) — cited in the Architecture Decisions slide
- **MODERATE MATCH** (≥1 service + ≥2 tag) — referenced in the technical document

```bash
python tools/refresh_arch_catalog.py --whats-new      # crawl What's New pages
python tools/refresh_arch_catalog.py --url <url>       # add a single entry
python tools/refresh_arch_catalog.py --validate        # validate catalog integrity
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
| TCO Comparison | Blank + Table | Current vs OCI (3-5 year) |
| ROI Headline | Blank + Metric | Big number (e.g., "2080% ROI") |
| Value Drivers | Blank + Cards | 4 categories: Cost, Risk, Agility, Innovation |
| Risk Assessment | Blank + 2-Column | Migration risks vs Do-nothing risks |
| Roadmap | Blank + Timeline | Implementation phases |
| Recommendation | Dark Impact | Clear ask with next steps |

Uses the **Oracle FY26 official PowerPoint template** with Redwood design system.

```bash
python tools/oci_bizcase_gen.py --spec business-case.yaml --output business-case.pptx
```

## Welcome Flow

When you start a conversation without discovery notes, the skill presents an interactive menu:

```
🏗️ OCI Deal Accelerator
━━━━━━━━━━━━━━━━━━━━━━━

 DESIGN & PROPOSE:      1-4  (proposal, diagram, deck, cost)
 VALIDATE & CHECK:      5-7  (WA review, compatibility, competitive)
 STRATEGY & BUSINESS:   8    (business case builder)
 KNOWLEDGE BASE:        9-11 (field findings, ref arch, report finding)
 ECAL GOVERNANCE:       12   (ECAL readiness score)
```

If you paste discovery notes directly, the skill skips the menu and goes straight to the full proposal flow.

## Tools

```bash
# Slide deck generation (technical proposal)
python tools/oci_deck_gen.py --spec examples/proposal-spec.yaml --output proposal.pptx

# Customer-facing PDF (branded, no internal KB refs)
python tools/oci_pdf_gen.py --spec examples/proposal-spec.yaml --output proposal.pdf
python tools/oci_pdf_gen.py --spec examples/proposal-spec.yaml --output proposal.pdf --diagram arch.png

# Business case deck
python tools/oci_bizcase_gen.py --spec business-case.yaml --output business-case.pptx

# Architecture diagram
python tools/oci_diagram_gen.py --spec examples/diagram-spec.yaml --output arch.drawio

# Output orchestrator (multiple formats at once)
python tools/oci_output.py --spec examples/proposal-spec.yaml --format full --output-dir output/

# Architecture Center catalog
python tools/refresh_arch_catalog.py --validate
python tools/refresh_arch_catalog.py --whats-new

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

The skill is LLM-agnostic. The same `SKILL.md` and KB work with:

| Platform | How to use |
|----------|-----------|
| **Claude Code** | Load SKILL.md as system prompt, tools run natively |
| **OpenAI Codex** | Use `codex/` packaging with `skill.json` manifest |
| **ChatGPT / GPT-4o** | Paste SKILL.md as system prompt |
| **Gemini Pro** | Paste SKILL.md as system instruction |

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
