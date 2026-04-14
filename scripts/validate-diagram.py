#!/usr/bin/env python3
"""
Diagram quality validator — checks generated .drawio files against
Oracle Architecture Center visual standards.

Usage:
    python3 scripts/validate-diagram.py examples/output-demo-pharma-mx/opt02-architecture.drawio
"""

import sys
import xml.etree.ElementTree as ET

MIN_ICON_H = 45       # Minimum icon height (px) — Oracle refs use 50-60
MIN_ICON_W = 30       # Minimum icon width (px)
MAX_EMPTY_RATIO = 0.7  # Max empty space ratio in a container
MIN_LABEL_FONT = 10    # Minimum label font size
MIN_GAP_PX = 5         # Minimum gap between sibling elements


def validate(filepath: str) -> list:
    """Return list of (severity, message) tuples."""
    issues = []
    tree = ET.parse(filepath)
    root = tree.getroot()

    icon_groups = []
    containers = []
    all_cells = {}

    for cell in root.iter('mxCell'):
        cid = cell.get('id', '')
        style = cell.get('style', '')
        value = cell.get('value', '')
        geo = cell.find('mxGeometry')
        all_cells[cid] = cell

        if geo is None:
            continue

        w = float(geo.get('width', 0))
        h = float(geo.get('height', 0))
        x = float(geo.get('x', 0))
        y = float(geo.get('y', 0))

        # Icon groups
        if 'group' in style and 'connectable=1' in style:
            icon_groups.append({
                'id': cid, 'x': x, 'y': y, 'w': w, 'h': h,
                'parent': cell.get('parent', ''),
            })
            if h < MIN_ICON_H:
                issues.append(('WARN', f'Icon {cid} too short: {h:.0f}px (min {MIN_ICON_H})'))
            if w < MIN_ICON_W:
                issues.append(('WARN', f'Icon {cid} too narrow: {w:.0f}px (min {MIN_ICON_W})'))

        # Containers (regions, VCNs, subnets)
        if value and any(kw in value for kw in ['Region', 'VCN', 'Subnet', 'Oracle Cloud']):
            containers.append({
                'id': cid, 'name': value[:40], 'x': x, 'y': y, 'w': w, 'h': h,
                'parent': cell.get('parent', ''),
            })

    # Check children overflow parents
    container_map = {}
    for cell in root.iter('mxCell'):
        cid = cell.get('id', '')
        val = cell.get('value', '')
        geo = cell.find('mxGeometry')
        if geo is not None and val:
            container_map[cid] = {
                'name': val[:50], 'x': float(geo.get('x', 0)),
                'y': float(geo.get('y', 0)), 'w': float(geo.get('width', 0)),
                'h': float(geo.get('height', 0)), 'parent': cell.get('parent', ''),
            }

    for cid, c in container_map.items():
        parent = container_map.get(c['parent'])
        if parent:
            child_right = c['x'] + c['w']
            child_bottom = c['y'] + c['h']
            overflow_r = child_right - parent['w']
            overflow_b = child_bottom - parent['h']
            if overflow_r > 2:
                issues.append(('ERROR', f'{c["name"]} overflows {parent["name"]} RIGHT by {overflow_r:.0f}px'))
            if overflow_b > 2:
                issues.append(('ERROR', f'{c["name"]} overflows {parent["name"]} BOTTOM by {overflow_b:.0f}px'))

    # Check for overlapping siblings (same parent)
    by_parent = {}
    for ig in icon_groups:
        by_parent.setdefault(ig['parent'], []).append(ig)

    for parent_id, siblings in by_parent.items():
        siblings.sort(key=lambda s: (s['y'], s['x']))
        for i in range(len(siblings) - 1):
            a = siblings[i]
            b = siblings[i + 1]
            # Check vertical overlap (same column, x ranges overlap)
            x_overlap = not (a['x'] + a['w'] < b['x'] or b['x'] + b['w'] < a['x'])
            if x_overlap:
                gap = b['y'] - (a['y'] + a['h'])
                if gap < MIN_GAP_PX:
                    issues.append(('ERROR', f'Overlap between icons in parent {parent_id}: gap={gap:.0f}px'))

    # Check container utilization (warn on mostly empty containers)
    for cont in containers:
        children_area = 0
        for ig in icon_groups:
            if ig['parent'] == cont['id']:
                children_area += ig['w'] * ig['h']
        for child_cont in containers:
            if child_cont['parent'] == cont['id']:
                children_area += child_cont['w'] * child_cont['h']
        cont_area = cont['w'] * cont['h']
        if cont_area > 0:
            fill_ratio = children_area / cont_area
            if fill_ratio < (1 - MAX_EMPTY_RATIO):
                issues.append(('INFO', f'{cont["name"]}: {fill_ratio:.0%} filled ({cont["w"]:.0f}x{cont["h"]:.0f})'))

    # Check edge labels have offset (mxPoint as="offset")
    edges_with_label = 0
    edges_with_offset = 0
    for cell in root.iter('mxCell'):
        if cell.get('edge') == '1' and cell.get('value', '').strip():
            edges_with_label += 1
            geo = cell.find('mxGeometry')
            if geo is not None:
                offset = geo.find('.//mxPoint[@as="offset"]')
                if offset is not None:
                    edges_with_offset += 1

    if edges_with_label > 0 and edges_with_offset < edges_with_label:
        issues.append(('WARN', f'{edges_with_label - edges_with_offset}/{edges_with_label} edge labels missing offset'))

    # Check jettySize=auto present
    has_jetty = False
    for cell in root.iter('mxCell'):
        if 'jettySize=auto' in cell.get('style', ''):
            has_jetty = True
            break
    if not has_jetty:
        issues.append(('WARN', 'No edges with jettySize=auto'))

    # Check container=1 present
    has_container = False
    for cell in root.iter('mxCell'):
        if 'container=1' in cell.get('style', ''):
            has_container = True
            break
    if not has_container:
        issues.append(('WARN', 'No containers with explicit container=1 style'))

    return issues


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <diagram.drawio>")
        sys.exit(1)

    filepath = sys.argv[1]
    issues = validate(filepath)

    if not issues:
        print(f"✅ {filepath}: All checks passed")
        sys.exit(0)

    errors = [i for i in issues if i[0] == 'ERROR']
    warns = [i for i in issues if i[0] == 'WARN']
    infos = [i for i in issues if i[0] == 'INFO']

    print(f"📋 Diagram validation: {filepath}")
    print(f"   {len(errors)} errors, {len(warns)} warnings, {len(infos)} info")
    print()

    for severity, msg in issues:
        icon = {'ERROR': '❌', 'WARN': '⚠️', 'INFO': 'ℹ️'}.get(severity, '?')
        print(f"  {icon} [{severity}] {msg}")

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
