# ======================================================================
# OCI DEAL ACCELERATOR — COMPLETE PROJECT BUILD PROMPT
# ======================================================================
#
# SINGLE SOURCE OF TRUTH for building the entire project.
# Feed this to Claude Code, Codex, or any AI coding agent.
# It generates ~60 files: foundation, KB, tools, tests, CI.
#
# ======================================================================


---

## ░░░ SECTION 0: GIT RULES ░░░

# FIX GIT BRANCH STRUCTURE — Claude Code Prompt

## Problem

This repo has orphan branches created by Claude Code with no common ancestor. 
GitHub shows "entirely different commit histories" when comparing them. 
We need to establish a proper `main` branch and make all future work branch from it.

## Step 1: Inspect Current State

Run these commands and show me the output:

```bash
cd /path/to/oci-deal-accelerator

# List all branches
git branch -a

# Show each branch's file count and last commit
for branch in $(git branch -r --format='%(refname:short)'); do
  echo "=== $branch ==="
  git log "$branch" --oneline -3
  echo "Files: $(git ls-tree -r "$branch" --name-only | wc -l)"
  echo ""
done

# Check if main exists
git branch -a | grep -E '(main|master)'
```

Show me the output so we can decide which branch has the best content.

## Step 2: Establish `main` (run AFTER reviewing Step 1 output)

Based on what we see, pick the branch with the most complete content 
(likely the one with ~43 files / 4,128 lines). Then:

```bash
# Option A: If NO main/master exists yet
# Replace BEST_BRANCH with the branch name from Step 1 that has the most content
git checkout BEST_BRANCH
git checkout -b main
git push -u origin main

# Set main as default branch on GitHub:
# Go to GitHub repo → Settings → General → Default branch → change to main

# Option B: If main exists but is empty/minimal
git checkout main
git merge BEST_BRANCH --allow-unrelated-histories -m "merge: establish main from best Claude Code branch"
git push origin main
```

## Step 3: Merge Other Branches Into Main

If other branches have content that main doesn't:

```bash
# For each other branch that has unique content:
git checkout main
git merge origin/OTHER_BRANCH --allow-unrelated-histories -m "merge: incorporate content from OTHER_BRANCH"

# Resolve any conflicts (prefer main's version for structure, other branch for content)
# Then:
git push origin main
```

## Step 4: Clean Up Orphan Branches

```bash
# Delete the orphan branches (remote)
git push origin --delete claude/oci-deal-accelerator-TXB47
git push origin --delete claude/oci-deal-accelerator-nhPQL
# Delete any other orphan branches shown in Step 1

# Delete local tracking branches
git branch -D claude/oci-deal-accelerator-TXB47
git branch -D claude/oci-deal-accelerator-nhPQL

# Verify
git branch -a
```

## Step 5: Verify

```bash
# Should show only main (and any feature branches from main)
git branch -a

# Verify main has the complete project structure
git ls-tree -r main --name-only | head -50

# Verify the key files exist
for f in SKILL.md README.md kb/diagram/oci-toolkit-styles.yaml; do
  if git show main:$f > /dev/null 2>&1; then
    echo "✓ $f exists"
  else
    echo "✗ $f MISSING"
  fi
done
```

## Step 6: Set Branch Protection

On GitHub (manual — can't do via CLI without admin token):
1. Settings → Branches → Add branch protection rule
2. Branch name pattern: `main`
3. Enable: "Require a pull request before merging"
4. This prevents Claude Code from pushing directly to main

## IMPORTANT: Rule for All Future Claude Code Tasks

From now on, EVERY Claude Code task MUST start with:

```bash
# ALWAYS run this before creating any files:
git checkout main
git pull origin main
git checkout -b feature/DESCRIPTIVE-NAME

# ... do the work ...

git add .
git commit -m "feat: description of what was built"
git push -u origin feature/DESCRIPTIVE-NAME
# Then create PR to main
```

NEVER create an orphan branch. NEVER push directly to main.
ALWAYS branch from main. ALWAYS create a PR.


---

## ░░░ SECTION 1: FOUNDATION — SKILL.md content ░░░

### Create file `SKILL.md` with this EXACT content:

```
# OCI Deal Accelerator

You are the **OCI Deal Accelerator**, an AI skill that helps Oracle/OCI Solutions Architects compress the cycle from customer discovery to architecture proposal from days to hours.

You take unstructured discovery notes from a customer meeting and produce a complete, costed, defensible OCI architecture — with diagrams, decision records, cost estimates, risk register, and a Well-Architected scorecard.

---

## Your Principles

1. **Empirical over theoretical.** Every recommendation must be justifiable with real metrics, benchmarks, or field experience — never "best practice because Oracle says so."
2. **Simplicity first.** Start with the simplest architecture that meets requirements. Complexity must be earned by evidence of need.
3. **Honest about limitations.** Acknowledge what OCI cannot do, where competitors have an edge, and where there are gotchas. Architect credibility depends on honesty.
4. **Composable, not monolithic.** Architectures are assembled from pattern blocks that combine, not from monolithic reference architecture templates.

---

## Your Workflow

You operate in three phases. You may run all three in sequence or be asked to start at any phase.

### Phase 1: Discovery Capture → Workload Profile

**Input:** Unstructured notes — messy, incomplete, mixed languages, abbreviations, half-sentences. This is how architects actually capture information.

**Your job:** Parse and structure into a **Workload Profile** (YAML). Identify gaps and state reasonable defaults. Tell the architect: "I have enough to start, but I'm missing X, Y, Z. I'll assume [defaults] — correct me if wrong."

The Workload Profile covers:
- **Current state**: databases (engine, version, size, features, HA), compute, middleware, messaging, storage, networking, identity, compliance, NoSQL/other data stores, integration
- **Requirements**: RTO/RPO, SLA target, performance (P95 latency, TPS, concurrent users), scalability (growth, peak multiplier), migration (downtime tolerance, timeline)
- **Decision drivers**: primary motivation, budget sensitivity, licensing (BYOL/ULA), team skills, political constraints

Refer to `kb/` files for service details, sizing ratios, and pattern applicability.

### Phase 2: Architecture Composition

Given the Workload Profile, compose a complete architecture:

1. **Select services** across the full OCI catalog — not just database, but compute, networking, security, observability, messaging, integration, AI/ML, migration tooling, governance.

2. **Dimension each service** using sizing rules from `kb/sizing/`. For Oracle databases, use AWR/CloudWatch metrics if available. Apply conversion ratios (vCPU→OCPU by processor family). For ADB-S, size base OCPUs for P75 (not P50) because auto-scaling activation takes 2-3 minutes.

3. **Compose the topology** from pattern blocks in `kb/patterns/`. Apply composition rules:
   - Check for conflicts between patterns
   - Add implied dependencies (ADB-S → Service Gateway for backup; FastConnect → DRG)
   - Apply compliance overlays (PCI, HIPAA, SOC2) if required

4. **Estimate costs** with explicit assumptions. Compare BYOL vs. License Included. Compare reserved vs. PAYG for stable workloads. Break down monthly by component.

5. **Validate against the Well-Architected Framework** — run the architecture through the 5 pillars (Security, Reliability, Performance/Cost, Operational Efficiency, Distributed Cloud) using checklists from `kb/well-architected/`. Flag gaps automatically. Do NOT ask the architect 50 questions — infer answers from the composed architecture.

### Phase 3: Output Generation

Produce these deliverables:

1. **Architecture Summary** — one page, executive-readable
2. **Architecture Decision Records (ADRs)** — for each significant choice: what, why, alternatives rejected
3. **Architecture Diagram** — generate a `.drawio` file using the diagram generator (see Diagram Generation section below)
4. **Cost Estimate** — line-item breakdown with assumptions
5. **Risk Register** — technical, migration, operational risks
6. **Well-Architected Scorecard** — 5-pillar validation with gaps and recommendations
7. **Competitive Positioning** (if competitor identified) — genuine advantages and honest gaps
8. **Migration High-Level Plan** — phases, dependencies, estimated effort

---

## Service Categorization

When discussing or diagramming services, use these categories for color coding and grouping:

| Category | Color | Services |
|----------|-------|----------|
| **Infrastructure** | Teal `#2D5967` | Compute (VM, BM, Flex, Burstable), OKE, Functions, Load Balancer, Gateways (IGW, NAT, SGW), WAF, Bastion, API Gateway, Vault, Data Safe, Cloud Guard, Object/Block/File Storage, Monitoring, Logging, DB Management, Ops Insights, Notifications, Events |
| **Database** | Copper `#AA643B` | ADB-S, ADB-D, DBCS, ExaCS, Exadata, MySQL, PostgreSQL, NoSQL, OpenSearch, OCI Cache (Redis), GoldenGate |
| **Integration** | Purple `#804998` | DRG, Streaming (Kafka), OCI Queue, Oracle Integration Cloud (OIC), FastConnect, Service Connector Hub |
| **Dormant** | Light gray `#DFDCD8` | Standby/inactive resources (DR app tier, pre-provisioned but not running) |
| **Legacy** | Medium gray `#70665E` | Non-OCI systems (MQ Series, legacy middleware, 3rd party) |

---

## Diagram Generation

When asked to generate a diagram, produce a `.drawio` XML file using the **OCI official container styles** from the OCI Style Guide for Draw.io Toolkit v24.2.

### Container Style Rules (MANDATORY)

| Container | Border | Fill | Text Color | Key Attributes |
|-----------|--------|------|------------|----------------|
| **Tenancy** | Dashed `#9E9892` | None | `#312D2A` | `strokeWidth=1;dashed=1` |
| **Region** | Solid `#9E9892` | `#F5F4F2` | `#312D2A` | `rounded=1;arcSize=10` — ONLY container with fill |
| **VCN** | Dashed `#AE562C` | None | `#AE562C` | `strokeWidth=2;dashed=1` — SIGNATURE ORACLE VISUAL |
| **Subnet** | Dashed `#AE562C` | `#FCFBFA` | `#AE562C` | `strokeWidth=1;dashed=1` — thinner than VCN |
| **Compartment** | Dashed `#9E9892` | None | `#312D2A` | Same as Tenancy |

### Service Block Style
All service blocks: `rounded=1;strokeColor=none;fontColor=#FFFFFF;fontSize=8;fontFamily=Oracle Sans;arcSize=8;` — vary only the `fillColor` per category.

### Connection Styles
- **Standard**: solid `#706E6F` gray
- **Database flow**: solid `#AA643B` copper, strokeWidth=1.5
- **Data Guard/Replication**: dashed `#AE562C` burnt orange, strokeWidth=2
- **FastConnect**: solid `#804998` purple, bidirectional arrows, strokeWidth=2
- **Migration**: dashed `#706E6F` gray, strokeWidth=1.5
- **ETL/event-driven**: dashed `#804998` purple

### Typography
- Font: `Oracle Sans` (fallback: Segoe UI, Helvetica Neue, Arial)
- Text is NEVER pure black — always `#312D2A`
- Container labels: 11-12px
- Service labels: 8-9px white on colored background
- Title: 10px italic `#70665E`

### Python Generator

Use the `tools/oci_diagram_gen.py` module to generate `.drawio` files programmatically. It accepts either:
- **Programmatic API**: `gen.add_region(...)`, `gen.add_vcn(...)`, `gen.add_service(...)`, `gen.save("output.drawio")`
- **YAML spec**: `gen = OCIDiagramGenerator.from_spec(yaml_dict)` — declarative, generated from the architecture composition

The generator produces valid `.drawio` XML with correct nesting (`parent` attributes), proper container hierarchy, and official styles. Service blocks are colored placeholders. For full OCI stencil icons, the architect loads `OCI Library.xml` and drags icons onto placeholders.

---

## Knowledge Base Structure

```
kb/
├── services/               # One YAML per OCI service — what, when to use, when NOT, gotchas, limits
├── patterns/                # Composable architecture blocks with pre/post conditions, conflicts
│   ├── database-ha/
│   ├── database-dr/
│   ├── compute-scaling/
│   ├── networking-hub-spoke/
│   ├── security-baseline/
│   ├── compliance-pci/
│   └── ...
├── sizing/                  # CPU conversion ratios, storage IOPS, ADB scaling behavior
├── pricing/                 # Simplified pricing models for estimation
├── competitive/             # Service-to-service mapping vs AWS/Azure/GCP with real differences
├── well-architected/        # 5-pillar validation checklists
│   ├── security-compliance.yaml
│   ├── reliability-resilience.yaml
│   ├── performance-cost.yaml
│   ├── operational-efficiency.yaml
│   └── distributed-cloud.yaml
├── diagram/                 # Diagram styles, color palette, reference layouts
│   ├── oci-toolkit-styles.yaml
│   └── reference-layouts/
└── field-knowledge/         # Gotchas, real-world limits, lessons learned
```

---

## Interaction Style

- The architect may communicate in **Spanish** but all deliverables are in **English**.
- Be direct and technical. No marketing language.
- When you don't know something, say so. Don't fabricate.
- When a simpler architecture would work, recommend it. Don't over-engineer.
- Present trade-offs explicitly. Let the architect decide.
- When generating outputs, produce the **minimum needed** — don't pad with supplementary docs unless asked.

---

## What You Do NOT Do

- You do NOT execute infrastructure changes. You design and recommend.
- You do NOT replace the architect's judgment. You accelerate it.
- You do NOT generate pixel-perfect diagrams. You generate 80% drafts the architect refines.
- You do NOT make up pricing. If you don't have current pricing, say so and estimate ranges.
- You do NOT claim features exist if you're unsure. Check the KB first.

```


---

## ░░░ SECTION 1b: FOUNDATION — README.md content ░░░

### Create file `README.md` with this EXACT content:

```
# OCI Deal Accelerator

An AI skill that compresses the OCI Solutions Architect's cycle from customer discovery to architecture proposal — from days to hours.

## What It Does

Takes unstructured discovery notes from a customer meeting and produces:

1. **Structured Workload Profile** — parsed from messy notes into a clean YAML
2. **Composed Architecture** — services selected, dimensioned, and validated
3. **Architecture Diagram** — `.drawio` file with official Oracle visual style
4. **Cost Estimate** — line-item breakdown with explicit assumptions
5. **Architecture Decision Records** — every choice documented with rationale
6. **Risk Register** — technical, migration, and operational risks
7. **Well-Architected Scorecard** — automated validation against Oracle's 5-pillar framework
8. **Competitive Positioning** — honest comparison vs. AWS/Azure/GCP when relevant

## Quick Start

### As an AI Skill

Feed the `SKILL.md` as a system prompt to any LLM (Claude, GPT-4o, Gemini Pro). Then give it your discovery notes:

```
Here are my notes from the discovery call with Acme Corp:

- 3 Oracle 19c databases on Exadata X8M on-prem, largest is 4TB OLTP
- Using GoldenGate for replication to reporting DB
- Need 99.95% availability, PCI compliance
- Seasonal peaks 3x normal during Black Friday
- Want to reduce costs, current Oracle licensing is $2M/year
- BYOL with 8 processor licenses
- Team has 2 Oracle DBAs, no cloud experience
- CTO wants to move to cloud in 6 months
- Comparing with AWS
```

The skill responds with:

```
PHASE 1: DISCOVERY CAPTURE
══════════════════════════

Parsed workload profile from your notes. 3 databases, 6 app servers, 
MQ Series messaging.

Gaps detected:
  - Missing P95 CPU for main OLTP DB → assuming 85% based on 70% avg
  - Missing IOPS metrics → will estimate from Exadata X8M baseline
  - PCI scope unclear → assuming OLTP DB + app tier (not reporting DB)

Correct me if wrong, or say "continue" to proceed.
```

```
> continue
```

```
PHASE 2: ARCHITECTURE COMPOSITION
══════════════════════════════════

Target Architecture: ADB-S Serverless with cross-region HA/DR

┌─ Primary: US East (Ashburn) ─────────────────────────────────┐
│                                                               │
│  ADB-S OLTP        8 OCPU (auto-scale 16) / 4 TB / BYOL     │
│  ADB-S DW          4 OCPU / 2 TB (replaces GoldenGate)       │
│  ADB-S APEX        2 OCPU / 200 GB                           │
│  Compute           2x VM.Standard.E5.Flex 4 OCPU / 64 GB     │
│  OKE               3 workers for future microservices         │
│  Networking         VCN + public/private subnets + DRG        │
│  Security           WAF, Bastion, Data Safe, Vault, NSGs      │
│  Connectivity       FastConnect 10 Gbps (redundant)           │
│                                                               │
└───────────────────────────────────────────────────────────────┘
         │
         │ Autonomous Data Guard (async, RPO ≈ seconds)
         ▼
┌─ DR: US West (Phoenix) ──────────────────────────────────────┐
│  ADB-S Standby     8 OCPU / 4 TB (auto-failover)            │
│  Refreshable Clone 4 OCPU / 4 TB (reporting offload)        │
│  App Tier           Dormant (Terraform on-demand)            │
└───────────────────────────────────────────────────────────────┘

Feature matrix check: ✓ All required features GA on ADB-S 23ai
  ⚠ TAC replay: audit app code for UTL_HTTP/DBMS_PIPE calls

Field findings check: 
  ⚠ FF-202603-004: DEP provisioning takes days-weeks. Not using DEP 
    for this architecture, but noting for future Elastic Pool consideration.

KEY DECISIONS:
  1. ADB-S over ExaCS → variable workload + no DBA team + auto-scaling
  2. Cross-region ADG → PCI requires geo-redundant DR
  3. FastConnect over VPN → low latency during hybrid migration period
  4. Replace GoldenGate replication with ADB-S DW + Refreshable Clone
     → simpler architecture, eliminates GoldenGate licensing

COST ESTIMATE:
  Component                         Monthly (PAYG)   Monthly (BYOL)
  ─────────────────────────────────────────────────────────────────
  ADB-S OLTP (8 OCPU, 4 TB)        $3,200           $1,600
  ADB-S DW (4 OCPU, 2 TB)          $1,600           $800
  ADB-S APEX (2 OCPU, 200 GB)      $700             $350
  ADB-S DR Standby (ADG)           $3,200           $1,600
  ADB-S DR Clone (Refreshable)     $1,600           $800
  Compute (2x E5.Flex 4 OCPU)      $440             $440
  OKE (3 workers 8 OCPU)           $1,320           $1,320
  FastConnect 10 Gbps               $600             $600
  Storage, Monitoring, Other        $900             $900
  ─────────────────────────────────────────────────────────────────
  TOTAL MONTHLY                     $13,560          $8,410
  TOTAL ANNUAL                      $162,720         $100,920

  vs. Current licensing: $2M/year → savings of $1.84M (PAYG) or $1.9M (BYOL)
  Assumptions: 730 hrs/mo, BYOL 8 proc licenses, auto-scaling ~4 hrs/day

WELL-ARCHITECTED SCORECARD:
  Security & Compliance       ✅ PASS              18/20
  Reliability & Resilience    ⚠️ RECOMMENDATIONS   12/15
  Performance & Cost          ✅ PASS              10/10
  Operational Efficiency      ❌ GAPS               6/10
  Distributed Cloud           ➖ N/A

  Top gaps:
    [OPS-DEPLOY-01] No IaC strategy → Define Terraform modules
    [OPS-MON-03] No APM configured → Enable OCI APM
    [REL-DR-03] No DR drill schedule → Quarterly automated DR drill

MIGRATION APPROACH:
  Phase 1: Assessment & Prep          weeks 1-4
  Phase 2: Infrastructure Setup       weeks 3-6
  Phase 3: Migration (DMS + ZDM)      weeks 5-10
  Phase 4: Cutover & Validation       weeks 9-12
  Downtime: Zero (ZDM with GoldenGate during transition)
```

```
> deck + drawio
```

```
PHASE 3: OUTPUT GENERATION
══════════════════════════

Generated:
  📊 acme-corp-architecture-proposal.pptx (12 slides)
  📐 acme-corp-architecture.drawio

Slide deck contents:
  Slide 1:  Title — Acme Corp Architecture Proposal
  Slide 2:  Engagement summary + current state
  Slide 3:  Architecture diagram (full page)
  Slide 4:  Key decisions table (4 ADRs)
  Slide 5:  HA/DR design + RTO/RPO table
  Slide 6:  Security & PCI compliance mapping
  Slide 7:  Cost estimate (PAYG vs BYOL)
  Slide 8:  Cost comparison vs current $2M/year
  Slide 9:  Migration timeline (4 phases)
  Slide 10: Risk register (top 5)
  Slide 11: Well-Architected scorecard
  Slide 12: Next steps with target dates

Ready to present. Load the .drawio in draw.io to refine the diagram 
or drag official OCI icons onto the service placeholders.
```

### Diagram Generator (Python)

```bash
# From YAML spec
python tools/oci_diagram_gen.py --spec examples/migration-adb-ha-dr.yaml --output architecture.drawio

# Open in draw.io — no library import needed
# Optionally load OCI Library.xml for official service icons
```

```python
# Programmatic
from tools.oci_diagram_gen import OCIDiagramGenerator

gen = OCIDiagramGenerator()
gen.add_tenancy("tenancy", "Oracle Cloud Infrastructure")
gen.add_region("r1", "Region — US East (Ashburn)", "tenancy")
gen.add_vcn("vcn1", "VCN prod-vcn 10.0.0.0/16", "r1")
gen.add_subnet("sub-db", "Private Subnet — Data Tier", "vcn1", 665, 30, 425, 450)
gen.add_service("adb1", "ADB-S OLTP\n8 OCPU / 2 TB", "adb", "sub-db", 25, 35, 375, 85)
gen.add_connection("c1", "Data Guard", "adg", "sub-db", "sub-dr-db")
gen.save("architecture.drawio")
```

## Project Structure

```
deal-accelerator/
├── SKILL.md                    # LLM system prompt (the skill itself)
├── README.md                   # This file
│
├── kb/                         # Knowledge Base — the skill's brain
│   ├── services/               # One YAML per OCI service
│   │   ├── adb-serverless.yaml
│   │   ├── adb-dedicated.yaml
│   │   ├── oke.yaml
│   │   ├── oci-queue.yaml
│   │   └── ...
│   ├── patterns/               # Composable architecture blocks
│   │   ├── database-ha/
│   │   ├── database-dr/
│   │   ├── compute-scaling/
│   │   ├── networking-hub-spoke/
│   │   ├── security-baseline/
│   │   ├── compliance-pci/
│   │   └── ...
│   ├── sizing/                 # Conversion ratios, benchmarks, scaling rules
│   │   ├── cpu-conversion-ratios.yaml
│   │   ├── storage-performance.yaml
│   │   ├── adb-scaling-behavior.yaml
│   │   └── memory-sizing-rules.yaml
│   ├── pricing/                # Simplified pricing for estimation
│   │   ├── compute.yaml
│   │   ├── database.yaml
│   │   ├── storage.yaml
│   │   └── pricing-models.yaml    # PAYG vs reserved vs BYOL logic
│   ├── competitive/            # Service mapping vs other clouds
│   │   ├── aws-mapping.yaml
│   │   ├── azure-mapping.yaml
│   │   └── common-objections.yaml
│   ├── well-architected/       # Oracle WA Framework checklists
│   │   ├── security-compliance.yaml
│   │   ├── reliability-resilience.yaml
│   │   ├── performance-cost.yaml
│   │   ├── operational-efficiency.yaml
│   │   └── distributed-cloud.yaml
│   ├── diagram/                # Diagram generation styles and layouts
│   │   ├── oci-toolkit-styles.yaml
│   │   └── reference-layouts/
│   └── field-knowledge/        # Real-world gotchas and lessons learned
│       ├── gotchas.yaml
│       ├── real-world-limits.yaml
│       └── lessons-learned.yaml
│
├── tools/                      # Python tooling
│   └── oci_diagram_gen.py      # .drawio diagram generator
│
├── config/                     # Configuration
│   └── service-categories.yaml # Service → color/category mapping
│
└── examples/                   # Example specs and outputs
    ├── migration-adb-ha-dr.yaml
    └── sample-output/
```

## How the Knowledge Base Works

The KB is consumed by both the LLM (via SKILL.md references) and the Python tools. Every KB file uses YAML with a `last_verified` date in its frontmatter for freshness tracking.

```yaml
# kb/services/adb-serverless.yaml
---
last_verified: 2026-03-14
service: Autonomous Database Serverless (ADB-S)
category: database
oci_color: "#AA643B"
---

what: Fully managed Oracle Database with auto-scaling, auto-patching, auto-tuning.

when_to_use:
  - OLTP or mixed workloads under 128 OCPUs
  - Teams without dedicated DBAs
  - Variable/unpredictable workload patterns (auto-scaling)
  - Rapid provisioning needed (minutes, not days)

when_NOT_to_use:
  - Workloads requiring OS-level access
  - Need for RAC (use ExaCS or ADB-D)
  - Regulatory requirement for dedicated infrastructure
  - Sustained >128 OCPU usage (ADB-D or ExaCS cheaper)

gotchas:
  - Auto-scaling activation takes 2-3 minutes — size base OCPUs for P75 not P50
  - TAC replay not guaranteed with non-replayable operations (UTL_HTTP, DBMS_PIPE, NOCACHE sequences)
  - Auto Indexing creates indexes HIDDEN by default — instantly reversible
  - Cross-region ADG is async only — RPO is seconds, not zero

sizing_rules:
  ocpu_base: "P75 of current CPU utilization, converted via cpu-conversion-ratios.yaml"
  ocpu_max: "P95 or 2x base, whichever is higher"
  storage: "Current data size + 30% growth headroom + index overhead"

pricing_model:
  base: "per OCPU per hour (PAYG) or per month (monthly flex)"
  storage: "per TB per month"
  byol_discount: "~50% reduction on OCPU cost"
  auto_scaling: "billed only when active, per OCPU per hour"
```

## Diagram Visual Style

Diagrams match Oracle's official **OCI Style Guide for Draw.io Toolkit v24.2**:

- **VCN/Subnet borders**: dashed burnt orange `#AE562C` (the signature Oracle visual)
- **Region containers**: solid fill `#F5F4F2`, rounded corners
- **Service blocks**: teal (infra), copper (database), purple (integration)
- **Text**: charcoal `#312D2A`, never pure black
- **Font**: Oracle Sans

Source: https://docs.oracle.com/en-us/iaas/Content/General/Reference/graphicsfordiagrams.htm

## Well-Architected Validation

Every architecture is automatically validated against Oracle's 5-pillar framework:

| Pillar | Key Checks |
|--------|------------|
| **Security & Compliance** | IAM least-privilege, MFA, private subnets, TDE+Vault, Data Safe, NSGs, Cloud Guard |
| **Reliability & Resilience** | Auto-scaling, redundant FastConnect, ADG, backups, DR drills |
| **Performance & Cost** | Right-sized shapes, BYOL analysis, reserved capacity, budget alerts |
| **Operational Efficiency** | IaC (Terraform), CI/CD, monitoring alarms, patching, runbooks |
| **Distributed Cloud** | Multi-region, data residency, sovereign cloud (when applicable) |

Source: https://docs.oracle.com/en/solutions/oci-best-practices/index.html

## Build Plan

### Iteration 1 — Database Deal Accelerator (Current)
- Scope: Oracle database workloads (on-prem Oracle, ExaCS, AWS RDS Oracle)
- Services: ADB-S, ADB-S Elastic Pool, DEP, ADB Dedicated, DBCS, ExaCS
- Patterns: database HA, database DR, basic networking
- Outputs: Architecture summary, ADRs, cost estimate, diagram, WA scorecard

### Iteration 2 — Full Stack
- Add: Compute (VM, OKE, Functions), storage, networking patterns, security patterns
- Add: Messaging (Queue, Streaming), NoSQL, integration (API Gateway, OIC)
- Add: Compliance overlays (PCI, HIPAA, SOC2)

### Iteration 3 — Competitive & Output Polish
- Add: Competitive mapping (AWS, Azure, GCP)
- Add: Slide deck / docx output generation
- Add: Migration plan generation
- Add: Objection handler

## Design Philosophy

- **LLM-agnostic**: Tested with Claude, GPT-4o, Gemini Pro. No LLM-specific features.
- **KB is the moat**: The knowledge base encodes field experience, not documentation. Anyone can read OCI docs — the value is knowing what the docs don't tell you.
- **80% draft, not 100% final**: The skill produces drafts the architect refines. Trying for perfection is an infinite rabbit hole.
- **Empirical over theoretical**: Recommendations cite real metrics, not marketing benchmarks.

## Requirements

- Python 3.8+ (for diagram generator)
- PyYAML (`pip install pyyaml`)
- No OCI CLI or SDK needed (the skill designs, it doesn't deploy)

## License

Internal use. Not for distribution.

```


---

## ░░░ SECTION 1c: FOUNDATION — OCI Toolkit Styles ░░░

### Create file `oci-toolkit-styles-official.yaml` with this EXACT content:

```
# OCI Official Diagram Styles — Extracted from OCI Style Guide for Draw.io Toolkit v24.2
# Source: OCI Library.xml + OCI Architecture Diagram Toolkit v24.2.drawio
# This supersedes earlier palette files based on inference from reference architectures.

# ============================================================
# CONTAINER STYLES (from Physical Groupings in the toolkit)
# These are the EXACT styles Oracle uses for diagram containers.
# ============================================================

containers:

  tenancy:
    # Toolkit item [200]: Physical - Grouping - Tenancy
    style: "whiteSpace=wrap;html=1;strokeWidth=1;dashed=1;align=left;fontFamily=Oracle Sans;verticalAlign=top;fillColor=none;fontColor=#312D2A;strokeColor=#9E9892;fontSize=12;spacingLeft=5;"
    notes:
      - "DASHED gray border, NO fill"
      - "Text color is charcoal #312D2A"
      - "Border is warm gray #9E9892"

  region:
    # Toolkit item [202]: Physical - Grouping - OCI Region
    style: "whiteSpace=wrap;html=1;align=center;fontFamily=Oracle Sans;verticalAlign=top;fillColor=#F5F4F2;rounded=1;arcSize=10;strokeColor=#9E9892;fontColor=#312D2A;fontSize=12;"
    notes:
      - "SOLID border, rounded corners"
      - "FILLED with warm gray #F5F4F2"
      - "This is the only container with a solid background fill"

  availability_domain:
    # From template styles
    style: "whiteSpace=wrap;html=1;strokeWidth=1;align=center;fontFamily=Oracle Sans;verticalAlign=top;fillColor=#DFDCD8;fontColor=#312D2A;strokeColor=#9E9892;rounded=1;arcSize=1;fontStyle=1;"
    notes:
      - "Slightly darker gray fill #DFDCD8"
      - "Bold text (fontStyle=1)"

  vcn:
    # Toolkit item [197]: Physical - Grouping - VCN
    style: "whiteSpace=wrap;html=1;strokeWidth=2;dashed=1;align=left;fontFamily=Oracle Sans;verticalAlign=top;fillColor=none;fontColor=#AE562C;strokeColor=#AE562C;perimeterSpacing=0;fontSize=12;spacingLeft=5;"
    notes:
      - "DASHED BURNT ORANGE border — this is the signature OCI VCN visual"
      - "strokeWidth=2 (thicker than subnet)"
      - "Text AND border are both #AE562C (burnt orange)"
      - "NO fill — transparent background"

  subnet:
    # Toolkit item [198]: Physical - Grouping - Subnet
    style: "whiteSpace=wrap;html=1;strokeWidth=1;dashed=1;align=left;fontFamily=Oracle Sans;verticalAlign=top;fillColor=none;fontColor=#AE562C;perimeterSpacing=0;strokeColor=#AE562C;fontSize=12;spacingLeft=5;"
    notes:
      - "DASHED BURNT ORANGE border — same color as VCN but THINNER (strokeWidth=1)"
      - "Inside templates, subnet interior uses fillColor=#FCFBFA (near-white)"
      - "Text is #AE562C (burnt orange)"

  compartment:
    # Toolkit item [199]: Physical - Grouping - Compartment
    style: "whiteSpace=wrap;html=1;strokeWidth=1;dashed=1;align=left;fontFamily=Oracle Sans;verticalAlign=top;fillColor=none;fontColor=#312D2A;strokeColor=#9E9892;fontSize=12;spacingLeft=5;"
    notes:
      - "Same as tenancy style — dashed gray"

  fault_domain:
    # Toolkit item [204]
    style: "whiteSpace=wrap;html=1;strokeWidth=1;dashed=1;align=left;fontFamily=Oracle Sans;verticalAlign=top;fillColor=none;fontColor=#312D2A;strokeColor=#9E9892;fontSize=12;spacingLeft=5;"

  tier:
    # Toolkit item [201]
    style: "whiteSpace=wrap;html=1;strokeWidth=1;dashed=1;align=left;fontFamily=Oracle Sans;verticalAlign=top;fillColor=none;fontColor=#312D2A;strokeColor=#9E9892;fontSize=12;spacingLeft=5;"

# ============================================================
# SERVICE ICON COLORS
# ============================================================

service_colors:
  oci_teal: "#2D5967"
  oracle_copper: "#AA643B"
  oracle_purple: "#804998"
  burnt_orange: "#AE562C"  # Used ONLY for VCN/Subnet borders and text — NOT for service icons
  oracle_red: "#C74634"     # Accent only

# ============================================================
# BACKGROUND AND TEXT COLORS
# ============================================================

backgrounds:
  region_fill: "#F5F4F2"      # Warm gray — region containers
  ad_fill: "#DFDCD8"          # Slightly darker — AD containers
  subnet_fill: "#FCFBFA"      # Near-white — subnet interiors in templates
  dormant: "#DFDCD8"          # Dormant/inactive elements

text:
  primary: "#312D2A"           # Charcoal — ALL text (never pure black)
  secondary: "#70665E"         # Medium gray — step circles, muted text
  on_dark: "#FFFFFF"           # White — text on colored service blocks

borders:
  container: "#9E9892"         # Warm gray — tenancy, region, compartment borders
  vcn_subnet: "#AE562C"       # Burnt orange — VCN and subnet borders ONLY
  connector: "#706E6F"        # Gray — standard connection arrows

# ============================================================
# CONNECTOR STYLES (from toolkit)
# ============================================================

connectors:
  standard:
    # Toolkit item [206]: Physical - Connector
    color: "#706E6F"
    strokeWidth: 1
    dashed: false

  fastconnect:
    # Toolkit items [209-210]: Physical - Special Connectors - FastConnect
    color: "#804998"
    strokeWidth: 2
    dashed: false
    notes: "Special icon with zigzag/lightning pattern"

  site_to_site_vpn:
    # Toolkit items [211-212]
    notes: "Dashed line with lock icon"

  remote_peering:
    # Toolkit items [213-214]
    notes: "Dashed line for inter-region connectivity"

# ============================================================
# TYPOGRAPHY
# ============================================================

typography:
  font_family: "Oracle Sans"
  fallback_fonts: "Segoe UI, Helvetica Neue, Arial, sans-serif"
  container_labels: "fontSize=12, fontColor=#312D2A"
  service_labels: "fontSize=8-9, fontColor=#FFFFFF (on colored background)"
  title_text: "fontSize=10, fontColor=#70665E, fontStyle=2 (italic)"

# ============================================================
# KEY VISUAL RULES (from toolkit analysis)
# ============================================================

design_rules:
  - "VCN and Subnet borders are ALWAYS dashed burnt orange (#AE562C) — this is the signature Oracle visual"
  - "VCN border is strokeWidth=2, Subnet border is strokeWidth=1"
  - "Region containers are the ONLY ones with solid background fill (#F5F4F2)"
  - "Tenancy and Compartment containers are dashed gray, NO fill"
  - "Service blocks use solid fills with NO stroke (strokeColor=none)"
  - "Text is NEVER pure black — always charcoal #312D2A"
  - "Font is Oracle Sans (falls back to Segoe UI)"
  - "Icons are composite multi-layer Visio stencils in the OCI Library.xml"
  - "Standard connectors use #706E6F gray"
  - "Data replication arrows use #AE562C burnt orange dashed"
  - "FastConnect arrows use #804998 purple"
  - "Oracle DB-related services use copper #AA643B"
  - "Integration/messaging services use purple #804998"
  - "All other OCI services use teal #2D5967"

# ============================================================
# FULL ICON CATALOG (224 icons in OCI Library.xml)
# ============================================================
# See separate file for the full icon list.
# Key icons for Deal Accelerator:
#   37: Database - Autonomous DB
#   18: Networking - Load Balancer
#   32: Networking - Internet Gateway
#   33: Networking - NAT Gateway
#   31: Networking - Service Gateway
#   30: Networking - Dynamic Routing Gateway DRG
#   102: Identity and Security - WAF
#   105: Identity and Security - Vault
#   106: Identity and Security - Bastion
#   45: Database - Data Safe
#   46: Database - NoSQL
#   74: Developer Services - Container Engine for Kubernetes
#   2: Compute - Functions
#   3: Compute - Virtual Machine VM
#   65: Analytics and AI - Streaming
#   127: Observability and Management - Queuing
#   79: Developer Services - API Gateway
#   120: Observability and Management - Monitoring
#   123: Observability and Management - Logging Analytics

```


---

## ░░░ SECTION 2: PROJECT BOOTSTRAP — KB, tools, examples, Codex ░░░

# OCI DEAL ACCELERATOR — Project Bootstrap Prompt

## CRITICAL: Git Branching Rule

Before creating ANY files, run:

```bash
git checkout main
git pull origin main
git checkout -b feature/phase1-bootstrap
```

NEVER create an orphan branch. NEVER push directly to main. 
ALWAYS branch from `main`. ALWAYS create a PR when done.

When finished building all files:

```bash
git add .
git commit -m "feat: Phase 1 bootstrap — KB, tools, Codex packaging, examples"
git push -u origin feature/phase1-bootstrap
```

Then create a PR to `main`.

---

## Context

You are building the **OCI Deal Accelerator**, an AI skill for Oracle/OCI Solutions Architects. The project structure, SKILL.md (system prompt), and README.md already exist. Your job is to build all the missing files that make it functional.

The project helps architects go from customer discovery notes to a complete architecture proposal (diagram, cost estimate, ADRs, risk register, Well-Architected scorecard) in hours instead of days.

## Existing Files (DO NOT recreate — these are done)

```
deal-accelerator/
├── SKILL.md                              # LLM system prompt — DONE
├── README.md                             # Project docs — DONE
├── kb/diagram/oci-toolkit-styles.yaml    # Official OCI diagram styles — DONE
├── kb/well-architected/README.md         # WA Framework narrative — DONE
├── tools/README.md                       # Diagram generator spec — DONE
```

## Target Project Structure (what you're building toward)

```
deal-accelerator/
├── SKILL.md
├── README.md
├── requirements.txt
├── Makefile
│
├── tools/
│   ├── README.md                         # (exists)
│   ├── oci_diagram_gen.py                # .drawio generator
│   ├── oci_deck_gen.py                   # .pptx generator
│   └── oci_output.py                     # Output orchestrator
│
├── config/
│   ├── workload-profile-schema.yaml
│   └── service-categories.yaml
│
├── kb/
│   ├── services/
│   │   ├── adb-serverless.yaml
│   │   ├── exadata-cloud.yaml
│   │   └── oci-networking-core.yaml
│   ├── patterns/
│   │   ├── database-ha-adb-s.yaml
│   │   ├── database-dr-cross-region.yaml
│   │   └── networking-basic.yaml
│   ├── sizing/
│   │   └── cpu-conversion-ratios.yaml
│   ├── pricing/
│   │   └── database.yaml
│   ├── competitive/
│   │   └── aws-mapping.yaml
│   ├── well-architected/
│   │   ├── README.md                     # (exists)
│   │   ├── security-compliance.yaml
│   │   ├── reliability-resilience.yaml
│   │   ├── performance-cost.yaml
│   │   ├── operational-efficiency.yaml
│   │   └── distributed-cloud.yaml
│   ├── diagram/
│   │   └── oci-toolkit-styles.yaml       # (exists)
│   └── field-knowledge/
│       └── gotchas.yaml
│
├── examples/
│   ├── sample-discovery-notes.md
│   ├── sample-workload-profile.yaml
│   ├── migration-adb-ha-dr.yaml
│   └── sample-output/
│
└── codex/                                # Codex skill packaging
    ├── SKILL.md                          # Codex-adapted instructions
    ├── skill.json                        # Codex manifest
    └── README.md
```

## What You Need to Build

Build these files in order. Each file should be complete and usable, not a skeleton.

---

### 1. `tools/oci_diagram_gen.py`

The Python diagram generator. Must be a working, executable script.

**Requirements:**
- Class `OCIDiagramGenerator` with methods: `add_tenancy()`, `add_region()`, `add_ad()`, `add_vcn()`, `add_subnet()`, `add_onprem()`, `add_service()`, `add_obs_bar()`, `add_connection()`, `add_title()`, `save()`, `to_xml()`
- Class method `from_spec(yaml_dict)` that builds a diagram from a YAML specification
- CLI: `python oci_diagram_gen.py --spec architecture.yaml --output diagram.drawio`
- All styles use the **exact OCI toolkit styles** (listed below)
- Service blocks are colored rectangles (teal `#2D5967` for infra, copper `#AA643B` for database, purple `#804998` for integration, `#DFDCD8` for dormant, `#70665E` for legacy)
- Auto-layout: services stack vertically inside their subnet with padding; subnets arrange horizontally inside VCN; gateways go at bottom of VCN
- Output is valid `.drawio` XML that opens in draw.io without any library imports

**Container styles (verbatim from OCI Toolkit v24.2 — use exactly as-is):**

```python
STYLES = {
    "tenancy": "whiteSpace=wrap;html=1;strokeWidth=1;dashed=1;align=left;fontFamily=Oracle Sans;verticalAlign=top;fillColor=none;fontColor=#312D2A;strokeColor=#9E9892;fontSize=12;spacingLeft=5;spacingTop=5;",

    "region": "whiteSpace=wrap;html=1;align=center;fontFamily=Oracle Sans;verticalAlign=top;fillColor=#F5F4F2;rounded=1;arcSize=10;strokeColor=#9E9892;fontColor=#312D2A;fontSize=12;spacingTop=5;",

    "ad": "whiteSpace=wrap;html=1;strokeWidth=1;align=center;fontFamily=Oracle Sans;verticalAlign=top;fillColor=#DFDCD8;fontColor=#312D2A;strokeColor=#9E9892;rounded=1;arcSize=1;fontStyle=1;",

    "vcn": "whiteSpace=wrap;html=1;strokeWidth=2;dashed=1;align=left;fontFamily=Oracle Sans;verticalAlign=top;fillColor=none;fontColor=#AE562C;strokeColor=#AE562C;perimeterSpacing=0;fontSize=12;spacingLeft=5;spacingTop=5;",

    "subnet": "whiteSpace=wrap;html=1;strokeWidth=1;dashed=1;align=left;fontFamily=Oracle Sans;verticalAlign=top;fillColor=#FCFBFA;fontColor=#AE562C;strokeColor=#AE562C;fontSize=11;spacingLeft=5;spacingTop=5;rounded=1;arcSize=3;",

    "compartment": "whiteSpace=wrap;html=1;strokeWidth=1;dashed=1;align=left;fontFamily=Oracle Sans;verticalAlign=top;fillColor=none;fontColor=#312D2A;strokeColor=#9E9892;fontSize=12;spacingLeft=5;",
}
```

**Connection styles:**
- `conn_standard`: strokeColor=#706e6f, strokeWidth=1
- `conn_db`: strokeColor=#aa643b, strokeWidth=1.5
- `conn_adg`: strokeColor=#AE562C, strokeWidth=2, dashed=1, dashPattern=10 6
- `conn_fastconnect`: strokeColor=#804998, strokeWidth=2, bidirectional (startArrow+endArrow)
- `conn_migration`: strokeColor=#706e6f, strokeWidth=1.5, dashed=1, dashPattern=12 6
- `conn_etl`: strokeColor=#804998, strokeWidth=1, dashed=1

**Service category mapping:**
- **Teal `#2D5967`**: compute, vm, load_balancer, igw, natgw, sgw, waf, bastion, functions, oke, apigw, monitoring, logging, db_management, ops_insights, notifications, events, cloud_guard, data_safe, vault, object_storage, block_storage, file_storage
- **Copper `#AA643B`**: adb, adb_s, adb_d, autonomous_db, dbcs, db_system, exadata, exacs, nosql, mysql, postgresql, opensearch, cache, redis, goldengate
- **Purple `#804998`**: drg, streaming, kafka, queue, oci_queue, oic, integration_cloud, fastconnect, service_connector_hub
- **Dormant `#DFDCD8`**: dormant
- **Legacy `#70665E`**: legacy

---

### 2. `config/workload-profile-schema.yaml`

The full Workload Profile schema — every field the skill captures from discovery, with types, descriptions, and sensible defaults.

**Sections:**
- `engagement`: customer_name, industry, decision_timeline, competitive_situation
- `current_state.databases[]`: name, engine, version, size_gb, type (OLTP/OLAP/mixed), current_platform, ha_current, replication, connections_peak, cpu_metrics (avg/p95/vcpus), storage_metrics (iops_avg/peak/throughput), notable_features[] (partitioning, TDE, VPD, advanced security, label security, spatial, graph, text, APEX, DBMS_SCHEDULER, db links, UTL_FILE, UTL_HTTP, external tables, directory objects, edition-based redefinition, flashback, blockchain tables)
- `current_state.compute[]`: name, purpose, os, vcpus, memory_gb, current_platform, scaling_pattern
- `current_state.middleware[]`: name, type (WebLogic/Tomcat/WildFly/IIS/Node.js), clustering
- `current_state.messaging_and_eventing[]`: name, type (Kafka/RabbitMQ/SQS/MQ Series/Oracle AQ), throughput_msgs_sec, pattern (pub-sub/point-to-point/streaming/event-driven)
- `current_state.storage[]`: name, type (NFS/block/object/archive), size_tb, access_pattern
- `current_state.networking`: connectivity (internet/VPN/dedicated), bandwidth_gbps, latency_requirement_ms, regions_needed[], on_prem_integration
- `current_state.identity_and_security`: idp (AD/Okta/SAML/OCI IAM), compliance[] (PCI-DSS/HIPAA/SOC2/GDPR/FedRAMP/ISO27001), encryption_requirements, vpd_rls, data_masking, audit_requirements
- `current_state.nosql_and_other_data[]`: name, type (MongoDB/DynamoDB/Cassandra/Redis/Elasticsearch), size_gb, access_pattern
- `current_state.integration[]`: name, type (API Gateway/ESB/ETL/CDC/file transfer/iPaaS), tool
- `requirements`: availability (rto_hours, rpo_hours, sla_target), performance (response_time_p95_ms, throughput_tps, concurrent_users), scalability (growth_annual_pct, peak_multiplier, scaling_speed), migration (downtime_tolerance, migration_timeline, parallel_run_needed)
- `decision_drivers`: primary (cost reduction/modernization/performance/compliance/end of hardware EOL/contract expiry/consolidation), budget_sensitivity, licensing (BYOL/new licenses/ULA/want to reduce Oracle footprint), team_skills, political constraints

Each field has: `type`, `description`, `default` (if applicable), `required` (true/false).

---

### 3. `config/service-categories.yaml`

The service→category→color mapping as a standalone config file. Same data as the Python dict but consumable by both the LLM and the tooling.

---

### 4. `kb/services/adb-serverless.yaml`

Complete service file for ADB Serverless. Format:

```yaml
---
last_verified: 2026-03-14
service: Autonomous Database Serverless (ADB-S)
category: database
oci_color: "#AA643B"
---

what: <one sentence>

when_to_use:
  - <condition>

when_NOT_to_use:
  - <condition>

limits:
  max_ocpu: 128
  max_storage_tb: 383
  max_connections: "function of OCPU count"
  # etc — document real limits, not marketing

features:
  auto_scaling: { available: true, notes: "Activation takes 2-3 min. Size base for P75." }
  auto_indexing: { available: true, notes: "Indexes created HIDDEN. Instantly reversible. DML costing in 23ai prevents over-indexing." }
  tac: { available: true, notes: "Replay not guaranteed with UTL_HTTP, DBMS_PIPE, NOCACHE sequences." }
  adg: { available: true, notes: "Local (sync), Cross-region (async, RPO ≈ seconds)." }
  refreshable_clone: { available: true, notes: "Read-only copy, configurable lag." }
  select_ai: { available: true, notes: "Natural language SQL via LLM." }
  apex: { available: true }
  private_endpoint: { available: true, notes: "Recommended for production." }
  # etc

gotchas:
  - "Auto-scaling activation takes 2-3 minutes — size base OCPUs for P75 not P50"
  - "TAC replay not guaranteed with non-replayable side effects"
  - "Cross-region ADG is async only — RPO is seconds, not zero"
  - "Auto Indexing creates indexes HIDDEN by default — instantly reversible"
  - "DEP provisioning takes days to weeks depending on capacity"
  - "Billing starts only at AVAILABLE state"

sizing_rules:
  ocpu_base: "P75 of current CPU, converted via cpu-conversion-ratios"
  ocpu_max: "P95 or 2x base, whichever is higher"
  storage: "Current data + 30% headroom + index overhead"

pricing_model:
  base_payg: "per OCPU per hour"
  base_monthly: "per OCPU per month (monthly flex)"
  storage: "per TB per month"
  byol_discount: "~50% on OCPU cost"
  auto_scaling: "billed per OCPU per hour when active"
  adg: "standby OCPU cost at same rate"

ha_dr_options:
  - { name: "TAC (Transparent Application Continuity)", rto: "0 perceived (DB ~2 min)", rpo: "0", notes: "Requires replayable operations" }
  - { name: "Local ADG", rto: "~2 min auto-failover", rpo: "0 (sync)", notes: "Same region" }
  - { name: "Cross-region ADG", rto: "minutes (manual or auto)", rpo: "seconds (async)", notes: "Different region" }
  - { name: "Refreshable Clone", rto: "N/A (read-only)", rpo: "configurable lag", notes: "For read offloading, not failover" }

competitive_notes:
  vs_aws_rds: "ADB-S is fully autonomous (no patching, no tuning). RDS requires manual maintenance. ADB auto-indexing and auto-scaling have no RDS equivalent."
  vs_aws_aurora: "Aurora is MySQL/PostgreSQL, not Oracle. Not comparable for Oracle workloads."
  vs_azure_sql: "Azure SQL Managed Instance is closer, but no equivalent to TAC or Auto Indexing."
```

---

### 5. `kb/services/exadata-cloud.yaml`

Same format as above but for ExaCS / Exadata Database Service. Include:
- When ExaCS over ADB-S (RAC needed, OS access, sustained >128 OCPU, regulatory)
- Quarter-rack/half-rack/full-rack sizing
- Gotchas: maintenance windows, scaling granularity, X8M vs X9M differences
- Competitive: vs AWS RDS Custom, vs Azure Oracle VM

---

### 6. `kb/services/oci-networking-core.yaml`

Bundle file covering VCN, subnets, gateways (IGW, NAT, SGW, DRG), Load Balancer, WAF, NSGs. Architecture-relevant details, not a doc rehash. Focus on:
- When hub-spoke vs flat VCN
- DRG vs LPG decision
- NSGs vs Security Lists (NSGs always preferred)
- FastConnect vs VPN decision criteria
- Gotchas: CIDR planning, routing asymmetry, cross-region peering limits

---

### 7. `kb/sizing/cpu-conversion-ratios.yaml`

```yaml
---
last_verified: 2026-03-14
---

# vCPU to OCPU conversion ratios
# An OCPU = 1 physical core with 2 hardware threads (= 2 vCPUs on most platforms)

ratios:
  # Source platform → OCPU multiplier
  aws_ec2:
    m5_intel: { vcpu_per_ocpu: 2, notes: "1 OCPU ≈ 2 m5 vCPUs" }
    m6i_intel: { vcpu_per_ocpu: 2 }
    m6g_graviton: { vcpu_per_ocpu: 2, notes: "ARM workloads — test performance parity" }
    r5_intel: { vcpu_per_ocpu: 2, notes: "Memory-optimized — check memory separately" }

  azure:
    d_series_v5: { vcpu_per_ocpu: 2 }
    e_series_v5: { vcpu_per_ocpu: 2, notes: "Memory-optimized" }

  on_prem_intel:
    xeon_skylake: { vcpu_per_ocpu: 2, notes: "Hyperthreaded cores" }
    xeon_cascade_lake: { vcpu_per_ocpu: 2 }
    xeon_ice_lake: { vcpu_per_ocpu: 2 }

  on_prem_exadata:
    x8m: { cores_per_ocpu: 1, notes: "Direct 1:1 mapping for enabled cores" }
    x9m: { cores_per_ocpu: 1 }

  oci_shapes:
    e4_flex_amd: { vcpu_per_ocpu: 1, notes: "OCI OCPU = 1 AMD core = 2 threads but counted as 1 OCPU" }
    e5_flex_amd: { vcpu_per_ocpu: 1 }
    a1_flex_arm: { vcpu_per_ocpu: 1, notes: "Ampere ARM — best price/performance for compatible workloads" }
    standard3_intel: { vcpu_per_ocpu: 1 }

sizing_methodology:
  1_gather: "Get P95 CPU utilization and vCPU count from source (AWR, CloudWatch, Azure Monitor)"
  2_calculate: "effective_load = source_vcpus × (p95_cpu_pct / 100)"
  3_convert: "target_ocpus = effective_load / vcpu_per_ocpu"
  4_headroom: "final_ocpus = target_ocpus × 1.3 (30% headroom)"
  5_adb_adjust: "For ADB-S: set base = P75 load (auto-scaling covers P75→P95+)"

example:
  source: "AWS m5.4xlarge (16 vCPUs), P95 CPU = 73%"
  effective_load: "16 × 0.73 = 11.68 vCPUs"
  target_ocpus: "11.68 / 2 = 5.84 OCPUs"
  with_headroom: "5.84 × 1.3 = 7.6 → round to 8 OCPUs"
  adb_recommendation: "Base: 6 OCPUs (P75), auto-scale max: 16 OCPUs"
```

---

### 8. `kb/patterns/database-ha-adb-s.yaml`

```yaml
---
last_verified: 2026-03-14
pattern:
  id: ha-adb-serverless
  name: "High Availability for ADB-S"
  category: database-ha
---

description: "TAC + Local ADG for ADB-S providing near-zero perceived downtime for the application."

services_used:
  - ADB-S (primary)
  - ADB-S (local standby via Autonomous Data Guard)
  - TAC (Transparent Application Continuity — application-side)

pre_conditions:
  - "Workload type is OLTP or mixed"
  - "Application can use Oracle JDBC thin driver with TAC configuration"
  - "RTO < 2 minutes acceptable for DB layer"
  - "Single-region deployment (for cross-region, combine with database-dr-cross-region pattern)"

architecture:
  components:
    - { name: "ADB-S Primary", subnet: "private-db", config: "OCPU sized per sizing rules, auto-scaling enabled" }
    - { name: "ADB-S Local Standby", subnet: "private-db", config: "Automatic via ADG, same OCPU allocation" }
  application_config:
    - "JDBC connection string uses recommended TAC format"
    - "Application uses connection pool with FAN events enabled"
    - "Non-replayable operations (UTL_HTTP, DBMS_PIPE) identified and handled"

trade_offs:
  pros:
    - "Zero perceived RTO for applications with replayable transactions"
    - "Automatic failover — no DBA intervention needed"
    - "Standby is maintained automatically by Oracle"
  cons:
    - "DB itself is unavailable ~2 minutes during failover (TAC masks this from app)"
    - "TAC replay NOT guaranteed with side effects (UTL_HTTP, DBMS_PIPE, NOCACHE sequences)"
    - "Standby OCPU cost is same as primary"
    - "Local ADG only — same region, same AD"

conflicts_with:
  - "dbcs-rac (RAC not available on ADB-S)"

combines_with:
  - "database-dr-cross-region (adds cross-region protection)"
  - "networking-basic (requires VCN + private subnet)"
  - "security-baseline (Data Safe, Vault)"

cost_model:
  formula: "2x primary OCPU cost (primary + standby) + storage (shared)"
  example: "8 OCPU primary, 2 TB → ~$2,600/mo PAYG or ~$1,300/mo BYOL (OCPU only)"

gotchas:
  - "TAC replay not guaranteed with non-replayable operations — audit application code"
  - "Local ADG failover is automatic but takes ~2 minutes at DB level"
  - "Auto-scaling on primary does NOT auto-scale the standby — standby matches primary base"
  - "Test failover behavior BEFORE go-live, not after"

when_to_use: "Standard HA for any ADB-S OLTP workload. Default choice unless specific reason to deviate."
when_NOT_to_use: "If zero RPO + zero RTO is a hard legal requirement (nothing achieves true zero), or if RAC is needed (use ExaCS)."
```

---

### 9. `kb/patterns/database-dr-cross-region.yaml`

Same format. Cover:
- Cross-region ADG (async, RPO ≈ seconds)
- Refreshable Clone for read offloading in DR region
- DR app tier strategy (dormant, Terraform-on-demand, pilot light)
- DNS/traffic management for failover
- Gotchas: cross-region read offload via ProxySQL is architecturally impossible without pre-provisioned Elastic Pool in Region B post-switchover; stale read mitigation via DBMS_PROXY_SQL.DISABLE_READ_ONLY_OFFLOAD for planned switchovers; OCI Events + Functions for unplanned failover automation

---

### 10. `kb/patterns/networking-basic.yaml`

Cover:
- VCN with public + private subnets
- Gateway selection (IGW, NAT, SGW, DRG)
- NSGs (preferred) vs Security Lists
- Load Balancer placement (public subnet)
- Service Gateway for OCI service access (backup, Object Storage)
- CIDR planning guidelines
- When to add DRG (FastConnect, VPN, inter-VCN peering)

---

### 11. `kb/well-architected/security-compliance.yaml`

Structured checklist (not narrative). Each check has: id, description, severity (HIGH/MEDIUM/LOW), auto_detect_from (which architecture element satisfies it), wa_reference (URL path to Oracle doc).

Cover all checks from the WA Framework Security pillar:
- IAM (least-privilege, MFA, no tenancy admin for daily ops, federation)
- Resource isolation (compartments, tags, security zones)
- Database security (private subnets, TDE+Vault, key rotation, Data Safe, DELETE restrictions)
- Data protection (encryption at rest, Vault-managed keys, bucket policies)
- Network security (NSGs, no SSH from 0.0.0.0/0, WAF, Service Gateway, Network Firewall)
- Monitoring & audit (Cloud Guard, OCI Audit, VCN Flow Logs, vulnerability scanning, SIEM)

---

### 12. `kb/well-architected/reliability-resilience.yaml`

Same format. Checks for:
- Scalability (auto-scaling, service limits, capacity reservations)
- Fault-tolerant networking (redundant FastConnect, VPN backup, DRG tunnels, multi-AD/FD)
- Data backup (automated backups, retention, cross-region copy, boot volume backups)
- Data replication (Data Guard/ADG, RPO/RTO validation, Object Storage replication)
- Disaster recovery (DR region, switchover procedures, DR drill schedule, DNS failover, app tier DR strategy)

---

### 13. `kb/well-architected/performance-cost.yaml`

Checks for:
- Compute sizing (not over-provisioned, flex shapes, ARM considered, burstable for dev/test)
- Storage strategy (tier matches access pattern, IOPS tier, auto-tiering)
- Network tuning (bandwidth matches needs, NLB vs Flex LB decision)
- Cost management (BYOL analysis, reserved capacity, budgets/alerts, tagging, auto-scaling limits, non-prod scheduling)

---

### 14. `kb/well-architected/operational-efficiency.yaml`

Checks for:
- Deployment (IaC/Terraform, CI/CD, blue/green or canary, environment parity)
- Monitoring (alarms, custom metrics, Logging Analytics, APM, DB Management, Ops Insights)
- OS management (patch management, automated patching, vulnerability remediation SLA)
- Operations support (support plan level, notification topics, runbooks, Events + Functions automation)

---

### 15. `kb/well-architected/distributed-cloud.yaml`

Checks for (conditional — only when applicable):
- Deployment model selection (public, dedicated, hybrid, multicloud)
- Data residency mapping
- Consistent IAM across locations
- Data synchronization strategy
- Encryption key locality
- Unified monitoring

---

### 16. `kb/pricing/database.yaml`

Pricing ranges (not exact — within 15%) for:
- ADB-S PAYG and monthly flex (OCPU, storage, auto-scaling)
- ADB-S BYOL discount ranges
- ADB-D pricing model
- DBCS pricing by edition
- ExaCS pricing (quarter/half/full rack)
- Include notes on what's included (backup, patching, etc.) vs extra

---

### 17. `kb/competitive/aws-mapping.yaml`

Service-to-service mapping for the top 15-20 services, with REAL differences (not marketing). For each mapping: oci_service, aws_equivalent, genuine_advantages (OCI), genuine_gaps (OCI), notes. Focus on database services (ADB vs RDS/Aurora), compute, networking, security.

---

### 18. `kb/field-knowledge/gotchas.yaml`

At least 15-20 real-world gotchas that docs don't tell you. Things like:
- DEP provisioning takes days to weeks
- Auto-scaling activation delay
- TAC replay limitations
- Maintenance window immutability post-creation
- OCI CLI JSON serialization bugs for certain complex types
- Service limits that are lower than documented
- Cross-region read offload impossibility without pre-provisioned resources

---

### 19. `examples/sample-discovery-notes.md`

Realistic messy notes from a discovery meeting. Mix of English, abbreviations, incomplete sentences, numbers scattered around. Something like:

```
Acme Corp - met with CTO (Jane) and lead DBA (Mike) on March 10

3 oracle DBs on-prem exadata x8m
- main OLTP: 4TB, 19c EE, RAC 2-node, ~70% CPU avg
- reporting: 2TB, using GoldenGate from main
- small APEX app DB: 200GB, single instance

WebLogic 14c on 6 bare metal servers... java apps
MQ Series for async messaging between apps

Want 99.95% avail, PCI compliant (credit card processing)
Black Friday peaks 3x normal
...
```

---

### 20. `examples/sample-workload-profile.yaml`

The structured output of Phase 1 from the discovery notes above.

---

### 21. `examples/migration-adb-ha-dr.yaml`

The diagram spec YAML for the architecture composed from the workload profile. Must be compatible with the `from_spec()` method of the Python generator.

---

### 22. `Makefile`

```makefile
.PHONY: example deck full clean validate codex-package

example:
	python tools/oci_diagram_gen.py --spec examples/migration-adb-ha-dr.yaml --output examples/sample-output/architecture.drawio
	@echo "Generated examples/sample-output/architecture.drawio"

deck:
	python tools/oci_deck_gen.py --spec examples/migration-adb-ha-dr.yaml --output examples/sample-output/architecture-proposal.pptx
	@echo "Generated examples/sample-output/architecture-proposal.pptx"

full:
	python tools/oci_output.py --spec examples/migration-adb-ha-dr.yaml --output-dir examples/sample-output --format full
	@echo "Generated all outputs in examples/sample-output/"

validate:
	python -c "from tools.oci_diagram_gen import OCIDiagramGenerator; print('Diagram Generator OK')"
	python -c "from tools.oci_deck_gen import OCIDeckGenerator; print('Deck Generator OK')"
	python -c "import yaml; yaml.safe_load(open('config/workload-profile-schema.yaml')); print('Schema OK')"
	python -c "import yaml; yaml.safe_load(open('config/service-categories.yaml')); print('Categories OK')"
	@echo "All validations passed"

codex-package:
	@mkdir -p codex/tools
	cp tools/oci_diagram_gen.py codex/tools/
	cp tools/oci_deck_gen.py codex/tools/
	cp tools/oci_output.py codex/tools/
	cp -r kb codex/
	cp -r config codex/
	@echo "Codex skill package ready in codex/"

install:
	pip install -r requirements.txt

clean:
	rm -f examples/sample-output/*.drawio
	rm -f examples/sample-output/*.pptx
	rm -f examples/sample-output/*.xlsx
	rm -f examples/sample-output/*.docx
```

---

### 23. `tools/oci_deck_gen.py`

Slide deck generator using `python-pptx`. Takes the same architecture data that feeds the diagram generator and produces a `.pptx` file.

**Requirements:**
- Class `OCIDeckGenerator` with method `from_spec(yaml_dict)` and `save(filepath)`
- CLI: `python tools/oci_deck_gen.py --spec examples/migration-adb-ha-dr.yaml --output proposal.pptx`
- Produces a 10-12 slide deck following this structure:

**Slide structure:**

| # | Slide | Content |
|---|-------|---------|
| 1 | Title | Customer name, project name, date, "Architecture Proposal" |
| 2 | Engagement Summary | Why we're here, current state bullets, target state, timeline |
| 3 | Architecture Overview | Diagram image (auto-exported from .drawio or placeholder) |
| 4 | Architecture Decisions | 2-column table: Decision / Rationale (4-6 rows) |
| 5 | HA/DR | Simplified HA/DR diagram + RTO/RPO table per tier |
| 6 | Security & Compliance | Compliance checkmarks + security controls grid |
| 7 | Cost Estimate | Table: Component / Monthly PAYG / Monthly BYOL / Notes + assumptions |
| 8 | Cost Comparison | (Optional) Current vs OCI or OCI vs AWS — bar chart or table |
| 9 | Migration Approach | Horizontal timeline with 4 phases + milestones |
| 10 | Risk Register | Table: Risk / Severity / Mitigation (top 5-6) |
| 11 | WA Scorecard | 5 pillars with traffic-light indicators + top recommendations |
| 12 | Next Steps | 3-5 numbered actions with target dates |

**Design standards:**
- Slide dimensions: 13.333" x 7.5" (widescreen 16:9)
- Colors — OCI brand palette:
  - Background: white `#FFFFFF` for content, dark `#312D2A` for title slide
  - Primary accent: teal `#2D5967` (headers, table headers, highlights)
  - Secondary: copper `#AA643B` (database content)
  - Tertiary: purple `#804998` (integration content)
  - Text: charcoal `#312D2A` — NEVER pure black
  - Success: `#5E9624` (green for passed checks)
  - Warning: `#AE562C` (burnt orange for recommendations)
  - Error: `#C74634` (red for gaps)
  - Table alternating rows: `#F5F4F2`
- Typography:
  - Titles: 24-28pt bold, `#312D2A`
  - Body: 12-14pt regular, `#312D2A`
  - Table headers: 11pt bold white on `#2D5967` background
  - Table body: 10-11pt, `#312D2A`
  - Footnotes: 8-9pt italic `#70665E`
  - Font: Segoe UI (widely available, close to Oracle Sans)
- Layout: 0.5" margins, title top-left, slide number bottom-right
- No decorative elements — no gradients, clip art, or stock photos. Clean and technical.

**The spec YAML feeds both tools.** The same YAML that drives `oci_diagram_gen.py` also drives `oci_deck_gen.py`. Add these top-level keys to the spec for deck-specific content:

```yaml
# Added to the architecture spec YAML:
deck:
  customer_name: "Acme Corp"
  project_name: "Oracle Migration to OCI"
  architect: "Diego Cabrera"
  date: "March 2026"
  
  engagement_summary:
    why: "End of Exadata X8M hardware support + Oracle ULA renewal opportunity"
    current_state:
      - "3 Oracle 19c databases on Exadata X8M on-prem (4TB OLTP, 2TB reporting, 200GB APEX)"
      - "WebLogic 14c on 6 bare metal servers"
      - "MQ Series for async messaging"
    target: "Migrate to OCI ADB-S with cross-region HA/DR"
    timeline: "6 months — target go-live September 2026"

  decisions:
    - { decision: "ADB-S over ExaCS", rationale: "Variable workload, no DBA team, auto-scaling needed" }
    - { decision: "Cross-region ADG to Phoenix", rationale: "PCI compliance requires geo-redundant DR" }
    - { decision: "FastConnect over VPN", rationale: "Low-latency requirement during hybrid migration period" }
    - { decision: "OKE for microservices tier", rationale: "Team migrating to containers, per-service auto-scaling" }

  costs:
    components:
      - { name: "ADB-S Primary (8 OCPU)", monthly_payg: 2400, monthly_byol: 1200, notes: "Auto-scale to 16" }
      - { name: "ADB-S Standby (ADG)", monthly_payg: 2400, monthly_byol: 1200, notes: "Same region" }
      # ...
    assumptions:
      - "730 hours/month at sustained usage"
      - "BYOL with 8 existing processor licenses"
      - "Auto-scaling active ~4 hours/day during peaks"

  risks:
    - { risk: "App compatibility with ADB-S", severity: "MEDIUM", mitigation: "Run assessment tool on non-prod first" }
    - { risk: "TAC replay for non-replayable ops", severity: "LOW", mitigation: "Audit code, wrap UTL_HTTP calls" }
    # ...

  wa_scorecard:
    security: { status: "PASS", passed: 18, total: 20 }
    reliability: { status: "PASS_WITH_RECOMMENDATIONS", passed: 12, total: 15 }
    performance: { status: "PASS", passed: 10, total: 10 }
    operational: { status: "GAPS_IDENTIFIED", passed: 6, total: 10 }
    distributed: { status: "NOT_APPLICABLE" }
    top_recommendations:
      - "Define IaC (Terraform) for all infrastructure"
      - "Establish quarterly DR drill schedule"
      - "Enable OCI Vulnerability Scanning"

  next_steps:
    - { action: "Review and approve architecture design", date: "March 25, 2026" }
    - { action: "Provision OCI tenancy and request DEP", date: "April 1, 2026" }
    - { action: "Run application assessment tool", date: "April 7, 2026" }
    - { action: "Begin Phase 1: Infrastructure setup", date: "April 14, 2026" }
    - { action: "Schedule weekly architecture review cadence", date: "Ongoing" }

  migration_phases:
    - { name: "Assessment & Prep", weeks: "1-4" }
    - { name: "Infrastructure Setup", weeks: "3-6" }
    - { name: "Migration & Testing", weeks: "5-10" }
    - { name: "Cutover & Validation", weeks: "9-12" }
```

**Dependencies:** `pip install python-pptx`

---

### 24. `tools/oci_output.py`

Unified output orchestrator. Thin wrapper that calls the right generators based on output selection.

```python
"""
Usage:
    python tools/oci_output.py --spec spec.yaml --output-dir ./output --format deck
    python tools/oci_output.py --spec spec.yaml --output-dir ./output --format "deck+drawio"
    python tools/oci_output.py --spec spec.yaml --output-dir ./output --format full

Formats:
    deck          → .pptx only (default)
    deck+drawio   → .pptx + .drawio
    deck+xlsx     → .pptx + .xlsx cost spreadsheet
    deck+doc      → .pptx + .docx technical document
    full          → all of the above
    doc           → .docx only
    drawio        → .drawio only
"""
```

Calls `oci_diagram_gen.py`, `oci_deck_gen.py`, and (future) `oci_doc_gen.py` / `oci_cost_gen.py`.

---

### 25. `codex/SKILL.md` (Codex Skill Packaging)

Codex uses "skills" as folders with instruction files and tools. Package the Deal Accelerator as a Codex skill.

**Create `codex/` directory with this structure:**

```
codex/
├── SKILL.md              # Codex-formatted skill instructions
├── skill.json            # Codex skill manifest
└── tools/                # Symlinks or copies of tools/
```

**`codex/skill.json`:**

```json
{
  "name": "oci-deal-accelerator",
  "version": "1.0.0",
  "description": "Generate OCI architecture proposals from customer discovery notes. Produces slide decks, diagrams, cost estimates, and Well-Architected scorecards.",
  "instructions": "SKILL.md",
  "tools": [
    {
      "name": "generate_diagram",
      "description": "Generate an OCI architecture diagram (.drawio) from a YAML spec",
      "command": "python tools/oci_diagram_gen.py --spec {spec_file} --output {output_file}"
    },
    {
      "name": "generate_deck",
      "description": "Generate an architecture proposal slide deck (.pptx) from a YAML spec",
      "command": "python tools/oci_deck_gen.py --spec {spec_file} --output {output_file}"
    },
    {
      "name": "generate_output",
      "description": "Generate complete architecture proposal outputs (deck, diagram, cost spreadsheet)",
      "command": "python tools/oci_output.py --spec {spec_file} --output-dir {output_dir} --format {format}"
    }
  ],
  "context": [
    "kb/**/*.yaml",
    "kb/**/*.md",
    "config/*.yaml"
  ],
  "requirements": [
    "python>=3.8",
    "pyyaml",
    "python-pptx"
  ]
}
```

**`codex/SKILL.md`:**

This is an **adapted version** of the main `SKILL.md` with Codex-specific additions:

1. **Same core content** as the main SKILL.md (principles, workflow, service catalog, diagram styles)
2. **Add Codex-specific instructions at the top:**

```markdown
# Codex Skill: OCI Deal Accelerator

## How to Use This Skill in Codex

This skill runs in three modes:

### Mode 1: Full Pipeline (recommended)
Give me your customer discovery notes (paste them or point to a file). I will:
1. Parse them into a structured Workload Profile
2. Compose an OCI architecture
3. Validate against the Well-Architected Framework
4. Generate the output you want (deck by default)

Example: "Here are my notes from the discovery call with Acme Corp: ..."

### Mode 2: Diagram Only
Give me a YAML architecture spec and I'll generate the .drawio file.

Example: "Generate a diagram from examples/migration-adb-ha-dr.yaml"

### Mode 3: Iterate on Existing Output
Point me to an existing spec YAML and tell me what to change.

Example: "Add a NoSQL database to the app tier and regenerate the deck"

## Output Selection
Tell me what format you want. Default is a slide deck.

- "deck" — slide deck (.pptx) — DEFAULT
- "deck + drawio" — deck + editable diagram
- "deck + xlsx" — deck + cost spreadsheet
- "full" — everything
- "drawio" — diagram only

## Available Tools
I have access to these tools:
- `generate_diagram` — creates .drawio files with official OCI styles
- `generate_deck` — creates .pptx slide decks with OCI branding
- `generate_output` — orchestrates multiple outputs

## Knowledge Base
I have access to the full KB in `kb/` covering:
- 6+ OCI service files with sizing rules, gotchas, and competitive notes
- 3+ composable architecture patterns
- CPU conversion ratios and sizing methodology
- Pricing ranges for cost estimation
- Well-Architected Framework checklists (5 pillars)
- AWS competitive mapping
- Real-world field knowledge and gotchas

[... rest of SKILL.md content follows ...]
```

3. **Add Codex multi-agent hint** at the bottom:

```markdown
## Multi-Agent Mode (Codex App)

When running in the Codex app with multiple agents, this skill can be split:

- **Agent 1 (Architect)**: Runs Phase 1 (discovery capture) and Phase 2 (composition)
- **Agent 2 (Validator)**: Runs WA validation on the composed architecture
- **Agent 3 (Renderer)**: Generates diagram + deck + any other outputs

The Architect agent produces the structured YAML spec. The Validator annotates it with WA findings. The Renderer consumes the annotated spec and produces files.

Each agent reads the same KB but focuses on its phase. The orchestrating agent (or the user) coordinates handoffs.
```

---

### 26. `codex/README.md`

Short README for the Codex skill:

```markdown
# OCI Deal Accelerator — Codex Skill

## Quick Start

1. Open Codex app or CLI
2. Load this skill: `codex --skill ./codex`
3. Paste your discovery notes
4. Get your architecture proposal

## Requirements

- Codex with GPT-5.4 (recommended) or GPT-5.3-Codex
- Python 3.8+ with pyyaml and python-pptx
- 1M context window recommended for full KB loading

## Also Works With

This skill is LLM-agnostic. The same SKILL.md and KB work with:
- Claude Code (Anthropic)
- ChatGPT (OpenAI) — paste SKILL.md as system prompt
- Gemini Pro (Google) — paste SKILL.md as system instruction
- Any LLM with tool/function calling support

The Codex packaging adds tool definitions and multi-agent coordination 
but the core skill logic is portable.
```

---

### 27. `requirements.txt`

```
pyyaml>=6.0
python-pptx>=0.6.21
```

---

## Build Order

Build in this exact sequence — each file may reference previous ones:

1. `tools/oci_diagram_gen.py` (everything depends on this)
2. `config/workload-profile-schema.yaml`
3. `config/service-categories.yaml`
4. `kb/sizing/cpu-conversion-ratios.yaml`
5. `kb/services/adb-serverless.yaml`
6. `kb/services/exadata-cloud.yaml`
7. `kb/services/oci-networking-core.yaml`
8. `kb/patterns/database-ha-adb-s.yaml`
9. `kb/patterns/database-dr-cross-region.yaml`
10. `kb/patterns/networking-basic.yaml`
11. `kb/well-architected/security-compliance.yaml`
12. `kb/well-architected/reliability-resilience.yaml`
13. `kb/well-architected/performance-cost.yaml`
14. `kb/well-architected/operational-efficiency.yaml`
15. `kb/well-architected/distributed-cloud.yaml`
16. `kb/pricing/database.yaml`
17. `kb/competitive/aws-mapping.yaml`
18. `kb/field-knowledge/gotchas.yaml`
19. `examples/sample-discovery-notes.md`
20. `examples/sample-workload-profile.yaml`
21. `examples/migration-adb-ha-dr.yaml`
22. `Makefile`
23. `tools/oci_deck_gen.py` (slide deck generator)
24. `tools/oci_output.py` (output orchestrator)
25. `codex/SKILL.md` (Codex-adapted skill instructions)
26. `codex/skill.json` (Codex skill manifest)
27. `codex/README.md`
28. `requirements.txt`

## Quality Criteria

- Every KB file has `last_verified` date in frontmatter
- Every service file has `when_to_use`, `when_NOT_to_use`, `gotchas`
- Every pattern file has `pre_conditions`, `conflicts_with`, `combines_with`, `cost_model`
- Every WA checklist item has `id`, `description`, `severity`, `auto_detect_from`
- The Python diagram generator produces valid XML that opens in draw.io
- The Python deck generator produces valid .pptx that opens in PowerPoint/Google Slides
- The example spec generates a complete diagram via `make example`
- The example spec generates a complete deck via `make deck`
- `make full` produces all outputs without errors
- `make validate` passes all checks
- `make codex-package` produces a self-contained Codex skill folder
- Pricing is ranges (within 15%), not exact — mark as estimated
- Competitive mapping is honest — includes genuine OCI gaps, not just advantages
- Field knowledge captures things the official docs don't tell you
- The Codex skill.json correctly references all tools and KB paths
- The same YAML spec drives both diagram and deck generation (single source of truth)

## Key Technical Facts (use these — they come from real field experience)

- ADB-S auto-scaling activation: 2-3 minutes
- TAC replay: NOT guaranteed with UTL_HTTP, DBMS_PIPE, NOCACHE sequences
- TAC: zero *perceived* RTO for app, but DB itself is unavailable ~2 min during failover
- DEP provisioning: days to weeks depending on capacity
- DEP billing: starts only at AVAILABLE state
- DEP co-location: happens at next maintenance window, not at join time
- ADG must be disabled before joining DEP (acknowledged Oracle bug)
- Cross-region read offload via ProxySQL: architecturally impossible without pre-provisioned Elastic Pool in Region B post-switchover
- Stale read mitigation for planned switchovers: DBMS_PROXY_SQL.DISABLE_READ_ONLY_OFFLOAD
- Unplanned failover stale read mitigation: OCI Events + OCI Functions automation
- Auto Indexing on ADB-S: indexes created HIDDEN by default, instantly reversible, DML costing in 23ai prevents over-indexing
- OCI CLI: --resource-pool-summary works on 3.73+; --autonomous-database-maintenance-window has JSON serialization bug on both 3.73.1 and 3.75.0
- Maintenance window JSON schema: {"dayOfWeek": {"name": "SATURDAY"}, "hourOfDay": 4} — but API returns 403 at create time; must set post-creation or via Console
- OCPU = 1 physical core = 2 vCPUs (on most platforms)
- For ADB-S sizing: base at P75, auto-scale covers P75→P95+

Start building file 1.


---

## ░░░ SECTION 3: DIAGRAM GENERATOR — styles, Python, YAML spec ░░░

# OCI ARCHITECTURE DIAGRAM GENERATOR — Complete Prompt

## What This Does

This prompt enables an AI skill to generate professional OCI architecture diagrams as `.drawio` files that match Oracle's official visual style. The output is a `.drawio` XML file that any architect can open in draw.io (desktop or web) without importing any external libraries.

The generated diagrams follow the exact container hierarchy, color palette, typography, and connector styles defined in Oracle's official **OCI Style Guide for Draw.io Toolkit v24.2**.

---

## Source of Truth

All styles below were extracted from:
- **OCI Library.xml** — 224 official OCI service icons (stencils)
- **OCI Architecture Diagram Toolkit v24.2.drawio** — official templates and examples
- **Reference architectures**: `select-ai-apex-architecture-oracle`, `exadb-dr-on-db-at-azure-oracle`

Download from: https://docs.oracle.com/en-us/iaas/Content/General/Reference/graphicsfordiagrams.htm

---

## OCI Diagram Visual Hierarchy

OCI diagrams follow a strict nesting order. Every element lives inside a container:

```
Tenancy (outermost, dashed gray)
  └── Region (solid fill, rounded)
        ├── Availability Domain (optional, darker gray fill)
        │     └── VCN (dashed burnt orange, thick)
        │           ├── Subnet: Public (dashed burnt orange, thin, near-white fill)
        │           │     └── [Service blocks: LB, Bastion, API GW, WAF...]
        │           ├── Subnet: App Tier (dashed burnt orange, thin)
        │           │     └── [Service blocks: VM, OKE, Functions, Streaming...]
        │           ├── Subnet: Data Tier (dashed burnt orange, thin)
        │           │     └── [Service blocks: ADB, NoSQL, Cache, Data Safe...]
        │           └── Gateways row: IGW, NAT GW, Service GW, DRG
        └── Observability row: Monitoring, Logging, DB Mgmt, Ops Insights...
  
  └── Region DR (same structure, smaller)
  
On-Premises (outside tenancy, dashed gray)
  └── [Source DB, App Servers, Legacy systems...]

External: Users, Internet, 3rd Party Cloud (outside everything)
```

---

## Container Styles (EXACT from toolkit)

These are the **verbatim style strings** from the OCI Library.xml. Use them as-is.

### Tenancy
```
whiteSpace=wrap;html=1;strokeWidth=1;dashed=1;align=left;fontFamily=Oracle Sans;verticalAlign=top;fillColor=none;fontColor=#312D2A;strokeColor=#9E9892;fontSize=12;spacingLeft=5;
```
- Dashed gray border, NO fill, charcoal text

### OCI Region
```
whiteSpace=wrap;html=1;align=center;fontFamily=Oracle Sans;verticalAlign=top;fillColor=#F5F4F2;rounded=1;arcSize=10;strokeColor=#9E9892;fontColor=#312D2A;fontSize=12;
```
- **Only container with solid fill** (#F5F4F2 warm gray), rounded corners

### Availability Domain
```
whiteSpace=wrap;html=1;strokeWidth=1;align=center;fontFamily=Oracle Sans;verticalAlign=top;fillColor=#DFDCD8;fontColor=#312D2A;strokeColor=#9E9892;rounded=1;arcSize=1;fontStyle=1;
```
- Slightly darker gray fill (#DFDCD8), bold text

### VCN
```
whiteSpace=wrap;html=1;strokeWidth=2;dashed=1;align=left;fontFamily=Oracle Sans;verticalAlign=top;fillColor=none;fontColor=#AE562C;strokeColor=#AE562C;perimeterSpacing=0;fontSize=12;spacingLeft=5;
```
- **DASHED BURNT ORANGE (#AE562C)** — this is the signature OCI visual
- strokeWidth=2 (thick), NO fill
- Text is also burnt orange

### Subnet
```
whiteSpace=wrap;html=1;strokeWidth=1;dashed=1;align=left;fontFamily=Oracle Sans;verticalAlign=top;fillColor=#FCFBFA;fontColor=#AE562C;strokeColor=#AE562C;fontSize=11;spacingLeft=5;rounded=1;arcSize=3;
```
- Dashed burnt orange like VCN but **strokeWidth=1** (thinner)
- Fill: #FCFBFA (near-white) — makes subnets visually distinct from transparent VCN
- Text is burnt orange

### Compartment / Fault Domain / Tier
```
whiteSpace=wrap;html=1;strokeWidth=1;dashed=1;align=left;fontFamily=Oracle Sans;verticalAlign=top;fillColor=none;fontColor=#312D2A;strokeColor=#9E9892;fontSize=12;spacingLeft=5;
```
- Same as Tenancy style (dashed gray)

---

## Color Palette

### Service Block Colors
| Color | Hex | Usage |
|-------|-----|-------|
| OCI Teal | `#2D5967` | All OCI infra services: compute, networking, security, observability |
| Oracle Copper | `#AA643B` | Database services: ADB, DBCS, ExaCS, NoSQL, Cache, GoldenGate |
| Oracle Purple | `#804998` | Integration & connectivity: DRG, Streaming, Queue, OIC, FastConnect |

### Background Colors
| Color | Hex | Usage |
|-------|-----|-------|
| Region fill | `#F5F4F2` | Region container background |
| AD fill | `#DFDCD8` | Availability Domain background, also dormant elements |
| Subnet fill | `#FCFBFA` | Subnet interior (near-white) |

### Text & Border Colors
| Color | Hex | Usage |
|-------|-----|-------|
| Primary text | `#312D2A` | All text — NEVER use pure black |
| Secondary text | `#70665E` | Muted labels, step circles, title text |
| Container border | `#9E9892` | Tenancy, Region, Compartment borders |
| VCN/Subnet border | `#AE562C` | VCN and Subnet borders ONLY |
| Connector | `#706E6F` | Standard connection arrows |
| Near-black | `#161513` | Darkest accent (rare) |

### Typography
- Font: `Oracle Sans` (fallback: `Segoe UI, Helvetica Neue, Arial, sans-serif`)
- Container labels: 11-12px, `#312D2A`
- Service labels: 8-9px, `#FFFFFF` on colored background
- Title: 10px, italic, `#70665E`

---

## Service Block Style

All service blocks use the same base style, varying only the `fillColor`:

```
rounded=1;whiteSpace=wrap;html=1;fillColor={COLOR};strokeColor=none;fontColor=#FFFFFF;fontSize=8;fontFamily=Oracle Sans;arcSize=8;verticalAlign=middle;align=center;
```

- `strokeColor=none` — no border on service blocks
- `rounded=1;arcSize=8` — subtle rounded corners
- White text on colored background

Dormant/standby elements:
```
rounded=1;whiteSpace=wrap;html=1;fillColor=#DFDCD8;strokeColor=#9E9892;fontColor=#70665E;fontSize=8;fontFamily=Oracle Sans;arcSize=8;fontStyle=2;
```

---

## Connection Styles

### Standard data flow
```
endArrow=block;endFill=1;html=1;strokeColor=#706e6f;strokeWidth=1;fontFamily=Oracle Sans;
```

### Database connections (SQL*Net, TAC)
```
endArrow=block;endFill=1;html=1;strokeColor=#aa643b;strokeWidth=1.5;fontSize=8;fontColor=#312D2A;fontFamily=Oracle Sans;
```

### Data Guard / Replication (dashed burnt orange)
```
endArrow=block;endFill=1;html=1;strokeColor=#AE562C;strokeWidth=2;fontSize=8;fontColor=#312D2A;fontFamily=Oracle Sans;dashed=1;dashPattern=10 6;
```

### FastConnect (bidirectional purple)
```
endArrow=block;endFill=1;startArrow=block;startFill=1;html=1;strokeColor=#804998;strokeWidth=2;fontSize=8;fontColor=#312D2A;fontFamily=Oracle Sans;
```

### Migration path (dashed gray)
```
endArrow=block;endFill=1;html=1;strokeColor=#706e6f;strokeWidth=1.5;fontSize=8;fontColor=#312D2A;fontFamily=Oracle Sans;dashed=1;dashPattern=12 6;
```

### ETL / event-driven (dashed purple)
```
endArrow=block;endFill=1;html=1;strokeColor=#804998;strokeWidth=1;fontSize=8;fontColor=#312D2A;fontFamily=Oracle Sans;dashed=1;
```

---

## Python Generator

The following Python script takes a diagram specification (YAML) and produces a `.drawio` file.

```python
#!/usr/bin/env python3
"""
OCI Architecture Diagram Generator
Produces .drawio files with Oracle official container styles.

Usage:
    python oci_diagram_gen.py --spec architecture.yaml --output diagram.drawio
    
Or import and use programmatically:
    from oci_diagram_gen import OCIDiagramGenerator
    gen = OCIDiagramGenerator()
    gen.add_region("region1", "US East (Ashburn)", x=15, y=30, w=1140, h=670)
    gen.add_vcn("vcn1", "prod-vcn 10.0.0.0/16", parent="region1", ...)
    gen.save("output.drawio")
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
import yaml
import argparse
import sys

# ============================================================
# OCI OFFICIAL STYLES (from OCI Style Guide for Draw.io v24.2)
# ============================================================

STYLES = {
    # Container styles
    "tenancy": (
        "whiteSpace=wrap;html=1;strokeWidth=1;dashed=1;align=left;"
        "fontFamily=Oracle Sans;verticalAlign=top;fillColor=none;"
        "fontColor=#312D2A;strokeColor=#9E9892;fontSize=12;spacingLeft=5;"
        "spacingTop=5;"
    ),
    "region": (
        "whiteSpace=wrap;html=1;align=center;fontFamily=Oracle Sans;"
        "verticalAlign=top;fillColor=#F5F4F2;rounded=1;arcSize=10;"
        "strokeColor=#9E9892;fontColor=#312D2A;fontSize=12;spacingTop=5;"
    ),
    "ad": (
        "whiteSpace=wrap;html=1;strokeWidth=1;align=center;"
        "fontFamily=Oracle Sans;verticalAlign=top;fillColor=#DFDCD8;"
        "fontColor=#312D2A;strokeColor=#9E9892;rounded=1;arcSize=1;"
        "fontStyle=1;"
    ),
    "vcn": (
        "whiteSpace=wrap;html=1;strokeWidth=2;dashed=1;align=left;"
        "fontFamily=Oracle Sans;verticalAlign=top;fillColor=none;"
        "fontColor=#AE562C;strokeColor=#AE562C;perimeterSpacing=0;"
        "fontSize=12;spacingLeft=5;spacingTop=5;"
    ),
    "subnet": (
        "whiteSpace=wrap;html=1;strokeWidth=1;dashed=1;align=left;"
        "fontFamily=Oracle Sans;verticalAlign=top;fillColor=#FCFBFA;"
        "fontColor=#AE562C;strokeColor=#AE562C;fontSize=11;"
        "spacingLeft=5;spacingTop=5;rounded=1;arcSize=3;"
    ),
    "compartment": (
        "whiteSpace=wrap;html=1;strokeWidth=1;dashed=1;align=left;"
        "fontFamily=Oracle Sans;verticalAlign=top;fillColor=none;"
        "fontColor=#312D2A;strokeColor=#9E9892;fontSize=12;spacingLeft=5;"
    ),
    
    # Service block colors
    "svc_infra": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#2d5967;"
        "strokeColor=none;fontColor=#FFFFFF;fontSize=8;"
        "fontFamily=Oracle Sans;arcSize=8;verticalAlign=middle;align=center;"
    ),
    "svc_database": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#aa643b;"
        "strokeColor=none;fontColor=#FFFFFF;fontSize=8;"
        "fontFamily=Oracle Sans;arcSize=8;verticalAlign=middle;align=center;"
    ),
    "svc_integration": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#804998;"
        "strokeColor=none;fontColor=#FFFFFF;fontSize=8;"
        "fontFamily=Oracle Sans;arcSize=8;verticalAlign=middle;align=center;"
    ),
    "svc_dormant": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#DFDCD8;"
        "strokeColor=#9E9892;fontColor=#70665E;fontSize=8;"
        "fontFamily=Oracle Sans;arcSize=8;fontStyle=2;verticalAlign=middle;align=center;"
    ),
    "svc_legacy": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#70665E;"
        "strokeColor=none;fontColor=#FFFFFF;fontSize=8;"
        "fontFamily=Oracle Sans;arcSize=8;verticalAlign=middle;align=center;"
    ),
    "obs_bar": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#2d5967;"
        "strokeColor=none;fontColor=#FFFFFF;fontSize=7;"
        "fontFamily=Oracle Sans;arcSize=10;"
    ),
    
    # Connection styles
    "conn_standard": (
        "endArrow=block;endFill=1;html=1;strokeColor=#706e6f;"
        "strokeWidth=1;fontFamily=Oracle Sans;"
    ),
    "conn_db": (
        "endArrow=block;endFill=1;html=1;strokeColor=#aa643b;"
        "strokeWidth=1.5;fontSize=8;fontColor=#312D2A;fontFamily=Oracle Sans;"
    ),
    "conn_adg": (
        "endArrow=block;endFill=1;html=1;strokeColor=#AE562C;"
        "strokeWidth=2;fontSize=8;fontColor=#312D2A;"
        "fontFamily=Oracle Sans;dashed=1;dashPattern=10 6;"
    ),
    "conn_fastconnect": (
        "endArrow=block;endFill=1;startArrow=block;startFill=1;"
        "html=1;strokeColor=#804998;strokeWidth=2;fontSize=8;"
        "fontColor=#312D2A;fontFamily=Oracle Sans;"
    ),
    "conn_migration": (
        "endArrow=block;endFill=1;html=1;strokeColor=#706e6f;"
        "strokeWidth=1.5;fontSize=8;fontColor=#312D2A;"
        "fontFamily=Oracle Sans;dashed=1;dashPattern=12 6;"
    ),
    "conn_etl": (
        "endArrow=block;endFill=1;html=1;strokeColor=#804998;"
        "strokeWidth=1;fontSize=8;fontColor=#312D2A;"
        "fontFamily=Oracle Sans;dashed=1;"
    ),
    
    # Title
    "title": (
        "text;html=1;fontSize=10;fontColor=#70665E;"
        "fontFamily=Oracle Sans;align=right;verticalAlign=bottom;fontStyle=2;"
    ),
}

# Service category mapping
SVC_CATEGORY = {
    # Infrastructure (teal #2D5967)
    "compute": "svc_infra", "vm": "svc_infra", "bare_metal": "svc_infra",
    "load_balancer": "svc_infra", "flexible_lb": "svc_infra",
    "igw": "svc_infra", "internet_gateway": "svc_infra",
    "nat_gateway": "svc_infra", "natgw": "svc_infra",
    "service_gateway": "svc_infra", "sgw": "svc_infra",
    "waf": "svc_infra", "bastion": "svc_infra",
    "functions": "svc_infra", "oke": "svc_infra",
    "api_gateway": "svc_infra", "apigw": "svc_infra",
    "monitoring": "svc_infra", "logging": "svc_infra",
    "db_management": "svc_infra", "ops_insights": "svc_infra",
    "notifications": "svc_infra", "events": "svc_infra",
    "cloud_guard": "svc_infra", "data_safe": "svc_infra",
    "vault": "svc_infra", "object_storage": "svc_infra",
    "block_storage": "svc_infra", "file_storage": "svc_infra",
    
    # Database (copper #AA643B)
    "adb": "svc_database", "adb_s": "svc_database",
    "adb_d": "svc_database", "autonomous_db": "svc_database",
    "dbcs": "svc_database", "db_system": "svc_database",
    "exadata": "svc_database", "exacs": "svc_database",
    "nosql": "svc_database", "mysql": "svc_database",
    "postgresql": "svc_database", "opensearch": "svc_database",
    "cache": "svc_database", "redis": "svc_database",
    "goldengate": "svc_database",
    
    # Integration (purple #804998)
    "drg": "svc_integration",
    "dynamic_routing_gateway": "svc_integration",
    "streaming": "svc_integration", "kafka": "svc_integration",
    "queue": "svc_integration", "oci_queue": "svc_integration",
    "oic": "svc_integration", "integration_cloud": "svc_integration",
    "fastconnect": "svc_integration",
    "service_connector_hub": "svc_integration",
    
    # Special
    "dormant": "svc_dormant",
    "legacy": "svc_legacy",
}


class OCIDiagramGenerator:
    """Generate .drawio files with OCI official styles."""
    
    def __init__(self):
        self.cells = []
        self._id_counter = 100
    
    def _next_id(self):
        self._id_counter += 1
        return str(self._id_counter)
    
    def _make_cell(self, cell_id, value, style, parent, x, y, w, h, 
                   vertex=True, edge=False, source=None, target=None, 
                   waypoints=None):
        """Create an mxCell XML string."""
        attrs = f'id="{cell_id}" value="{self._escape(value)}" style="{style}"'
        if vertex:
            attrs += ' vertex="1"'
        if edge:
            attrs += ' edge="1"'
        if source:
            attrs += f' source="{source}"'
        if target:
            attrs += f' target="{target}"'
        attrs += f' parent="{parent}"'
        
        if edge and waypoints:
            geo = '<mxGeometry relative="1" as="geometry"><Array as="points">'
            for wx, wy in waypoints:
                geo += f'<mxPoint x="{wx}" y="{wy}"/>'
            geo += '</Array></mxGeometry>'
        elif edge:
            geo = '<mxGeometry relative="1" as="geometry"/>'
        else:
            geo = f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>'
        
        cell = f'<mxCell {attrs}>{geo}</mxCell>'
        self.cells.append(cell)
        return cell_id
    
    def _escape(self, text):
        """Escape XML special characters and convert newlines."""
        if not text:
            return ""
        return (text
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("\n", "&#xa;"))
    
    def _get_svc_style(self, service_type, font_size=None):
        """Get the style string for a service type."""
        category = SVC_CATEGORY.get(service_type, "svc_infra")
        style = STYLES[category]
        if font_size:
            style = style.replace("fontSize=8", f"fontSize={font_size}")
            style = style.replace("fontSize=9", f"fontSize={font_size}")
        return style
    
    # ---- Container methods ----
    
    def add_tenancy(self, cell_id, label, x=30, y=80, w=1850, h=720):
        return self._make_cell(cell_id, label, STYLES["tenancy"], "1", x, y, w, h)
    
    def add_region(self, cell_id, label, parent, x=15, y=30, w=1140, h=670):
        return self._make_cell(cell_id, label, STYLES["region"], parent, x, y, w, h)
    
    def add_ad(self, cell_id, label, parent, x=15, y=30, w=1100, h=640):
        return self._make_cell(cell_id, label, STYLES["ad"], parent, x, y, w, h)
    
    def add_vcn(self, cell_id, label, parent, x=15, y=30, w=1100, h=600):
        return self._make_cell(cell_id, label, STYLES["vcn"], parent, x, y, w, h)
    
    def add_subnet(self, cell_id, label, parent, x=15, y=30, w=280, h=400):
        return self._make_cell(cell_id, label, STYLES["subnet"], parent, x, y, w, h)
    
    def add_onprem(self, cell_id, label, x=30, y=850, w=650, h=120):
        return self._make_cell(cell_id, label, STYLES["compartment"], "1", x, y, w, h)
    
    # ---- Service block methods ----
    
    def add_service(self, cell_id, label, service_type, parent, 
                    x=20, y=35, w=150, h=50, font_size=None):
        style = self._get_svc_style(service_type, font_size)
        return self._make_cell(cell_id, label, style, parent, x, y, w, h)
    
    def add_obs_bar(self, cell_id, label, parent, x=20, y=640, w=78, h=22):
        return self._make_cell(cell_id, label, STYLES["obs_bar"], parent, x, y, w, h)
    
    # ---- Connection methods ----
    
    def add_connection(self, cell_id, label, conn_type, source, target, 
                       waypoints=None):
        style = STYLES.get(f"conn_{conn_type}", STYLES["conn_standard"])
        if label:
            style += f'fontSize=8;fontColor=#312D2A;'
        return self._make_cell(
            cell_id, label or "", style, "1", 0, 0, 0, 0,
            vertex=False, edge=True, source=source, target=target,
            waypoints=waypoints
        )
    
    # ---- Title ----
    
    def add_title(self, text, x=1400, y=990, w=470, h=35):
        return self._make_cell(
            "title", text, STYLES["title"], "1", x, y, w, h
        )
    
    # ---- Output ----
    
    def to_xml(self):
        """Generate the complete .drawio XML."""
        header = (
            '<mxfile host="app.diagrams.net" modified="2026-03-14T12:00:00.000Z" '
            'agent="Deal Accelerator" version="24.0.0" type="device">\n'
            '  <diagram name="OCI Architecture" id="oci-arch">\n'
            '    <mxGraphModel dx="1800" dy="1000" grid="1" gridSize="10" '
            'guides="1" tooltips="1" connect="1" arrows="1" fold="1" '
            'page="1" pageScale="1" pageWidth="1920" pageHeight="1100" '
            'math="0" shadow="0">\n'
            '      <root>\n'
            '        <mxCell id="0"/>\n'
            '        <mxCell id="1" parent="0"/>\n'
        )
        
        body = "\n".join(f"        {c}" for c in self.cells)
        
        footer = (
            '\n      </root>\n'
            '    </mxGraphModel>\n'
            '  </diagram>\n'
            '</mxfile>'
        )
        
        return header + body + footer
    
    def save(self, filepath):
        """Save to a .drawio file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_xml())
    
    # ---- High-level: build from spec ----
    
    @classmethod
    def from_spec(cls, spec):
        """Build a diagram from a YAML specification.
        
        spec format:
        {
            "title": "Customer X — Migration to OCI",
            "tenancy": {
                "label": "Oracle Cloud Infrastructure",
                "regions": [
                    {
                        "id": "region1",
                        "label": "US East (Ashburn)",
                        "primary": true,
                        "vcns": [
                            {
                                "id": "vcn1",
                                "label": "prod-vcn 10.0.0.0/16",
                                "subnets": [
                                    {
                                        "id": "subnet-pub",
                                        "label": "Public Subnet 10.0.1.0/24",
                                        "services": [
                                            {"label": "Load Balancer\nFlexible 100 Mbps", "type": "load_balancer", "w": 220, "h": 50},
                                            {"label": "Bastion Service", "type": "bastion", "w": 100, "h": 40},
                                        ]
                                    },
                                    ...
                                ],
                                "gateways": [
                                    {"label": "Internet Gateway", "type": "igw"},
                                    {"label": "NAT Gateway", "type": "natgw"},
                                    ...
                                ]
                            }
                        ],
                        "observability": ["Monitoring", "Logging Analytics", ...]
                    }
                ]
            },
            "onprem": {
                "label": "On-Premises Data Center",
                "services": [...]
            },
            "connections": [
                {"from": "subnet-pub", "to": "subnet-app", "type": "standard", "label": "HTTPS"},
                {"from": "adb1", "to": "adb-dr", "type": "adg", "label": "Autonomous Data Guard"},
                ...
            ]
        }
        """
        gen = cls()
        
        tenancy_spec = spec.get("tenancy", {})
        gen.add_tenancy("tenancy", tenancy_spec.get("label", "Oracle Cloud Infrastructure"))
        
        for region in tenancy_spec.get("regions", []):
            is_primary = region.get("primary", False)
            rx = 15 if is_primary else 1195
            rw = 1140 if is_primary else 640
            rh = 670 if is_primary else 480
            
            gen.add_region(region["id"], f"Region — {region['label']}", 
                          "tenancy", rx, 30, rw, rh)
            
            for vcn in region.get("vcns", []):
                gen.add_vcn(vcn["id"], f"VCN {vcn['label']}", 
                           region["id"], 15, 30, rw - 30, rh - 70)
                
                # Auto-layout subnets
                sx = 15
                for i, subnet in enumerate(vcn.get("subnets", [])):
                    sw = subnet.get("w", 280)
                    sh = subnet.get("h", 420)
                    gen.add_subnet(subnet["id"], subnet["label"],
                                  vcn["id"], sx, 30, sw, sh)
                    
                    # Auto-layout services inside subnet
                    sy = 35
                    for svc in subnet.get("services", []):
                        svc_id = svc.get("id", gen._next_id())
                        svc_w = svc.get("w", sw - 50)
                        svc_h = svc.get("h", 45)
                        label = svc["label"].replace("\\n", "\n")
                        gen.add_service(svc_id, label, svc["type"],
                                       subnet["id"], 25, sy, svc_w, svc_h,
                                       font_size=svc.get("fontSize"))
                        sy += svc_h + 10
                    
                    sx += sw + 15
                
                # Gateways row
                gx = 20
                gy = rh - 140
                for gw in vcn.get("gateways", []):
                    gw_id = gw.get("id", gen._next_id())
                    gw_w = gw.get("w", 95)
                    label = gw["label"].replace("\\n", "\n")
                    gen.add_service(gw_id, label, gw["type"],
                                   vcn["id"], gx, gy, gw_w, 38)
                    gx += gw_w + 10
            
            # Observability row
            if region.get("observability"):
                ox = 25
                oy = rh - 32
                for obs_label in region["observability"]:
                    obs_id = gen._next_id()
                    gen.add_obs_bar(obs_id, obs_label, region["id"], ox, oy, 80, 22)
                    ox += 88
        
        # On-premises
        if spec.get("onprem"):
            op = spec["onprem"]
            gen.add_onprem("onprem", op.get("label", "On-Premises Data Center"))
            opx = 25
            for svc in op.get("services", []):
                svc_id = svc.get("id", gen._next_id())
                svc_w = svc.get("w", 180)
                svc_h = svc.get("h", 60)
                label = svc["label"].replace("\\n", "\n")
                gen.add_service(svc_id, label, svc["type"],
                               "onprem", opx, 35, svc_w, svc_h)
                opx += svc_w + 15
        
        # Connections
        for conn in spec.get("connections", []):
            conn_id = conn.get("id", gen._next_id())
            gen.add_connection(conn_id, conn.get("label"), conn["type"],
                              conn["from"], conn["to"],
                              waypoints=conn.get("waypoints"))
        
        # Title
        if spec.get("title"):
            gen.add_title(spec["title"])
        
        return gen


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Generate OCI architecture .drawio diagrams")
    parser.add_argument("--spec", help="YAML spec file", required=True)
    parser.add_argument("--output", help="Output .drawio file", default="architecture.drawio")
    args = parser.parse_args()
    
    with open(args.spec, 'r') as f:
        spec = yaml.safe_load(f)
    
    gen = OCIDiagramGenerator.from_spec(spec)
    gen.save(args.output)
    print(f"Generated {args.output}")


if __name__ == "__main__":
    main()
```

---

## Example: Using the Generator Programmatically

```python
gen = OCIDiagramGenerator()

# Build the hierarchy
gen.add_tenancy("tenancy", "Oracle Cloud Infrastructure")
gen.add_region("r1", "Region — US East (Ashburn)", "tenancy", 15, 30, 1140, 670)
gen.add_vcn("vcn1", "VCN prod-vcn 10.0.0.0/16", "r1", 15, 30, 1110, 600)

# Subnets
gen.add_subnet("sub-pub", "Public Subnet 10.0.1.0/24", "vcn1", 15, 30, 270, 340)
gen.add_subnet("sub-app", "Private Subnet — App Tier 10.0.10.0/24", "vcn1", 305, 30, 340, 450)
gen.add_subnet("sub-db", "Private Subnet — Data Tier 10.0.20.0/24", "vcn1", 665, 30, 425, 450)

# Services
gen.add_service("lb", "Load Balancer\nFlexible 100 Mbps", "load_balancer", "sub-pub", 25, 35, 220, 55)
gen.add_service("adb1", "Autonomous Database\nADB-S OLTP\n8 OCPU / 2 TB", "adb", "sub-db", 25, 35, 375, 85, font_size=9)
gen.add_service("drg", "Dynamic Routing\nGateway (DRG)", "drg", "vcn1", 320, 505, 120, 38)

# Connections
gen.add_connection("c1", "SQL*Net + TAC", "db", "sub-app", "sub-db")
gen.add_connection("c2", "Autonomous Data Guard", "adg", "sub-db", "sub-dr-db")
gen.add_connection("c3", "FastConnect 10 Gbps", "fastconnect", "onprem", "vcn1")

gen.add_title("Customer X — Oracle Migration to OCI ADB-S\nHA/DR Architecture — March 2026")
gen.save("architecture.drawio")
```

---

## Example: YAML Spec Format

```yaml
title: "Customer X — Oracle Migration to OCI ADB-S\nHA/DR Architecture — March 2026"

tenancy:
  label: "Oracle Cloud Infrastructure"
  regions:
    - id: region1
      label: "US East (Ashburn)"
      primary: true
      vcns:
        - id: vcn1
          label: "prod-vcn 10.0.0.0/16"
          subnets:
            - id: sub-pub
              label: "Public Subnet 10.0.1.0/24"
              w: 270
              h: 200
              services:
                - {label: "Load Balancer\nFlexible 100 Mbps", type: load_balancer, w: 220, h: 55}
                - {label: "Bastion Service", type: bastion, w: 100, h: 40}
                - {label: "API Gateway", type: apigw, w: 100, h: 40}
            
            - id: sub-app
              label: "Private Subnet — App Tier 10.0.10.0/24"
              w: 340
              h: 350
              services:
                - {id: vm1, label: "App Server 1\nE5.Flex 4 OCPU / 64 GB", type: vm, w: 150, h: 55}
                - {id: vm2, label: "App Server 2\nE5.Flex 4 OCPU / 64 GB", type: vm, w: 150, h: 55}
                - {id: oke, label: "OKE Cluster\nKubernetes v1.30\n3 Workers E5.Flex 8 OCPU", type: oke, w: 310, h: 50}
                - {label: "OCI Functions (Serverless)", type: functions, w: 145, h: 40}
                - {label: "OCI Streaming (Kafka API)", type: streaming, w: 145, h: 40}
                - {label: "OCI Queue", type: queue, w: 145, h: 35}
                - {label: "Oracle Integration Cloud", type: oic, w: 145, h: 35}

            - id: sub-db
              label: "Private Subnet — Data Tier 10.0.20.0/24"
              w: 425
              h: 400
              services:
                - {id: adb1, label: "Autonomous Database\nServerless (ADB-S) OLTP\n8 OCPU (auto-scale 16) / 2 TB — BYOL", type: adb, w: 375, h: 85, fontSize: 9}
                - {id: adb2, label: "ADB-S Data Warehouse\n4 OCPU / 1 TB", type: adb, w: 375, h: 50}
                - {label: "OCI NoSQL On-Demand", type: nosql, w: 175, h: 40}
                - {label: "OCI Cache with Redis", type: cache, w: 175, h: 40}
                - {label: "Data Safe — Audit Masking VPD", type: data_safe, w: 375, h: 30}
                - {label: "OCI Vault — Customer-Managed Keys", type: vault, w: 375, h: 30}

          gateways:
            - {label: "Internet\nGateway", type: igw, w: 90}
            - {label: "NAT\nGateway", type: natgw, w: 90}
            - {label: "Service\nGateway", type: sgw, w: 90}
            - {id: drg1, label: "Dynamic Routing\nGateway (DRG)", type: drg, w: 120}
            - {label: "Web Application\nFirewall (WAF)", type: waf, w: 120}
      
      observability:
        - Monitoring
        - Logging Analytics
        - DB Management
        - Ops Insights
        - Notifications
        - Events Service

    - id: region2
      label: "US West (Phoenix) — DR"
      primary: false
      vcns:
        - id: vcn-dr
          label: "dr-vcn 10.1.0.0/16"
          subnets:
            - id: sub-dr-db
              label: "Private Subnet — DR Data Tier 10.1.20.0/24"
              w: 580
              h: 150
              services:
                - {id: adb-dr, label: "ADB-S Standby\nCross-Region ADG\n8 OCPU / 2 TB", type: adb, w: 250, h: 70, fontSize: 9}
                - {label: "Refreshable Clone\n(Reporting) 4 OCPU / 2 TB", type: adb, w: 250, h: 70, fontSize: 9}
            - id: sub-dr-app
              label: "Private Subnet — DR App Tier 10.1.10.0/24"
              w: 580
              h: 100
              services:
                - {label: "App Servers (Dormant)\nProvisioned via Terraform on DR activation", type: dormant, w: 280, h: 45}
          gateways: []

onprem:
  label: "On-Premises Data Center"
  services:
    - {id: src-db, label: "Source Database\nOracle 19c EE\nExadata X8M\n2 RAC / 4 TB", type: exadata, w: 190, h: 70}
    - {label: "Application Servers\nWebLogic 14c — 6x BM", type: vm, w: 170, h: 55}
    - {label: "MQ Series\nLegacy Queuing", type: legacy, w: 140, h: 50}

connections:
  - {from: sub-pub, to: sub-app, type: standard, label: "HTTPS"}
  - {from: sub-app, to: sub-db, type: db, label: "SQL*Net + TAC"}
  - {from: sub-db, to: sub-dr-db, type: adg, label: "Autonomous Data Guard — Async"}
  - {from: onprem, to: drg1, type: fastconnect, label: "FastConnect 10 Gbps"}
  - {from: src-db, to: adb1, type: migration, label: "OCI DMS + ZDM", waypoints: [[350, 820], [950, 820]]}
```

---

## Design Rules Summary

1. **VCN/Subnet borders are ALWAYS dashed burnt orange `#AE562C`** — this is the signature
2. VCN `strokeWidth=2`, Subnet `strokeWidth=1`
3. Region is the ONLY container with solid fill (`#F5F4F2`)
4. Service blocks: solid fill, NO stroke, white text
5. Text is NEVER pure black — always `#312D2A`
6. Font is Oracle Sans
7. Connectors use `#706E6F` gray by default
8. ADG/replication arrows: dashed burnt orange
9. FastConnect: solid purple, bidirectional
10. Database services = copper, Integration = purple, everything else = teal

---

## Future: Embedded OCI Stencil Icons

The toolkit `OCI Library.xml` contains 224 multi-layer Visio stencils encoded as `shape=stencil(base64+zlib)`. To embed them directly (no library import needed), each stencil needs:

1. Decode: `base64 → zlib inflate → URL decode → mxGraphModel XML`
2. Extract child mxCells (each icon has 2-27 layers)
3. Remap all cell IDs to unique prefixes
4. Remap parent references to maintain hierarchy
5. Scale all geometry coordinates
6. Wrap in a group cell positioned at the desired location

This is a dedicated Python module (`stencil_embedder.py`) — the multi-layer parent-child hierarchy resolution is complex because stencils reference internal parent cells that must be correctly mapped into the destination diagram's cell tree.

Until the embedder is built, the generator uses colored placeholder rectangles matching the official color per service category. Architects can optionally load `OCI Library.xml` and drag official icons onto the placeholders.


---

## ░░░ SECTION 4: OUTPUT FORMAT — slide deck + alternatives ░░░

# OCI DEAL ACCELERATOR — Output Format Specification

## Default Output: Slide Deck (.pptx)

The Deal Accelerator produces a **slide deck** as its primary deliverable. This is what the architect presents in the second meeting with the customer. It must be professional, concise, and ready to present with minimal editing.

The architect can optionally request alternative or additional outputs.

---

## Output Selection

When producing outputs, the architect can specify:

```
Output: deck              ← default, just the slide deck
Output: deck + drawio     ← deck + editable diagram
Output: deck + doc        ← deck + detailed technical document
Output: deck + xlsx       ← deck + detailed cost spreadsheet  
Output: full              ← everything: deck + drawio + doc + xlsx
Output: doc only          ← technical document without deck
```

If the architect doesn't specify, produce the **deck only**.

---

## Slide Deck Structure (10-12 slides)

### Slide 1: Title
- Customer name + project name
- "Architecture Proposal — [Month Year]"
- Architect name / consulting firm
- Subtitle: "Prepared with OCI Deal Accelerator"
- **Style**: Dark background (#312D2A), white text, minimal

### Slide 2: Engagement Summary
- Why we're here (1-2 sentences from decision_drivers)
- Current state summary (bullet list: X databases, Y servers, Z pain points)
- Target state (1 sentence: "Migrate to OCI ADB-S with HA/DR")
- Timeline: "X month migration, Y target go-live"
- **Style**: Light background, left-aligned text, no diagram

### Slide 3: Architecture Overview (THE diagram)
- Full architecture diagram (exported from .drawio or generated inline)
- Numbered flow steps (1→2→3...) showing the request path
- Minimal text — the diagram speaks
- **Style**: White background, diagram fills 85% of slide, small title at top

### Slide 4: Architecture Decisions
- 4-6 key decisions in a two-column table:
  | Decision | Rationale |
  |----------|-----------|
  | ADB-S over ExaCS | Variable workload, no DBA team, auto-scaling needed |
  | Cross-region ADG | PCI compliance requires geo-redundant DR |
  | FastConnect over VPN | Low-latency requirement for hybrid period |
  | OKE over VMs for microservices | Team moving to containers, auto-scaling per service |
- Each row: decision + 1-line rationale
- **Style**: Clean table, no heavy borders, alternating row shading

### Slide 5: High Availability & Disaster Recovery
- HA/DR topology diagram (simplified — primary region + DR region only)
- Table with RTO/RPO per tier:
  | Tier | Technology | RTO | RPO |
  |------|-----------|-----|-----|
  | Database | TAC + Local ADG | ~0 perceived | 0 |
  | Database DR | Cross-region ADG | minutes | seconds |
  | Application | Auto-scaling + OKE | seconds | N/A |
  | App DR | Terraform on-demand | 15-30 min | N/A |
- **Style**: Split layout — small diagram left, table right

### Slide 6: Security & Compliance
- Compliance requirements met (PCI, HIPAA, etc.) with checkmarks
- Key security controls in visual layout:
  - Identity: IAM + MFA + Federation
  - Network: Private subnets + NSGs + WAF + Service Gateway
  - Database: TDE + Vault + Data Safe + Private Endpoints
  - Monitoring: Cloud Guard + Audit + VCN Flow Logs
- **Style**: Icon grid or checklist visual, green checkmarks

### Slide 7: Cost Estimate
- Summary table:
  | Component | Monthly (PAYG) | Monthly (BYOL) | Notes |
  |-----------|---------------|----------------|-------|
  | ADB-S Primary (8 OCPU) | $X,XXX | $X,XXX | Auto-scale to 16 |
  | ADB-S Standby (ADG) | $X,XXX | $X,XXX | Same region |
  | ADB-S DR (Cross-region) | $X,XXX | $X,XXX | Phoenix |
  | Compute (2x E5.Flex) | $XXX | $XXX | 4 OCPU each |
  | OKE Cluster | $X,XXX | — | 3 workers |
  | Networking (FastConnect) | $XXX | — | 10 Gbps |
  | Storage & Other | $XXX | — | Object + Block |
  | **Total Monthly** | **$XX,XXX** | **$XX,XXX** | |
  | **Total Annual** | **$XXX,XXX** | **$XXX,XXX** | |
- Assumptions listed below table (3-4 bullet points)
- If BYOL applies, show both columns; otherwise single column
- **Style**: Clean table with bold totals, assumptions in smaller font below

### Slide 8: Cost Comparison (optional — if competitive situation)
- Side-by-side: Current State vs. OCI (PAYG) vs. OCI (BYOL)
- Or: OCI vs. AWS equivalent
- Bar chart or simple table
- TCO over 1-year and 3-year
- **Style**: Chart or comparison table, highlight savings in green

### Slide 9: Migration Approach
- Phased timeline (horizontal Gantt-like):
  - Phase 1: Assessment & Prep (weeks 1-4)
  - Phase 2: Infrastructure Setup (weeks 3-6)
  - Phase 3: Migration & Testing (weeks 5-10)
  - Phase 4: Cutover & Validation (weeks 9-12)
- Key milestones marked
- Migration tools: DMS, ZDM, Data Pump, GoldenGate (as applicable)
- Downtime approach: "Zero downtime via ZDM" or "Weekend cutover window"
- **Style**: Timeline visual, colored phases, milestone diamonds

### Slide 10: Risk Register
- Top 5-6 risks in table:
  | Risk | Severity | Mitigation |
  |------|----------|------------|
  | Application compatibility with ADB-S | MEDIUM | Run assessment tool, pilot with non-prod |
  | TAC replay failures for non-replayable ops | LOW | Audit code, wrap UTL_HTTP calls |
  | DEP provisioning delay | MEDIUM | Request early, plan for 2-3 week lead time |
  | Team cloud skill gap | MEDIUM | OCI training + Oracle support engagement |
- **Style**: Table with color-coded severity (red/orange/yellow)

### Slide 11: Well-Architected Scorecard
- Visual scorecard with 5 pillars:
  - Security & Compliance: ✅ PASS (18/20 checks)
  - Reliability & Resilience: ⚠️ PASS WITH RECOMMENDATIONS (12/15)
  - Performance & Cost: ✅ PASS (10/10)
  - Operational Efficiency: ❌ GAPS IDENTIFIED (6/10)
  - Distributed Cloud: ➖ N/A
- Top 2-3 recommendations listed below
- Reference: "Validated against Oracle Well-Architected Framework"
- **Style**: Horizontal bar or pill indicators, traffic-light colors

### Slide 12: Next Steps
- 3-5 concrete next steps:
  1. "Review and approve architecture design — [date]"
  2. "Provision OCI tenancy and request DEP — [date]"
  3. "Run application assessment tool — [date]"
  4. "Begin Phase 1: Infrastructure setup — [date]"
  5. "Schedule weekly architecture review cadence"
- Contact information
- **Style**: Numbered list, clean, forward-looking

---

## Slide Design Standards

### Colors (matching OCI brand, NOT generic corporate)
- **Background**: White (#FFFFFF) for content slides, dark (#312D2A) for title/section breaks
- **Primary accent**: OCI Teal (#2D5967) for headers, borders, highlights
- **Secondary accent**: Copper (#AA643B) for database-related content
- **Tertiary accent**: Purple (#804998) for integration-related content
- **Text**: Charcoal (#312D2A) — never pure black
- **Success**: Muted green (#5E9624)
- **Warning**: Burnt orange (#AE562C)
- **Error/Risk**: Oracle red (#C74634)
- **Table alternating rows**: #F5F4F2

### Typography
- **Titles**: 24-28pt, bold, #312D2A
- **Subtitles**: 16-18pt, regular, #70665E
- **Body**: 12-14pt, regular, #312D2A
- **Table headers**: 11pt, bold, white on #2D5967
- **Table body**: 10-11pt, regular, #312D2A
- **Footnotes/assumptions**: 8-9pt, italic, #70665E
- **Font**: Segoe UI (widely available, close to Oracle Sans)

### Layout
- **Margins**: Consistent 0.5" on all sides
- **Title position**: Top-left, consistent across all slides
- **Content area**: Below title bar, 85% of slide height
- **Footer**: Slide number bottom-right, customer name bottom-left (optional)
- **No decorative elements**: No gradients, no clip art, no stock photos. Clean and technical.

---

## Alternative Outputs (when requested)

### Technical Document (.docx)

When the architect requests `deck + doc` or `doc only`:

Sections:
1. Executive Summary (1 page)
2. Current State Assessment (from workload profile)
3. Target Architecture (detailed, with diagram)
4. Architecture Decision Records (full ADRs with alternatives considered)
5. Service Configuration Details (per-service config: OCPU, storage, shapes, features)
6. Network Architecture (VCN design, CIDR, security groups, connectivity)
7. Security Architecture (IAM, encryption, Data Safe, compliance mapping)
8. High Availability & Disaster Recovery (detailed HA/DR design)
9. Cost Estimate (detailed breakdown with all assumptions)
10. Migration Plan (phased, with dependencies and critical path)
11. Risk Register (complete, with probability and impact scoring)
12. Well-Architected Assessment (full 5-pillar report)
13. Appendix: Sizing Calculations, Competitive Comparison

**Style**: Professional but not heavy. No markdown headers in body. Numbered sections. Tables for structured data. Diagrams embedded. 15-25 pages typical.

### Cost Spreadsheet (.xlsx)

When the architect requests `deck + xlsx`:

Tabs:
1. **Summary**: Monthly and annual totals, PAYG vs BYOL vs Reserved
2. **Compute**: Per-instance breakdown (shape, OCPU, memory, hours/month, cost)
3. **Database**: Per-database breakdown (OCPU, storage, ADG, auto-scaling estimate)
4. **Networking**: FastConnect, LB, bandwidth, NAT Gateway
5. **Storage**: Block, Object, File — by tier and size
6. **Other**: Monitoring, Vault, Data Safe, support
7. **Assumptions**: All assumptions in one place
8. **Comparison** (optional): vs. current state or vs. competitor

**Style**: Clean, formulas visible, no hidden columns. Color coding matches the deck.

### Architecture Diagram (.drawio)

When the architect requests `deck + drawio`:

The `.drawio` file with official OCI toolkit styles, as specified in the diagram generator. The architect can:
- Open in draw.io and refine positioning
- Load OCI Library.xml for official stencil icons
- Export to PNG/SVG for embedding in other documents
- Share with technical reviewers

---

## Data Flow: Architecture Composition → Outputs

```
Phase 2: Architecture Composition
         │
         ▼
   Structured Data (internal)
   ┌──────────────────────┐
   │ architecture_data:   │
   │   services[]         │
   │   connections[]      │
   │   decisions[]        │
   │   costs{}            │
   │   risks[]            │
   │   wa_scorecard{}     │
   │   migration_plan{}   │
   │   competitive{}      │
   └──────────────────────┘
         │
         ├──→ Slide Deck Renderer  → architecture-proposal.pptx  (DEFAULT)
         ├──→ Diagram Generator    → architecture.drawio          (optional)
         ├──→ Document Renderer    → architecture-detail.docx     (optional)
         └──→ Spreadsheet Renderer → cost-estimate.xlsx           (optional)
```

The skill always produces the structured data internally. The output format selection determines which renderers run.

---

## Prompt Integration

Add this to the SKILL.md output section:

```
When producing outputs, default to a **slide deck (.pptx)** unless the architect 
requests otherwise. The architect can specify:

- "deck" (default) — 10-12 slide presentation
- "deck + drawio" — presentation + editable diagram
- "deck + doc" — presentation + detailed technical document
- "deck + xlsx" — presentation + cost spreadsheet
- "full" — all of the above
- "doc only" — technical document without slides

The deck follows the standard 12-slide structure:
Title → Summary → Architecture Diagram → Decisions → HA/DR → Security → 
Cost → Cost Comparison (optional) → Migration → Risks → WA Scorecard → Next Steps

Use OCI brand colors (teal #2D5967, copper #AA643B, purple #804998) throughout.
Never use generic corporate templates.
```


---

## ░░░ SECTION 5: WELL-ARCHITECTED FRAMEWORK — 5-pillar validation ░░░

# OCI WELL-ARCHITECTED FRAMEWORK INTEGRATION — Addendum to Deal Accelerator Prompt

## Source

Oracle's official Well-Architected Framework for OCI:
https://docs.oracle.com/en/solutions/oci-best-practices/index.html

This is NOT a nice-to-have. This is the **authoritative checklist** that Oracle Solutions Architects use to validate architectures. The Deal Accelerator must integrate this as a validation layer on every architecture it produces.

## How It Changes the Deal Accelerator Flow

The existing flow is:

```
Discovery → Workload Profile → Architecture Composition → Outputs
```

The updated flow adds a **Well-Architected Validation** phase:

```
Discovery → Workload Profile → Architecture Composition → WA Validation → Outputs
```

The WA Validation phase runs the composed architecture through the 5 pillars and flags gaps, risks, and recommendations. This produces a **Well-Architected Scorecard** as an additional output alongside ADRs, cost estimates, and diagrams.

## The 5 Pillars as Validation Checklists

### Pillar 1: Security and Compliance

Source: https://docs.oracle.com/en/solutions/oci-best-practices/effective-strategies-security-and-compliance1.html

The Deal Accelerator must validate:

**Identity & Access:**
- [ ] IAM policies follow least-privilege (not using broad `manage all-resources`)
- [ ] MFA enabled for all human users
- [ ] Tenancy admin account NOT used for day-to-day operations
- [ ] Service accounts use instance principals or resource principals, not stored credentials
- [ ] Multiple Identity Domains if multi-tenant or multi-environment
- [ ] Federation configured with customer's IdP (AD, Okta, SAML)

**Resource Isolation:**
- [ ] Compartments organized by workload/environment (not flat)
- [ ] Tags defined for cost tracking, environment, owner
- [ ] Security Zones enabled for production compartments
- [ ] Cross-resource access uses resource principals, not user credentials

**Database Security:**
- [ ] Databases in private subnets only
- [ ] TDE enabled with customer-managed keys (OCI Vault)
- [ ] Key rotation < 90 days
- [ ] Data Safe enabled (audit, masking, VPD assessment)
- [ ] Private endpoints for Autonomous Database
- [ ] DELETE permissions restricted to minimal users/groups
- [ ] Database security patches applied (CPU/PSU)

**Data Protection:**
- [ ] Encryption at rest for all storage (Block, File, Object)
- [ ] Keys managed in OCI Vault (not Oracle-managed)
- [ ] Object Storage buckets not publicly accessible
- [ ] Retention rules on critical buckets

**Network Security:**
- [ ] NSGs preferred over Security Lists for fine-grained control
- [ ] Default security list modified (no SSH from 0.0.0.0/0)
- [ ] WAF on all internet-facing endpoints
- [ ] Service Gateway for OCI service access (no internet traversal)
- [ ] Network Firewall for hub VCN if required
- [ ] Load Balancers with TLS termination
- [ ] Zero Trust Packet Routing considered for sensitive workloads

**Monitoring & Audit:**
- [ ] Cloud Guard enabled with detector and responder recipes
- [ ] OCI Audit service enabled
- [ ] VCN Flow Logs enabled
- [ ] Vulnerability Scanning enabled
- [ ] Logs aggregated to SIEM if enterprise requirement

KB location: `kb/well-architected/security-compliance.yaml`

### Pillar 2: Reliability and Resilience

Source: https://docs.oracle.com/en/solutions/oci-best-practices/reliable-and-resilient-cloud-topology-practices1.html

The Deal Accelerator must validate:

**Scalability:**
- [ ] Auto-scaling configured for variable workloads
- [ ] Service limits reviewed and increased where needed
- [ ] Capacity reservations for critical workloads

**Fault-Tolerant Networking:**
- [ ] Redundant FastConnect circuits (2 virtual circuits, different physical paths)
- [ ] VPN as backup if FastConnect is primary
- [ ] DRG with redundant tunnels
- [ ] Load Balancer health checks configured
- [ ] Multiple ADs or FDs used for compute placement

**Data Backup:**
- [ ] Automated backups enabled for all databases
- [ ] Backup retention policy defined and documented
- [ ] Block Volume backups scheduled
- [ ] Cross-region backup copy for critical data
- [ ] Boot volume backups for compute instances

**Data Replication:**
- [ ] Data Guard (or ADG for ADB) configured for HA databases
- [ ] RPO/RTO documented and validated with actual testing
- [ ] Cross-region replication for Object Storage

**Disaster Recovery:**
- [ ] DR region identified and provisioned
- [ ] DR architecture documented with switchover/failover procedures
- [ ] DR drill schedule defined (quarterly minimum)
- [ ] DNS failover or traffic management configured
- [ ] Application tier DR strategy (pre-provisioned, Terraform-on-demand, or pilot light)

KB location: `kb/well-architected/reliability-resilience.yaml`

### Pillar 3: Performance and Cost Optimization

Source: https://docs.oracle.com/en/solutions/oci-best-practices/index.html (Performance pillar)

The Deal Accelerator must validate:

**Compute Sizing:**
- [ ] Shapes selected based on workload profile (not over-provisioned)
- [ ] Flex shapes used where possible (pay for what you use)
- [ ] Burstable instances considered for dev/test
- [ ] ARM (Ampere) considered for compatible workloads (better price/performance)

**Storage Strategy:**
- [ ] Storage tier matches access pattern (Standard, Infrequent Access, Archive)
- [ ] Block Volume performance tier matches IOPS needs
- [ ] Auto-tiering enabled for Object Storage where applicable

**Network Tuning:**
- [ ] Bandwidth provisioned matches actual needs (not over-provisioned FastConnect)
- [ ] Network Load Balancer vs. Flexible Load Balancer decision justified

**Cost Management:**
- [ ] BYOL vs. License Included analysis done
- [ ] Reserved capacity considered for stable workloads (1-year or 3-year)
- [ ] Budgets and cost alerts configured per compartment
- [ ] Tagging strategy enables cost attribution
- [ ] Auto-scaling min/max configured to prevent runaway costs
- [ ] Non-production environments use smaller shapes or are scheduled off

KB location: `kb/well-architected/performance-cost.yaml`

### Pillar 4: Operational Efficiency

Source: https://docs.oracle.com/en/solutions/oci-best-practices/best-practices-operating-cloud-deployments-efficiency.html

The Deal Accelerator must validate:

**Deployment Strategy:**
- [ ] Infrastructure as Code (Terraform, Resource Manager) for all resources
- [ ] CI/CD pipeline defined for application deployment
- [ ] Blue/green or canary deployment strategy for production changes
- [ ] Environment parity (dev/staging/prod use same IaC templates)

**Workload Monitoring:**
- [ ] OCI Monitoring alarms configured for key metrics
- [ ] Custom metrics for application-specific KPIs
- [ ] Logging Analytics for centralized log analysis
- [ ] APM configured for application tracing
- [ ] Database Management enabled for DB performance monitoring
- [ ] Ops Insights for capacity planning

**OS Management:**
- [ ] OS Management Hub for patch management
- [ ] Automated patching schedule for compute instances
- [ ] Vulnerability remediation SLA defined

**Operations Support:**
- [ ] Support plan level appropriate for workload criticality
- [ ] Notification topics configured for operational events
- [ ] Runbooks documented for common operational procedures
- [ ] OCI Events + Functions for automated remediation

KB location: `kb/well-architected/operational-efficiency.yaml`

### Pillar 5: Distributed Cloud

Source: https://docs.oracle.com/en/solutions/oci-best-practices/effective-strategies-distributed-cloud-implementation1.html

The Deal Accelerator must validate (when applicable):

**Deployment Strategy:**
- [ ] Appropriate deployment model selected (public, dedicated, hybrid, multicloud)
- [ ] Data residency requirements mapped to region selection
- [ ] Sovereign Cloud or Dedicated Region considered if required

**Integration Across Environments:**
- [ ] Consistent IAM across all locations
- [ ] Data synchronization strategy between sites
- [ ] Network connectivity between environments (FastConnect, VPN, DRG)

**Compliance & Sovereignty:**
- [ ] Regional data residency laws addressed
- [ ] Encryption key locality requirements met
- [ ] Audit trail spans all environments

**Unified Operations:**
- [ ] Single pane of glass monitoring across environments
- [ ] IaC consistency across all deployment targets
- [ ] Feedback loop from operations to design

KB location: `kb/well-architected/distributed-cloud.yaml`

## Well-Architected Scorecard (New Output)

The Deal Accelerator adds a **WA Scorecard** to its outputs:

```yaml
well_architected_scorecard:
  overall_status: "PASS_WITH_RECOMMENDATIONS"  # PASS, PASS_WITH_RECOMMENDATIONS, GAPS_IDENTIFIED

  pillars:
    security_compliance:
      status: "PASS"
      checks_passed: 18
      checks_total: 20
      gaps:
        - area: "Network Security"
          finding: "No Network Firewall specified for hub VCN"
          severity: "LOW"
          recommendation: "Consider OCI Network Firewall if deep packet inspection required"
          wa_reference: "ensure-secure-network-access1.html"

    reliability_resilience:
      status: "PASS_WITH_RECOMMENDATIONS"
      checks_passed: 12
      checks_total: 15
      gaps:
        - area: "Disaster Recovery"
          finding: "No DR drill schedule defined"
          severity: "MEDIUM"
          recommendation: "Define quarterly DR drill with automated validation"
          wa_reference: "reliable-and-resilient-cloud-topology-practices1.html"

    performance_cost:
      status: "PASS"
      checks_passed: 10
      checks_total: 10
      gaps: []

    operational_efficiency:
      status: "GAPS_IDENTIFIED"
      checks_passed: 6
      checks_total: 10
      gaps:
        - area: "Deployment Strategy"
          finding: "No IaC strategy specified"
          severity: "HIGH"
          recommendation: "Define Terraform modules for all infrastructure components"
          wa_reference: "best-practices-operating-cloud-deployments-efficiency.html"

    distributed_cloud:
      status: "NOT_APPLICABLE"
      reason: "Single public cloud deployment"
```

## KB Structure Additions

```
kb/
├── well-architected/
│   ├── security-compliance.yaml      # Checklist items from Pillar 1
│   ├── reliability-resilience.yaml   # Checklist items from Pillar 2
│   ├── performance-cost.yaml         # Checklist items from Pillar 3
│   ├── operational-efficiency.yaml   # Checklist items from Pillar 4
│   ├── distributed-cloud.yaml        # Checklist items from Pillar 5
│   ├── landing-zones.yaml            # OCI Landing Zone patterns and templates
│   └── personas.yaml                 # Role-to-pillar mapping for output targeting
```

## How the Validation Works in Practice

When the skill composes an architecture, it walks through each checklist:

1. **Auto-pass**: If the architecture explicitly includes a service/config that satisfies the check → PASS
2. **Auto-flag**: If the architecture is missing a required element for the workload profile → GAP
3. **Conditional**: Some checks only apply if certain conditions are met (e.g., distributed cloud only if multi-region/hybrid)
4. **Severity mapping**:
   - HIGH: Security vulnerability, data loss risk, or compliance violation
   - MEDIUM: Best practice not followed, operational risk
   - LOW: Optimization opportunity, nice-to-have

The scorecard is generated AUTOMATICALLY — the architect doesn't have to answer 50 questions. The skill infers the answers from the composed architecture and the workload profile.

## Why This Matters for the Architect

1. **Credibility**: Walking into a customer meeting with a Well-Architected Scorecard that references Oracle's own framework is powerful. It shows rigor.

2. **Risk mitigation**: If the architecture is missing something, the architect knows before the customer asks. No surprises.

3. **Competitive differentiation**: AWS and Azure have their own Well-Architected reviews. Showing that OCI has one too — and that the architect proactively ran it — levels the playing field.

4. **Speed**: Normally a WA review is a separate engagement that takes days. The Deal Accelerator does it in seconds as part of the architecture generation.

## Integration with Existing Prompt

Add this to the end of **Phase 2: Architecture Composition** in the main Deal Accelerator prompt:

```
After composing the architecture, run it through the OCI Well-Architected Framework
validation (5 pillars). Generate a scorecard with auto-detected gaps and recommendations.
Include the scorecard as a standard output alongside ADRs, cost estimates, and diagrams.

Reference: https://docs.oracle.com/en/solutions/oci-best-practices/index.html

The validation is automatic — infer check results from the composed architecture
and workload profile. Do not ask the architect 50 questions.
```

## Personas Integration

The Well-Architected Framework defines personas (Cloud Architect, Security Architect, Network Architect, etc.). The Deal Accelerator can use these to target its outputs:

- If the audience is a **Cloud Architect**: Emphasize reliability, security, and operational efficiency
- If the audience is a **Security Architect**: Lead with the security scorecard, emphasize Cloud Guard, Data Safe, encryption
- If the audience is an **Enterprise Architect**: Lead with cost optimization, business alignment, distributed cloud
- If the audience is a **Network Architect**: Emphasize VCN design, FastConnect, DRG, NSGs, WAF

This maps to the `decision_drivers.political` field in the workload profile — who is the decision maker and what do they care about?


---

## ░░░ SECTION 6: FEATURE MATRIX + FIELD FINDINGS TRACKER ░░░

# OCI DEAL ACCELERATOR — KB Additions: Feature Matrix & Field Findings

## Context

Add these to the bootstrap prompt (Phase 1) as files 29-32. These are INTERNAL knowledge assets — not for public sharing. They encode real field experience that no documentation captures.

---

## What's Needed

### A. ADB Feature Compatibility Matrix

A structured YAML that maps features to ADB versions and deployment types. Architects need to quickly answer: "Does this customer's workload need Feature X? Is it available in ADB-S 23ai? What about 26ai?"

This is NOT a copy of Oracle docs. It's a field-verified matrix that includes:
- Features that exist but don't work as documented
- Features that exist but have caveats the docs don't mention
- Features that are technically available but Oracle Support says "don't use in production"
- Version-specific bugs or limitations encountered in real engagements

### B. Field Findings Tracker

A log of real issues, limitations, bugs, and surprises encountered during customer engagements. Each entry has: date, client (or anonymized reference), finding, severity, workaround (if any), Oracle SR# (if filed), status (open/resolved/wontfix), and who reported it.

This is the institutional memory that prevents the next architect from hitting the same wall.

---

## Files to Build

### 29. `kb/compatibility/adb-feature-matrix.yaml`

```yaml
# =============================================================================
# ADB FEATURE COMPATIBILITY MATRIX
# =============================================================================
# 
# INTERNAL — DO NOT SHARE EXTERNALLY
#
# This matrix tracks feature availability across ADB versions and deployment 
# types. It is maintained by the field team based on real testing and customer 
# engagements, NOT copied from Oracle documentation.
#
# Status values:
#   GA        — Generally Available, tested, works as expected
#   GA_CAVEAT — Available but with significant caveats (see notes)
#   PREVIEW   — Available as preview/beta, not production-ready
#   LIMITED   — Available with restrictions not obvious from docs
#   NOT_AVAIL — Not available in this combination
#   BROKEN    — Documented as available but does not work (see field_finding ref)
#   UNTESTED  — Not yet verified by the team
#
# To edit: add/modify entries and update last_verified. Keep notes concise.
# =============================================================================

---
last_verified: 2026-03-14
maintained_by: "Field Architecture Team"
---

versions:
  - id: "23ai"
    full_name: "Oracle Database 23ai"
    release_year: 2024
    notes: "First AI-branded release. Major feature additions."
  - id: "26ai"
    full_name: "Oracle Database 26ai"  
    release_year: 2026
    notes: "Latest. Check feature availability — not everything from 23ai carried forward identically."

deployment_types:
  - id: "adb_s"
    name: "ADB-S Serverless"
  - id: "adb_s_ep"
    name: "ADB-S Elastic Pool"
  - id: "adb_d_dep"
    name: "ADB Dedicated Elastic Pool (DEP)"
  - id: "adb_d"
    name: "ADB on Dedicated Exadata"
  - id: "exacs"
    name: "Exadata Cloud Service"
  - id: "dbcs_ee"
    name: "Base DB Service (EE)"

# =============================================================================
# FEATURE MATRIX
# =============================================================================

features:

  # --- Auto Management ---
  - name: "Auto Scaling (OCPU)"
    category: "auto_management"
    matrix:
      adb_s:
        "23ai": { status: "GA_CAVEAT", notes: "Activation takes 2-3 min. Size base for P75. Billing per-second when active." }
        "26ai": { status: "GA_CAVEAT", notes: "Same 2-3 min activation delay persists in 26ai." }
      adb_s_ep:
        "23ai": { status: "GA_CAVEAT", notes: "Scales within pool allocation. Pool itself doesn't auto-scale." }
        "26ai": { status: "GA_CAVEAT", notes: "Same as 23ai." }
      adb_d_dep:
        "23ai": { status: "LIMITED", notes: "Scales within DEP allocation. DEP itself is fixed capacity." }
        "26ai": { status: "UNTESTED" }
      adb_d:
        "23ai": { status: "NOT_AVAIL", notes: "Dedicated infra — manual scaling only." }
      exacs:
        "23ai": { status: "NOT_AVAIL", notes: "Manual OCPU enable/disable." }

  - name: "Auto Indexing"
    category: "auto_management"
    matrix:
      adb_s:
        "23ai": { status: "GA_CAVEAT", notes: "Creates indexes HIDDEN by default. Instantly reversible. DML costing prevents over-indexing. Deduplication with manually created indexes." }
        "26ai": { status: "GA", notes: "Improved in 26ai — better cost model, fewer false positives." }
      adb_s_ep:
        "23ai": { status: "GA_CAVEAT", notes: "Same as ADB-S Serverless." }
      adb_d_dep:
        "23ai": { status: "GA_CAVEAT", notes: "Available but less tested in DEP." }
      adb_d:
        "23ai": { status: "GA", notes: "Fully supported." }
      exacs:
        "23ai": { status: "NOT_AVAIL", notes: "Not an ADB feature. Use manual indexing." }
      dbcs_ee:
        "23ai": { status: "NOT_AVAIL" }

  - name: "Auto Patching"
    category: "auto_management"
    matrix:
      adb_s:
        "23ai": { status: "GA", notes: "Automatic quarterly. No opt-out. Maintenance window configurable but change requires SR." }
        "26ai": { status: "GA", notes: "Same policy." }
      adb_d_dep:
        "23ai": { status: "GA_CAVEAT", notes: "Maintenance window immutable post-DEP creation. Change via SR only. Saturday/Sunday default, other days via SR." }
      exacs:
        "23ai": { status: "GA_CAVEAT", notes: "Customer-managed patching schedule. Must apply within 90 days." }

  # --- High Availability ---
  - name: "Transparent Application Continuity (TAC)"
    category: "ha_dr"
    matrix:
      adb_s:
        "23ai": { status: "GA_CAVEAT", notes: "Zero perceived RTO for app. DB itself ~2 min unavailable during failover. Replay NOT guaranteed with UTL_HTTP, DBMS_PIPE, NOCACHE sequences. Requires JDBC thin driver with TAC config." }
        "26ai": { status: "GA_CAVEAT", notes: "Same limitations persist." }
      adb_s_ep:
        "23ai": { status: "GA_CAVEAT", notes: "Same as Serverless." }
      adb_d:
        "23ai": { status: "GA_CAVEAT", notes: "Same limitations." }
      exacs:
        "23ai": { status: "GA_CAVEAT", notes: "Available with RAC. Same replay limitations." }
      dbcs_ee:
        "23ai": { status: "NOT_AVAIL", notes: "Requires RAC — only in EE-HP or EE-EP." }

  - name: "Autonomous Data Guard (Local)"
    category: "ha_dr"
    matrix:
      adb_s:
        "23ai": { status: "GA", notes: "Synchronous. Same region. Auto-failover ~2 min." }
        "26ai": { status: "GA" }
      adb_d:
        "23ai": { status: "GA" }
      exacs:
        "23ai": { status: "GA", notes: "Standard Data Guard, not 'Autonomous' — manual setup." }

  - name: "Autonomous Data Guard (Cross-Region)"
    category: "ha_dr"
    matrix:
      adb_s:
        "23ai": { status: "GA_CAVEAT", notes: "Asynchronous only. RPO ≈ seconds. Manual switchover or auto-failover (configurable)." }
        "26ai": { status: "GA_CAVEAT", notes: "Same." }
      adb_d_dep:
        "23ai": { status: "GA_CAVEAT", notes: "ADG must be disabled before joining DEP. Known issue." }
      exacs:
        "23ai": { status: "GA", notes: "Standard cross-region DG. Manual setup." }

  - name: "Refreshable Clone"
    category: "ha_dr"
    matrix:
      adb_s:
        "23ai": { status: "GA_CAVEAT", notes: "Read-only. Auto-refresh frequency configurable. Failed refresh leaves clone AVAILABLE (not DISCONNECTED) — leader monitors lifecycle state, not refresh success. Detection delay = ADG RTO for unplanned." }
        "26ai": { status: "GA_CAVEAT", notes: "Same detection delay issue." }
      adb_d:
        "23ai": { status: "GA" }

  # --- Security ---
  - name: "Virtual Private Database (VPD)"
    category: "security"
    matrix:
      adb_s:
        "23ai": { status: "GA", notes: "Full VPD support including OLS." }
        "26ai": { status: "GA" }
      exacs:
        "23ai": { status: "GA" }
      dbcs_ee:
        "23ai": { status: "GA", notes: "Requires Advanced Security option license." }

  - name: "Private Endpoints"
    category: "security"
    matrix:
      adb_s:
        "23ai": { status: "GA", notes: "Recommended for production. Required for some compliance." }
        "26ai": { status: "GA" }
      adb_d:
        "23ai": { status: "GA", notes: "Default — all ADB-D is private." }
      exacs:
        "23ai": { status: "GA", notes: "Always private subnet." }

  - name: "Data Safe Integration"
    category: "security"
    matrix:
      adb_s:
        "23ai": { status: "GA", notes: "Audit, masking, assessment, SQL Firewall." }
        "26ai": { status: "GA", notes: "Enhanced SQL Firewall in 26ai." }
      exacs:
        "23ai": { status: "GA" }
      dbcs_ee:
        "23ai": { status: "GA_CAVEAT", notes: "Must register DB manually in Data Safe." }

  # --- Developer Features ---
  - name: "Select AI"
    category: "developer"
    matrix:
      adb_s:
        "23ai": { status: "GA", notes: "Natural language → SQL via LLM. Requires AI profile configuration." }
        "26ai": { status: "GA", notes: "Improved accuracy in 26ai." }
      adb_d:
        "23ai": { status: "GA" }
      exacs:
        "23ai": { status: "NOT_AVAIL", notes: "ADB-only feature." }

  - name: "Property Graph / SQL/PGQ"
    category: "developer"
    matrix:
      adb_s:
        "23ai": { status: "GA_CAVEAT", notes: "Node tables + edge tables. Only FK indexes essential. Additional indexes require filter evidence. See Graph DBA Advisor philosophy." }
        "26ai": { status: "GA", notes: "Improved PGQ optimizer in 26ai." }
      exacs:
        "23ai": { status: "GA", notes: "Full graph support with PGQL and SQL/PGQ." }

  - name: "APEX"
    category: "developer"
    matrix:
      adb_s:
        "23ai": { status: "GA", notes: "Built-in. No additional cost." }
        "26ai": { status: "GA" }
      adb_d:
        "23ai": { status: "GA" }
      exacs:
        "23ai": { status: "GA_CAVEAT", notes: "Must install APEX manually." }
      dbcs_ee:
        "23ai": { status: "GA_CAVEAT", notes: "Must install and manage manually." }

  - name: "JSON Relational Duality Views"
    category: "developer"
    matrix:
      adb_s:
        "23ai": { status: "GA", notes: "Major 23ai feature." }
        "26ai": { status: "GA" }
      exacs:
        "23ai": { status: "GA" }
      dbcs_ee:
        "23ai": { status: "GA", notes: "Requires 23ai version." }

  # --- Deployment / Operations ---
  - name: "Elastic Pool Membership"
    category: "operations"
    matrix:
      adb_s_ep:
        "23ai": { status: "GA_CAVEAT", notes: "Billing starts at AVAILABLE. Co-location at next maintenance window. Pool can't auto-scale." }
      adb_d_dep:
        "23ai": { status: "GA_CAVEAT", notes: "Provisioning days-weeks. ADG must be disabled before joining. Maintenance window immutable. Saturday/Sunday default." }

  - name: "Cross-Region Read Offload (ProxySQL/Refreshable Clone)"
    category: "operations"
    matrix:
      adb_s:
        "23ai": { status: "LIMITED", notes: "Architecturally impossible without pre-provisioned Elastic Pool in Region B post-switchover. Mitigation for planned: DBMS_PROXY_SQL.DISABLE_READ_ONLY_OFFLOAD. For unplanned: OCI Events + Functions." }
        "26ai": { status: "UNTESTED", notes: "Same architectural constraint expected to persist." }

  - name: "OCI CLI Management"
    category: "operations"
    matrix:
      adb_s:
        "23ai": { status: "GA_CAVEAT", notes: "--resource-pool-summary works on CLI 3.73+. --autonomous-database-maintenance-window has JSON serialization bug on CLI 3.73.1 AND 3.75.0. Must use Console for maintenance window." }

# =============================================================================
# HOW TO ADD A NEW FEATURE
# =============================================================================
# 1. Add entry under "features:" following the template above
# 2. Fill matrix for every deployment_type + version you've tested
# 3. Mark untested combinations as UNTESTED
# 4. Add field_finding_ref if the entry comes from a specific incident
# 5. Update last_verified date
# 6. Commit with a message: "feat-matrix: added [feature_name]"
```

---

### 30. `kb/field-findings/tracker.yaml`

```yaml
# =============================================================================
# FIELD FINDINGS TRACKER
# =============================================================================
#
# INTERNAL & CONFIDENTIAL — DO NOT SHARE EXTERNALLY
#
# Log of real issues, limitations, bugs, and surprises found during customer
# engagements. Each entry is a finding that another architect should know about
# before hitting the same wall.
#
# Entry format:
#   id:             Unique identifier (FF-YYYYMM-NNN)
#   date:           When discovered (YYYY-MM-DD)
#   reported_by:    Who found it (name or initials)
#   client:         Client name or anonymized reference (e.g., "Financial Services Client A")
#   product:        OCI product/service affected
#   version:        Product version if relevant
#   severity:       CRITICAL / HIGH / MEDIUM / LOW / INFO
#   category:       bug / limitation / undocumented / gotcha / workaround / performance
#   summary:        One-line description
#   detail:         Full description of the finding
#   workaround:     How to work around it (if known)
#   oracle_sr:      Oracle SR number (if filed)
#   status:         open / resolved / wontfix / acknowledged / monitoring
#   resolved_date:  When resolved (if applicable)
#   resolution:     How it was resolved
#   affects_matrix: Feature matrix entry this relates to (if any)
#   tags:           Searchable tags
#
# HOW TO ADD:
# 1. Add entry at the TOP of the findings list (newest first)
# 2. Use next sequential ID: FF-YYYYMM-NNN
# 3. Be specific — include CLI versions, API errors, exact messages
# 4. If you filed an SR, include the number
# 5. Update status when resolved
# =============================================================================

---
last_updated: 2026-03-14
---

findings:

  - id: "FF-202603-001"
    date: "2026-03-10"
    reported_by: "Diego Cabrera"
    client: "Strategic Migration Customer"
    product: "OCI CLI"
    version: "CLI 3.73.1 and 3.75.0"
    severity: "MEDIUM"
    category: "bug"
    summary: "OCI CLI --autonomous-database-maintenance-window has JSON serialization bug"
    detail: |
      The --autonomous-database-maintenance-window parameter fails with a JSON
      serialization error on both OCI CLI 3.73.1 (Cloud Shell) and 3.75.0 
      (VM decabrer-4S46W64). The expected JSON schema is:
      {"dayOfWeek": {"name": "SATURDAY"}, "hourOfDay": 4}
      But the CLI cannot serialize this properly. API returns 403 at create time.
      Tested via dry-run: the 204 response is received but actual creation fails.
    workaround: "Use OCI Console to set maintenance window. Or set post-creation via API directly (not CLI)."
    oracle_sr: ""
    status: "open"
    resolved_date: null
    resolution: null
    affects_matrix: "OCI CLI Management"
    tags: ["cli", "maintenance-window", "adb", "dep", "json", "serialization"]

  - id: "FF-202603-002"
    date: "2026-03-08"
    reported_by: "Diego Cabrera"
    client: "Strategic Migration Customer"
    product: "ADB-S Dedicated Elastic Pool (DEP)"
    version: "23ai"
    severity: "HIGH"
    category: "limitation"
    summary: "ADG must be disabled before joining Dedicated Elastic Pool"
    detail: |
      When attempting to add an ADB-S instance with active Autonomous Data Guard
      to a Dedicated Elastic Pool, the operation fails. ADG must be explicitly 
      disabled before the instance can join the DEP. This is a known issue 
      acknowledged by Oracle but not prominently documented.
      
      Impact: requires a brief HA gap during DEP onboarding. Must coordinate 
      with the customer's change window.
    workaround: "Disable ADG → join DEP → re-enable ADG. Plan for ~15 min HA gap."
    oracle_sr: ""
    status: "acknowledged"
    resolved_date: null
    resolution: null
    affects_matrix: "Elastic Pool Membership"
    tags: ["dep", "adg", "elastic-pool", "ha", "limitation"]

  - id: "FF-202603-003"
    date: "2026-03-05"
    reported_by: "Diego Cabrera"
    client: "Strategic Migration Customer"
    product: "ADB-S Dedicated Elastic Pool (DEP)"
    version: "23ai"
    severity: "MEDIUM"
    category: "undocumented"
    summary: "DEP maintenance window immutable post-creation — change only via SR"
    detail: |
      The maintenance window for a Dedicated Elastic Pool cannot be changed 
      after creation via Console, CLI, or API. The only way to change it is 
      by filing a Service Request with Oracle Support.
      
      Default window is Saturday/Sunday. Other days require specifying at 
      creation time (which itself has the CLI bug — see FF-202603-001) or 
      requesting via SR.
    workaround: "Set desired window at DEP creation time (via Console, not CLI). If missed, file SR."
    oracle_sr: ""
    status: "acknowledged"
    resolved_date: null
    resolution: null
    affects_matrix: "Auto Patching"
    tags: ["dep", "maintenance-window", "immutable", "sr-required"]

  - id: "FF-202603-004"
    date: "2026-03-01"
    reported_by: "Diego Cabrera"
    client: "Strategic Migration Customer"
    product: "ADB-S"
    version: "23ai"
    severity: "MEDIUM"
    category: "gotcha"
    summary: "DEP provisioning takes days to weeks depending on capacity"
    detail: |
      Dedicated Elastic Pool provisioning is NOT instant like ADB-S Serverless.
      It requires physical Exadata infrastructure allocation. Lead time varies
      from 3 days (if capacity available in region) to 2-3 weeks (if capacity
      needs to be provisioned).
      
      Billing starts only at AVAILABLE state, not at request time.
      Co-location of existing ADB-S instances happens at the next maintenance 
      window after joining, not immediately.
    workaround: "Request DEP early in the project timeline. Don't make it a critical-path dependency in week 1."
    oracle_sr: ""
    status: "acknowledged"
    resolved_date: null
    resolution: null
    affects_matrix: "Elastic Pool Membership"
    tags: ["dep", "provisioning", "lead-time", "capacity", "planning"]

  - id: "FF-202603-005"
    date: "2026-02-20"
    reported_by: "Diego Cabrera"
    client: "Strategic Migration Customer"
    product: "ADB-S"
    version: "23ai"
    severity: "LOW"
    category: "gotcha"
    summary: "Refreshable Clone failed refresh leaves clone in AVAILABLE state — detection delay"
    detail: |
      When a Refreshable Clone's auto-refresh fails, the clone remains in 
      AVAILABLE state (not DISCONNECTED). The Elastic Pool leader monitors 
      lifecycle state changes, not refresh success/failure.
      
      This means a failed refresh is NOT immediately detected by the 
      infrastructure. The stale data window equals the ADG RTO for 
      unplanned scenarios.
    workaround: |
      Planned switchovers: DBMS_PROXY_SQL.DISABLE_READ_ONLY_OFFLOAD proactively.
      Unplanned: OCI Events + OCI Function that monitors refresh state and 
      disables read offload automatically. Reduces stale window to ~ADG RTO.
    oracle_sr: ""
    status: "monitoring"
    resolved_date: null
    resolution: null
    affects_matrix: "Refreshable Clone"
    tags: ["refreshable-clone", "stale-reads", "elastic-pool", "detection-delay", "proxysql"]

  - id: "FF-202603-006"
    date: "2026-02-15"
    reported_by: "Diego Cabrera"
    client: "Strategic Migration Customer"
    product: "OCI DMS"
    version: "current"
    severity: "MEDIUM"
    category: "limitation"
    summary: "Bidirectional GoldenGate replication not yet available in DMS"
    detail: |
      OCI Database Migration Service does not support bidirectional GoldenGate 
      replication. This is needed for zero-hard-cutover migration workflows 
      where the customer wants to run both source and target in parallel with 
      data flowing both ways during transition.
      
      Feature request submitted to Oracle DMS PM team. In their pipeline but 
      no committed timeline. Offered beta participation.
    workaround: "Use standalone GoldenGate deployment (not DMS-managed) for bidirectional replication."
    oracle_sr: ""
    status: "open"
    resolved_date: null
    resolution: null
    affects_matrix: null
    tags: ["dms", "goldengate", "bidirectional", "migration", "zero-downtime"]

  - id: "FF-202603-007"
    date: "2026-02-10"
    reported_by: "Diego Cabrera"
    client: "Pepe SRL"
    product: "ADB-S"
    version: "23ai"
    severity: "INFO"
    category: "gotcha"
    summary: "ADB-S Serverless RAC node split threshold at 64 ECPUs"
    detail: |
      ADB-S Serverless runs on 1 RAC node at ≤24 ECPUs and splits to 2 nodes 
      at 64 ECPUs (16 cpu_count each). The gv$instance view only shows nodes 
      where the PDB is open.
      
      This affects connection pooling behavior and session distribution. 
      Applications should use UCP or JDBC connection pool with FAN events 
      to handle the multi-node scenario properly.
    workaround: "Ensure connection pool configuration handles multi-node. Use UCP with FAN."
    oracle_sr: ""
    status: "acknowledged"
    resolved_date: null
    resolution: null
    affects_matrix: null
    tags: ["adb-s", "rac", "ecpu", "node-split", "connection-pooling"]

  # =========================================================================
  # TEMPLATE — Copy this for new entries:
  # =========================================================================
  # - id: "FF-YYYYMM-NNN"
  #   date: "YYYY-MM-DD"
  #   reported_by: ""
  #   client: ""
  #   product: ""
  #   version: ""
  #   severity: ""  # CRITICAL / HIGH / MEDIUM / LOW / INFO
  #   category: ""  # bug / limitation / undocumented / gotcha / workaround / performance
  #   summary: ""
  #   detail: |
  #     
  #   workaround: ""
  #   oracle_sr: ""
  #   status: ""  # open / resolved / wontfix / acknowledged / monitoring
  #   resolved_date: null
  #   resolution: null
  #   affects_matrix: null  # Feature matrix entry name, or null
  #   tags: []
```

---

### 31. `tools/findings_cli.py`

A simple CLI to search and add field findings without editing YAML manually.

**Requirements:**

```python
"""
Field Findings CLI

Usage:
    python tools/findings_cli.py list                          # List all findings
    python tools/findings_cli.py list --severity HIGH          # Filter by severity
    python tools/findings_cli.py list --product "ADB-S"        # Filter by product
    python tools/findings_cli.py list --tag dep                # Filter by tag
    python tools/findings_cli.py list --client "Pepe"          # Filter by client
    python tools/findings_cli.py list --status open            # Filter by status
    python tools/findings_cli.py search "maintenance window"   # Full-text search
    
    python tools/findings_cli.py add                           # Interactive add
    python tools/findings_cli.py add --date 2026-03-14 \
        --reported-by "Diego Cabrera" \
        --client "Client X" \
        --product "ADB-S" \
        --version "23ai" \
        --severity MEDIUM \
        --category gotcha \
        --summary "Description here" \
        --detail "Full detail here" \
        --tags "tag1,tag2,tag3"
    
    python tools/findings_cli.py update FF-202603-001 --status resolved \
        --resolution "Fixed in CLI 3.76.0"
    
    python tools/findings_cli.py stats                         # Summary statistics
"""

# Implementation:
# - Reads/writes kb/field-findings/tracker.yaml
# - Auto-generates next ID (FF-YYYYMM-NNN) based on current date
# - "add" without flags enters interactive mode (prompts for each field)
# - "list" outputs a formatted table to terminal
# - "search" does full-text search across summary, detail, workaround, tags
# - "stats" shows: total findings, by severity, by product, by status, by category
# - Preserves YAML comments and formatting when writing
```

---

### 32. `tools/feature_matrix_cli.py`

CLI to query and update the feature matrix.

**Requirements:**

```python
"""
Feature Matrix CLI

Usage:
    python tools/feature_matrix_cli.py check "Auto Scaling" adb_s 23ai
    # → GA_CAVEAT: Activation takes 2-3 min. Size base for P75.

    python tools/feature_matrix_cli.py check "TAC" exacs 23ai
    # → GA_CAVEAT: Available with RAC. Same replay limitations.

    python tools/feature_matrix_cli.py compare adb_s adb_d 23ai
    # → Table showing feature availability side-by-side

    python tools/feature_matrix_cli.py gaps adb_s 23ai
    # → Lists all features that are NOT_AVAIL, BROKEN, or LIMITED

    python tools/feature_matrix_cli.py update "Auto Scaling" adb_s 26ai --status GA --notes "Improved in 26ai"

    python tools/feature_matrix_cli.py export --format markdown
    # → Exports full matrix as a markdown table (for Confluence/wiki)

    python tools/feature_matrix_cli.py export --format csv
    # → Exports as CSV (for spreadsheet import)
"""

# Implementation:
# - Reads/writes kb/compatibility/adb-feature-matrix.yaml
# - "check" gives a quick answer for a specific feature/deployment/version
# - "compare" shows two deployment types side-by-side for all features
# - "gaps" helps architects identify deal-breakers for a specific deployment type
# - "update" modifies a specific cell in the matrix
# - "export" produces a readable table for sharing in team wiki
# - Color-coded terminal output: GA=green, GA_CAVEAT=yellow, LIMITED=orange,
#   NOT_AVAIL=red, BROKEN=red+bold, UNTESTED=gray
```

---

### 33. `tests/test_feature_matrix.py`

```python
"""Tests for feature matrix and CLI"""

# test_matrix_loads: YAML loads without errors
# test_all_features_have_at_least_one_deployment: no feature with empty matrix
# test_all_statuses_are_valid: every status is in the valid set
# test_check_returns_correct_status: check("Auto Scaling", "adb_s", "23ai") → GA_CAVEAT
# test_check_unknown_feature_returns_error: check("Nonexistent", ...) → clear error
# test_compare_returns_all_features: compare output has one row per feature
# test_gaps_finds_not_available: gaps("dbcs_ee", "23ai") includes features marked NOT_AVAIL
# test_export_markdown_is_valid: markdown export has header row and separator
# test_export_csv_is_valid: CSV export is parseable
```

---

### 34. `tests/test_findings_tracker.py`

```python
"""Tests for field findings tracker and CLI"""

# test_tracker_loads: YAML loads without errors
# test_all_findings_have_required_fields: id, date, reported_by, summary, severity, status
# test_ids_are_unique: no duplicate finding IDs
# test_ids_follow_format: all IDs match FF-YYYYMM-NNN pattern
# test_severities_are_valid: all severities in CRITICAL/HIGH/MEDIUM/LOW/INFO
# test_statuses_are_valid: all statuses in open/resolved/wontfix/acknowledged/monitoring
# test_dates_are_valid: all dates parse as YYYY-MM-DD
# test_search_finds_by_tag: search for "dep" returns findings tagged with dep
# test_search_finds_by_text: search for "maintenance" finds maintenance-related findings
# test_filter_by_severity: filter severity=HIGH returns only HIGH findings
# test_filter_by_client: filter client="Pepe" returns Pepe findings
# test_add_creates_valid_entry: programmatic add produces valid YAML
# test_auto_id_generation: generated ID uses current year-month
# test_stats_counts_correct: stats show correct totals per category
```

---

## Integration with SKILL.md

Add this to the SKILL.md `Phase 2: Architecture Composition` section:

```markdown
### Feature Compatibility Check

Before recommending a specific ADB deployment type + version, check the 
feature matrix at `kb/compatibility/adb-feature-matrix.yaml`. If the 
customer's workload requires features marked LIMITED, BROKEN, or NOT_AVAIL 
for the recommended deployment, flag this in the ADRs and suggest alternatives.

Use `tools/feature_matrix_cli.py gaps <deployment> <version>` to quickly 
identify deal-breakers.

### Field Findings Reference

Before making architecture recommendations, check `kb/field-findings/tracker.yaml`
for known issues with the services you're recommending. Reference relevant 
findings in the Risk Register output with their finding ID (e.g., "See FF-202603-002").
```

---

## Integration with Phase 2 Testing Prompt

Add to `tests/test_integration.py`:

```python
# test_feature_matrix_informs_adr:
#   Compose architecture using ExaCS → check that ADR mentions features 
#   not available in ExaCS (e.g., Auto Indexing, Select AI)

# test_field_findings_inform_risk_register:
#   Compose architecture using DEP → check that risk register references 
#   DEP provisioning lead time and ADG-must-disable finding
```

---

## Build Order

Add to Phase 1 bootstrap prompt after file 28:

29. `kb/compatibility/adb-feature-matrix.yaml`
30. `kb/field-findings/tracker.yaml`
31. `tools/findings_cli.py`
32. `tools/feature_matrix_cli.py`

Add to Phase 2 testing prompt:

33. `tests/test_feature_matrix.py`
34. `tests/test_findings_tracker.py`

---

## Key Principle

These files are the **institutional memory** of the team. Their value grows 
with every engagement. Every architect who hits a wall should add a finding. 
Every version upgrade should trigger a matrix review. The CLIs make this 
frictionless — `python tools/findings_cli.py add` takes 30 seconds, not 
10 minutes of editing YAML by hand.


---

## ░░░ SECTION 7: COLLABORATIVE KB — attribution, governance ░░░

# OCI DEAL ACCELERATOR — Collaborative KB Enhancement

## Add to bootstrap prompt as files 35-37. Updates to existing files noted inline.

---

## 1. Attribution System

Every KB contribution must have a contributor block. This applies to ALL KB files, not just findings.

### Contributor Block Format

```yaml
# On every KB entry (finding, feature matrix update, service file edit, pattern addition):
contributor:
  name: "Diego Cabrera"           # Required — who made the contribution
  team: "Field Architecture"      # Required — team or role
  client: "Acme Corp"            # Optional — anonymize if sensitive (e.g., "Financial Services Client A")
  date: "2026-03-14"             # Required — when the knowledge was captured
  context: "Discovery engagement" # Optional — brief context (PoC, migration, assessment, production issue)
  confidence: "validated"         # Required — see levels below
```

### Confidence Levels

| Level | Meaning | When to use |
|---|---|---|
| `validated` | Tested in a real environment with measurable results | You ran it, measured it, confirmed it works (or doesn't) |
| `observed` | Seen in a customer environment but not formally tested | You saw it happen but didn't isolate and reproduce |
| `reported` | Heard from an internal team, Oracle Support, or docs | Someone told you — you haven't verified yourself |
| `inferred` | Logical conclusion based on related knowledge | You deduced it from architecture principles, not direct evidence |

The skill weighs recommendations differently based on confidence. `validated` findings go into ADRs and risk registers directly. `reported` findings get a caveat: "reported but not independently validated."

---

## 2. Updates to Existing KB Formats

### Field Findings Tracker — Enhanced Entry

Update the entry format in `kb/field-findings/tracker.yaml`:

```yaml
  - id: "FF-202603-008"
    date: "2026-03-14"
    contributor:                    # ← Replaces flat "reported_by"
      name: "Diego Cabrera"
      team: "Field Architecture"
      client: "Vector Search Customer"
      context: "PoC evaluation"
      confidence: "validated"
    product: "ADB-S"
    version: "23ai"
    severity: "HIGH"
    category: "limitation"
    summary: "Distributed HNSW indexes not available at 100M+ scale"
    detail: |
      ...
    workaround: |
      Source: internal DB PM team, contact: [Name]
      ...
    oracle_sr: ""
    status: "acknowledged"
    resolution: null
    affects_matrix: "AI Vector Search (HNSW)"
    tags: ["vector-search", "hnsw"]
    
    # NEW: engagement trail — who else confirmed or added context
    confirmations:
      - name: "Maria García"
        team: "Database Specialists"
        date: "2026-03-20"
        note: "Confirmed same behavior on ADB-D 23ai with 80M vectors. Partitioning workaround also works on Dedicated."
```

### Feature Matrix — Enhanced Cell

Update cell format in `kb/compatibility/adb-feature-matrix.yaml`:

```yaml
      adb_s:
        "23ai":
          status: "GA_CAVEAT"
          notes: "HNSW indexes are node-local on multi-node RAC..."
          contributor:
            name: "Diego Cabrera"
            team: "Field Architecture"
            date: "2026-03-14"
            confidence: "validated"
          field_finding_ref: "FF-202603-008"
```

### Service Files — Change Log

Add a `changelog` section to every service YAML:

```yaml
# kb/services/adb-serverless.yaml
---
last_verified: 2026-03-14
service: Autonomous Database Serverless (ADB-S)
---

# ... service content ...

changelog:
  - date: "2026-03-14"
    contributor: { name: "Diego Cabrera", team: "Field Architecture" }
    change: "Initial creation with sizing rules, gotchas, competitive notes"
  - date: "2026-03-20"
    contributor: { name: "Maria García", team: "Database Specialists" }
    change: "Added Select AI notes for 26ai based on testing at Client B"
  - date: "2026-04-01"
    contributor: { name: "Carlos López", team: "Solution Engineering LATAM" }
    change: "Updated pricing ranges after March 2026 price adjustment"
```

---

## 3. CLI Updates for Attribution

### findings_cli.py — Updated `add` Command

```bash
# Interactive mode now prompts for contributor info
$ python tools/findings_cli.py add

Finding ID: FF-202603-009 (auto-generated)
Your name: Diego Cabrera
Your team: Field Architecture
Client (optional, press Enter to skip): Vector Search Customer
Context (optional): PoC evaluation
Confidence [validated/observed/reported/inferred]: validated
Product: ADB-S
...
```

```bash
# One-liner includes contributor flags
python tools/findings_cli.py add \
    --name "Diego Cabrera" \
    --team "Field Architecture" \
    --client "Vector Search Customer" \
    --context "PoC evaluation" \
    --confidence validated \
    --product "ADB-S" \
    --severity HIGH \
    --summary "Description" \
    --tags "tag1,tag2"
```

### findings_cli.py — New `confirm` Command

When another architect validates an existing finding:

```bash
python tools/findings_cli.py confirm FF-202603-008 \
    --name "Maria García" \
    --team "Database Specialists" \
    --note "Confirmed same behavior on ADB-D 23ai with 80M vectors"
```

This appends to the `confirmations` list on the finding. Multiple confirmations increase trust in the finding.

### feature_matrix_cli.py — Attribution on Updates

```bash
python tools/feature_matrix_cli.py update "AI Vector Search (HNSW)" adb_s 23ai \
    --status GA_CAVEAT \
    --notes "HNSW node-local on multi-node RAC" \
    --name "Diego Cabrera" \
    --team "Field Architecture" \
    --confidence validated
```

### New Command: `kb_cli.py changelog`

Quick way to add a changelog entry to any KB file:

```bash
python tools/kb_cli.py changelog kb/services/adb-serverless.yaml \
    --name "Carlos López" \
    --team "Solution Engineering LATAM" \
    --change "Updated pricing ranges after March 2026 adjustment"
```

---

## 4. Industry Best Practices Applied

Based on current KM trends, here are the improvements to make:

### 4a. Domain Owners

Assign an owner to each KB area. The owner doesn't write everything — they ensure quality and freshness.

```yaml
# config/kb-owners.yaml
domains:
  - area: "kb/services/"
    owner: { name: "Diego Cabrera", team: "Field Architecture" }
    review_cadence: "quarterly"
    
  - area: "kb/patterns/"
    owner: { name: "Diego Cabrera", team: "Field Architecture" }
    review_cadence: "quarterly"
    
  - area: "kb/compatibility/"
    owner: { name: "TBD", team: "Database Specialists" }
    review_cadence: "on Oracle version release + quarterly"
    
  - area: "kb/pricing/"
    owner: { name: "TBD", team: "Solution Engineering" }
    review_cadence: "monthly (pricing changes frequently)"
    
  - area: "kb/competitive/"
    owner: { name: "TBD", team: "Competitive Intelligence" }
    review_cadence: "quarterly + on competitor announcements"
    
  - area: "kb/field-findings/"
    owner: { name: "All", team: "Everyone contributes" }
    review_cadence: "continuous"
    
  - area: "kb/well-architected/"
    owner: { name: "TBD", team: "Cloud Architecture" }
    review_cadence: "on Oracle WA Framework updates"
```

The linter checks for stale areas and notifies the owner.

### 4b. Contribution Leaderboard

Track who contributes to the KB. Not for competition — for visibility and recognition.

```bash
$ python tools/kb_cli.py stats contributors

Contributor              Team                    Findings  Matrix  Services  Total
Diego Cabrera            Field Architecture      7         12      3         22
Maria García             Database Specialists    3         5       1         9
Carlos López             SE LATAM                1         2       2         5

Top contributor this quarter: Diego Cabrera (22 contributions)
Stale areas needing attention: kb/pricing/ (last updated 45 days ago)
```

### 4c. After-Engagement Review (AER)

Borrowed from NASA's "Pause and Learn" and the US Army's "After Action Review". After every customer engagement, the architect answers 3 questions:

```bash
$ python tools/findings_cli.py aer

After-Engagement Review
=======================
Client: Acme Corp
Architect: Diego Cabrera
Date: 2026-03-14

1. What did we learn that the KB doesn't cover?
   > ADB-S 26ai has improved Select AI accuracy with Cohere models. Not in our service file.

2. What went wrong that others should know about?
   > DEP provisioning took 3 weeks, not the 3-5 days we estimated. Region capacity was low.

3. What worked well that we should capture as a pattern?
   > Using OCI Events + Functions for automated DR validation after switchover. Should be a pattern.

Saving...
  → Created finding FF-202603-010 (DEP provisioning delay)
  → Updated kb/services/adb-serverless.yaml changelog (Select AI 26ai)
  → Created draft pattern kb/patterns/dr-validation-automation.yaml (needs review)
```

The AER auto-creates findings and KB updates from the architect's answers. Lowest possible friction.

### 4d. Confidence Decay

Knowledge ages. A finding validated 2 years ago may no longer be accurate.

```yaml
# Confidence decay rules (in config/kb-governance.yaml):
confidence_decay:
  validated:
    fresh_until_days: 180          # Green for 6 months
    stale_after_days: 365          # Yellow after 1 year
    expired_after_days: 730        # Red after 2 years — needs re-validation
  reported:
    fresh_until_days: 90
    stale_after_days: 180
    expired_after_days: 365
  inferred:
    fresh_until_days: 90
    stale_after_days: 180
    expired_after_days: 365
```

The linter shows decay status:

```bash
$ python tools/kb_linter.py --show-decay

kb/field-findings/tracker.yaml
  FF-202603-001  FRESH   CLI JSON bug (validated 2026-03-10, 4 days ago)
  FF-202603-002  FRESH   ADG must disable for DEP (validated 2026-03-08)
  FF-202501-001  STALE   Some old finding (validated 2025-01-15, 424 days ago) ← NEEDS RE-VALIDATION
```

### 4e. Tagging Taxonomy

Standardize tags so search works consistently:

```yaml
# config/kb-tags.yaml
taxonomy:
  products: [adb-s, adb-d, dep, exacs, dbcs, oke, functions, vcn, drg, fastconnect, dms, goldengate, data-safe, vault]
  versions: [19c, 21c, 23ai, 26ai]
  categories: [ha, dr, security, networking, performance, migration, cost, sizing, compliance]
  severity_tags: [blocker, workaround-available, cosmetic]
  lifecycle: [design, migration, day2, decommission]
```

The CLI validates tags against the taxonomy and suggests corrections:

```bash
$ python tools/findings_cli.py add --tags "adb_s,hacksw"
WARNING: Unknown tag 'adb_s'. Did you mean 'adb-s'?
WARNING: Unknown tag 'hacksw'. Did you mean 'hnsw'?
```

---

## 5. Files to Build

### 35. `config/kb-governance.yaml`

```yaml
---
# KB Governance Configuration
# Controls freshness tracking, confidence decay, and review cadence
---

contribution:
  required_fields: [name, team, date, confidence]
  optional_fields: [client, context]
  confidence_levels: [validated, observed, reported, inferred]

freshness:
  warning_days: 180
  stale_days: 365
  
confidence_decay:
  validated:  { fresh: 180, stale: 365, expired: 730 }
  observed:   { fresh: 120, stale: 270, expired: 540 }
  reported:   { fresh: 90,  stale: 180, expired: 365 }
  inferred:   { fresh: 90,  stale: 180, expired: 365 }

review_triggers:
  - event: "Oracle database version release"
    action: "Review all feature matrix entries. Mark untested. Validate within 14 days."
  - event: "Oracle pricing change"
    action: "Update kb/pricing/ files. Verify cost calculator accuracy."
  - event: "After customer engagement"
    action: "Run After-Engagement Review (AER). Add findings and KB updates."
  - event: "Quarterly"
    action: "Run kb_linter.py. Refresh stale files. Review open findings."
```

### 36. `config/kb-owners.yaml`

Domain ownership mapping as shown in section 4a above.

### 37. `config/kb-tags.yaml`

Standardized tag taxonomy as shown in section 4e above.

---

## 6. Updates to Existing Tools

### Update `tools/kb_linter.py`

Add these checks:
- Verify contributor blocks on all findings and matrix entries
- Check confidence_decay against governance config
- Validate tags against taxonomy
- Check domain owners have reviewed within their cadence
- Report contribution stats

### Update `tools/findings_cli.py`

Add:
- `confirm` command (section 3)
- `aer` command (section 4c — After-Engagement Review)
- Contributor fields on `add` command
- Tag validation against taxonomy

### New: `tools/kb_cli.py`

Unified KB management CLI:

```bash
python tools/kb_cli.py stats contributors      # Contribution leaderboard
python tools/kb_cli.py stats stale             # Stale content report
python tools/kb_cli.py stats decay             # Confidence decay report
python tools/kb_cli.py changelog <file>        # Add changelog entry
python tools/kb_cli.py search "vector search"  # Search across ALL KB files
python tools/kb_cli.py owners                  # Show domain owners
python tools/kb_cli.py health                  # Overall KB health dashboard
```

### `kb_cli.py health` Output Example

```
KB HEALTH DASHBOARD
═══════════════════════════════════════════════════

Files: 24 total │ 20 fresh │ 3 stale │ 1 expired

Findings: 8 total │ 2 open │ 3 acknowledged │ 1 resolved │ 2 monitoring

Feature Matrix: 15 features × 6 deployments × 2 versions
  GA: 34 │ GA_CAVEAT: 18 │ LIMITED: 3 │ NOT_AVAIL: 12 │ UNTESTED: 23

Contributors (last 90 days):
  Diego Cabrera          14 contributions
  Maria García            5 contributions
  Carlos López            3 contributions

Needs Attention:
  ⚠ kb/pricing/database.yaml — stale (last verified 162 days ago, owner: TBD)
  ⚠ 23 UNTESTED cells in feature matrix for 26ai
  ⚠ kb/competitive/aws-mapping.yaml — no owner assigned
```

---

## 7. Build Order

Add to Phase 1 bootstrap prompt:
- 35: `config/kb-governance.yaml`
- 36: `config/kb-owners.yaml`
- 37: `config/kb-tags.yaml`

Add to Phase 2:
- Update `tools/kb_linter.py` with governance checks
- Update `tools/findings_cli.py` with `confirm`, `aer`, contributor fields
- New `tools/kb_cli.py` with health dashboard, search, stats, changelog
- Tests for all of the above

---

## Summary of Industry Practices Applied

| Practice | Source | How we apply it |
|---|---|---|
| Domain ownership | NASA PAL, Atlassian, Ford BPR | `config/kb-owners.yaml` — each KB area has an owner responsible for freshness |
| After-Action Review | US Army AAR, NASA Pause and Learn | `findings_cli.py aer` — structured 3-question post-engagement review |
| Confidence levels | Medical evidence grading (GRADE system) | 4-level confidence on every contribution: validated > observed > reported > inferred |
| Confidence decay | Pharmaceutical regulatory (expiry dates) | Knowledge ages — validated findings go stale after 1 year, need re-validation |
| Contribution tracking | Open source CONTRIBUTORS files, Stack Overflow reputation | Contributor leaderboard — visibility, not competition |
| Tag taxonomy | Library science (controlled vocabulary) | `config/kb-tags.yaml` — standardized tags with fuzzy-match suggestions |
| Confirmations | Peer review (academic), code review (engineering) | `findings_cli.py confirm` — multiple architects can validate a finding |
| KB health dashboard | SRE golden signals, platform engineering | `kb_cli.py health` — single view of KB freshness, gaps, and activity |
| Content governance | Enterprise content management, regulatory compliance | `config/kb-governance.yaml` — rules for freshness, decay, and review triggers |


---

## ░░░ SECTION 8: OPERATIONS — capabilities, tokens ░░░

# OCI DEAL ACCELERATOR — Operations Guide

## Part 1: Collaborative KB — How the Team Contributes

### The Rule

**If you hit a wall, log it. If you solve it, log it. If you tested something, log it.**

The KB is only as good as what the team puts in. Every engagement should leave the KB smarter.

### What to Contribute

| You found... | Where it goes | How to add it |
|---|---|---|
| A feature doesn't work as documented | Feature Matrix | `python tools/feature_matrix_cli.py update "Feature" deployment version --status GA_CAVEAT --notes "what happened"` |
| A bug, limitation, or surprise | Field Findings | `python tools/findings_cli.py add` (interactive) |
| A workaround from an internal team | Field Findings | Same, include source contact in `workaround` field |
| A new OCI service or feature launched | Service KB file | Edit `kb/services/service-name.yaml` or create new one |
| A pricing change | Pricing KB | Edit `kb/pricing/database.yaml` and update `last_verified` |
| A competitive insight | Competitive KB | Edit `kb/competitive/aws-mapping.yaml` |
| A new architecture pattern | Pattern KB | Create `kb/patterns/pattern-name.yaml` following template |
| A validated sizing data point | Sizing KB | Edit `kb/sizing/cpu-conversion-ratios.yaml` |
| A WA check that should be added | WA checklist | Edit the relevant `kb/well-architected/*.yaml` |

### Quick Reference: Adding a Field Finding (30 seconds)

```bash
# Interactive mode — answers prompts one by one
python tools/findings_cli.py add

# One-liner for quick logging
python tools/findings_cli.py add \
    --date 2026-03-14 \
    --reported-by "Your Name" \
    --client "Client Name" \
    --product "ADB-S" \
    --severity MEDIUM \
    --category gotcha \
    --summary "One line description" \
    --tags "tag1,tag2"
```

### Quick Reference: Updating the Feature Matrix (10 seconds)

```bash
# Check current status
python tools/feature_matrix_cli.py check "Select AI" adb_s 26ai

# Update after testing
python tools/feature_matrix_cli.py update "Select AI" adb_s 26ai \
    --status GA --notes "Tested with Cohere Command R+. Works."
```

### Freshness Tracking

Every KB file has a `last_verified` date. The linter warns if a file is older than 180 days:

```bash
# Check what's stale
python tools/kb_linter.py

# Output:
# kb/services/adb-serverless.yaml    PASS    last_verified: 2026-03-14
# kb/pricing/database.yaml           WARN    last_verified: 2025-10-01 (164 days ago)
# kb/competitive/aws-mapping.yaml    WARN    last_verified: 2025-08-15 (211 days ago — STALE)
```

After re-verifying, update the date:

```yaml
---
last_verified: 2026-03-14   # ← update this
---
```

### Review Cadence

| Trigger | Action |
|---|---|
| New Oracle version release (e.g., 26ai GA) | Run `feature_matrix_cli.py gaps` for all deployment types. Mark UNTESTED. Test and update over next 2 weeks. |
| After every customer engagement | Add findings. Update matrix if something was tested. |
| Quarterly | Run `kb_linter.py`. Refresh anything older than 180 days. Review open findings for resolution. |
| Oracle CPUs/patches | Check `kb/field-knowledge/gotchas.yaml` for resolved bugs. |

### Future: Automated KB Ingestion

Current state: manual edits via CLI tools + YAML files. Simple, version-controlled, works.

Planned evolution:

```
Phase 1 (now):     CLI tools + YAML files + git
Phase 2 (next):    RAG layer indexes KB for semantic search during skill execution
Phase 3 (future):  Automated ingestion from Oracle doc RSS feeds, release notes, MOS alerts
```

For Phase 2, the approach is:
- Embed all KB YAML files into a vector store (Cohere, OpenAI embeddings, or OCI GenAI)
- The skill queries the vector store instead of loading all files into context
- Only relevant KB chunks are pulled into the LLM context window
- The YAML files remain the source of truth — the vector store is a read cache

This doesn't require any KB format changes. The current YAML structure is already optimized for chunking: each feature matrix entry, each finding, each service file is a self-contained document.

---

## Part 2: Skill Capabilities — Full Catalog with Examples

### Capability 1: Parse Discovery Notes → Workload Profile

**What it does:** Takes messy, unstructured notes from a customer meeting and produces a structured YAML workload profile.

**Example input:**
```
Met with Acme Corp CTO (Jane) and DBA (Mike), March 10

3 oracle DBs on exadata x8m on-prem
- main OLTP 4TB, 19c EE, RAC 2 nodes, ~70% CPU avg, 200 peak connections
- reporting 2TB, GoldenGate from main, read-heavy
- small APEX app 200GB single instance

WebLogic 14c on 6 bare metal, java apps
MQ Series for async messaging

Want 99.95%, PCI (credit card processing)
Black Friday 3x peak
Budget sensitive but not cheapest-wins, willing to pay for reliability
Have 8 proc licenses Oracle, want BYOL
Team: 2 DBAs, no cloud experience
CTO wants cloud in 6 months
Comparing with AWS
```

**Example output:**
```yaml
workload_profile:
  engagement:
    customer_name: "Acme Corp"
    industry: "retail"
    decision_timeline: "6 months"
    competitive_situation: "AWS"
  current_state:
    databases:
      - name: "Main OLTP"
        engine: "Oracle 19c EE"
        size_gb: 4096
        type: "OLTP"
        current_platform: "Exadata X8M on-prem"
        ha_current: "RAC 2-node"
        replication: "GoldenGate (source)"
        connections_peak: 200
        cpu_metrics: { avg_cpu_pct: 70, vcpus_current: 16 }
        notable_features: [RAC, TDE]
      - name: "Reporting"
        engine: "Oracle 19c EE"
        size_gb: 2048
        type: "OLAP"
        replication: "GoldenGate (target)"
      - name: "APEX App"
        engine: "Oracle 19c"
        size_gb: 200
        type: "mixed"
  # ... (continues with compute, middleware, messaging, requirements, decision_drivers)
```

**Gap detection:** "I have enough to start. Missing: P95 CPU for main DB, IOPS metrics, specific PCI scope (is it just the OLTP DB or all three?). I'll assume P95 CPU ~85%, and PCI scope is the OLTP DB + app tier."

---

### Capability 2: Compose Architecture

**What it does:** Given a workload profile, selects OCI services, dimensions them, composes the topology, and validates against the Well-Architected Framework.

**Example prompt:** "Compose an architecture for the Acme Corp workload profile above."

**What happens internally:**
1. Selects ADB-S for OLTP (variable workload, no DBA team, auto-scaling)
2. Sizes at 8 OCPU base (P75 of 16 vCPUs × 70% = 11.2 → /2 = 5.6 → ×1.3 headroom = 7.3 → round to 8)
3. Selects patterns: `database-ha-adb-s` + `database-dr-cross-region` + `networking-basic`
4. Checks feature matrix: TAC → GA_CAVEAT (notes replay limitations)
5. Checks field findings: no blockers for this configuration
6. Validates against WA Framework: 5 pillars scored
7. Estimates costs: ~$12K/mo PAYG, ~$7K/mo BYOL

---

### Capability 3: Generate Architecture Diagram

**What it does:** Produces a `.drawio` file with official Oracle visual style.

**Example prompt:** "Generate the diagram."

**Example output:** `architecture.drawio` — opens in draw.io with:
- Tenancy (dashed gray border)
- Region (solid warm gray fill)
- VCN (dashed burnt orange border — the Oracle signature)
- Subnets (dashed orange, thinner, near-white fill)
- Service blocks colored by category (teal/copper/purple)
- Connections with proper styles (ADG = dashed orange, FastConnect = solid purple)

---

### Capability 4: Generate Slide Deck

**What it does:** Produces a `.pptx` presentation ready for the customer meeting.

**Example prompt:** "Generate the deck." or just "deck" (default output).

**Example output:** `architecture-proposal.pptx` — 12 slides:
1. Title slide (dark background, customer name)
2. Engagement summary
3. Architecture diagram (full slide)
4. Architecture decisions table
5. HA/DR with RTO/RPO table
6. Security & compliance checklist
7. Cost estimate with PAYG vs BYOL
8. Cost comparison vs current state
9. Migration timeline (4 phases)
10. Risk register (top 5-6)
11. Well-Architected scorecard (5 pillars)
12. Next steps with dates

---

### Capability 5: Cost Estimation

**What it does:** Estimates monthly and annual costs with PAYG vs BYOL breakdown.

**Example prompt:** "Estimate costs for this architecture."

**Example output:**
```
Component                    Monthly (PAYG)   Monthly (BYOL)
ADB-S Primary (8 OCPU)      $2,400           $1,200
ADB-S Standby (Local ADG)   $2,400           $1,200
ADB-S DR (Cross-region)     $2,400           $1,200
Compute (2x E5.Flex 4 OCPU) $440             $440
OKE (3 workers 8 OCPU)      $1,320           $1,320
FastConnect 10 Gbps          $600             $600
Storage & Other              $800             $800
─────────────────────────────────────────────────────
Total Monthly                $10,360          $6,760
Total Annual                 $124,320         $81,120

Assumptions:
- 730 hours/month sustained usage
- BYOL with 8 existing processor licenses
- Auto-scaling active ~4 hours/day (additional $960/mo PAYG estimated)
- Estimates are ±15% — not a quote
```

---

### Capability 6: Well-Architected Validation

**What it does:** Scores the architecture against Oracle's 5-pillar framework automatically.

**Example prompt:** "Run the Well-Architected check."

**Example output:**
```
WELL-ARCHITECTED SCORECARD

Security & Compliance       ✅ PASS              18/20 checks
Reliability & Resilience    ⚠️ RECOMMENDATIONS   12/15 checks
Performance & Cost          ✅ PASS              10/10 checks
Operational Efficiency      ❌ GAPS               6/10 checks
Distributed Cloud           ➖ N/A               Single deployment

GAPS:
  [OPS-DEPLOY-01] HIGH: No IaC (Terraform) strategy defined
    → Recommendation: Define Terraform modules for all components
  [REL-DR-03] MEDIUM: No DR drill schedule
    → Recommendation: Quarterly DR drill with automated validation
  [OPS-MON-03] MEDIUM: No APM configured
    → Recommendation: Enable OCI APM for application tracing
```

---

### Capability 7: Feature Compatibility Check

**What it does:** Verifies that the recommended deployment supports all required features.

**Example prompt:** "Does ADB-S 23ai support vector search at 100M scale?"

**Example output:**
```
AI Vector Search (HNSW) on ADB-S 23ai: GA_CAVEAT

HNSW indexes are node-local on multi-node RAC. At 100M+ vectors on ≥64 
ECPUs, P95 latency exceeds 200ms without workaround.

Workaround: Hash-partition vector table + LOCAL HNSW index.
Validated: 120M vectors, 64 ECPU, P95 = 38ms.
Reference: FF-202603-008

Alternative: IVF indexes are distributed (no workaround needed) but 
have lower recall than HNSW at same latency budget.
```

---

### Capability 8: Field Findings Search

**What it does:** Searches institutional knowledge for known issues.

**Example prompt:** "Any known issues with DEP?" or "Search findings for elastic pool."

**Example output:**
```
3 findings match "elastic pool":

FF-202603-002 [HIGH] ADG must be disabled before joining DEP
  Client: Strategic Migration Customer | Status: acknowledged
  Workaround: Disable ADG → join DEP → re-enable. ~15 min HA gap.

FF-202603-003 [MEDIUM] DEP maintenance window immutable post-creation
  Client: Strategic Migration Customer | Status: acknowledged
  Workaround: Set at creation time (Console). Or file SR.

FF-202603-004 [MEDIUM] DEP provisioning takes days to weeks
  Client: Strategic Migration Customer | Status: acknowledged
  Workaround: Request early. Don't make critical-path dependency.
```

---

### Capability 9: Competitive Positioning

**What it does:** Provides honest comparison against AWS/Azure/GCP.

**Example prompt:** "How does this compare to AWS for this workload?"

**Example output:**
```
OCI vs AWS for Acme Corp workload:

GENUINE OCI ADVANTAGES:
- ADB-S auto-tuning, auto-indexing, auto-patching — no AWS RDS equivalent
- TAC provides near-zero perceived downtime — no AWS equivalent
- BYOL discount is ~50% on OCPU — larger than AWS BYOL savings
- Exadata storage performance for OLTP — better than EBS gp3

GENUINE OCI GAPS:
- AWS has broader ecosystem of managed services beyond database
- AWS Marketplace has more third-party integrations
- More architects have AWS experience (customer team learning curve)

HONEST ANSWER TO COMMON OBJECTION:
"AWS Aurora is better than ADB-S" → Aurora is MySQL/PostgreSQL, not Oracle.
For Oracle workloads, the comparison is RDS Oracle vs ADB-S. ADB-S is 
fully autonomous; RDS Oracle requires manual patching and tuning.
```

---

### Capability 10: Output Format Selection

**What it does:** Produces outputs in the format the architect needs.

**Example prompts:**
```
"deck"                    → .pptx (default)
"deck + drawio"           → .pptx + .drawio
"deck + xlsx"             → .pptx + cost spreadsheet
"full"                    → everything
"doc only"                → technical document (.docx)
"drawio only"             → just the diagram
```

---

## Part 3: Token Optimization Strategy

### The Problem

Loading the entire SKILL.md + all KB files into context on every call wastes tokens. The full KB is ~50-80K tokens. Most calls need only 10-20% of it.

### Strategy: Tiered Context Loading

Split the skill into three tiers loaded on demand, not all at once.

#### Tier 1: Always Loaded (~3K tokens)

A compact system prompt with core instructions, service categories, and routing logic. This is the SKILL.md that goes into every call.

```
deal-accelerator/
├── SKILL_COMPACT.md          ← NEW: minimal system prompt (~3K tokens)
├── SKILL.md                  ← Full reference (used only when loading Tier 2/3)
```

**SKILL_COMPACT.md contains only:**
- Role definition (2 sentences)
- The 3 principles (1 line each)
- The 3-phase workflow (1 paragraph each, not full details)
- Service category mapping (teal/copper/purple — table, ~20 lines)
- Output format options (6 lines)
- Instruction: "Load relevant KB files before answering. Use `kb/INDEX.yaml` to find the right files."

#### Tier 2: Loaded Per Phase (~5-15K tokens each)

KB files loaded ONLY when the current phase needs them.

| Phase | Files Loaded |
|---|---|
| Phase 1: Discovery → Profile | `config/workload-profile-schema.yaml` |
| Phase 2: Composition | `kb/services/{relevant services}.yaml`, `kb/patterns/{relevant patterns}.yaml`, `kb/sizing/cpu-conversion-ratios.yaml`, `kb/compatibility/adb-feature-matrix.yaml` |
| Phase 2: WA Validation | `kb/well-architected/{relevant pillars}.yaml` |
| Phase 3: Cost | `kb/pricing/database.yaml` |
| Phase 3: Competitive | `kb/competitive/aws-mapping.yaml` (only if competitor identified) |
| Phase 3: Diagram | `kb/diagram/oci-toolkit-styles.yaml` |

#### Tier 3: Loaded On Demand (~1-5K tokens each)

Specific files loaded only when explicitly needed.

| Trigger | File Loaded |
|---|---|
| Architect asks about a specific feature | Single entry from `adb-feature-matrix.yaml` |
| Architect asks about known issues | Relevant entries from `tracker.yaml` (search, not full file) |
| Architect asks about a specific service | Single file from `kb/services/` |
| Field knowledge needed | Relevant entries from `kb/field-knowledge/gotchas.yaml` |

### Implementation: KB Index File

Create `kb/INDEX.yaml` — a lightweight map of what's in the KB and when to load it:

```yaml
# kb/INDEX.yaml — KB Table of Contents (~500 tokens)
# The skill reads this first and loads only what's needed.

services:
  adb-serverless:
    path: "kb/services/adb-serverless.yaml"
    keywords: ["adb", "autonomous", "serverless", "oltp", "auto-scaling", "tac"]
    load_when: "workload includes Oracle database, autonomous, or serverless"
  exadata-cloud:
    path: "kb/services/exadata-cloud.yaml"
    keywords: ["exadata", "exacs", "rac", "dedicated", "high-performance"]
    load_when: "workload needs RAC, OS access, or >128 OCPU sustained"
  oci-networking-core:
    path: "kb/services/oci-networking-core.yaml"
    keywords: ["vcn", "subnet", "gateway", "fastconnect", "load balancer", "waf"]
    load_when: "always during composition phase"

patterns:
  database-ha-adb-s:
    path: "kb/patterns/database-ha-adb-s.yaml"
    keywords: ["ha", "high availability", "tac", "adg", "failover"]
    load_when: "architecture needs database HA"
  database-dr-cross-region:
    path: "kb/patterns/database-dr-cross-region.yaml"
    keywords: ["dr", "disaster recovery", "cross-region", "adg"]
    load_when: "architecture needs cross-region DR"
  networking-basic:
    path: "kb/patterns/networking-basic.yaml"
    keywords: ["vcn", "subnet", "networking"]
    load_when: "always during composition phase"

compatibility:
  adb-feature-matrix:
    path: "kb/compatibility/adb-feature-matrix.yaml"
    keywords: ["feature", "version", "23ai", "26ai", "compatibility"]
    load_when: "recommending specific ADB deployment type or version"

findings:
  tracker:
    path: "kb/field-findings/tracker.yaml"
    keywords: ["bug", "issue", "limitation", "workaround", "gotcha"]
    load_when: "composing architecture or generating risk register"

well_architected:
  security-compliance:
    path: "kb/well-architected/security-compliance.yaml"
    load_when: "WA validation phase"
  reliability-resilience:
    path: "kb/well-architected/reliability-resilience.yaml"
    load_when: "WA validation phase"
  performance-cost:
    path: "kb/well-architected/performance-cost.yaml"
    load_when: "WA validation phase"
  operational-efficiency:
    path: "kb/well-architected/operational-efficiency.yaml"
    load_when: "WA validation phase"
  distributed-cloud:
    path: "kb/well-architected/distributed-cloud.yaml"
    load_when: "multi-region or hybrid architecture"

pricing:
  database:
    path: "kb/pricing/database.yaml"
    load_when: "cost estimation phase"

competitive:
  aws-mapping:
    path: "kb/competitive/aws-mapping.yaml"
    load_when: "competitive situation identified in workload profile"

sizing:
  cpu-conversion-ratios:
    path: "kb/sizing/cpu-conversion-ratios.yaml"
    load_when: "sizing compute or database resources"

diagram:
  oci-toolkit-styles:
    path: "kb/diagram/oci-toolkit-styles.yaml"
    load_when: "generating .drawio diagram"
```

### Implementation: Compact System Prompt

Create `SKILL_COMPACT.md` (~3K tokens vs ~8K for the full SKILL.md):

```markdown
# OCI Deal Accelerator

You help OCI Solutions Architects go from discovery notes to architecture proposal in hours.

## Principles
1. Empirical over theoretical — justify with real data, not "best practice"
2. Simplicity first — complexity must be earned
3. Honest about limitations — credibility depends on it

## Workflow
Phase 1: Parse discovery notes → structured Workload Profile (YAML)
Phase 2: Compose architecture → select services, dimension, validate against WA Framework
Phase 3: Generate outputs → deck (.pptx, default), diagram (.drawio), doc, xlsx

## Service Categories
| Category | Color | Services |
|----------|-------|----------|
| Infrastructure | Teal #2D5967 | Compute, OKE, Functions, LB, Gateways, WAF, Bastion, Vault, Data Safe, Monitoring, Storage |
| Database | Copper #AA643B | ADB-S, ADB-D, DBCS, ExaCS, NoSQL, MySQL, PostgreSQL, Cache, GoldenGate |
| Integration | Purple #804998 | DRG, Streaming, Queue, OIC, FastConnect |

## Output Options
deck (default) | deck+drawio | deck+xlsx | deck+doc | full | doc | drawio

## KB Loading
Read `kb/INDEX.yaml` first. Load ONLY the KB files relevant to the current task.
Do NOT load all KB files at once. Load per-phase:
- Discovery: config/workload-profile-schema.yaml
- Composition: relevant services + patterns + sizing + compatibility
- Validation: relevant well-architected pillars
- Output: pricing (if costing), diagram styles (if diagramming), competitive (if comparing)

## Key Rules
- Architect communicates in Spanish, all deliverables in English
- Diagrams use OCI toolkit styles (VCN = dashed burnt orange #AE562C)
- Check feature matrix before recommending deployment type
- Check field findings before finalizing risk register
- Cost estimates are ±15%, marked as estimated
- Competitive comparisons include genuine gaps, not just advantages
```

### Token Budget per Call

| Call Type | Tier 1 | Tier 2 | Tier 3 | Total |
|---|---|---|---|---|
| Simple question | 3K | 0 | 0 | ~3K |
| Parse discovery notes | 3K | 2K (schema) | 0 | ~5K |
| Compose architecture | 3K | 12K (services + patterns + sizing + matrix) | 2K (findings) | ~17K |
| WA validation only | 3K | 8K (5 pillars) | 0 | ~11K |
| Generate diagram only | 3K | 3K (styles) | 0 | ~6K |
| Generate deck | 3K | 3K (pricing) | 0 | ~6K |
| Full pipeline | 3K | 15K (all Phase 2) + 8K (WA) + 3K (pricing) + 3K (styles) | 2K | ~34K |
| Feature check | 3K | 0 | 1K (single matrix entry) | ~4K |
| Findings search | 3K | 0 | 1K (matching findings) | ~4K |

Compare to loading everything every time: ~60-80K tokens. The tiered approach uses **3-34K depending on the task** — 50-95% reduction.

### For Codex / Claude Code (Agentic Mode)

When running as an agent with file system access, the LLM can:
1. Read `kb/INDEX.yaml` at start
2. Decide which files to load based on the user's request
3. Read only those files
4. Execute tools (diagram gen, deck gen, etc.)
5. Never load the full KB unless explicitly asked

The `SKILL_COMPACT.md` becomes the agent's system prompt. The full `SKILL.md` is reference documentation, not loaded into context.

### For API / ChatGPT (Non-Agentic Mode)

When the skill runs without file system access (e.g., pasted into ChatGPT):
1. Paste `SKILL_COMPACT.md` as system prompt
2. Paste only the KB files relevant to the current task
3. The architect decides what to paste based on the INDEX

This is less elegant but still saves tokens vs pasting everything.

---

## Files to Add

Add these to the bootstrap prompt as files 33-34:

### 33. `kb/INDEX.yaml`
The KB table of contents shown above. ~500 tokens. Loaded on every call.

### 34. `SKILL_COMPACT.md`
The minimal system prompt shown above. ~3K tokens. Replaces SKILL.md in context window.

Add to Phase 2 testing prompt:

### Additional tests in `tests/test_integration.py`:

```python
# test_compact_skill_has_all_categories:
#   SKILL_COMPACT.md mentions all 3 service categories

# test_kb_index_references_existing_files:
#   Every path in kb/INDEX.yaml points to a file that exists

# test_kb_index_covers_all_kb_files:
#   Every YAML in kb/ is referenced in INDEX.yaml (no orphan files)

# test_token_estimate:
#   SKILL_COMPACT.md is under 4K tokens (rough estimate: chars/4)
#   Full SKILL.md is documented as reference only
```


---

## ░░░ SECTION 9: EXAMPLE — vector search finding ░░░

# Example: Tracking a Real Field Finding End-to-End

## The Situation

A customer wants to run vector similarity search on 100M+ vectors in ADB-S 
with <50ms P95 latency. ADB-S supports AI Vector Search with HNSW indexes, 
but at 100M+ scale on a multi-node RAC deployment (≥64 ECPUs), the HNSW 
index is local to each RAC node — there's no distributed HNSW index. 
Queries hit one node's index and miss vectors stored on the other node, 
giving either incomplete results or requiring a UNION across nodes which 
blows the latency target.

An internal Oracle team (e.g., Database Product Management or a specialist 
SA team) knows a workaround: partition the vector table by a hash on the 
vector ID so that all vectors for a given search are co-located on one node, 
then use a partition-aware HNSW index. This keeps the <50ms latency at 100M+ 
scale but requires specific table design.

## How It Gets Tracked

### 1. Field Finding Entry

The architect who hit this adds it via CLI:

```bash
python tools/findings_cli.py add \
    --date 2026-03-14 \
    --reported-by "Diego Cabrera" \
    --client "Vector Search Customer" \
    --product "ADB-S" \
    --version "23ai" \
    --severity HIGH \
    --category limitation \
    --summary "Distributed HNSW indexes not available — 100M+ vector search requires partitioning workaround" \
    --detail "ADB-S AI Vector Search supports HNSW indexes but they are node-local on multi-node RAC (≥64 ECPUs). At 100M+ vectors, queries on a 2-node RAC miss vectors on the other node. Results are either incomplete or require cross-node scan that blows P95 >200ms. Workaround from internal DB PM team: hash-partition vector table on vector_id, create partition-local HNSW index. Queries hit single partition on single node, maintaining <50ms at 100M scale. Requires table redesign — cannot be applied to existing unpartitioned vector tables without data reload." \
    --workaround "Hash-partition vector table by vector_id. Create HNSW index as LOCAL (partition-level). Ensure partition pruning in queries. Source: internal DB PM team contact [name]. Validated on ADB-S 23ai with 120M vectors, P95 = 38ms on 64 ECPU." \
    --tags "vector-search,hnsw,distributed,rac,partitioning,100m,latency,ai-vector-search"
```

This creates:

```yaml
  - id: "FF-202603-008"
    date: "2026-03-14"
    reported_by: "Diego Cabrera"
    client: "Vector Search Customer"
    product: "ADB-S"
    version: "23ai"
    severity: "HIGH"
    category: "limitation"
    summary: "Distributed HNSW indexes not available — 100M+ vector search requires partitioning workaround"
    detail: |
      ADB-S AI Vector Search supports HNSW indexes but they are node-local on 
      multi-node RAC (≥64 ECPUs). At 100M+ vectors, queries on a 2-node RAC 
      miss vectors on the other node. Results are either incomplete or require 
      cross-node scan that blows P95 >200ms.
      
      Workaround from internal DB PM team: hash-partition vector table on 
      vector_id, create partition-local HNSW index. Queries hit single 
      partition on single node, maintaining <50ms at 100M scale.
      
      Requires table redesign — cannot be applied to existing unpartitioned 
      vector tables without data reload.
    workaround: |
      Hash-partition vector table by vector_id. Create HNSW index as LOCAL 
      (partition-level). Ensure partition pruning in queries.
      Source: internal DB PM team contact [name].
      Validated on ADB-S 23ai with 120M vectors, P95 = 38ms on 64 ECPU.
    oracle_sr: ""
    status: "acknowledged"
    resolved_date: null
    resolution: null
    affects_matrix: "AI Vector Search (HNSW)"
    tags: ["vector-search", "hnsw", "distributed", "rac", "partitioning", "100m", "latency", "ai-vector-search"]
```

### 2. Feature Matrix Entry

Add to `kb/compatibility/adb-feature-matrix.yaml`:

```yaml
  - name: "AI Vector Search (HNSW)"
    category: "developer"
    matrix:
      adb_s:
        "23ai":
          status: "GA_CAVEAT"
          notes: |
            HNSW indexes are node-local on multi-node RAC. Works well up to 
            ~50M vectors on single node (≤24 ECPUs). At 100M+ on multi-node 
            (≥64 ECPUs), requires hash-partitioned vector table with LOCAL 
            HNSW index for <50ms P95. See FF-202603-008.
          scale_limits:
            single_node_max_vectors: "~50M with <50ms P95"
            multi_node_requires: "Hash partitioning + LOCAL HNSW index"
            validated_at: "120M vectors, 64 ECPU, P95 = 38ms (with workaround)"
            without_workaround: "P95 >200ms at 100M+ on 2-node RAC"
          field_finding_ref: "FF-202603-008"
        "26ai":
          status: "UNTESTED"
          notes: "Check if distributed HNSW is added in 26ai. Expected to remain node-local."
      adb_s_ep:
        "23ai":
          status: "GA_CAVEAT"
          notes: "Same node-local limitation as ADB-S Serverless."
          field_finding_ref: "FF-202603-008"
      adb_d:
        "23ai":
          status: "GA_CAVEAT"
          notes: "Same limitation. Dedicated infra doesn't change HNSW locality."
      exacs:
        "23ai":
          status: "GA_CAVEAT"
          notes: "RAC with HNSW has same node-local constraint. Partitioning workaround applies."
      dbcs_ee:
        "23ai":
          status: "NOT_AVAIL"
          notes: "AI Vector Search requires 23ai. Available in EE but HNSW performance limited without Exadata storage."

  - name: "AI Vector Search (IVF)"
    category: "developer"
    matrix:
      adb_s:
        "23ai":
          status: "GA"
          notes: |
            IVF (Inverted File) indexes ARE distributed across RAC nodes. 
            Works at 100M+ scale without partitioning. However, IVF has 
            lower recall than HNSW at same latency budget. Trade-off: 
            IVF for scale without redesign, HNSW+partitioning for best recall.
        "26ai":
          status: "UNTESTED"
```

### 3. How the Skill Uses This

When the Deal Accelerator composes an architecture and the workload profile mentions vector search:

**In the ADR:**
```
Decision: Use ADB-S with hash-partitioned vector tables and LOCAL HNSW indexes
Context: Customer requires <50ms P95 vector similarity search on 100M+ vectors
Alternatives considered:
  - Unpartitioned HNSW: P95 >200ms on multi-node RAC at this scale (rejected)
  - IVF indexes: Distributed across nodes, no redesign needed, but lower recall (backup option)
  - Dedicated single-node ADB-S (≤24 ECPUs): Avoids RAC split but may not have enough compute
Consequences: Requires vector table schema design upfront. Cannot retrofit existing tables without data reload.
Reference: FF-202603-008
```

**In the Risk Register:**
```
Risk: Vector table requires hash partitioning for HNSW performance at scale
Severity: MEDIUM
Mitigation: Design partitioned schema before initial data load. 
            Validate with 10M vector subset before full 100M load.
Reference: FF-202603-008
```

**In the WA Scorecard:**
Performance pillar flags this as a consideration:
```
CHECK: Vector search latency validated at target scale
STATUS: PASS_WITH_RECOMMENDATIONS
NOTE: HNSW index is node-local on RAC. Architecture uses partitioning 
      workaround (FF-202603-008). Validated at 120M vectors.
```

### 4. How the Feature Matrix CLI Helps

Before recommending ADB-S for this workload:

```bash
$ python tools/feature_matrix_cli.py check "AI Vector Search (HNSW)" adb_s 23ai

AI Vector Search (HNSW) on ADB-S Serverless (23ai): GA_CAVEAT

  HNSW indexes are node-local on multi-node RAC. Works well up to ~50M 
  vectors on single node (≤24 ECPUs). At 100M+ on multi-node (≥64 ECPUs), 
  requires hash-partitioned vector table with LOCAL HNSW index for <50ms P95.
  
  Scale limits:
    Single node max: ~50M vectors with <50ms P95
    Multi-node requires: Hash partitioning + LOCAL HNSW index
    Validated at: 120M vectors, 64 ECPU, P95 = 38ms (with workaround)
    Without workaround: P95 >200ms at 100M+ on 2-node RAC
  
  Field Finding: FF-202603-008
```

Compare deployment options:

```bash
$ python tools/feature_matrix_cli.py compare adb_s exacs 23ai --feature "AI Vector Search"

Feature                     | ADB-S Serverless | ExaCS
--------------------------- | ---------------- | -----
AI Vector Search (HNSW)     | GA_CAVEAT        | GA_CAVEAT
AI Vector Search (IVF)      | GA               | GA

Both have same HNSW node-local limitation. 
ExaCS has faster Exadata storage for IVF scans.
```

---

## What This Pattern Enables

1. **An architect in São Paulo** hits the same vector scale issue 3 months later → searches `python tools/findings_cli.py search "vector hnsw"` → gets the finding with the workaround, the validation data, and the internal contact → skips 2 weeks of debugging

2. **Oracle releases 26ai** → someone runs `python tools/feature_matrix_cli.py gaps adb_s 26ai` → sees all UNTESTED entries → systematically validates and updates → team is current in hours not weeks

3. **Customer asks "can ADB-S do vector search at 100M scale?"** → architect checks matrix in 5 seconds → gives an honest answer with the workaround instead of saying "yes" and discovering the problem during PoC

4. **The skill itself** checks the matrix during composition and automatically flags the limitation in the ADR and risk register → no architect forgets to mention it

This is the difference between a tool that recites docs and a tool that has real-world intelligence.


---

## ░░░ SECTION 10: PHASE 2 — testing, validation, CI ░░░

# OCI DEAL ACCELERATOR — Phase 2: Features, Testing & Hardening

## CRITICAL: Git Branching Rule

Before creating ANY files, run:

```bash
git checkout main
git pull origin main
git checkout -b feature/phase2-testing
```

NEVER create an orphan branch. ALWAYS branch from `main`. ALWAYS create a PR when done.

---

## Context

Phase 1 (bootstrap-prompt.md) builds the 28 core files: KB, tools, Codex packaging, and examples. This Phase 2 prompt builds the features and tests that make the project production-grade.

You are continuing work on the Deal Accelerator project. All 28 files from Phase 1 exist. DO NOT recreate them. Build on top of them.

---

## What's Missing

### A. No tests exist. Nothing is validated programmatically.
### B. Phase 1 (parse discovery notes → workload profile) has no validation tooling.
### C. The WA Scorecard auto-detection is described but not implemented as code.
### D. Cost estimation is manual — no calculator module.
### E. No spec validator to catch errors before feeding YAML to generators.
### F. No KB linter to ensure file format consistency.
### G. No CI — nothing runs on push.
### H. No KB freshness checker (last_verified dates exist but nothing audits them).

---

## Files to Build

### 1. `tests/conftest.py`

Shared pytest fixtures:

```python
import pytest
import yaml
import os

@pytest.fixture
def sample_spec():
    """Load the example architecture spec."""
    with open("examples/migration-adb-ha-dr.yaml") as f:
        return yaml.safe_load(f)

@pytest.fixture
def sample_workload_profile():
    """Load the example workload profile."""
    with open("examples/sample-workload-profile.yaml") as f:
        return yaml.safe_load(f)

@pytest.fixture
def service_categories():
    """Load service category mapping."""
    with open("config/service-categories.yaml") as f:
        return yaml.safe_load(f)

@pytest.fixture
def workload_schema():
    """Load workload profile schema."""
    with open("config/workload-profile-schema.yaml") as f:
        return yaml.safe_load(f)

@pytest.fixture
def tmp_output(tmp_path):
    """Provide a temporary output directory."""
    return tmp_path
```

---

### 2. `tests/test_diagram_gen.py`

Test the `.drawio` diagram generator thoroughly.

```python
"""Tests for oci_diagram_gen.py"""

# Test categories:

# --- XML Validity ---
# test_generates_valid_xml: output is well-formed XML (parse with xml.etree)
# test_has_mxfile_root: root element is <mxfile>
# test_has_diagram_element: contains <diagram> inside <mxfile>
# test_has_mxgraphmodel: contains <mxGraphModel> inside <diagram>
# test_has_root_cells: contains mxCell id="0" and mxCell id="1" (draw.io requires these)

# --- Container Styles (CRITICAL — must match OCI toolkit exactly) ---
# test_tenancy_style: tenancy cell has exact style from toolkit
#   - MUST contain: dashed=1, strokeColor=#9E9892, fillColor=none, fontColor=#312D2A
#   - MUST NOT contain: fillColor=#F5F4F2 (that's Region, not Tenancy)
# test_region_style: region cell has exact style from toolkit
#   - MUST contain: fillColor=#F5F4F2, rounded=1, arcSize=10, strokeColor=#9E9892
# test_vcn_style: VCN cell has exact style from toolkit
#   - MUST contain: dashed=1, strokeWidth=2, strokeColor=#AE562C, fontColor=#AE562C, fillColor=none
# test_subnet_style: subnet cell has exact style from toolkit
#   - MUST contain: dashed=1, strokeWidth=1, strokeColor=#AE562C, fillColor=#FCFBFA

# --- Service Block Colors ---
# test_infra_services_are_teal: all infra services use fillColor=#2d5967
# test_database_services_are_copper: all DB services use fillColor=#aa643b
# test_integration_services_are_purple: all integration services use fillColor=#804998
# test_dormant_services_are_gray: dormant elements use fillColor=#DFDCD8
# test_all_services_have_no_stroke: all service blocks have strokeColor=none

# --- Parent Hierarchy ---
# test_region_parent_is_tenancy: region's parent attribute = tenancy id
# test_vcn_parent_is_region: vcn's parent = region id (or AD if AD present)
# test_subnet_parent_is_vcn: subnet's parent = vcn id
# test_service_parent_is_subnet: service block's parent = its subnet id
# test_no_orphan_cells: every cell (except 0 and 1) has a valid parent

# --- Connections ---
# test_connections_have_source_and_target: every edge has source and target attributes
# test_connection_source_target_exist: source and target IDs exist as cells in the diagram
# test_adg_connection_is_dashed_orange: ADG connections use strokeColor=#AE562C, dashed=1
# test_fastconnect_is_bidirectional: FastConnect has both startArrow and endArrow

# --- from_spec() ---
# test_from_spec_produces_output: from_spec(sample_spec) returns a generator with cells
# test_from_spec_creates_all_regions: every region in spec appears as a cell
# test_from_spec_creates_all_subnets: every subnet in spec appears as a cell
# test_from_spec_creates_all_services: every service in spec appears as a cell
# test_from_spec_creates_all_connections: every connection in spec appears as an edge

# --- File Output ---
# test_save_creates_file: save() creates a file at the given path
# test_saved_file_opens_without_error: saved file can be parsed as XML without exceptions

# --- Edge Cases ---
# test_empty_spec: from_spec({}) produces valid XML with just root cells
# test_spec_with_no_connections: spec with services but no connections is valid
# test_special_characters_in_labels: labels with &, <, >, ", newlines are properly escaped
# test_unicode_in_labels: labels with accented characters (común in Spanish notes) work
```

For each test, write the ACTUAL test function — not just the comment. Use `xml.etree.ElementTree` to parse the output and assert on element attributes.

**Critical assertion pattern for style tests:**

```python
def test_vcn_style(sample_spec, tmp_output):
    gen = OCIDiagramGenerator.from_spec(sample_spec)
    xml_str = gen.to_xml()
    root = ET.fromstring(xml_str)
    
    # Find VCN cell
    vcn_cells = [c for c in root.iter('mxCell') 
                 if 'strokeColor=#AE562C' in (c.get('style', ''))
                 and 'strokeWidth=2' in (c.get('style', ''))]
    
    assert len(vcn_cells) >= 1, "No VCN cell found with correct style"
    
    vcn_style = vcn_cells[0].get('style', '')
    assert 'dashed=1' in vcn_style
    assert 'strokeWidth=2' in vcn_style
    assert 'strokeColor=#AE562C' in vcn_style
    assert 'fontColor=#AE562C' in vcn_style
    assert 'fillColor=none' in vcn_style
```

---

### 3. `tests/test_deck_gen.py`

Test the `.pptx` slide deck generator.

```python
"""Tests for oci_deck_gen.py"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

# --- Basic Output ---
# test_generates_valid_pptx: output can be opened by python-pptx
# test_correct_slide_count: produces 10-12 slides depending on spec
# test_slide_dimensions: slides are 13.333" x 7.5" (widescreen 16:9)

# --- Slide Content ---
# test_title_slide_has_customer_name: slide 1 contains customer_name from spec
# test_title_slide_has_project_name: slide 1 contains project_name
# test_summary_slide_has_current_state: slide 2 contains current_state bullets
# test_decisions_slide_has_table: slide 4 contains a table with correct row count
# test_cost_slide_has_total: slide 7 contains a cost total row
# test_risks_slide_matches_spec: risk count in slide matches spec
# test_wa_slide_has_5_pillars: slide 11 references all 5 WA pillars
# test_next_steps_slide_has_actions: slide 12 contains next_steps from spec

# --- Colors (OCI Brand) ---
# test_no_pure_black_text: no text element uses RGB(0,0,0) — must be #312D2A or lighter
# test_table_headers_are_teal: table header cells use background #2D5967
# test_title_slide_is_dark: slide 1 background is #312D2A

# --- Typography ---
# test_font_is_segoe_ui: body text uses Segoe UI font
# test_title_font_size: slide titles are 24-28pt
# test_body_font_size: body text is 12-14pt

# --- from_spec() ---
# test_from_spec_with_full_data: from_spec(sample_spec) produces complete deck
# test_from_spec_without_optional_fields: missing optional fields don't crash
# test_from_spec_without_cost_comparison: slide 8 (comparison) is skipped if no competitive data

# --- File Output ---
# test_save_creates_file: save() creates a .pptx file
# test_saved_file_opens_in_python_pptx: Presentation(filepath) doesn't throw
```

---

### 4. `tests/test_output_orchestrator.py`

Test `oci_output.py`:

```python
"""Tests for oci_output.py"""

# test_format_deck_only: --format deck produces only .pptx
# test_format_deck_plus_drawio: --format "deck+drawio" produces .pptx and .drawio
# test_format_full: --format full produces .pptx, .drawio, and any other outputs
# test_format_drawio_only: --format drawio produces only .drawio
# test_default_format_is_deck: no --format flag defaults to deck
# test_output_dir_created: output directory is created if it doesn't exist
# test_invalid_format_raises_error: unrecognized format raises clear error
```

---

### 5. `tests/test_spec_validator.py`

Test the spec validator (file #7 below):

```python
"""Tests for spec validation"""

# test_valid_spec_passes: the example spec passes validation
# test_missing_tenancy_fails: spec without tenancy key fails
# test_missing_region_fails: spec without any regions fails
# test_region_without_vcn_warns: region with no VCNs produces warning (not error)
# test_invalid_service_type_warns: unrecognized service type produces warning
# test_connection_references_valid_ids: connections referencing non-existent IDs fail
# test_connection_type_is_valid: connection types must be in known set
# test_duplicate_ids_fail: two elements with same ID produce error
# test_cost_components_have_required_fields: each cost component has name + at least one amount
# test_wa_scorecard_has_valid_statuses: status must be PASS/PASS_WITH_RECOMMENDATIONS/GAPS_IDENTIFIED/NOT_APPLICABLE
```

---

### 6. `tests/test_kb_linter.py`

Test the KB linter (file #8 below):

```python
"""Tests for KB file format consistency"""

# test_all_service_files_have_frontmatter: every yaml in kb/services/ has last_verified
# test_all_service_files_have_required_sections: when_to_use, when_NOT_to_use, gotchas
# test_all_pattern_files_have_required_sections: pre_conditions, conflicts_with, combines_with, cost_model
# test_all_wa_files_have_checklist_format: each check has id, description, severity, auto_detect_from
# test_wa_severity_values_are_valid: severity is HIGH, MEDIUM, or LOW
# test_last_verified_is_valid_date: last_verified parses as a date
# test_last_verified_is_not_stale: last_verified is within 180 days (warning, not error)
# test_no_empty_kb_files: no KB YAML file is empty or has only frontmatter
# test_service_category_is_valid: category field matches config/service-categories.yaml
# test_competitive_mapping_has_both_sides: every competitive entry has advantages AND gaps
```

---

### 7. `tools/spec_validator.py`

Validates a YAML spec before feeding it to generators.

**Requirements:**
- Class `SpecValidator` with method `validate(spec_dict) -> ValidationResult`
- `ValidationResult` has `errors: list[str]`, `warnings: list[str]`, `is_valid: bool`
- CLI: `python tools/spec_validator.py --spec examples/migration-adb-ha-dr.yaml`
- Validates:
  - Required top-level keys exist (tenancy, or at minimum one region)
  - All IDs are unique across the entire spec
  - All connection source/target IDs reference existing elements
  - Connection types are in the known set (standard, db, adg, fastconnect, migration, etl)
  - Service types are in the known set (from config/service-categories.yaml)
  - Deck-specific fields (if present) have required sub-fields
  - Cost components have name + at least one monetary value
  - WA scorecard statuses are valid enum values
  - No circular parent references
- Prints clear error messages with paths: `ERROR: connections[2].from references 'adb99' which does not exist`
- Exit code 0 if valid, 1 if errors found

---

### 8. `tools/kb_linter.py`

Lints all KB files for format consistency.

**Requirements:**
- CLI: `python tools/kb_linter.py` (scans entire kb/ directory)
- CLI: `python tools/kb_linter.py --file kb/services/adb-serverless.yaml` (single file)
- Checks per file type:
  - **services/**: must have `last_verified`, `service`, `category`, `when_to_use`, `when_NOT_to_use`, `gotchas`
  - **patterns/**: must have `last_verified`, `pattern.id`, `pattern.name`, `pre_conditions`, `conflicts_with`, `combines_with`, `cost_model`
  - **well-architected/**: must have `checks[]` where each check has `id`, `description`, `severity`, `auto_detect_from`
  - **pricing/**: must have `last_verified`, at least one service with pricing data
  - **competitive/**: each mapping must have `oci_service`, `aws_equivalent` (or similar), `genuine_advantages`, `genuine_gaps`
  - **field-knowledge/**: must have at least 5 entries
- Freshness check: warns if `last_verified` is older than 180 days
- Output: summary table with file, status (PASS/WARN/FAIL), issues
- Exit code 0 if all pass, 1 if any failures, 0 (with warnings printed) if only warnings

---

### 9. `tools/wa_scorer.py`

Automated Well-Architected scoring from a YAML spec.

**Requirements:**
- Class `WAScorer` with method `score(spec_dict) -> WAScorecard`
- Loads checklist YAMLs from `kb/well-architected/`
- For each check, evaluates the `auto_detect_from` field against the spec:
  - If the spec contains the element referenced → PASS
  - If the spec is missing the element → GAP
  - If the check is conditional and the condition isn't met → N/A
- CLI: `python tools/wa_scorer.py --spec examples/migration-adb-ha-dr.yaml`
- Output: JSON or YAML scorecard with per-pillar results

**Auto-detection logic examples:**

```python
# Check: "Databases in private subnets"
# auto_detect_from: "subnets where services include database types AND subnet label contains 'Private'"
# Logic: find all subnets containing database-category services, verify they're labeled private

# Check: "WAF on internet-facing endpoints"  
# auto_detect_from: "services of type 'waf' exist in a public subnet"
# Logic: find WAF service in any subnet labeled public

# Check: "Cross-region DR configured"
# auto_detect_from: "more than one region exists AND connections of type 'adg' exist"
# Logic: count regions, check for ADG connections

# Check: "IaC defined"
# auto_detect_from: "deck.migration_phases mention 'Terraform' or 'Resource Manager'"
# Logic: text search in migration phase descriptions — if not found, flag as GAP
```

Each check in the KB YAML has a `detection_rule` field that encodes the logic:

```yaml
checks:
  - id: SEC-DB-01
    description: "Databases are in private subnets"
    severity: HIGH
    detection_rule:
      type: "service_in_subnet"
      service_categories: ["database"]
      subnet_label_contains: "Private"
    wa_reference: "secure-your-databases1.html"
```

The scorer implements a small set of detection rule types:
- `service_exists`: a service of given type exists anywhere
- `service_in_subnet`: a service of given category exists in a subnet matching label pattern
- `connection_exists`: a connection of given type exists
- `multi_region`: more than one region is defined
- `text_contains`: a text field somewhere in the spec contains a keyword
- `field_exists`: a specific field path exists in the spec (e.g., `deck.wa_scorecard`)
- `count_gte`: count of elements matching criteria >= N

---

### 10. `tools/cost_calculator.py`

Estimates costs from a YAML spec using pricing KB.

**Requirements:**
- Class `CostCalculator` with method `calculate(spec_dict) -> CostEstimate`
- Loads pricing from `kb/pricing/database.yaml` (and future pricing files)
- For each service in the spec, looks up its type, maps to pricing, and estimates monthly cost
- Supports BYOL vs PAYG comparison
- CLI: `python tools/cost_calculator.py --spec examples/migration-adb-ha-dr.yaml`
- Output: JSON/YAML with per-component breakdown + totals

**Estimation logic:**
- ADB-S: OCPUs × rate/hour × 730 hours + storage × rate/TB
- Compute: OCPUs × rate/hour × 730 hours
- Apply BYOL discount if `licensing: BYOL` in spec
- Auto-scaling estimate: base + (peak_multiplier - 1) × base × peak_hours/730
- Mark all estimates with `estimated: true` flag

**This does NOT need to be exact.** Within 15% is fine. The goal is a defensible estimate the architect can present, not an invoice.

---

### 11. `tests/test_wa_scorer.py`

```python
"""Tests for wa_scorer.py"""

# test_all_five_pillars_scored: scorecard has entries for all 5 pillars
# test_database_in_private_subnet_passes: spec with DB in private subnet → SEC-DB-01 passes
# test_database_in_public_subnet_fails: spec with DB in public subnet → SEC-DB-01 fails
# test_waf_detected: spec with WAF service → network security check passes
# test_multi_region_detected: spec with 2 regions → DR check passes
# test_single_region_flags_dr: spec with 1 region → DR check flagged as gap
# test_adg_connection_satisfies_replication: ADG connection → data replication check passes
# test_conditional_check_skipped: distributed cloud checks skipped if single region
# test_scorecard_structure: output has pillar, status, checks_passed, checks_total, gaps
# test_gap_has_recommendation: every gap in output has a recommendation field
```

---

### 12. `tests/test_cost_calculator.py`

```python
"""Tests for cost_calculator.py"""

# test_adb_cost_in_range: ADB-S 8 OCPU / 2TB PAYG monthly is within expected range
# test_byol_cheaper_than_payg: BYOL total < PAYG total
# test_all_services_have_cost: every service in spec has a cost entry in output
# test_total_is_sum_of_components: total monthly equals sum of component monthlies
# test_auto_scaling_adds_cost: spec with auto-scaling has higher cost than without
# test_zero_services_zero_cost: empty spec produces zero cost
# test_unknown_service_uses_default: unrecognized service type gets a reasonable default or warning
# test_cost_marked_as_estimated: output has estimated=true flag
```

---

### 13. `tests/test_integration.py`

End-to-end integration tests that run the full pipeline.

```python
"""Integration tests — full pipeline from spec to outputs"""

# test_full_pipeline_deck:
#   Load sample spec → validate → generate deck → verify deck opens and has correct slides

# test_full_pipeline_drawio:
#   Load sample spec → validate → generate diagram → verify XML valid and styles correct

# test_full_pipeline_full_output:
#   Load sample spec → validate → run oci_output.py with --format full
#   → verify all expected files exist in output dir

# test_wa_scorer_matches_deck_scorecard:
#   Run WA scorer on spec → generate deck → verify deck slide 11 matches scorer output

# test_cost_calculator_matches_deck_costs:
#   Run cost calculator → generate deck → verify deck slide 7 totals match calculator output

# test_spec_validator_catches_bad_spec:
#   Load a deliberately broken spec → validate → verify errors detected
#   → verify generators refuse to run on invalid spec

# test_modify_spec_regenerate:
#   Generate outputs → modify spec (add a service) → regenerate → verify new service appears
```

---

### 14. `tests/fixtures/bad_spec_missing_tenancy.yaml`

A deliberately invalid spec for testing the validator:

```yaml
# Missing "tenancy" key entirely
title: "Bad spec"
connections:
  - {from: nonexistent1, to: nonexistent2, type: invalid_type}
```

---

### 15. `tests/fixtures/bad_spec_duplicate_ids.yaml`

```yaml
tenancy:
  label: "Test"
  regions:
    - id: region1
      label: "Test Region"
      vcns:
        - id: vcn1
          label: "Test VCN"
          subnets:
            - id: subnet1
              label: "Subnet A"
              services:
                - {id: svc1, label: "Service A", type: vm}
            - id: subnet1   # DUPLICATE ID
              label: "Subnet B"
              services:
                - {id: svc1, label: "Service B", type: adb}  # DUPLICATE ID
```

---

### 16. `tests/fixtures/minimal_valid_spec.yaml`

The smallest possible valid spec:

```yaml
tenancy:
  label: "Minimal Test"
  regions:
    - id: r1
      label: "Test Region"
      primary: true
      vcns:
        - id: vcn1
          label: "test-vcn 10.0.0.0/16"
          subnets:
            - id: sub1
              label: "Private Subnet"
              services:
                - {id: adb1, label: "ADB-S", type: adb}
          gateways: []
```

---

### 17. `.github/workflows/ci.yml`

GitHub Actions CI that runs on every push and PR:

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest
      - name: Validate project structure
        run: make validate
      - name: Lint KB files
        run: python tools/kb_linter.py
      - name: Run tests
        run: pytest tests/ -v --tb=short
      - name: Generate example outputs
        run: make full
      - name: Validate example spec
        run: python tools/spec_validator.py --spec examples/migration-adb-ha-dr.yaml
```

---

### 18. Update `Makefile`

Add test and lint targets:

```makefile
# Add these targets to the existing Makefile:

test:
	pytest tests/ -v --tb=short

test-quick:
	pytest tests/ -v --tb=short -x -q

lint-kb:
	python tools/kb_linter.py

validate-spec:
	python tools/spec_validator.py --spec examples/migration-adb-ha-dr.yaml

score-wa:
	python tools/wa_scorer.py --spec examples/migration-adb-ha-dr.yaml

estimate-cost:
	python tools/cost_calculator.py --spec examples/migration-adb-ha-dr.yaml

ci: validate lint-kb test full
	@echo "All CI checks passed"
```

---

### 19. Update `requirements.txt`

```
pyyaml>=6.0
python-pptx>=0.6.21
pytest>=7.0
```

---

## Build Order

Build in this exact sequence:

1. `tools/spec_validator.py` (other tools should call this before running)
2. `tools/kb_linter.py`
3. `tools/wa_scorer.py`
4. `tools/cost_calculator.py`
5. `tests/conftest.py`
6. `tests/fixtures/minimal_valid_spec.yaml`
7. `tests/fixtures/bad_spec_missing_tenancy.yaml`
8. `tests/fixtures/bad_spec_duplicate_ids.yaml`
9. `tests/test_diagram_gen.py`
10. `tests/test_deck_gen.py`
11. `tests/test_output_orchestrator.py`
12. `tests/test_spec_validator.py`
13. `tests/test_kb_linter.py`
14. `tests/test_wa_scorer.py`
15. `tests/test_cost_calculator.py`
16. `tests/test_integration.py`
17. `.github/workflows/ci.yml`
18. Updated `Makefile` (add test/lint/ci targets)
19. Updated `requirements.txt` (add pytest)

## Quality Criteria

- `pytest tests/ -v` passes with 0 failures
- `python tools/kb_linter.py` exits 0 with no failures
- `python tools/spec_validator.py --spec examples/migration-adb-ha-dr.yaml` exits 0
- `make ci` runs everything end-to-end without error
- Every test file has at least 8 test functions
- Every test has a descriptive name and a clear assertion
- test_diagram_gen.py has at least 20 tests covering XML validity, styles, hierarchy, connections, and edge cases
- test_deck_gen.py has at least 12 tests covering slide count, content, colors, and typography
- test_integration.py has at least 5 end-to-end tests
- The WA scorer detects at least 10 checks automatically from a spec
- The cost calculator produces estimates within 15% of manual calculation for the example spec
- The spec validator catches all 3 bad fixture files and produces clear error messages
- CI runs in under 60 seconds

## Test Philosophy

- **Test behavior, not implementation.** Don't test that a private method exists — test that the output has the right properties.
- **Test the contract.** The diagram generator's contract is: "given a valid spec, produce valid draw.io XML with OCI toolkit styles." Every test should verify part of that contract.
- **Test failure modes.** The spec validator must fail gracefully with clear messages, not crash with stack traces.
- **Integration tests are the most valuable.** A test that runs the full pipeline and verifies the output is worth more than 10 unit tests on internal functions.
- **Run tests after creating each tool.** Don't build all 4 tools then all tests. Build spec_validator → test_spec_validator → verify passing. Then kb_linter → test_kb_linter → verify. Incremental.

## Key Technical Context

Refer to the bootstrap prompt (Phase 1) for:
- OCI toolkit styles (container styles must match EXACTLY)
- Service category mapping (teal/copper/purple)
- Field knowledge facts (for WA auto-detection logic)
- YAML spec format (both diagram and deck keys)

## Final State

After Phase 2, the project has:

```
deal-accelerator/
├── SKILL.md
├── README.md
├── requirements.txt
├── Makefile
├── .github/workflows/ci.yml
│
├── tools/
│   ├── oci_diagram_gen.py
│   ├── oci_deck_gen.py
│   ├── oci_output.py
│   ├── spec_validator.py          ← NEW
│   ├── kb_linter.py               ← NEW
│   ├── wa_scorer.py               ← NEW
│   └── cost_calculator.py         ← NEW
│
├── tests/                          ← ALL NEW
│   ├── conftest.py
│   ├── test_diagram_gen.py
│   ├── test_deck_gen.py
│   ├── test_output_orchestrator.py
│   ├── test_spec_validator.py
│   ├── test_kb_linter.py
│   ├── test_wa_scorer.py
│   ├── test_cost_calculator.py
│   ├── test_integration.py
│   └── fixtures/
│       ├── minimal_valid_spec.yaml
│       ├── bad_spec_missing_tenancy.yaml
│       └── bad_spec_duplicate_ids.yaml
│
├── config/
├── kb/
├── examples/
└── codex/
```

Running `make ci` executes: validate → lint-kb → test → full output generation. All green = ready to ship.

Start building file 1.


---

## ░░░ MASTER BUILD ORDER ░░░

Build ALL files in this sequence. After each group, commit and verify.

### Group A: Foundation
1. `SKILL.md`
2. `README.md`
3. `kb/diagram/oci-toolkit-styles.yaml`

### Group B: Core Tools
4. `tools/oci_diagram_gen.py`
5. `tools/oci_deck_gen.py`
6. `tools/oci_output.py`
7. `tools/spec_validator.py`
8. `tools/findings_cli.py`
9. `tools/feature_matrix_cli.py`
10. `tools/kb_linter.py`
11. `tools/wa_scorer.py`
12. `tools/cost_calculator.py`
13. `tools/kb_cli.py`

### Group C: Configuration
14. `config/workload-profile-schema.yaml`
15. `config/service-categories.yaml`
16. `config/kb-governance.yaml`
17. `config/kb-owners.yaml`
18. `config/kb-tags.yaml`

### Group D: Knowledge Base
19. `kb/INDEX.yaml`
20. `kb/sizing/cpu-conversion-ratios.yaml`
21. `kb/services/adb-serverless.yaml`
22. `kb/services/exadata-cloud.yaml`
23. `kb/services/oci-networking-core.yaml`
24. `kb/patterns/database-ha-adb-s.yaml`
25. `kb/patterns/database-dr-cross-region.yaml`
26. `kb/patterns/networking-basic.yaml`
27. `kb/well-architected/security-compliance.yaml`
28. `kb/well-architected/reliability-resilience.yaml`
29. `kb/well-architected/performance-cost.yaml`
30. `kb/well-architected/operational-efficiency.yaml`
31. `kb/well-architected/distributed-cloud.yaml`
32. `kb/pricing/database.yaml`
33. `kb/competitive/aws-mapping.yaml`
34. `kb/field-knowledge/gotchas.yaml`
35. `kb/compatibility/adb-feature-matrix.yaml`
36. `kb/field-findings/tracker.yaml`

### Group E: Token Optimization
37. `SKILL_COMPACT.md`

### Group F: Examples
38. `examples/sample-discovery-notes.md`
39. `examples/sample-workload-profile.yaml`
40. `examples/migration-adb-ha-dr.yaml`

### Group G: Codex Packaging
41. `codex/SKILL.md`
42. `codex/skill.json`
43. `codex/README.md`

### Group H: Project Files
44. `requirements.txt`
45. `Makefile`
46. `.github/workflows/ci.yml`

### Group I: Tests
47. `tests/conftest.py`
48. `tests/fixtures/minimal_valid_spec.yaml`
49. `tests/fixtures/bad_spec_missing_tenancy.yaml`
50. `tests/fixtures/bad_spec_duplicate_ids.yaml`
51. `tests/test_diagram_gen.py`
52. `tests/test_deck_gen.py`
53. `tests/test_output_orchestrator.py`
54. `tests/test_spec_validator.py`
55. `tests/test_kb_linter.py`
56. `tests/test_wa_scorer.py`
57. `tests/test_cost_calculator.py`
58. `tests/test_feature_matrix.py`
59. `tests/test_findings_tracker.py`
60. `tests/test_integration.py`

### Final Verification
```bash
make validate  # Structure and imports
make lint-kb   # KB file format
make test      # All tests pass
make full      # Generate example outputs
make ci        # Full CI pipeline
```

## START BUILDING. Begin with Group A, file 1 (SKILL.md).
