# OCI Deal Accelerator

AI skill aligned with Oracle ECAL framework (Define → Design → Deliver) that compresses the OCI SA's cycle from customer discovery to architecture proposal and delivery handover — from days to hours.

## Project Structure

```
├── SKILL.md                    # LLM system prompt (the skill itself)
├── README.md                   # Project overview and quick start
├── CLAUDE.md                   # This file (dev guide)
├── Makefile                    # Build automation (make help for commands)
├── docs/                       # ECAL phase guides (progressive disclosure from SKILL.md)
│   ├── define-phase.md         # DEFINE phase detailed guide
│   ├── design-phase.md         # DESIGN phase detailed guide
│   ├── deliver-phase.md        # DELIVER phase detailed guide
│   ├── engagement-tiers.md     # Tier definitions and artifact matrix
│   └── ecal-gaps-backlog.md    # Remaining ECAL gaps to implement (20 items)
├── kb/                         # Knowledge Base
│   ├── architecture-center/    # Oracle Architecture Center reference catalog
│   │   └── catalog.yaml        # 123 curated reference architectures
│   ├── services/               # One YAML per OCI service (what, when, gotchas)
│   ├── patterns/               # Composable architecture blocks
│   │   ├── business-patterns.yaml    # Business-level patterns (DEFINE)
│   │   ├── application-patterns.yaml # Application architecture patterns (DESIGN)
│   │   ├── service-tiering.yaml      # Service tier model (Platinum/Gold/Silver/Bronze)
│   │   ├── architecture-principles.yaml # ECAL principles (Design/Deployment/Service)
│   │   ├── operational-raci.yaml     # RACI matrix templates (3 operational models)
│   │   ├── engagement-raci.yaml     # ECAL engagement RACI (10 roles, all 9 steps)
│   │   ├── business-drivers.yaml    # 4-pillar business drivers + hypothesis families
│   │   ├── ecal-artefacts-catalog.yaml # Complete ECAL 3.1 artefacts catalog (60 items)
│   │   ├── environment-catalogue.yaml # Environment templates per tier
│   │   ├── database-ha-adb-s.yaml
│   │   ├── database-dr-cross-region.yaml
│   │   ├── networking-basic.yaml
│   │   └── (dirs: database-ha/, database-dr/, networking-hub-spoke/, etc.)
│   ├── sizing/                 # CPU conversion ratios, IOPS, scaling rules
│   ├── pricing/                # Simplified pricing for estimation
│   ├── competitive/            # AWS/Azure/GCP service mapping
│   ├── well-architected/       # 5-pillar WA Framework checklists
│   ├── compatibility/          # Feature matrices (ADB, etc.)
│   ├── diagram/                # Diagram styles (OCI Toolkit v24.2)
│   └── field-knowledge/        # Real-world gotchas and lessons learned
├── tools/                      # Python tooling
│   ├── oci_deck_gen.py         # .pptx slide deck generator (DEFAULT output)
│   ├── oci_pdf_gen.py          # .pdf customer-facing document (branded, no internal refs)
│   ├── oci_diagram_gen.py      # .drawio diagram generator
│   ├── oci_output.py           # Output orchestrator
│   └── refresh_arch_catalog.py # Architecture Center catalog refresh tool
├── scripts/                    # Validation and utilities
│   └── validate-architecture.py # WA validation engine
├── config/
│   ├── service-categories.yaml # Service → color/category mapping
│   ├── output-formats.yaml     # Output format specs and design standards
│   ├── engagement-tiers.yaml   # Tier definitions (small/standard/complex)
│   ├── workload-profile-schema.yaml # Workload profile field definitions
│   └── oracle-pptx-layouts.yaml # Oracle FY26 POTX layout mapping for deck generation
├── templates/                  # ECAL phase templates
│   ├── Oracle_PPT-template_FY26.pptx # Official Oracle FY26 PowerPoint template
│   ├── workload-profile.yaml   # DEFINE: Discovery capture
│   ├── customer-profile.yaml   # DEFINE: Strategic customer profiling (internal)
│   ├── strategy-map.yaml       # DEFINE: Goals→Strategies→Capabilities→Enablers
│   ├── discovery-questionnaire.yaml # DESIGN: Structured customer IT collection
│   ├── business-case.yaml      # DEFINE: Business case for customer approval
│   ├── value-story.yaml        # DEFINE: Business value hypothesis
│   ├── joint-engagement-plan.yaml # DEFINE: Engagement scoping
│   ├── scorecard.yaml          # DESIGN: WA validation results
│   ├── adr-template.md         # DESIGN: Architecture Decision Records
│   ├── operations-model.yaml   # DESIGN: Day-2 operations design
│   ├── handover-document.yaml  # DELIVER: Implementation handover
│   ├── go-live-checklist.yaml  # DELIVER: Pre-cutover verification
│   ├── success-criteria.yaml   # DELIVER: Post go-live metrics
│   └── lessons-learned.yaml    # DELIVER: Engagement retrospective
├── codex/                      # Codex skill packaging
└── examples/                   # Example specs and generated outputs
```

## ECAL-Aligned Workflow

```
DEFINE (Ideate → Validate → Plan)  →  DESIGN (Current → Future → Confirm)  →  DELIVER (Adopt → Operate → Improve)
```

1. **DEFINE**: Discovery notes → Workload Profile + Value Story + Joint Engagement Plan
2. **DESIGN**: Current state (people/process/tech) → Architecture + Operations Model → Solution Proposal
3. **DELIVER**: Handover Document → Go-Live Checklist + Success Criteria → Lessons Learned

Phase details in `docs/` — SKILL.md references them via progressive disclosure.

## Output Formats

Default output is a **slide deck (.pptx)** — adapts to engagement tier (6-8 / 10-12 / 12-16 slides).

```
deck              ← default
deck + drawio     ← + editable diagram
deck + doc        ← + technical document
deck + xlsx       ← + cost spreadsheet
deck + pdf        ← + customer-facing PDF (branded, no internal refs)
pdf               ← customer PDF only
full              ← everything (pptx + drawio + docx + xlsx + pdf)
doc only          ← technical doc without slides
deliver           ← handover + go-live checklist + success criteria
```

## Running Tools

```bash
# Generate slide deck (default output)
python tools/oci_deck_gen.py --spec examples/proposal-spec.yaml --output proposal.pptx

# Generate customer-facing PDF (branded, no internal KB refs)
python tools/oci_pdf_gen.py --spec examples/proposal-spec.yaml --output proposal.pdf
python tools/oci_pdf_gen.py --spec examples/proposal-spec.yaml --output proposal.pdf --diagram arch.png

# Generate diagram
python tools/oci_diagram_gen.py --spec examples/diagram-spec.yaml --output arch.drawio

# Run WA validation
python scripts/validate-architecture.py \
  --profile examples/sample-workload-profile.yaml \
  --architecture examples/sample-architecture.yaml \
  --output scorecard.yaml

# Output orchestrator (multiple formats at once)
python tools/oci_output.py --spec examples/proposal-spec.yaml --format full --output-dir output/

# Refresh Architecture Center catalog
python tools/refresh_arch_catalog.py --whats-new      # crawl What's New pages
python tools/refresh_arch_catalog.py --url <url>       # add single entry
python tools/refresh_arch_catalog.py --validate        # validate catalog

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
- **ECAL-aligned** — Define → Design → Deliver with iterative checkpoints

## Welcome Flow

When the user starts a conversation without providing discovery notes or a specific request (e.g., a greeting like "hola", "hey", or empty context), present the welcome message and capability menu defined in `SKILL.md` § Welcome Flow. Specifically:

1. Show the welcome banner and numbered capability menu from SKILL.md
2. Follow the behavior rules for each option (1-10)
3. After completing any task, offer the next-step menu (A-E)
4. If the user sends discovery notes directly, skip the menu and go straight to full proposal flow
5. If the user asks a specific question, skip the menu and answer directly
