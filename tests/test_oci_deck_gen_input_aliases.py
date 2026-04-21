import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = PROJECT_ROOT / "tools"

if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from oci_deck_gen import OCIDeckGenerator


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


def test_from_spec_accepts_metadata_aliases_and_current_state_string():
    spec = {
        "metadata": {
            "customer_name": "Acme Corp",
            "project_name": "DB Migration",
            "prepared_by": "Diego",
            "title": "Target Architecture",
        },
        "summary": {
            "why": "Modernize platform",
            "current_state": "Legacy estate",
            "target_state": "OCI landing zone",
            "timeline": "Q3",
        },
    }

    gen = OCIDeckGenerator.from_spec(spec)
    text = _collect_slide_text(gen)

    assert gen.customer == "Acme Corp"
    assert gen.project == "DB Migration"
    assert gen.architect == "Diego"
    assert "Legacy estate" in text
    assert "OCI landing zone" in text


def test_from_spec_accepts_aliases_for_cost_migration_risk_scorecard_and_next_steps():
    spec = {
        "metadata": {"customer": "Acme"},
        "cost": {
            "line_items": [
                {"name": "DB Service", "monthly": "USD 100", "note": "Includes storage"}
            ],
            "assumptions": ["1 region"],
            "show_byol": False,
        },
        "migration": {
            "phases": [
                {"title": "Discover", "weeks": "2 weeks", "tasks": ["Inventory", "Assess"]}
            ],
            "tools": ["ZDM"],
            "downtime": "Near-zero",
        },
        "risks": [
            {"title": "Cutover risk", "action": "Pilot first", "severity": "high"}
        ],
        "scorecard": {
            "pillars": [
                {"pillar": "Security", "status": "PASS", "passed": 2, "total": 2}
            ],
            "recommendations": ["Enable auditing"],
        },
        "next_steps": {"next_steps": ["Validate scope"]},
    }

    gen = OCIDeckGenerator.from_spec(spec)
    text = _collect_slide_text(gen)

    assert "DB Service" in text
    assert "USD 100" in text
    assert "Includes storage" in text
    assert "Discover" in text
    assert "Inventory" in text
    assert "Cutover risk" in text
    assert "Pilot first" in text
    assert "Security" in text
    assert "2/2" in text
    assert "Validate scope" in text
