# BOM Cookbook — Building `generate_bom` Payloads

Copy-paste recipes that map common customer requirements to the exact OCI SKUs the
`generate_bom`, `generate_bom_appca`, and `generate_cost_estimate` MCP tools expect.
The goal is to skip the "grep the catalog and guess SKUs" exploration loop that
burns tool calls on well-known patterns.

> **If the requirement does not match any recipe below, consult
> [`kb/services/`](../kb/services/) and
> [`kb/pricing/oci-sku-catalog.yaml`](../kb/pricing/oci-sku-catalog.yaml)
> before inventing SKUs.** All SKUs below are verified against the catalog as of
> 2026-04-20; re-`grep` the catalog if a recipe ever fails.

## Payload Shape

All three tools accept the same envelope:

```json
{
  "customer_id": "acme-prod",
  "discount_pct": 0.35,
  "currency": "USD",
  "services": [
    { "sku": "B90777", "quantity": 1 }
  ]
}
```

- `customer_id`: free-form identifier, used for output file naming.
- `discount_pct`: decimal (0.35 = 35%). Applied to every line unless overridden.
- `services[].quantity`: integer or float depending on the SKU metric (ECPUs, GB, hours).

---

## Recipe 1 — Exadata Cloud Service (ExaCS) X11M, BYOL

**When it matches:** "ExaCS X11M BYOL, N ECPUs, M TB storage, no DR" — customer-managed
Oracle Database on dedicated Exadata hardware, BYOL licensing.

**SKUs:**

| SKU | Component | Typical qty |
|-----|-----------|-------------|
| `B90777` | Exadata Infrastructure — Base System | `1` per rack |
| `B110627` | Exadata Database Server — X11M | `2` (Base/Quarter) — adjust per rack config |
| `B110629` | Exadata Storage Server — X11M | `3` (Base/Quarter) — adjust per rack config |
| `B110632` | Exadata Database ECPU — Dedicated Infra BYOL (X11M) | One per ECPU |

Swap `B110632` → `B110631` for PAYG (license-included) pricing.

**Payload (120 ECPUs, 120 TB, BYOL, standard Base System):**

```json
{
  "customer_id": "acme-exacs",
  "discount_pct": 0.35,
  "currency": "USD",
  "services": [
    { "sku": "B90777",  "quantity": 1 },
    { "sku": "B110627", "quantity": 2 },
    { "sku": "B110629", "quantity": 3 },
    { "sku": "B110632", "quantity": 120 }
  ]
}
```

---

## Recipe 2 — Autonomous Database Dedicated (ADB-D), BYOL

**When it matches:** "ADB Dedicated, N ECPUs, M TB, BYOL" — Autonomous Database running
on dedicated Exadata infrastructure.

**⚠️ Gotcha that burns tool calls:** ADB-Dedicated has **no separate infrastructure
SKUs** in the catalog. It reuses the same Exadata dedicated infra SKUs as ExaCS
(`B90777`, `B110627`, `B110629`) plus the same Exadata ECPU SKU (`B110631`/`B110632`).
The Autonomous-vs-customer-managed distinction is a tenancy-level configuration,
not a billing line item. Do not search for `autonomous_dedicated` SKUs — they do
not exist.

**SKUs:** identical to Recipe 1.

**Payload (64 ECPUs, BYOL):**

```json
{
  "customer_id": "acme-adbd",
  "discount_pct": 0.35,
  "currency": "USD",
  "services": [
    { "sku": "B90777",  "quantity": 1 },
    { "sku": "B110627", "quantity": 2 },
    { "sku": "B110629", "quantity": 3 },
    { "sku": "B110632", "quantity": 64 }
  ]
}
```

---

## Recipe 3 — Autonomous Database Serverless (ADB-S) + Block Volume + FastConnect

**When it matches:** "ADB-S ATP, N ECPUs, M TB data + block storage for app tier +
FastConnect to on-prem" — the typical "app on OCI Compute, DB on ADB-S" pattern.

**SKUs:**

| SKU | Component | Metric |
|-----|-----------|--------|
| `B95701` | ADB ECPU (ATP or ADW) — license-included | ECPU/hour |
| `B95703` | ADB ECPU BYOL — use instead of B95701 if BYOL | ECPU/hour |
| `B95706` | ADB ATP data storage | GB/month |
| `B95754` | ADB ADW data storage — use instead of B95706 for warehouse | GB/month |
| `B95754a` | ADB backup storage | GB/month |
| `B91961` | Block Volume storage (app tier) | GB/month |
| `B91962` | Block Volume performance (VPU) — optional, for higher IOPS tiers | VPU/GB/month |
| `B88326` | FastConnect 10 Gbps port | port-hour |

Swap `B88326` → `B88325` (1 Gbps) or `B93126` (100 Gbps) as needed.

**Payload (16 ECPUs ATP license-included, 2 TB data + 1 TB backup, 500 GB block, 10 G FastConnect):**

```json
{
  "customer_id": "acme-adbs",
  "discount_pct": 0.35,
  "currency": "USD",
  "services": [
    { "sku": "B95701",  "quantity": 16 },
    { "sku": "B95706",  "quantity": 2048 },
    { "sku": "B95754a", "quantity": 1024 },
    { "sku": "B91961",  "quantity": 500 },
    { "sku": "B88326",  "quantity": 1 }
  ]
}
```

---

## When a recipe doesn't fit

1. Grep the catalog: `grep -n "<product keyword>" kb/pricing/oci-sku-catalog.yaml`
2. Check service docs under `kb/services/` for deployment-specific guidance.
3. Check `kb/field-knowledge/` for known sizing/pricing gotchas.
4. If a SKU still cannot be located, surface the gap to the user rather than guessing — fabricated SKUs break the BOM silently.
