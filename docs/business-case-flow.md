# Business Case Flow

Option 8 produces an executive business-case deck plus reusable YAML backing
data. For ADB-S to ADB-D cases, use `business_case.adbs_to_adbd`.

## ADB-S to ADB-D Rules

- Keep workload/billable ECPU demand comparable between ADB-S and ADB-D unless
  the customer provides a different target demand.
- Dedicated physical capacity is a separate fixed footprint:
  `DB nodes x ECPU per DB node`.
- Never model ADB-D at 100% utilization by default. Show utilization explicitly.
- ADB-D fixed infrastructure includes DB servers and storage servers; workload
  ECPU demand remains a separate line.
- Projected BOMs are annual run-rate snapshots at the horizon, not cumulative
  multi-year totals.
- GoldenGate can be `steady_state`, `migration_bridge_only`, or
  `migration_plus_fallback_months`. Bridge-only GoldenGate is excluded from
  future steady-state BOMs.

## Read Architecture

ADB-S and ADB-D can carry the same workload demand while using different read
architectures. ADB-S may require refreshable/read clones when standby is not the
application read path. ADB-D may use Local ADG read-only standby and retire
steady-state clones. The deck should call this out in BOM notes, value drivers,
and risk/value slides.

## Storage Economics

Storage economics are shown separately from aggregate TCO:

```text
break-even TB = fixed dedicated infra monthly cost / ADB-S storage USD per GB-month / 1024
```

Apply discounts uniformly when comparing scenarios. If customer material
provides a baseline break-even, show it beside the recalculated break-even for
the proposed footprint.

## Business Value

Risk-reduction cases use a Business Value Model instead of generic ROI
percentages. Do not invent revenue impact. Convert stability to USD only when
the customer provides revenue-at-risk, transaction margin, fraud loss impact, or
cost per degraded/outage hour.

Use:

```text
avoided degraded/outage hours x business impact per hour
```

Track success metrics such as CPU utilization, read latency, clone lag retired,
ADG read lag, GoldenGate/apply lag during migration, incidents avoided, and
degraded hours avoided.

## Validation

Business-case deck validation reads text boxes, table cells, and grouped shapes.
It checks expected titles, disclaimer-last, required assumptions, and forbidden
obsolete phrases such as `OCI Annual`, stale scenario risks, and unclear
language like `FTE-year`.
