#!/usr/bin/env python3
"""Download MCP-generated artifacts and compare them against local analysis."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from random_eval_cases import analyze_drawio, analyze_pptx, analyze_xlsx


def download(url: str, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, path)


def main():
    parser = argparse.ArgumentParser(description="Analyze MCP artifacts against local baseline.")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--local-analysis", required=True)
    parser.add_argument("--deck-url", required=True)
    parser.add_argument("--diagram-url", required=True)
    parser.add_argument("--bizcase-url", required=True)
    parser.add_argument("--bom-url", required=True)
    parser.add_argument("--appca-url", required=True)
    args = parser.parse_args()

    out_dir = PROJECT_ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    files = {
        "deck": ("mcp-deck.pptx", args.deck_url, analyze_pptx),
        "diagram": ("mcp-diagram.drawio", args.diagram_url, analyze_drawio),
        "business_case": ("mcp-bizcase.pptx", args.bizcase_url, analyze_pptx),
        "bom": ("mcp-bom.xlsx", args.bom_url, analyze_xlsx),
        "bom_appca": ("mcp-bom-appca.xlsx", args.appca_url, analyze_xlsx),
    }

    analysis = {}
    for key, (filename, url, analyzer) in files.items():
        path = out_dir / filename
        download(url, path)
        analysis[key] = analyzer(path)

    local = json.loads((PROJECT_ROOT / args.local_analysis).read_text(encoding="utf-8"))
    local_analysis = local["local_analysis"]

    comparison = {
        "deck": {
            "local_slides": local_analysis["deck"]["slide_count"],
            "mcp_slides": analysis["deck"]["slide_count"],
            "local_blank_slides": local_analysis["deck"]["blank_slides"],
            "mcp_blank_slides": analysis["deck"]["blank_slides"],
        },
        "business_case": {
            "local_slides": local_analysis["business_case"]["slide_count"],
            "mcp_slides": analysis["business_case"]["slide_count"],
            "local_blank_slides": local_analysis["business_case"]["blank_slides"],
            "mcp_blank_slides": analysis["business_case"]["blank_slides"],
        },
        "bom": {
            "local_empty_sheets": local_analysis["bom"]["empty_sheets"],
            "mcp_empty_sheets": analysis["bom"]["empty_sheets"],
        },
        "bom_appca": {
            "local_empty_sheets": local_analysis["bom_appca"]["empty_sheets"],
            "mcp_empty_sheets": analysis["bom_appca"]["empty_sheets"],
        },
        "diagram": {
            "local_bytes": local_analysis["diagram"]["bytes"],
            "mcp_bytes": analysis["diagram"]["bytes"],
            "local_cell_values": local_analysis["diagram"]["cell_values"],
            "mcp_cell_values": analysis["diagram"]["cell_values"],
        },
    }

    output = {
        "mcp_analysis": analysis,
        "comparison": comparison,
    }
    output_path = out_dir / "mcp-analysis.json"
    output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(output_path.relative_to(PROJECT_ROOT))


if __name__ == "__main__":
    main()
