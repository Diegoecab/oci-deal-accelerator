#!/usr/bin/env python3
"""
OCI Icon Extractor

Reads the OCI Library.xml (draw.io library), decodes each icon's embedded XML,
and saves a JSON mapping file (oci-icons.json) for use by oci_diagram_gen.py.

Usage:
    python3 tools/oci_icon_extractor.py

Output:
    kb/diagram/oci-icons.json
"""

import json
import re
import base64
import zlib
import urllib.parse
import os
import sys
import xml.etree.ElementTree as ET
from typing import List


# Map from library index to (list of service_type keys)
# The index corresponds to the icon's position in the OCI Library.xml JSON array.
ICON_KEY_MAP = {
    3: ["vm", "compute"],
    2: ["functions"],
    5: ["flex_vm"],
    7: ["block_storage"],
    10: ["file_storage"],
    11: ["object_storage"],
    17: ["vcn_icon"],
    18: ["load_balancer"],
    19: ["flexible_lb"],
    30: ["drg", "dynamic_routing_gateway"],
    31: ["sgw", "service_gateway"],
    32: ["igw", "internet_gateway"],
    33: ["natgw", "nat_gateway"],
    36: ["dbcs", "db_system"],
    37: ["autonomous_db", "adb", "adb_s", "atp", "adw"],
    38: ["adb_d"],
    43: ["exadata", "exacs"],
    45: ["data_safe"],
    46: ["nosql"],
    47: ["mysql"],
    49: ["opensearch"],
    51: ["goldengate"],
    65: ["streaming", "kafka"],
    66: ["service_connector_hub"],
    74: ["oke"],
    77: ["apex"],
    79: ["apigw", "api_gateway"],
    82: ["notifications"],
    97: ["cloud_guard"],
    101: ["network_firewall"],
    102: ["waf"],
    105: ["vault"],
    106: ["bastion"],
    114: ["nsg"],
    116: ["apm"],
    117: ["logging"],
    120: ["monitoring"],
    123: ["logging_analytics"],
    124: ["events"],
    125: ["ops_insights"],
    127: ["queue", "oci_queue"],
    158: ["db_management"],
}


def decode_icon_xml(xml_encoded: str) -> str:
    """Decode a draw.io library icon's XML: base64 -> zlib decompress -> URL decode."""
    decoded = base64.b64decode(xml_encoded)
    decompressed = zlib.decompress(decoded, -15)
    return urllib.parse.unquote(decompressed.decode("utf-8"))


def extract_icon_cells(xml_str: str) -> List[str]:
    """Extract mxCell elements from decoded icon XML, excluding root cells 0 and 1."""
    root = ET.fromstring(xml_str)
    cells = root.findall(".//mxCell")
    result = []
    for cell in cells:
        cell_id = cell.get("id", "")
        if cell_id in ("0", "1"):
            continue
        result.append(ET.tostring(cell, encoding="unicode"))
    return result


def main():
    # Resolve paths relative to project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    library_path = os.path.join(project_root, "kb", "diagram", "OCI Library.xml")
    output_path = os.path.join(project_root, "kb", "diagram", "oci-icons.json")

    if not os.path.exists(library_path):
        print(f"Error: OCI Library.xml not found at {library_path}", file=sys.stderr)
        sys.exit(1)

    with open(library_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Parse JSON array from <mxlibrary>...</mxlibrary>
    m = re.search(r"<mxlibrary>(.*?)</mxlibrary>", content, re.DOTALL)
    if not m:
        print("Error: Could not find <mxlibrary> tags in OCI Library.xml", file=sys.stderr)
        sys.exit(1)

    icons = json.loads(m.group(1))
    print(f"Loaded {len(icons)} icons from OCI Library.xml")

    # Build the output mapping
    icon_data = {}
    processed = 0

    for idx, keys in ICON_KEY_MAP.items():
        if idx >= len(icons):
            print(f"  Warning: index {idx} out of range (max {len(icons) - 1}), skipping")
            continue

        icon = icons[idx]
        title = icon.get("title", f"Icon_{idx}")
        w = icon.get("w", 84)
        h = icon.get("h", 109)

        # Decode the XML
        try:
            xml_str = decode_icon_xml(icon["xml"])
            cells = extract_icon_cells(xml_str)
        except Exception as e:
            print(f"  Warning: failed to decode icon [{idx}] {title}: {e}")
            continue

        entry = {
            "title": title,
            "w": w,
            "h": h,
            "cells": cells,
        }

        # Map all keys to this entry
        for key in keys:
            icon_data[key] = entry

        processed += 1

    # Write output
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(icon_data, f, indent=2, ensure_ascii=False)

    unique_icons = processed
    total_keys = len(icon_data)
    print(f"Extracted {unique_icons} unique icons mapped to {total_keys} service type keys")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
