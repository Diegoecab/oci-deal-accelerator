import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = PROJECT_ROOT / "tools"

if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from oci_diagram_gen import OCIDiagramGenerator


def test_from_spec_accepts_name_aliases_and_generates_ids():
    spec = {
        "external": [{"name": "Users"}],
        "clouds": [{"name": "AWS", "services": [{"name": "EC2 App", "service_type": "ec2"}]}],
        "tenancy": {
            "regions": [
                {
                    "name": "Ashburn",
                    "vcns": [
                        {
                            "name": "App VCN",
                            "subnets": [
                                {"name": "App Subnet", "services": [{"name": "App VM"}]}
                            ],
                        }
                    ],
                }
            ]
        },
        "on_prem": {"name": "Primary DC", "services": [{"name": "Legacy DB"}]},
    }

    gen = OCIDiagramGenerator.from_spec(spec)
    values = [getattr(obj, "value", "") for obj in gen._objects.values()]

    assert "Users" in values
    assert "AWS" in values
    assert "Ashburn" in values
    assert "VCN App VCN" in values
    assert "App Subnet" in values
    assert "App VM" in values
    assert "Primary DC" in values
    assert "Legacy DB" in values


def test_from_spec_accepts_source_target_and_omits_unresolved_connections():
    spec = {
        "external": [{"name": "Users"}],
        "tenancy": {
            "regions": [
                {
                    "name": "Ashburn",
                    "vcns": [
                        {
                            "name": "App VCN",
                            "subnets": [
                                {"name": "App Subnet", "services": [{"name": "App VM"}]}
                            ],
                        }
                    ],
                }
            ]
        },
        "connections": [
            {"source": "Users", "target": "App VM", "type": "standard", "label": "HTTPS"},
            {"from": "Users", "to": "App VM", "type": "standard", "label": "Duplicate"},
            {"source": "Users", "target": "Missing VM", "type": "standard", "label": "Broken"},
        ],
    }

    gen = OCIDiagramGenerator.from_spec(spec)

    assert gen._connection_count == 1


def test_drawio_icon_resolution_accepts_common_native_aliases():
    gen = OCIDiagramGenerator()

    db_icon, db_key = gen._resolve_icon_entry("database_system")
    vm_icon, vm_key = gen._resolve_icon_entry("virtual_machine")
    stream_icon, stream_key = gen._resolve_icon_entry("oci_streaming")

    assert db_icon is not None
    assert db_key in {"db_system", "dbcs"}
    assert vm_icon is not None
    assert vm_key in {"compute", "vm"}
    assert stream_icon is not None
    assert stream_key in {"streaming", "kafka"}
