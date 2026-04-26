#!/usr/bin/env python3
"""
import_oci_library — bulk-import every shape from the official Oracle
``OCI Library.xml`` (downloadable from the Style Guide for Drawio zip)
into ``kb/diagram/oci-icons.json``.

Why this is a real tool, not a one-off audit: the previous icon set
covered ~60 shapes hand-harvested from a handful of Architecture
Center exports. The official library has 220+ shapes. Without a bulk
importer we silently fail to render whole product families
(Analytics, AI, Applications, Identity & Security, Compute variants,
…), and a developer wouldn't know until the deliverable comes out
without the right icon.

Usage:
  python tools/import_oci_library.py
  python tools/import_oci_library.py --library /path/to/OCI Library.xml
  python tools/import_oci_library.py --dry-run

The library file lives under
``kb/diagram/assets/oci-toolkit-drawio/OCI Library.xml`` after running
``tools/refresh_oci_drawio_toolkit.py``.

Each entry is decoded (zlib + base64 + URL-encoded XML), its cells'
geometry is normalised so the wrapper sits at ``(0, 0, w, h)``, and
the resulting entry is keyed by a canonical slug derived from the
title (e.g. ``Database - Autonomous Database`` →
``database_autonomous_database`` plus ``autonomous_database`` alias).
"""

from __future__ import annotations

import argparse
import base64
import html
import json
import re
import sys
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LIBRARY = PROJECT_ROOT / "kb" / "diagram" / "assets" / "oci-toolkit-drawio" / "OCI Library.xml"
DEFAULT_DEST = PROJECT_ROOT / "kb" / "diagram" / "oci-icons.json"


def _slug(text: str) -> str:
    text = html.unescape(text).replace("&nbsp;", " ")
    text = re.sub(r"[^a-zA-Z0-9]+", "_", text.lower()).strip("_")
    return text


def _decode_xml(payload: str) -> str:
    """drawio library entries are zlib-deflated + base64 + URL-encoded."""
    raw = base64.b64decode(payload)
    xml_bytes = zlib.decompress(raw, -15)
    return unquote(xml_bytes.decode("utf-8"))


def _normalize_cells(xml_text: str, w: float, h: float) -> tuple[list[str], int]:
    """Return cells serialised with normalised geometry.

    Strategy:
      1. Parse the XML fragment (drawio wraps cells in <root>…</root>).
      2. Find the wrapper cell — the one whose mxGeometry width/height
         most closely matches the entry's declared (w, h). That cell
         becomes id "2", with geometry forced to (0, 0, w, h).
      3. All other cells get sequential ids; their geometry is left
         alone (it's relative to their parent). Parent ids are remapped.
    """
    # The library blob is just a list of mxCell siblings, not a full doc.
    # Wrap so ET can parse.
    wrapped = f"<root>{xml_text}</root>"
    try:
        root = ET.fromstring(wrapped)
    except ET.ParseError:
        return [], 0

    cells = list(root.iter("mxCell"))
    if not cells:
        return [], 0

    # Identify wrapper: cell whose geometry's w/h best matches (w, h).
    def _dims(c: ET.Element) -> tuple[float, float]:
        g = c.find("mxGeometry")
        if g is None:
            return 0.0, 0.0
        try:
            return float(g.get("width") or 0), float(g.get("height") or 0)
        except ValueError:
            return 0.0, 0.0

    wrapper_idx = 0
    best_score = float("inf")
    for i, c in enumerate(cells):
        cw, ch = _dims(c)
        score = abs(cw - w) + abs(ch - h)
        if score < best_score and cw > 0 and ch > 0:
            best_score = score
            wrapper_idx = i

    # Build id map. Wrapper → "2"; descendants → "3","4",…
    id_map: dict[str, str] = {}
    wrapper_orig = cells[wrapper_idx].get("id") or f"_w{wrapper_idx}"
    id_map[wrapper_orig] = "2"
    counter = 3
    for i, c in enumerate(cells):
        if i == wrapper_idx:
            continue
        orig = c.get("id") or f"_c{i}"
        id_map[orig] = str(counter)
        counter += 1

    serialized: list[str] = []
    for i, c in enumerate(cells):
        orig = c.get("id") or (f"_w{i}" if i == wrapper_idx else f"_c{i}")
        new_id = id_map[orig]
        c_copy = ET.fromstring(ET.tostring(c))
        c_copy.set("id", new_id)
        old_parent = c_copy.get("parent") or ""
        c_copy.set("parent", id_map.get(old_parent, "1"))
        if i == wrapper_idx:
            geom = c_copy.find("mxGeometry")
            if geom is not None:
                geom.set("x", "0")
                geom.set("y", "0")
                geom.set("width", str(w))
                geom.set("height", str(h))
        serialized.append(ET.tostring(c_copy, encoding="unicode"))

    return serialized, len(cells)


# ---------------------------------------------------------------------------
# Canonical-title → short alias map. Keys must be the EXACT library title
# (post HTML-decode, after stripping the category prefix). Substring
# matching was tried first but produced silent collisions — e.g.
# "Burstable Virtual Machine Burstable VM" contains the substring
# "virtual machine", so it claimed the canonical `virtual_machine` alias
# from the actual "Virtual Machine VM" entry. Exact match means each
# alias has exactly one source.
# ---------------------------------------------------------------------------
# Verified against `OCI Library.xml` v24.2 short suffixes 2026-04-25.
# Substring matching produced silent collisions (e.g. "virtual machine" hit
# Burstable VM first), so this table uses EXACT title-suffix matches. Run
# `python tools/import_oci_library.py --dry-run` to verify which entries
# resolve before writing.
TITLE_TO_ALIASES: dict[str, list[str]] = {
    # Compute (Compute - …)
    "Virtual Machine VM": ["virtual_machine", "vm", "oci_compute", "compute_instance", "compute"],
    "Bare Metal Compute": ["bare_metal", "bare_metal_compute"],
    "Burstable Virtual Machine Burstable VM": ["burstable_vm", "burstable_virtual_machine"],
    "Flex Virtual Machine Flex VM": ["flex_vm"],
    "Instance Pools": ["instance_pool", "instance_pools"],
    "Functions": ["functions", "oci_functions"],
    "Autoscaling": ["autoscaling"],
    # Database (Database - …) — verified library suffixes
    "Database System": ["database_system", "base_db", "base_database", "dbcs", "db_system"],
    "Autonomous DB": ["autonomous_db", "autonomous_database"],
    "ADB-D": ["adb_d", "adb"],          # ADB on Dedicated infrastructure
    "ADW-D": ["adw_d", "adw"],
    "ATP-D": ["atp_d", "atp"],
    "ADB-S": ["adb_s"],
    "Exadata": ["exadata", "exacs", "oracle_exadata_database_service", "exadata_dedicated"],
    "Exadata C@C": ["exadata_cc", "exacc"],
    "Data Safe": ["data_safe"],
    "GoldenGate": ["goldengate"],
    "NoSQL": ["nosql"],
    "MySQL": ["mysql"],
    "APEX": ["apex"],
    # Storage (Storage - …)
    "Object Storage": ["object_storage", "bucket", "storage", "oci_object_storage"],
    "Block Storage": ["block_volume", "block_storage"],
    "File Storage": ["file_storage"],
    "Buckets": ["bucket"],
    "Backup Restore": ["backup_restore"],
    # Networking (Networking - …)
    "Internet Gateway": ["internet_gateway", "igw"],
    "Service Gateway": ["service_gateway", "sgw"],
    "NAT Gateway": ["nat_gateway", "natgw"],
    "Dynamic Routing Gateway DRG": ["drg", "dynamic_routing_gateway"],
    "Load Balancer": ["load_balancer", "lb"],
    "Flexible Load Balancer": ["flexible_lb", "nlb", "network_load_balancer"],
    # FastConnect icon — Library only ships connector-themed variants;
    # use the vertical 71×75 stencil as the canonical FastConnect badge.
    "Special Connectors - FastConnect - Vertical": ["fastconnect", "fastconnect_vertical"],
    "Special Connectors - FastConnect - Horizontal": ["fastconnect_horizontal"],
    "Virtual Cloud Network VCN": ["vcn", "vcn_icon"],
    "Route Table": [
        # Per OCI Toolkit slide 18: "VCN, routing table, and security list
        # icons are used at half size as labels to differentiate the VCN
        # and subnet." There is no separate Security List entry, so the
        # Route Table stencil serves as the canonical subnet corner marker.
        "route_table", "route_table_and_security_list",
        "security_list", "security_lists",
    ],
    "DNS": ["dns"],
    # Identity & Security (Identity and Security - …)
    "Policies": ["policies", "iam_policies"],
    "Vault": ["vault"],
    "Key Vault": ["key_vault", "vault_secrets"],
    "Bastion": ["bastion"],
    "Cloud Guard": ["cloud_guard"],
    "Firewall": ["network_firewall", "firewall"],
    "Web Application Firewall WAF": ["waf", "web_application_firewall"],
    # Observability and Management
    "Monitoring": ["monitoring"],
    "Notifications": ["notifications", "notification"],
    "Logging": ["logging"],
    "Logging Analytics": ["logging_analytics"],
    "Alarms": ["alarms"],
    # Integration / Developer Services
    "API Gateway": ["api_gateway"],
    "Streaming": ["streaming", "oci_streaming"],
    "Queue": ["queue"],
    "Events Service": ["events_service"],
    "API Service": ["api_service"],
    # Containers
    "Container Engine for Kubernetes Container Engine for Kubernetes Cluster": [
        "oke", "kubernetes", "container_engine_for_kubernetes_cluster",
    ],
    # Migration / DR
    "Full Stack Disaster Recovery FSDR": ["full_stack_disaster_recovery", "fsdr"],
}

# Some types Oracle's library doesn't ship a stencil for (Data Guard,
# Refreshable Clone). For those we point the alias at an equivalent
# Database icon so renders don't fall back to colored rectangles.
COMPOSITE_FALLBACK_ALIASES: dict[str, str] = {
    "data_guard": "Database",          # plain "Database" stencil
    "data_guard_recovery": "Database",
    "refreshable_clone": "ADB-D",
}


def _alias_keys(title: str) -> list[str]:
    """Return [canonical_slug, *short_aliases].

    The canonical slug is always the long title slug
    (e.g. ``compute_virtual_machine_vm``). Short aliases come from the
    explicit TITLE_TO_ALIASES table, keyed by the title *suffix* after
    the category prefix (post HTML-decode).
    """
    canonical = _slug(title)
    aliases: list[str] = [canonical]
    decoded = html.unescape(title).replace("&nbsp;", " ").replace("&amp;", "&")
    short = decoded.split(" - ", 1)[-1].strip()
    if short in TITLE_TO_ALIASES:
        aliases.extend(TITLE_TO_ALIASES[short])
    seen: set[str] = set()
    out: list[str] = []
    for a in aliases:
        if a and a not in seen:
            out.append(a)
            seen.add(a)
    return out


def _iter_library_entries(library_path: Path) -> Iterable[dict]:
    raw = library_path.read_text(encoding="utf-8")
    m = re.search(r"<mxlibrary>(.+?)</mxlibrary>", raw, re.DOTALL)
    if not m:
        raise SystemExit(f"No <mxlibrary> in {library_path}")
    entries = json.loads(m.group(1))
    yield from entries


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, default=DEFAULT_LIBRARY)
    parser.add_argument("--dest", type=Path, default=DEFAULT_DEST)
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would be added without writing.")
    parser.add_argument("--keep-existing", action="store_true",
                        help="Preserve hand-curated entries already present "
                             "(do not overwrite). Off by default — the official "
                             "library is the source of truth.")
    args = parser.parse_args()

    icons = json.loads(args.dest.read_text(encoding="utf-8")) if args.dest.exists() else {}
    initial_count = len(icons)
    added: list[str] = []
    aliased: list[str] = []
    skipped: list[str] = []
    failed: list[str] = []

    for entry in _iter_library_entries(args.library):
        title = entry.get("title", "")
        if not title:
            continue
        try:
            xml_text = _decode_xml(entry["xml"])
        except Exception as exc:
            failed.append(f"{title}: {exc}")
            continue
        w = float(entry.get("w", 0) or 0)
        h = float(entry.get("h", 0) or 0)
        if w <= 0 or h <= 0:
            failed.append(f"{title}: missing w/h")
            continue
        cells, ncells = _normalize_cells(xml_text, w, h)
        if not cells:
            failed.append(f"{title}: no cells parsed")
            continue
        keys = _alias_keys(title)
        canonical = keys[0]
        record = {
            "title": title.replace("&amp;nbsp;", " ").replace("&amp;", "&"),
            "w": w, "h": h, "cells": cells,
            "source": "OCI Library.xml v24.2",
        }
        if canonical in icons and args.keep_existing:
            skipped.append(canonical)
        else:
            icons[canonical] = record
            added.append(canonical)
        for alias in keys[1:]:
            if alias in icons and args.keep_existing:
                continue
            icons[alias] = record
            aliased.append(alias)

    # Composite/derived types Oracle does not ship as their own stencil
    # (Data Guard, refreshable clones, …). Resolve via fallback aliases
    # so spec authors can keep using the friendly names without falling
    # back to a colored rectangle.
    by_short_title: dict[str, dict] = {}
    for record in icons.values():
        title = record.get("title", "")
        if " - " in title:
            by_short_title.setdefault(title.split(" - ", 1)[-1].strip(), record)
    fallback_count = 0
    for alias, source_title in COMPOSITE_FALLBACK_ALIASES.items():
        if alias in icons:
            continue
        source = by_short_title.get(source_title)
        if source:
            icons[alias] = source
            fallback_count += 1

    print(f"Initial entries:  {initial_count}", file=sys.stderr)
    print(f"Library entries:  {len(added) + len(skipped) + len(failed)}", file=sys.stderr)
    if fallback_count:
        print(f"Composite fallbacks added: {fallback_count}", file=sys.stderr)
    print(f"Added/replaced:   {len(added)}", file=sys.stderr)
    print(f"Aliased:          {len(aliased)}", file=sys.stderr)
    print(f"Skipped (kept):   {len(skipped)}", file=sys.stderr)
    print(f"Failed to parse:  {len(failed)}", file=sys.stderr)
    for line in failed[:10]:
        print(f"  - {line}", file=sys.stderr)
    print(f"Final entries:    {len(icons)}", file=sys.stderr)

    if not args.dry_run:
        args.dest.write_text(json.dumps(icons, indent=2), encoding="utf-8")
        print(f"\nWrote {args.dest}", file=sys.stderr)


if __name__ == "__main__":
    main()
