import base64
import sys
import zlib
from pathlib import Path
from urllib.parse import quote

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = PROJECT_ROOT / "tools"

if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from archcenter_case_runner import _canonical_service_label, _label_to_type, extract_layout
from drawio_visual_validator import validate_drawio
from oci_archcenter_batch import choose_zip_urls, process_case
from oci_diagram_gen import OCIDiagramGenerator


def test_extract_layout_recovers_service_from_layered_userobject_icon(tmp_path):
    drawio = tmp_path / "layered.drawio"
    drawio.write_text(
        """<mxfile host="app.diagrams.net">
  <diagram id="d1" name="Page-1">
    <mxGraphModel dx="800" dy="600" grid="1" gridSize="10">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <UserObject id="svc-base" label="">
          <mxCell parent="1" style="shape=stencil(base);fillColor=#FFFFFF;strokeColor=none;" vertex="1">
            <mxGeometry x="100" y="100" width="60" height="60" as="geometry"/>
          </mxCell>
        </UserObject>
        <UserObject id="svc-top" label="">
          <mxCell parent="1" style="shape=stencil(top);fillColor=#2D5967;strokeColor=none;" vertex="1">
            <mxGeometry x="101" y="101" width="58" height="58" as="geometry"/>
          </mxCell>
        </UserObject>
        <UserObject id="svc-label" label="Object Storage">
          <mxCell parent="1" style="verticalAlign=middle;align=center;overflow=width;shape=stencil(label);fillColor=none;strokeColor=none;" vertex="1">
            <mxGeometry x="82" y="168" width="95" height="20" as="geometry"/>
          </mxCell>
        </UserObject>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
""",
        encoding="utf-8",
    )

    result = extract_layout(drawio)

    assert len(result.services) == 1
    assert result.services[0]["type"] == "object_storage"
    assert result.icon_clusters_total == 1
    assert result.icon_clusters_classified == 1


def test_choose_zip_urls_prefers_architecture_assets_over_functional_assets():
    ordered = choose_zip_urls([
        "https://docs.oracle.com/en/solutions/example/img/lakehouse-functional-oracle.zip",
        "https://docs.oracle.com/en/solutions/example/img/lakehouse-architecture-oracle.zip",
        "https://docs.oracle.com/en/solutions/example/img/lakehouse-overview-oracle.zip",
    ])

    assert ordered[0].endswith("lakehouse-architecture-oracle.zip")
    assert ordered[-1].endswith("lakehouse-overview-oracle.zip")


def test_label_to_type_normalizes_multiline_captions():
    assert _label_to_type("Internet\ngateway") == "internet_gateway"
    assert _label_to_type("Virtual\nMachine") == "virtual_machine"
    assert _label_to_type("Oracle\nIntegration 3") == "integration"


def test_label_to_type_prefers_autonomous_database_when_integration_noise_leaks_in():
    assert _label_to_type(
        "OCI Region\nOracle\nIntegration 3\nAutonomous\nInstance\nDatabase"
    ) == "adb_d"


def test_canonical_service_label_drops_nearby_annotation_noise():
    assert _canonical_service_label(
        "drg",
        'Match attachment "VCN-3"\nDRG\nVCN-4 Import Route Distribution',
    ) == "DRG"
    assert _canonical_service_label(
        "oracle_exadata_database_service",
        "Oracle Services Network\nRecovery Service",
    ) == ""


def test_extract_layout_supports_compressed_drawio_payloads(tmp_path):
    graph_xml = (
        '<mxGraphModel><root>'
        '<mxCell id="0"/>'
        '<mxCell id="1" parent="0"/>'
        '<UserObject id="svc" label="">'
        '<mxCell parent="1" style="shape=stencil(icon);fillColor=#FFFFFF;strokeColor=none;" vertex="1">'
        '<mxGeometry x="120" y="120" width="60" height="60" as="geometry"/>'
        '</mxCell></UserObject>'
        '<UserObject id="lbl" label="Internet Gateway">'
        '<mxCell parent="1" style="verticalAlign=middle;align=center;overflow=width;shape=stencil(label);fillColor=none;strokeColor=none;" vertex="1">'
        '<mxGeometry x="92" y="190" width="120" height="20" as="geometry"/>'
        '</mxCell></UserObject>'
        "</root></mxGraphModel>"
    )
    compressor = zlib.compressobj(level=9, wbits=-15)
    compressed_bytes = compressor.compress(quote(graph_xml).encode("utf-8")) + compressor.flush()
    compressed = base64.b64encode(compressed_bytes).decode("ascii")
    drawio = tmp_path / "compressed.drawio"
    drawio.write_text(
        f'<mxfile host="app.diagrams.net"><diagram id="d1">{compressed}</diagram></mxfile>',
        encoding="utf-8",
    )

    result = extract_layout(drawio)

    assert len(result.services) == 1
    assert result.services[0]["type"] == "internet_gateway"


def test_extract_layout_merges_nested_icon_satellite_cells(tmp_path):
    drawio = tmp_path / "satellite.drawio"
    drawio.write_text(
        """<mxfile host="app.diagrams.net">
  <diagram id="d1" name="Page-1">
    <mxGraphModel dx="800" dy="600" grid="1" gridSize="10">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <UserObject id="svc-base" label="">
          <mxCell parent="1" style="shape=stencil(base);fillColor=#FFFFFF;strokeColor=none;" vertex="1">
            <mxGeometry x="100" y="100" width="63" height="59" as="geometry"/>
          </mxCell>
        </UserObject>
        <UserObject id="svc-overlay" label="">
          <mxCell parent="1" style="shape=stencil(overlay);fillColor=#2D5967;strokeColor=none;" vertex="1">
            <mxGeometry x="135" y="123" width="26" height="35" as="geometry"/>
          </mxCell>
        </UserObject>
        <UserObject id="svc-label" label="Object Storage">
          <mxCell parent="1" style="verticalAlign=middle;align=center;overflow=width;shape=stencil(label);fillColor=none;strokeColor=none;" vertex="1">
            <mxGeometry x="88" y="168" width="95" height="20" as="geometry"/>
          </mxCell>
        </UserObject>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
""",
        encoding="utf-8",
    )

    result = extract_layout(drawio)

    assert len(result.services) == 1
    assert result.services[0]["type"] == "object_storage"
    assert len(result.services[0]["raw_icon_cells"]) == 2


def test_drawio_absolute_layout_preserves_raw_icon_cells(tmp_path):
    spec = {
        "absolute_layout": {
            "canvas": {"width": 180, "height": 120},
            "containers": [],
            "services": [{
                "id": "svc1",
                "label": "",
                "type": "custom_unknown",
                "x": 24,
                "y": 16,
                "w": 60,
                "h": 60,
                "raw_icon_cells": [
                    '<mxCell id="10" parent="1" style="shape=stencil(custom_base);fillColor=#FFFFFF;strokeColor=none;" vertex="1"><mxGeometry x="0" y="0" width="60" height="60" as="geometry"/></mxCell>',
                    '<mxCell id="11" parent="1" style="shape=stencil(custom_overlay);fillColor=#2D5967;strokeColor=none;" vertex="1"><mxGeometry x="12" y="14" width="24" height="24" as="geometry"/></mxCell>',
                ],
            }],
            "labels": [],
            "connections": [],
        },
    }

    output = tmp_path / "raw-icon.drawio"
    OCIDiagramGenerator.from_spec(spec).save(output)
    xml = output.read_text(encoding="utf-8")

    assert "shape=stencil(custom_base)" in xml
    assert "shape=stencil(custom_overlay)" in xml


def test_drawio_absolute_layout_preserves_raw_underlay_cells_before_objects(tmp_path):
    spec = {
        "absolute_layout": {
            "canvas": {"width": 180, "height": 120},
            "containers": [],
            "services": [],
            "labels": [{
                "id": "lbl1",
                "text": "OCI Region",
                "x": 60,
                "y": 18,
                "w": 70,
                "h": 18,
                "fontSize": 700,
            }],
            "raw_underlay_cells": [
                '<mxCell id="u10" parent="1" style="shape=stencil(context_box);fillColor=#FFFFFF;strokeColor=none;" vertex="1"><mxGeometry x="6" y="4" width="36" height="18" as="geometry"/></mxCell>',
            ],
            "connections": [],
        },
    }

    output = tmp_path / "raw-underlay.drawio"
    OCIDiagramGenerator.from_spec(spec).save(output)
    xml = output.read_text(encoding="utf-8")

    assert "shape=stencil(context_box)" in xml
    assert xml.index("shape=stencil(context_box)") < xml.index('value="OCI Region"')


def test_validate_drawio_supports_compressed_payloads(tmp_path):
    graph_xml = (
        '<mxGraphModel><root>'
        '<mxCell id="0"/>'
        '<mxCell id="1" parent="0"/>'
        '<UserObject id="svc" label="">'
        '<mxCell parent="1" style="shape=stencil(icon);fontSize=14;" vertex="1">'
        '<mxGeometry x="120" y="120" width="60" height="60" as="geometry"/>'
        '</mxCell></UserObject>'
        "</root></mxGraphModel>"
    )
    compressor = zlib.compressobj(level=9, wbits=-15)
    compressed_bytes = compressor.compress(quote(graph_xml).encode("utf-8")) + compressor.flush()
    compressed = base64.b64encode(compressed_bytes).decode("ascii")
    drawio = tmp_path / "compressed.drawio"
    drawio.write_text(
        f'<mxfile host="app.diagrams.net"><diagram id="d1">{compressed}</diagram></mxfile>',
        encoding="utf-8",
    )

    report = validate_drawio(drawio)

    assert report["status"] == "pass"
    assert report["cell_count"] > 0
    assert report["issue_count"] == 0


def test_process_case_forwards_fidelity_threshold_and_requires_native_fidelity(tmp_path, monkeypatch):
    output_root = tmp_path / "batch"
    candidate = {
        "entry": {
            "title": "Example Architecture",
            "url": "https://docs.oracle.com/en/solutions/example/index.html",
            "date": "2026-04",
            "tags": ["database"],
            "services": ["exacs"],
        }
    }
    reference_drawio = tmp_path / "reference.drawio"
    reference_drawio.write_text(
        '<mxfile><diagram id="d1"><mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/></root></mxGraphModel></diagram></mxfile>',
        encoding="utf-8",
    )
    reference_png = tmp_path / "reference.png"
    Image.new("RGB", (32, 24), "white").save(reference_png)
    reference_svg = tmp_path / "reference.svg"
    reference_svg.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>', encoding="utf-8")

    def fake_stage_reference_assets(candidate_arg, case_dir):
        (case_dir / "evidence").mkdir(parents=True, exist_ok=True)
        return reference_drawio, reference_png, reference_svg, {"chosen_zip": "example.zip"}

    captured: dict = {}

    def fake_run_case(**kwargs):
        captured.update(kwargs)
        return {
            "drawio": {
                "rebuilt_path": "examples/out/example-rebuilt.drawio",
                "status": "rebuilt+verbatim",
            },
            "pptx": {
                "status": "ok",
                "audit": {"unresolved_count": 0, "oversize_ref_count": 0},
            },
            "pptx_fidelity": {"status": "pass"},
            "fidelity": {"status": "pass"},
            "eval": {"status": "fail"},
            "extraction": {"icon_clusters_total": 2, "icon_clusters_classified": 2},
        }

    monkeypatch.setattr("oci_archcenter_batch.stage_reference_assets", fake_stage_reference_assets)
    monkeypatch.setattr("oci_archcenter_batch.run_case", fake_run_case)

    result = process_case(candidate, 1, output_root, 0.82, 0.91)

    assert captured["fidelity_threshold"] == 0.91
    assert result["status"] == "PASS"
    assert result["reasons"] == []

    def fake_run_case_fail(**kwargs):
        return {
            "drawio": {
                "rebuilt_path": "examples/out/example-rebuilt.drawio",
                "status": "rebuilt+verbatim",
            },
            "pptx": {
                "status": "ok",
                "audit": {"unresolved_count": 0, "oversize_ref_count": 0},
            },
            "pptx_fidelity": {"status": "fail"},
            "fidelity": {"status": "pass"},
            "eval": {"status": "pass"},
            "extraction": {"icon_clusters_total": 2, "icon_clusters_classified": 2},
        }

    monkeypatch.setattr("oci_archcenter_batch.run_case", fake_run_case_fail)
    result_fail = process_case(candidate, 2, output_root, 0.82, 0.91)

    assert result_fail["status"] == "FAIL"
    assert "pptx_fidelity" in result_fail["reasons"]


def test_process_case_skips_cases_outside_native_benchmark_pool(tmp_path, monkeypatch):
    output_root = tmp_path / "batch"
    candidate = {
        "entry": {
            "title": "Learn about dynamic routing gateway solutions",
            "url": "https://docs.oracle.com/en/solutions/example/index.html",
            "date": "2026-04",
            "tags": ["networking"],
            "services": ["drg", "fastconnect"],
        }
    }
    reference_drawio = tmp_path / "reference.drawio"
    reference_drawio.write_text(
        '<mxfile><diagram id="d1"><mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/></root></mxGraphModel></diagram></mxfile>',
        encoding="utf-8",
    )
    reference_png = tmp_path / "reference.png"
    Image.new("RGB", (32, 24), "white").save(reference_png)

    def fake_stage_reference_assets(candidate_arg, case_dir):
        (case_dir / "evidence").mkdir(parents=True, exist_ok=True)
        return reference_drawio, reference_png, None, {"chosen_zip": "example.zip"}

    def fail_run_case(**kwargs):
        raise AssertionError("run_case should not execute for skipped candidates")

    monkeypatch.setattr("oci_archcenter_batch.stage_reference_assets", fake_stage_reference_assets)
    monkeypatch.setattr(
        "oci_archcenter_batch.assess_native_suitability",
        lambda title, drawio_path: {"benchmarkable": False, "reasons": ["label_heavy"]},
    )
    monkeypatch.setattr("oci_archcenter_batch.run_case", fail_run_case)

    result = process_case(candidate, 1, output_root, 0.82, 0.91)

    assert result["status"] == "SKIP"
    assert result["preflight"]["reasons"] == ["label_heavy"]
