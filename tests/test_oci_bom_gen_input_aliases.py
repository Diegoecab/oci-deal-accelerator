import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = PROJECT_ROOT / "tools"

if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from oci_bom_gen import OCIBomGenerator


def test_from_spec_accepts_metadata_and_line_item_aliases():
    spec = {
        "customer": "Acme Corp",
        "project": "Database Migration",
        "author": "Diego",
        "reference": "REF-1",
        "conversion": {
            "currency": "BRL",
            "exchange_rate": 5.2,
            "tax_rate": 0.1,
        },
        "line_items": [
            {
                "part_number": "SKU-001",
                "quantity": 2,
                "units": 730,
                "discount_pct": 15,
                "label": "Database",
                "note": "Primary environment",
            }
        ],
    }

    gen = OCIBomGenerator.from_spec(spec)
    item = gen.line_items[0]

    assert gen.customer == "Acme Corp"
    assert gen.project == "Database Migration"
    assert gen.prepared_by == "Diego"
    assert gen.reference_label == "REF-1"
    assert gen.conversion["target_currency"] == "BRL"
    assert item["sku"] == "SKU-001"
    assert item["qty"] == 2
    assert item["hours_units"] == 730
    assert item["discount"] == 15
    assert item["custom_label"] == "Database"
    assert item["custom_note"] == "Primary environment"


def test_from_spec_accepts_canonical_sku_and_custom_note():
    spec = {
        "line_items": [
            {
                "sku": "SKU-002",
                "qty": 1,
                "hours_units": 100,
                "custom_note": "Canonical form",
            }
        ]
    }

    gen = OCIBomGenerator.from_spec(spec)
    item = gen.line_items[0]

    assert item["sku"] == "SKU-002"
    assert item["qty"] == 1
    assert item["hours_units"] == 100
    assert item["custom_note"] == "Canonical form"


def test_from_spec_requires_sku_or_part_number():
    spec = {"line_items": [{"quantity": 1}]}

    with pytest.raises(ValueError, match="sku"):
        OCIBomGenerator.from_spec(spec)
