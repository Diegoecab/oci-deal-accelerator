# OCI Deal Accelerator — Codex Skill

## Quick Start

1. Open Codex app or CLI
2. Load this skill: `codex --skill ./codex`
3. Paste your discovery notes
4. Get your architecture proposal

## What It Does

Takes unstructured customer discovery notes and produces:
- Architecture slide deck (.pptx) with OCI branding
- Editable architecture diagram (.drawio) with official OCI styles
- Cost estimates (PAYG vs BYOL breakdown)
- Well-Architected Framework scorecard
- Risk register and migration timeline

## Usage Modes

**Full Pipeline** — Paste discovery notes, get a complete proposal:
```
"Here are my notes from the Acme Corp discovery call: 3 Oracle DBs on Exadata X8M..."
```

**Diagram Only** — Generate from a YAML spec:
```
"Generate a diagram from examples/migration-adb-ha-dr.yaml"
```

**Iterate** — Modify an existing architecture:
```
"Add a NoSQL database to the app tier and regenerate the deck"
```

## Output Formats

| Command | Output |
|---------|--------|
| `deck` (default) | .pptx slide deck |
| `deck + drawio` | .pptx + .drawio diagram |
| `deck + xlsx` | .pptx + cost spreadsheet |
| `full` | All formats |
| `drawio` | .drawio only |

## Requirements

- Python 3.8+ with `pyyaml` and `python-pptx`
- Install: `pip install -r requirements.txt`

## Also Works With

This skill is LLM-agnostic. The same SKILL.md and KB work with:
- Claude Code (Anthropic)
- ChatGPT (OpenAI) — paste SKILL.md as system prompt
- Gemini Pro (Google) — paste SKILL.md as system instruction
- Any LLM with tool/function calling support

The Codex packaging adds tool definitions and multi-agent coordination
but the core skill logic is portable.

## Knowledge Base

The `kb/` directory contains:
- **services/**: OCI service files with sizing rules, gotchas, competitive notes
- **patterns/**: Composable architecture blocks (HA, DR, networking)
- **sizing/**: CPU conversion ratios, storage performance tiers
- **pricing/**: Estimation ranges for cost modeling
- **well-architected/**: 5-pillar validation checklists
- **competitive/**: AWS service mapping with honest pros/cons
- **field-knowledge/**: Real-world gotchas the docs don't tell you
