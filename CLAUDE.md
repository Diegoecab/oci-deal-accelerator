# OCI Deal Accelerator

AI skill aligned with Oracle ECAL framework (Define → Design → Deliver) that compresses the OCI SA's cycle from customer discovery to architecture proposal and delivery handover — from days to hours.

## Project Structure

```
├── SKILL.md                    # LLM system prompt (the skill itself)
├── AGENTS.md                   # Codex agent instructions (mirrors CLAUDE.md)
├── .agents/skills/oci-deal-accelerator/
│   └── SKILL.md                # Codex skill definition (full skill, Codex format)
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
│   ├── pricing/                # Auto-refreshed from Oracle public pricing API
│   │   ├── oci-sku-catalog.yaml  # 200+ OCI SKUs across 20 categories (BOM source of truth)
│   │   └── compute.yaml          # Shape-level estimation pricing
│   ├── competitive/            # AWS/Azure/GCP service mapping
│   ├── well-architected/       # 5-pillar WA Framework checklists
│   ├── compatibility/          # Feature matrices (ADB, etc.)
│   ├── diagram/                # Diagram styles (OCI Toolkit v24.2)
│   └── field-knowledge/        # Real-world gotchas and lessons learned
├── tools/                      # Python tooling
│   ├── oci_deck_gen.py         # .pptx slide deck generator (DEFAULT output)
│   ├── oci_pdf_gen.py          # .pdf customer-facing document (branded, no internal refs)
│   ├── oci_diagram_gen.py      # .drawio diagram generator
│   ├── oci_bom_gen.py          # .xlsx Bill of Materials generator (SA tool)
│   ├── oci_output.py           # Output orchestrator
│   ├── refresh_sku_catalog.py  # SKU catalog refresh from Oracle pricing API
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
│   ├── lessons-learned.yaml    # DELIVER: Engagement retrospective
│   └── bom-spec.yaml          # SA TOOL: BOM input spec template
├── codex/                      # Codex setup guide (README only)
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

## Environment Setup

Before running ANY Python tool, ensure dependencies are installed:

```bash
make venv && source .venv/bin/activate
```

The Makefile auto-detects the best available Python (3.12 > 3.11 > 3.10 > python3).
**Always use `make <target>` to run tools** — this guarantees the correct Python with all dependencies.

## Running Tools

Prefer `make` targets. For custom specs, activate the venv first (`source .venv/bin/activate`), then use `python`:

```bash
# Standard targets (recommended)
make deck                    # slide deck with sample spec
make diagram                 # architecture diagram
make full                    # all outputs (pptx + drawio + docx + xlsx + pdf)
make validate                # WA validation
make lint                    # check YAML syntax
make venv                    # create/update virtual environment
make freshness               # check KB freshness

# Custom specs (activate venv first)
python tools/oci_deck_gen.py --spec examples/proposal-spec.yaml --output proposal.pptx
python tools/oci_pdf_gen.py --spec examples/proposal-spec.yaml --output proposal.pdf
python tools/oci_bom_gen.py --spec examples/bom-spec.yaml --output customer-bom.xlsx
python tools/oci_diagram_gen.py --spec examples/diagram-spec.yaml --output arch.drawio
python tools/oci_output.py --spec examples/proposal-spec.yaml --format full --output-dir output/

# KB maintenance (activate venv first)
python tools/refresh_sku_catalog.py --refresh          # update all prices
python tools/refresh_sku_catalog.py --refresh --diff   # update + show changes
python tools/refresh_sku_catalog.py --validate         # check for stale prices
python tools/refresh_arch_catalog.py --whats-new       # crawl What's New pages
python tools/refresh_arch_catalog.py --validate        # validate catalog
```

## Key Principles

- **Empirical over theoretical** — cite metrics, not marketing
- **Simplicity first** — complexity must be earned
- **Honest about limitations** — acknowledge OCI gaps
- **Composable** — patterns combine, not monolithic templates
- **KB is the moat** — field experience, not documentation regurgitation
- **ECAL-aligned** — Define → Design → Deliver with iterative checkpoints

## Git Remotes (Gitea = source of truth, GitHub = mirror)

`origin` is configured with **one fetch URL (Gitea) and two push URLs (Gitea + GitHub)**, so a single `git push origin main` updates both. Gitea is authoritative; GitHub is a public mirror.

```
fetch  → git.tech-lad.com.br/diegoecab/oci-deal-accelerator.git
push   → git.tech-lad.com.br/diegoecab/oci-deal-accelerator.git
push   → github.com/Diegoecab/oci-deal-accelerator.git
```

**Recreating this on a new clone** (the dual-push lives in `.git/config`, not tracked):

```bash
git remote set-url --add --push origin https://github.com/Diegoecab/oci-deal-accelerator.git
git remote set-url --add --push origin https://git.tech-lad.com.br/diegoecab/oci-deal-accelerator.git
git remote -v   # confirm one fetch + two push URLs
```

The first command substitutes the implicit Gitea push URL with GitHub's; the second re-adds Gitea so origin pushes to BOTH. Counter-intuitive but necessary.

**Agent guidance**:
- After creating a commit on `main`, **always propose `git push origin main`** (not separate pushes per remote) — it covers both. Confirm with the user before pushing (pushing is shared-state).
- If a push fails on GitHub but succeeds on Gitea (or vice versa), the dual-push is partial. Re-run after fixing the failing one — Gitea's second push will be a no-op fast-forward.
- Never force-push Gitea unless explicitly asked; force-pushing GitHub is acceptable when needed because GitHub is downstream.
- If history diverges between Gitea and GitHub (e.g. after a rebase), the recovery pattern is: temporarily strip the GitHub URL (`git remote set-url --delete --push origin <github-url>`), push Gitea fast-forward, add `github` as a standalone remote, force-push, then restore the dual-push.

## Coding Guidelines

### 1. Think Before Coding
Don't assume. Don't hide confusion. Surface tradeoffs.
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First
Minimum code that solves the problem. Nothing speculative.
- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

### 3. Surgical Changes
Touch only what you must. Clean up only your own mess.
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.
- Remove imports/variables/functions that YOUR changes made unused.
- Every changed line should trace directly to the user's request.

### 4. Goal-Driven Execution
Define success criteria. Loop until verified.
- "Add validation" → write tests for invalid inputs, then make them pass.
- "Fix the bug" → write a test that reproduces it, then make it pass.
- "Refactor X" → ensure tests pass before and after.
- For multi-step tasks, state a brief plan with verification steps.

## Welcome Flow

When the user starts a conversation without providing discovery notes or a specific request (e.g., a greeting like "hola", "hey", or empty context):

**MANDATORY:** Use the `Read` tool to open `SKILL.md` and read the entire `## Welcome Flow` section **before** showing anything to the user. Reproduce the welcome banner and the 14-option capability menu **verbatim** from that file. Do NOT paraphrase, reorder, summarize, translate, or reconstruct the menu from memory, folder structure, or prior conversations. If `SKILL.md` cannot be read for any reason, tell the user instead of improvising a menu.

**Pre-flight check (also defined in SKILL.md):** Before showing the welcome message, run `make kb-check 2>/dev/null`. If `stale_count > 0`, follow the banner-and-prompt logic in SKILL.md § Welcome Flow → Pre-flight. If the tool errors, silently skip the banner — never block the user.

Then:

1. Show the welcome banner and numbered capability menu exactly as defined in SKILL.md (14 options across DESIGN & PROPOSE, VALIDATE & CHECK, STRATEGY & BUSINESS, KNOWLEDGE BASE, ECAL GOVERNANCE, SA TOOLS)
2. Follow the behavior rules in SKILL.md for each option (1-14)
3. After completing any task, offer the next-step menu (A-E) as defined in SKILL.md
4. If the user sends discovery notes directly, skip the menu and go straight to full proposal flow
5. If the user asks a specific question, skip the menu and answer directly
