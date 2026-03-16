#!/usr/bin/env python3
"""
OCI Architecture Diagram Generator — Hybrid drawpyo + Custom Icon Injection
Produces .drawio files with Oracle official container styles and OCI Library icons.

HYBRID APPROACH:
- drawpyo handles: File, Page, Object (containers/groups), Edge (connections), save
- Custom icon extractor (kb/diagram/oci-icons.json) handles: multi-cell OCI stencil icons
  injected as raw XML into drawpyo's output

Styles extracted from:
- OCI Library.xml — 224 official OCI service icons
- OCI Architecture Diagram Toolkit v24.2.drawio
- Reference architectures: select-ai-apex, exadb-dr-on-db-at-azure

Usage:
    python3.12 oci_diagram_gen.py --spec architecture-spec.yaml --output diagram.drawio

Or import and use programmatically:
    from oci_diagram_gen import OCIDiagramGenerator
    gen = OCIDiagramGenerator()
    gen.add_region("region1", "US East (Ashburn)", parent="tenancy", ...)
    gen.save("output.drawio")
"""

import json
import os
import re
import yaml
import argparse
import sys
import xml.etree.ElementTree as ET
from typing import Optional

import drawpyo
import drawpyo.diagram

# ============================================================
# OCI OFFICIAL STYLES (from OCI Style Guide for Draw.io v24.2)
# ============================================================

STYLES = {
    # --- Container styles ---
    "tenancy": (
        "whiteSpace=wrap;html=1;strokeWidth=2;dashed=1;align=left;"
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

    # --- Service block styles (fallback when no icon available) ---
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

    # --- Title ---
    "title": (
        "text;html=1;fontSize=10;fontColor=#70665E;"
        "fontFamily=Oracle Sans;align=right;verticalAlign=bottom;fontStyle=2;"
    ),
}

# Connection style strings — used ONLY for raw XML fallback summary stats.
# Actual edge styling is done via drawpyo Edge attributes.
CONN_STYLES = {
    "conn_standard": (
        "endArrow=open;endFill=0;startArrow=none;startFill=0;html=1;"
        "strokeColor=#312D2A;strokeWidth=1;rounded=0;"
        "edgeStyle=orthogonalEdgeStyle;endSize=6;elbow=vertical;"
        "fontFamily=Oracle Sans;fontSize=10;fontColor=#312D2A;"
        "labelBackgroundColor=none;"
    ),
    "conn_db": (
        "endArrow=open;endFill=0;startArrow=none;startFill=0;html=1;"
        "strokeColor=#312D2A;strokeWidth=1;rounded=0;"
        "edgeStyle=orthogonalEdgeStyle;endSize=6;elbow=vertical;"
        "fontFamily=Oracle Sans;fontSize=10;fontColor=#312D2A;"
        "labelBackgroundColor=none;"
    ),
    "conn_adg": (
        "endArrow=open;endFill=0;startArrow=none;startFill=0;html=1;"
        "strokeColor=#312D2A;strokeWidth=1;rounded=0;"
        "edgeStyle=orthogonalEdgeStyle;endSize=6;elbow=vertical;"
        "dashed=1;dashPattern=8 4;"
        "fontFamily=Oracle Sans;fontSize=10;fontColor=#312D2A;"
        "labelBackgroundColor=none;"
    ),
    "conn_fastconnect": (
        "endArrow=open;endFill=0;startArrow=open;startFill=0;html=1;"
        "strokeColor=#312D2A;strokeWidth=1;rounded=0;"
        "edgeStyle=orthogonalEdgeStyle;endSize=6;elbow=vertical;"
        "fontFamily=Oracle Sans;fontSize=10;fontColor=#312D2A;"
        "labelBackgroundColor=none;"
    ),
    "conn_migration": (
        "endArrow=open;endFill=0;startArrow=none;startFill=0;html=1;"
        "strokeColor=#312D2A;strokeWidth=1;rounded=0;"
        "edgeStyle=orthogonalEdgeStyle;endSize=6;elbow=vertical;"
        "dashed=1;dashPattern=10 6;"
        "fontFamily=Oracle Sans;fontSize=10;fontColor=#312D2A;"
        "labelBackgroundColor=none;"
    ),
    "conn_etl": (
        "endArrow=open;endFill=0;startArrow=none;startFill=0;html=1;"
        "strokeColor=#312D2A;strokeWidth=1;rounded=0;"
        "edgeStyle=orthogonalEdgeStyle;endSize=6;elbow=vertical;"
        "dashed=1;dashPattern=6 4;"
        "fontFamily=Oracle Sans;fontSize=10;fontColor=#312D2A;"
        "labelBackgroundColor=none;"
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


# Map observability bar labels to icon service types
OBS_TYPE_MAP = {
    "monitoring": "monitoring",
    "logging": "logging",
    "logging analytics": "logging_analytics",
    "apm": "apm",
    "db management": "db_management",
    "ops insights": "ops_insights",
    "notifications": "notifications",
    "events": "events",
    "auditing": "monitoring",  # uses monitoring icon as closest match
}


class OCIDiagramGenerator:
    """Generate .drawio files using drawpyo for structure + custom icon injection.

    drawpyo handles: File, Page, Object (containers/groups), Edge (connections).
    Custom code handles: injecting multi-cell OCI stencil icons from oci-icons.json.
    """

    # Lazily loaded icon cache from kb/diagram/oci-icons.json
    ICON_CACHE = None

    @classmethod
    def _load_icon_cache(cls):
        """Load icon data from oci-icons.json if available."""
        if cls.ICON_CACHE is not None:
            return
        # Try multiple paths: relative to this script, then cwd
        candidates = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "..", "kb", "diagram", "oci-icons.json"),
            os.path.join("kb", "diagram", "oci-icons.json"),
        ]
        for path in candidates:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    cls.ICON_CACHE = json.load(f)
                return
        # Not found — fall back to empty dict (colored rectangles)
        cls.ICON_CACHE = {}

    def __init__(self):
        self._load_icon_cache()
        self.file = drawpyo.File()
        self.page = drawpyo.Page(file=self.file)
        self._objects = {}        # cell_id (str) -> drawpyo Object
        self._abs_positions = {}  # cell_id -> (abs_x, abs_y) for relative→absolute conversion
        self._raw_cells = []      # raw mxCell XML strings for icon stencil cells
        self._edge_extras = {}    # drawpyo edge id -> extra style attrs string
        self._id_counter = 1000   # counter for auto-generated cell IDs
        # Track counts for summary
        self._container_count = 0
        self._service_count = 0
        self._connection_count = 0

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

    def _get_svc_style(self, service_type: str, font_size: Optional[int] = None) -> str:
        """Get the style string for a service type."""
        category = SVC_CATEGORY.get(service_type, "svc_infra")
        style = STYLES[category]
        if font_size:
            style = style.replace("fontSize=8", f"fontSize={font_size}")
            style = style.replace("fontSize=9", f"fontSize={font_size}")
        return style

    def _create_object(
        self, cell_id: str, label: str, style_str: str,
        parent_id: Optional[str], x: int, y: int, w: int, h: int,
    ) -> "drawpyo.diagram.Object":
        """Create a drawpyo Object with OCI style, register it, and return it.

        drawpyo uses ABSOLUTE coordinates for children, but our specs use
        RELATIVE coords (relative to parent). We convert by adding the
        parent's absolute position to the child's relative offset.
        """
        parent_obj = self._objects.get(parent_id) if parent_id else None

        # Convert relative (x, y) to absolute by adding parent's absolute position
        abs_x, abs_y = x, y
        if parent_obj:
            parent_abs = self._abs_positions.get(parent_id, (0, 0))
            abs_x = parent_abs[0] + x
            abs_y = parent_abs[1] + y

        if parent_obj:
            obj = drawpyo.diagram.Object(
                page=self.page, value=label, parent=parent_obj,
            )
        else:
            obj = drawpyo.diagram.Object(page=self.page, value=label)
        obj.apply_style_string(style_str)
        obj.position = (abs_x, abs_y)
        obj.width = w
        obj.height = h
        self._objects[cell_id] = obj
        # Store the absolute position for children to reference
        self._abs_positions[cell_id] = (abs_x, abs_y)
        return obj

    # ================================================================
    # Container methods
    # ================================================================

    def add_tenancy(
        self, cell_id: str, label: str,
        x: int = 30, y: int = 80, w: int = 1850, h: int = 720,
    ) -> str:
        """Add the outermost Tenancy container (dashed gray, no fill)."""
        self._create_object(cell_id, label, STYLES["tenancy"], None, x, y, w, h)
        self._container_count += 1
        return cell_id

    def add_region(
        self, cell_id: str, label: str, parent: str,
        x: int = 15, y: int = 30, w: int = 1140, h: int = 670,
    ) -> str:
        """Add a Region container (solid warm gray fill, rounded)."""
        self._create_object(cell_id, label, STYLES["region"], parent, x, y, w, h)
        self._container_count += 1
        return cell_id

    def add_ad(
        self, cell_id: str, label: str, parent: str,
        x: int = 15, y: int = 30, w: int = 1100, h: int = 640,
    ) -> str:
        """Add an Availability Domain container (darker gray fill)."""
        self._create_object(cell_id, label, STYLES["ad"], parent, x, y, w, h)
        self._container_count += 1
        return cell_id

    def add_vcn(
        self, cell_id: str, label: str, parent: str,
        x: int = 15, y: int = 30, w: int = 1100, h: int = 600,
    ) -> str:
        """Add a VCN container (dashed burnt orange, thick, no fill)."""
        self._create_object(cell_id, label, STYLES["vcn"], parent, x, y, w, h)
        self._container_count += 1
        return cell_id

    def add_subnet(
        self, cell_id: str, label: str, parent: str,
        x: int = 15, y: int = 30, w: int = 280, h: int = 400,
    ) -> str:
        """Add a Subnet container (dashed burnt orange, thin, near-white fill)."""
        self._create_object(cell_id, label, STYLES["subnet"], parent, x, y, w, h)
        self._container_count += 1
        return cell_id

    def add_compartment(
        self, cell_id: str, label: str, parent: str,
        x: int = 15, y: int = 30, w: int = 400, h: int = 300,
    ) -> str:
        """Add a Compartment / Fault Domain / Tier container (dashed gray)."""
        self._create_object(cell_id, label, STYLES["compartment"], parent, x, y, w, h)
        self._container_count += 1
        return cell_id

    def add_onprem(
        self, cell_id: str, label: str,
        x: int = 30, y: int = 850, w: int = 650, h: int = 120,
    ) -> str:
        """Add an On-Premises container (outside tenancy, dashed gray)."""
        self._create_object(cell_id, label, STYLES["compartment"], None, x, y, w, h)
        self._container_count += 1
        return cell_id

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
        self._create_object(cell_id, label, style, None, x, y, w, h)
        return cell_id

    # ================================================================
    # Service block methods
    # ================================================================

    @staticmethod
    def _is_icon_label_cell(style: str) -> bool:
        """Detect the label cell within an OCI Library icon."""
        return ("verticalAlign=middle" in style
                and ("align=center" in style or "align=left" in style)
                and "shape=stencil(" in style
                and "fillColor=none" in style)

    def add_service(
        self, cell_id: str, label: str, service_type: str, parent: str,
        x: int = 20, y: int = 35, w: int = 150, h: int = 50,
        font_size: Optional[int] = None,
    ) -> str:
        """Add a service block with icon (if available) or colored rectangle fallback."""
        icon_entry = self.ICON_CACHE.get(service_type) if self.ICON_CACHE else None
        if icon_entry:
            return self._add_service_with_icon(
                cell_id, label, service_type, parent, icon_entry,
                x, y, w, h, font_size,
            )
        # Fallback: colored rectangle via drawpyo Object
        style = self._get_svc_style(service_type, font_size)
        self._create_object(cell_id, label, style, parent, x, y, w, h)
        self._service_count += 1
        return cell_id

    def _add_service_with_icon(
        self, cell_id: str, label: str, service_type: str, parent: str,
        icon_entry: dict,
        x: int, y: int, w: int, h: int,
        font_size: Optional[int] = None,
    ) -> str:
        """Embed official OCI icon cells inside a drawpyo group Object.

        The group Object is created via drawpyo (so edges can connect to it).
        Icon stencil cells are injected as raw XML with parent references
        remapped to the group's drawpyo-assigned ID using a placeholder.
        """
        icon_w = icon_entry["w"]
        icon_h = icon_entry["h"]
        icon_cells = icon_entry["cells"]

        # Layout: icon on top, custom label text below
        label_h = max(20, h * 0.3)
        icon_area_h = h - label_h

        # Scale icon to fit the icon area
        scale = min(w / icon_w, icon_area_h / icon_h, 1.0)
        scaled_w = icon_w * scale
        scaled_h = icon_h * scale

        # Create an invisible group Object via drawpyo (for connections)
        group_style = (
            "group;fillColor=none;strokeColor=none;pointerEvents=1;"
            "connectable=1;"
        )
        self._create_object(cell_id, "", group_style, parent, x, y, w, h)

        # Build ID mapping: original cell id -> unique cell id
        original_ids = set()
        for cell_xml in icon_cells:
            cell_elem = ET.fromstring(cell_xml)
            original_ids.add(cell_elem.get("id"))

        id_map = {}
        for orig_id in sorted(original_ids,
                              key=lambda x_: int(x_) if x_.isdigit() else 0):
            id_map[orig_id] = f"{cell_id}_i{orig_id}"

        # Center the icon horizontally within the group
        icon_offset_x = (w - scaled_w) / 2

        # Use a placeholder for the group's drawpyo ID — replaced in to_xml()
        group_placeholder = f"__DRAWPYO_{cell_id}__"

        # Emit icon cells (skip the library's built-in label cell)
        for cell_xml in icon_cells:
            cell_elem = ET.fromstring(cell_xml)
            orig_id = cell_elem.get("id")
            orig_parent = cell_elem.get("parent", "1")
            style = cell_elem.get("style", "")

            # Skip the icon's built-in label cell — we replace with our own
            if self._is_icon_label_cell(style):
                continue

            new_id = id_map[orig_id]

            # Remap parent
            if orig_parent == "1":
                new_parent = group_placeholder
            elif orig_parent in id_map:
                new_parent = id_map[orig_parent]
            else:
                new_parent = group_placeholder

            cell_elem.set("id", new_id)
            cell_elem.set("parent", new_parent)

            # Scale and offset geometry
            geo = cell_elem.find("mxGeometry")
            if geo is not None:
                for attr in ("x", "y", "width", "height"):
                    val = geo.get(attr)
                    if val is not None:
                        try:
                            geo.set(attr, str(float(val) * scale))
                        except ValueError:
                            pass
                # Offset x for centering (only top-level icon cells parented to group)
                if orig_parent == "1":
                    cur_x = float(geo.get("x", "0"))
                    geo.set("x", str(cur_x + icon_offset_x))

            cell_str = ET.tostring(cell_elem, encoding="unicode")
            self._raw_cells.append(cell_str)

        # Add our custom label below the icon as a drawpyo Object
        fs = font_size or 10
        label_style = (
            f"text;html=1;whiteSpace=wrap;overflow=fill;align=center;verticalAlign=top;"
            f"fontFamily=Oracle Sans;fontSize={fs};fontColor=#312D2A;"
            f"strokeColor=none;fillColor=none;spacingTop=2;"
        )
        label_w = max(w, 120)
        label_x = int((w - label_w) / 2)
        label_id = f"{cell_id}_label"
        self._create_object(
            label_id, label, label_style, cell_id,
            label_x, int(scaled_h + 2), int(label_w), int(label_h),
        )

        self._service_count += 1
        return cell_id

    def add_obs_bar(
        self, cell_id: str, label: str, parent: str,
        x: int = 20, y: int = 640, w: int = 78, h: int = 22,
    ) -> str:
        """Add an observability bar element (small teal pill)."""
        self._create_object(cell_id, label, STYLES["obs_bar"], parent, x, y, w, h)
        return cell_id

    # ================================================================
    # Connection methods
    # ================================================================

    def add_connection(
        self, cell_id: str, label: Optional[str], conn_type: str,
        source: str, target: str,
        waypoints: Optional[list] = None,
    ) -> str:
        """Add a connection arrow between two elements using drawpyo Edge."""
        src_obj = self._objects.get(source)
        tgt_obj = self._objects.get(target)
        if not src_obj or not tgt_obj:
            # Source or target not found — skip silently
            return cell_id

        edge = drawpyo.diagram.Edge(
            page=self.page, source=src_obj, target=tgt_obj,
            label=label or "",
        )

        # Base OCI style: open arrows, charcoal color, orthogonal routing
        edge.line_end_target = "open"
        edge.line_end_source = "none"
        edge.strokeColor = "#312D2A"
        edge.strokeWidth = 1
        edge.rounded = False
        edge.endSize = 6
        edge.waypoints = "orthogonal"

        # Font styling via text_format (drawpyo's supported approach)
        edge.text_format.fontFamily = "Oracle Sans"
        edge.text_format.fontSize = 10
        edge.text_format.fontColor = "#312D2A"
        edge.text_format.labelBackgroundColor = "none"

        # Extra style attributes that drawpyo Edge doesn't support natively.
        # These are injected via XML post-processing in to_xml().
        extra_style = "elbow=vertical;endFill=0;startFill=0;"

        # Customize per connection type
        if conn_type == "fastconnect":
            # Bidirectional
            edge.line_end_source = "open"
        elif conn_type == "adg":
            # Dashed (ADG replication)
            edge.pattern = "dashed_small"
            extra_style += "dashPattern=8 4;"
        elif conn_type == "migration":
            # Dashed (migration)
            edge.pattern = "dashed_medium"
            extra_style += "dashPattern=10 6;"
        elif conn_type == "etl":
            # Dashed (ETL/streaming)
            edge.pattern = "dashed_small"
            extra_style += "dashPattern=6 4;"
        # "standard" and "db" use solid line defaults — no changes needed

        # Add waypoints if provided
        if waypoints:
            for wx, wy in waypoints:
                edge.add_point(wx, wy)

        # Store extra style for post-processing (keyed by drawpyo's edge id)
        self._edge_extras[str(edge.id)] = extra_style

        self._objects[cell_id] = src_obj  # register for potential referencing
        self._connection_count += 1
        return cell_id

    # ================================================================
    # Title
    # ================================================================

    def add_title(
        self, text: str,
        x: int = 1400, y: int = 990, w: int = 470, h: int = 35,
    ) -> str:
        """Add an italic title label."""
        self._create_object("title", text, STYLES["title"], None, x, y, w, h)
        return "title"

    # ================================================================
    # Output — merge drawpyo XML + injected raw icon cells
    # ================================================================

    def to_xml(self) -> str:
        """Generate the complete .drawio XML.

        1. Get drawpyo's XML via file.xml property
        2. Replace drawpyo's default mxfile/diagram attributes with OCI ones
        3. Inject extra style attributes into edge cells
        4. Inject raw icon stencil cells before </root>
        5. Replace group parent placeholders with actual drawpyo IDs
        """
        xml = self.file.xml

        # Replace drawpyo's default mxfile attributes with OCI-branded ones
        xml = re.sub(
            r'<mxfile[^>]*>',
            '<mxfile host="app.diagrams.net" '
            'agent="OCI Deal Accelerator" version="24.0.0" type="device">',
            xml,
        )

        # Replace drawpyo's default diagram attributes
        xml = re.sub(
            r'<diagram[^>]*>',
            '<diagram name="OCI Architecture" id="oci-arch">',
            xml,
        )

        # Replace drawpyo's default mxGraphModel attributes with OCI page size
        xml = re.sub(
            r'<mxGraphModel[^>]*>',
            '<mxGraphModel dx="1800" dy="1000" grid="1" gridSize="10" '
            'guides="1" tooltips="1" connect="1" arrows="1" fold="1" '
            'page="1" pageScale="1" pageWidth="1920" pageHeight="1100" '
            'math="0" shadow="0">',
            xml,
        )

        # Inject extra style attributes into edge cells (e.g., elbow, dashPattern)
        for edge_id, extra_style in self._edge_extras.items():
            # Find the edge cell by its drawpyo ID and append extra styles
            pattern = f'id="{edge_id}" style="'
            if pattern in xml:
                xml = xml.replace(pattern, f'id="{edge_id}" style="{extra_style}')

        # Inject raw icon stencil cells before </root>
        if self._raw_cells:
            inject = "\n".join(f"        {c}" for c in self._raw_cells)
            xml = xml.replace("</root>", inject + "\n      </root>")

        # Replace placeholder parent references with actual drawpyo IDs
        for cell_id, obj in self._objects.items():
            placeholder = f"__DRAWPYO_{cell_id}__"
            if placeholder in xml:
                xml = xml.replace(placeholder, str(obj.id))

        return xml

    def save(self, filepath: str):
        """Save to a .drawio file."""
        xml = self.to_xml()
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(xml)

    # ================================================================
    # High-level: build from YAML spec
    # ================================================================

    @classmethod
    def from_spec(cls, spec: dict) -> "OCIDiagramGenerator":
        """Build a diagram from a YAML specification.

        The spec follows the OCI visual hierarchy:

            tenancy -> region(s) -> vcn(s) -> subnet(s) -> service(s)

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

            # Observability row at bottom of region — uses icons
            if region.get("observability"):
                obs_icon_w = 90
                obs_icon_h = 80
                ox = 25
                oy = rh - obs_icon_h - 10
                for obs_label in region["observability"]:
                    obs_id = gen._next_id()
                    obs_type = OBS_TYPE_MAP.get(obs_label.lower(), None)
                    if obs_type:
                        gen.add_service(
                            obs_id, obs_label, obs_type,
                            region["id"], ox, oy, obs_icon_w, obs_icon_h,
                            font_size=8,
                        )
                    else:
                        gen.add_obs_bar(
                            obs_id, obs_label, region["id"],
                            ox, oy + obs_icon_h - 22, 80, 22,
                        )
                    ox += obs_icon_w + 10

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
    print(f"Generated: {args.output}")
    print(f"  Containers: {gen._container_count}")
    print(f"  Service blocks: {gen._service_count}")
    print(f"  Connections: {gen._connection_count}")
    print(f"  Raw icon cells: {len(gen._raw_cells)}")
    print(f"  Registered objects: {len(gen._objects)}")


if __name__ == "__main__":
    main()
