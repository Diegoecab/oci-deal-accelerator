import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = PROJECT_ROOT / "tools"

if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from oci_business_case_model import (  # noqa: E402
    SKU_ADBD_DB_SERVER,
    SKU_ADBD_STORAGE_SERVER,
    SKU_ADBS_STORAGE_ATP,
    build_bom_specs,
    build_crossover_chart,
    build_storage_economics,
    build_tco_projection,
    capacity_model,
    first_crossover_period,
    storage_break_even_tb,
)


def _scenario():
    return {
        "customer_name": "Synthetic Retail",
        "prepared_by": "Diego Cabrera",
        "license_model": "BYOL",
        "discount_pct": 0.10,
        "ecpu_per_db_node": 760,
        "current": {
            "label": "ADB-S As-Is",
            "workload_ecpu": 1000,
            "storage_tb": 80,
        },
        "target": {
            "label": "ADB-D Dedicated",
            "workload_ecpu": 1000,
            "storage_tb": 80,
            "db_nodes": 2,
            "storage_servers": 3,
        },
        "forecasts": [
            {
                "period": "24M",
                "display_label": "Year 2",
                "as_is": {"workload_ecpu": 1300, "storage_tb": 120},
                "to_be": {"workload_ecpu": 1300, "storage_tb": 120, "db_nodes": 3, "storage_servers": 3},
            },
            {
                "period": "36M",
                "display_label": "Year 3",
                "as_is": {"workload_ecpu": 1600, "storage_tb": 160},
                "to_be": {"workload_ecpu": 1600, "storage_tb": 160, "db_nodes": 4, "storage_servers": 3},
            },
        ],
        "goldengate": {"mode": "migration_bridge_only", "ocpus": 2, "bridge_months": 3},
    }


def test_capacity_model_separates_workload_demand_from_physical_capacity():
    cap = capacity_model({"workload_ecpu": 3705, "db_nodes": 7}, 760)

    assert cap.physical_capacity_ecpu == 5320
    assert round(cap.utilization_pct) == 70
    assert "3,705 ECPU used over 5,320 ECPU capacity" in cap.label


def test_storage_break_even_calculation_applies_uniform_discount():
    tb = storage_break_even_tb(14500, 0.1156, 0.10)

    assert round(tb) == round(14500 / (0.1156 * 0.90) / 1024)


def test_build_bom_specs_generates_current_and_projected_run_rate_boms():
    specs = build_bom_specs(_scenario())

    assert "current_as_is" in specs
    assert "to_be_steady_state" in specs
    assert "as_is_projected_24m" in specs
    assert "to_be_projected_36m" in specs
    assert "migration_bridge_year1" in specs

    current_skus = {item["sku"] for item in specs["current_as_is"]["bom"]["line_items"]}
    target_skus = {item["sku"] for item in specs["to_be_steady_state"]["bom"]["line_items"]}
    future_target_skus = {item["sku"] for item in specs["to_be_projected_36m"]["bom"]["line_items"]}
    bridge_skus = {item["sku"] for item in specs["migration_bridge_year1"]["bom"]["line_items"]}

    assert SKU_ADBS_STORAGE_ATP in current_skus
    assert SKU_ADBD_DB_SERVER in target_skus
    assert SKU_ADBD_STORAGE_SERVER in target_skus
    assert future_target_skus == target_skus
    assert "B92993" in bridge_skus
    assert "B92993" not in future_target_skus
    assert any("annual run-rate snapshots" in note for note in specs["to_be_projected_36m"]["bom"]["notes"])


def test_forecast_projection_and_crossover_chart_are_native_shape_ready():
    projection = build_tco_projection(_scenario())
    chart = build_crossover_chart(projection, _scenario())

    assert projection[0]["label"] == "Near-term"
    assert chart["categories"] == ["Near-term", "Year 2", "Year 3"]
    assert chart["note"].startswith("Bars are native PowerPoint shapes")
    assert chart["bullets"][0].startswith("Near-term: ADB-D")


def test_storage_economics_exposes_break_even_and_offset():
    economics = build_storage_economics(_scenario())

    assert economics["break_even_tb"] > 0
    assert economics["storage_offset_monthly"] > 0
    assert any(card["label"] == "Storage offset" for card in economics["cards"])


def test_first_crossover_period_detects_first_cheaper_target():
    rows = [
        {"label": "Near-term", "as_is_annual_tco": 100, "to_be_annual_tco": 110},
        {"label": "Year 1", "as_is_annual_tco": 120, "to_be_annual_tco": 115},
    ]

    assert first_crossover_period(rows) == "Year 1"
