# KB Changelog

Recent changes to the Knowledge Base. The skill shows the latest entry in the welcome banner.

## 2026-04-14
- Diagram generator: icon sizing calibrated from 37 Oracle Architecture Center .drawio files (63px services, 42px gateways)
- Diagram generator: auto-sizing containers, DRG placement outside VCN, edge label offsets
- Diagram generator: VCN/subnet dash pattern corrected to "4 2" (Oracle ref standard)
- New: `scripts/validate-diagram.py` — automated diagram quality validation
- New: `--check-links` in refresh_arch_catalog.py — detects broken URLs in catalog
- New: weekly KB health CI workflow (`.gitea/workflows/kb-health.yaml`)
- SKILL.md: anti-hallucination guardrails (closed whitelist + mandatory pre-generation review)
- SKILL.md: structured data intake (Extraction Receipt + Completeness Gate)

## 2026-04-01
- KB validation: 30 corrections across 16 files (ExaCS storage, ECPU transition, IOPS fixes)

## 2026-03-16
- Architecture Center catalog refreshed: 123 entries verified
