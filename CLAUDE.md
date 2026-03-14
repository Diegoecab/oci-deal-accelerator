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
│   │   ├── database-ha/        # HA patterns (Active Data Guard, etc.)
│   │   ├── database-dr/        # DR patterns
│   │   ├── compute-scaling/    # Auto-scaling, OKE patterns
│   │   ├── networking-hub-spoke/ # Hub-spoke via DRG
│   │   ├── security-baseline/  # CIS baseline, security controls
│   │   └── compliance-pci/     # PCI-DSS overlay
│   ├── sizing/                 # CPU conversion ratios, IOPS, scaling rules
│   ├── pricing/                # Simplified pricing for estimation
│   ├── competitive/            # AWS/Azure/GCP service mapping
│   ├── well-architected/       # 5-pillar WA Framework checklists
│   ├── diagram/                # Diagram styles (OCI Toolkit v24.2)
│   └── field-knowledge/        # Real-world gotchas and lessons learned
├── tools/                      # Python tooling
│   └── oci_diagram_gen.py      # .drawio diagram generator
├── scripts/                    # Validation and utilities
│   ├── oci_diagram_gen.py      # Diagram generator (also in tools/)
│   └── validate-architecture.py # WA validation engine
├── config/
│   └── service-categories.yaml # Service → color/category mapping
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
4. **Outputs**: ADRs, cost estimate, .drawio diagram, scorecard, risk register

## Running Tools

```bash
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
