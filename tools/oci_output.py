#!/usr/bin/env python3
"""
OCI Deal Accelerator — Output Orchestrator

Routes output generation based on the architect's format selection.
Supports: deck (default), deck+drawio, deck+doc, deck+xlsx, full, doc only.

Usage:
    python oci_output.py --spec proposal.yaml --format deck --output-dir ./output
    python oci_output.py --spec proposal.yaml --format full --output-dir ./output
"""

import yaml
import argparse
import os
import sys
from pathlib import Path

# Output format definitions
FORMATS = {
    "deck": ["pptx"],
    "deck+drawio": ["pptx", "drawio"],
    "deck+doc": ["pptx", "docx"],
    "deck+xlsx": ["pptx", "xlsx"],
    "full": ["pptx", "drawio", "docx", "xlsx"],
    "doc": ["docx"],
}

GENERATORS = {
    "pptx": {
        "module": "oci_deck_gen",
        "class": "OCIDeckGenerator",
        "method": "from_spec",
        "description": "Slide deck (.pptx)",
    },
    "drawio": {
        "module": "oci_diagram_gen",
        "class": "OCIDiagramGenerator",
        "method": "from_spec",
        "description": "Architecture diagram (.drawio)",
    },
    "docx": {
        "module": "oci_doc_gen",
        "class": "OCIDocGenerator",
        "method": "from_spec",
        "description": "Technical document (.docx)",
        "optional": True,
    },
    "xlsx": {
        "module": "oci_cost_gen",
        "class": "OCICostGenerator",
        "method": "from_spec",
        "description": "Cost spreadsheet (.xlsx)",
        "optional": True,
    },
}


def resolve_format(format_str: str) -> list:
    """Resolve a format string to a list of output types."""
    normalized = format_str.lower().strip().replace(" ", "")
    # Handle common variations
    for key in FORMATS:
        if normalized == key.replace("+", "").replace(" ", ""):
            return FORMATS[key]
    if normalized in FORMATS:
        return FORMATS[normalized]
    # Default to deck
    print(f"Warning: Unknown format '{format_str}', defaulting to 'deck'")
    return FORMATS["deck"]


def generate_output(spec: dict, output_type: str, output_dir: str,
                    base_name: str) -> str | None:
    """Generate a single output type. Returns the output path or None."""
    gen_config = GENERATORS.get(output_type)
    if not gen_config:
        print(f"  Skip: No generator for .{output_type}")
        return None

    output_path = os.path.join(output_dir, f"{base_name}.{output_type}")

    try:
        # Dynamic import
        module = __import__(gen_config["module"])
        gen_class = getattr(module, gen_config["class"])
        factory = getattr(gen_class, gen_config["method"])
        gen = factory(spec)
        gen.save(output_path)
        print(f"  Generated: {output_path}")
        return output_path
    except ImportError:
        if gen_config.get("optional"):
            print(f"  Skip: {gen_config['description']} "
                  f"(generator not available)")
            return None
        raise
    except Exception as e:
        print(f"  Error generating {gen_config['description']}: {e}")
        return None


def orchestrate(spec_path: str, format_str: str = "deck",
                output_dir: str = ".", base_name: str = None) -> list:
    """Main orchestration: load spec, generate all requested outputs."""
    with open(spec_path, 'r') as f:
        spec = yaml.safe_load(f)

    if not base_name:
        base_name = Path(spec_path).stem

    os.makedirs(output_dir, exist_ok=True)

    output_types = resolve_format(format_str)
    print(f"Output format: {format_str}")
    print(f"Generating: {', '.join(f'.{t}' for t in output_types)}")
    print(f"Output directory: {output_dir}")
    print()

    results = []
    for output_type in output_types:
        result = generate_output(spec, output_type, output_dir, base_name)
        if result:
            results.append(result)

    print(f"\nDone. Generated {len(results)} file(s).")
    return results


def main():
    parser = argparse.ArgumentParser(
        description="OCI Deal Accelerator — Output Orchestrator"
    )
    parser.add_argument(
        "--spec", required=True,
        help="Path to YAML spec file",
    )
    parser.add_argument(
        "--format", default="deck",
        choices=list(FORMATS.keys()),
        help="Output format selection (default: deck)",
    )
    parser.add_argument(
        "--output-dir", default=".",
        help="Output directory (default: current directory)",
    )
    parser.add_argument(
        "--name", default=None,
        help="Base name for output files (default: spec filename)",
    )
    args = parser.parse_args()

    # Add tools/ to path so generators can be imported
    tools_dir = os.path.dirname(os.path.abspath(__file__))
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)

    orchestrate(args.spec, args.format, args.output_dir, args.name)


if __name__ == "__main__":
    main()
