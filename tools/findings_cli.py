#!/usr/bin/env python3
"""
OCI Deal Accelerator — Field Findings CLI

Search, add, update, and report on field findings tracked in
kb/field-findings/tracker.yaml.

Usage:
    python findings_cli.py list                          # List all findings
    python findings_cli.py list --severity HIGH          # Filter by severity
    python findings_cli.py list --product "ADB-S"        # Filter by product
    python findings_cli.py list --tag dep                # Filter by tag
    python findings_cli.py list --client "Pepe"          # Filter by client
    python findings_cli.py list --status open            # Filter by status
    python findings_cli.py search "maintenance window"   # Full-text search

    python findings_cli.py add --reported-by "Name" --client "Client" ...
    python findings_cli.py add                           # Interactive mode

    python findings_cli.py update FF-202603-001 --status resolved --resolution "Fixed"

    python findings_cli.py stats                         # Summary statistics
"""

import argparse
import os
import sys
from collections import Counter
from datetime import date, datetime
from typing import Any, Dict, List, Optional

import yaml


# =============================================================================
# Constants
# =============================================================================

TRACKER_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "kb", "field-findings", "tracker.yaml",
)

VALID_SEVERITIES = {"CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"}
VALID_STATUSES = {"open", "resolved", "wontfix", "acknowledged", "monitoring"}
VALID_CATEGORIES = {"bug", "limitation", "undocumented", "gotcha", "workaround", "performance"}

# ANSI colors
_SEV_COLORS = {
    "CRITICAL": "\033[1;31m",  # red bold
    "HIGH":     "\033[31m",    # red
    "MEDIUM":   "\033[33m",    # yellow
    "LOW":      "\033[36m",    # cyan
    "INFO":     "\033[37m",    # white
}
_RESET = "\033[0m"


# =============================================================================
# Data helpers
# =============================================================================

def load_tracker(path: str = TRACKER_PATH) -> Dict[str, Any]:
    """Load the tracker YAML and return the full dict."""
    resolved = os.path.realpath(path)
    if not os.path.isfile(resolved):
        print(f"Error: Tracker file not found at {resolved}", file=sys.stderr)
        sys.exit(1)
    with open(resolved, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not data or "findings" not in data:
        print("Error: Tracker file missing 'findings' key.", file=sys.stderr)
        sys.exit(1)
    return data


def save_tracker(data: Dict[str, Any], path: str = TRACKER_PATH) -> None:
    """Write tracker data back to YAML."""
    resolved = os.path.realpath(path)
    data["last_updated"] = date.today().isoformat()
    with open(resolved, "w", encoding="utf-8") as fh:
        yaml.dump(
            data,
            fh,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
            width=120,
        )


def _get_findings(path: str = TRACKER_PATH) -> List[Dict[str, Any]]:
    """Return the findings list from the tracker."""
    return load_tracker(path).get("findings", [])


def _next_id(findings: List[Dict[str, Any]]) -> str:
    """Generate the next FF-YYYYMM-NNN id."""
    prefix = f"FF-{date.today().strftime('%Y%m')}-"
    existing = [
        int(f["id"].split("-")[-1])
        for f in findings
        if f["id"].startswith(prefix)
    ]
    next_num = max(existing, default=0) + 1
    return f"{prefix}{next_num:03d}"


def _sev_color(severity: str) -> str:
    """Wrap severity with ANSI color if terminal supports it."""
    if not (hasattr(sys.stdout, "isatty") and sys.stdout.isatty()):
        return severity
    code = _SEV_COLORS.get(severity, "")
    return f"{code}{severity}{_RESET}" if code else severity


# =============================================================================
# Library API — importable functions for programmatic use and testing
# =============================================================================

def search(query: str, tracker_path: str = TRACKER_PATH) -> List[Dict[str, Any]]:
    """Full-text search across summary, detail, workaround, and tags."""
    findings = _get_findings(tracker_path)
    query_lower = query.lower()
    results = []
    for f in findings:
        searchable = " ".join([
            str(f.get("summary", "")),
            str(f.get("detail", "")),
            str(f.get("workaround", "")),
            " ".join(str(t) for t in f.get("tags", [])),
        ]).lower()
        if query_lower in searchable:
            results.append(f)
    return results


def filter_by_severity(severity: str, tracker_path: str = TRACKER_PATH) -> List[Dict[str, Any]]:
    """Return findings matching the given severity."""
    findings = _get_findings(tracker_path)
    return [f for f in findings if f.get("severity") == severity]


def filter_by_client(client: str, tracker_path: str = TRACKER_PATH) -> List[Dict[str, Any]]:
    """Return findings whose client field contains the query string."""
    findings = _get_findings(tracker_path)
    client_lower = client.lower()
    return [f for f in findings if client_lower in str(f.get("client", "")).lower()]


def filter_findings(
    findings: List[Dict[str, Any]],
    severity: Optional[str] = None,
    product: Optional[str] = None,
    tag: Optional[str] = None,
    client: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Apply multiple filters to a findings list."""
    results = findings
    if severity:
        results = [f for f in results if f.get("severity") == severity.upper()]
    if product:
        product_lower = product.lower()
        results = [f for f in results if product_lower in str(f.get("product", "")).lower()]
    if tag:
        tag_lower = tag.lower()
        results = [f for f in results if tag_lower in [str(t).lower() for t in f.get("tags", [])]]
    if client:
        client_lower = client.lower()
        results = [f for f in results if client_lower in str(f.get("client", "")).lower()]
    if status:
        results = [f for f in results if f.get("status") == status]
    if category:
        results = [f for f in results if f.get("category") == category]
    return results


def add(
    tracker_path: str = TRACKER_PATH,
    reported_by: str = "",
    client: str = "",
    product: str = "",
    version: str = "",
    severity: str = "MEDIUM",
    category: str = "gotcha",
    summary: str = "",
    detail: str = "",
    workaround: str = "",
    tags: Optional[List[str]] = None,
    status: str = "open",
    date_str: Optional[str] = None,
    oracle_sr: str = "",
) -> Dict[str, Any]:
    """Add a new finding programmatically. Returns the new entry dict."""
    data = load_tracker(tracker_path)
    findings = data.get("findings", [])

    entry = {
        "id": _next_id(findings),
        "date": date_str or date.today().isoformat(),
        "reported_by": reported_by,
        "client": client,
        "product": product,
        "version": version,
        "severity": severity.upper(),
        "category": category,
        "summary": summary,
        "detail": detail,
        "workaround": workaround,
        "oracle_sr": oracle_sr,
        "status": status,
        "resolved_date": None,
        "resolution": None,
        "affects_matrix": None,
        "tags": tags or [],
    }

    # Insert at top (newest first)
    findings.insert(0, entry)
    data["findings"] = findings
    save_tracker(data, tracker_path)
    return entry


def stats(tracker_path: str = TRACKER_PATH) -> Dict[str, Any]:
    """Return summary statistics about findings."""
    findings = _get_findings(tracker_path)
    return {
        "total": len(findings),
        "by_severity": dict(Counter(f.get("severity", "UNKNOWN") for f in findings)),
        "by_product": dict(Counter(f.get("product", "UNKNOWN") for f in findings)),
        "by_status": dict(Counter(f.get("status", "unknown") for f in findings)),
        "by_category": dict(Counter(f.get("category", "unknown") for f in findings)),
    }


# =============================================================================
# CLI subcommands
# =============================================================================

def cmd_list(args: argparse.Namespace) -> None:
    """List findings with optional filters."""
    data = load_tracker(TRACKER_PATH)
    findings = data.get("findings", [])

    results = filter_findings(
        findings,
        severity=args.severity,
        product=args.product,
        tag=args.tag,
        client=args.client,
        status=args.status,
        category=getattr(args, "category", None),
    )

    if not results:
        print("No findings match the given filters.")
        return

    # Table output
    id_w, date_w, sev_w, prod_w = 16, 12, 10, 30
    header = f"{'ID':<{id_w}} {'Date':<{date_w}} {'Severity':<{sev_w}} {'Product':<{prod_w}} Summary"
    print(header)
    print("-" * len(header))

    for f in results:
        fid = f.get("id", "?")
        fdate = str(f.get("date", "?"))
        sev = f.get("severity", "?")
        prod = str(f.get("product", "?"))[:prod_w]
        summary = str(f.get("summary", ""))[:60]
        print(f"{fid:<{id_w}} {fdate:<{date_w}} {_sev_color(sev):<{sev_w}} {prod:<{prod_w}} {summary}")


def cmd_search(args: argparse.Namespace) -> None:
    """Full-text search."""
    results = search(args.query)

    if not results:
        print(f"No findings matching '{args.query}'.")
        return

    print(f"Found {len(results)} finding(s) matching '{args.query}':\n")
    for f in results:
        sev = f.get("severity", "?")
        print(f"  {f['id']}  [{_sev_color(sev)}]  {f.get('summary', '')}")


def cmd_add(args: argparse.Namespace) -> None:
    """Add a new finding."""
    if args.summary:
        # Non-interactive mode
        tags_list = [t.strip() for t in args.tags.split(",")] if args.tags else []
        entry = add(
            reported_by=args.reported_by or "",
            client=args.client or "",
            product=args.product or "",
            version=args.version or "",
            severity=args.severity or "MEDIUM",
            category=args.category or "gotcha",
            summary=args.summary,
            detail=args.detail or "",
            workaround=args.workaround or "",
            tags=tags_list,
            date_str=args.date,
            oracle_sr=args.oracle_sr or "",
        )
    else:
        # Interactive mode
        print("Add new field finding (press Enter to skip optional fields):\n")
        entry = add(
            date_str=input("Date [today]: ").strip() or None,
            reported_by=input("Reported by: ").strip(),
            client=input("Client: ").strip(),
            product=input("Product: ").strip(),
            version=input("Version: ").strip(),
            severity=input("Severity (CRITICAL/HIGH/MEDIUM/LOW/INFO) [MEDIUM]: ").strip() or "MEDIUM",
            category=input("Category (bug/limitation/undocumented/gotcha/workaround/performance) [gotcha]: ").strip() or "gotcha",
            summary=input("Summary (one line): ").strip(),
            detail=input("Detail: ").strip(),
            workaround=input("Workaround: ").strip(),
            tags=[t.strip() for t in input("Tags (comma-separated): ").strip().split(",") if t.strip()],
            oracle_sr=input("Oracle SR#: ").strip(),
        )

    print(f"\nAdded: {entry['id']}  [{entry['severity']}]  {entry['summary']}")


def cmd_update(args: argparse.Namespace) -> None:
    """Update an existing finding."""
    data = load_tracker(TRACKER_PATH)
    findings = data.get("findings", [])

    target = None
    for f in findings:
        if f["id"] == args.finding_id:
            target = f
            break

    if target is None:
        print(f"Error: Finding '{args.finding_id}' not found.", file=sys.stderr)
        sys.exit(1)

    updated_fields = []
    if args.status:
        target["status"] = args.status
        updated_fields.append(f"status -> {args.status}")
    if args.resolution:
        target["resolution"] = args.resolution
        updated_fields.append(f"resolution -> {args.resolution}")
    if args.resolved_date:
        target["resolved_date"] = args.resolved_date
        updated_fields.append(f"resolved_date -> {args.resolved_date}")
    if args.workaround:
        target["workaround"] = args.workaround
        updated_fields.append("workaround updated")
    if args.oracle_sr:
        target["oracle_sr"] = args.oracle_sr
        updated_fields.append(f"oracle_sr -> {args.oracle_sr}")

    if not updated_fields:
        print("No fields to update. Use --status, --resolution, --resolved-date, --workaround, or --oracle-sr.")
        return

    save_tracker(data, TRACKER_PATH)
    print(f"Updated {args.finding_id}:")
    for field in updated_fields:
        print(f"  {field}")


def cmd_stats(args: argparse.Namespace) -> None:
    """Display summary statistics."""
    s = stats()

    print(f"Total findings: {s['total']}\n")

    print("By Severity:")
    for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
        count = s["by_severity"].get(sev, 0)
        if count:
            print(f"  {_sev_color(sev):<10} {count}")

    print("\nBy Status:")
    for status, count in sorted(s["by_status"].items()):
        print(f"  {status:<15} {count}")

    print("\nBy Product:")
    for product, count in sorted(s["by_product"].items(), key=lambda x: -x[1]):
        print(f"  {product:<35} {count}")

    print("\nBy Category:")
    for cat, count in sorted(s["by_category"].items(), key=lambda x: -x[1]):
        print(f"  {cat:<15} {count}")


# =============================================================================
# CLI entry point
# =============================================================================

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="findings_cli",
        description="Manage the Field Findings Tracker.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- list ---
    p_list = subparsers.add_parser("list", help="List findings with optional filters.")
    p_list.add_argument("--severity", help="Filter by severity.")
    p_list.add_argument("--product", help="Filter by product (partial match).")
    p_list.add_argument("--tag", help="Filter by tag.")
    p_list.add_argument("--client", help="Filter by client (partial match).")
    p_list.add_argument("--status", help="Filter by status.")
    p_list.add_argument("--category", help="Filter by category.")

    # --- search ---
    p_search = subparsers.add_parser("search", help="Full-text search.")
    p_search.add_argument("query", help="Search term.")

    # --- add ---
    p_add = subparsers.add_parser("add", help="Add a new finding.")
    p_add.add_argument("--date", default=None, help="Date (YYYY-MM-DD). Defaults to today.")
    p_add.add_argument("--reported-by", help="Who reported the finding.")
    p_add.add_argument("--client", help="Client name or reference.")
    p_add.add_argument("--product", help="OCI product/service affected.")
    p_add.add_argument("--version", help="Product version.")
    p_add.add_argument("--severity", help="CRITICAL/HIGH/MEDIUM/LOW/INFO.")
    p_add.add_argument("--category", help="bug/limitation/undocumented/gotcha/workaround/performance.")
    p_add.add_argument("--summary", help="One-line summary.")
    p_add.add_argument("--detail", help="Full description.")
    p_add.add_argument("--workaround", help="Known workaround.")
    p_add.add_argument("--tags", help="Comma-separated tags.")
    p_add.add_argument("--oracle-sr", help="Oracle SR number.")

    # --- update ---
    p_update = subparsers.add_parser("update", help="Update an existing finding.")
    p_update.add_argument("finding_id", help="Finding ID (e.g., FF-202603-001).")
    p_update.add_argument("--status", help="New status.")
    p_update.add_argument("--resolution", help="Resolution description.")
    p_update.add_argument("--resolved-date", help="Resolved date (YYYY-MM-DD).")
    p_update.add_argument("--workaround", help="Updated workaround.")
    p_update.add_argument("--oracle-sr", help="Oracle SR number.")

    # --- stats ---
    subparsers.add_parser("stats", help="Show summary statistics.")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    dispatch = {
        "list": cmd_list,
        "search": cmd_search,
        "add": cmd_add,
        "update": cmd_update,
        "stats": cmd_stats,
    }

    handler = dispatch.get(args.command)
    if handler is None:
        parser.print_help()
        sys.exit(1)

    handler(args)


if __name__ == "__main__":
    main()
