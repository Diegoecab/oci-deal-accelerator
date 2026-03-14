#!/usr/bin/env python3
"""
OCI Architecture Diagram Generator

Generates .drawio files matching Oracle's official OCI Style Guide
for Draw.io Toolkit v24.2.

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
import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# OCI Style Guide colors
COLORS = {
    "oracle_red": "#C74634",
    "burnt_orange": "#AE562C",
    "teal": "#4F7B6E",
    "copper": "#AA643B",
    "purple": "#6B4D9A",
    "charcoal": "#312D2A",
    "light_gray": "#F5F4F2",
    "medium_gray": "#CCCCCC",
    "white": "#FFFFFF",
}

# Service category to color mapping
CATEGORY_COLORS = {
    "database": COLORS["copper"],
    "compute": COLORS["teal"],
    "networking": COLORS["teal"],
    "storage": COLORS["teal"],
    "security": COLORS["purple"],
    "integration": COLORS["purple"],
    "monitoring": COLORS["purple"],
}

# Service type to category mapping
SERVICE_CATEGORIES = {
    "adb": "database",
    "exacs": "database",
    "dbcs": "database",
    "compute": "compute",
    "oke": "compute",
    "vcn": "networking",
    "lb": "networking",
    "nlb": "networking",
    "fastconnect": "networking",
    "waf": "security",
    "bastion": "security",
    "vault": "security",
    "datasafe": "security",
    "cloudguard": "security",
    "queue": "integration",
    "streaming": "integration",
    "apigw": "integration",
    "objectstorage": "storage",
    "blockstorage": "storage",
    "filestorage": "storage",
}

# Connection type styles
CONNECTION_STYLES = {
    "adg": {
        "stroke": COLORS["copper"],
        "width": 2,
        "dash": True,
        "label": "Autonomous Data Guard",
    },
    "dg": {
        "stroke": COLORS["copper"],
        "width": 2,
        "dash": True,
        "label": "Data Guard",
    },
    "network": {
        "stroke": COLORS["teal"],
        "width": 1,
        "dash": False,
        "label": "",
    },
    "replication": {
        "stroke": COLORS["purple"],
        "width": 1,
        "dash": True,
        "label": "Replication",
    },
    "fastconnect": {
        "stroke": COLORS["teal"],
        "width": 2,
        "dash": False,
        "label": "FastConnect",
    },
    "vpn": {
        "stroke": COLORS["teal"],
        "width": 1,
        "dash": True,
        "label": "IPSec VPN",
    },
}


class OCIDiagramGenerator:
    """Generates OCI architecture diagrams in .drawio format."""

    def __init__(self):
        self._cells = []
        self._cell_id = 1
        self._id_map = {}  # user_id -> internal cell_id

    def _next_id(self):
        self._cell_id += 1
        return str(self._cell_id)

    def _register_id(self, user_id):
        internal_id = self._next_id()
        self._id_map[user_id] = internal_id
        return internal_id

    def _get_id(self, user_id):
        return self._id_map.get(user_id, "1")

    def _escape_label(self, label):
        """Escape special characters for XML."""
        return (
            label.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("\n", "&#xa;")
        )

    def add_tenancy(self, user_id, label, x=0, y=0, width=1200, height=800):
        """Add a tenancy container (outermost boundary)."""
        internal_id = self._register_id(user_id)
        style = (
            f"rounded=1;whiteSpace=wrap;html=1;fillColor={COLORS['white']};"
            f"strokeColor={COLORS['charcoal']};strokeWidth=2;"
            f"fontColor={COLORS['charcoal']};fontSize=16;"
            f"fontFamily=Oracle Sans;verticalAlign=top;align=left;"
            f"spacingLeft=10;spacingTop=5;container=1;collapsible=0;"
        )
        self._cells.append({
            "id": internal_id,
            "value": self._escape_label(label),
            "style": style,
            "parent": "1",
            "vertex": True,
            "x": x, "y": y, "width": width, "height": height,
        })

    def add_region(self, user_id, label, parent_id, x=20, y=40, width=1160, height=740):
        """Add a region container within a tenancy."""
        internal_id = self._register_id(user_id)
        parent = self._get_id(parent_id)
        style = (
            f"rounded=1;whiteSpace=wrap;html=1;fillColor={COLORS['light_gray']};"
            f"strokeColor={COLORS['charcoal']};strokeWidth=1;"
            f"fontColor={COLORS['charcoal']};fontSize=14;"
            f"fontFamily=Oracle Sans;verticalAlign=top;align=left;"
            f"spacingLeft=10;spacingTop=5;container=1;collapsible=0;"
        )
        self._cells.append({
            "id": internal_id,
            "value": self._escape_label(label),
            "style": style,
            "parent": parent,
            "vertex": True,
            "x": x, "y": y, "width": width, "height": height,
        })

    def add_vcn(self, user_id, label, parent_id, x=20, y=40, width=1100, height=680):
        """Add a VCN container (dashed burnt orange border)."""
        internal_id = self._register_id(user_id)
        parent = self._get_id(parent_id)
        style = (
            f"rounded=1;whiteSpace=wrap;html=1;fillColor=none;"
            f"strokeColor={COLORS['burnt_orange']};strokeWidth=2;dashed=1;"
            f"fontColor={COLORS['charcoal']};fontSize=12;"
            f"fontFamily=Oracle Sans;verticalAlign=top;align=left;"
            f"spacingLeft=10;spacingTop=5;container=1;collapsible=0;"
        )
        self._cells.append({
            "id": internal_id,
            "value": self._escape_label(label),
            "style": style,
            "parent": parent,
            "vertex": True,
            "x": x, "y": y, "width": width, "height": height,
        })

    def add_subnet(self, user_id, label, parent_id, x=20, y=30, width=500, height=300):
        """Add a subnet container (dashed burnt orange border, thinner)."""
        internal_id = self._register_id(user_id)
        parent = self._get_id(parent_id)
        style = (
            f"rounded=0;whiteSpace=wrap;html=1;fillColor=none;"
            f"strokeColor={COLORS['burnt_orange']};strokeWidth=1;dashed=1;"
            f"fontColor={COLORS['charcoal']};fontSize=11;"
            f"fontFamily=Oracle Sans;verticalAlign=top;align=left;"
            f"spacingLeft=10;spacingTop=5;container=1;collapsible=0;"
        )
        self._cells.append({
            "id": internal_id,
            "value": self._escape_label(label),
            "style": style,
            "parent": parent,
            "vertex": True,
            "x": x, "y": y, "width": width, "height": height,
        })

    def add_service(self, user_id, label, service_type, parent_id,
                    x=25, y=35, width=170, height=85):
        """Add a service block within a subnet or container."""
        internal_id = self._register_id(user_id)
        parent = self._get_id(parent_id)

        category = SERVICE_CATEGORIES.get(service_type, "compute")
        stroke_color = CATEGORY_COLORS.get(category, COLORS["teal"])

        style = (
            f"rounded=1;whiteSpace=wrap;html=1;fillColor={COLORS['white']};"
            f"strokeColor={stroke_color};strokeWidth=1;"
            f"fontColor={COLORS['charcoal']};fontSize=10;"
            f"fontFamily=Oracle Sans;verticalAlign=middle;align=center;"
        )
        self._cells.append({
            "id": internal_id,
            "value": self._escape_label(label),
            "style": style,
            "parent": parent,
            "vertex": True,
            "x": x, "y": y, "width": width, "height": height,
        })

    def add_connection(self, user_id, label, conn_type, source_id, target_id):
        """Add a connection (edge) between two elements."""
        internal_id = self._register_id(user_id)
        source = self._get_id(source_id)
        target = self._get_id(target_id)

        conn_style = CONNECTION_STYLES.get(conn_type, CONNECTION_STYLES["network"])
        dash_str = "1" if conn_style["dash"] else "0"
        display_label = label if label else conn_style.get("label", "")

        style = (
            f"edgeStyle=orthogonalEdgeStyle;rounded=1;"
            f"strokeColor={conn_style['stroke']};"
            f"strokeWidth={conn_style['width']};dashed={dash_str};"
            f"fontColor={COLORS['charcoal']};fontSize=9;"
            f"fontFamily=Oracle Sans;"
        )
        self._cells.append({
            "id": internal_id,
            "value": self._escape_label(display_label),
            "style": style,
            "parent": "1",
            "edge": True,
            "source": source,
            "target": target,
        })

    def add_text(self, user_id, label, parent_id="1", x=0, y=0, width=200, height=30):
        """Add a text label (not a container)."""
        internal_id = self._register_id(user_id)
        parent = self._get_id(parent_id) if parent_id != "1" else "1"
        style = (
            f"text;html=1;whiteSpace=wrap;fillColor=none;strokeColor=none;"
            f"fontColor={COLORS['charcoal']};fontSize=11;"
            f"fontFamily=Oracle Sans;verticalAlign=middle;align=center;"
        )
        self._cells.append({
            "id": internal_id,
            "value": self._escape_label(label),
            "style": style,
            "parent": parent,
            "vertex": True,
            "x": x, "y": y, "width": width, "height": height,
        })

    def build_xml(self):
        """Build the .drawio XML document."""
        mxfile = ET.Element("mxfile", {
            "host": "app.diagrams.net",
            "type": "device",
        })
        diagram = ET.SubElement(mxfile, "diagram", {
            "name": "OCI Architecture",
            "id": "oci-arch-1",
        })
        model = ET.SubElement(diagram, "mxGraphModel", {
            "dx": "1422",
            "dy": "794",
            "grid": "1",
            "gridSize": "10",
            "guides": "1",
            "tooltips": "1",
            "connect": "1",
            "arrows": "1",
            "fold": "1",
            "page": "1",
            "pageScale": "1",
            "pageWidth": "2400",
            "pageHeight": "1200",
            "math": "0",
            "shadow": "0",
        })
        root = ET.SubElement(model, "root")

        # Root cells required by draw.io
        ET.SubElement(root, "mxCell", {"id": "0"})
        ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})

        # Add all user cells
        for cell in self._cells:
            attrs = {"id": cell["id"], "value": cell["value"], "style": cell["style"]}
            attrs["parent"] = cell.get("parent", "1")

            if cell.get("vertex"):
                attrs["vertex"] = "1"
            if cell.get("edge"):
                attrs["edge"] = "1"
                if "source" in cell:
                    attrs["source"] = cell["source"]
                if "target" in cell:
                    attrs["target"] = cell["target"]

            mx_cell = ET.SubElement(root, "mxCell", attrs)

            if cell.get("vertex") and not cell.get("edge"):
                ET.SubElement(mx_cell, "mxGeometry", {
                    "x": str(cell.get("x", 0)),
                    "y": str(cell.get("y", 0)),
                    "width": str(cell.get("width", 170)),
                    "height": str(cell.get("height", 85)),
                    "as": "geometry",
                })

        return mxfile

    def to_xml_string(self):
        """Return the .drawio XML as a formatted string."""
        tree = self.build_xml()
        rough_string = ET.tostring(tree, encoding="unicode")
        dom = minidom.parseString(rough_string)
        return dom.toprettyxml(indent="  ", encoding=None)

    def save(self, filepath):
        """Save the diagram to a .drawio file."""
        xml_string = self.to_xml_string()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(xml_string)
        print(f"Diagram saved to {filepath}")


def load_from_yaml(spec_path):
    """Load a diagram spec from YAML and generate the diagram."""
    if not HAS_YAML:
        print("Error: PyYAML is required. Install with: pip install pyyaml")
        sys.exit(1)

    with open(spec_path, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)

    gen = OCIDiagramGenerator()

    tenancy = spec.get("tenancy", {})
    tenancy_name = tenancy.get("name", "Oracle Cloud Infrastructure")
    gen.add_tenancy("tenancy", tenancy_name,
                    width=tenancy.get("width", 2200),
                    height=tenancy.get("height", 1000))

    for region in tenancy.get("regions", []):
        region_id = region["id"]
        gen.add_region(region_id, region["name"], "tenancy",
                       x=region.get("x", 20), y=region.get("y", 40),
                       width=region.get("width", 1060),
                       height=region.get("height", 940))

        for vcn in region.get("vcns", []):
            vcn_id = vcn["id"]
            gen.add_vcn(vcn_id, vcn["name"], region_id,
                        x=vcn.get("x", 20), y=vcn.get("y", 40),
                        width=vcn.get("width", 1000),
                        height=vcn.get("height", 880))

            for subnet in vcn.get("subnets", []):
                subnet_id = subnet["id"]
                gen.add_subnet(subnet_id, subnet["name"], vcn_id,
                               x=subnet.get("x", 20), y=subnet.get("y", 30),
                               width=subnet.get("width", 460),
                               height=subnet.get("height", 200))

                for svc in subnet.get("services", []):
                    gen.add_service(
                        svc["id"], svc["name"], svc.get("type", "compute"),
                        subnet_id,
                        x=svc.get("x", 25), y=svc.get("y", 35),
                        width=svc.get("width", 170),
                        height=svc.get("height", 85),
                    )

    for conn in spec.get("connections", []):
        gen.add_connection(
            conn["id"],
            conn.get("label", ""),
            conn.get("type", "network"),
            conn["source"],
            conn["target"],
        )

    return gen


def main():
    parser = argparse.ArgumentParser(
        description="Generate OCI architecture diagrams in .drawio format"
    )
    parser.add_argument(
        "--spec", required=True,
        help="Path to YAML spec file"
    )
    parser.add_argument(
        "--output", default="architecture.drawio",
        help="Output .drawio file path (default: architecture.drawio)"
    )
    args = parser.parse_args()

    gen = load_from_yaml(args.spec)
    gen.save(args.output)


if __name__ == "__main__":
    main()
