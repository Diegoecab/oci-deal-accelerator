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
import json
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
ARCH_CATALOG_PATH = os.path.join(KB_ROOT, "architecture-center", "catalog.yaml")
ECAL_CATALOG_PATH = os.path.join(KB_ROOT, "patterns", "ecal-artefacts-catalog.yaml")

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
        docs = list(yaml.safe_load_all(fh))
    # Merge multi-document YAML (front matter + body) into single dict
    merged: Dict[str, Any] = {}
    for doc in docs:
        if isinstance(doc, dict):
            merged.update(doc)
    return merged or None


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

    if getattr(args, "json_output", False):
        json_results = [
            {"file": fp, "matches": [{"line": ln, "text": txt} for ln, txt in ms]}
            for fp, ms in results
        ]
        print(json.dumps(json_results, indent=2))
        return

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
# Architecture Center search command
# =============================================================================

def cmd_arch_search(args: argparse.Namespace) -> None:
    """Search Architecture Center catalog by services and/or tags."""
    data = _load_yaml(ARCH_CATALOG_PATH)
    if not data or "entries" not in data:
        print("Error: Architecture catalog not found or empty.", file=sys.stderr)
        sys.exit(1)

    results = data["entries"]

    # Filter by services (OR match, case-insensitive)
    if args.services:
        svc_set = {s.lower() for s in args.services}
        results = [
            e for e in results
            if svc_set & {s.lower() for s in e.get("services", [])}
        ]

    # Filter by tags (OR match, case-insensitive)
    if args.tags:
        tag_set = {t.lower() for t in args.tags}
        results = [
            e for e in results
            if tag_set & {t.lower() for t in e.get("tags", [])}
        ]

    # Optional text search across title + summary
    if args.query:
        q = args.query.lower()
        results = [
            e for e in results
            if q in e.get("title", "").lower() or q in e.get("summary", "").lower()
        ]

    if getattr(args, "json_output", False):
        print(json.dumps(results, indent=2, default=str))
        return

    if not results:
        print("No matching architecture references found.")
        return

    print(f"Found {len(results)} architecture reference(s):\n")
    for e in results:
        svcs = ", ".join(e.get("services", []))
        tags = ", ".join(e.get("tags", []))
        print(f"  {_c(e.get('title', ''), _CYAN)}")
        print(f"    Services: {svcs}")
        print(f"    Tags: {tags}")
        print(f"    URL: {e.get('url', 'N/A')}")
        if e.get("terraform"):
            print(f"    Terraform: {e['terraform']}")
        print()


# =============================================================================
# ECAL score command
# =============================================================================

def _load_ecal_artefacts() -> List[Dict[str, Any]]:
    """Load and flatten all ECAL artefacts from the catalog."""
    data = _load_yaml(ECAL_CATALOG_PATH)
    if not data:
        return []

    artefacts = []
    for phase in ["define", "design", "deliver"]:
        phase_data = data.get(phase, {})
        if not isinstance(phase_data, dict):
            continue
        for step, items in phase_data.items():
            if not isinstance(items, list):
                continue
            for item in items:
                if isinstance(item, dict) and "id" in item:
                    item["_phase"] = phase
                    item["_step"] = step
                    artefacts.append(item)
    return artefacts


def cmd_ecal_score(args: argparse.Namespace) -> None:
    """Evaluate engagement readiness against ECAL 3.1 artefacts."""
    artefacts = _load_ecal_artefacts()
    if not artefacts:
        print("Error: Could not load ECAL artefacts catalog.", file=sys.stderr)
        sys.exit(1)

    summary_lower = args.summary.lower()
    summary_words = set(summary_lower.split())
    stopwords = {
        "the", "a", "an", "and", "or", "for", "to", "in", "of", "is",
        "with", "on", "at", "by", "as", "it", "be", "this", "that", "from",
    }

    # Filter by phase if specified
    if args.phase:
        artefacts = [a for a in artefacts if a.get("_phase") == args.phase]

    scored = []
    for art in artefacts:
        name_lower = art.get("name", "").lower()
        what_lower = art.get("what", "").lower()
        id_lower = art.get("id", "").lower()

        # Check if artefact name or ID appears in summary
        name_match = name_lower in summary_lower
        id_match = id_lower in summary_lower

        # Keyword overlap with the "what" field
        what_words = set(what_lower.split()) - stopwords
        meaningful_overlap = summary_words & what_words

        if name_match or id_match:
            relevance = "mentioned"
        elif len(meaningful_overlap) >= 3:
            relevance = "likely_relevant"
        elif len(meaningful_overlap) >= 1:
            relevance = "possibly_relevant"
        else:
            relevance = "none"

        scored.append({
            "id": art.get("id"),
            "name": art.get("name"),
            "phase": art.get("_phase"),
            "step": art.get("_step"),
            "skill_support": art.get("skill_support"),
            "customer_facing": art.get("customer_facing"),
            "relevance": relevance,
        })

    # Compute summary stats
    mentioned = [s for s in scored if s["relevance"] == "mentioned"]
    likely = [s for s in scored if s["relevance"] == "likely_relevant"]
    possibly = [s for s in scored if s["relevance"] == "possibly_relevant"]
    not_covered = [s for s in scored if s["relevance"] == "none"]
    relevant = [s for s in scored if s["relevance"] != "none"]
    auto_gen = [s for s in relevant if s["skill_support"] == "auto_generate"]
    assist = [s for s in relevant if s["skill_support"] == "assist"]

    if getattr(args, "json_output", False):
        output = {
            "summary": {
                "total_artefacts": len(scored),
                "mentioned": len(mentioned),
                "likely_relevant": len(likely),
                "possibly_relevant": len(possibly),
                "not_covered": len(not_covered),
                "skill_auto_generate": len(auto_gen),
                "skill_assist": len(assist),
            },
            "artefacts": scored,
        }
        print(json.dumps(output, indent=2, default=str))
        return

    # Text output
    print(f"\n{_c('ECAL 3.1 READINESS ASSESSMENT', _BOLD)}")
    print("=" * 50)
    print(f"\nArtefacts assessed: {len(scored)}")
    print(f"  Mentioned in summary: {_c(str(len(mentioned)), _GREEN)}")
    print(f"  Likely relevant:      {_c(str(len(likely)), _YELLOW)}")
    print(f"  Possibly relevant:    {str(len(possibly))}")
    print(f"  Not covered:          {_c(str(len(not_covered)), _RED)}")
    print(f"\nSkill can auto-generate: {len(auto_gen)} relevant artefact(s)")
    print(f"Skill can assist:        {len(assist)} relevant artefact(s)")

    if mentioned or likely:
        print(f"\n{'ID':<10} {'Phase':<8} {'Name':<35} {'Support':<15} Relevance")
        print("-" * 85)
        for s in mentioned + likely:
            rel_color = _GREEN if s["relevance"] == "mentioned" else _YELLOW
            print(
                f"{s['id']:<10} {s['phase']:<8} "
                f"{str(s['name']):<35} {str(s['skill_support']):<15} "
                f"{_c(s['relevance'], rel_color)}"
            )

    if not_covered:
        print(f"\nNot covered ({len(not_covered)} artefact(s)) — consider adding to engagement:")
        for s in not_covered[:10]:
            cf = " [customer-facing]" if s.get("customer_facing") else ""
            print(f"  {s['id']} {s['name']}{cf}")
        if len(not_covered) > 10:
            print(f"  ... and {len(not_covered) - 10} more (use --json for full list)")


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
    p_search.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON.")

    # --- owners ---
    subparsers.add_parser("owners", help="Show domain owners.")

    # --- arch-search ---
    p_arch = subparsers.add_parser("arch-search", help="Search Architecture Center catalog.")
    p_arch.add_argument("query", nargs="?", default=None, help="Optional text search term.")
    p_arch.add_argument("--services", nargs="+", help="Filter by service names (e.g., adb-s exacs).")
    p_arch.add_argument("--tags", nargs="+", help="Filter by tags (e.g., ha-dr multicloud).")
    p_arch.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON.")

    # --- ecal-score ---
    p_ecal = subparsers.add_parser("ecal-score", help="ECAL engagement readiness assessment.")
    p_ecal.add_argument("--summary", required=True, help="Text describing the engagement.")
    p_ecal.add_argument("--phase", choices=["define", "design", "deliver"], help="Limit to a specific ECAL phase.")
    p_ecal.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON.")

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
    elif args.command == "arch-search":
        cmd_arch_search(args)
    elif args.command == "ecal-score":
        cmd_ecal_score(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
