# OCI Deal Accelerator

AI skill that compresses the OCI Solutions Architect's cycle from customer discovery to architecture proposal — from days to hours.

## Project Structure

```
├── SKILL.md                    # LLM system prompt (the skill itself)
├── README.md                   # Project overview and quick start
├── CLAUDE.md                   # This file (dev guide)
├── kb/                         # Knowledge Base
│   ├── services/               # One YAML per OCI service (what, when, gotchas)
│   ├── patterns/               # Composable architecture blocks
│   ├── sizing/                 # CPU conversion ratios, IOPS, scaling rules
│   ├── pricing/                # Simplified pricing for estimation
│   ├── competitive/            # AWS/Azure/GCP service mapping
│   ├── well-architected/       # 5-pillar WA Framework checklists
│   ├── diagram/                # Diagram styles (OCI Toolkit v24.2)
│   └── field-knowledge/        # Real-world gotchas and lessons learned
├── tools/                      # Python tooling
│   ├── oci_slide_gen.py        # .pptx slide deck generator (DEFAULT output)
│   └── oci_diagram_gen.py      # .drawio diagram generator
├── scripts/                    # Validation and utilities
│   ├── oci_diagram_gen.py      # Diagram generator (also in tools/)
│   └── validate-architecture.py # WA validation engine
├── config/
│   ├── service-categories.yaml # Service → color/category mapping
│   └── output-formats.yaml    # Output format specs and design standards
├── templates/                  # Output templates (workload profile, scorecard, ADR)
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
python tools/oci_slide_gen.py --spec examples/proposal-spec.yaml --output proposal.pptx

# Generate diagram
python tools/oci_diagram_gen.py --spec examples/diagram-spec.yaml --output arch.drawio

# Run WA validation
python scripts/validate-architecture.py \
  --profile examples/sample-workload-profile.yaml \
  --architecture examples/sample-architecture.yaml \
  --output scorecard.yaml
```

## Key Principles

- **Empirical over theoretical** — cite metrics, not marketing
- **Simplicity first** — complexity must be earned
- **Honest about limitations** — acknowledge OCI gaps
- **Composable** — patterns combine, not monolithic templates
- **KB is the moat** — field experience, not documentation regurgitation
