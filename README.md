# OCI Deal Accelerator

AI skill aligned with Oracle's **ECAL framework** (Define → Design → Deliver) that compresses the OCI SA's cycle from customer discovery to architecture proposal — from days to hours.

## What It Does

Takes unstructured discovery notes and produces a complete OCI architecture package:

- **Workload Profile** — structured from messy notes (YAML)
- **Value Story** — business hypothesis linked to OCI outcomes
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
full              ← everything
deliver           ← handover + go-live checklist + success criteria
```

## Architecture Center Catalog

The skill includes a curated catalog of **123 Oracle Architecture Center reference architectures** (`kb/architecture-center/catalog.yaml`) covering Database@Azure/AWS/Google Cloud, networking, security, AI/ML, migration, HA/DR, and more.

During **Phase 2 (DESIGN)**, the skill automatically matches the proposed architecture against the catalog:

- **STRONG MATCH** (≥2 service + ≥1 tag) — cited in the Architecture Decisions slide
- **MODERATE MATCH** (≥1 service + ≥2 tag) — referenced in the technical document

This adds credibility: *"Your architecture aligns with Oracle Reference Architecture: Deploy Oracle Database@Azure — [link]"*.

### Refresh the catalog

```bash
python tools/refresh_arch_catalog.py --whats-new      # crawl What's New pages
python tools/refresh_arch_catalog.py --url <url>       # add a single entry
python tools/refresh_arch_catalog.py --validate        # validate catalog integrity
```

Recommended cadence: monthly, or after major Oracle releases.

## Field Intelligence

Internal knowledge base built from real customer engagements. Two systems work together:

### Feature Compatibility Matrix

Before recommending a deployment type, the skill checks `kb/compatibility/adb-feature-matrix.yaml` — a field-verified matrix of what works, what doesn't, and what has caveats the docs don't mention.

```bash
# Quick check
python tools/feature_matrix_cli.py check "Auto Scaling" adb_s 23ai
# → GA_CAVEAT: Activation takes 2-3 min. Size base for P75.

# Compare deployment options side-by-side
python tools/feature_matrix_cli.py compare adb_s exacs 23ai

# Find deal-breakers for a deployment type
python tools/feature_matrix_cli.py gaps dbcs_ee 23ai

# Export for Confluence/wiki
python tools/feature_matrix_cli.py export --format markdown
```

Status values: `GA` · `GA_CAVEAT` · `LIMITED` · `NOT_AVAIL` · `BROKEN` · `UNTESTED`

Every cell has a confidence level (`validated` / `observed` / `reported` / `inferred`) and the name of who verified it.

### Field Findings Tracker

Real issues, limitations, and workarounds encountered during customer engagements (`kb/field-findings/tracker.yaml`). Each finding has: date, who reported it, client, severity, workaround, Oracle SR# if filed, and status.

```bash
# Search for known issues
python tools/findings_cli.py search "maintenance window"

# Add a finding (interactive)
python tools/findings_cli.py add

# Add a finding (one-liner)
python tools/findings_cli.py add \
    --name "Your Name" \
    --team "Field Architecture" \
    --client "Client Name" \
    --product "ADB-S" \
    --severity HIGH \
    --category limitation \
    --summary "Description of what you found" \
    --tags "adb-s,dep,gotcha"

# Another architect validates a finding
python tools/findings_cli.py confirm FF-202603-008 \
    --name "María García" \
    --team "Database Specialists" \
    --note "Confirmed same behavior on ADB-D with 80M vectors"

# Post-engagement review (3 questions, auto-generates findings)
python tools/findings_cli.py aer

# Stats
python tools/findings_cli.py stats
```

The skill uses findings automatically: referenced in ADRs, risk registers, and WA scorecards by finding ID.

### How It Works in Practice

1. Architect hits a wall with a client → adds a finding in 30 seconds
2. Another architect 3 months later searches the KB → finds the workaround instantly
3. Oracle fixes the issue → finding updated to `resolved`
4. Skill checks findings during composition → flags known risks automatically

Example finding:
```
FF-202603-008 [HIGH] — Distributed HNSW indexes not available at 100M+ scale
  Product: ADB-S 23ai
  Reported by: Diego Cabrera (Field Architecture)
  Client: Vector Search Customer
  Workaround: Hash-partition vector table + LOCAL HNSW index.
              Validated at 120M vectors, 64 ECPU, P95 = 38ms.
  Status: acknowledged
```

## Competitive Positioning

The skill includes honest AWS/Azure/GCP comparisons (`kb/competitive/aws-mapping.yaml`, `azure-mapping.yaml`, `common-objections.yaml`) that cover **genuine advantages AND genuine gaps**. No marketing — only field-verified facts.

When a competitive situation is identified in the workload profile, the skill produces a balanced comparison in the deck and technical document.

## KB Governance

Every contribution to the KB requires attribution:

```yaml
contributor:
  name: "Diego Cabrera"        # Required
  team: "Field Architecture"   # Required
  client: "Acme Corp"          # Optional
  date: "2026-03-14"           # Required
  confidence: "validated"       # validated / observed / reported / inferred
```

Domain owners, freshness tracking (180-day warning), confidence decay, and standardized tags ensure the KB stays accurate over time.

```bash
# KB health dashboard
python tools/kb_cli.py health

# Who's contributing
python tools/kb_cli.py stats contributors

# What's stale
python tools/kb_cli.py stats stale
```

## Example Output

Feed the skill your discovery notes and specify an output format:

```
> Here are my notes from the Acme Corp discovery call: [notes]
> Output: deck + drawio
```

**Phase 1 — DEFINE:**
```
Parsed workload profile: 3 databases, 6 app servers, MQ Series messaging.
Gaps detected:
  - Missing P95 CPU → assuming 85% based on 70% avg
  - PCI scope unclear → assuming OLTP DB + app tier
```

**Phase 2 — DESIGN:**
```
Target: ADB-S Serverless with cross-region HA/DR

  ADB-S OLTP         8 OCPU (auto-scale 16) / 4 TB / BYOL
  ADB-S DR Standby   Cross-region ADG (async, RPO ≈ seconds)
  Compute            2x VM.Standard.E5.Flex 4 OCPU
  Networking         VCN + FastConnect 10 Gbps (redundant)

Feature matrix check: ✓ All required features GA on ADB-S 23ai
  ⚠ TAC replay: audit app code for UTL_HTTP/DBMS_PIPE calls

Field findings check:
  ⚠ FF-202603-004: DEP provisioning takes days-weeks

Reference architecture match:
  ✅ "Deploy secure ADB and APEX application" (STRONG)
  ✅ "Migrate on-premises Oracle Database to ADB" (MODERATE)

Cost: $13,560/mo PAYG → $8,410/mo BYOL (vs $2M/year current = 95% savings)

WA Scorecard: Security ✅ | Reliability ⚠️ | Performance ✅ | Ops ❌ | Distributed ➖
```

**Phase 3 — DELIVER:**
```
Generated:
  📊 acme-corp-proposal.pptx (12 slides)
  📐 acme-corp-architecture.drawio
```

## Multi-LLM Support

The skill is LLM-agnostic. The same `SKILL.md` and KB work with:

| Platform | How to use |
|----------|-----------|
| **Claude Code** | Load SKILL.md as system prompt, tools run natively |
| **OpenAI Codex** | Use `codex/` packaging with `skill.json` manifest |
| **ChatGPT / GPT-4o** | Paste SKILL.md as system prompt |
| **Gemini Pro** | Paste SKILL.md as system instruction |

## Tools

```bash
# Slide deck generation
python tools/oci_deck_gen.py --spec examples/proposal-spec.yaml --output proposal.pptx

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
python scripts/validate-architecture.py --profile examples/sample-workload-profile.yaml --architecture examples/sample-architecture.yaml --output scorecard.yaml

# Build automation
make help
```

## Requirements

- Python 3.8+
- `pip install pyyaml python-pptx requests beautifulsoup4`
- No OCI CLI or SDK needed (the skill designs, it doesn't deploy)

## License

Internal use. Not for distribution.
