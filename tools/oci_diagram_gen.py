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
#
# Color palette (no #FFFFFF — use #FCFBFA near-white instead):
#   Charcoal  #312D2A   — text, connectors
#   Warm Gray #9E9892   — container borders
#   Light     #F5F4F2   — region/subnet fill
#   Medium    #E4E1DD   — AD fill
#   Near-White#FCFBFA   — background elements
#   Teal      #2D5967   — infrastructure services
#   Copper    #AA643B   — database services (NOT #AE562C)
#   Burnt-Org #AE562C   — VCN/subnet borders ONLY
#   Purple    #804998   — integration services
#   Muted     #70665E   — legacy, external actors

STYLES = {
    # --- Container styles (OCI Architecture Diagram Toolkit v24.2) ---
    "tenancy": (
        "whiteSpace=wrap;html=1;strokeWidth=1;dashed=1;dashPattern=6 4;align=left;"
        "fontFamily=Oracle Sans;verticalAlign=top;fillColor=none;"
        "fontColor=#312D2A;strokeColor=#9E9892;fontSize=13;fontStyle=1;"
        "spacingLeft=10;spacingTop=8;rounded=1;arcSize=1;"
    ),
    "region": (
        "whiteSpace=wrap;html=1;align=left;fontFamily=Oracle Sans;"
        "verticalAlign=top;fillColor=#F5F4F2;rounded=1;arcSize=5;"
        "strokeColor=#9E9892;fontColor=#312D2A;fontSize=13;fontStyle=1;"
        "spacingLeft=10;spacingTop=8;"
    ),
    "ad": (
        "whiteSpace=wrap;html=1;strokeWidth=1;align=center;"
        "fontFamily=Oracle Sans;verticalAlign=top;fillColor=#DFDCD8;"
        "fontColor=#312D2A;strokeColor=#9E9892;rounded=1;arcSize=1;"
        "fontSize=12;fontStyle=1;"
    ),
    "fault_domain": (
        "whiteSpace=wrap;html=1;strokeWidth=1;align=center;"
        "fontFamily=Oracle Sans;verticalAlign=top;fillColor=#FCFBFA;"
        "fontColor=#312D2A;strokeColor=#9E9892;rounded=1;arcSize=3;"
        "fontSize=11;"
    ),
    "vcn": (
        "whiteSpace=wrap;html=1;strokeWidth=2;dashed=1;dashPattern=4 2;align=left;"
        "fontFamily=Oracle Sans;verticalAlign=top;fillColor=none;"
        "fontColor=#aa643b;strokeColor=#aa643b;perimeterSpacing=0;"
        "fontSize=12;fontStyle=1;spacingLeft=8;spacingTop=6;"
    ),
    "subnet": (
        "whiteSpace=wrap;html=1;strokeWidth=2;dashed=1;dashPattern=4 2;align=left;"
        "fontFamily=Oracle Sans;verticalAlign=top;fillColor=none;"
        "fontColor=#aa643b;strokeColor=#aa643b;fontSize=11;fontStyle=1;"
        "spacingLeft=8;spacingTop=4;"
    ),
    "compartment": (
        "whiteSpace=wrap;html=1;strokeWidth=1;dashed=1;dashPattern=6 4;align=left;"
        "fontFamily=Oracle Sans;verticalAlign=top;fillColor=none;"
        "fontColor=#312D2A;strokeColor=#9E9892;fontSize=12;fontStyle=1;"
        "spacingLeft=5;spacingTop=5;rounded=1;arcSize=1;"
    ),
    # --- External cloud containers (AWS, Azure, GCP) ---
    # Generic / AWS: dashed muted border (Oracle style for non-Azure clouds)
    "cloud_container": (
        "whiteSpace=wrap;html=1;strokeWidth=2;dashed=1;dashPattern=6 4;align=left;"
        "fontFamily=Oracle Sans;verticalAlign=top;fillColor=none;"
        "fontColor=#70665E;strokeColor=#70665E;fontSize=12;spacingLeft=5;"
        "spacingTop=5;rounded=1;arcSize=6;"
    ),
    # Azure: solid blue border + light blue fill (matches Oracle ref arch style)
    # Source: confirmed from 4 Oracle reference architecture diagrams (exadb-dr, adb-azure, etc.)
    "azure_container": (
        "whiteSpace=wrap;html=1;strokeWidth=2;align=left;"
        "fontFamily=Oracle Sans;verticalAlign=top;fillColor=#EBF5FF;"
        "fontColor=#0050A2;strokeColor=#0078D4;fontSize=12;fontStyle=1;"
        "spacingLeft=5;spacingTop=5;rounded=1;arcSize=3;"
    ),
    # GCP: solid green border + light green fill
    "gcp_container": (
        "whiteSpace=wrap;html=1;strokeWidth=2;align=left;"
        "fontFamily=Oracle Sans;verticalAlign=top;fillColor=#E8F5E9;"
        "fontColor=#1E6B3C;strokeColor=#34A853;fontSize=12;fontStyle=1;"
        "spacingLeft=5;spacingTop=5;rounded=1;arcSize=3;"
    ),
    # Oracle Services Network: dashed gray column (right-side managed services panel)
    # Source: confirmed in hub-spoke, OKE, lakehouse Oracle reference architectures
    "oracle_services_network": (
        "whiteSpace=wrap;html=1;strokeWidth=1;dashed=1;dashPattern=6 4;align=left;"
        "fontFamily=Oracle Sans;verticalAlign=top;fillColor=none;"
        "fontColor=#312D2A;strokeColor=#9E9892;fontSize=12;fontStyle=1;"
        "spacingLeft=5;spacingTop=5;rounded=1;arcSize=1;"
    ),

    # --- Service block styles (fallback when no icon available) ---
    # OUTLINED style — Oracle reference archs never use solid-filled rectangles.
    # Fallback uses near-white fill + colored border + colored text to approximate
    # the lightweight look of OCI line-art stencil icons.
    "svc_infra": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FCFBFA;"
        "strokeColor=#2D5967;strokeWidth=1.5;fontColor=#2D5967;fontSize=11;"
        "fontFamily=Oracle Sans;arcSize=8;verticalAlign=middle;align=center;"
    ),
    "svc_database": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FCFBFA;"
        "strokeColor=#AA643B;strokeWidth=1.5;fontColor=#AA643B;fontSize=11;"
        "fontFamily=Oracle Sans;arcSize=8;verticalAlign=middle;align=center;"
    ),
    "svc_integration": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FCFBFA;"
        "strokeColor=#804998;strokeWidth=1.5;fontColor=#804998;fontSize=11;"
        "fontFamily=Oracle Sans;arcSize=8;verticalAlign=middle;align=center;"
    ),
    "svc_dormant": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FCFBFA;"
        "strokeColor=#9E9892;strokeWidth=1;fontColor=#70665E;fontSize=11;"
        "fontFamily=Oracle Sans;arcSize=8;fontStyle=2;verticalAlign=middle;align=center;"
    ),
    "svc_legacy": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FCFBFA;"
        "strokeColor=#70665E;strokeWidth=1.5;fontColor=#70665E;fontSize=11;"
        "fontFamily=Oracle Sans;arcSize=8;verticalAlign=middle;align=center;"
    ),
    "obs_bar": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#2D5967;"
        "strokeColor=none;fontColor=#FCFBFA;fontSize=10;"
        "fontFamily=Oracle Sans;arcSize=10;"
    ),

    # --- External actor: person silhouette (head circle + body arc) ---
    # Rendered as raw SVG in to_xml() post-processing, not as a drawpyo stencil.
    # This style is for the invisible connectable group + label below the icon.
    "external_user": (
        "group;fillColor=none;strokeColor=none;connectable=1;pointerEvents=1;"
    ),
    # --- External actor: cloud (internet) ---
    "external_internet": (
        "shape=mxgraph.cisco.clouds.cloud;"
        "sketch=0;fillColor=#2D5967;strokeColor=none;"
        "fontColor=#312D2A;fontSize=12;fontFamily=Oracle Sans;"
        "verticalLabelPosition=bottom;verticalAlign=top;"
        "align=center;html=1;"
    ),
    # --- External actor: generic box ---
    "external_generic": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#70665E;"
        "strokeColor=none;fontColor=#FCFBFA;fontSize=12;"
        "fontFamily=Oracle Sans;arcSize=12;verticalAlign=middle;align=center;"
    ),

    # --- Flow number badge (gray circle with white number) ---
    "flow_badge": (
        "ellipse;whiteSpace=wrap;html=1;fillColor=#2D5967;"
        "strokeColor=none;fontColor=#FCFBFA;fontSize=10;"
        "fontFamily=Oracle Sans;fontStyle=1;"
        "verticalAlign=middle;align=center;"
    ),

    # --- Title ---
    "title": (
        "text;html=1;fontSize=18;fontColor=#312D2A;"
        "fontFamily=Oracle Sans;align=center;verticalAlign=middle;fontStyle=1;"
    ),
}

# Connection style strings — used ONLY for raw XML fallback summary stats.
# Actual edge styling is done via drawpyo Edge attributes.
CONN_STYLES = {
    "conn_standard": (
        "endArrow=open;endFill=0;startArrow=none;startFill=0;html=1;"
        "strokeColor=#312D2A;strokeWidth=1;rounded=1;"
        "edgeStyle=orthogonalEdgeStyle;endSize=6;elbow=vertical;"
        "fontFamily=Oracle Sans;fontSize=10;fontColor=#312D2A;"
        "labelBackgroundColor=none;"
    ),
    "conn_db": (
        "endArrow=open;endFill=0;startArrow=none;startFill=0;html=1;"
        "strokeColor=#312D2A;strokeWidth=1;rounded=1;"
        "edgeStyle=orthogonalEdgeStyle;endSize=6;elbow=vertical;"
        "fontFamily=Oracle Sans;fontSize=10;fontColor=#312D2A;"
        "labelBackgroundColor=none;"
    ),
    "conn_adg": (
        "endArrow=open;endFill=0;startArrow=none;startFill=0;html=1;"
        "strokeColor=#312D2A;strokeWidth=1;rounded=1;"
        "edgeStyle=orthogonalEdgeStyle;endSize=6;elbow=vertical;"
        "dashed=1;dashPattern=8 4;"
        "fontFamily=Oracle Sans;fontSize=10;fontColor=#312D2A;"
        "labelBackgroundColor=none;"
    ),
    "conn_fastconnect": (
        "endArrow=open;endFill=0;startArrow=open;startFill=0;html=1;"
        "strokeColor=#312D2A;strokeWidth=1;rounded=1;"
        "edgeStyle=orthogonalEdgeStyle;endSize=6;elbow=vertical;"
        "fontFamily=Oracle Sans;fontSize=10;fontColor=#312D2A;"
        "labelBackgroundColor=none;"
    ),
    "conn_migration": (
        "endArrow=open;endFill=0;startArrow=none;startFill=0;html=1;"
        "strokeColor=#312D2A;strokeWidth=1;rounded=1;"
        "edgeStyle=orthogonalEdgeStyle;endSize=6;elbow=vertical;"
        "dashed=1;dashPattern=8 4;"
        "fontFamily=Oracle Sans;fontSize=10;fontColor=#312D2A;"
        "labelBackgroundColor=none;"
    ),
    "conn_etl": (
        "endArrow=open;endFill=0;startArrow=none;startFill=0;html=1;"
        "strokeColor=#312D2A;strokeWidth=1;rounded=1;"
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
    "cloud_guard": "svc_infra",
    "security_zone": "svc_infra",
    "vulnerability_scanning": "svc_infra",
    "object_storage": "svc_infra", "block_storage": "svc_infra",
    "file_storage": "svc_infra",
    "dns": "svc_infra", "traffic_management": "svc_infra",
    "certificates": "svc_infra", "apm": "svc_infra",
    "logging_analytics": "svc_infra",
    "os_management": "svc_infra",
    "resource_manager": "svc_infra",
    "devops": "svc_infra",
    # AI Services (teal — OCI AI service category)
    "gen_ai": "svc_infra", "generative_ai": "svc_infra",
    "language_ai": "svc_infra", "vision_ai": "svc_infra",
    "speech_ai": "svc_infra", "document_understanding": "svc_infra",
    "anomaly_detection": "svc_infra", "digital_assistant": "svc_infra",

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
    # Security services that touch data tier use database copper
    "data_safe": "svc_database",
    "vault": "svc_database",

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

# ============================================================
# AWS / GCP / AZURE ICON STYLES (mxgraph stencil libraries)
# ============================================================
# draw.io includes official cloud provider shape libraries:
#   AWS:   mxgraph.aws4.*  (orange #ED7100, dark text #232F3E)
#   GCP:   mxgraph.gcp2.*  (blue #4285F4)
#   Azure: mxgraph.azure.* (blue #0078D4)
#
# These are used when a service inside a cloud container specifies
# a cloud_icon field (e.g., cloud_icon: "aws4.ec2").

# AWS service type → (resIcon stencil path, fillColor)
AWS_ICONS = {
    "ec2":           ("mxgraph.aws4.ec2", "#ED7100"),
    "eks":           ("mxgraph.aws4.eks", "#ED7100"),
    "ecs":           ("mxgraph.aws4.ecs", "#ED7100"),
    "lambda":        ("mxgraph.aws4.lambda_function", "#ED7100"),
    "rds":           ("mxgraph.aws4.rds", "#C925D1"),
    "aurora":        ("mxgraph.aws4.aurora", "#C925D1"),
    "dynamodb":      ("mxgraph.aws4.dynamodb", "#C925D1"),
    "s3":            ("mxgraph.aws4.s3", "#3F8624"),
    "elb":           ("mxgraph.aws4.elb", "#8C4FFF"),
    "alb":           ("mxgraph.aws4.application_load_balancer", "#8C4FFF"),
    "cloudfront":    ("mxgraph.aws4.cloudfront", "#8C4FFF"),
    "vpc":           ("mxgraph.aws4.vpc", "#8C4FFF"),
    "direct_connect":("mxgraph.aws4.direct_connect", "#8C4FFF"),
    "route53":       ("mxgraph.aws4.route_53", "#8C4FFF"),
    "sqs":           ("mxgraph.aws4.sqs", "#E7157B"),
    "sns":           ("mxgraph.aws4.sns", "#E7157B"),
    "kinesis":       ("mxgraph.aws4.kinesis", "#8C4FFF"),
    "api_gateway":   ("mxgraph.aws4.api_gateway", "#E7157B"),
    "cognito":       ("mxgraph.aws4.cognito", "#DD344C"),
    "iam":           ("mxgraph.aws4.iam", "#DD344C"),
    "cloudwatch":    ("mxgraph.aws4.cloudwatch_2", "#E7157B"),
    "sagemaker":     ("mxgraph.aws4.sagemaker", "#01A88D"),
    "bedrock":       ("mxgraph.aws4.bedrock", "#01A88D"),
}

# GCP service type → (shape path, fillColor)
GCP_ICONS = {
    "gce":           ("mxgraph.gcp2.compute_engine", "#4285F4"),
    "gke":           ("mxgraph.gcp2.google_kubernetes_engine", "#4285F4"),
    "cloud_sql":     ("mxgraph.gcp2.cloud_sql", "#4285F4"),
    "bigquery":      ("mxgraph.gcp2.bigquery", "#4285F4"),
    "cloud_storage": ("mxgraph.gcp2.cloud_storage", "#4285F4"),
    "cloud_run":     ("mxgraph.gcp2.cloud_run", "#4285F4"),
    "cloud_functions":("mxgraph.gcp2.cloud_functions", "#4285F4"),
    "pub_sub":       ("mxgraph.gcp2.cloud_pubsub", "#4285F4"),
}

def _aws_icon_style(service_type: str) -> Optional[str]:
    """Return draw.io style string for an AWS service icon, or None."""
    entry = AWS_ICONS.get(service_type)
    if not entry:
        return None
    stencil, fill = entry
    return (
        f"outlineConnect=0;fontColor=#232F3E;gradientColor=none;"
        f"fillColor={fill};strokeColor=none;dashed=0;"
        f"verticalLabelPosition=bottom;verticalAlign=top;"
        f"align=center;html=1;fontSize=10;fontStyle=0;"
        f"aspect=fixed;"
        f"shape=mxgraph.aws4.resourceIcon;resIcon={stencil};"
    )

def _gcp_icon_style(service_type: str) -> Optional[str]:
    """Return draw.io style string for a GCP service icon, or None."""
    entry = GCP_ICONS.get(service_type)
    if not entry:
        return None
    stencil, fill = entry
    return (
        f"outlineConnect=0;fontColor=#232F3E;gradientColor=none;"
        f"fillColor={fill};strokeColor=none;dashed=0;"
        f"verticalLabelPosition=bottom;verticalAlign=top;"
        f"align=center;html=1;fontSize=10;fontStyle=0;"
        f"aspect=fixed;"
        f"shape={stencil};"
    )


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


def pick(mapping: dict, *keys, default=""):
    """Return the first non-empty value for any of the provided keys."""
    if not isinstance(mapping, dict):
        return default
    for key in keys:
        if key in mapping:
            value = mapping.get(key)
            if value is not None:
                return value
    return default


def pick_list(mapping: dict, *keys):
    """Return the first list-like field normalized to a list."""
    if not isinstance(mapping, dict):
        return []
    for key in keys:
        if key in mapping:
            value = mapping.get(key)
            if value is None:
                return []
            if isinstance(value, list):
                return value
            return [value]
    return []


def _slugify(value: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", str(value or "").lower()).strip("-")
    return text or "item"


class _SpecIdGenerator:
    """Generate stable unique ids within one normalized spec."""

    def __init__(self):
        self.used = set()
        self.counters = {}

    def make(self, prefix: str, seed: str = "") -> str:
        base = f"{prefix}-{_slugify(seed)}" if seed else prefix
        candidate = base
        idx = 2
        while candidate in self.used:
            candidate = f"{base}-{idx}"
            idx += 1
        self.used.add(candidate)
        return candidate


def _normalize_diagram_spec(spec: dict) -> dict:
    """Normalize aliases and synthesize ids before rendering."""
    spec = spec or {}
    id_gen = _SpecIdGenerator()
    aliases = {}

    def remember(node: dict, node_id: str):
        for key in ("id", "name", "label", "title"):
            value = node.get(key)
            if value:
                aliases[str(value)] = node_id

    def resolve_ref(value):
        if value in (None, ""):
            return None
        return aliases.get(str(value), str(value))

    def normalize_service(node: dict, prefix: str, default_type: str = "compute") -> dict:
        raw = dict(node or {})
        label = pick(raw, "label", "name", "title")
        node_id = pick(raw, "id", "name") or id_gen.make(prefix, label)
        normalized = dict(raw)
        normalized["id"] = str(node_id)
        normalized["label"] = label or str(node_id)
        normalized["type"] = pick(raw, "type", "service_type", default=default_type)
        remember(raw, normalized["id"])
        return normalized

    normalized = {
        "title": spec.get("title", ""),
        "external": [],
        "clouds": [],
        "tenancy": {},
        "connections": [],
    }

    for ext in pick_list(spec, "external"):
        normalized["external"].append(normalize_service(ext, "external"))

    for cloud in pick_list(spec, "clouds"):
        raw_cloud = dict(cloud or {})
        label = pick(raw_cloud, "label", "name", "title")
        cloud_id = pick(raw_cloud, "id", "name") or id_gen.make("cloud", label)
        normalized_cloud = dict(raw_cloud)
        normalized_cloud["id"] = str(cloud_id)
        normalized_cloud["label"] = label or str(cloud_id)
        normalized_cloud["services"] = [
            normalize_service(svc, "cloud-svc", default_type="compute")
            for svc in pick_list(raw_cloud, "services")
        ]
        remember(raw_cloud, normalized_cloud["id"])
        normalized["clouds"].append(normalized_cloud)

    tenancy_spec = dict(spec.get("tenancy", {}) or {})
    normalized_tenancy = dict(tenancy_spec)
    normalized_tenancy["label"] = pick(tenancy_spec, "label", "name", "title", default="Oracle Cloud Infrastructure")
    normalized_tenancy["regions"] = []

    for region in pick_list(tenancy_spec, "regions"):
        raw_region = dict(region or {})
        region_label = pick(raw_region, "label", "name", "title")
        region_id = pick(raw_region, "id", "name") or id_gen.make("region", region_label)
        normalized_region = dict(raw_region)
        normalized_region["id"] = str(region_id)
        normalized_region["label"] = region_label or str(region_id)
        normalized_region["availability_domains"] = []
        normalized_region["vcns"] = []
        normalized_region["compartments"] = []
        normalized_region["observability"] = pick_list(raw_region, "observability")
        remember(raw_region, normalized_region["id"])

        for ad in pick_list(raw_region, "availability_domains"):
            raw_ad = dict(ad or {})
            ad_label = pick(raw_ad, "label", "name", "title")
            ad_id = pick(raw_ad, "id", "name") or id_gen.make("ad", ad_label)
            normalized_ad = dict(raw_ad)
            normalized_ad["id"] = str(ad_id)
            normalized_ad["label"] = ad_label or str(ad_id)
            remember(raw_ad, normalized_ad["id"])
            normalized_region["availability_domains"].append(normalized_ad)

        def normalize_vcn(raw_vcn: dict) -> dict:
            vcn_label = pick(raw_vcn, "label", "name", "title")
            vcn_id = pick(raw_vcn, "id", "name") or id_gen.make("vcn", vcn_label)
            normalized_vcn = dict(raw_vcn)
            normalized_vcn["id"] = str(vcn_id)
            normalized_vcn["label"] = vcn_label or str(vcn_id)
            parent_ref = pick(raw_vcn, "parent", default="")
            if parent_ref:
                normalized_vcn["parent"] = resolve_ref(parent_ref) or str(parent_ref)
            normalized_vcn["gateways"] = [
                normalize_service(gw, "gw", default_type="drg" if pick(gw, "type", "service_type") in ("drg", "dynamic_routing_gateway") else "compute")
                for gw in pick_list(raw_vcn, "gateways")
            ]
            normalized_vcn["subnets"] = []
            remember(raw_vcn, normalized_vcn["id"])

            for subnet in pick_list(raw_vcn, "subnets"):
                raw_subnet = dict(subnet or {})
                subnet_label = pick(raw_subnet, "label", "name", "title")
                subnet_id = pick(raw_subnet, "id", "name") or id_gen.make("subnet", subnet_label)
                normalized_subnet = dict(raw_subnet)
                normalized_subnet["id"] = str(subnet_id)
                normalized_subnet["label"] = subnet_label or str(subnet_id)
                normalized_subnet["services"] = [
                    normalize_service(svc, "svc", default_type="compute")
                    for svc in pick_list(raw_subnet, "services")
                ]
                remember(raw_subnet, normalized_subnet["id"])
                normalized_vcn["subnets"].append(normalized_subnet)
            return normalized_vcn

        for vcn in pick_list(raw_region, "vcns"):
            normalized_region["vcns"].append(normalize_vcn(dict(vcn or {})))

        for comp in pick_list(raw_region, "compartments"):
            raw_comp = dict(comp or {})
            comp_label = pick(raw_comp, "label", "name", "title")
            comp_id = pick(raw_comp, "id", "name") or id_gen.make("compartment", comp_label)
            normalized_comp = dict(raw_comp)
            normalized_comp["id"] = str(comp_id)
            normalized_comp["label"] = comp_label or str(comp_id)
            normalized_comp["vcns"] = [
                normalize_vcn(dict(vcn or {}))
                for vcn in pick_list(raw_comp, "vcns")
            ]
            remember(raw_comp, normalized_comp["id"])
            normalized_region["compartments"].append(normalized_comp)

        normalized_tenancy["regions"].append(normalized_region)

    normalized["tenancy"] = normalized_tenancy

    onprem_spec = spec.get("onprem")
    if not onprem_spec:
        onprem_spec = spec.get("on_prem")
    if onprem_spec:
        raw_onprem = dict(onprem_spec or {})
        onprem_label = pick(raw_onprem, "label", "name", "title", default="On-Premises Data Center")
        normalized_onprem = dict(raw_onprem)
        normalized_onprem["id"] = pick(raw_onprem, "id", "name", default="onprem") or "onprem"
        normalized_onprem["label"] = onprem_label
        normalized_onprem["services"] = [
            normalize_service(svc, "onprem-svc", default_type="compute")
            for svc in pick_list(raw_onprem, "services")
        ]
        remember(raw_onprem, normalized_onprem["id"])
        normalized["onprem"] = normalized_onprem

    for conn in pick_list(spec, "connections"):
        raw_conn = dict(conn or {})
        source = resolve_ref(pick(raw_conn, "from", "source", default=None))
        target = resolve_ref(pick(raw_conn, "to", "target", default=None))
        if not source or not target:
            continue
        normalized_conn = dict(raw_conn)
        normalized_conn["from"] = source
        normalized_conn["to"] = target
        normalized_conn["type"] = pick(raw_conn, "type", "service_type", default="standard")
        normalized["connections"].append(normalized_conn)

    return normalized

# Unicode circled numbers for flow badges ① ② ③ ... ⑳
_CIRCLED_NUMS = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳"


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
        self._edge_objects = {}   # drawpyo edge id -> (source_id, target_id) for badge placement
        self._flow_badges = []    # list of (flow_order, edge_id) for deferred badge creation
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

    # Layout constants — calibrated from 37 Oracle Architecture Center .drawio files
    # (12,617 cells parsed: 234x 63x63 service icons, 245x 42x42 gateway icons)
    VCN_TOP_PAD = 50     # Oracle ref: VCN top to first subnet
    SUBNET_GAP = 28      # Oracle ref: subnet-to-subnet gap
    SVC_SPACING = 28     # Oracle ref: service-to-service horizontal gap
    GW_DEFAULT_H = 110   # Gateway block: ~70px icon + 2px gap + 36px label
    GW_SPACING = 20      # Gateway-to-gateway vertical gap
    MIN_ICON_W = 42      # Oracle ref: gateway icons = 42x42
    MIN_ICON_H = 42      # Oracle ref: gateway icons = 42x42
    SVC_ICON_TARGET = 63 # Oracle ref: service icons = 63x63
    GW_ICON_TARGET = 42  # Oracle ref: gateway icons = 42x42

    @classmethod
    def _calc_service_block_h(cls, label: str, service_type: str) -> int:
        """Calculate the total height a service block needs (icon + label).

        Used by both auto-sizing (pre-calculation) and rendering to ensure
        containers are always big enough for their content.
        """
        n_lines = label.count('\n') + 1
        label_h = max(n_lines * 16 + 4, 20)

        # Estimate icon height using Oracle ref targets (63px height, 45px min width)
        icon_entry = cls.ICON_CACHE.get(service_type) if cls.ICON_CACHE else None
        if icon_entry:
            iw, ih = icon_entry["w"], icon_entry["h"]
            scale = min(63 / ih, 1.0)
            if iw * scale < 45:
                scale = 45 / iw
            icon_h = int(ih * scale)
        else:
            icon_h = 63

        return icon_h + 2 + label_h  # icon + gap + label

    @classmethod
    def _calc_subnet_h(cls, subnet_spec: dict) -> int:
        """Calculate the auto-height for a subnet from its services."""
        svcs = subnet_spec.get("services", [])
        max_svc_h = 80
        for svc in svcs:
            label = svc.get("label", "").replace("\\n", "\n")
            block_h = cls._calc_service_block_h(label, svc.get("type", "compute"))
            max_svc_h = max(max_svc_h, block_h)
        return 30 + max_svc_h + 15  # top pad + content + bottom pad

    def _get_svc_style(self, service_type: str, font_size: Optional[int] = None) -> str:
        """Get the style string for a service type."""
        category = SVC_CATEGORY.get(service_type, "svc_infra")
        style = STYLES[category]
        if font_size:
            style = re.sub(r"fontSize=\d+", f"fontSize={font_size}", style)
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
        """Add an Availability Domain container (medium gray fill)."""
        self._create_object(cell_id, label, STYLES["ad"], parent, x, y, w, h)
        self._container_count += 1
        return cell_id

    def add_vcn(
        self, cell_id: str, label: str, parent: str,
        x: int = 15, y: int = 30, w: int = 1100, h: int = 600,
    ) -> str:
        """Add a VCN container (dashed burnt orange border, no fill)."""
        self._create_object(cell_id, label, STYLES["vcn"], parent, x, y, w, h)
        self._container_count += 1
        return cell_id

    def add_subnet(
        self, cell_id: str, label: str, parent: str,
        x: int = 15, y: int = 30, w: int = 280, h: int = 400,
    ) -> str:
        """Add a Subnet container (dashed orange border, no fill)."""
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

    def add_cloud(
        self, cell_id: str, label: str,
        x: int = 10, y: int = 80, w: int = 200, h: int = 300,
        provider: str = "generic",
    ) -> str:
        """Add an external cloud container (AWS, Azure, GCP).

        provider: "azure" → solid blue border (Oracle multicloud style)
                  "gcp"   → solid green border
                  "aws"   → dashed muted border (default)
                  "generic" → dashed muted border
        """
        style_map = {
            "azure": "azure_container",
            "gcp": "gcp_container",
        }
        style_key = style_map.get(provider, "cloud_container")
        self._create_object(cell_id, label, STYLES[style_key], None, x, y, w, h)
        self._container_count += 1
        return cell_id

    def add_external(
        self, cell_id: str, label: str,
        x: int = 30, y: int = 30, w: int = 50, h: int = 80,
        icon: str = "user",
    ) -> str:
        """Add an external actor with icon.

        icon: "user"     — single person silhouette (circle head + body arc) in teal
              "users"    — two person silhouettes side by side (group icon)
              "internet" — cloud stencil
              "generic"  — colored rectangle
        """
        if icon in ("user", "users"):
            # Create an invisible group for connectivity + label
            self._create_object(cell_id, "", STYLES["external_user"], None, x, y, w, h)
            group_placeholder = f"__DRAWPYO_{cell_id}__"

            if icon == "users":
                # Two person silhouettes side by side (group icon)
                # Left person (slightly behind, offset left)
                cx_l = w // 2 - 10
                self._raw_cells.append(
                    f'<mxCell id="{self._next_id()}" value="" '
                    f'style="ellipse;fillColor=none;strokeColor=#2D5967;strokeWidth=1.5;" '
                    f'vertex="1" parent="{group_placeholder}">'
                    f'<mxGeometry x="{cx_l - 8}" y="2" width="16" height="16" as="geometry"/>'
                    f'</mxCell>'
                )
                self._raw_cells.append(
                    f'<mxCell id="{self._next_id()}" value="" '
                    f'style="shape=mxgraph.basic.arc;dx=0.5;fillColor=none;'
                    f'strokeColor=#2D5967;strokeWidth=1.5;rotation=180;" '
                    f'vertex="1" parent="{group_placeholder}">'
                    f'<mxGeometry x="{cx_l - 12}" y="20" width="24" height="16" as="geometry"/>'
                    f'</mxCell>'
                )
                # Right person (foreground, offset right)
                cx_r = w // 2 + 10
                self._raw_cells.append(
                    f'<mxCell id="{self._next_id()}" value="" '
                    f'style="ellipse;fillColor=none;strokeColor=#2D5967;strokeWidth=2;" '
                    f'vertex="1" parent="{group_placeholder}">'
                    f'<mxGeometry x="{cx_r - 9}" y="0" width="18" height="18" as="geometry"/>'
                    f'</mxCell>'
                )
                self._raw_cells.append(
                    f'<mxCell id="{self._next_id()}" value="" '
                    f'style="shape=mxgraph.basic.arc;dx=0.5;fillColor=none;'
                    f'strokeColor=#2D5967;strokeWidth=2;rotation=180;" '
                    f'vertex="1" parent="{group_placeholder}">'
                    f'<mxGeometry x="{cx_r - 13}" y="20" width="26" height="18" as="geometry"/>'
                    f'</mxCell>'
                )
            else:
                # Single person silhouette
                cx = w // 2
                self._raw_cells.append(
                    f'<mxCell id="{self._next_id()}" value="" '
                    f'style="ellipse;fillColor=none;strokeColor=#2D5967;strokeWidth=2;" '
                    f'vertex="1" parent="{group_placeholder}">'
                    f'<mxGeometry x="{cx - 11}" y="0" width="22" height="22" as="geometry"/>'
                    f'</mxCell>'
                )
                self._raw_cells.append(
                    f'<mxCell id="{self._next_id()}" value="" '
                    f'style="shape=mxgraph.basic.arc;dx=0.5;fillColor=none;'
                    f'strokeColor=#2D5967;strokeWidth=2;rotation=180;" '
                    f'vertex="1" parent="{group_placeholder}">'
                    f'<mxGeometry x="{cx - 16}" y="24" width="32" height="22" as="geometry"/>'
                    f'</mxCell>'
                )

            # Label below the icon
            label_id = f"{cell_id}_label"
            label_style = (
                "text;html=1;whiteSpace=wrap;align=center;verticalAlign=top;"
                "fontFamily=Oracle Sans;fontSize=11;fontColor=#312D2A;"
                "strokeColor=none;fillColor=none;"
            )
            self._create_object(
                label_id, label, label_style, cell_id,
                -10, 48, w + 20, 20,
            )
        else:
            style_key = f"external_{icon}" if f"external_{icon}" in STYLES else "external_generic"
            self._create_object(cell_id, label, STYLES[style_key], None, x, y, w, h)
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

        Architecture:
        - The group Object (cell_id) covers ONLY the icon area — its height equals
          the scaled icon height, NOT the full service block height.  This ensures
          draw.io routes connection arrows to the icon boundary, not the label area.
        - The label is a SIBLING of the icon group (child of the same parent), placed
          immediately below the group.  It does not affect connection geometry.

        Benefit: connections from/to services visually terminate at the icon itself,
        which matches Oracle Architecture Center reference diagram style.
        """
        icon_w = icon_entry["w"]
        icon_h = icon_entry["h"]
        icon_cells = icon_entry["cells"]

        # Label height: proportional to actual line count (no over-allocation).
        # ~16px per line at 12pt Oracle Sans, minimum 20px for single-line labels.
        n_lines = label.count('\n') + 1
        label_h = max(n_lines * 16 + 4, 20)

        # ── Icon sizing: Oracle ref arch standard ──
        # Oracle reference diagrams use ~55-65px icons that are visually
        # prominent. We enforce minimum rendered width of 50px so that
        # tall/narrow icons (ExaCS, Compute, DBCS, NAT GW — 21 of 61 icons
        # have aspect ratio > 1.3) don't render as tiny slivers.
        MIN_ICON_W = 50   # minimum rendered icon WIDTH (px)
        MIN_ICON_H = 60   # minimum rendered icon HEIGHT (px)

        # For tall/narrow icons (ratio > 1.3), we need more vertical space
        # so the width doesn't shrink below MIN_ICON_W when scaling to fit.
        aspect_ratio = icon_h / icon_w if icon_w > 0 else 1
        if aspect_ratio > 1.3:
            # Need enough height so that width = icon_w * scale >= MIN_ICON_W
            # scale = MIN_ICON_W / icon_w, needed_h = icon_h * scale
            needed_h = int(icon_h * (MIN_ICON_W / icon_w))
            icon_area_h = max(h - label_h, MIN_ICON_H, needed_h)
        else:
            icon_area_h = max(h - label_h, MIN_ICON_H)

        # Scale icon to Oracle ref standard (calibrated from 37 Oracle .drawio files):
        #   Oracle uses 63x63 square icon boxes. Our OCI Library stencils are
        #   rectangular (tall), so we target 63px height and enforce minimum
        #   45px width for legibility of detailed multi-cell stencils.
        ICON_TARGET_H = 63   # Oracle ref: 63px icon box height
        ICON_MIN_W = 45      # Minimum width for legible stencils

        # Scale to fit target height
        scale = min(ICON_TARGET_H / icon_h, 1.0)
        scaled_w = icon_w * scale
        scaled_h = icon_h * scale

        # If too narrow, scale up to meet minimum width
        if scaled_w < ICON_MIN_W:
            scale = ICON_MIN_W / icon_w
            scaled_w = icon_w * scale
            scaled_h = icon_h * scale

        # Icon group dimensions = scaled icon size (not spec width).
        # This ensures edges connect TO the visible icon, not to an
        # invisible wide group. The label (sibling) uses spec width.
        icon_group_w = max(int(scaled_w) + 4, MIN_ICON_W)  # small padding
        icon_group_h = max(int(scaled_h), MIN_ICON_H)

        # Center the icon group horizontally within the spec width
        icon_group_x = x + (w - icon_group_w) // 2

        group_style = (
            "group;fillColor=none;strokeColor=none;pointerEvents=1;"
            "connectable=1;"
        )
        self._create_object(cell_id, "", group_style, parent, icon_group_x, y, icon_group_w, icon_group_h)

        # Build ID mapping: original cell id -> unique cell id
        original_ids = set()
        for cell_xml in icon_cells:
            cell_elem = ET.fromstring(cell_xml)
            original_ids.add(cell_elem.get("id"))

        id_map = {}
        for orig_id in sorted(original_ids,
                              key=lambda x_: int(x_) if x_.isdigit() else 0):
            id_map[orig_id] = f"{cell_id}_i{orig_id}"

        # Center the icon horizontally within the (now tight) group
        icon_offset_x = (icon_group_w - scaled_w) / 2

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

            # NOTE: Stencil icons are ALWAYS teal (#2D5967) per OCI visual style.
            # Copper (#AA643B) is only for fallback rectangles (no icon available).

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

        # Label is a SIBLING of the icon group (child of `parent`, not of `cell_id`).
        # This keeps connection geometry clean: arrows connect to the icon group only.
        # Oracle ref arch style: 12pt, charcoal (#312D2A), centered below icon.
        fs = font_size or 12
        label_style = (
            f"text;html=1;whiteSpace=wrap;overflow=visible;align=center;verticalAlign=top;"
            f"fontFamily=Oracle Sans;fontSize={fs};fontColor=#312D2A;"
            f"strokeColor=none;fillColor=none;spacingTop=2;"
        )
        # Label width = icon width (centered); overflow=visible handles longer text.
        label_w = w
        label_id = f"{cell_id}_label"
        self._create_object(
            label_id, label, label_style, parent,
            x, y + icon_group_h + 2, label_w, label_h,
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
    # NSG corner badge — Oracle visual signature
    # ================================================================

    # ================================================================
    # Connection methods
    # ================================================================

    def add_connection(
        self, cell_id: str, label: Optional[str], conn_type: str,
        source: str, target: str,
        waypoints: Optional[list] = None,
        flow_order: Optional[int] = None,
    ) -> str:
        """Add a connection arrow between two elements using drawpyo Edge.

        flow_order: if set (1-20), renders a teal circle badge with the number
        on the midpoint of the edge for visual storytelling.
        """
        src_obj = self._objects.get(source)
        tgt_obj = self._objects.get(target)
        if not src_obj or not tgt_obj:
            # Source or target not found — skip silently
            return cell_id

        edge = drawpyo.diagram.Edge(
            page=self.page, source=src_obj, target=tgt_obj,
            label=label or "",
        )

        # Base OCI style: open arrows, charcoal color
        # Note: orthogonal routing is set via extra_style (edgeStyle=orthogonalEdgeStyle)
        # to avoid conflicts with drawpyo's own style merging
        edge.line_end_target = "open"
        edge.line_end_source = "none"
        edge.strokeColor = "#312D2A"
        edge.strokeWidth = 1
        edge.rounded = True
        edge.endSize = 6

        # Font styling via text_format (drawpyo's supported approach)
        edge.text_format.fontFamily = "Oracle Sans"
        edge.text_format.fontSize = 10
        edge.text_format.fontColor = "#312D2A"
        edge.text_format.labelBackgroundColor = "#FFFFFF"

        # Extra style attributes that drawpyo Edge doesn't support natively.
        # - edgeStyle=orthogonalEdgeStyle: right-angle routing (no diagonal lines)
        # - jumpStyle=arc: when edges cross, show a small arc instead of overlapping
        # - labelBackgroundColor: white so labels are readable over the line
        # - NO elbow=vertical (it conflicts with orthogonal + port constraints)
        extra_style = (
            "edgeStyle=orthogonalEdgeStyle;orthogonalLoop=1;"
            "jettySize=auto;"
            "jumpStyle=arc;jumpSize=8;"
            "endFill=0;startFill=0;"
            "labelBackgroundColor=#FFFFFF;labelBorderColor=none;"
            "fontFamily=Oracle Sans;fontSize=10;fontColor=#312D2A;"
        )

        # Customize per connection type
        if conn_type == "fastconnect":
            # Bidirectional, thicker line
            edge.line_end_source = "open"
            edge.strokeWidth = 2
        elif conn_type == "network":
            # Network connections: thicker, teal color
            edge.strokeColor = "#2C5967"
            edge.strokeWidth = 2
        elif conn_type == "adg":
            # Dashed (ADG replication) — toolkit pattern: 8 4
            edge.pattern = "dashed_small"
            extra_style += "dashPattern=8 4;"
        elif conn_type == "migration":
            # Dashed (migration) — toolkit pattern: 8 4
            edge.pattern = "dashed_medium"
            extra_style += "dashPattern=8 4;"
        elif conn_type == "etl":
            # Dashed (ETL/streaming) — toolkit pattern: 6 4
            edge.pattern = "dashed_small"
            extra_style += "dashPattern=6 4;"
        elif conn_type == "internal":
            # Internal/management connections: lighter, thinner
            edge.strokeColor = "#9E9892"
            extra_style += "dashPattern=4 4;"
        # "standard", "data", and "db" use solid line defaults

        # ── Auto-port detection ──
        # Calculate exit/entry ports based on relative positions of source and
        # target. This prevents draw.io's auto-router from creating crossing
        # arrows — instead, edges exit/enter from the geometrically correct side.
        src_pos = self._abs_positions.get(source)
        tgt_pos = self._abs_positions.get(target)
        if src_pos and tgt_pos:
            src_obj_w = getattr(src_obj, 'width', 100) or 100
            src_obj_h = getattr(src_obj, 'height', 60) or 60
            # Center points
            sx = src_pos[0] + src_obj_w / 2
            sy = src_pos[1] + src_obj_h / 2
            tgt_obj_w = getattr(tgt_obj, 'width', 100) or 100
            tgt_obj_h = getattr(tgt_obj, 'height', 60) or 60
            tx = tgt_pos[0] + tgt_obj_w / 2
            ty = tgt_pos[1] + tgt_obj_h / 2

            dx = tx - sx
            dy = ty - sy

            # Determine dominant direction and set exit/entry ports.
            # Threshold: prefer vertical for diagonal connections (natural
            # top-down flow between subnets in Oracle ref arch style).
            is_horizontal = abs(dx) > abs(dy) * 1.5

            if is_horizontal:
                # Horizontal: exit right → enter left (or vice versa)
                if dx > 0:
                    extra_style += "exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;"
                else:
                    extra_style += "exitX=0;exitY=0.5;exitDx=0;exitDy=0;entryX=1;entryY=0.5;entryDx=0;entryDy=0;"
            else:
                # Vertical: exit bottom → enter top (or vice versa)
                if dy > 0:
                    extra_style += "exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;"
                else:
                    extra_style += "exitX=0.5;exitY=0;exitDx=0;exitDy=0;entryX=0.5;entryY=1;entryDx=0;entryDy=0;"

                # For vertical edges with labels, position label to the right
                # so it doesn't overlap the source/target icons
                if label:
                    extra_style += "align=left;verticalAlign=middle;"

        # Add waypoints if provided
        if waypoints:
            for wx, wy in waypoints:
                edge.add_point(wx, wy)

        # Store extra style for post-processing (keyed by drawpyo's edge id)
        self._edge_extras[str(edge.id)] = extra_style

        # Track edge endpoints for flow badge placement
        self._edge_objects[str(edge.id)] = (source, target)

        # Queue flow badge if requested
        if flow_order is not None and 1 <= flow_order <= 20:
            self._flow_badges.append((flow_order, source, target))

        self._objects[cell_id] = src_obj  # register for potential referencing
        self._connection_count += 1
        return cell_id

    # ================================================================
    # Flow badges — numbered circles on connection midpoints
    # ================================================================

    def _create_flow_badges(self):
        """Create teal circle badges with flow numbers near connection sources.

        Called after all objects and connections are registered, before save.
        Badge is positioned at 25% of the path from source (not midpoint) to
        avoid overlapping with destination icons.  A small perpendicular offset
        prevents badges from sitting on top of the arrow line itself.
        """
        badge_size = 18
        for flow_order, source_id, target_id in self._flow_badges:
            src_pos = self._abs_positions.get(source_id)
            tgt_pos = self._abs_positions.get(target_id)
            if not src_pos or not tgt_pos:
                continue

            src_obj = self._objects.get(source_id)
            tgt_obj = self._objects.get(target_id)
            if not src_obj or not tgt_obj:
                continue

            # Compute center of source and target
            src_cx = src_pos[0] + src_obj.width / 2
            src_cy = src_pos[1] + src_obj.height / 2
            tgt_cx = tgt_pos[0] + tgt_obj.width / 2
            tgt_cy = tgt_pos[1] + tgt_obj.height / 2

            # Position at 25% from source (closer to source, avoids target overlap)
            t = 0.25
            mid_x = int(src_cx + (tgt_cx - src_cx) * t - badge_size / 2)
            mid_y = int(src_cy + (tgt_cy - src_cy) * t - badge_size / 2)

            # Small perpendicular offset to avoid sitting on the arrow line
            dx = tgt_cx - src_cx
            dy = tgt_cy - src_cy
            length = max((dx**2 + dy**2) ** 0.5, 1)
            # Offset 14px perpendicular to the connection direction
            offset_x = int(-dy / length * 14)
            offset_y = int(dx / length * 14)
            mid_x += offset_x
            mid_y += offset_y

            # Use circled number character or plain number
            if flow_order <= len(_CIRCLED_NUMS):
                badge_label = str(flow_order)
            else:
                badge_label = str(flow_order)

            badge_id = f"flow_{flow_order}"
            self._create_object(
                badge_id, badge_label, STYLES["flow_badge"],
                None, mid_x, mid_y, badge_size, badge_size,
            )

    # ================================================================
    # Title
    # ================================================================

    def add_title(
        self, text: str,
        x: int = 30, y: int = 10, w: int = 800, h: int = 30,
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
        6. Sanitize: replace #ffffff with #FCFBFA (no pure white in OCI palette)
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

        # Canvas: white background so region fill (#F0EDE9) is clearly visible
        xml = re.sub(
            r'<mxGraphModel[^>]*>',
            '<mxGraphModel dx="1900" dy="1200" grid="1" gridSize="10" '
            'guides="1" tooltips="1" connect="1" arrows="1" fold="1" '
            'page="1" pageScale="1" pageWidth="1900" pageHeight="1200" '
            'background="#FFFFFF" math="0" shadow="0">',
            xml,
        )

        # Inject extra style attributes into edge cells (e.g., elbow, dashPattern)
        for edge_id, extra_style in self._edge_extras.items():
            # Find the edge cell by its drawpyo ID and append extra styles
            pattern = f'id="{edge_id}" style="'
            if pattern in xml:
                xml = xml.replace(pattern, f'id="{edge_id}" style="{extra_style}')

        # ── Edge label offset injection ──
        # Push labels away from the edge midpoint to avoid overlapping with
        # source/target icons.  Uses mxGeometry relative positioning:
        #   x: position along edge (-1=source, 0=center, 1=target)
        #   <mxPoint as="offset">: absolute pixel offset from that position
        # Horizontal edges: push label 15px above the line (offset y=-15)
        # Vertical edges: push label 15px to the right (offset x=15)
        for edge_id, (src_id, tgt_id) in self._edge_objects.items():
            src_pos = self._abs_positions.get(src_id)
            tgt_pos = self._abs_positions.get(tgt_id)
            if not src_pos or not tgt_pos:
                continue
            src_obj = self._objects.get(src_id)
            tgt_obj = self._objects.get(tgt_id)
            if not src_obj or not tgt_obj:
                continue
            sx = src_pos[0] + (getattr(src_obj, 'width', 100) or 100) / 2
            sy = src_pos[1] + (getattr(src_obj, 'height', 60) or 60) / 2
            tx = tgt_pos[0] + (getattr(tgt_obj, 'width', 100) or 100) / 2
            ty = tgt_pos[1] + (getattr(tgt_obj, 'height', 60) or 60) / 2
            dx = tx - sx
            dy = ty - sy
            dist = max((dx**2 + dy**2) ** 0.5, 1)
            # Larger offset for short connections to avoid icon overlap
            base_offset = 20 if dist < 300 else 15
            is_horiz = abs(dx) > abs(dy) * 1.5
            if is_horiz:
                offset_x, offset_y = 0, -base_offset
            else:
                offset_x, offset_y = base_offset, 0
            # Find the edge's mxGeometry and inject label offset.
            # drawpyo emits: <mxGeometry relative="1" as="geometry" />
            # We replace with expanded form containing offset point.
            new_geo = (
                f'<mxGeometry x="-0.2" y="0" relative="1" as="geometry">'
                f'<mxPoint x="{offset_x}" y="{offset_y}" as="offset" />'
                f'</mxGeometry>'
            )
            # Match both self-closing variants that drawpyo may produce
            for old_geo in [
                '<mxGeometry relative="1" as="geometry" />',
                '<mxGeometry relative="1" as="geometry"/>',
            ]:
                marker = f'id="{edge_id}"'
                if marker in xml and old_geo in xml:
                    # Only replace the mxGeometry that belongs to THIS edge
                    # Find the edge cell, then replace its geometry
                    idx = xml.find(marker)
                    if idx >= 0:
                        geo_idx = xml.find(old_geo, idx)
                        if geo_idx >= 0 and geo_idx - idx < 2000:  # sanity: within same cell
                            xml = xml[:geo_idx] + new_geo + xml[geo_idx + len(old_geo):]
                            break

        # Inject raw icon stencil cells before </root>
        if self._raw_cells:
            inject = "\n".join(f"        {c}" for c in self._raw_cells)
            xml = xml.replace("</root>", inject + "\n      </root>")

        # Replace placeholder parent references with actual drawpyo IDs
        for cell_id, obj in self._objects.items():
            placeholder = f"__DRAWPYO_{cell_id}__"
            if placeholder in xml:
                xml = xml.replace(placeholder, str(obj.id))

        # Inject container=1;collapsible=0 into container styles via XML.
        # drawpyo doesn't support 'container' as a settable property, so we
        # append it to the style string in the final XML.
        for container_marker in ["arcSize=1;", "arcSize=5;", "arcSize=3;",
                                 "perimeterSpacing=0;", "spacingTop=4;"]:
            # Only add to styles that already contain these OCI container markers
            # and don't already have container=1
            old = f'{container_marker}"'
            new = f'{container_marker}container=1;collapsible=0;"'
            xml = xml.replace(old, new)

        # Sanitize: no pure white in OCI palette
        xml = xml.replace('fill="#ffffff"', 'fill="#FCFBFA"')
        xml = xml.replace('fill="#FFFFFF"', 'fill="#FCFBFA"')
        xml = xml.replace("fillColor=#ffffff", "fillColor=#FCFBFA")
        xml = xml.replace("fillColor=#FFFFFF", "fillColor=#FCFBFA")

        # Fix drawpyo's default dash patterns to match OCI toolkit
        # drawpyo emits dashed=1 without dashPattern → draw.io defaults to 3 3
        # We ensure all dashed containers get 6 4 and dashed edges get 8 4
        # (Edge dashPatterns are already injected via _edge_extras above)

        return xml

    def save(self, filepath: str):
        """Save to a .drawio file."""
        # Create flow badges before generating XML
        # self._create_flow_badges()  # disabled — Oracle style uses dash patterns, not numbered badges
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
        spec = _normalize_diagram_spec(spec)
        gen = cls()

        # External actors (users, internet, third-party)
        for ext in spec.get("external", []):
            ext_id = ext.get("id", gen._next_id())
            gen.add_external(
                ext_id,
                ext["label"].replace("\\n", "\n"),
                x=ext.get("x", 30), y=ext.get("y", 30),
                w=ext.get("w", 50), h=ext.get("h", 60),
                icon=ext.get("icon", "user"),
            )

        # External cloud containers (AWS, Azure, GCP)
        for cloud in spec.get("clouds", []):
            cloud_id = cloud.get("id", gen._next_id())
            gen.add_cloud(
                cloud_id,
                cloud["label"].replace("\\n", "\n"),
                x=cloud.get("x", 10), y=cloud.get("y", 80),
                w=cloud.get("w", 200), h=cloud.get("h", 300),
                provider=cloud.get("provider", "generic"),
            )
            # Services inside the cloud container.
            # cy=60: enough vertical room for 2-line cloud container titles at 12pt.
            # Services are centered horizontally within the cloud container.
            cloud_w = cloud.get("w", 200)
            cy = 60
            for svc in cloud.get("services", []):
                svc_id = svc.get("id", gen._next_id())
                svc_w = svc.get("w", 100)
                svc_h = svc.get("h", 80)
                # Center each service horizontally in the cloud container
                cx = max(10, (cloud_w - svc_w) // 2)
                label = svc["label"].replace("\\n", "\n")
                cloud_icon = svc.get("cloud_icon")
                if cloud_icon:
                    # Use cloud provider icon (AWS/GCP) via stencil style
                    style = _aws_icon_style(cloud_icon) or _gcp_icon_style(cloud_icon)
                    if style:
                        gen._create_object(
                            svc_id, label, style, cloud_id,
                            cx, cy, svc_w, svc_h,
                        )
                        gen._service_count += 1
                    else:
                        gen.add_service(svc_id, label, svc.get("type", "compute"),
                                        cloud_id, cx, cy, svc_w, svc_h)
                else:
                    gen.add_service(svc_id, label, svc.get("type", "compute"),
                                    cloud_id, cx, cy, svc_w, svc_h)
                actual_h = gen._calc_service_block_h(label, svc.get("type", "compute"))
                cy += max(svc_h, actual_h) + 20

        # Tenancy — auto-size from regions if w/h not specified in spec
        tenancy_spec = spec.get("tenancy", {})
        tenancy_x = tenancy_spec.get("x", 30)
        tenancy_y = tenancy_spec.get("y", 80)

        # Pre-calculate tenancy size from region content if not explicit
        # Always pre-calculate auto-size even if spec has dimensions (use max)
        if True:
            regions = tenancy_spec.get("regions", [])
            max_region_right = 0
            max_region_bottom = 0
            region_x_cursor = 15
            for r in regions:
                # Estimate region dimensions (will be refined when regions are created)
                r_vcns = r.get("vcns", [])
                r_has_drg = any(
                    gw.get("type") in ("drg", "dynamic_routing_gateway")
                    for v in r_vcns for gw in v.get("gateways", [])
                )
                drg_w = 120 if r_has_drg else 0
                # Subnet height calc (mirrors actual rendering)
                total_sub_h = 0
                max_sub_w = 300
                for v in r_vcns:
                    for s in v.get("subnets", []):
                        auto_sh = cls._calc_subnet_h(s)
                        total_sub_h += max(s.get("h", auto_sh), auto_sh) + cls.SUBNET_GAP
                        svcs = s.get("services", [])
                        row_w = sum(sv.get("w", 150) for sv in svcs) + cls.SVC_SPACING * max(0, len(svcs) - 1) + 30
                        max_sub_w = max(max_sub_w, row_w)
                    vcn_gws = [gw for gw in v.get("gateways", [])
                               if gw.get("type") not in ("drg", "dynamic_routing_gateway")]
                    if vcn_gws:
                        max_sub_w += max(gw.get("w", 110) for gw in vcn_gws) + 20

                est_rw = max_sub_w + drg_w + 80
                est_rh = total_sub_h + 150  # 45 top + VCN_TOP_PAD(50) + bottom padding + margins

                rx_val = r.get("x", region_x_cursor)
                ry_val = r.get("y", 40)
                max_region_right = max(max_region_right, rx_val + est_rw)
                max_region_bottom = max(max_region_bottom, ry_val + est_rh)
                region_x_cursor = max_region_right + 20

            auto_tw = max(max_region_right + 30, 600)
            auto_th = max(max_region_bottom + 30, 400)
            tenancy_w = max(tenancy_spec.get("w", auto_tw), auto_tw)
            tenancy_h = max(tenancy_spec.get("h", auto_th), auto_th)

        gen.add_tenancy(
            "tenancy",
            tenancy_spec.get("label", "Oracle Cloud Infrastructure"),
            x=tenancy_x, y=tenancy_y, w=tenancy_w, h=tenancy_h,
        )

        # Regions — auto-size containers from content when spec doesn't override
        region_x_cursor = 15  # tracks right edge for auto-positioning next region
        for region in tenancy_spec.get("regions", []):
            is_primary = region.get("primary", False)
            rx = region.get("x", region_x_cursor)
            ry = region.get("y", 40)

            # ── Pre-calculate content size for auto-sizing ──
            # Walk all VCNs → subnets → services to compute minimum dimensions
            region_vcns = region.get("vcns", [])
            auto_rw, auto_rh = 640 if not is_primary else 1140, 480 if not is_primary else 670

            if region_vcns:
                # Calculate total height needed from subnets + gateways
                for vcn in region_vcns:
                    gateways = vcn.get("gateways", [])
                    # Separate DRG from VCN-internal gateways (IGW, NAT, SGW)
                    drg_gateways = [gw for gw in gateways if gw.get("type") in ("drg", "dynamic_routing_gateway")]
                    vcn_gateways = [gw for gw in gateways if gw.get("type") not in ("drg", "dynamic_routing_gateway")]

                    gw_lane_w = 0
                    if vcn_gateways:
                        gw_lane_w = max(gw.get("w", 110) for gw in vcn_gateways) + 20

                    subnets = vcn.get("subnets", [])

                    # Calculate actual subnet heights (same logic as rendering)
                    total_subnet_h = 0
                    max_svc_row_w = 0
                    for subnet in subnets:
                        auto_sh = cls._calc_subnet_h(subnet)
                        sh = max(subnet.get("h", auto_sh), auto_sh)
                        total_subnet_h += sh + cls.SUBNET_GAP

                        svcs = subnet.get("services", [])
                        row_w = sum(svc.get("w", 150) for svc in svcs) + cls.SVC_SPACING * max(0, len(svcs) - 1) + 30
                        max_svc_row_w = max(max_svc_row_w, row_w)

                    # VCN = gw_lane + content + margins
                    content_w = gw_lane_w + max(max_svc_row_w, 300) + 40
                    content_h = cls.VCN_TOP_PAD + total_subnet_h + 20

                    # Also account for gateway column height
                    if vcn_gateways:
                        total_gw_h = sum(gw.get("h", cls.GW_DEFAULT_H) for gw in vcn_gateways) + cls.GW_SPACING * max(0, len(vcn_gateways) - 1) + 64
                        content_h = max(content_h, total_gw_h)

                    # Store calculated VCN dimensions for use below
                    vcn["_auto_w"] = content_w
                    vcn["_auto_h"] = content_h
                    vcn["_drg_gateways"] = drg_gateways
                    vcn["_vcn_gateways"] = vcn_gateways

                # Region size = VCN size + margins + DRG lane
                total_vcn_w = max(v.get("_auto_w", 600) for v in region_vcns)
                total_vcn_h = max(v.get("_auto_h", 400) for v in region_vcns)
                # DRG lane on left edge of region (outside VCN)
                has_drg = any(v.get("_drg_gateways") for v in region_vcns)
                drg_lane_w = 120 if has_drg else 0
                auto_rw = total_vcn_w + drg_lane_w + 50  # margins
                auto_rh = total_vcn_h + 70  # 45 top (label) + 25 bottom

            # Always use at least auto-calculated size even if spec is smaller
            rw = max(region.get("w", auto_rw), auto_rw)
            rh = max(region.get("h", auto_rh), auto_rh)

            gen.add_region(
                region["id"],
                region["label"],
                "tenancy", rx, ry, rw, rh,
            )
            # Advance cursor for next region positioning
            region_x_cursor = rx + rw + 20

            # Availability Domains (optional)
            for ad in region.get("availability_domains", []):
                gen.add_ad(
                    ad["id"], ad["label"], region["id"],
                    x=ad.get("x", 15), y=ad.get("y", 30),
                    w=ad.get("w", rw - 30), h=ad.get("h", rh - 70),
                )

            # ── DRG placement: OUTSIDE VCN, INSIDE region ──
            # Oracle ref arch pattern: DRG sits in the region between external
            # actors and VCNs, not inside any VCN.
            has_drg = any(v.get("_drg_gateways") for v in region_vcns)
            drg_lane_w = 120 if has_drg else 0
            for vcn in region_vcns:
                for drg in vcn.get("_drg_gateways", []):
                    drg_id = drg.get("id", gen._next_id())
                    drg_w = drg.get("w", 90)
                    drg_h = drg.get("h", 60)
                    # Position: left edge of region, vertically centered
                    drg_x = 15
                    drg_y = max(45, (rh - drg_h) // 2)
                    label = drg["label"].replace("\\n", "\n")
                    gen.add_service(
                        drg_id, label, drg["type"],
                        region["id"], drg_x, drg_y, drg_w, drg_h,
                    )

            # VCNs — offset right if DRG lane present
            vcn_offset_x = drg_lane_w + 15
            for vcn in region_vcns:
                vcn_parent = vcn.get("parent", region["id"])
                auto_w = vcn.get("_auto_w", rw - vcn_offset_x - 15)
                auto_h = vcn.get("_auto_h", rh - 70)
                # Always use at least auto-calculated size even if spec is smaller
                vcn_w = max(vcn.get("w", auto_w), auto_w)
                vcn_h = max(vcn.get("h", auto_h), auto_h)
                gen.add_vcn(
                    vcn["id"],
                    f"VCN {vcn['label']}",
                    vcn_parent,
                    x=vcn.get("x", vcn_offset_x), y=vcn.get("y", 45),
                    w=vcn_w, h=vcn_h,
                )

                # ── VCN-internal gateways (IGW, NAT, SGW — NOT DRG) ──
                vcn_gateways = vcn.get("_vcn_gateways", [])
                gw_lane_w = 0

                if vcn_gateways:
                    GW_DEFAULT_W = 110
                    GW_DEFAULT_H = gen.GW_DEFAULT_H
                    GW_SPACING = gen.GW_SPACING
                    gw_lane_w = max(gw.get("w", GW_DEFAULT_W) for gw in vcn_gateways) + 20
                    total_gw_h = sum(gw.get("h", GW_DEFAULT_H) for gw in vcn_gateways) + GW_SPACING * max(0, len(vcn_gateways) - 1)
                    gw_start_y = max(32, (vcn_h - total_gw_h) // 2)
                    gy = gw_start_y
                    for gw in vcn_gateways:
                        gw_id = gw.get("id", gen._next_id())
                        gw_w = gw.get("w", GW_DEFAULT_W)
                        gw_x = gw.get("x", 10)
                        gw_y = gw.get("y", gy)
                        label = gw["label"].replace("\\n", "\n")
                        # Calculate ACTUAL rendered block height for correct stacking
                        actual_block_h = gen._calc_service_block_h(label, gw["type"])
                        gw_h = max(gw.get("h", GW_DEFAULT_H), GW_DEFAULT_H, actual_block_h)
                        gen.add_service(
                            gw_id, label, gw["type"],
                            vcn["id"], gw_x, gw_y, gw_w, gw_h,
                        )
                        # Stack using actual rendered height, not spec height
                        gy = gw_y + actual_block_h + GW_SPACING

                # Subnet offset — Oracle ref arch: 42px left indent, 50px top
                VCN_LEFT_PAD = 42 if not vcn_gateways else 8
                VCN_TOP_PAD = gen.VCN_TOP_PAD
                SUBNET_GAP = gen.SUBNET_GAP

                subnet_x = VCN_LEFT_PAD + gw_lane_w
                subnet_avail_w = vcn_w - subnet_x - 16  # 16px right margin

                # Stack subnets vertically (top-to-bottom)
                subnet_y = VCN_TOP_PAD
                SVC_SPACING = gen.SVC_SPACING
                for subnet in vcn.get("subnets", []):
                    sw = subnet.get("w", subnet_avail_w)
                    subnet_svcs = subnet.get("services", [])

                    # ── Auto-calculate subnet height from service content ──
                    # Each service = icon group (MIN 60px, grows for tall icons) + label + gap
                    # Icon group grows based on aspect ratio (see _add_service_with_icon)
                    # Use shared auto-height calculation
                    auto_sh = gen._calc_subnet_h(subnet)
                    sh = max(subnet.get("h", auto_sh), auto_sh)
                    # Calculate max service block height for layout
                    max_svc_h = auto_sh - 30 - 15  # reverse: total - top_pad - bottom_pad

                    gen.add_subnet(
                        subnet["id"], subnet["label"],
                        vcn["id"], subnet_x, subnet_y, sw, sh,
                    )

                    # Auto-layout services HORIZONTALLY within subnet, centered.
                    svc_top = 30
                    svc_widths = [svc.get("w", min(sw - 30, 150)) for svc in subnet_svcs]
                    total_svc_w = sum(svc_widths) + SVC_SPACING * max(0, len(svc_widths) - 1)
                    svc_x = max(15, (sw - total_svc_w) // 2)
                    for svc, svc_w in zip(subnet_svcs, svc_widths):
                        svc_id = svc.get("id", gen._next_id())
                        # Use auto-calculated height (ensures icons fit at MIN_ICON_H)
                        svc_h = max(svc.get("h", 80), max_svc_h)
                        label = svc["label"].replace("\\n", "\n")
                        gen.add_service(
                            svc_id, label, svc["type"],
                            subnet["id"], svc_x, svc_top, svc_w, svc_h,
                            font_size=svc.get("fontSize"),
                        )
                        svc_x += svc_w + SVC_SPACING

                    subnet_y += sh + SUBNET_GAP

            # Compartments inside region — can contain VCNs
            for comp in region.get("compartments", []):
                comp_id = comp.get("id", gen._next_id())
                comp_w = comp.get("w", rw - 20)
                comp_h = comp.get("h", 60)
                gen.add_compartment(
                    comp_id, comp["label"],
                    region["id"],
                    x=comp.get("x", 10), y=comp.get("y", rh - 80),
                    w=comp_w, h=comp_h,
                )
                # VCNs inside compartment
                for vcn in comp.get("vcns", []):
                    vcn_parent = comp_id
                    vcn_w = vcn.get("w", comp_w - 20)
                    vcn_h = vcn.get("h", comp_h - 50)
                    gen.add_vcn(
                        vcn["id"],
                        f"VCN {vcn['label']}",
                        vcn_parent,
                        x=vcn.get("x", 10), y=vcn.get("y", 45),
                        w=vcn_w, h=vcn_h,
                    )
                    subnet_y = 32
                    for subnet in vcn.get("subnets", []):
                        sw = subnet.get("w", vcn_w - 16)
                        sh = subnet.get("h", 120)
                        gen.add_subnet(
                            subnet["id"], subnet["label"],
                            vcn["id"], 8, subnet_y, sw, sh,
                        )
                        svc_top = 30
                        comp_svcs = subnet.get("services", [])
                        comp_svc_ws = [svc.get("w", min(sw - 30, 150)) for svc in comp_svcs]
                        total_csvc_w = sum(comp_svc_ws) + 12 * max(0, len(comp_svc_ws) - 1)
                        svc_x = max(15, (sw - total_csvc_w) // 2)
                        for svc, svc_w in zip(comp_svcs, comp_svc_ws):
                            svc_id = svc.get("id", gen._next_id())
                            svc_h = svc.get("h", 80)
                            label = svc["label"].replace("\\n", "\n")
                            gen.add_service(
                                svc_id, label, svc["type"],
                                subnet["id"], svc_x, svc_top, svc_w, svc_h,
                                font_size=svc.get("fontSize"),
                            )
                            svc_x += svc_w + 16
                        subnet_y += sh + 28  # Oracle ref: subnet gap
                    # Gateways on left side of compartment VCN, stacked vertically
                    gx = 10
                    gy = 40
                    for gw in vcn.get("gateways", []):
                        gw_id = gw.get("id", gen._next_id())
                        gw_w = gw.get("w", 95)
                        gw_x = gw.get("x", gx)
                        gw_y = gw.get("y", gy)
                        label = gw["label"].replace("\\n", "\n")
                        actual_h = gen._calc_service_block_h(label, gw["type"])
                        gw_h = max(gw.get("h", actual_h), actual_h)
                        gen.add_service(
                            gw_id, label, gw["type"],
                            vcn["id"], gw_x, gw_y, gw_w, gw_h,
                        )
                        gy = gw_y + actual_h + cls.GW_SPACING

            # Observability row at bottom of region — uses icons (only if explicitly requested)
            if region.get("observability"):
                obs_icon_w = 90
                obs_icon_h = 80
                ox = 20
                oy = rh - obs_icon_h - 8
                for obs_label in region["observability"]:
                    obs_id = gen._next_id()
                    obs_type = OBS_TYPE_MAP.get(obs_label.lower(), None)
                    if obs_type:
                        gen.add_service(
                            obs_id, obs_label, obs_type,
                            region["id"], ox, oy, obs_icon_w, obs_icon_h,
                            font_size=10,
                        )
                    else:
                        gen.add_obs_bar(
                            obs_id, obs_label, region["id"],
                            ox, oy + obs_icon_h - 22, 80, 22,
                        )
                    ox += obs_icon_w + 8

        # On-premises
        if spec.get("onprem"):
            op = spec["onprem"]
            op_x = op.get("x", 30)
            op_y = op.get("y", tenancy_y + tenancy_h + 20)
            op_w = op.get("w", 750)
            op_h = op.get("h", 120)
            gen.add_onprem("onprem", op.get("label", "On-Premises Data Center"),
                           x=op_x, y=op_y, w=op_w, h=op_h)
            opx = 20
            for svc in op.get("services", []):
                svc_id = svc.get("id", gen._next_id())
                svc_w = svc.get("w", 180)
                svc_h = svc.get("h", 60)
                label = svc["label"].replace("\\n", "\n")
                gen.add_service(
                    svc_id, label, svc["type"],
                    "onprem", opx, 30, svc_w, svc_h,
                )
                opx += svc_w + 12

        # Connections — merge duplicate from/to pairs (e.g., dual FastConnect)
        # into a single edge with combined label
        connections = spec.get("connections", [])
        seen_pairs = {}  # (from, to) -> index in deduped list
        deduped = []
        for conn in connections:
            pair = (conn["from"], conn["to"])
            if pair in seen_pairs:
                # Merge: combine labels
                existing = deduped[seen_pairs[pair]]
                old_label = existing.get("label", "")
                new_label = conn.get("label", "")
                if old_label and new_label and old_label != new_label:
                    existing["label"] = f"{old_label}\n+ {new_label}"
                elif new_label and not old_label:
                    existing["label"] = new_label
                # Upgrade: if either is "Dual", keep it in label
            else:
                seen_pairs[pair] = len(deduped)
                deduped.append(dict(conn))

        for conn in deduped:
            conn_id = conn.get("id", gen._next_id())
            gen.add_connection(
                conn_id, conn.get("label"), conn["type"],
                conn["from"], conn["to"],
                waypoints=conn.get("waypoints"),
                flow_order=conn.get("flow_order"),
            )

        # Title — centered across the full diagram width
        if spec.get("title"):
            total_w = tenancy_x + tenancy_w
            gen.add_title(spec["title"], x=0, y=8, w=total_w, h=35)

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
    print(f"  Flow badges: {len(gen._flow_badges)}")
    print(f"  Raw icon cells: {len(gen._raw_cells)}")
    print(f"  Registered objects: {len(gen._objects)}")


if __name__ == "__main__":
    main()
