# Evaluations

Baseline evaluation scenarios for the OCI Deal Accelerator skill, following
the format recommended in the [Anthropic Agent Skills best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#build-evaluations-first).

These are **manual evaluations** — there is no automated test runner yet.
Use them as a regression checklist after non-trivial changes to `SKILL.md`,
`CLAUDE.md`, or the welcome flow.

## How to run

1. Open a fresh Claude Code conversation in this repo.
2. For each `*.json` file in this directory:
   - Read the `query` field — paste it as the user message (or simulate the trigger described in the file).
   - If `files` is non-empty, attach those files as context.
   - Observe the assistant's behavior.
   - Manually verify each item in `expected_behavior` is met.
3. Note any failures — file an issue or update the skill accordingly.

## Scenarios

| File | Purpose |
|---|---|
| `welcome-flow.json` | Greeting → exact 14-option menu (verbatim from SKILL.md) |
| `full-proposal.json` | Discovery notes → bypass menu, run full proposal flow |
| `wa-review.json` | WA review request → scorecard format + saved YAML files |
