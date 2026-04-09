# Knowledge Base — Contributor Guide

The KB is the moat. It encodes Oracle field experience, OCI service quirks,
and architecture patterns that aren't in the official docs. Tools and the
skill itself read these YAMLs at runtime.

## Directory map

| Directory | Purpose | Format |
|---|---|---|
| `services/` | One file per OCI service. Capabilities, limits, gotchas, when-to-use. | Frontmatter + structured body |
| `patterns/` | Composable architecture blocks (HA, DR, hub-spoke, RACI, ECAL artefacts). | Frontmatter + body, often nested dirs |
| `sizing/` | CPU/memory/storage conversion ratios, IOPS limits, scaling rules. | Body only |
| `pricing/` | `oci-sku-catalog.yaml` (200+ SKUs, auto-refreshed) + `compute.yaml` (shape-level, auto-refreshed). Both pull from the Oracle public pricing API. | Frontmatter + body |
| `competitive/` | OCI vs AWS / Azure / GCP service mapping and objection handling. | Frontmatter + body |
| `compatibility/` | Feature matrices (e.g. ADB-S features). Currently thin — expected to grow. | Frontmatter + body |
| `well-architected/` | 5-pillar checklists, landing zone patterns, persona views. | Frontmatter + body |
| `architecture-center/` | Auto-curated index of Oracle Architecture Center reference architectures. | Single `catalog.yaml` |
| `field-knowledge/` | Real-world gotchas, lessons learned, undocumented limits. | Frontmatter + body |
| `field-findings/` | Tracker of newly logged field issues with confidence decay. | Single `tracker.yaml` |
| `diagram/` | OCI icon library and reference layouts for diagram generation. | Mixed |

## Required frontmatter

Every YAML file under `kb/` should start with a frontmatter block:

```yaml
---
last_verified: 2026-04-08            # YYYY-MM-DD, when the file was last reviewed against current Oracle docs
source: https://docs.oracle.com/...  # primary source(s) used during last verification
description: One-line summary of what this file contains
---

# body starts here
key: value
```

The freshness checker (`tools/kb_freshness.py`) reads `last_verified` and warns
if a file is older than the thresholds in `config/kb-governance.yaml`
(default: warning at 180 days, stale at 365 days). The KB linter
(`tools/kb_linter.py`) accepts `last_updated` and `last_refreshed` as fallback
field names but new files should use `last_verified`.

## How to add a new service card

1. Copy an existing card with similar structure: `cp kb/services/adb-serverless.yaml kb/services/<your-service>.yaml`.
2. Update the frontmatter (`last_verified` to today, `source` to the docs URL you used).
3. Fill in fields. Keep gotchas honest — if the service has a limitation, write it down. The KB's value is honesty, not marketing.
4. Run `python tools/kb_linter.py` and fix any issues it reports for your file.
5. Run `make freshness` to confirm your new file is FRESH.

## How to add a pattern

Patterns can be either single-file (e.g. `kb/patterns/business-drivers.yaml`)
or directory-based for larger blocks (e.g. `kb/patterns/database-ha/`).
Use a directory when you need multiple files (pattern + diagrams + ADRs).

## Refresh tooling

| File | Refresh tool |
|---|---|
| `kb/pricing/oci-sku-catalog.yaml` | `python tools/refresh_sku_catalog.py --refresh` (Oracle pricing API) |
| `kb/pricing/compute.yaml` | `python tools/refresh_sku_catalog.py --refresh-domain compute` (same API, shape-level) |
| `kb/architecture-center/catalog.yaml` | `python tools/refresh_arch_catalog.py --whats-new` (web crawl) |
| Other `kb/pricing/<domain>.yaml` | Not yet automated. Add a new entry to `DOMAIN_REGISTRY` in `tools/refresh_sku_catalog.py` and write a domain-specific refresher (see `refresh_compute_yaml` as a template). |
| Everything else | **Manual** — review against Oracle docs, bump `last_verified` |

The shortcut for everyone:

```bash
make freshness            # report stale files
make freshness-refresh    # run automatic refreshes for files that support them
```

## Pricing files

There are exactly **two** pricing files, both auto-refreshed from the
[Oracle public pricing API](https://apexapps.oracle.com/pls/apex/cetools/api/v1/products/?currencyCode=USD):

1. **`kb/pricing/oci-sku-catalog.yaml`** — 200+ SKUs across 20 categories
   (compute, storage, database, networking, observability, security, AI/ML,
   GenAI, etc.). Refresh: `python tools/refresh_sku_catalog.py --refresh`.
2. **`kb/pricing/compute.yaml`** — shape-level estimation pricing
   (VM.Standard.E5.Flex hourly, monthly, etc.). Different abstraction from
   the SKU catalog — useful for SA estimation. Refresh:
   `python tools/refresh_sku_catalog.py --refresh-domain compute`.

**Pricing context that ISN'T a price** (billing models, BYOL rules, free
tiers, service nuances, hyperscaler comparisons) lives in
`kb/field-knowledge/pricing-knowledge.yaml`. That file is non-numeric where
possible and does not need API refresh.

There are no other pricing files. The previous `kb/pricing/database.yaml`,
`storage.yaml`, `networking.yaml`, etc. were removed on 2026-04-08 — their
prices were drift-prone and 30-800% off the live API; their notes were
migrated to `kb/field-knowledge/pricing-knowledge.yaml`.

## Linter

```bash
python tools/kb_linter.py                # all checks
python tools/kb_linter.py --show-decay   # confidence decay only
python tools/kb_linter.py --check-tags   # tag taxonomy only
python tools/kb_linter.py --check-owners # domain owner assignments only
```

The linter reports STALE / WARNING for files past their freshness threshold,
unknown tags in field findings, and missing domain owners. Exit code is 1 if
any issues are found.

## Review cadence

- **Field findings**: confidence decays automatically — see `config/kb-governance.yaml`
- **Service cards**: review at least every 6 months, or when Oracle publishes a major update
- **Patterns**: review at least once a year
- **Pricing**: ideally every quarter — Oracle changes prices ~2x per year for major SKUs

## Thin directories

`compatibility/` and `field-findings/` currently hold a single file each.
Both are expected to grow as more SAs contribute. If after 6 months they
remain at 1 file, consider consolidating with a parent directory.
