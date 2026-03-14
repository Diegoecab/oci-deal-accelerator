#!/usr/bin/env python3
"""
OCI Deal Accelerator — ADB Feature Compatibility Matrix CLI

Query, compare, and update the ADB feature compatibility matrix from
the command line.

Usage:
    python feature_matrix_cli.py check "auto scaling" adb_s 23ai
    python feature_matrix_cli.py compare adb_s exacs 23ai
    python feature_matrix_cli.py gaps adb_s 23ai
    python feature_matrix_cli.py update "Auto Scaling (OCPU)" adb_s 23ai --status GA --notes "Updated"
    python feature_matrix_cli.py export --format markdown
    python feature_matrix_cli.py export --format csv
"""

import argparse
import csv
import io
import os
import sys
from datetime import date
from typing import Any, Dict, List, Optional, Tuple

VALID_CONFIDENCE = {"validated", "observed", "reported", "inferred"}

import yaml


# =============================================================================
# Constants
# =============================================================================

MATRIX_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "kb", "compatibility", "adb-feature-matrix.yaml",
)

VALID_STATUSES = {"GA", "GA_CAVEAT", "PREVIEW", "LIMITED", "NOT_AVAIL", "BROKEN", "UNTESTED"}

# ANSI color codes for terminal output
_COLORS = {
    "GA":        "\033[32m",        # green
    "GA_CAVEAT": "\033[33m",        # yellow
    "PREVIEW":   "\033[36m",        # cyan
    "LIMITED":   "\033[93m",        # bright yellow
    "NOT_AVAIL": "\033[31m",        # red
    "BROKEN":    "\033[1;31m",      # red bold
    "UNTESTED":  "\033[90m",        # gray
}
_RESET = "\033[0m"


# =============================================================================
# Helpers
# =============================================================================

def _color(status: str) -> str:
    """Wrap a status string with the appropriate ANSI color."""
    code = _COLORS.get(status, "")
    return f"{code}{status}{_RESET}" if code else status


def _supports_color() -> bool:
    """Return True when stdout is a tty that likely supports ANSI escapes."""
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _plain(status: str) -> str:
    """Return the status without color codes."""
    return status


def _get_color_fn():
    """Return the appropriate formatter (colored or plain)."""
    return _color if _supports_color() else _plain


def load_matrix(path: str) -> Dict[str, Any]:
    """Load the YAML matrix file and return its contents as a dict."""
    resolved = os.path.realpath(path)
    if not os.path.isfile(resolved):
        print(f"Error: Matrix file not found at {resolved}", file=sys.stderr)
        sys.exit(1)
    with open(resolved, "r", encoding="utf-8") as fh:
        try:
            data = yaml.safe_load(fh)
        except yaml.YAMLError as exc:
            print(f"Error: Failed to parse YAML — {exc}", file=sys.stderr)
            sys.exit(1)
    if not data or "features" not in data:
        print("Error: Matrix file is missing 'features' key.", file=sys.stderr)
        sys.exit(1)
    return data


def save_matrix(path: str, data: Dict[str, Any]) -> None:
    """Write the matrix dict back to YAML, preserving readability."""
    resolved = os.path.realpath(path)
    with open(resolved, "w", encoding="utf-8") as fh:
        yaml.dump(
            data,
            fh,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
            width=120,
        )


def get_version_ids(data: Dict[str, Any]) -> List[str]:
    """Return ordered list of version ids from the matrix."""
    return [v["id"] for v in data.get("versions", [])]


def get_deployment_ids(data: Dict[str, Any]) -> List[str]:
    """Return ordered list of deployment type ids from the matrix."""
    return [d["id"] for d in data.get("deployment_types", [])]


def get_deployment_name(data: Dict[str, Any], deploy_id: str) -> str:
    """Look up the human-readable name for a deployment id."""
    for d in data.get("deployment_types", []):
        if d["id"] == deploy_id:
            return d.get("name", deploy_id)
    return deploy_id


def validate_deployment(data: Dict[str, Any], deploy_id: str) -> None:
    """Exit with an error if the deployment id is not in the matrix."""
    valid = get_deployment_ids(data)
    if deploy_id not in valid:
        print(
            f"Error: Unknown deployment type '{deploy_id}'. "
            f"Valid types: {', '.join(valid)}",
            file=sys.stderr,
        )
        sys.exit(1)


def validate_version(data: Dict[str, Any], version: str) -> None:
    """Exit with an error if the version is not in the matrix."""
    valid = get_version_ids(data)
    if version not in valid:
        print(
            f"Error: Unknown version '{version}'. Valid versions: {', '.join(valid)}",
            file=sys.stderr,
        )
        sys.exit(1)


def find_features(data: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
    """
    Find features whose name matches *query* (case-insensitive, partial).
    Returns a list of matching feature dicts.
    """
    query_lower = query.lower()
    return [
        f for f in data["features"]
        if query_lower in f["name"].lower()
    ]


def get_cell(feature: Dict[str, Any], deploy: str, version: str) -> Optional[Dict[str, Any]]:
    """Return the matrix cell dict for a feature/deploy/version, or None."""
    return feature.get("matrix", {}).get(deploy, {}).get(version)


# =============================================================================
# Library API — importable functions for programmatic use and testing
# =============================================================================

def check(feature_name: str, deployment: str, version: str, matrix_path: str = MATRIX_PATH) -> Dict[str, Any]:
    """Look up a feature/deployment/version and return {status, notes, feature_name}."""
    data = load_matrix(matrix_path)
    matches = find_features(data, feature_name)
    if not matches:
        raise LookupError(f"No features matching '{feature_name}'")
    if len(matches) > 1:
        raise LookupError(
            f"Ambiguous feature name '{feature_name}'. Matches: "
            + ", ".join(m["name"] for m in matches)
        )
    feature = matches[0]
    cell = get_cell(feature, deployment, version)
    if cell is None:
        return {"status": "UNTESTED", "notes": "no entry in matrix", "feature_name": feature["name"]}
    return {
        "status": cell.get("status", "UNTESTED"),
        "notes": cell.get("notes", ""),
        "feature_name": feature["name"],
    }


def compare(deploy1: str, deploy2: str, version: str, matrix_path: str = MATRIX_PATH) -> List[Dict[str, Any]]:
    """Compare two deployment types. Returns list of dicts with name, status1, status2."""
    data = load_matrix(matrix_path)
    results = []
    for feature in data["features"]:
        cell1 = get_cell(feature, deploy1, version)
        cell2 = get_cell(feature, deploy2, version)
        results.append({
            "name": feature["name"],
            "status1": cell1["status"] if cell1 else "UNTESTED",
            "status2": cell2["status"] if cell2 else "UNTESTED",
        })
    return results


def gaps(deployment: str, version: str, matrix_path: str = MATRIX_PATH) -> List[Dict[str, Any]]:
    """List features that are NOT_AVAIL, BROKEN, or LIMITED."""
    data = load_matrix(matrix_path)
    gap_statuses = {"NOT_AVAIL", "BROKEN", "LIMITED"}
    results = []
    for feature in data["features"]:
        cell = get_cell(feature, deployment, version)
        if cell is None:
            continue
        status = cell.get("status", "UNTESTED")
        if status in gap_statuses:
            results.append({
                "name": feature["name"],
                "status": status,
                "notes": cell.get("notes", ""),
            })
    return results


def export_markdown(output_path: str, matrix_path: str = MATRIX_PATH) -> None:
    """Export the full matrix as a markdown table to a file."""
    data = load_matrix(matrix_path)
    versions = get_version_ids(data)
    deployments = get_deployment_ids(data)
    columns = [(d, v) for d in deployments for v in versions]
    col_labels = [f"{d}/{v}" for d, v in columns]
    features = data["features"]

    feat_width = max((len(f["name"]) for f in features), default=7)
    feat_width = max(feat_width, len("Feature"))
    col_widths = [max(len(lbl), 10) for lbl in col_labels]

    lines = []
    header = f"| {'Feature':<{feat_width}} |"
    for lbl, w in zip(col_labels, col_widths):
        header += f" {lbl:<{w}} |"
    lines.append(header)

    sep = f"|{'-' * (feat_width + 2)}|"
    for w in col_widths:
        sep += f"{'-' * (w + 2)}|"
    lines.append(sep)

    for feature in features:
        row = f"| {feature['name']:<{feat_width}} |"
        for (d, v), w in zip(columns, col_widths):
            cell = get_cell(feature, d, v)
            status = cell["status"] if cell else "-"
            row += f" {status:<{w}} |"
        lines.append(row)

    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def export_csv(output_path: str, matrix_path: str = MATRIX_PATH) -> None:
    """Export the full matrix as CSV to a file."""
    data = load_matrix(matrix_path)
    versions = get_version_ids(data)
    deployments = get_deployment_ids(data)
    columns = [(d, v) for d in deployments for v in versions]
    col_labels = [f"{d}/{v}" for d, v in columns]

    with open(output_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["Feature", "Category"] + col_labels)
        for feature in data["features"]:
            row = [feature["name"], feature.get("category", "")]
            for d, v in columns:
                cell = get_cell(feature, d, v)
                row.append(cell["status"] if cell else "")
            writer.writerow(row)


# =============================================================================
# Subcommands (CLI handlers)
# =============================================================================

def cmd_check(args: argparse.Namespace) -> None:
    """Look up a specific feature / deployment / version combo."""
    data = load_matrix(MATRIX_PATH)
    validate_deployment(data, args.deployment)
    validate_version(data, args.version)

    matches = find_features(data, args.feature)

    if not matches:
        print(f"No features matching '{args.feature}'.")
        sys.exit(1)

    if len(matches) > 1:
        print(f"Ambiguous feature name '{args.feature}'. Multiple matches:")
        for m in matches:
            print(f"  - {m['name']}")
        print("\nPlease be more specific.")
        sys.exit(1)

    feature = matches[0]
    cell = get_cell(feature, args.deployment, args.version)
    cfn = _get_color_fn()
    deploy_name = get_deployment_name(data, args.deployment)

    print(f"Feature:    {feature['name']}")
    print(f"Deployment: {deploy_name} ({args.deployment})")
    print(f"Version:    {args.version}")
    print()

    if cell is None:
        print(f"Status:     {cfn('UNTESTED')} (no entry in matrix)")
    else:
        status = cell.get("status", "UNTESTED")
        print(f"Status:     {cfn(status)}")
        notes = cell.get("notes")
        if notes:
            print(f"Notes:      {notes}")


def cmd_compare(args: argparse.Namespace) -> None:
    """Side-by-side comparison of two deployment types for a version."""
    data = load_matrix(MATRIX_PATH)
    validate_deployment(data, args.deploy1)
    validate_deployment(data, args.deploy2)
    validate_version(data, args.version)

    cfn = _get_color_fn()
    name1 = get_deployment_name(data, args.deploy1)
    name2 = get_deployment_name(data, args.deploy2)

    # Determine column widths
    feature_names = [f["name"] for f in data["features"]]
    col_feat = max(len(n) for n in feature_names) + 2
    col_status = max(len(name1), len(name2), 12) + 2

    header = (
        f"{'Feature':<{col_feat}}"
        f"  {name1:<{col_status}}"
        f"  {name2:<{col_status}}"
    )
    print(f"Comparison: {name1} vs {name2}  (version {args.version})")
    print()
    print(header)
    print("-" * len(header))

    for feature in data["features"]:
        cell1 = get_cell(feature, args.deploy1, args.version)
        cell2 = get_cell(feature, args.deploy2, args.version)
        s1 = cell1["status"] if cell1 else "UNTESTED"
        s2 = cell2["status"] if cell2 else "UNTESTED"

        # For plain (non-tty) we can just print aligned; for color we need
        # to pad BEFORE wrapping with color codes so alignment is correct.
        s1_padded = f"{s1:<{col_status}}"
        s2_padded = f"{s2:<{col_status}}"

        if _supports_color():
            s1_display = f"{_COLORS.get(s1, '')}{s1_padded}{_RESET}"
            s2_display = f"{_COLORS.get(s2, '')}{s2_padded}{_RESET}"
        else:
            s1_display = s1_padded
            s2_display = s2_padded

        print(f"{feature['name']:<{col_feat}}  {s1_display}  {s2_display}")


def cmd_gaps(args: argparse.Namespace) -> None:
    """List features that are NOT_AVAIL, BROKEN, or LIMITED for a deploy/version."""
    data = load_matrix(MATRIX_PATH)
    validate_deployment(data, args.deployment)
    validate_version(data, args.version)

    cfn = _get_color_fn()
    deploy_name = get_deployment_name(data, args.deployment)
    gap_statuses = {"NOT_AVAIL", "BROKEN", "LIMITED"}
    gaps: List[Tuple[str, str, Optional[str]]] = []

    for feature in data["features"]:
        cell = get_cell(feature, args.deployment, args.version)
        if cell is None:
            # No entry — could be untested or implicitly not available
            continue
        status = cell.get("status", "UNTESTED")
        if status in gap_statuses:
            gaps.append((feature["name"], status, cell.get("notes")))

    print(f"Gaps for {deploy_name} ({args.deployment}), version {args.version}:")
    print()

    if not gaps:
        print("  No gaps found — all mapped features are GA, GA_CAVEAT, PREVIEW, or UNTESTED.")
        return

    name_width = max(len(g[0]) for g in gaps) + 2
    for name, status, notes in gaps:
        status_display = cfn(status)
        line = f"  {name:<{name_width}} {status_display}"
        if notes:
            line += f"  — {notes}"
        print(line)


def cmd_update(args: argparse.Namespace) -> None:
    """Modify a specific cell in the matrix."""
    status = args.status.upper()
    if status not in VALID_STATUSES:
        print(
            f"Error: Invalid status '{args.status}'. "
            f"Valid statuses: {', '.join(sorted(VALID_STATUSES))}",
            file=sys.stderr,
        )
        sys.exit(1)

    data = load_matrix(MATRIX_PATH)
    validate_deployment(data, args.deployment)
    validate_version(data, args.version)

    matches = find_features(data, args.feature)

    if not matches:
        print(f"Error: No features matching '{args.feature}'.", file=sys.stderr)
        sys.exit(1)

    if len(matches) > 1:
        print(f"Ambiguous feature name '{args.feature}'. Multiple matches:")
        for m in matches:
            print(f"  - {m['name']}")
        print("\nPlease use the exact feature name.")
        sys.exit(1)

    feature = matches[0]

    # Ensure nested dicts exist
    if "matrix" not in feature:
        feature["matrix"] = {}
    if args.deployment not in feature["matrix"]:
        feature["matrix"][args.deployment] = {}

    cell: Dict[str, Any] = {"status": status}
    if args.notes:
        cell["notes"] = args.notes

    # Add contributor attribution if provided
    contributor_name = getattr(args, "name", None)
    contributor_team = getattr(args, "team", None)
    if contributor_name and contributor_team:
        contributor = {
            "name": contributor_name,
            "team": contributor_team,
            "date": date.today().isoformat(),
        }
        confidence = getattr(args, "confidence", None)
        if confidence and confidence in VALID_CONFIDENCE:
            contributor["confidence"] = confidence
        cell["contributor"] = contributor

    # Add field_finding_ref if provided
    field_ref = getattr(args, "field_finding_ref", None)
    if field_ref:
        cell["field_finding_ref"] = field_ref

    feature["matrix"][args.deployment][args.version] = cell

    # Update last_verified at root
    data["last_verified"] = date.today().isoformat()

    save_matrix(MATRIX_PATH, data)

    cfn = _get_color_fn()
    print(f"Updated '{feature['name']}' / {args.deployment} / {args.version}:")
    print(f"  Status: {cfn(status)}")
    if args.notes:
        print(f"  Notes:  {args.notes}")
    print(f"  last_verified set to {data['last_verified']}")


def cmd_export(args: argparse.Namespace) -> None:
    """Export the full matrix as markdown or CSV."""
    data = load_matrix(MATRIX_PATH)
    versions = get_version_ids(data)
    deployments = get_deployment_ids(data)

    # Build column headers: each column is deploy + version
    columns: List[Tuple[str, str]] = []
    for d in deployments:
        for v in versions:
            columns.append((d, v))

    col_labels = [f"{d}/{v}" for d, v in columns]

    if args.format == "csv":
        _export_csv(data, columns, col_labels)
    else:
        _export_markdown(data, columns, col_labels)


def _export_markdown(
    data: Dict[str, Any],
    columns: List[Tuple[str, str]],
    col_labels: List[str],
) -> None:
    """Print a markdown table to stdout."""
    features = data["features"]

    # Column widths
    feat_width = max(len(f["name"]) for f in features)
    feat_width = max(feat_width, len("Feature"))
    col_widths = [max(len(lbl), 10) for lbl in col_labels]

    # Header row
    header = f"| {'Feature':<{feat_width}} |"
    for lbl, w in zip(col_labels, col_widths):
        header += f" {lbl:<{w}} |"
    print(header)

    # Separator
    sep = f"|{'-' * (feat_width + 2)}|"
    for w in col_widths:
        sep += f"{'-' * (w + 2)}|"
    print(sep)

    # Data rows
    for feature in features:
        row = f"| {feature['name']:<{feat_width}} |"
        for (d, v), w in zip(columns, col_widths):
            cell = get_cell(feature, d, v)
            status = cell["status"] if cell else "-"
            row += f" {status:<{w}} |"
        print(row)


def _export_csv(
    data: Dict[str, Any],
    columns: List[Tuple[str, str]],
    col_labels: List[str],
) -> None:
    """Print CSV to stdout."""
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(["Feature", "Category"] + col_labels)

    for feature in data["features"]:
        row = [feature["name"], feature.get("category", "")]
        for d, v in columns:
            cell = get_cell(feature, d, v)
            row.append(cell["status"] if cell else "")
        writer.writerow(row)

    print(output.getvalue(), end="")


# =============================================================================
# CLI entry point
# =============================================================================

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="feature_matrix_cli",
        description="Query and update the ADB feature compatibility matrix.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- check ---
    p_check = subparsers.add_parser(
        "check",
        help="Look up a specific feature/deployment/version combo.",
    )
    p_check.add_argument("feature", help="Feature name (case-insensitive, partial match).")
    p_check.add_argument("deployment", help="Deployment type id (e.g. adb_s, exacs).")
    p_check.add_argument("version", help="Version id (e.g. 23ai, 26ai).")

    # --- compare ---
    p_compare = subparsers.add_parser(
        "compare",
        help="Side-by-side comparison of two deployment types for a version.",
    )
    p_compare.add_argument("deploy1", help="First deployment type id.")
    p_compare.add_argument("deploy2", help="Second deployment type id.")
    p_compare.add_argument("version", help="Version id.")

    # --- gaps ---
    p_gaps = subparsers.add_parser(
        "gaps",
        help="List features that are NOT_AVAIL, BROKEN, or LIMITED.",
    )
    p_gaps.add_argument("deployment", help="Deployment type id.")
    p_gaps.add_argument("version", help="Version id.")

    # --- update ---
    p_update = subparsers.add_parser(
        "update",
        help="Modify a specific cell in the matrix.",
    )
    p_update.add_argument("feature", help="Feature name (case-insensitive, partial match).")
    p_update.add_argument("deployment", help="Deployment type id.")
    p_update.add_argument("version", help="Version id.")
    p_update.add_argument("--status", required=True, help="New status value.")
    p_update.add_argument("--notes", default=None, help="Optional notes for the cell.")
    p_update.add_argument("--name", default=None, help="Contributor name for attribution.")
    p_update.add_argument("--team", default=None, help="Contributor team for attribution.")
    p_update.add_argument("--confidence", default=None, help="Confidence level: validated/observed/reported/inferred.")
    p_update.add_argument("--field-finding-ref", default=None, help="Reference to field finding ID.")

    # --- export ---
    p_export = subparsers.add_parser(
        "export",
        help="Export the full matrix as markdown or CSV.",
    )
    p_export.add_argument(
        "--format",
        required=True,
        choices=["markdown", "csv"],
        help="Output format.",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    dispatch = {
        "check": cmd_check,
        "compare": cmd_compare,
        "gaps": cmd_gaps,
        "update": cmd_update,
        "export": cmd_export,
    }

    handler = dispatch.get(args.command)
    if handler is None:
        parser.print_help()
        sys.exit(1)

    handler(args)


if __name__ == "__main__":
    main()
