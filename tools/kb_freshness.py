#!/usr/bin/env python3
"""
OCI Deal Accelerator — KB Freshness Reporter

Thin wrapper around kb_linter.check_freshness() that:
  - reports stale/warning KB files in a compact, scriptable format
  - knows which stale files have a refresh tool, and can run it on demand
  - is safe to call from the skill welcome flow as a precondition check

Usage:
    python tools/kb_freshness.py --check          # human-readable report
    python tools/kb_freshness.py --check --quiet  # no output, exit 1 if stale
    python tools/kb_freshness.py --check --json   # JSON output for the skill
    python tools/kb_freshness.py --auto-refresh   # run refresh tools for stale files

Exit codes:
    0 — all files fresh (or all stale files refreshed successfully)
    1 — stale files found (in --check mode) or refresh failed (--auto-refresh)
    2 — internal error
"""

import argparse
import json
import os
import subprocess
import sys
from typing import Any, Dict, List, Optional

# Reuse the linter's freshness implementation. kb_linter.py lives in the same
# directory; add it to sys.path so this script can be invoked from anywhere.
_HERE = os.path.dirname(os.path.realpath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from kb_linter import check_freshness  # type: ignore  # noqa: E402

PROJECT_ROOT = os.path.dirname(_HERE)


# Bridge: KB file -> refresh command (relative to PROJECT_ROOT).
# Only files with a known automated source belong here. Files with no entry
# can only be refreshed by a human and will be reported as such.
REFRESH_TOOLS: Dict[str, List[str]] = {
    "kb/pricing/oci-sku-catalog.yaml": [
        sys.executable, "tools/refresh_sku_catalog.py", "--refresh",
    ],
    "kb/pricing/compute.yaml": [
        sys.executable, "tools/refresh_sku_catalog.py", "--refresh-domain", "compute",
    ],
    "kb/architecture-center/catalog.yaml": [
        sys.executable, "tools/refresh_arch_catalog.py", "--whats-new",
    ],
}


def collect_stale() -> List[Dict[str, Any]]:
    """Return only files in WARNING or STALE state, sorted oldest first."""
    results = check_freshness()
    stale = [r for r in results if r["status"] in ("STALE", "WARNING")]
    stale.sort(key=lambda r: r["age_days"], reverse=True)
    return stale


def has_refresh_tool(rel_path: str) -> bool:
    return rel_path in REFRESH_TOOLS


def run_refresh(rel_path: str) -> bool:
    """Run the refresh tool for `rel_path`. Returns True on success."""
    cmd = REFRESH_TOOLS[rel_path]
    print(f"  refreshing {rel_path} ...")
    proc = subprocess.run(cmd, cwd=PROJECT_ROOT)
    return proc.returncode == 0


def cmd_check(args: argparse.Namespace) -> int:
    stale = collect_stale()

    if args.json:
        payload = {
            "stale_count": len(stale),
            "files": [
                {
                    "file": s["file"],
                    "status": s["status"],
                    "age_days": s["age_days"],
                    "refreshable": has_refresh_tool(s["file"]),
                }
                for s in stale
            ],
        }
        print(json.dumps(payload, indent=2))
        return 1 if stale else 0

    if not stale:
        if not args.quiet:
            print("KB freshness: OK (all files within thresholds)")
        return 0

    if args.quiet:
        return 1

    refreshable = sum(1 for s in stale if has_refresh_tool(s["file"]))
    print(f"KB freshness: {len(stale)} file(s) need attention "
          f"({refreshable} have an automatic refresh tool)")
    print()
    for s in stale:
        marker = "[auto]" if has_refresh_tool(s["file"]) else "[manual]"
        print(f"  {s['status']:<7} {marker:<8} {s['age_days']:>4}d  {s['file']}")
    print()
    print("To refresh files with [auto]:  python tools/kb_freshness.py --auto-refresh")
    return 1


def cmd_auto_refresh(args: argparse.Namespace) -> int:
    stale = collect_stale()
    refreshable = [s for s in stale if has_refresh_tool(s["file"])]

    if not refreshable:
        print("KB freshness: nothing to auto-refresh "
              f"({len(stale)} stale file(s), none have a refresh tool)")
        return 0 if not stale else 1

    print(f"Auto-refreshing {len(refreshable)} file(s)...")
    failures: List[str] = []
    for s in refreshable:
        if not run_refresh(s["file"]):
            failures.append(s["file"])

    if failures:
        print(f"\nFAILED: {len(failures)} refresh(es) errored:")
        for f in failures:
            print(f"  - {f}")
        return 1

    print("\nAll automatic refreshes completed.")
    # Re-check to confirm
    remaining = [s for s in collect_stale() if has_refresh_tool(s["file"])]
    if remaining:
        print(f"WARNING: {len(remaining)} file(s) still stale after refresh:")
        for r in remaining:
            print(f"  - {r['file']} ({r['age_days']}d)")
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kb_freshness",
        description="Report and refresh stale KB files.",
    )
    parser.add_argument("--check", action="store_true",
                        help="Report stale files (default mode).")
    parser.add_argument("--auto-refresh", action="store_true",
                        help="Run refresh tools for stale files that support them.")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress output; use exit code only.")
    parser.add_argument("--json", action="store_true",
                        help="Emit JSON (for the skill welcome flow to consume).")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.auto_refresh:
        return cmd_auto_refresh(args)
    # Default mode is --check
    return cmd_check(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # pragma: no cover
        print(f"kb_freshness: internal error: {e}", file=sys.stderr)
        sys.exit(2)
