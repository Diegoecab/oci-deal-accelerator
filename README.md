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

## Tools

```bash
python tools/oci_deck_gen.py --spec examples/proposal-spec.yaml --output proposal.pptx
python tools/oci_diagram_gen.py --spec examples/diagram-spec.yaml --output arch.drawio
python scripts/validate-architecture.py --profile examples/sample-workload-profile.yaml --architecture examples/sample-architecture.yaml --output scorecard.yaml
make help    # all commands
```

## Requirements

- Python 3.8+
- `pip install pyyaml python-pptx`
- No OCI CLI or SDK needed (the skill designs, it doesn't deploy)

## License

Internal use. Not for distribution.
