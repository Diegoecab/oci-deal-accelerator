import sys
from pathlib import Path

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = PROJECT_ROOT / "tools"

if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from oci_deck_gen import OCIDeckGenerator
from oci_pptx_render import render_pptx_to_png


def test_render_pptx_to_png_detects_native_architecture_slide(tmp_path):
    spec = {
        "metadata": {
            "customer": "TestCo",
            "project": "Native Diagram",
            "subtitle": "Render test",
        },
        "summary": {
            "why": "Test native rendering",
            "current_state": ["Legacy DB"],
            "target_state": "OCI target",
            "timeline": "Q2",
        },
        "architecture": {
            "description": "Absolute layout render test",
            "visual": {
                "render_mode": "native_pptx",
                "absolute_layout": {
                    "canvas": {"width": 900, "height": 520},
                    "containers": [
                        {"id": "region", "type": "region", "label": "OCI Region", "x": 160, "y": 30, "w": 640, "h": 430},
                        {"id": "vcn", "type": "vcn", "label": "VCN 10.0.0.0/16", "x": 210, "y": 110, "w": 500, "h": 270},
                    ],
                    "services": [
                        {"id": "api", "type": "api_gateway", "label": "", "x": 290, "y": 170, "w": 90, "h": 84},
                        {"id": "oke", "type": "oke", "label": "", "x": 420, "y": 165, "w": 96, "h": 88},
                        {"id": "notify", "type": "notifications", "label": "", "x": 560, "y": 170, "w": 90, "h": 84},
                    ],
                    "labels": [
                        {"id": "lbl1", "text": "Coordinate-faithful reconstruction from the official Architecture Center diagram.", "x": 80, "y": 470, "w": 740, "h": 26},
                    ],
                    "connections": [],
                },
            },
        },
        "output": {"render_standard_sections": False},
        "custom_slides": [{
            "type": "diagram",
            "title": "Render Test",
            "description": "Coordinate-faithful reconstruction from the official Architecture Center diagram.",
            "visual": {
                "render_mode": "native_pptx",
                "absolute_layout": {
                    "canvas": {"width": 900, "height": 520},
                    "containers": [
                        {"id": "region", "type": "region", "label": "OCI Region", "x": 160, "y": 30, "w": 640, "h": 430},
                    ],
                    "services": [
                        {"id": "api", "type": "api_gateway", "label": "", "x": 320, "y": 170, "w": 90, "h": 84},
                        {"id": "notify", "type": "notifications", "label": "", "x": 480, "y": 170, "w": 90, "h": 84},
                    ],
                    "labels": [
                        {"id": "lbl1", "text": "Coordinate-faithful reconstruction from the official Architecture Center diagram.", "x": 90, "y": 470, "w": 720, "h": 26},
                    ],
                    "connections": [],
                },
            },
        }],
    }

    pptx_path = tmp_path / "render-test.pptx"
    png_path = tmp_path / "render-test.png"

    gen = OCIDeckGenerator.from_spec(spec)
    gen.save(str(pptx_path))

    meta = render_pptx_to_png(pptx_path, png_path, width=1200)

    assert png_path.is_file()
    assert meta["display_number"] >= 1
    assert meta["shape_counts"]["grpSp"] >= 2
    with Image.open(png_path) as image:
        assert image.size[0] == 1200
        assert image.getbbox() is not None
