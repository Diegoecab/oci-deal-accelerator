#!/usr/bin/env python3
"""Reusable business-case modeling helpers for OCI Deal Accelerator.

The functions in this module intentionally avoid customer-specific logic. They
turn a compact ADB-S to ADB-D scenario description into audit-friendly TCO,
BOM, storage economics, and value-model structures consumed by the deck and
BOM generators.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from oci_bom_gen import OCIBomGenerator
except ModuleNotFoundError:
    from tools.oci_bom_gen import OCIBomGenerator


HOURS_PER_MONTH = 730
MONTHS_PER_YEAR = 12

SKU_ADBS_ECPU_PAYG = "B95701"
SKU_ADBS_ECPU_BYOL = "B95703"
SKU_ADBS_STORAGE_ATP = "B95706"
SKU_ADBD_ECPU_PAYG = "B110631"
SKU_ADBD_ECPU_BYOL = "B110632"
SKU_ADBD_BASE = "B90777"
SKU_ADBD_DB_SERVER = "B110627"
SKU_ADBD_STORAGE_SERVER = "B110629"
SKU_GG_PAYG = "B92992"
SKU_GG_BYOL = "B92993"


@dataclass(frozen=True)
class CapacityModel:
    workload_ecpu: float
    db_nodes: float
    ecpu_per_db_node: float

    @property
    def physical_capacity_ecpu(self) -> float:
        return self.db_nodes * self.ecpu_per_db_node

    @property
    def utilization_pct(self) -> float:
        capacity = self.physical_capacity_ecpu
        return (self.workload_ecpu / capacity * 100) if capacity else 0

    @property
    def label(self) -> str:
        return (
            f"{self.workload_ecpu:,.0f} ECPU used over "
            f"{self.physical_capacity_ecpu:,.0f} ECPU capacity = "
            f"{self.utilization_pct:.0f}%"
        )


def pct(value: Any) -> float:
    """Normalize discounts that may be expressed as 11 or 0.11."""
    try:
        number = float(value or 0)
    except (TypeError, ValueError):
        return 0.0
    return number / 100 if number > 1 else number


def money(value: float) -> str:
    sign = "-" if value < 0 else ""
    return f"{sign}USD {abs(value):,.0f}"


def millions(value: float) -> float:
    return round(float(value or 0) / 1_000_000, 3)


def _num(mapping: dict, *keys: str, default: float = 0.0) -> float:
    for key in keys:
        if isinstance(mapping, dict) and key in mapping and mapping.get(key) is not None:
            try:
                return float(mapping.get(key) or 0)
            except (TypeError, ValueError):
                return default
    return default


def _pick(mapping: dict, *keys: str, default: Any = "") -> Any:
    if not isinstance(mapping, dict):
        return default
    for key in keys:
        if key in mapping and mapping.get(key) is not None:
            return mapping.get(key)
    return default


def _sku_price(catalog: dict[str, dict], sku: str) -> float:
    return float((catalog.get(sku) or {}).get("list_price_usd", 0) or 0)


def _load_catalog(catalog_path: str | None = None) -> dict[str, dict]:
    gen = OCIBomGenerator()
    gen.load_catalog(catalog_path)
    return gen.catalog


def capacity_model(stage: dict, ecpu_per_db_node: float) -> CapacityModel:
    return CapacityModel(
        workload_ecpu=_num(stage, "workload_ecpu", "ecpu_demand", default=0),
        db_nodes=_num(stage, "db_nodes", "database_servers", default=0),
        ecpu_per_db_node=ecpu_per_db_node,
    )


def storage_break_even_tb(
    fixed_monthly_cost: float,
    adbs_storage_usd_per_gb_month: float,
    discount_pct: float = 0,
) -> float:
    discounted_storage = adbs_storage_usd_per_gb_month * (1 - pct(discount_pct))
    if discounted_storage <= 0:
        return 0
    return fixed_monthly_cost / discounted_storage / 1024


def first_crossover_period(periods: list[dict]) -> str:
    for row in periods:
        if float(row.get("to_be_annual_tco", 0) or 0) < float(row.get("as_is_annual_tco", 0) or 0):
            return str(row.get("label") or row.get("period") or "")
    return ""


def _hours_units_for_monthly_sku(sku: str) -> int:
    return 1 if sku in {SKU_ADBS_STORAGE_ATP} else HOURS_PER_MONTH


def _line(sku: str, qty: float, discount: float, label: str, note: str = "", months: int = 12) -> dict:
    return {
        "sku": sku,
        "qty": round(float(qty or 0), 4),
        "hours_units": _hours_units_for_monthly_sku(sku),
        "months": months,
        "discount": pct(discount),
        "custom_label": label,
        "custom_note": note,
    }


def _goldengate_line(config: dict, discount: float, include_steady_state: bool, bridge_months: int = 0) -> dict | None:
    gg = config.get("goldengate") or {}
    mode = _pick(gg, "mode", default="")
    ocpus = _num(gg, "ocpus", "quantity", default=0)
    if not ocpus:
        return None
    include = mode == "steady_state" or include_steady_state
    if mode == "migration_bridge_only":
        include = bridge_months > 0
    if mode == "migration_plus_fallback_months":
        include = bridge_months > 0
    if not include:
        return None
    sku = SKU_GG_BYOL if str(_pick(config, "license_model", default="BYOL")).upper() == "BYOL" else SKU_GG_PAYG
    months = bridge_months or 12
    note = {
        "steady_state": "GoldenGate modeled as steady-state run-rate.",
        "migration_bridge_only": f"GoldenGate migration bridge only; modeled for {months} month(s), excluded from future steady-state BOM.",
        "migration_plus_fallback_months": f"GoldenGate migration plus fallback bridge; modeled for {months} month(s).",
    }.get(mode, "GoldenGate assumption from scenario input.")
    return _line(sku, ocpus, discount, "GoldenGate", note, months=months)


def _goldengate_bridge_months(config: dict) -> int:
    gg = config.get("goldengate") or {}
    return int(_num(gg, "bridge_months", "fallback_months", default=0))


def goldengate_bridge_term_cost(config: dict, catalog_path: str | None = None) -> float:
    gg = config.get("goldengate") or {}
    mode = _pick(gg, "mode", default="")
    if mode not in {"migration_bridge_only", "migration_plus_fallback_months"}:
        return 0
    ocpus = _num(gg, "ocpus", "quantity", default=0)
    months = _goldengate_bridge_months(config)
    if not ocpus or not months:
        return 0
    catalog = _load_catalog(catalog_path)
    license_model = str(_pick(config, "license_model", default="BYOL")).upper()
    sku = SKU_GG_BYOL if license_model == "BYOL" else SKU_GG_PAYG
    return _sku_price(catalog, sku) * HOURS_PER_MONTH * ocpus * months * (1 - pct(_pick(config, "discount_pct", "discount", default=0)))


def _adbs_lines(config: dict, stage: dict, discount: float, label: str, include_gg: bool) -> list[dict]:
    license_model = str(_pick(config, "license_model", default="BYOL")).upper()
    sku_ecpu = SKU_ADBS_ECPU_BYOL if license_model == "BYOL" else SKU_ADBS_ECPU_PAYG
    workload_ecpu = _num(stage, "workload_ecpu", "ecpu_demand", default=0)
    storage_gb = _num(stage, "storage_gb", default=0) or _num(stage, "storage_tb", default=0) * 1024
    lines = [
        _line(
            sku_ecpu,
            workload_ecpu,
            discount,
            f"{label} workload ECPU demand",
            "Workload/billable ECPU demand; not physical dedicated capacity.",
        )
    ]
    if storage_gb:
        lines.append(_line(SKU_ADBS_STORAGE_ATP, storage_gb, discount, f"{label} ATP storage", "ADB-S per-GB storage."))
    for component in stage.get("components", []) or []:
        sku = component.get("sku")
        if sku:
            lines.append(_line(
                sku,
                _num(component, "qty", "quantity", default=0),
                discount,
                _pick(component, "label", default="As-is component"),
                _pick(component, "note", default="As-is architecture component."),
                months=int(_num(component, "months", default=12)),
            ))
    gg_line = _goldengate_line(config, discount, include_steady_state=include_gg)
    if gg_line:
        lines.append(gg_line)
    return lines


def _adbd_lines(config: dict, stage: dict, discount: float, label: str, include_gg: bool) -> list[dict]:
    license_model = str(_pick(config, "license_model", default="BYOL")).upper()
    sku_ecpu = SKU_ADBD_ECPU_BYOL if license_model == "BYOL" else SKU_ADBD_ECPU_PAYG
    workload_ecpu = _num(stage, "workload_ecpu", "ecpu_demand", default=0)
    db_nodes = _num(stage, "db_nodes", "database_servers", default=0)
    storage_servers = _num(stage, "storage_servers", default=0)
    cap = capacity_model(stage, _num(config, "ecpu_per_db_node", default=760))
    lines = [
        _line(SKU_ADBD_BASE, 1, discount, f"{label} base infrastructure", "Dedicated base hosted environment."),
        _line(SKU_ADBD_DB_SERVER, db_nodes, discount, f"{label} DB servers", cap.label),
        _line(SKU_ADBD_STORAGE_SERVER, storage_servers, discount, f"{label} storage servers", "Fixed dedicated storage/infrastructure footprint."),
        _line(sku_ecpu, workload_ecpu, discount, f"{label} workload ECPU demand", "Billable/planning ECPU demand; does not assume 100% physical utilization."),
    ]
    gg_line = _goldengate_line(config, discount, include_steady_state=include_gg)
    if gg_line:
        lines.append(gg_line)
    return lines


def build_bom_specs(config: dict) -> dict[str, dict]:
    """Build current, steady-state, and projected BOM specs from a scenario."""
    discount = pct(_pick(config, "discount_pct", "discount", default=0))
    customer = _pick(config, "customer_name", "customer", default="")
    prepared_by = _pick(config, "prepared_by", "author", default="")
    license_model = _pick(config, "license_model", default="BYOL")
    current = config.get("current") or {}
    target = config.get("target") or {}
    forecasts = config.get("forecasts") or []
    gg_mode = _pick(config.get("goldengate") or {}, "mode", default="")
    include_future_gg = gg_mode == "steady_state"

    def spec(name: str, project: str, lines: list[dict], notes: list[str]) -> dict:
        return {
            "bom": {
                "customer_name": customer,
                "project_name": project,
                "prepared_by": prepared_by,
                "currency": "USD",
                "metadata": {"discount_pct": discount},
                "line_items": [line for line in lines if float(line.get("qty") or 0) > 0],
                "notes": notes,
            }
        }

    common_notes = [
        f"Discount: {discount:.0%} applied uniformly to discountable lines.",
        f"License model: {license_model}.",
        "Projected BOMs are annual run-rate snapshots at horizon, not cumulative multi-year totals.",
    ]

    specs = {
        "current_as_is": spec(
            "current_as_is",
            "Current As-Is BOM",
            _adbs_lines(config, current, discount, _pick(current, "label", default="ADB-S As-Is"), include_gg=True),
            common_notes + [
                f"ECPU demand: {_num(current, 'workload_ecpu', 'ecpu_demand'):,.0f}.",
                f"Storage forecast/base: {_num(current, 'storage_tb'):,.1f} TB.",
            ],
        ),
        "to_be_steady_state": spec(
            "to_be_steady_state",
            "To-Be Steady-State BOM",
            _adbd_lines(config, target, discount, _pick(target, "label", default="ADB-D Dedicated"), include_gg=include_future_gg),
            common_notes + [
                capacity_model(target, _num(config, "ecpu_per_db_node", default=760)).label,
                f"GoldenGate mode: {gg_mode or 'not provided'}.",
            ],
        ),
    }

    gg = config.get("goldengate") or {}
    gg_mode = _pick(gg, "mode", default="")
    bridge_months = _goldengate_bridge_months(config)
    if gg_mode in {"migration_bridge_only", "migration_plus_fallback_months"} and bridge_months:
        gg_line = _goldengate_line(config, discount, include_steady_state=False, bridge_months=bridge_months)
        if gg_line:
            specs["migration_bridge_year1"] = spec(
                "migration_bridge_year1",
                "Migration Bridge Year-1 BOM",
                [gg_line],
                common_notes + [
                    f"GoldenGate bridge duration: {bridge_months} month(s).",
                    "Migration bridge is one-time / Year-1-only and excluded from future steady-state BOMs.",
                ],
            )

    for forecast in forecasts:
        period = str(_pick(forecast, "period", "label", default="future")).lower().replace(" ", "_")
        as_is = forecast.get("as_is") or forecast
        to_be = forecast.get("to_be") or forecast
        specs[f"as_is_projected_{period}"] = spec(
            f"as_is_projected_{period}",
            f"As-Is Projected {period.upper()} BOM",
            _adbs_lines(config, as_is, discount, "ADB-S As-Is Projected", include_gg=include_future_gg),
            common_notes + [f"Projected as-is ECPU demand: {_num(as_is, 'workload_ecpu', 'ecpu_demand'):,.0f}."],
        )
        specs[f"to_be_projected_{period}"] = spec(
            f"to_be_projected_{period}",
            f"To-Be Projected {period.upper()} BOM",
            _adbd_lines(config, to_be, discount, "ADB-D Dedicated Projected", include_gg=include_future_gg),
            common_notes + [capacity_model(to_be, _num(config, "ecpu_per_db_node", default=760)).label],
        )

    return specs


def bom_monthly_total(bom_spec: dict, catalog_path: str | None = None) -> float:
    gen = OCIBomGenerator.from_spec(bom_spec, catalog_path=catalog_path)
    total = 0.0
    for item in gen.line_items:
        _, monthly_w = gen._monthly_values(item)
        total += monthly_w
    return total


def build_tco_projection(config: dict, catalog_path: str | None = None) -> list[dict]:
    specs = build_bom_specs(config)
    rows: list[dict] = []
    labels = {
        "current_as_is": "Near-term",
        "to_be_steady_state": "Near-term",
    }
    near_as_is = bom_monthly_total(specs["current_as_is"], catalog_path) * 12
    near_to_be = bom_monthly_total(specs["to_be_steady_state"], catalog_path) * 12
    current = config.get("current") or {}
    target = config.get("target") or {}
    rows.append({
        "period": "near_term",
        "label": "Near-term",
        "cpu": f"{_num(current, 'workload_ecpu', 'ecpu_demand'):,.0f} ECPU",
        "storage": f"{_num(current, 'storage_tb'):,.1f} TB",
        "as_is_annual_tco": near_as_is,
        "to_be_annual_tco": near_to_be,
        "as_is": money(near_as_is),
        "to_be": money(near_to_be),
        "delta": money(near_as_is - near_to_be),
        "note": capacity_model(target, _num(config, "ecpu_per_db_node", default=760)).label,
    })

    for idx, forecast in enumerate(config.get("forecasts") or [], start=1):
        period = str(_pick(forecast, "period", "label", default=f"year_{idx}")).lower().replace(" ", "_")
        as_key = f"as_is_projected_{period}"
        to_key = f"to_be_projected_{period}"
        if as_key not in specs or to_key not in specs:
            continue
        as_is = forecast.get("as_is") or forecast
        to_be = forecast.get("to_be") or forecast
        as_annual = bom_monthly_total(specs[as_key], catalog_path) * 12
        to_annual = bom_monthly_total(specs[to_key], catalog_path) * 12
        label = _pick(forecast, "display_label", default=f"Year {idx}")
        rows.append({
            "period": period,
            "label": label,
            "cpu": f"{_num(as_is, 'workload_ecpu', 'ecpu_demand'):,.0f} ECPU",
            "storage": f"{_num(as_is, 'storage_tb'):,.1f} TB",
            "as_is_annual_tco": as_annual,
            "to_be_annual_tco": to_annual,
            "as_is": money(as_annual),
            "to_be": money(to_annual),
            "delta": money(as_annual - to_annual),
            "note": capacity_model(to_be, _num(config, "ecpu_per_db_node", default=760)).label,
        })
    return rows


def build_storage_economics(config: dict, catalog_path: str | None = None) -> dict:
    catalog = _load_catalog(catalog_path)
    discount = pct(_pick(config, "discount_pct", "discount", default=0))
    storage_price = _num(config.get("storage_economics") or {}, "adbs_storage_usd_per_gb_month", default=0)
    storage_price = storage_price or _sku_price(catalog, SKU_ADBS_STORAGE_ATP)
    specs = build_bom_specs(config)
    target_monthly = bom_monthly_total(specs["to_be_steady_state"], catalog_path)
    target = config.get("target") or {}
    # ECPU demand is not fixed storage infrastructure; remove it to approximate fixed footprint.
    discount_factor = 1 - discount
    fixed_monthly = (
        _sku_price(catalog, SKU_ADBD_BASE) * HOURS_PER_MONTH
        + _sku_price(catalog, SKU_ADBD_DB_SERVER) * HOURS_PER_MONTH * _num(target, "db_nodes", "database_servers")
        + _sku_price(catalog, SKU_ADBD_STORAGE_SERVER) * HOURS_PER_MONTH * _num(target, "storage_servers")
    ) * discount_factor
    fixed_monthly = fixed_monthly or target_monthly
    break_even_tb = storage_break_even_tb(fixed_monthly, storage_price, discount)
    current_tb = _num(config.get("current") or {}, "storage_tb", default=0)
    storage_offset = current_tb * 1024 * storage_price * discount_factor
    base_break_even = _pick(config.get("storage_economics") or {}, "base_break_even_tb", default="")
    cards = [
        {
            "value": f"USD {storage_price * discount_factor:.4f}/GB-mo",
            "label": "ADB-S storage after discount",
            "detail": "Per-GB storage remains variable in the as-is model.",
        },
        {
            "value": f"{break_even_tb:,.0f} TB",
            "label": "Recalculated break-even",
            "detail": "Fixed dedicated footprint / ADB-S storage USD per GB-month.",
        },
        {
            "value": f"USD {storage_offset:,.0f}/mo",
            "label": "Storage offset",
            "detail": f"Current {current_tb:,.0f} TB storage avoided or absorbed by dedicated footprint.",
        },
    ]
    if base_break_even:
        cards[1]["detail"] = f"Customer base break-even: {base_break_even} TB; recalculated for proposed footprint."
    return {
        "headline": "Storage economics: variable ADB-S storage offsets fixed ADB-D infrastructure",
        "cards": cards,
        "break_even_tb": break_even_tb,
        "fixed_monthly_cost": fixed_monthly,
        "storage_offset_monthly": storage_offset,
    }


def build_crossover_chart(projection: list[dict], config: dict) -> dict:
    categories = [row["label"] for row in projection]
    as_is = [millions(row["as_is_annual_tco"]) for row in projection]
    to_be = [millions(row["to_be_annual_tco"]) for row in projection]
    crossover = first_crossover_period(projection)
    bullets = []
    for row in projection[:4]:
        delta = float(row["to_be_annual_tco"] or 0) - float(row["as_is_annual_tco"] or 0)
        sign = "+" if delta >= 0 else "-"
        bullets.append(f"{row['label']}: ADB-D {sign}USD {abs(delta):,.0f}/year")
    chart_cfg = config.get("crossover_chart") or {}
    return {
        "title": _pick(chart_cfg, "title", default="TCO Crossover"),
        "subtitle": "Annual run-rate comparison using equal workload ECPU demand.",
        "categories": categories,
        "as_is": as_is,
        "to_be": to_be,
        "as_is_label": _pick(config.get("current") or {}, "label", default="ADB-S As-Is"),
        "to_be_label": _pick(config.get("target") or {}, "label", default="ADB-D Dedicated"),
        "callout": f"Crossover: {crossover}" if crossover else "No crossover in modeled horizon",
        "bullets": bullets,
        "y_axis_min": _pick(chart_cfg, "y_axis_min", default=max(0, min(as_is + to_be) * 0.85 if as_is and to_be else 0)),
        "y_axis_max": _pick(chart_cfg, "y_axis_max", default=max(as_is + to_be) * 1.12 if as_is and to_be else 1),
        "y_axis_major_unit": _pick(chart_cfg, "y_axis_major_unit", default=0.5),
        "note": "Bars are native PowerPoint shapes for compatibility with lightweight renderers.",
    }


def build_business_value(config: dict) -> dict:
    impact = config.get("business_impact") or {}
    can_monetize = any(_num(impact, key, default=0) for key in [
        "business_impact_per_hour",
        "revenue_at_risk_per_hour",
        "transaction_margin_per_hour",
        "fraud_loss_impact_per_hour",
        "cost_per_outage_hour",
    ])
    treatment = (
        "Quantified only from customer-provided business impact per degraded/outage hour."
        if can_monetize
        else "Not converted to USD; customer business-impact input required."
    )
    rows = [
        {
            "area": "Financial baseline",
            "measure": "As-is run-rate, target run-rate, forecasted annual TCO.",
            "treatment": "Hard TCO only; no revenue impact invented.",
        },
        {
            "area": "Architecture benefit",
            "measure": "Local ADG read path, retired clones, explicit utilization headroom.",
            "treatment": "Explained separately from equal workload ECPU demand.",
        },
        {
            "area": "Risk-adjusted value",
            "measure": "avoided degraded/outage hours x business impact per hour",
            "treatment": treatment,
        },
        {
            "area": "Operational KPIs",
            "measure": "CPU utilization, read latency, ADG read lag, GoldenGate/apply lag, incidents avoided.",
            "treatment": "Tracked as success metrics after cutover.",
        },
    ]
    return {
        "title": "Business Value Model",
        "headline": "Risk-reduction value is explicit, not assumed as revenue uplift",
        "rows": rows,
    }


def build_cost_breakdown(config: dict, projection: list[dict]) -> dict:
    if not projection:
        return {}
    current = projection[0]
    target = config.get("target") or {}
    current_monthly = float(current["as_is_annual_tco"]) / 12
    target_monthly = float(current["to_be_annual_tco"]) / 12
    bridge_cost = goldengate_bridge_term_cost(config)
    cap = capacity_model(target, _num(config, "ecpu_per_db_node", default=760))
    notes = [
        f"Workload ECPU demand is modeled separately from physical capacity: {cap.label}.",
        "Cloud services, storage/infra, GoldenGate, operations, and one-time bridge assumptions remain separate.",
        f"GoldenGate mode: {_pick(config.get('goldengate') or {}, 'mode', default='not provided')}.",
    ]
    return {
        "title": "BOM + Operations Cost Breakdown",
        "scenarios": [
            {
                "name": _pick(config.get("current") or {}, "label", default="ADB-S As-Is"),
                "lines": [
                    {"item": "Cloud services", "monthly": money(current_monthly * 0.68), "annual": money(current_monthly * 0.68 * 12)},
                    {"item": "Storage / infrastructure", "monthly": money(current_monthly * 0.24), "annual": money(current_monthly * 0.24 * 12)},
                    {"item": "GoldenGate", "monthly": "As modeled", "annual": "As modeled"},
                    {"item": "Operations", "monthly": "Assumption", "annual": "Assumption"},
                ],
                "total": {"monthly": money(current_monthly), "annual": money(current["as_is_annual_tco"])},
            },
            {
                "name": _pick(config.get("target") or {}, "label", default="ADB-D Dedicated"),
                "lines": [
                    {"item": "Cloud services", "monthly": money(target_monthly * 0.50), "annual": money(target_monthly * 0.50 * 12)},
                    {"item": "Storage / infrastructure", "monthly": money(target_monthly * 0.42), "annual": money(target_monthly * 0.42 * 12)},
                    {"item": "Migration bridge / one-time", "monthly": "Year-1 only", "annual": money(bridge_cost) if bridge_cost else "Year-1 only"},
                    {"item": "Operations", "monthly": "Assumption", "annual": "Assumption"},
                ],
                "total": {"monthly": money(target_monthly), "annual": money(current["to_be_annual_tco"])},
            },
        ],
        "notes": notes,
    }


def enrich_adbs_to_adbd_business_case(spec: dict, catalog_path: str | None = None) -> dict:
    """Return a copy of a business-case spec enriched with reusable model output."""
    root = deepcopy(spec)
    bc = root.get("business_case", root)
    config = bc.get("adbs_to_adbd") or bc.get("adb_s_to_adb_d")
    if not isinstance(config, dict):
        return root
    config = {**config, "customer_name": _pick(bc, "customer_name", "customer"), "prepared_by": _pick(bc, "prepared_by", "author")}
    projection = build_tco_projection(config, catalog_path)
    tco = dict(bc.get("tco") or {})
    tco.setdefault("comparison_label", "ADB-S As-Is vs ADB-D Dedicated")
    tco["projection"] = [
        {
            "period": row["label"],
            "cpu": row["cpu"],
            "storage": row["storage"],
            "as_is": row["as_is"],
            "to_be": row["to_be"],
            "delta": row["delta"],
            "note": row["note"],
        }
        for row in projection
    ]
    if projection:
        tco["current_state"] = {
            "total_annual": projection[0]["as_is_annual_tco"],
            "annual_infrastructure": projection[0]["as_is_annual_tco"],
        }
        tco["proposed_oci"] = {
            "total_annual": projection[0]["to_be_annual_tco"],
            "annual_cloud_consumption": projection[0]["to_be_annual_tco"],
            "migration_one_time": _num(config.get("goldengate") or {}, "bridge_one_time_cost", default=0) or goldengate_bridge_term_cost(config, catalog_path),
        }
        tco["savings"] = {"annual": projection[0]["as_is_annual_tco"] - projection[0]["to_be_annual_tco"]}
    tco["breakdown"] = build_cost_breakdown(config, projection)
    tco["storage_economics"] = build_storage_economics(config, catalog_path)
    tco["crossover_chart"] = build_crossover_chart(projection, config)
    tco["business_value"] = build_business_value(config)
    tco["assumptions"] = [
        f"BYOL/PAYG model: {_pick(config, 'license_model', default='BYOL')}.",
        f"Discount: {pct(_pick(config, 'discount_pct', default=0)):.0%}.",
        f"Workload ECPU demand: {_num(config.get('current') or {}, 'workload_ecpu', 'ecpu_demand'):,.0f}.",
        capacity_model(config.get("target") or {}, _num(config, "ecpu_per_db_node", default=760)).label,
        f"Storage break-even: {tco['storage_economics']['break_even_tb']:,.0f} TB.",
        f"Crossover period: {first_crossover_period(projection) or 'not reached in modeled horizon'}.",
        f"GoldenGate bridge duration: {_pick(config.get('goldengate') or {}, 'bridge_months', 'fallback_months', default='not provided')}.",
    ]
    bc["tco"] = tco
    bc.setdefault("roi", {
        "headline": "Business Value Model",
        "label": "Risk-adjusted value requires customer-provided business impact.",
        "cards": [
            {"title": "Financial baseline", "metric": "Run-rate TCO", "detail": "As-is, to-be, and forecasted annual run-rate are separated."},
            {"title": "Architecture benefit", "metric": "Read path simplified", "detail": "ADB-D Local ADG read-only standby can retire steady-state clones when applicable."},
            {"title": "Risk value", "metric": "No invented revenue", "detail": "Use avoided degraded/outage hours x customer-provided impact per hour."},
        ],
    })
    bc.setdefault("value_drivers", [
        {
            "category": "cost",
            "title": "Storage offset",
            "quantified": f"{tco['storage_economics']['break_even_tb']:,.0f} TB break-even",
            "description": "ADB-S per-GB storage is compared with the fixed ADB-D footprint.",
        },
        {
            "category": "risk_reduction",
            "title": "Dedicated capacity headroom",
            "quantified": capacity_model(config.get("target") or {}, _num(config, "ecpu_per_db_node", default=760)).label,
            "description": "Dedicated physical capacity is shown separately from workload demand.",
        },
        {
            "category": "operations",
            "title": "Read architecture cleanup",
            "quantified": "Retire clones when ADG read path is adopted",
            "description": "Read clones remain only where the application read path still requires them.",
        },
    ])
    risks = bc.setdefault("risks", {})
    risks.setdefault("migration_risks", [
        {"risk": "Migration delay affects Year-1 bridge duration.", "mitigation": "Lock rehearsal plan and fallback window."},
        {"risk": "GoldenGate/apply lag during migration.", "mitigation": "Track apply lag during rehearsal and cutover."},
        {"risk": "Late capacity reservation.", "mitigation": "Reserve target DB and storage server footprint before cutover."},
    ])
    risks.setdefault("do_nothing_risks", [
        {"risk": "Clone/read model remains in production.", "impact": "Operational complexity and lag remain part of steady-state."},
        {"risk": "Cutover rehearsal risk remains unresolved.", "impact": "Decision delay compresses migration validation time."},
    ])
    if "business_case" in root:
        root["business_case"] = bc
    return root


def write_bom_outputs(config: dict, output_dir: str | Path, catalog_path: str | None = None) -> list[Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []
    for name, bom_spec in build_bom_specs(config).items():
        yaml_path = output_path / f"{name}.yaml"
        xlsx_path = output_path / f"{name}.xlsx"
        import yaml
        yaml_path.write_text(yaml.safe_dump(bom_spec, sort_keys=False), encoding="utf-8")
        gen = OCIBomGenerator.from_spec(bom_spec, catalog_path=catalog_path)
        gen.save(str(xlsx_path))
        saved.extend([yaml_path, xlsx_path])
    return saved
