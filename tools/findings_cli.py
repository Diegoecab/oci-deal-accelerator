#!/usr/bin/env python3
"""
OCI Deal Accelerator — Field Findings CLI

Search, add, update, confirm, and report on field findings tracked in
kb/field-findings/tracker.yaml.

Usage:
    python findings_cli.py list                          # List all findings
    python findings_cli.py list --severity HIGH          # Filter by severity
    python findings_cli.py list --product "ADB-S"        # Filter by product
    python findings_cli.py list --tag dep                # Filter by tag
    python findings_cli.py list --client "Pepe"          # Filter by client
    python findings_cli.py list --status open            # Filter by status
    python findings_cli.py search "maintenance window"   # Full-text search

    python findings_cli.py add --name "Name" --team "Team" --confidence validated ...
    python findings_cli.py add                           # Interactive mode

    python findings_cli.py update FF-202603-001 --status resolved --resolution "Fixed"

    python findings_cli.py confirm FF-202603-001 --name "Name" --team "Team" --note "Confirmed"

    python findings_cli.py aer                           # After-Engagement Review (interactive)

    python findings_cli.py stats                         # Summary statistics
"""

import argparse
import difflib
import json
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

TAGS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "config", "kb-tags.yaml",
)

VALID_SEVERITIES = {"CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"}
VALID_STATUSES = {"open", "resolved", "wontfix", "acknowledged", "monitoring"}
VALID_CATEGORIES = {"bug", "limitation", "undocumented", "gotcha", "workaround", "performance"}
VALID_CONFIDENCE = {"validated", "observed", "reported", "inferred"}

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


def _get_client(finding: Dict[str, Any]) -> str:
    """Get client from finding, supporting both old and new format."""
    contributor = finding.get("contributor")
    if isinstance(contributor, dict):
        return str(contributor.get("client", ""))
    return str(finding.get("client", ""))


def _get_reporter(finding: Dict[str, Any]) -> str:
    """Get reporter name, supporting both old and new format."""
    contributor = finding.get("contributor")
    if isinstance(contributor, dict):
        return str(contributor.get("name", ""))
    return str(finding.get("reported_by", ""))


# =============================================================================
# Tag validation
# =============================================================================

def _load_taxonomy() -> List[str]:
    """Load all valid tags from the taxonomy config."""
    resolved = os.path.realpath(TAGS_PATH)
    if not os.path.isfile(resolved):
        return []
    with open(resolved, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not data or "taxonomy" not in data:
        return []
    all_tags = []
    for category_tags in data["taxonomy"].values():
        if isinstance(category_tags, list):
            all_tags.extend(str(t) for t in category_tags)
    return all_tags


def validate_tags(tags: List[str], taxonomy: Optional[List[str]] = None) -> List[str]:
    """Validate tags against taxonomy. Returns list of warning messages."""
    if taxonomy is None:
        taxonomy = _load_taxonomy()
    if not taxonomy:
        return []
    warnings = []
    for tag in tags:
        if tag not in taxonomy:
            close = difflib.get_close_matches(tag, taxonomy, n=1, cutoff=0.5)
            if close:
                warnings.append(f"WARNING: Unknown tag '{tag}'. Did you mean '{close[0]}'?")
            else:
                warnings.append(f"WARNING: Unknown tag '{tag}'. Not in taxonomy.")
    return warnings


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
    return [f for f in findings if client_lower in _get_client(f).lower()]


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
        results = [f for f in results if client_lower in _get_client(f).lower()]
    if status:
        results = [f for f in results if f.get("status") == status]
    if category:
        results = [f for f in results if f.get("category") == category]
    return results


def add(
    tracker_path: str = TRACKER_PATH,
    name: str = "",
    team: str = "",
    confidence: str = "validated",
    client: str = "",
    context: str = "",
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
    reported_by: str = "",
    affects_matrix: Optional[str] = None,
) -> Dict[str, Any]:
    """Add a new finding programmatically. Returns the new entry dict.

    Supports both new contributor block (name/team/confidence) and legacy
    reported_by for backward compatibility.
    """
    data = load_tracker(tracker_path)
    findings = data.get("findings", [])

    contributor_name = name or reported_by

    contributor = {
        "name": contributor_name,
        "team": team,
        "date": date_str or date.today().isoformat(),
        "confidence": confidence if confidence in VALID_CONFIDENCE else "validated",
    }
    if client:
        contributor["client"] = client
    if context:
        contributor["context"] = context

    entry = {
        "id": _next_id(findings),
        "date": date_str or date.today().isoformat(),
        "contributor": contributor,
        "reported_by": contributor_name,
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
        "affects_matrix": affects_matrix,
        "tags": tags or [],
        "confirmations": [],
    }

    # Insert at top (newest first)
    findings.insert(0, entry)
    data["findings"] = findings
    save_tracker(data, tracker_path)
    return entry


def confirm(
    finding_id: str,
    name: str,
    team: str,
    note: str = "",
    tracker_path: str = TRACKER_PATH,
) -> Dict[str, Any]:
    """Add a confirmation to an existing finding. Returns the confirmation dict."""
    data = load_tracker(tracker_path)
    findings = data.get("findings", [])

    target = None
    for f in findings:
        if f["id"] == finding_id:
            target = f
            break

    if target is None:
        raise LookupError(f"Finding '{finding_id}' not found.")

    confirmation = {
        "name": name,
        "team": team,
        "date": date.today().isoformat(),
    }
    if note:
        confirmation["note"] = note

    if "confirmations" not in target:
        target["confirmations"] = []
    target["confirmations"].append(confirmation)

    save_tracker(data, tracker_path)
    return confirmation


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

    if getattr(args, "json_output", False):
        print(json.dumps(results, indent=2, default=str))
        return

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

    # Apply optional filters (mirrors list subcommand)
    results = filter_findings(
        results,
        severity=getattr(args, "severity", None),
        product=getattr(args, "product", None),
        tag=getattr(args, "tag", None),
        client=getattr(args, "client", None),
        status=getattr(args, "status", None),
        category=getattr(args, "category", None),
    )

    if getattr(args, "json_output", False):
        print(json.dumps(results, indent=2, default=str))
        return

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
        # Validate tags
        tag_warnings = validate_tags(tags_list)
        for w in tag_warnings:
            print(w, file=sys.stderr)
        entry = add(
            name=args.name or args.reported_by or "",
            team=args.team or "",
            confidence=args.confidence or "validated",
            client=args.client or "",
            context=args.context or "",
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
            affects_matrix=args.affects_matrix or None,
        )
    else:
        # Interactive mode
        print("Add new field finding (press Enter to skip optional fields):\n")
        contributor_name = input("Your name: ").strip()
        contributor_team = input("Your team: ").strip()
        contributor_client = input("Client (optional, press Enter to skip): ").strip()
        contributor_context = input("Context (optional): ").strip()
        confidence = input("Confidence [validated/observed/reported/inferred]: ").strip() or "validated"
        tags_str = input("Tags (comma-separated): ").strip()
        tags_list = [t.strip() for t in tags_str.split(",") if t.strip()]
        tag_warnings = validate_tags(tags_list)
        for w in tag_warnings:
            print(w)
        entry = add(
            date_str=input("Date [today]: ").strip() or None,
            name=contributor_name,
            team=contributor_team,
            client=contributor_client,
            context=contributor_context,
            confidence=confidence,
            product=input("Product: ").strip(),
            version=input("Version: ").strip(),
            severity=input("Severity (CRITICAL/HIGH/MEDIUM/LOW/INFO) [MEDIUM]: ").strip() or "MEDIUM",
            category=input("Category (bug/limitation/undocumented/gotcha/workaround/performance) [gotcha]: ").strip() or "gotcha",
            summary=input("Summary (one line): ").strip(),
            detail=input("Detail: ").strip(),
            workaround=input("Workaround: ").strip(),
            tags=tags_list,
            oracle_sr=input("Oracle SR#: ").strip(),
            affects_matrix=input("Affects matrix entry (feature name, or blank): ").strip() or None,
        )

    print(f"\nAdded: {entry['id']}  [{entry['severity']}]  {entry['summary']}")


def cmd_confirm(args: argparse.Namespace) -> None:
    """Add a confirmation to an existing finding."""
    try:
        confirmation = confirm(
            finding_id=args.finding_id,
            name=args.name,
            team=args.team,
            note=args.note or "",
        )
        print(f"Confirmed {args.finding_id}:")
        print(f"  by: {confirmation['name']} ({confirmation.get('team', '')})")
        if confirmation.get("note"):
            print(f"  note: {confirmation['note']}")
    except LookupError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_aer(args: argparse.Namespace) -> None:
    """After-Engagement Review — interactive post-engagement knowledge capture."""
    print("After-Engagement Review")
    print("=" * 23)

    client = input("Client: ").strip()
    architect = input("Architect: ").strip()
    team = input("Team: ").strip() or "Field Architecture"
    print()

    q1 = input("1. What did we learn that the KB doesn't cover?\n   > ").strip()
    print()
    q2 = input("2. What went wrong that others should know about?\n   > ").strip()
    print()
    q3 = input("3. What worked well that we should capture as a pattern?\n   > ").strip()
    print()

    print("Saving...")
    created = []

    # Create finding from Q2 (what went wrong) if provided
    if q2:
        entry = add(
            name=architect,
            team=team,
            client=client,
            context="After-Engagement Review",
            confidence="observed",
            product=input("Product for issue (Q2): ").strip() or "General",
            severity=input("Severity for issue (CRITICAL/HIGH/MEDIUM/LOW/INFO) [MEDIUM]: ").strip() or "MEDIUM",
            category="gotcha",
            summary=q2[:120],
            detail=q2,
        )
        created.append(f"  -> Created finding {entry['id']} ({q2[:60]})")

    # Create finding from Q1 (KB gap) if provided
    if q1:
        entry = add(
            name=architect,
            team=team,
            client=client,
            context="After-Engagement Review",
            confidence="observed",
            product=input("Product for KB gap (Q1): ").strip() or "General",
            severity="INFO",
            category="undocumented",
            summary=f"KB gap: {q1[:110]}",
            detail=q1,
        )
        created.append(f"  -> Created finding {entry['id']} (KB gap: {q1[:50]})")

    if q3:
        created.append(f"  -> Pattern suggestion noted: {q3[:60]}...")
        created.append(f"     (Create manually: kb/patterns/<name>.yaml)")

    if created:
        for line in created:
            print(line)
    else:
        print("  No items to create. Review complete.")


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

    if getattr(args, "json_output", False):
        print(json.dumps(s, indent=2))
        return

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
    p_list.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON.")

    # --- search ---
    p_search = subparsers.add_parser("search", help="Full-text search.")
    p_search.add_argument("query", help="Search term.")
    p_search.add_argument("--severity", help="Filter by severity.")
    p_search.add_argument("--product", help="Filter by product (partial match).")
    p_search.add_argument("--tag", help="Filter by tag.")
    p_search.add_argument("--client", help="Filter by client (partial match).")
    p_search.add_argument("--status", help="Filter by status.")
    p_search.add_argument("--category", help="Filter by category.")
    p_search.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON.")

    # --- add ---
    p_add = subparsers.add_parser("add", help="Add a new finding.")
    p_add.add_argument("--date", default=None, help="Date (YYYY-MM-DD). Defaults to today.")
    p_add.add_argument("--name", help="Contributor name.")
    p_add.add_argument("--team", help="Contributor team.")
    p_add.add_argument("--confidence", help="Confidence level: validated/observed/reported/inferred.")
    p_add.add_argument("--context", help="Engagement context (PoC, migration, assessment).")
    p_add.add_argument("--reported-by", help="(Legacy) Who reported the finding. Use --name instead.")
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
    p_add.add_argument("--affects-matrix", help="Feature matrix entry this relates to.")

    # --- update ---
    p_update = subparsers.add_parser("update", help="Update an existing finding.")
    p_update.add_argument("finding_id", help="Finding ID (e.g., FF-202603-001).")
    p_update.add_argument("--status", help="New status.")
    p_update.add_argument("--resolution", help="Resolution description.")
    p_update.add_argument("--resolved-date", help="Resolved date (YYYY-MM-DD).")
    p_update.add_argument("--workaround", help="Updated workaround.")
    p_update.add_argument("--oracle-sr", help="Oracle SR number.")

    # --- confirm ---
    p_confirm = subparsers.add_parser("confirm", help="Add a confirmation to an existing finding.")
    p_confirm.add_argument("finding_id", help="Finding ID to confirm (e.g., FF-202603-001).")
    p_confirm.add_argument("--name", required=True, help="Your name.")
    p_confirm.add_argument("--team", required=True, help="Your team.")
    p_confirm.add_argument("--note", help="Confirmation note.")

    # --- aer ---
    subparsers.add_parser("aer", help="After-Engagement Review (interactive).")

    # --- stats ---
    p_stats = subparsers.add_parser("stats", help="Show summary statistics.")
    p_stats.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON.")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    dispatch = {
        "list": cmd_list,
        "search": cmd_search,
        "add": cmd_add,
        "update": cmd_update,
        "confirm": cmd_confirm,
        "aer": cmd_aer,
        "stats": cmd_stats,
    }

    handler = dispatch.get(args.command)
    if handler is None:
        parser.print_help()
        sys.exit(1)

    handler(args)


if __name__ == "__main__":
    main()
