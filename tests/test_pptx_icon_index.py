import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = PROJECT_ROOT / "tools"

if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from refresh_pptx_icon_index import DEFAULT_CONFIG_PATH, build_outputs, load_config


def test_build_outputs_detects_semantic_slides_for_bundled_oci_icons():
    config = load_config(DEFAULT_CONFIG_PATH)
    asset = PROJECT_ROOT / config["asset"]["bundled_path"]

    index, manifest = build_outputs(asset, config)

    assert asset.is_file()
    assert index["library"]["slide_count"] >= 40
    assert "connectors_logical" in index["semantic_slides"]
    assert "grouping" in index["semantic_slides"]
    assert "database_icons" in index["semantic_slides"]
    assert len(index["slide_catalog"]) == index["library"]["slide_count"]
    assert index["instruction_catalog"]["slide_count_with_instructions"] >= 10
    assert manifest["asset"]["sha256"] == index["library"]["sha256"]


def test_build_outputs_extracts_expected_database_icon_refs():
    config = load_config(DEFAULT_CONFIG_PATH)
    asset = PROJECT_ROOT / config["asset"]["bundled_path"]

    index, _ = build_outputs(asset, config)
    icons = index["stencils"]["database_icons"]

    assert "adb_d" in icons
    assert "atp_d" in icons
    assert "adw_d" in icons
    assert "data_guard" in icons


def test_build_outputs_indexes_full_slide_and_shape_library():
    config = load_config(DEFAULT_CONFIG_PATH)
    asset = PROJECT_ROOT / config["asset"]["bundled_path"]

    index, manifest = build_outputs(asset, config)
    slide_catalog = index["slide_catalog"]
    instruction_slides = {
        slide["display_number"]: slide
        for slide in index["instruction_catalog"]["slides"]
    }
    shape_library = index["shape_library"]["entries"]

    assert slide_catalog[0]["display_number"] == 1
    assert slide_catalog[-1]["display_number"] == index["library"]["slide_count"]
    assert 10 in instruction_slides
    assert 18 in instruction_slides
    assert 43 in instruction_slides
    assert any("Open Arrowhead style" in line for line in instruction_slides[10]["instruction_lines"])
    assert any("OCI Region" in line for line in instruction_slides[18]["instruction_lines"])
    assert "adb_d" in shape_library
    assert "data_guard" in shape_library
    assert "api_gateway" in shape_library
    assert "notifications" in shape_library
    assert "oci_container_engine_for_kubernetes" in shape_library
    assert any(ref.get("node_path") and len(ref["node_path"]) > 1 for ref in shape_library["api_gateway"])
    assert manifest["coverage"]["catalogued_slides"] == index["library"]["slide_count"]
