# OCI Deal Accelerator — Codex Setup

## Quick Start

### Option 1: Using Codex CLI (recommended)

```bash
# Navigate to the project root
cd oci-deal-accelerator

# One-time: create virtual environment with all dependencies
make venv

# Run Codex — it auto-discovers AGENTS.md, .agents/skills/, and .codex/config.toml
codex

# Or explicitly load the skill
codex --skill oci-deal-accelerator
```

Codex automatically reads:
- `AGENTS.md` at project root (project-level instructions)
- `.agents/skills/oci-deal-accelerator/SKILL.md` (the skill definition)
- `.codex/config.toml` (project sandbox + approval config — **enables network for pip**)

### Why `.codex/config.toml` matters

By default Codex CLI blocks network access and prompts before every command.
The committed `.codex/config.toml` pre-configures this project with:

- `approval_policy = "never"` — no per-command prompts
- `sandbox_mode = "workspace-write"` — agent can write in the repo
- `network_access = true` — `pip install` and `make venv` actually work

Without this file, `make venv` fails with `No matching distribution found for pyyaml` because PyPI is unreachable from the sandbox.

### Option 2: Using Codex App

1. Open the Codex app
2. Point it to this repository
3. The skill is auto-discovered from `.agents/skills/`

## File Structure (Codex-Specific)

```
├── AGENTS.md                                    # Project instructions (Codex reads this)
├── .agents/
│   └── skills/
│       └── oci-deal-accelerator/
│           └── SKILL.md                         # Full skill definition (Codex skill format)
├── codex/
│   └── README.md                                # This file (setup guide)
├── kb/                                          # Knowledge Base (shared with all LLM targets)
├── tools/                                       # Python tooling (shared)
├── templates/                                   # ECAL phase templates (shared)
├── config/                                      # Configuration (shared)
└── examples/                                    # Example specs and outputs
```

## How It Works

### AGENTS.md vs SKILL.md

- **AGENTS.md** (project root): Codex reads this automatically when you open the project. It contains project structure, build commands, and conventions — equivalent to Claude Code's `CLAUDE.md`.
- **SKILL.md** (`.agents/skills/oci-deal-accelerator/`): The full skill definition with the welcome flow, ECAL workflow, output generation, guardrails, and multi-agent mode. Codex discovers this automatically from the `.agents/skills/` directory.

### AGENTS.override.md

If you need temporary overrides (e.g., focusing on a specific customer engagement), create an `AGENTS.override.md` at project root. It takes highest priority:

```markdown
# Override: Acme Corp Engagement

Focus on the Acme Corp engagement. The customer is migrating 5 Oracle 19c
databases from on-prem Exadata to OCI. Key constraints:
- Must use BYOL (ULA in place)
- PCI-DSS compliance required
- 4-hour RTO, 1-hour RPO
- Timeline: 12 weeks
```

## What the Skill Does

Takes unstructured customer discovery notes and produces:
- Architecture slide deck (.pptx) with Oracle FY26 branding
- Editable architecture diagram (.drawio) with official OCI styles
- Customer-facing PDF (branded, no internal KB refs)
- Cost estimates (PAYG vs BYOL breakdown)
- Well-Architected Framework scorecard
- Business case with TCO/ROI analysis
- ECAL readiness score (60 artefacts)
- Handover documents, go-live checklists, lessons learned

## 12 Capabilities

| # | Capability | Category |
|---|-----------|----------|
| 1 | Full proposal from discovery notes | Design & Propose |
| 2 | Generate architecture diagram | Design & Propose |
| 3 | Generate slide deck | Design & Propose |
| 4 | Cost estimate | Design & Propose |
| 5 | Well-Architected review | Validate & Check |
| 6 | Feature compatibility check | Validate & Check |
| 7 | Competitive comparison | Validate & Check |
| 8 | Business case builder | Strategy & Business |
| 9 | Search field findings | Knowledge Base |
| 10 | Find reference architecture | Knowledge Base |
| 11 | Report a field finding | Knowledge Base |
| 12 | ECAL readiness score | ECAL Governance |

## Multi-Agent Mode

When running in Codex with multiple agents enabled, the skill splits into:

- **Agent 1 (Architect)**: DEFINE + DESIGN phases — parses discovery, composes architecture
- **Agent 2 (Validator)**: WA validation — scores against 5 pillars
- **Agent 3 (Renderer)**: Output generation — deck, diagram, PDF, cost spreadsheet

Each agent reads the same KB but focuses on its phase.

## Requirements

- Python 3.8+
- Install dependencies: `pip install -r requirements.txt`
- Key packages: `pyyaml`, `python-pptx`, `reportlab` (for PDF)

## Also Works With

This skill is LLM-agnostic. The same KB and templates work with:
- **Claude Code** (Anthropic) — uses `SKILL.md` + `CLAUDE.md`
- **Codex** (OpenAI) — uses `AGENTS.md` + `.agents/skills/` (this setup)
- **ChatGPT** — paste SKILL.md as system prompt
- **Gemini Pro** — paste SKILL.md as system instruction
- Any LLM with tool/function calling support
