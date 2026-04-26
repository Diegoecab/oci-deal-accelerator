import sys
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = PROJECT_ROOT / "tools"

if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from oci_deck_gen import OCIDeckGenerator
from oci_pptx_diagram_gen import NativePPTXDiagramRenderer


def test_native_pptx_architecture_slide_renders_into_saved_deck(tmp_path):
    spec = {
        "metadata": {
            "customer": "TestCo",
            "project": "Native Diagram",
            "subtitle": "Smoke test",
        },
        "summary": {
            "why": "Test native rendering",
            "current_state": ["Legacy DB"],
            "target_state": "OCI target",
            "timeline": "Q2",
        },
        "architecture": {
            "description": "Two-region native PPTX test",
            "visual": {
                "render_mode": "native_pptx",
                "on_prem": {"name": "On-Premises", "connection": "FastConnect"},
                "regions": [
                    {
                        "name": "Ashburn",
                        "label": "PRIMARY",
                        "availability_domains": [
                            {
                                "name": "Availability Domain 1",
                                "vcn": {
                                    "name": "VCN",
                                    "cidr": "10.10.0.0/16",
                                    "subnets": [
                                        {
                                            "name": "App Subnet",
                                            "cidr": "10.10.10.0/24",
                                            "services": [
                                                {"id": "lb", "name": "Load Balancer", "type": "load_balancer"},
                                                {"id": "vm1", "name": "Virtual Machine", "type": "virtual_machine"},
                                                {"id": "sgw", "name": "Service Gateway", "type": "service_gateway"},
                                            ],
                                        },
                                        {
                                            "name": "Data Subnet",
                                            "cidr": "10.10.20.0/24",
                                            "services": [
                                                {"id": "db", "name": "ADB-D", "type": "adb_d"},
                                                {"id": "safe", "name": "Data Safe", "type": "data_safe"},
                                                {"id": "obj", "name": "Object Storage", "type": "object_storage"},
                                            ],
                                        },
                                    ],
                                },
                            },
                            {
                                "name": "Availability Domain 2",
                                "vcn": {
                                    "name": "VCN",
                                    "cidr": "10.10.0.0/16",
                                    "subnets": [
                                        {
                                            "name": "Standby Subnet",
                                            "cidr": "10.10.30.0/24",
                                            "services": [
                                                {"id": "dg", "name": "Data Guard", "type": "data_guard"},
                                            ],
                                        },
                                    ],
                                },
                            },
                        ],
                    },
                    {
                        "name": "Montreal",
                        "label": "DR STANDBY",
                        "services": [
                            {"id": "drdb", "name": "ADB-D", "type": "adb_d"},
                            {"id": "drdg", "name": "Data Guard", "type": "data_guard"},
                        ],
                        "details": "Cross-region DR",
                    },
                ],
                "connections": [
                    {"from": "lb", "to": "vm1", "label": "HTTPS"},
                    {"from": "vm1", "to": "db", "label": "SQL"},
                    {"from": "db", "to": "dg", "label": "ADG"},
                    {"from": "db", "to": "drdb", "label": "DR", "style": "dashed"},
                ],
                "security_footer": "OCI-native smoke test footer",
            },
        },
    }

    output = tmp_path / "native-smoke-test.pptx"
    gen = OCIDeckGenerator.from_spec(spec)
    gen.save(str(output))

    assert output.is_file()
    with zipfile.ZipFile(output) as archive:
        slide_xml = b"".join(
            archive.read(name)
            for name in archive.namelist()
            if name.startswith("ppt/slides/slide") and name.endswith(".xml")
        ).decode("utf-8", errors="ignore")
        rels_xml = b"".join(
            archive.read(name)
            for name in archive.namelist()
            if name.startswith("ppt/slides/_rels/slide") and name.endswith(".rels")
        ).decode("utf-8", errors="ignore")
        media_files = [
            name for name in archive.namelist()
            if name.startswith("ppt/media/")
        ]

    assert "Availability Domain 1" in slide_xml
    assert "FastConnect" in slide_xml
    assert "OCI-native smoke test footer" in slide_xml
    assert "Load" in slide_xml
    assert "relationships/image" in rels_xml
    assert media_files


def test_native_pptx_icon_resolution_accepts_common_aliases():
    renderer = NativePPTXDiagramRenderer()

    compute_ref = renderer._resolve_icon_ref(
        {"name": "Virtual Machine app tier", "type": "compute"}
    )
    lb_ref = renderer._resolve_icon_ref(
        {"name": "Ingress", "type": "public_load_balancer"}
    )
    storage_ref = renderer._resolve_icon_ref(
        {"name": "Object Storage (DR)", "type": "storage"}
    )

    assert compute_ref is not None
    assert compute_ref["display_number"] in {29, 30, 32, 34}
    assert lb_ref is not None
    assert "load" in lb_ref["text"].lower()
    assert storage_ref is not None
    assert "object" in storage_ref["text"].lower()


def test_native_pptx_icon_resolution_prefers_compact_refs_for_problem_icons():
    renderer = NativePPTXDiagramRenderer()

    api_ref = renderer._resolve_icon_ref({"name": "OCI API Gateway", "type": "api_gateway"})
    notify_ref = renderer._resolve_icon_ref({"name": "Notifications", "type": "notifications"})
    oke_ref = renderer._resolve_icon_ref({"name": "OKE cluster", "type": "oke"})
    vpn_ref = renderer._resolve_icon_ref({"name": "Site-to-Site VPN", "type": "vpn"})

    assert api_ref is not None
    assert notify_ref is not None
    assert oke_ref is not None
    assert vpn_ref is not None
    assert int(api_ref["bbox"]["cx"]) < 2_500_000
    assert int(notify_ref["bbox"]["cx"]) < 2_500_000
    assert int(oke_ref["bbox"]["cx"]) < 2_500_000
