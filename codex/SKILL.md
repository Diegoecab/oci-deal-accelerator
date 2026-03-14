# OCI Deal Accelerator — Codex Skill

See the root `SKILL.md` for the full system prompt.

This directory packages the OCI Deal Accelerator as a Codex-compatible skill.

## Files

- `skill.json` — Skill manifest with tool definitions
- `SKILL.md` — This file (Codex entry point)

## Usage

The skill provides three tools:
1. `generate_diagram` — Produces .drawio architecture diagrams
2. `generate_deck` — Produces .pptx slide decks
3. `validate_architecture` — Runs Well-Architected validation

Feed discovery notes and the skill will produce the full architecture package.
