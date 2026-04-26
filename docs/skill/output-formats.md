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
| `deck` (default) | 10-12 slide presentation, with native OCI PowerPoint diagram when applicable |
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
5. **Architecture Diagram** — fills 85% of slide; prefer native OCI PowerPoint shapes inside the deck when the architecture is structured enough
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

Use `tools/oci_deck_gen.py` for generation. Decks should prefer native OCI PowerPoint diagrams over pasted images when the architecture can be rendered from structured input. Colors: teal `#2D5967`, copper `#AA643B`, purple `#804998`. Font: Segoe UI. Design standards: `config/output-formats.yaml`.

## Architecture diagram

Use `tools/oci_diagram_gen.py` with OCI official styles from `kb/diagram/oci-toolkit-styles.yaml` when the user wants an editable technical diagram (`.drawio`). For customer-facing or presentation-ready output, prefer the native PowerPoint path via `tools/oci_deck_gen.py` and the PPTX icon library/index under `kb/diagram/`.

### Standard diagram-generation procedure (MANDATORY)

Follow these steps for every diagram, in order. Skipping a step is the single most common source of layout regressions.

1. **Reference architecture lookup.** Run `python tools/archcenter_pattern_lookup.py "<topology keywords>"` against `kb/architecture-center/catalog.yaml` (123 entries). Pick the highest-scoring entry whose topology matches what the user asked for. The lookup surfaces cached `.drawio` / `.svg` under `kb/diagram/assets/archcenter-refs/<slug>/` — open it to copy proven container nesting, padding, and AD/subnet placement instead of inventing geometry.
2. **Pre-generation review (per SKILL.md § What You Do NOT Do).** Confirm the component list with the user. Never add services the user did not mention except via the explicit auto-include whitelist.
3. **Author the spec.** Use `absolute_layout` for ref-arch reproductions or any topology where geometry matters. Honor the geometry rules below (the spec validator enforces them).
4. **Spec validation runs automatically.** Both `tools/oci_diagram_gen.py` (drawio) and `tools/oci_pptx_diagram_gen.py` (PPTX, called via `oci_deck_gen.py`) call `tools/diagram_spec_validator.py` before emitting any output. A `fail` status raises and aborts generation — fix the geometry, re-run.
5. **Render.** Generate the `.drawio` and/or `.pptx`. The drawio path additionally runs `drawio_visual_validator.py` post-render to catch anything the spec validator missed (font sizes, off-canvas, duplicate ids).
6. **Visually verify.** Rasterize the PPTX with `python tools/oci_pptx_render.py --pptx X.pptx --output X.png --width 1600` and inspect the PNG before reporting success.

### Geometry rules for `absolute_layout`

These rules are enforced by `tools/diagram_spec_validator.py` and exist because each one corresponds to a regression that previously shipped to the user:

- **Container padding ≥ 12px.** Every nested container must keep ≥12px between its bottom edge and its parent's bottom edge. Otherwise the borders visually merge (`CONTAINER_PADDING_VIOLATION`).
- **Subnet height ≥ label band + 12px.** A container labeled at 11pt needs h ≥ ~30px to avoid the label collapsing onto the bottom edge. Public-subnet bands holding an icon need to clear icon height + label band + breathing room (`CONTAINER_TOO_THIN`).
- **Labels stay inside their parent, ≥ 6px from the bottom edge.** Free-floating labels under a service icon must not cross or sit within 6px of the enclosing subnet's bottom edge (`LABEL_OVERFLOW_PARENT`).
- **AD columns nest INSIDE the VCN, never beside it.** Otherwise AD borders align with VCN borders and visually merge.
- **Subnets may span AD columns** (regional public subnet, cross-AD DB subnet) — that is the canonical Oracle pattern for HA topologies; do not split a regional subnet per AD.

### Diagram modes

The diagram generator accepts two spec shapes:

1. **Workload-driven (default)** — `tenancy → region(s) → vcn(s) → subnet(s) → service(s)` plus on-premises and external actors. The generator auto-lays out containers and service blocks. Use this for most customer proposals where you describe the workload abstractly.
2. **`absolute_layout` (fidelity mode)** — explicit `(x, y, w, h)` for every container, service, label, and connection. Use this when the user wants to reproduce an Oracle Architecture Center reference diagram with maximum visual fidelity, or when a layout already exists (e.g. extracted from an official `.drawio`).

```yaml
absolute_layout:
  canvas: {width: 720, height: 420}
  containers:
    - {id: region, type: region, label: "OCI Region", x: 0, y: 0, w: 720, h: 420}
    - {id: vcn, type: vcn, label: "VCN 10.10.0.0/16", x: 28, y: 52, w: 670, h: 348}
  services:
    - {id: drg,  label: "", type: drg,  x: 8, y: 200, w: 55, h: 66}
    - {id: adb,  label: "", type: adb_d, x: 230, y: 240, w: 60, h: 80}
  labels:
    - {id: lbl_drg, text: "DRG", x: 8, y: 268, w: 55, h: 14, fontSize: 700}
  connections:
    - {id: c1, from: drg, to: adb, type: standard, points: [[63, 233], [260, 240]]}
```

`fontSize` is shared with the PPTX `absolute_layout` schema — it's hundredths of a point (720 → 7.2pt). The drawio renderer auto-converts.

The Architecture Center reconstruction pipeline lives at `tools/archcenter_case_runner.py` (single case) and `tools/archcenter_batch_driver.py` (batch). Reference: `kb/diagram/reference-layouts/archcenter-batch-runner.yaml`.

### Pre-delivery validation (automatic)

Both generators run sanity checks before the file ships, so a broken artifact never reaches the user:

- **`tools/diagram_spec_validator.py`** — runs automatically *before* either renderer (drawio or PPTX). Validates the parsed `absolute_layout` for `CONTAINER_TOO_THIN`, `CONTAINER_PADDING_VIOLATION`, and `LABEL_OVERFLOW_PARENT`. A fail aborts generation. Set `OCI_DIAGRAM_VALIDATOR_SOFT=1` to demote errors to warnings.
- **`tools/drawio_visual_validator.py`** — runs automatically inside `OCIDiagramGenerator.save()`. Hard-fails on `fontSize ≥ 50pt` (catches the PPTX-cents-of-pt → drawio-pt unit confusion that produced 700pt labels), duplicate cell ids, off-canvas geometry, and dangling edge endpoints. Reports OK/warnings/errors to stderr. Pass `--strict` on the CLI to make errors fail the build.
- **`OCIDeckGenerator.save()` post-check** — verifies `[Content_Types].xml` declares a `<Default>` for every embedded media extension (PowerPoint refuses to open a deck and prompts to "repair" it when this is missing — the SVG-backed icons in `OCI_Icons.pptx` are the canonical case), and that no slide rels point to absent media or duplicate cNvPr ids.
- **`tools/drawio_fidelity_eval.py`** — pixel-diff the rebuilt drawio against a canonical Architecture Center PNG. Runs automatically when the spec carries `source.diagram_asset` (or via `--reference-png` on the CLI). Default rendering path is the SVG companion via `cairosvg` (works in any environment); the rebuilt-drawio path through the actual `draw.io` binary is opt-in via the `DRAWIO_EXE` env var (the binary is not bundled with the skill — install on demand).

CLI usage:

```bash
# Standard run (validators on by default)
python tools/oci_diagram_gen.py --spec my-spec.yaml --output out.drawio

# Fail the build if validator finds errors
python tools/oci_diagram_gen.py --spec my-spec.yaml --output out.drawio --strict

# Fidelity comparison vs canonical PNG
python tools/oci_diagram_gen.py --spec my-spec.yaml --output out.drawio \
   --reference-png kb/diagram/reference-layouts/.../canonical.png

# Strict draw.io binary path (opt-in)
DRAWIO_EXE=/usr/bin/drawio python tools/oci_diagram_gen.py --spec ... --reference-png ...
```

Skip validators only when intentionally generating a fixture or test: `--no-validate`.

## Service categorization

| Category | Color | Use |
|----------|-------|-----|
| **Infrastructure** | Teal `#2D5967` | Compute, OKE, LB, Gateways, WAF, Bastion, Storage, Monitoring |
| **Database** | Copper `#AA643B` | ADB-S/D, DBCS, ExaCS, MySQL, PostgreSQL, NoSQL, GoldenGate |
| **Integration** | Purple `#804998` | DRG, Streaming, Queue, OIC, FastConnect, Service Connector Hub |
| **Dormant** | Light gray `#DFDCD8` | Standby/inactive resources (DR tier) |
| **Legacy** | Medium gray `#70665E` | Non-OCI systems (MQ Series, legacy middleware) |
