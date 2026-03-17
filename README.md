# OCI Deal Accelerator

AI skill aligned with Oracle's **ECAL framework** (Define → Design → Deliver) that compresses the OCI SA's cycle from customer discovery to architecture proposal — from days to hours.

## What It Does

Takes unstructured discovery notes and produces a complete OCI architecture package:

- **Workload Profile** — structured from messy notes (YAML)
- **Value Story** — business hypothesis linked to OCI outcomes
- **Business Case** — TCO comparison, ROI analysis, value drivers, risk assessment (.pptx)
- **Architecture Diagram** — `.drawio` with official Oracle visual style
- **Slide Deck** — 6-15 slides scaled to engagement complexity (.pptx)
- **Cost Estimate** — BYOL vs PAYG breakdown with assumptions
- **Well-Architected Scorecard** — 5-pillar automated validation
- **Operations Model** — day-2 monitoring, patching, incident response
- **Delivery Artifacts** — handover, go-live checklist, success criteria

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
bizcase           ← business case deck for customer approval
full              ← everything
deliver           ← handover + go-live checklist + success criteria
```

## Knowledge Base

The KB is the moat — field experience, not documentation regurgitation.

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

 DESIGN & PROPOSE:      1-4 (proposal, diagram, deck, cost)
 VALIDATE & CHECK:      5-7 (WA review, compatibility, competitive)
 STRATEGY & BUSINESS:   8   (business case builder)
 KNOWLEDGE BASE:        9-11 (field findings, ref arch, report finding)
```

If you paste discovery notes directly, the skill skips the menu and goes straight to the full proposal flow.

## Tools

```bash
# Slide deck generation (technical proposal)
python tools/oci_deck_gen.py --spec examples/proposal-spec.yaml --output proposal.pptx

# Business case deck
python tools/oci_bizcase_gen.py --spec business-case.yaml --output business-case.pptx

# Architecture diagram
python tools/oci_diagram_gen.py --spec examples/diagram-spec.yaml --output arch.drawio

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

- Interactive what-if cost simulator (adjust ECPU/storage/commitment live)
- Automated migration complexity scoring from discovery notes
- Customer-facing PDF export (branded, no internal KB references)
- Multi-region DR cost optimizer
- Engagement timeline generator (Gantt-style from Joint Engagement Plan)
- DBExpert API auto-refresh for database service catalog

## Requirements

- Python 3.8+
- `pip install pyyaml python-pptx requests beautifulsoup4 lxml`
- No OCI CLI or SDK needed (the skill designs, it doesn't deploy)

## License

Internal use. Not for distribution.
