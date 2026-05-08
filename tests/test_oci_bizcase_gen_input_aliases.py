import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = PROJECT_ROOT / "tools"

if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from oci_bizcase_gen import BusinessCaseDeckGenerator


def _collect_slide_text(gen):
    texts = []
    for slide in gen.prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text = shape.text.strip()
                if text:
                    texts.append(text)
            if getattr(shape, "has_table", False):
                for row in shape.table.rows:
                    for cell in row.cells:
                        text = cell.text.strip()
                        if text:
                            texts.append(text)
    return "\n".join(texts)


def test_from_spec_accepts_cover_aliases_and_recommendation_fallback():
    spec = {
        "customer": "Acme Corp",
        "author": "Diego",
        "generated_on": "2026-04-21",
        "recommendation": {
            "commitment_amount": "100K",
            "commitment_type": "UCM",
        },
    }

    gen = BusinessCaseDeckGenerator.from_spec(spec)
    text = _collect_slide_text(gen)

    assert "Acme Corp" in text
    assert "Prepared by: Diego" in text
    assert "Recommended: 100K UCM commitment" in text


def test_from_spec_accepts_roadmap_aliases_and_mixed_next_steps():
    spec = {
        "customer_name": "Acme Corp",
        "roadmap": {
            "phases": [
                {
                    "title": "Assess",
                    "weeks": "2 weeks",
                    "outputs": ["Blueprint"],
                    "milestones": ["Kickoff"],
                }
            ],
            "total_duration": "6 weeks",
        },
        "recommendation": {
            "summary": "Proceed with phased migration",
            "next_steps": [
                "Confirm scope",
                {"action": "Approve budget", "owner": "Finance", "deadline": "May"},
            ],
        },
    }

    gen = BusinessCaseDeckGenerator.from_spec(spec)
    text = _collect_slide_text(gen)

    assert "Assess" in text
    assert "2 weeks" in text
    assert "Kickoff" in text
    assert "Blueprint" in text
    assert "Confirm scope" in text
    assert "Approve budget" in text
    assert "Finance" in text
    assert "May" in text


def test_from_spec_enriches_sparse_business_case_from_executive_summary():
    spec = {
        "customer_name": "Acme Corp",
        "executive_summary": (
            "Acme wants to move an on-prem Oracle platform to OCI to reduce cost "
            "and improve disaster recovery in 12 weeks."
        ),
    }

    gen = BusinessCaseDeckGenerator.from_spec(spec)
    text = _collect_slide_text(gen)

    assert "Business Drivers" in text
    assert "Risk Assessment" in text
    assert "Implementation Roadmap" in text
    assert "Our Recommendation" in text
    assert "12 weeks" in text


def test_from_spec_enriches_adbs_to_adbd_business_case_without_meli_hardcoding():
    spec = {
        "customer_name": "Synthetic Retail",
        "cover_subtitle": "ADB-S to ADB-D Migration Business Case",
        "prepared_by": "Diego Cabrera",
        "prepared_by_role": "Solutions Architect",
        "executive_summary": "Move a fraud analytics workload from ADB-S to ADB-D for stability.",
        "adbs_to_adbd": {
            "license_model": "BYOL",
            "discount_pct": 0.11,
            "ecpu_per_db_node": 760,
            "current": {"label": "ADB-S As-Is", "workload_ecpu": 1000, "storage_tb": 80},
            "target": {"label": "ADB-D Dedicated", "workload_ecpu": 1000, "storage_tb": 80, "db_nodes": 2, "storage_servers": 3},
            "forecasts": [
                {
                    "period": "24M",
                    "display_label": "Year 2",
                    "as_is": {"workload_ecpu": 1300, "storage_tb": 120},
                    "to_be": {"workload_ecpu": 1300, "storage_tb": 120, "db_nodes": 3, "storage_servers": 3},
                }
            ],
            "goldengate": {"mode": "migration_bridge_only", "ocpus": 2, "bridge_months": 3},
        },
    }

    gen = BusinessCaseDeckGenerator.from_spec(spec)
    text = _collect_slide_text(gen)

    assert "Prepared by: Diego Cabrera, Solutions Architect" in text
    assert "ADB-S As-Is" in text
    assert "ADB-D Dedicated" in text
    assert "BOM + Operations Cost Breakdown" in text
    assert "TCO Crossover" in text
    assert "Business Value Model" in text
    assert "Workload ECPU demand" in text
    assert "ECPU capacity" in text
    assert "No invented revenue" in text
    assert "MELI" not in text
