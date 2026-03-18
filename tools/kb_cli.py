#!/usr/bin/env python3
"""
OCI Deal Accelerator — Unified KB Management CLI

Provides a single entry point for KB management tasks:
  - Health dashboard
  - Contribution stats and leaderboard
  - Stale content reporting
  - Confidence decay reporting
  - Changelog management for service files
  - Cross-KB search
  - Domain owner listing

Usage:
    python kb_cli.py health                          # Overall KB health dashboard
    python kb_cli.py stats contributors              # Contribution leaderboard
    python kb_cli.py stats stale                     # Stale content report
    python kb_cli.py stats decay                     # Confidence decay report
    python kb_cli.py changelog <file> --name "Name" --team "Team" --change "Description"
    python kb_cli.py search "vector search"          # Search across ALL KB files
    python kb_cli.py owners                          # Show domain owners
"""

import argparse
import os
import re
import sys
from collections import Counter
from datetime import date, datetime
from typing import Any, Dict, List, Optional

import yaml

# =============================================================================
# Constants
# =============================================================================

PROJECT_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
KB_ROOT = os.path.join(PROJECT_ROOT, "kb")
GOVERNANCE_PATH = os.path.join(PROJECT_ROOT, "config", "kb-governance.yaml")
OWNERS_PATH = os.path.join(PROJECT_ROOT, "config", "kb-owners.yaml")
TRACKER_PATH = os.path.join(PROJECT_ROOT, "kb", "field-findings", "tracker.yaml")
MATRIX_PATH = os.path.join(PROJECT_ROOT, "kb", "compatibility", "adb-feature-matrix.yaml")

_RESET = "\033[0m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_RED = "\033[31m"
_BOLD = "\033[1m"
_CYAN = "\033[36m"


def _supports_color() -> bool:
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _c(text: str, color: str) -> str:
    if not _supports_color():
        return text
    return f"{color}{text}{_RESET}"


# =============================================================================
# Loaders
# =============================================================================

def _load_yaml(path: str) -> Optional[Dict[str, Any]]:
    resolved = os.path.realpath(path)
    if not os.path.isfile(resolved):
        return None
    with open(resolved, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _parse_date(d: Any) -> Optional[date]:
    if isinstance(d, date) and not isinstance(d, datetime):
        return d
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, str):
        try:
            return datetime.strptime(d, "%Y-%m-%d").date()
        except ValueError:
            pass
        # Try YYYY-MM format
        try:
            return datetime.strptime(d + "-01", "%Y-%m-%d").date()
        except ValueError:
            return None
    return None


def _days_ago(d: Any) -> Optional[int]:
    parsed = _parse_date(d)
    if parsed is None:
        return None
    return (date.today() - parsed).days


def _all_kb_files() -> List[str]:
    """Return all YAML files under kb/."""
    files = []
    for dirpath, _dirnames, filenames in os.walk(KB_ROOT):
        for filename in filenames:
            if filename.endswith((".yaml", ".yml")):
                files.append(os.path.join(dirpath, filename))
    return sorted(files)


# =============================================================================
# Health dashboard
# =============================================================================

def cmd_health(args: argparse.Namespace) -> None:
    """Overall KB health dashboard."""
    governance = _load_yaml(GOVERNANCE_PATH) or {}
    warning_days = governance.get("freshness", {}).get("warning_days", 180)
    stale_days = governance.get("freshness", {}).get("stale_days", 365)
    decay_config = governance.get("confidence_decay", {})

    # File freshness
    kb_files = _all_kb_files()
    fresh_count = stale_count = expired_count = 0
    stale_files = []

    for filepath in kb_files:
        data = _load_yaml(filepath)
        rel = os.path.relpath(filepath, PROJECT_ROOT)
        last = None
        if data:
            last = data.get("last_verified") or data.get("last_updated")
        age = _days_ago(last) if last else None
        if age is None:
            mtime = os.path.getmtime(filepath)
            mdate = datetime.fromtimestamp(mtime).date()
            age = (date.today() - mdate).days
        if age > stale_days:
            expired_count += 1
            stale_files.append((rel, age, "expired"))
        elif age > warning_days:
            stale_count += 1
            stale_files.append((rel, age, "stale"))
        else:
            fresh_count += 1

    # Findings stats
    tracker = _load_yaml(TRACKER_PATH) or {}
    findings = tracker.get("findings", [])
    status_counts = Counter(f.get("status", "unknown") for f in findings)

    # Feature matrix stats
    matrix = _load_yaml(MATRIX_PATH) or {}
    features = matrix.get("features", [])
    cell_counts: Dict[str, int] = Counter()
    for feat in features:
        for deploy_versions in feat.get("matrix", {}).values():
            for ver_data in deploy_versions.values():
                if isinstance(ver_data, dict):
                    cell_counts[ver_data.get("status", "UNTESTED")] += 1

    # Contributor stats (last 90 days)
    contributor_counts: Dict[str, int] = Counter()
    for f in findings:
        contrib = f.get("contributor", {})
        if isinstance(contrib, dict):
            name = contrib.get("name", "Unknown")
            cdate = _parse_date(contrib.get("date", f.get("date")))
            if cdate and (date.today() - cdate).days <= 90:
                contributor_counts[name] += 1
        for c in f.get("confirmations", []):
            cdate = _parse_date(c.get("date"))
            if cdate and (date.today() - cdate).days <= 90:
                contributor_counts[c.get("name", "Unknown")] += 1

    # Owner check
    owners = _load_yaml(OWNERS_PATH) or {}
    unassigned = []
    for domain in owners.get("domains", []):
        if domain.get("owner", {}).get("name") == "TBD":
            unassigned.append(domain.get("area", ""))

    # Print dashboard
    total_files = len(kb_files)
    print(_c("KB HEALTH DASHBOARD", _BOLD))
    print("=" * 50)
    print()
    print(f"Files: {total_files} total | {_c(str(fresh_count), _GREEN)} fresh | "
          f"{_c(str(stale_count), _YELLOW)} stale | {_c(str(expired_count), _RED)} expired")
    print()
    print(f"Findings: {len(findings)} total | "
          f"{status_counts.get('open', 0)} open | "
          f"{status_counts.get('acknowledged', 0)} acknowledged | "
          f"{status_counts.get('resolved', 0)} resolved | "
          f"{status_counts.get('monitoring', 0)} monitoring")
    print()

    if cell_counts:
        parts = []
        for status in ["GA", "GA_CAVEAT", "LIMITED", "NOT_AVAIL", "UNTESTED"]:
            if cell_counts.get(status, 0) > 0:
                parts.append(f"{status}: {cell_counts[status]}")
        print(f"Feature Matrix: {len(features)} features")
        print(f"  {' | '.join(parts)}")
        print()

    if contributor_counts:
        print("Contributors (last 90 days):")
        for name, count in contributor_counts.most_common(10):
            print(f"  {name:<30} {count} contributions")
        print()

    needs_attention = []
    for filepath, age, status in stale_files:
        needs_attention.append(f"  {filepath} -- {status} ({age} days old)")
    untested = cell_counts.get("UNTESTED", 0)
    if untested > 0:
        needs_attention.append(f"  {untested} UNTESTED cells in feature matrix")
    for area in unassigned:
        needs_attention.append(f"  {area} -- no owner assigned")

    if needs_attention:
        print("Needs Attention:")
        for item in needs_attention:
            print(item)
    else:
        print(_c("All areas healthy.", _GREEN))


# =============================================================================
# Stats commands
# =============================================================================

def cmd_stats_contributors(args: argparse.Namespace) -> None:
    """Show contribution leaderboard."""
    tracker = _load_yaml(TRACKER_PATH) or {}
    findings = tracker.get("findings", [])

    # Count findings per contributor
    finding_counts: Dict[str, Dict[str, int]] = {}
    for f in findings:
        contrib = f.get("contributor", {})
        if isinstance(contrib, dict):
            name = contrib.get("name", "Unknown")
            team = contrib.get("team", "")
        else:
            name = str(f.get("reported_by", "Unknown"))
            team = ""
        key = f"{name}|{team}"
        if key not in finding_counts:
            finding_counts[key] = {"findings": 0, "confirmations": 0, "team": team}
        finding_counts[key]["findings"] += 1

        for c in f.get("confirmations", []):
            cname = c.get("name", "Unknown")
            cteam = c.get("team", "")
            ckey = f"{cname}|{cteam}"
            if ckey not in finding_counts:
                finding_counts[ckey] = {"findings": 0, "confirmations": 0, "team": cteam}
            finding_counts[ckey]["confirmations"] += 1

    if not finding_counts:
        print("No contributions found.")
        return

    print(f"{'Contributor':<25} {'Team':<25} {'Findings':>8} {'Confirms':>8} {'Total':>8}")
    print("-" * 80)
    for key, counts in sorted(finding_counts.items(), key=lambda x: -(x[1]["findings"] + x[1]["confirmations"])):
        name = key.split("|")[0]
        total = counts["findings"] + counts["confirmations"]
        print(f"{name:<25} {counts['team']:<25} {counts['findings']:>8} {counts['confirmations']:>8} {total:>8}")


def cmd_stats_stale(args: argparse.Namespace) -> None:
    """Show stale content report."""
    governance = _load_yaml(GOVERNANCE_PATH) or {}
    warning_days = governance.get("freshness", {}).get("warning_days", 180)
    stale_days = governance.get("freshness", {}).get("stale_days", 365)

    kb_files = _all_kb_files()
    stale = []
    for filepath in kb_files:
        data = _load_yaml(filepath)
        rel = os.path.relpath(filepath, PROJECT_ROOT)
        last = None
        if data:
            last = data.get("last_verified") or data.get("last_updated")
        age = _days_ago(last) if last else None
        if age is None:
            mtime = os.path.getmtime(filepath)
            mdate = datetime.fromtimestamp(mtime).date()
            age = (date.today() - mdate).days
        if age > warning_days:
            status = "STALE" if age > stale_days else "WARNING"
            stale.append((rel, age, status))

    if not stale:
        print(_c("No stale content found.", _GREEN))
        return

    print(f"{'File':<50} {'Age':>8} {'Status':>10}")
    print("-" * 70)
    for filepath, age, status in sorted(stale, key=lambda x: -x[1]):
        sc = _RED if status == "STALE" else _YELLOW
        print(f"{filepath:<50} {age:>5}d   {_c(status, sc)}")


def cmd_stats_decay(args: argparse.Namespace) -> None:
    """Show confidence decay report."""
    governance = _load_yaml(GOVERNANCE_PATH) or {}
    decay_config = governance.get("confidence_decay", {})
    tracker = _load_yaml(TRACKER_PATH) or {}
    findings = tracker.get("findings", [])

    if not findings:
        print("No findings found.")
        return

    print(f"{'ID':<18} {'Status':<10} {'Summary':<45} {'Confidence':<12} {'Age'}")
    print("-" * 100)

    for f in findings:
        fid = f.get("id", "???")
        contributor = f.get("contributor", {})
        confidence = contributor.get("confidence", "validated") if isinstance(contributor, dict) else "validated"
        finding_date = contributor.get("date", f.get("date")) if isinstance(contributor, dict) else f.get("date")
        age = _days_ago(finding_date)
        summary = str(f.get("summary", ""))[:43]

        if age is None:
            status = "UNKNOWN"
        else:
            thresholds = decay_config.get(confidence, {"fresh": 180, "stale": 365, "expired": 730})
            if age <= thresholds.get("fresh", 180):
                status = "FRESH"
            elif age <= thresholds.get("stale", 365):
                status = "STALE"
            else:
                status = "EXPIRED"

        color = _GREEN if status == "FRESH" else (_YELLOW if status == "STALE" else _RED)
        age_str = f"{age}d" if age is not None else "?"
        print(f"{fid:<18} {_c(status, color):<10} {summary:<45} {confidence:<12} {age_str}")


# =============================================================================
# Changelog command
# =============================================================================

def cmd_changelog(args: argparse.Namespace) -> None:
    """Add a changelog entry to a KB file."""
    filepath = os.path.realpath(args.file)
    if not os.path.isfile(filepath):
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)

    if data is None:
        data = {}

    if "changelog" not in data:
        data["changelog"] = []

    entry = {
        "date": date.today().isoformat(),
        "contributor": {"name": args.name, "team": args.team},
        "change": args.change,
    }
    data["changelog"].append(entry)

    with open(filepath, "w", encoding="utf-8") as fh:
        yaml.dump(data, fh, default_flow_style=False, sort_keys=False, allow_unicode=True, width=120)

    rel = os.path.relpath(filepath, PROJECT_ROOT)
    print(f"Added changelog entry to {rel}:")
    print(f"  date: {entry['date']}")
    print(f"  contributor: {args.name} ({args.team})")
    print(f"  change: {args.change}")


# =============================================================================
# Search command
# =============================================================================

def cmd_search(args: argparse.Namespace) -> None:
    """Search across ALL KB files."""
    query = args.query.lower()
    kb_files = _all_kb_files()
    results = []

    for filepath in kb_files:
        with open(filepath, "r", encoding="utf-8") as fh:
            content = fh.read()
        if query in content.lower():
            rel = os.path.relpath(filepath, PROJECT_ROOT)
            # Find matching lines
            matches = []
            for i, line in enumerate(content.splitlines(), 1):
                if query in line.lower():
                    matches.append((i, line.strip()[:80]))
            results.append((rel, matches))

    if not results:
        print(f"No results for '{args.query}'.")
        return

    print(f"Found matches in {len(results)} file(s) for '{args.query}':\n")
    for filepath, matches in results:
        print(f"  {_c(filepath, _CYAN)}")
        for lineno, text in matches[:3]:
            print(f"    L{lineno}: {text}")
        if len(matches) > 3:
            print(f"    ... and {len(matches) - 3} more match(es)")
        print()


# =============================================================================
# Owners command
# =============================================================================

def cmd_owners(args: argparse.Namespace) -> None:
    """Show domain owners."""
    owners = _load_yaml(OWNERS_PATH)
    if not owners or "domains" not in owners:
        print("No owners configuration found.")
        return

    print(f"{'Area':<30} {'Owner':<25} {'Team':<25} {'Review Cadence'}")
    print("-" * 100)
    for domain in owners["domains"]:
        area = domain.get("area", "")
        owner = domain.get("owner", {})
        name = owner.get("name", "TBD")
        team = owner.get("team", "")
        cadence = domain.get("review_cadence", "")
        name_display = _c(name, _RED) if name == "TBD" else name
        print(f"{area:<30} {name_display:<25} {team:<25} {cadence}")


# =============================================================================
# CLI entry point
# =============================================================================

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kb_cli",
        description="Unified KB management CLI.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- health ---
    subparsers.add_parser("health", help="Overall KB health dashboard.")

    # --- stats ---
    p_stats = subparsers.add_parser("stats", help="KB statistics.")
    stats_sub = p_stats.add_subparsers(dest="stats_type", required=True)
    stats_sub.add_parser("contributors", help="Contribution leaderboard.")
    stats_sub.add_parser("stale", help="Stale content report.")
    stats_sub.add_parser("decay", help="Confidence decay report.")

    # --- changelog ---
    p_changelog = subparsers.add_parser("changelog", help="Add changelog entry to a KB file.")
    p_changelog.add_argument("file", help="Path to the KB YAML file.")
    p_changelog.add_argument("--name", required=True, help="Contributor name.")
    p_changelog.add_argument("--team", required=True, help="Contributor team.")
    p_changelog.add_argument("--change", required=True, help="Description of the change.")

    # --- search ---
    p_search = subparsers.add_parser("search", help="Search across all KB files.")
    p_search.add_argument("query", help="Search term.")

    # --- owners ---
    subparsers.add_parser("owners", help="Show domain owners.")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "health":
        cmd_health(args)
    elif args.command == "stats":
        dispatch = {
            "contributors": cmd_stats_contributors,
            "stale": cmd_stats_stale,
            "decay": cmd_stats_decay,
        }
        dispatch[args.stats_type](args)
    elif args.command == "changelog":
        cmd_changelog(args)
    elif args.command == "search":
        cmd_search(args)
    elif args.command == "owners":
        cmd_owners(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
