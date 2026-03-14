#!/usr/bin/env python3
"""
OCI Architecture Diagram Generator

Generates .drawio XML files with Oracle Cloud Infrastructure visual style
matching the OCI Draw.io Toolkit v24.2.

Usage:
    # From YAML spec
    python oci_diagram_gen.py --spec examples/migration-adb-ha-dr.yaml --output architecture.drawio

    # Programmatic
    from oci_diagram_gen import OCIDiagramGenerator
    gen = OCIDiagramGenerator()
    gen.add_tenancy("tenancy", "Oracle Cloud Infrastructure")
    gen.add_region("r1", "Region — US East (Ashburn)", "tenancy")
    gen.save("architecture.drawio")
"""

import argparse
import os
import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom

try:
    import yaml
except ImportError:
    yaml = None

# --- OCI Color Palette (from OCI Toolkit v24.2) ---

COLORS = {
    "oracle_red": "#C74634",
    "text_primary": "#312D2A",
    "text_secondary": "#6B6560",
    "region_fill": "#F5F4F2",
    "region_stroke": "#B8B5B2",
    "vcn_stroke": "#AE562C",
    "subnet_stroke": "#AE562C",
    "ad_fill": "#EEEDEB",
    "fd_fill": "#E5E3E0",
}

CATEGORY_COLORS = {
    "database": {"fill": "#AA643B", "stroke": "#8A5030", "text": "#FFFFFF"},
    "compute": {"fill": "#647A4F", "stroke": "#4D6139", "text": "#FFFFFF"},
    "networking": {"fill": "#3B7393", "stroke": "#2D5A73", "text": "#FFFFFF"},
    "storage": {"fill": "#5A5A5A", "stroke": "#404040", "text": "#FFFFFF"},
    "security": {"fill": "#8B4F8B", "stroke": "#6B3D6B", "text": "#FFFFFF"},
    "integration": {"fill": "#564B9E", "stroke": "#413A7A", "text": "#FFFFFF"},
    "management": {"fill": "#3B7393", "stroke": "#2D5A73", "text": "#FFFFFF"},
}

SERVICE_CATEGORY = {
    "adb": "database",
    "adb-s": "database",
    "adb-d": "database",
    "dbcs": "database",
    "exacs": "database",
    "data-safe": "database",
    "goldengate": "database",
    "vm": "compute",
    "bm": "compute",
    "oke": "compute",
    "functions": "compute",
    "vcn": "networking",
    "lb": "networking",
    "waf": "networking",
    "drg": "networking",
    "fastconnect": "networking",
    "vpn": "networking",
    "nfw": "networking",
    "object-storage": "storage",
    "block-volume": "storage",
    "file-storage": "storage",
    "vault": "security",
    "bastion": "security",
    "cloud-guard": "security",
    "queue": "integration",
    "streaming": "integration",
    "api-gateway": "integration",
    "monitoring": "management",
    "logging": "management",
    "apm": "management",
}

CONNECTION_STYLES = {
    "default": "endArrow=block;endFill=1;strokeColor=#312D2A;strokeWidth=1;",
    "adg": "endArrow=block;endFill=1;strokeColor=#AA643B;strokeWidth=2;dashed=1;dashPattern=8 4;",
    "data-guard": "endArrow=block;endFill=1;strokeColor=#AA643B;strokeWidth=2;dashed=1;dashPattern=8 4;",
    "fastconnect": "endArrow=block;endFill=1;strokeColor=#3B7393;strokeWidth=2;",
    "vpn": "endArrow=block;endFill=1;strokeColor=#3B7393;strokeWidth=1;dashed=1;dashPattern=4 4;",
    "data-flow": "endArrow=open;endFill=0;strokeColor=#6B6560;strokeWidth=1;",
}


class OCIDiagramGenerator:
    """Generates .drawio XML files with OCI visual style."""

    def __init__(self):
        self._id_counter = 2  # 0 and 1 reserved for root and default parent
        self._cells = []
        self._connections = []

    def _next_id(self):
        """Generate the next unique cell ID."""
        cid = str(self._id_counter)
        self._id_counter += 1
        return cid

    def _add_cell(self, cell_id, value, style, parent, geometry):
        """Add a cell (container or service block) to the diagram."""
        self._cells.append({
            "id": cell_id,
            "value": value,
            "style": style,
            "parent": parent,
            "geometry": geometry,
            "vertex": True,
        })

    def add_tenancy(self, cell_id, label, parent=None):
        """Add a tenancy container."""
        style = (
            "rounded=1;whiteSpace=wrap;fillColor=#FFFFFF;"
            "strokeColor=#312D2A;strokeWidth=2;dashed=0;arcSize=8;"
            "fontFamily=Oracle Sans;fontSize=14;fontColor=#312D2A;fontStyle=1;"
            "verticalAlign=top;align=left;spacingLeft=10;spacingTop=5;"
        )
        self._add_cell(cell_id, label, style, parent or "1", {
            "x": 0, "y": 0, "width": 1200, "height": 800,
        })

    def add_region(self, cell_id, label, parent):
        """Add a region container inside a tenancy."""
        style = (
            "rounded=1;whiteSpace=wrap;fillColor=#F5F4F2;"
            "strokeColor=#B8B5B2;strokeWidth=1;dashed=0;arcSize=8;"
            "fontFamily=Oracle Sans;fontSize=12;fontColor=#312D2A;fontStyle=1;"
            "verticalAlign=top;align=left;spacingLeft=10;spacingTop=5;"
        )
        self._add_cell(cell_id, label, style, parent, {
            "x": 20, "y": 40, "width": 1160, "height": 720,
        })

    def add_vcn(self, cell_id, label, parent):
        """Add a VCN container inside a region."""
        style = (
            "rounded=0;whiteSpace=wrap;fillColor=none;"
            "strokeColor=#AE562C;strokeWidth=2;dashed=1;dashPattern=8 4;"
            "fontFamily=Oracle Sans;fontSize=11;fontColor=#AE562C;fontStyle=1;"
            "verticalAlign=top;align=left;spacingLeft=10;spacingTop=5;"
        )
        self._add_cell(cell_id, label, style, parent, {
            "x": 20, "y": 40, "width": 1120, "height": 660,
        })

    def add_subnet(self, cell_id, label, parent, x=20, y=30, width=500, height=300):
        """Add a subnet container inside a VCN."""
        style = (
            "rounded=0;whiteSpace=wrap;fillColor=none;"
            "strokeColor=#AE562C;strokeWidth=1;dashed=1;dashPattern=4 4;"
            "fontFamily=Oracle Sans;fontSize=10;fontColor=#AE562C;fontStyle=0;"
            "verticalAlign=top;align=left;spacingLeft=8;spacingTop=4;"
        )
        self._add_cell(cell_id, label, style, parent, {
            "x": x, "y": y, "width": width, "height": height,
        })

    def add_availability_domain(self, cell_id, label, parent, x=20, y=40, width=540, height=600):
        """Add an availability domain container."""
        style = (
            "rounded=1;whiteSpace=wrap;fillColor=#EEEDEB;"
            "strokeColor=#B8B5B2;strokeWidth=1;dashed=0;arcSize=4;"
            "fontFamily=Oracle Sans;fontSize=10;fontColor=#6B6560;"
            "verticalAlign=top;align=left;spacingLeft=8;spacingTop=4;"
        )
        self._add_cell(cell_id, label, style, parent, {
            "x": x, "y": y, "width": width, "height": height,
        })

    def add_fault_domain(self, cell_id, label, parent, x=10, y=30, width=160, height=550):
        """Add a fault domain container."""
        style = (
            "rounded=1;whiteSpace=wrap;fillColor=#E5E3E0;"
            "strokeColor=#B8B5B2;strokeWidth=1;dashed=1;arcSize=4;"
            "fontFamily=Oracle Sans;fontSize=9;fontColor=#6B6560;"
            "verticalAlign=top;align=left;spacingLeft=6;spacingTop=3;"
        )
        self._add_cell(cell_id, label, style, parent, {
            "x": x, "y": y, "width": width, "height": height,
        })

    def add_service(self, cell_id, label, service_type, parent, x=20, y=30, width=160, height=60):
        """Add a service block inside a container.

        Args:
            cell_id: Unique ID for this cell
            label: Display label
            service_type: Service type key (e.g., 'adb', 'vm', 'oke')
            parent: Parent container ID
            x, y: Position within parent
            width, height: Block dimensions
        """
        category = SERVICE_CATEGORY.get(service_type, "compute")
        colors = CATEGORY_COLORS.get(category, CATEGORY_COLORS["compute"])
        style = (
            f"rounded=1;whiteSpace=wrap;"
            f"fillColor={colors['fill']};strokeColor={colors['stroke']};"
            f"strokeWidth=1;arcSize=12;"
            f"fontFamily=Oracle Sans;fontSize=10;fontColor={colors['text']};"
        )
        self._add_cell(cell_id, label, style, parent, {
            "x": x, "y": y, "width": width, "height": height,
        })

    def add_connection(self, cell_id, label, conn_type, source_id, target_id):
        """Add a connection (edge) between two cells.

        Args:
            cell_id: Unique ID for this connection
            label: Connection label
            conn_type: Connection type key (e.g., 'adg', 'fastconnect', 'default')
            source_id: Source cell ID
            target_id: Target cell ID
        """
        style = CONNECTION_STYLES.get(conn_type, CONNECTION_STYLES["default"])
        style += "fontFamily=Oracle Sans;fontSize=9;fontColor=#312D2A;"
        self._connections.append({
            "id": cell_id,
            "value": label,
            "style": style,
            "source": source_id,
            "target": target_id,
        })

    def _build_xml(self):
        """Build the .drawio XML document."""
        mxfile = ET.Element("mxfile", {
            "host": "app.diagrams.net",
            "type": "device",
            "version": "24.2.0",
        })
        diagram = ET.SubElement(mxfile, "diagram", {
            "id": "oci-architecture",
            "name": "OCI Architecture",
        })
        model = ET.SubElement(diagram, "mxGraphModel", {
            "dx": "1200",
            "dy": "800",
            "grid": "1",
            "gridSize": "10",
            "guides": "1",
            "tooltips": "1",
            "connect": "1",
            "arrows": "1",
            "fold": "1",
            "page": "1",
            "pageScale": "1",
            "pageWidth": "1654",
            "pageHeight": "1169",
            "math": "0",
            "shadow": "0",
        })
        root = ET.SubElement(model, "root")

        # Root cells (required by draw.io)
        ET.SubElement(root, "mxCell", {"id": "0"})
        ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})

        # Add all cells (containers and service blocks)
        for cell in self._cells:
            attrs = {
                "id": cell["id"],
                "value": cell["value"],
                "style": cell["style"],
                "parent": cell["parent"],
                "vertex": "1",
            }
            mx_cell = ET.SubElement(root, "mxCell", attrs)
            geo = cell["geometry"]
            ET.SubElement(mx_cell, "mxGeometry", {
                "x": str(geo["x"]),
                "y": str(geo["y"]),
                "width": str(geo["width"]),
                "height": str(geo["height"]),
                "as": "geometry",
            })

        # Add all connections
        for conn in self._connections:
            attrs = {
                "id": conn["id"],
                "value": conn["value"],
                "style": conn["style"],
                "source": conn["source"],
                "target": conn["target"],
                "edge": "1",
                "parent": "1",
            }
            mx_cell = ET.SubElement(root, "mxCell", attrs)
            ET.SubElement(mx_cell, "mxGeometry", {
                "relative": "1",
                "as": "geometry",
            })

        return mxfile

    def to_xml(self):
        """Return the diagram as a formatted XML string."""
        tree = self._build_xml()
        rough = ET.tostring(tree, encoding="unicode")
        parsed = minidom.parseString(rough)
        return parsed.toprettyxml(indent="  ", encoding=None)

    def save(self, filepath):
        """Save the diagram as a .drawio file."""
        xml_str = self.to_xml()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(xml_str)
        print(f"Diagram saved to: {filepath}")

    @classmethod
    def from_spec(cls, spec):
        """Build a diagram from a YAML spec dictionary.

        Expected spec format:
            architecture:
              name: "Architecture Name"
              regions:
                - id: r1
                  label: "Region — US East (Ashburn)"
                  vcns:
                    - id: vcn1
                      label: "VCN prod-vcn 10.0.0.0/16"
                      subnets:
                        - id: sub1
                          label: "Private Subnet — Data Tier"
                          x: 20
                          y: 30
                          width: 500
                          height: 300
                          services:
                            - id: adb1
                              label: "ADB-S OLTP\\n8 OCPU / 4 TB"
                              type: adb
                              x: 25
                              y: 35
              connections:
                - id: c1
                  label: "Data Guard"
                  type: adg
                  source: sub1
                  target: sub2
        """
        gen = cls()

        arch = spec.get("architecture", spec)
        name = arch.get("name", "OCI Architecture")

        # Add tenancy
        gen.add_tenancy("tenancy", name)

        # Add regions
        for region in arch.get("regions", []):
            gen.add_region(region["id"], region["label"], "tenancy")

            for vcn in region.get("vcns", []):
                gen.add_vcn(vcn["id"], vcn["label"], region["id"])

                for subnet in vcn.get("subnets", []):
                    gen.add_subnet(
                        subnet["id"],
                        subnet["label"],
                        vcn["id"],
                        x=subnet.get("x", 20),
                        y=subnet.get("y", 30),
                        width=subnet.get("width", 500),
                        height=subnet.get("height", 300),
                    )

                    for svc in subnet.get("services", []):
                        gen.add_service(
                            svc["id"],
                            svc["label"],
                            svc.get("type", "vm"),
                            subnet["id"],
                            x=svc.get("x", 20),
                            y=svc.get("y", 30),
                            width=svc.get("width", 160),
                            height=svc.get("height", 60),
                        )

        # Add connections
        for conn in arch.get("connections", []):
            gen.add_connection(
                conn["id"],
                conn.get("label", ""),
                conn.get("type", "default"),
                conn["source"],
                conn["target"],
            )

        return gen


def load_spec(filepath):
    """Load a YAML spec file."""
    if yaml is None:
        print("ERROR: PyYAML is required. Install with: pip install pyyaml")
        sys.exit(1)
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(
        description="Generate OCI architecture diagrams (.drawio) from YAML specs"
    )
    parser.add_argument(
        "--spec",
        required=True,
        help="Path to YAML architecture specification file",
    )
    parser.add_argument(
        "--output",
        default="architecture.drawio",
        help="Output .drawio file path (default: architecture.drawio)",
    )
    args = parser.parse_args()

    if not os.path.exists(args.spec):
        print(f"ERROR: Spec file not found: {args.spec}")
        sys.exit(1)

    spec = load_spec(args.spec)
    gen = OCIDiagramGenerator.from_spec(spec)
    gen.save(args.output)


if __name__ == "__main__":
    main()
