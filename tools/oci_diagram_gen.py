#!/usr/bin/env python3
"""
OCI Architecture Diagram Generator
Produces .drawio files with Oracle official container styles.

Styles extracted from:
- OCI Library.xml — 224 official OCI service icons
- OCI Architecture Diagram Toolkit v24.2.drawio
- Reference architectures: select-ai-apex, exadb-dr-on-db-at-azure

Usage:
    python oci_diagram_gen.py --spec architecture-spec.yaml --output diagram.drawio

Or import and use programmatically:
    from oci_diagram_gen import OCIDiagramGenerator
    gen = OCIDiagramGenerator()
    gen.add_region("region1", "US East (Ashburn)", parent="tenancy", ...)
    gen.save("output.drawio")
"""

import yaml
import argparse
import sys
from typing import Optional

# ============================================================
# OCI OFFICIAL STYLES (from OCI Style Guide for Draw.io v24.2)
# ============================================================

STYLES = {
    # --- Container styles ---
    "tenancy": (
        "whiteSpace=wrap;html=1;strokeWidth=1;dashed=1;align=left;"
        "fontFamily=Oracle Sans;verticalAlign=top;fillColor=none;"
        "fontColor=#312D2A;strokeColor=#9E9892;fontSize=12;spacingLeft=5;"
        "spacingTop=5;"
    ),
    "region": (
        "whiteSpace=wrap;html=1;align=center;fontFamily=Oracle Sans;"
        "verticalAlign=top;fillColor=#F5F4F2;rounded=1;arcSize=10;"
        "strokeColor=#9E9892;fontColor=#312D2A;fontSize=12;spacingTop=5;"
    ),
    "ad": (
        "whiteSpace=wrap;html=1;strokeWidth=1;align=center;"
        "fontFamily=Oracle Sans;verticalAlign=top;fillColor=#DFDCD8;"
        "fontColor=#312D2A;strokeColor=#9E9892;rounded=1;arcSize=1;"
        "fontStyle=1;"
    ),
    "vcn": (
        "whiteSpace=wrap;html=1;strokeWidth=2;dashed=1;align=left;"
        "fontFamily=Oracle Sans;verticalAlign=top;fillColor=none;"
        "fontColor=#AE562C;strokeColor=#AE562C;perimeterSpacing=0;"
        "fontSize=12;spacingLeft=5;spacingTop=5;"
    ),
    "subnet": (
        "whiteSpace=wrap;html=1;strokeWidth=1;dashed=1;align=left;"
        "fontFamily=Oracle Sans;verticalAlign=top;fillColor=#FCFBFA;"
        "fontColor=#AE562C;strokeColor=#AE562C;fontSize=11;"
        "spacingLeft=5;spacingTop=5;rounded=1;arcSize=3;"
    ),
    "compartment": (
        "whiteSpace=wrap;html=1;strokeWidth=1;dashed=1;align=left;"
        "fontFamily=Oracle Sans;verticalAlign=top;fillColor=none;"
        "fontColor=#312D2A;strokeColor=#9E9892;fontSize=12;spacingLeft=5;"
    ),

    # --- Service block styles ---
    "svc_infra": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#2d5967;"
        "strokeColor=none;fontColor=#FFFFFF;fontSize=8;"
        "fontFamily=Oracle Sans;arcSize=8;verticalAlign=middle;align=center;"
    ),
    "svc_database": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#aa643b;"
        "strokeColor=none;fontColor=#FFFFFF;fontSize=8;"
        "fontFamily=Oracle Sans;arcSize=8;verticalAlign=middle;align=center;"
    ),
    "svc_integration": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#804998;"
        "strokeColor=none;fontColor=#FFFFFF;fontSize=8;"
        "fontFamily=Oracle Sans;arcSize=8;verticalAlign=middle;align=center;"
    ),
    "svc_dormant": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#DFDCD8;"
        "strokeColor=#9E9892;fontColor=#70665E;fontSize=8;"
        "fontFamily=Oracle Sans;arcSize=8;fontStyle=2;verticalAlign=middle;align=center;"
    ),
    "svc_legacy": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#70665E;"
        "strokeColor=none;fontColor=#FFFFFF;fontSize=8;"
        "fontFamily=Oracle Sans;arcSize=8;verticalAlign=middle;align=center;"
    ),
    "obs_bar": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#2d5967;"
        "strokeColor=none;fontColor=#FFFFFF;fontSize=7;"
        "fontFamily=Oracle Sans;arcSize=10;"
    ),

    # --- Connection styles ---
    "conn_standard": (
        "endArrow=block;endFill=1;html=1;strokeColor=#706e6f;"
        "strokeWidth=1;fontFamily=Oracle Sans;"
    ),
    "conn_db": (
        "endArrow=block;endFill=1;html=1;strokeColor=#aa643b;"
        "strokeWidth=1.5;fontSize=8;fontColor=#312D2A;fontFamily=Oracle Sans;"
    ),
    "conn_adg": (
        "endArrow=block;endFill=1;html=1;strokeColor=#AE562C;"
        "strokeWidth=2;fontSize=8;fontColor=#312D2A;"
        "fontFamily=Oracle Sans;dashed=1;dashPattern=10 6;"
    ),
    "conn_fastconnect": (
        "endArrow=block;endFill=1;startArrow=block;startFill=1;"
        "html=1;strokeColor=#804998;strokeWidth=2;fontSize=8;"
        "fontColor=#312D2A;fontFamily=Oracle Sans;"
    ),
    "conn_migration": (
        "endArrow=block;endFill=1;html=1;strokeColor=#706e6f;"
        "strokeWidth=1.5;fontSize=8;fontColor=#312D2A;"
        "fontFamily=Oracle Sans;dashed=1;dashPattern=12 6;"
    ),
    "conn_etl": (
        "endArrow=block;endFill=1;html=1;strokeColor=#804998;"
        "strokeWidth=1;fontSize=8;fontColor=#312D2A;"
        "fontFamily=Oracle Sans;dashed=1;"
    ),

    # --- Title ---
    "title": (
        "text;html=1;fontSize=10;fontColor=#70665E;"
        "fontFamily=Oracle Sans;align=right;verticalAlign=bottom;fontStyle=2;"
    ),
}

# Map service types to style categories
SVC_CATEGORY = {
    # Infrastructure (teal #2D5967)
    "compute": "svc_infra", "vm": "svc_infra", "bare_metal": "svc_infra",
    "load_balancer": "svc_infra", "flexible_lb": "svc_infra",
    "network_lb": "svc_infra",
    "igw": "svc_infra", "internet_gateway": "svc_infra",
    "nat_gateway": "svc_infra", "natgw": "svc_infra",
    "service_gateway": "svc_infra", "sgw": "svc_infra",
    "waf": "svc_infra", "bastion": "svc_infra",
    "network_firewall": "svc_infra",
    "functions": "svc_infra", "oke": "svc_infra",
    "api_gateway": "svc_infra", "apigw": "svc_infra",
    "monitoring": "svc_infra", "logging": "svc_infra",
    "db_management": "svc_infra", "ops_insights": "svc_infra",
    "notifications": "svc_infra", "events": "svc_infra",
    "cloud_guard": "svc_infra", "data_safe": "svc_infra",
    "vault": "svc_infra", "security_zone": "svc_infra",
    "vulnerability_scanning": "svc_infra",
    "object_storage": "svc_infra", "block_storage": "svc_infra",
    "file_storage": "svc_infra",
    "dns": "svc_infra", "traffic_management": "svc_infra",
    "certificates": "svc_infra", "apm": "svc_infra",
    "logging_analytics": "svc_infra",
    "os_management": "svc_infra",
    "resource_manager": "svc_infra",
    "devops": "svc_infra",

    # Database (copper #AA643B)
    "adb": "svc_database", "adb_s": "svc_database",
    "adb_d": "svc_database", "autonomous_db": "svc_database",
    "atp": "svc_database", "adw": "svc_database",
    "dbcs": "svc_database", "db_system": "svc_database",
    "exadata": "svc_database", "exacs": "svc_database",
    "nosql": "svc_database", "mysql": "svc_database",
    "mysql_heatwave": "svc_database",
    "postgresql": "svc_database", "opensearch": "svc_database",
    "cache": "svc_database", "redis": "svc_database",
    "goldengate": "svc_database",
    "data_catalog": "svc_database",

    # Integration (purple #804998)
    "drg": "svc_integration",
    "dynamic_routing_gateway": "svc_integration",
    "streaming": "svc_integration", "kafka": "svc_integration",
    "queue": "svc_integration", "oci_queue": "svc_integration",
    "oic": "svc_integration", "integration_cloud": "svc_integration",
    "fastconnect": "svc_integration",
    "service_connector_hub": "svc_integration",
    "vpn": "svc_integration",

    # Special
    "dormant": "svc_dormant",
    "standby": "svc_dormant",
    "legacy": "svc_legacy",
    "external": "svc_legacy",
}


class OCIDiagramGenerator:
    """Generate .drawio files with OCI official styles."""

    def __init__(self):
        self.cells = []
        self._id_counter = 100

    def _next_id(self) -> str:
        self._id_counter += 1
        return str(self._id_counter)

    @staticmethod
    def _escape(text: str) -> str:
        """Escape XML special characters and convert newlines."""
        if not text:
            return ""
        return (text
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("\n", "&#xa;"))

    def _make_cell(
        self,
        cell_id: str,
        value: str,
        style: str,
        parent: str,
        x: int,
        y: int,
        w: int,
        h: int,
        vertex: bool = True,
        edge: bool = False,
        source: Optional[str] = None,
        target: Optional[str] = None,
        waypoints: Optional[list] = None,
    ) -> str:
        """Create an mxCell and append it to the cells list."""
        attrs = f'id="{cell_id}" value="{self._escape(value)}" style="{style}"'
        if vertex:
            attrs += ' vertex="1"'
        if edge:
            attrs += ' edge="1"'
        if source:
            attrs += f' source="{source}"'
        if target:
            attrs += f' target="{target}"'
        attrs += f' parent="{parent}"'

        if edge and waypoints:
            geo = '<mxGeometry relative="1" as="geometry"><Array as="points">'
            for wx, wy in waypoints:
                geo += f'<mxPoint x="{wx}" y="{wy}"/>'
            geo += '</Array></mxGeometry>'
        elif edge:
            geo = '<mxGeometry relative="1" as="geometry"/>'
        else:
            geo = (
                f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" '
                f'as="geometry"/>'
            )

        cell = f'<mxCell {attrs}>{geo}</mxCell>'
        self.cells.append(cell)
        return cell_id

    def _get_svc_style(self, service_type: str, font_size: Optional[int] = None) -> str:
        """Get the style string for a service type."""
        category = SVC_CATEGORY.get(service_type, "svc_infra")
        style = STYLES[category]
        if font_size:
            style = style.replace("fontSize=8", f"fontSize={font_size}")
            style = style.replace("fontSize=9", f"fontSize={font_size}")
        return style

    # ================================================================
    # Container methods
    # ================================================================

    def add_tenancy(
        self, cell_id: str, label: str,
        x: int = 30, y: int = 80, w: int = 1850, h: int = 720,
    ) -> str:
        """Add the outermost Tenancy container (dashed gray, no fill)."""
        return self._make_cell(cell_id, label, STYLES["tenancy"], "1", x, y, w, h)

    def add_region(
        self, cell_id: str, label: str, parent: str,
        x: int = 15, y: int = 30, w: int = 1140, h: int = 670,
    ) -> str:
        """Add a Region container (solid warm gray fill, rounded)."""
        return self._make_cell(cell_id, label, STYLES["region"], parent, x, y, w, h)

    def add_ad(
        self, cell_id: str, label: str, parent: str,
        x: int = 15, y: int = 30, w: int = 1100, h: int = 640,
    ) -> str:
        """Add an Availability Domain container (darker gray fill)."""
        return self._make_cell(cell_id, label, STYLES["ad"], parent, x, y, w, h)

    def add_vcn(
        self, cell_id: str, label: str, parent: str,
        x: int = 15, y: int = 30, w: int = 1100, h: int = 600,
    ) -> str:
        """Add a VCN container (dashed burnt orange, thick, no fill)."""
        return self._make_cell(cell_id, label, STYLES["vcn"], parent, x, y, w, h)

    def add_subnet(
        self, cell_id: str, label: str, parent: str,
        x: int = 15, y: int = 30, w: int = 280, h: int = 400,
    ) -> str:
        """Add a Subnet container (dashed burnt orange, thin, near-white fill)."""
        return self._make_cell(cell_id, label, STYLES["subnet"], parent, x, y, w, h)

    def add_compartment(
        self, cell_id: str, label: str, parent: str,
        x: int = 15, y: int = 30, w: int = 400, h: int = 300,
    ) -> str:
        """Add a Compartment / Fault Domain / Tier container (dashed gray)."""
        return self._make_cell(cell_id, label, STYLES["compartment"], parent, x, y, w, h)

    def add_onprem(
        self, cell_id: str, label: str,
        x: int = 30, y: int = 850, w: int = 650, h: int = 120,
    ) -> str:
        """Add an On-Premises container (outside tenancy, dashed gray)."""
        return self._make_cell(cell_id, label, STYLES["compartment"], "1", x, y, w, h)

    def add_external(
        self, cell_id: str, label: str,
        x: int = 30, y: int = 30, w: int = 180, h: int = 60,
    ) -> str:
        """Add an external actor (users, internet, 3rd party)."""
        style = (
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#70665E;"
            "strokeColor=none;fontColor=#FFFFFF;fontSize=9;"
            "fontFamily=Oracle Sans;arcSize=12;verticalAlign=middle;align=center;"
        )
        return self._make_cell(cell_id, label, style, "1", x, y, w, h)

    # ================================================================
    # Service block methods
    # ================================================================

    def add_service(
        self, cell_id: str, label: str, service_type: str, parent: str,
        x: int = 20, y: int = 35, w: int = 150, h: int = 50,
        font_size: Optional[int] = None,
    ) -> str:
        """Add a service block with color based on category."""
        style = self._get_svc_style(service_type, font_size)
        return self._make_cell(cell_id, label, style, parent, x, y, w, h)

    def add_obs_bar(
        self, cell_id: str, label: str, parent: str,
        x: int = 20, y: int = 640, w: int = 78, h: int = 22,
    ) -> str:
        """Add an observability bar element (small teal pill)."""
        return self._make_cell(cell_id, label, STYLES["obs_bar"], parent, x, y, w, h)

    # ================================================================
    # Connection methods
    # ================================================================

    def add_connection(
        self, cell_id: str, label: Optional[str], conn_type: str,
        source: str, target: str,
        waypoints: Optional[list] = None,
    ) -> str:
        """Add a connection arrow between two elements."""
        style = STYLES.get(f"conn_{conn_type}", STYLES["conn_standard"])
        if label:
            style += "fontSize=8;fontColor=#312D2A;"
        return self._make_cell(
            cell_id, label or "", style, "1", 0, 0, 0, 0,
            vertex=False, edge=True, source=source, target=target,
            waypoints=waypoints,
        )

    # ================================================================
    # Title
    # ================================================================

    def add_title(
        self, text: str,
        x: int = 1400, y: int = 990, w: int = 470, h: int = 35,
    ) -> str:
        """Add an italic title label."""
        return self._make_cell("title", text, STYLES["title"], "1", x, y, w, h)

    # ================================================================
    # Output
    # ================================================================

    def to_xml(self) -> str:
        """Generate the complete .drawio XML."""
        header = (
            '<mxfile host="app.diagrams.net" '
            'agent="OCI Deal Accelerator" version="24.0.0" type="device">\n'
            '  <diagram name="OCI Architecture" id="oci-arch">\n'
            '    <mxGraphModel dx="1800" dy="1000" grid="1" gridSize="10" '
            'guides="1" tooltips="1" connect="1" arrows="1" fold="1" '
            'page="1" pageScale="1" pageWidth="1920" pageHeight="1100" '
            'math="0" shadow="0">\n'
            '      <root>\n'
            '        <mxCell id="0"/>\n'
            '        <mxCell id="1" parent="0"/>\n'
        )

        body = "\n".join(f"        {c}" for c in self.cells)

        footer = (
            '\n      </root>\n'
            '    </mxGraphModel>\n'
            '  </diagram>\n'
            '</mxfile>'
        )

        return header + body + footer

    def save(self, filepath: str):
        """Save to a .drawio file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_xml())

    # ================================================================
    # High-level: build from YAML spec
    # ================================================================

    @classmethod
    def from_spec(cls, spec: dict) -> "OCIDiagramGenerator":
        """Build a diagram from a YAML specification.

        The spec follows the OCI visual hierarchy:

            tenancy → region(s) → vcn(s) → subnet(s) → service(s)

        Plus optional on-premises, external actors, and connections.
        See examples/diagram-spec.yaml for the full format.
        """
        gen = cls()

        # External actors (users, internet, third-party)
        for ext in spec.get("external", []):
            ext_id = ext.get("id", gen._next_id())
            gen.add_external(
                ext_id,
                ext["label"].replace("\\n", "\n"),
                x=ext.get("x", 30), y=ext.get("y", 30),
                w=ext.get("w", 180), h=ext.get("h", 60),
            )

        # Tenancy
        tenancy_spec = spec.get("tenancy", {})
        tenancy_x = tenancy_spec.get("x", 30)
        tenancy_y = tenancy_spec.get("y", 80)
        tenancy_w = tenancy_spec.get("w", 1850)
        tenancy_h = tenancy_spec.get("h", 720)
        gen.add_tenancy(
            "tenancy",
            tenancy_spec.get("label", "Oracle Cloud Infrastructure"),
            x=tenancy_x, y=tenancy_y, w=tenancy_w, h=tenancy_h,
        )

        # Regions
        for region in tenancy_spec.get("regions", []):
            is_primary = region.get("primary", False)
            rx = region.get("x", 15 if is_primary else 1195)
            ry = region.get("y", 30)
            rw = region.get("w", 1140 if is_primary else 640)
            rh = region.get("h", 670 if is_primary else 480)

            gen.add_region(
                region["id"],
                f"Region \u2014 {region['label']}",
                "tenancy", rx, ry, rw, rh,
            )

            # Availability Domains (optional)
            for ad in region.get("availability_domains", []):
                gen.add_ad(
                    ad["id"], ad["label"], region["id"],
                    x=ad.get("x", 15), y=ad.get("y", 30),
                    w=ad.get("w", rw - 30), h=ad.get("h", rh - 70),
                )

            # VCNs
            for vcn in region.get("vcns", []):
                vcn_parent = vcn.get("parent", region["id"])
                vcn_w = vcn.get("w", rw - 30)
                vcn_h = vcn.get("h", rh - 70)
                gen.add_vcn(
                    vcn["id"],
                    f"VCN {vcn['label']}",
                    vcn_parent,
                    x=vcn.get("x", 15), y=vcn.get("y", 30),
                    w=vcn_w, h=vcn_h,
                )

                # Auto-layout subnets side by side
                sx = 15
                for subnet in vcn.get("subnets", []):
                    sw = subnet.get("w", 280)
                    sh = subnet.get("h", 420)
                    gen.add_subnet(
                        subnet["id"], subnet["label"],
                        vcn["id"], sx, 30, sw, sh,
                    )

                    # Auto-layout services vertically inside subnet
                    sy = 35
                    for svc in subnet.get("services", []):
                        svc_id = svc.get("id", gen._next_id())
                        svc_w = svc.get("w", sw - 50)
                        svc_h = svc.get("h", 45)
                        label = svc["label"].replace("\\n", "\n")
                        gen.add_service(
                            svc_id, label, svc["type"],
                            subnet["id"], 25, sy, svc_w, svc_h,
                            font_size=svc.get("fontSize"),
                        )
                        sy += svc_h + 10

                    sx += sw + 15

                # Gateways row at bottom of VCN
                gx = 20
                gy = vcn_h - 55
                for gw in vcn.get("gateways", []):
                    gw_id = gw.get("id", gen._next_id())
                    gw_w = gw.get("w", 95)
                    gw_h = gw.get("h", 38)
                    label = gw["label"].replace("\\n", "\n")
                    gen.add_service(
                        gw_id, label, gw["type"],
                        vcn["id"], gx, gy, gw_w, gw_h,
                    )
                    gx += gw_w + 10

            # Observability row at bottom of region
            if region.get("observability"):
                ox = 25
                oy = rh - 32
                for obs_label in region["observability"]:
                    obs_id = gen._next_id()
                    gen.add_obs_bar(obs_id, obs_label, region["id"], ox, oy, 80, 22)
                    ox += 88

        # On-premises
        if spec.get("onprem"):
            op = spec["onprem"]
            op_x = op.get("x", 30)
            op_y = op.get("y", tenancy_y + tenancy_h + 30)
            op_w = op.get("w", 750)
            op_h = op.get("h", 120)
            gen.add_onprem("onprem", op.get("label", "On-Premises Data Center"),
                           x=op_x, y=op_y, w=op_w, h=op_h)
            opx = 25
            for svc in op.get("services", []):
                svc_id = svc.get("id", gen._next_id())
                svc_w = svc.get("w", 180)
                svc_h = svc.get("h", 60)
                label = svc["label"].replace("\\n", "\n")
                gen.add_service(
                    svc_id, label, svc["type"],
                    "onprem", opx, 35, svc_w, svc_h,
                )
                opx += svc_w + 15

        # Connections
        for conn in spec.get("connections", []):
            conn_id = conn.get("id", gen._next_id())
            gen.add_connection(
                conn_id, conn.get("label"), conn["type"],
                conn["from"], conn["to"],
                waypoints=conn.get("waypoints"),
            )

        # Title
        if spec.get("title"):
            gen.add_title(spec["title"])

        return gen


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate OCI architecture .drawio diagrams from YAML specs"
    )
    parser.add_argument(
        "--spec", required=True,
        help="Path to YAML spec file describing the architecture",
    )
    parser.add_argument(
        "--output", default="architecture.drawio",
        help="Output .drawio file path (default: architecture.drawio)",
    )
    args = parser.parse_args()

    with open(args.spec, 'r') as f:
        spec = yaml.safe_load(f)

    gen = OCIDiagramGenerator.from_spec(spec)
    gen.save(args.output)

    # Print summary
    containers = sum(1 for c in gen.cells if 'vertex="1"' in c and
                     any(s in c for s in ['dashed=1', 'fillColor=#F5F4F2',
                                          'fillColor=#DFDCD8']))
    services = sum(1 for c in gen.cells if 'vertex="1"' in c and
                   'arcSize=8' in c)
    connections = sum(1 for c in gen.cells if 'edge="1"' in c)

    print(f"Generated: {args.output}")
    print(f"  Containers: {containers}")
    print(f"  Service blocks: {services}")
    print(f"  Connections: {connections}")
    print(f"  Total cells: {len(gen.cells)}")


if __name__ == "__main__":
    main()
