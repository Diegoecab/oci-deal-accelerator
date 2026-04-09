# Output Formats and Conventions

Referenced from `SKILL.md` § Output Generation.

## Output directory convention

All generated files MUST be saved inside a dedicated output folder per customer/initiative:

```
examples/output-<customer>-<initiative>/
```

Examples:
- `examples/output-meli-im06/` — MELI MySQL engagement
- `examples/output-meli-im30/` — MELI ElasticSearch engagement
- `examples/output-acme-migration/` — ACME cloud migration

This folder contains ALL outputs for that engagement: `.pptx`, `.drawio`, `.yaml` specs, `.pdf`, scorecards. The folder is gitignored via `examples/output-*/` — never commit customer data.

YAML spec files (architecture, workload-profile, diagram-spec) are saved IN the output folder, not loose in `examples/`. This keeps everything grouped and portable.

## Format options

Default output is a **slide deck (.pptx)**. The architect can specify:

| Format | Output |
|--------|--------|
| `deck` (default) | 10-12 slide presentation |
| `deck + drawio` | + editable architecture diagram |
| `deck + doc` | + technical document (15-25 pages) |
| `deck + xlsx` | + cost spreadsheet with formulas |
| `deck + pdf` | + customer-facing PDF (branded, no internal refs) |
| `pdf` | Customer PDF only |
| `full` | Everything (pptx + drawio + docx + xlsx + pdf) |
| `doc only` | Technical document without slides |
| `deliver` | Handover + go-live checklist + success criteria |

## Slide deck structure

Slide count adapts to engagement tier (6-8 small, 10-12 standard, 12-16 complex):

1. **Title** — customer, project, date (dark background)
2. **Value Story** — business driver, hypothesis, desired outcomes
3. **Service Tiering** — workload-to-tier mapping (Platinum/Gold/Silver/Bronze) with SLA, RTO/RPO
4. **Architecture Principles** — selected ECAL principles (Design/Deployment/Service) that govern the architecture
5. **Architecture Diagram** — fills 85% of slide
6. **Architecture Decisions** — 4-6 key decisions with rationale
7. **HA/DR** — topology + RTO/RPO per tier
8. **Security & Compliance** — controls grid, compliance badges
9. **Environment Catalogue** — Prod/Pre-Prod/Dev-Test/DR per workload with sizing and isolation
10. **Cost Estimate** — PAYG vs BYOL table with assumptions (all environments)
11. **Cost Comparison** (optional) — vs current state or competitor
12. **Migration Approach** — phased timeline, tools, downtime strategy
13. **Operational RACI** — responsibility matrix (customer vs Oracle/partner)
14. **Risk Register** — severity-coded risk table
15. **Well-Architected Scorecard** — 5-pillar traffic-light indicators
16. **Next Steps** — concrete SMART actions with dates

Use `tools/oci_deck_gen.py` for generation. Colors: teal `#2D5967`, copper `#AA643B`, purple `#804998`. Font: Segoe UI. Design standards: `config/output-formats.yaml`.

## Architecture diagram

Use `tools/oci_diagram_gen.py` with OCI official styles from `kb/diagram/oci-toolkit-styles.yaml`. Containers, service blocks, connections, and typography rules are defined there.

## Service categorization

| Category | Color | Use |
|----------|-------|-----|
| **Infrastructure** | Teal `#2D5967` | Compute, OKE, LB, Gateways, WAF, Bastion, Storage, Monitoring |
| **Database** | Copper `#AA643B` | ADB-S/D, DBCS, ExaCS, MySQL, PostgreSQL, NoSQL, GoldenGate |
| **Integration** | Purple `#804998` | DRG, Streaming, Queue, OIC, FastConnect, Service Connector Hub |
| **Dormant** | Light gray `#DFDCD8` | Standby/inactive resources (DR tier) |
| **Legacy** | Medium gray `#70665E` | Non-OCI systems (MQ Series, legacy middleware) |
