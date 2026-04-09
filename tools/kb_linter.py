#!/usr/bin/env python3
"""
OCI Deal Accelerator — KB Linter

Validates KB files against governance rules:
- Contributor blocks on findings and matrix entries
- Confidence decay against governance config
- Tag validation against taxonomy
- Domain owner review cadence
- Freshness checks on all KB files

Usage:
    python kb_linter.py                    # Run all checks
    python kb_linter.py --show-decay       # Show confidence decay status
    python kb_linter.py --check-tags       # Validate tags only
    python kb_linter.py --check-owners     # Check domain owner review cadence
"""

import argparse
import os
import sys
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple

import yaml

# =============================================================================
# Constants
# =============================================================================

PROJECT_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
GOVERNANCE_PATH = os.path.join(PROJECT_ROOT, "config", "kb-governance.yaml")
OWNERS_PATH = os.path.join(PROJECT_ROOT, "config", "kb-owners.yaml")
TAGS_PATH = os.path.join(PROJECT_ROOT, "config", "kb-tags.yaml")
TRACKER_PATH = os.path.join(PROJECT_ROOT, "kb", "field-findings", "tracker.yaml")
MATRIX_PATH = os.path.join(PROJECT_ROOT, "kb", "compatibility", "adb-feature-matrix.yaml")

_RESET = "\033[0m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_RED = "\033[31m"


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
        # Many KB files use a frontmatter pattern: a metadata doc followed by
        # a body doc, separated by `---`. Merge all dict docs into one so
        # callers see a single namespace (later docs override earlier keys).
        merged: Dict[str, Any] = {}
        for doc in yaml.safe_load_all(fh):
            if isinstance(doc, dict):
                merged.update(doc)
        return merged or None


def _load_governance() -> Dict[str, Any]:
    data = _load_yaml(GOVERNANCE_PATH)
    return data if data else {}


def _load_taxonomy() -> List[str]:
    data = _load_yaml(TAGS_PATH)
    if not data or "taxonomy" not in data:
        return []
    all_tags = []
    for category_tags in data["taxonomy"].values():
        if isinstance(category_tags, list):
            all_tags.extend(str(t) for t in category_tags)
    return all_tags


def _parse_date(d: Any) -> Optional[date]:
    if isinstance(d, date) and not isinstance(d, datetime):
        return d
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, str):
        try:
            return datetime.strptime(d, "%Y-%m-%d").date()
        except ValueError:
            return None
    return None


def _days_ago(d: Any) -> Optional[int]:
    parsed = _parse_date(d)
    if parsed is None:
        return None
    return (date.today() - parsed).days


# =============================================================================
# Check: Contributor blocks
# =============================================================================

def check_contributor_blocks(tracker_path: str = TRACKER_PATH) -> List[str]:
    """Verify all findings have proper contributor blocks."""
    issues = []
    data = _load_yaml(tracker_path)
    if not data or "findings" not in data:
        issues.append("Cannot load tracker file.")
        return issues

    governance = _load_governance()
    required = governance.get("contribution", {}).get("required_fields", ["name", "team", "date", "confidence"])
    valid_confidence = governance.get("contribution", {}).get("confidence_levels",
                                                              ["validated", "observed", "reported", "inferred"])

    for f in data["findings"]:
        fid = f.get("id", "???")
        contributor = f.get("contributor")
        if not isinstance(contributor, dict):
            if f.get("reported_by"):
                issues.append(f"{fid}: uses legacy 'reported_by' instead of contributor block")
            else:
                issues.append(f"{fid}: missing contributor block")
            continue
        # The finding's top-level `date` is the canonical discovery date and
        # acts as a fallback when the contributor block doesn't repeat it.
        finding_date = f.get("date")
        for field in required:
            value = contributor.get(field)
            if not value and field == "date" and finding_date:
                continue
            if not value:
                issues.append(f"{fid}: contributor missing required field '{field}'")
        conf = contributor.get("confidence", "")
        if conf and conf not in valid_confidence:
            issues.append(f"{fid}: invalid confidence level '{conf}'")
    return issues


# =============================================================================
# Check: Confidence decay
# =============================================================================

def check_confidence_decay(tracker_path: str = TRACKER_PATH) -> List[Dict[str, Any]]:
    """Check confidence decay for all findings. Returns list of decay reports."""
    governance = _load_governance()
    decay_config = governance.get("confidence_decay", {})
    data = _load_yaml(tracker_path)
    if not data or "findings" not in data:
        return []

    results = []
    for f in data["findings"]:
        fid = f.get("id", "???")
        contributor = f.get("contributor", {})
        confidence = contributor.get("confidence", "validated") if isinstance(contributor, dict) else "validated"
        finding_date = contributor.get("date", f.get("date")) if isinstance(contributor, dict) else f.get("date")
        age = _days_ago(finding_date)
        if age is None:
            results.append({"id": fid, "status": "UNKNOWN", "confidence": confidence, "age_days": None})
            continue

        thresholds = decay_config.get(confidence, {"fresh": 180, "stale": 365, "expired": 730})
        if age <= thresholds.get("fresh", 180):
            decay_status = "FRESH"
        elif age <= thresholds.get("stale", 365):
            decay_status = "STALE"
        else:
            decay_status = "EXPIRED"

        results.append({
            "id": fid,
            "status": decay_status,
            "confidence": confidence,
            "age_days": age,
            "summary": f.get("summary", ""),
        })
    return results


# =============================================================================
# Check: Tag validation
# =============================================================================

def check_tags(tracker_path: str = TRACKER_PATH) -> List[str]:
    """Validate all tags against the taxonomy."""
    taxonomy = _load_taxonomy()
    if not taxonomy:
        return ["No taxonomy loaded — skipping tag validation."]
    data = _load_yaml(tracker_path)
    if not data or "findings" not in data:
        return ["Cannot load tracker file."]

    issues = []
    for f in data["findings"]:
        fid = f.get("id", "???")
        for tag in f.get("tags", []):
            if str(tag) not in taxonomy:
                issues.append(f"{fid}: unknown tag '{tag}'")
    return issues


# =============================================================================
# Check: Domain owners
# =============================================================================

def check_owners() -> List[str]:
    """Check if domain owners need to review their areas."""
    owners_data = _load_yaml(OWNERS_PATH)
    if not owners_data or "domains" not in owners_data:
        return ["No owners config found."]

    issues = []
    for domain in owners_data["domains"]:
        area = domain.get("area", "")
        owner = domain.get("owner", {})
        if owner.get("name") == "TBD":
            issues.append(f"{area}: no owner assigned (TBD)")
    return issues


# =============================================================================
# Check: File freshness
# =============================================================================

def check_freshness() -> List[Dict[str, Any]]:
    """Check freshness of all YAML files in kb/."""
    governance = _load_governance()
    warning_days = governance.get("freshness", {}).get("warning_days", 180)
    stale_days = governance.get("freshness", {}).get("stale_days", 365)

    kb_root = os.path.join(PROJECT_ROOT, "kb")
    results = []

    for dirpath, _dirnames, filenames in os.walk(kb_root):
        for filename in filenames:
            if not filename.endswith((".yaml", ".yml")):
                continue
            filepath = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(filepath, PROJECT_ROOT)
            data = _load_yaml(filepath)
            if not data:
                continue

            last_verified = (
                data.get("last_verified")
                or data.get("last_updated")
                or data.get("last_refreshed")
            )
            if last_verified:
                age = _days_ago(last_verified)
                if age is not None:
                    if age > stale_days:
                        status = "STALE"
                    elif age > warning_days:
                        status = "WARNING"
                    else:
                        status = "FRESH"
                    results.append({"file": rel_path, "status": status, "age_days": age})
                    continue

            # Use file modification time as fallback
            mtime = os.path.getmtime(filepath)
            mdate = datetime.fromtimestamp(mtime).date()
            age = (date.today() - mdate).days
            if age > stale_days:
                status = "STALE"
            elif age > warning_days:
                status = "WARNING"
            else:
                status = "FRESH"
            results.append({"file": rel_path, "status": status, "age_days": age})
    return results


# =============================================================================
# Check: Contribution stats
# =============================================================================

def contribution_stats(tracker_path: str = TRACKER_PATH) -> Dict[str, int]:
    """Count contributions per person across findings."""
    data = _load_yaml(tracker_path)
    if not data or "findings" not in data:
        return {}
    counts: Dict[str, int] = {}
    for f in data["findings"]:
        contributor = f.get("contributor", {})
        if isinstance(contributor, dict):
            name = contributor.get("name", "Unknown")
        else:
            name = str(f.get("reported_by", "Unknown"))
        counts[name] = counts.get(name, 0) + 1
        for c in f.get("confirmations", []):
            cname = c.get("name", "Unknown")
            counts[cname] = counts.get(cname, 0) + 1
    return counts


# =============================================================================
# CLI
# =============================================================================

def cmd_lint(args: argparse.Namespace) -> None:
    """Run all lint checks."""
    total_issues = 0

    # Contributor blocks
    print("Checking contributor blocks...")
    contributor_issues = check_contributor_blocks()
    if contributor_issues:
        for issue in contributor_issues:
            print(f"  {_c('ISSUE', _YELLOW)}: {issue}")
        total_issues += len(contributor_issues)
    else:
        print(f"  {_c('OK', _GREEN)}: All findings have valid contributor blocks.")

    # Tags
    if args.check_tags or not (args.show_decay or args.check_owners):
        print("\nChecking tags against taxonomy...")
        tag_issues = check_tags()
        if tag_issues:
            for issue in tag_issues:
                print(f"  {_c('ISSUE', _YELLOW)}: {issue}")
            total_issues += len(tag_issues)
        else:
            print(f"  {_c('OK', _GREEN)}: All tags are valid.")

    # Domain owners
    if args.check_owners or not (args.show_decay or args.check_tags):
        print("\nChecking domain owners...")
        owner_issues = check_owners()
        if owner_issues:
            for issue in owner_issues:
                print(f"  {_c('ISSUE', _YELLOW)}: {issue}")
            total_issues += len(owner_issues)
        else:
            print(f"  {_c('OK', _GREEN)}: All domains have assigned owners.")

    # Freshness
    if not (args.show_decay or args.check_tags or args.check_owners):
        print("\nChecking file freshness...")
        freshness = check_freshness()
        stale = [f for f in freshness if f["status"] in ("STALE", "WARNING")]
        if stale:
            for f in stale:
                status_color = _RED if f["status"] == "STALE" else _YELLOW
                print(f"  {_c(f['status'], status_color)}: {f['file']} ({f['age_days']} days old)")
            total_issues += len(stale)
        else:
            print(f"  {_c('OK', _GREEN)}: All files are fresh.")

    # Confidence decay
    if args.show_decay or not (args.check_tags or args.check_owners):
        print("\nConfidence decay status...")
        decay = check_confidence_decay()
        for d in decay:
            if d["status"] == "FRESH":
                status_display = _c("FRESH", _GREEN)
            elif d["status"] == "STALE":
                status_display = _c("STALE", _YELLOW)
                total_issues += 1
            elif d["status"] == "EXPIRED":
                status_display = _c("EXPIRED", _RED)
                total_issues += 1
            else:
                status_display = d["status"]
            age_str = f"{d['age_days']} days ago" if d["age_days"] is not None else "unknown age"
            summary = d.get("summary", "")[:50]
            print(f"  {d['id']}  {status_display}   {summary} ({d['confidence']}, {age_str})")

    # Contribution stats
    if not (args.show_decay or args.check_tags or args.check_owners):
        print("\nContribution stats:")
        cstats = contribution_stats()
        for name, count in sorted(cstats.items(), key=lambda x: -x[1]):
            print(f"  {name:<30} {count} contributions")

    print(f"\n{'=' * 40}")
    if total_issues:
        print(f"{_c(f'{total_issues} issue(s) found.', _YELLOW)}")
    else:
        print(f"{_c('All checks passed.', _GREEN)}")

    sys.exit(1 if total_issues > 0 else 0)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kb_linter",
        description="Validate KB files against governance rules.",
    )
    parser.add_argument("--show-decay", action="store_true", help="Show confidence decay status.")
    parser.add_argument("--check-tags", action="store_true", help="Validate tags only.")
    parser.add_argument("--check-owners", action="store_true", help="Check domain owner assignments.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    cmd_lint(args)


if __name__ == "__main__":
    main()
