# OCI Deal Accelerator

AI-powered tool for Oracle Solutions Architects to rapidly compose, validate, and document OCI architectures.

## Project Structure

```
oci-deal-accelerator/
├── CLAUDE.md                           # This file
├── prompts/
│   └── deal-accelerator.md             # Main system prompt for the Deal Accelerator
├── kb/
│   └── well-architected/
│       ├── security-compliance.yaml    # Pillar 1: Security & Compliance checks
│       ├── reliability-resilience.yaml # Pillar 2: Reliability & Resilience checks
│       ├── performance-cost.yaml       # Pillar 3: Performance & Cost checks
│       ├── operational-efficiency.yaml # Pillar 4: Operational Efficiency checks
│       ├── distributed-cloud.yaml      # Pillar 5: Distributed Cloud checks
│       ├── landing-zones.yaml          # OCI Landing Zone patterns
│       └── personas.yaml              # Role-to-pillar output targeting
├── templates/
│   ├── workload-profile.yaml          # Discovery output template
│   ├── scorecard.yaml                 # WA Scorecard output template
│   └── adr-template.md               # Architecture Decision Record template
├── scripts/
│   └── validate-architecture.py       # WA validation engine
└── examples/
    ├── sample-architecture.yaml       # Example architecture (e-commerce)
    └── sample-workload-profile.yaml   # Example workload profile
```

## Flow

```
Discovery → Workload Profile → Architecture Composition → WA Validation → Outputs
```

1. **Discovery**: Gather customer requirements using structured questions
2. **Workload Profile**: Capture findings in `templates/workload-profile.yaml` format
3. **Architecture Composition**: Design OCI architecture based on workload profile
4. **WA Validation**: Auto-validate against 5 Well-Architected pillars (kb/well-architected/)
5. **Outputs**: ADRs, cost estimates, diagrams, scorecard, roadmap

## Well-Architected Framework

Reference: https://docs.oracle.com/en/solutions/oci-best-practices/index.html

The 5 pillars are defined as YAML checklists in `kb/well-architected/`. Each check has:
- `auto_detect` rules (pass_if / gap_if)
- `severity` (HIGH / MEDIUM / LOW)
- `applies_when` conditions based on workload profile flags

## Running Validation

```bash
python scripts/validate-architecture.py \
  --profile examples/sample-workload-profile.yaml \
  --architecture examples/sample-architecture.yaml \
  --output scorecard-output.yaml
```

## Key Design Decisions

- Validation is **automatic** — inferred from architecture + workload profile, no manual checklists
- Scorecard is a **standard output** alongside ADRs, cost estimates, and diagrams
- Output emphasis is **persona-driven** based on `decision_drivers.political.primary_audience`
- Checks are **conditional** — only applicable checks are evaluated based on workload flags
