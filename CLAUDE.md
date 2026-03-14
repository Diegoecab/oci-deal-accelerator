# OCI Deal Accelerator

AI skill that compresses the OCI Solutions Architect's cycle from customer discovery to architecture proposal — from days to hours.

## Project Structure

```
├── SKILL.md                    # LLM system prompt (the skill itself)
├── README.md                   # Project overview and quick start
├── CLAUDE.md                   # This file (dev guide)
├── Makefile                    # Build automation (make help for commands)
├── kb/                         # Knowledge Base
│   ├── services/               # One YAML per OCI service (what, when, gotchas)
│   │   ├── adb-serverless.yaml
│   │   ├── exadata-cloud.yaml
│   │   ├── oke.yaml
│   │   └── oci-networking-core.yaml
│   ├── patterns/               # Composable architecture blocks
│   │   ├── database-ha-adb-s.yaml
│   │   ├── database-dr-cross-region.yaml
│   │   ├── networking-basic.yaml
│   │   └── (legacy dirs: database-ha/, database-dr/, etc.)
│   ├── sizing/                 # CPU conversion ratios, IOPS, scaling rules
│   │   ├── cpu-conversion-ratios.yaml
│   │   └── storage-iops.yaml
│   ├── pricing/                # Simplified pricing for estimation
│   │   └── database.yaml
│   ├── competitive/            # AWS/Azure/GCP service mapping
│   │   └── aws-mapping.yaml
│   ├── well-architected/       # 5-pillar WA Framework checklists
│   ├── diagram/                # Diagram styles (OCI Toolkit v24.2)
│   └── field-knowledge/        # Real-world gotchas and lessons learned
├── tools/                      # Python tooling
│   ├── oci_deck_gen.py         # .pptx slide deck generator (DEFAULT output)
│   ├── oci_diagram_gen.py      # .drawio diagram generator
│   └── oci_output.py           # Output orchestrator
├── scripts/                    # Validation and utilities
│   └── validate-architecture.py # WA validation engine
├── config/
│   ├── service-categories.yaml # Service → color/category mapping
│   ├── output-formats.yaml     # Output format specs and design standards
│   └── workload-profile-schema.yaml # Workload profile field definitions
├── templates/                  # Output templates (workload profile, scorecard, ADR)
├── codex/                      # Codex skill packaging
│   ├── skill.json
│   ├── SKILL.md
│   └── README.md
└── examples/                   # Example specs and generated outputs
```

## Workflow

```
Discovery Notes → Workload Profile → Architecture Composition → WA Validation → Outputs
```

1. **Discovery**: Unstructured notes parsed into structured Workload Profile (YAML)
2. **Composition**: Services selected from `kb/services/`, composed from `kb/patterns/`, sized from `kb/sizing/`
3. **Validation**: Auto-validated against 5 WA pillars (`kb/well-architected/`)
4. **Outputs**: Slide deck (.pptx) by default + optional .drawio, .docx, .xlsx

## Output Formats

Default output is a **slide deck (.pptx)** — 10-12 slides ready for customer meeting.

```
deck              ← default
deck + drawio     ← + editable diagram
deck + doc        ← + technical document
deck + xlsx       ← + cost spreadsheet
full              ← everything
doc only          ← technical doc without slides
```

## Running Tools

```bash
# Generate slide deck (default output)
python tools/oci_deck_gen.py --spec examples/proposal-spec.yaml --output proposal.pptx

# Generate diagram
python tools/oci_diagram_gen.py --spec examples/diagram-spec.yaml --output arch.drawio

# Run WA validation
python scripts/validate-architecture.py \
  --profile examples/sample-workload-profile.yaml \
  --architecture examples/sample-architecture.yaml \
  --output scorecard.yaml

# Output orchestrator (multiple formats at once)
python tools/oci_output.py --spec examples/proposal-spec.yaml --format full --output-dir output/

# Build automation
make help           # show all commands
make full           # generate all outputs
make validate       # run WA validation
make lint           # check YAML syntax
```

## Key Principles

- **Empirical over theoretical** — cite metrics, not marketing
- **Simplicity first** — complexity must be earned
- **Honest about limitations** — acknowledge OCI gaps
- **Composable** — patterns combine, not monolithic templates
- **KB is the moat** — field experience, not documentation regurgitation
