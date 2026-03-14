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

The skill will produce the full architecture package.

### Slide Deck Generator (default output)

```bash
# Generate a proposal deck from YAML spec
python tools/oci_deck_gen.py --spec examples/proposal-spec.yaml --output proposal.pptx
```

### Diagram Generator

```bash
# Generate architecture diagram
python tools/oci_diagram_gen.py --spec examples/diagram-spec.yaml --output architecture.drawio
```

### Output Selection

The architect can choose which outputs to generate:
```
deck              ← default, 10-12 slide .pptx
deck + drawio     ← deck + editable .drawio diagram
deck + doc        ← deck + detailed .docx technical document
deck + xlsx       ← deck + cost spreadsheet
full              ← everything
doc only          ← technical document without slides
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
│   │   ├── exadata-cloud.yaml
│   │   ├── oke.yaml
│   │   ├── oci-networking-core.yaml
│   │   └── ...
│   ├── patterns/               # Composable architecture blocks
│   │   ├── database-ha-adb-s.yaml
│   │   ├── database-dr-cross-region.yaml
│   │   ├── networking-basic.yaml
│   │   └── ...
│   ├── sizing/                 # Conversion ratios, benchmarks, scaling rules
│   │   ├── cpu-conversion-ratios.yaml
│   │   └── storage-iops.yaml
│   ├── pricing/                # Simplified pricing for estimation
│   │   └── database.yaml
│   ├── competitive/            # Service mapping vs other clouds
│   │   └── aws-mapping.yaml
│   ├── well-architected/       # Oracle WA Framework checklists
│   │   ├── security-compliance.yaml
│   │   ├── reliability-resilience.yaml
│   │   ├── performance-cost.yaml
│   │   ├── operational-efficiency.yaml
│   │   ├── distributed-cloud.yaml
│   │   ├── landing-zones.yaml
│   │   └── personas.yaml
│   ├── diagram/                # Diagram generation styles and layouts
│   │   ├── oci-toolkit-styles.yaml
│   │   └── reference-layouts/
│   └── field-knowledge/        # Real-world gotchas and lessons learned
│       └── gotchas.yaml
│
├── tools/                      # Python tooling
│   ├── oci_deck_gen.py         # .pptx slide deck generator (default output)
│   ├── oci_diagram_gen.py      # .drawio diagram generator
│   └── oci_output.py           # Output orchestrator
│
├── scripts/                    # Additional scripts
│   └── validate-architecture.py # WA validation engine
│
├── config/                     # Configuration
│   ├── service-categories.yaml # Service → color/category mapping
│   ├── output-formats.yaml    # Output format specs and design standards
│   └── workload-profile-schema.yaml # Field definitions
│
├── templates/                  # Output templates
│   ├── workload-profile.yaml
│   ├── scorecard.yaml
│   └── adr-template.md
│
├── codex/                      # Codex skill packaging
│   ├── skill.json
│   ├── SKILL.md
│   └── README.md
│
└── examples/                   # Example specs and outputs
    ├── diagram-spec.yaml
    ├── proposal-spec.yaml          # Slide deck spec (YAML → .pptx)
    ├── migration-adb-ha-dr.yaml    # ADB HA/DR diagram spec
    ├── sample-discovery-notes.md   # Realistic messy notes
    ├── sample-architecture.yaml
    ├── sample-workload-profile.yaml
    ├── ecommerce-architecture.drawio
    ├── scorecard-output.yaml
    └── sample-output/
        └── architecture-proposal.pptx  # Generated slide deck
```

## How the Knowledge Base Works

The KB is consumed by both the LLM (via SKILL.md references) and the Python tools. Every KB file uses YAML with structured fields for service details, sizing rules, gotchas, and competitive comparisons.

Example service entry:
```yaml
# kb/services/adb-serverless.yaml
service:
  name: "Autonomous Database"
  category: database
  color: "#AA643B"

when_to_use:
  - "Oracle Database workloads migrating to cloud"
  - "Need automated patching, tuning, and scaling"

gotchas:
  - description: "Auto-scaling takes 2-3 minutes. Size base OCPUs for P75."
    severity: MEDIUM

sizing:
  adb_s:
    sizing_guidance: "Size base OCPUs for P75 sustained load, not P50."
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

## Running the Tools

### WA Validation Engine

```bash
python scripts/validate-architecture.py \
  --profile examples/sample-workload-profile.yaml \
  --architecture examples/sample-architecture.yaml \
  --output scorecard-output.yaml
```

### Diagram Generator

```bash
python tools/oci_diagram_gen.py \
  --spec examples/diagram-spec.yaml \
  --output architecture.drawio
```

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

- Python 3.8+ (for generators)
- PyYAML (`pip install pyyaml`)
- python-pptx (`pip install python-pptx`) — for slide deck generation
- python-docx (`pip install python-docx`) — for document generation (optional)
- openpyxl (`pip install openpyxl`) — for spreadsheet generation (optional)
- No OCI CLI or SDK needed (the skill designs, it doesn't deploy)

## License

Internal use. Not for distribution.
