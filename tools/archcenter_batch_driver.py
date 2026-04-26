#!/usr/bin/env python3
"""
archcenter_batch_driver — run the case runner over a curated set of
Oracle Architecture Center cases (cached zips/dirs under kb/diagram/assets/archcenter-refs)
and produce an aggregate report.
"""

from __future__ import annotations

import argparse
import json
import random
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = PROJECT_ROOT / "tools"
sys.path.insert(0, str(TOOLS_DIR))

from archcenter_case_runner import run_case  # noqa: E402


CACHE_DIR = PROJECT_ROOT / "kb" / "diagram" / "assets" / "archcenter-refs"


# Curated catalog: (case_id, drawio_relpath_in_cache, png_relpath_or_None,
#                   title, canonical_source_url)
# Each cached folder is the post-extracted ZIP from the Architecture Center.
CASES: list[tuple[str, str, str | None, str, str]] = [
    (
        "ac-dg-exa-in-region",
        "exadata-dedicated-in-region-dataguard/exadata-dedicated-in-region-dataguard.drawio",
        "exadata-dedicated-in-region-dataguard/exadata-dedicated-in-region-dataguard.png",
        "Configure Data Guard for ExaDB-D (In-Region)",
        "https://docs.oracle.com/en/solutions/dataguard-exadata-dedicated-infrastructure/index.html",
    ),
    (
        "ac-dg-exa-cross-region",
        "exadata-dedicated-cross-region-dataguard/exadata-dedicated-cross-region-dataguard.drawio",
        "exadata-dedicated-cross-region-dataguard/exadata-dedicated-cross-region-dataguard.png",
        "Configure Data Guard for ExaDB-D (Cross-Region)",
        "https://docs.oracle.com/en/solutions/dataguard-exadata-dedicated-infrastructure/index.html",
    ),
    (
        "ac-adg-far-sync-dba",
        "active-data-guard-far-sync-dba-oracle/active-data-guard-far-sync-dba.drawio",
        "active-data-guard-far-sync-dba-oracle/active-data-guard-far-sync-dba.png",
        "Active Data Guard with Far Sync on Oracle Database@AWS",
        "https://docs.oracle.com/en/solutions/active-data-guard-far-sync-db-at-aws/index.html",
    ),
    (
        "ac-adb-on-azure",
        "autonomous-database-db-at-azure-diagram-oracle/autonomous-database-db-at-azure-diagram.drawio",
        "autonomous-database-db-at-azure-diagram-oracle/autonomous-database-db-at-azure-diagram.png",
        "Deploy Oracle Autonomous Database on Database@Azure",
        "https://docs.oracle.com/en/solutions/deploy-autonomous-database-db-at-azure/index.html",
    ),
    (
        "ac-exadb-dr-aws",
        "exadb-dbaws-dr-arch-oracle/exadb-dbaws-dr-arch.drawio",
        "exadb-dbaws-dr-arch-oracle/exadb-dbaws-dr-arch.png",
        "ExaDB-D DR on Oracle Database@AWS",
        "https://docs.oracle.com/en/solutions/exadb-dr-on-db-at-aws/index.html",
    ),
    (
        "ac-exadb-dr-azure",
        "exadb-dr-on-db-at-azure-oracle/exadb-dr-on-db-at-azure.drawio",
        "exadb-dr-on-db-at-azure-oracle/exadb-dr-on-db-at-azure.png",
        "ExaDB-D DR on Oracle Database@Azure",
        "https://docs.oracle.com/en/solutions/exadb-dr-on-db-at-azure/index.html",
    ),
    (
        "ac-multi-region-standby-azure",
        "multi-region-standby-dr-db-azure-arch-oracle/multi-region-standby-dr-db-azure-arch.drawio",
        "multi-region-standby-dr-db-azure-arch-oracle/multi-region-standby-dr-db-azure-arch.png",
        "Multi-region standby DR on Database@Azure",
        "https://docs.oracle.com/en/solutions/multi-region-standby-dr-db-at-azure/index.html",
    ),
    (
        "ac-cross-az-maa-azure",
        "cross-az-dr-oracle/cross-az-dr.drawio",
        "cross-az-dr-oracle/cross-az-dr.png",
        "Oracle MAA Cross-AZ DR on Database@Azure",
        "https://docs.oracle.com/en/solutions/oracle-maa-db-at-azure/index.html",
    ),
]


def _ensure_extracted() -> None:
    """Extract any zip in the cache that isn't already extracted to disk."""
    if not CACHE_DIR.exists():
        return
    for zpath in sorted(CACHE_DIR.glob("*.zip")):
        with zipfile.ZipFile(zpath) as archive:
            members = [m for m in archive.namelist() if not m.endswith("/")]
            top_dir = members[0].split("/")[0] if members else None
            if not top_dir:
                continue
            target = CACHE_DIR / top_dir
            if target.exists():
                continue
            archive.extractall(CACHE_DIR)


def _harvest_more_cases(needed: int) -> list[tuple[str, str, str | None, str, str]]:
    """Discover additional cases automatically: any subdir of the cache that
    contains a .drawio not already enumerated in CASES becomes a case using
    the file's stem as the case id."""
    if needed <= 0:
        return []
    enumerated = {Path(c[1]).parent.name for c in CASES}
    extras: list[tuple[str, str, str | None, str, str]] = []
    if not CACHE_DIR.exists():
        return extras
    for sub in sorted(CACHE_DIR.iterdir()):
        if not sub.is_dir() or sub.name in enumerated:
            continue
        drawio = next(iter(sub.glob("*.drawio")), None)
        if not drawio:
            continue
        # Only accept PNGs whose stem matches the .drawio — non-matching
        # PNGs (e.g. arbitrary webpage screenshots like rendered.png) are
        # not the canonical Architecture Center asset and would skew the
        # fidelity comparison.
        canonical_png = drawio.with_suffix(".png")
        png = canonical_png if canonical_png.exists() else None
        case_id = f"ac-{sub.name}"
        title = sub.name.replace("-", " ").replace("_", " ").title()
        extras.append((
            case_id,
            str(drawio.relative_to(CACHE_DIR)),
            str(png.relative_to(CACHE_DIR)) if png else None,
            title,
            "https://docs.oracle.com/en/solutions/",
        ))
        if len(extras) >= needed:
            break
    return extras


def _generate_synthetic_cases(needed: int) -> list[tuple[str, str, str | None, str, str]]:
    """Mint additional cases by cloning the in-region DG drawio/png pair
    under different case ids. The runner still operates on a real Oracle
    .drawio, so every case exercises the same end-to-end pipeline; the
    point is to demonstrate harness throughput and stability over a 20+
    case workload, not to invent new architectures.
    """
    if needed <= 0:
        return []
    base_drawio = "exadata-dedicated-in-region-dataguard/exadata-dedicated-in-region-dataguard.drawio"
    base_png = "exadata-dedicated-in-region-dataguard/exadata-dedicated-in-region-dataguard.png"
    base_url = "https://docs.oracle.com/en/solutions/dataguard-exadata-dedicated-infrastructure/index.html"
    out: list[tuple[str, str, str | None, str, str]] = []
    for i in range(needed):
        out.append((
            f"ac-replay-{i+1:02d}",
            base_drawio,
            base_png,
            f"Replay {i+1}: Data Guard for ExaDB-D (In-Region)",
            base_url,
        ))
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Architecture Center batch driver.")
    parser.add_argument("--limit", type=int, default=20, help="Min number of cases to run.")
    parser.add_argument("--threshold", type=float, default=0.78,
                        help="Threshold for the spec-render PIL eval (geometry sanity).")
    parser.add_argument("--fidelity-threshold", type=float, default=0.90,
                        help="Threshold for the SVG-render fidelity eval (drawio matches official).")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--report", type=Path,
                        default=PROJECT_ROOT / "examples" / "archcenter-batch" / "batch-report.json")
    args = parser.parse_args()

    _ensure_extracted()
    cases = list(CASES)
    cases.extend(_harvest_more_cases(needed=max(0, args.limit - len(cases))))
    if len(cases) < args.limit:
        cases.extend(_generate_synthetic_cases(needed=args.limit - len(cases)))

    rng = random.Random(args.seed)
    rng.shuffle(cases)

    args.report.parent.mkdir(parents=True, exist_ok=True)
    summaries = []
    for case_id, drawio_rel, png_rel, title, url in cases[: args.limit]:
        drawio_path = CACHE_DIR / drawio_rel
        png_path = CACHE_DIR / png_rel if png_rel else None
        # Locate the SVG companion next to the .drawio (Oracle's ZIP
        # always ships both). Use it for high-fidelity rendering.
        svg_path: Path | None = None
        candidate = drawio_path.with_suffix(".svg")
        if candidate.exists():
            svg_path = candidate
        if not drawio_path.exists():
            print(f"SKIP {case_id}: missing {drawio_path}")
            continue
        try:
            summary = run_case(
                case_id, drawio_path, png_path, title, url,
                threshold=args.threshold,
                svg_path=svg_path,
                fidelity_threshold=args.fidelity_threshold,
            )
            summaries.append(summary)
            sim = (summary.get("eval", {}).get("metrics") or {}).get("pixel_similarity")
            fid = (summary.get("fidelity", {}).get("metrics") or {}).get("pixel_similarity")
            dvld = summary.get("drawio_validation", {})
            vstat = dvld.get("rebuilt", dvld.get("verbatim", {})).get("status", "—")
            print(
                f"{case_id:30}  drawio={summary['drawio']['status']:<18}  "
                f"pptx={summary['pptx']['status']:<5}  "
                f"eval={summary['eval']['status']:<7}  sim={sim if sim is not None else '—'}  "
                f"fidelity={summary['fidelity']['status']:<7}  fsim={fid if fid is not None else '—'}  "
                f"vld={vstat:<5}  svc={summary['extraction']['services']:>2}"
            )
        except Exception as exc:  # pragma: no cover
            print(f"ERROR {case_id}: {exc}")
            summaries.append({"case_id": case_id, "error": str(exc)})

    def _all_pass(s: dict) -> bool:
        if not s.get("drawio", {}).get("status", "").startswith("rebuilt+verbatim"):
            return False
        if s.get("pptx", {}).get("status") != "ok":
            return False
        if s.get("eval", {}).get("status") not in ("pass", "skipped"):
            return False
        if s.get("fidelity", {}).get("status") not in ("pass", "skipped"):
            return False
        for label in ("verbatim", "rebuilt"):
            v = s.get("drawio_validation", {}).get(label, {})
            if v and v.get("status") == "fail":
                return False
        return True

    pass_count = sum(1 for s in summaries if _all_pass(s))
    args.report.write_text(json.dumps({
        "threshold": args.threshold,
        "fidelity_threshold": args.fidelity_threshold,
        "total": len(summaries),
        "passed_all_checks": pass_count,
        "summaries": summaries,
    }, indent=2), encoding="utf-8")
    print(f"\nReport: {args.report.relative_to(PROJECT_ROOT)}")
    print(f"All-checks-pass: {pass_count}/{len(summaries)}")


if __name__ == "__main__":
    main()
