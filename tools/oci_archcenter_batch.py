#!/usr/bin/env python3
"""
Batch native benchmark harness for Oracle Architecture Center diagrams.

This runner fetches official Architecture Center pages, prefers `Download
Diagram` ZIP assets, extracts editable sources (`.drawio`, `.svg`, `.png`,
`.vsdx`), reconstructs each case through the native draw.io + PPTX pipeline,
and records PASS/FAIL evidence per case.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import zipfile
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

import yaml
from PIL import Image

from archcenter_case_runner import extract_layout, run_case
from oci_diagram_gen import OCIDiagramGenerator


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = PROJECT_ROOT / "kb" / "architecture-center" / "catalog.yaml"
DEFAULT_OUTPUT = PROJECT_ROOT / "examples" / "eval-2026-04-25-archcenter-native-20-v8"
USER_AGENT = "OCI-Deal-Accelerator-ArchCenter-Native-Benchmark/1.0"

# Catalog service slugs -> renderer/extractor types we know how to render
# natively or with OCI-official icons.
SERVICE_SUPPORT = {
    "adb-s": "adb_d",
    "adb-d": "adb_d",
    "adw": "adw_d",
    "adg": "data_guard",
    "api-gateway": "api_gateway",
    "base-db": "database_system",
    "bastion": "bastion",
    "block-storage": "block_volume",
    "cloud-guard": "cloud_guard",
    "compute": "virtual_machine",
    "data-catalog": "data_catalog",
    "data-integration": "oci_data_integration",
    "data-safe": "data_safe",
    "dns": "dns",
    "drg": "drg",
    "exacs": "oracle_exadata_database_service",
    "fastconnect": "fastconnect",
    "file-storage": "file_storage",
    "fsdr": "full_stack_disaster_recovery",
    "goldengate": "goldengate",
    "load-balancer": "load_balancer",
    "object-storage": "object_storage",
    "oic": "integration",
    "oic3": "integration",
    "oke": "oke",
    "streaming": "oci_streaming",
    "vault": "vault",
    "vcn": "vcn",
    "wls": "virtual_machine",
}

POSITIVE_TAGS = {"database", "ha-dr", "networking", "security"}
NEGATIVE_TAGS = {"data-platform", "ai-ml", "migration", "application"}
TITLE_NEGATIVE_PHRASES = (
    "learn about",
    "best practices",
    "well-architected framework",
    "foundations benchmark",
)


def _drawio_icon_types() -> set[str]:
    OCIDiagramGenerator._load_icon_cache()
    return set(OCIDiagramGenerator.ICON_CACHE or {})


def assess_native_suitability(title: str, drawio_path: Path) -> dict:
    layout = extract_layout(drawio_path)
    _drawio_icon_types()
    label_count = len(layout.labels)
    service_count = len(layout.services)
    label_density = round(label_count / max(service_count, 1), 2)
    fallback_count = sum(1 for note in layout.notes if note.startswith("fallback compute anchor"))
    missing_icon_types = sorted({
        service["type"]
        for service in layout.services
        if not OCIDiagramGenerator._resolve_icon_entry(service.get("type", ""))[0]
    })
    reasons: list[str] = []
    title_lower = title.lower()
    if any(phrase in title_lower for phrase in TITLE_NEGATIVE_PHRASES):
        reasons.append("conceptual_title")
    if label_count >= 20 and label_density >= 3.0:
        reasons.append("label_heavy")
    if service_count <= 12 and label_density >= 2.0:
        reasons.append("annotation_dominant")
    if fallback_count >= 4 and label_density >= 1.5:
        reasons.append("fallback_icons")
    if len(missing_icon_types) >= 2:
        reasons.append("missing_drawio_icons")
    return {
        "benchmarkable": not reasons,
        "service_count": service_count,
        "label_count": label_count,
        "label_density": label_density,
        "fallback_count": fallback_count,
        "missing_icon_types": missing_icon_types,
        "reasons": reasons,
        "icon_clusters_total": layout.icon_clusters_total,
        "icon_clusters_classified": layout.icon_clusters_classified,
    }


def fetch(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=45) as response:
        return response.read()


def slugify(text: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return text[:72] or "case"


def load_catalog() -> list[dict]:
    data = yaml.safe_load(CATALOG_PATH.read_text(encoding="utf-8"))
    return [e for e in data.get("entries", []) if e.get("type") == "reference-architecture"]


def discover_diagram(page_url: str, html_text: str) -> dict | None:
    matches = []
    for match in re.finditer(r"<img\b[^>]*>", html_text, flags=re.IGNORECASE):
        tag = match.group(0)
        src_match = re.search(r'\bsrc=["\']([^"\']+)["\']', tag, flags=re.IGNORECASE)
        if not src_match:
            continue
        src = html.unescape(src_match.group(1))
        if not re.search(r"\.(png|jpg|jpeg|svg)(\?|$)", src, flags=re.IGNORECASE):
            continue
        alt = ""
        alt_match = re.search(r'\b(?:alt|title)=["\']([^"\']*)["\']', tag, flags=re.IGNORECASE)
        if alt_match:
            alt = html.unescape(alt_match.group(1))
        longdesc = ""
        longdesc_match = re.search(r'\blongdesc=["\']([^"\']+)["\']', tag, flags=re.IGNORECASE)
        if longdesc_match:
            longdesc = html.unescape(longdesc_match.group(1))
        score = 0
        haystack = f"{src} {alt} {longdesc}".lower()
        if "img_text" in haystack:
            score += 4
        if "diagram" in haystack or "architecture" in haystack or "description of" in haystack:
            score += 3
        if "/img/" in src:
            score += 2
        matches.append({
            "src": urljoin(page_url, src),
            "longdesc": urljoin(page_url, longdesc) if longdesc else "",
            "alt": alt,
            "score": score,
        })
    if not matches:
        return None
    return max(matches, key=lambda item: item["score"])


def discover_zip_assets(page_url: str, html_text: str) -> list[str]:
    urls = []
    seen = set()
    for match in re.finditer(r'href=["\']([^"\']+\.zip[^"\']*)["\']', html_text, flags=re.IGNORECASE):
        url = urljoin(page_url, html.unescape(match.group(1)))
        if url not in seen:
            seen.add(url)
            urls.append(url)
    return urls


def file_ext(url: str) -> str:
    suffix = Path(urlparse(url).path).suffix.lower()
    return suffix if suffix in {".png", ".jpg", ".jpeg", ".svg"} else ".png"


def support_score(entry: dict) -> tuple[int, int, str]:
    services = list(entry.get("services") or [])
    supported = sum(1 for service in services if service in SERVICE_SUPPORT)
    unsupported = len(services) - supported
    tags = set(entry.get("tags") or [])
    penalty = len(tags & NEGATIVE_TAGS) - len(tags & POSITIVE_TAGS)
    return (penalty, unsupported, -supported, entry.get("title", ""))


def choose_zip_urls(zip_urls: list[str]) -> list[str]:
    def score(url: str) -> tuple[int, str]:
        name = Path(urlparse(url).path).name.lower()
        positive = 0
        negative = 0
        if any(token in name for token in ("architecture", "physical", "detailed", "topology", "logical", "arch")):
            positive += 3
        if any(token in name for token in ("functional", "overview", "process", "context", "medallion", "business")):
            negative += 3
        if "oracle" in name:
            positive += 1
        return (negative - positive, name)

    return sorted(zip_urls, key=score)


def select_candidates(limit: int, include_multicloud: bool) -> list[dict]:
    candidates: list[dict] = []
    max_candidates = max(limit * 6, limit + 30)
    for entry in load_catalog():
        tags = set(entry.get("tags") or [])
        services = set(entry.get("services") or [])
        if not include_multicloud and (tags & {"multicloud"} or services & {"azure", "aws", "google-cloud"}):
            continue
        try:
            page_bytes = fetch(entry["url"])
        except Exception:
            continue
        html_text = page_bytes.decode("utf-8", errors="ignore")
        zip_urls = discover_zip_assets(entry["url"], html_text)
        if not zip_urls:
            continue
        candidates.append({
            "entry": entry,
            "page_bytes": page_bytes,
            "html_text": html_text,
            "zip_urls": zip_urls,
            "diagram": discover_diagram(entry["url"], html_text),
            "score": support_score(entry),
        })
        if len(candidates) >= max_candidates:
            break
    candidates.sort(key=lambda item: item["score"])
    return candidates


def stage_reference_assets(candidate: dict, case_dir: Path) -> tuple[Path, Path | None, Path | None, dict]:
    entry = candidate["entry"]
    ref_dir = case_dir / "reference"
    ref_dir.mkdir(parents=True, exist_ok=True)

    (ref_dir / "oracle-page.html").write_bytes(candidate["page_bytes"])

    diagram = candidate.get("diagram")
    page_png_path: Path | None = None
    if diagram:
        image_path = ref_dir / f"official-diagram{file_ext(diagram['src'])}"
        image_path.write_bytes(fetch(diagram["src"]))
        if diagram.get("longdesc"):
            try:
                (ref_dir / "official-diagram-description.html").write_bytes(fetch(diagram["longdesc"]))
            except Exception as exc:
                (case_dir / "evidence").mkdir(parents=True, exist_ok=True)
                (case_dir / "evidence" / "description-fetch-error.txt").write_text(str(exc), encoding="utf-8")
        if image_path.suffix.lower() == ".png":
            page_png_path = image_path
        elif image_path.suffix.lower() in {".jpg", ".jpeg"}:
            with Image.open(image_path) as image:
                page_png_path = ref_dir / "official-diagram.png"
                image.convert("RGB").save(page_png_path)

    chosen_zip = None
    zip_path = None
    extract_root = None
    drawio_candidates: list[Path] = []
    svg_candidates: list[Path] = []
    png_candidates: list[Path] = []
    vsdx_candidates: list[Path] = []
    zip_errors = []
    for zip_url in choose_zip_urls(candidate["zip_urls"]):
        candidate_zip_path = ref_dir / Path(urlparse(zip_url).path).name
        candidate_zip_path.write_bytes(fetch(zip_url))
        candidate_extract_root = ref_dir / f"zip-extract-{candidate_zip_path.stem}"
        try:
            with zipfile.ZipFile(candidate_zip_path) as archive:
                archive.extractall(candidate_extract_root)
        except zipfile.BadZipFile as exc:
            zip_errors.append(f"{zip_url}: {exc}")
            continue
        candidate_drawio = sorted(candidate_extract_root.rglob("*.drawio"))
        if not candidate_drawio:
            zip_errors.append(f"{zip_url}: no drawio asset found")
            continue
        chosen_zip = zip_url
        zip_path = candidate_zip_path
        extract_root = candidate_extract_root
        drawio_candidates = candidate_drawio
        svg_candidates = sorted(candidate_extract_root.rglob("*.svg"))
        png_candidates = sorted(candidate_extract_root.rglob("*.png"))
        vsdx_candidates = sorted(candidate_extract_root.rglob("*.vsdx"))
        break
    if not chosen_zip or not zip_path or not extract_root:
        raise FileNotFoundError("; ".join(zip_errors) or "No usable ZIP asset found")

    drawio_path = drawio_candidates[0]
    svg_path = svg_candidates[0] if svg_candidates else None
    png_path = png_candidates[0] if png_candidates else page_png_path
    metadata = {
        "title": entry["title"],
        "url": entry["url"],
        "zip_assets": candidate["zip_urls"],
        "chosen_zip": chosen_zip,
        "diagram_asset": diagram["src"] if diagram else "",
        "longdesc": diagram.get("longdesc", "") if diagram else "",
        "extracted_drawio": [str(path.relative_to(case_dir)) for path in drawio_candidates],
        "extracted_svg": [str(path.relative_to(case_dir)) for path in svg_candidates],
        "extracted_png": [str(path.relative_to(case_dir)) for path in png_candidates],
        "extracted_vsdx": [str(path.relative_to(case_dir)) for path in vsdx_candidates],
        "zip_selection_errors": zip_errors,
    }
    return drawio_path, png_path, svg_path, metadata


def process_case(
    candidate: dict,
    index: int,
    output_root: Path,
    threshold: float,
    fidelity_threshold: float,
) -> dict:
    entry = candidate["entry"]
    case_id = f"{index:02d}-{slugify(entry['title'])}"
    case_dir = output_root / case_id
    drawio_path, png_path, svg_path, metadata = stage_reference_assets(candidate, case_dir)
    preflight = assess_native_suitability(entry["title"], drawio_path)
    if not preflight["benchmarkable"]:
        result = {
            "case_id": case_id,
            "title": entry["title"],
            "url": entry["url"],
            "date": entry.get("date"),
            "tags": entry.get("tags") or [],
            "services": entry.get("services") or [],
            "assets": metadata,
            "status": "SKIP",
            "preflight": preflight,
        }
        (case_dir / "evidence").mkdir(parents=True, exist_ok=True)
        (case_dir / "evidence" / "case-result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        return result
    summary = run_case(
        case_id=case_id,
        drawio_path=drawio_path,
        png_path=png_path,
        title=entry["title"],
        source_url=entry["url"],
        threshold=threshold,
        output_root=output_root,
        svg_path=svg_path,
        fidelity_threshold=fidelity_threshold,
    )

    extraction = summary["extraction"]
    total_clusters = extraction.get("icon_clusters_total", 0)
    classified_clusters = extraction.get("icon_clusters_classified", 0)
    coverage = 1.0 if total_clusters == 0 else round(classified_clusters / total_clusters, 4)
    pptx_audit = summary["pptx"].get("audit") or {}
    pptx_ok = (
        summary["pptx"]["status"] == "ok"
        and pptx_audit.get("unresolved_count", 0) == 0
        and pptx_audit.get("oversize_ref_count", 0) == 0
    )
    pptx_fidelity_ok = summary.get("pptx_fidelity", {}).get("status") == "pass"
    drawio_fidelity_ok = (
        summary.get("fidelity", {}).get("status") == "pass"
        or (
            summary.get("fidelity", {}).get("status") == "skipped"
            and summary["eval"]["status"] == "pass"
        )
    )
    overall = (
        summary["drawio"].get("rebuilt_path")
        and drawio_fidelity_ok
        and coverage >= 0.55
        and pptx_ok
        and pptx_fidelity_ok
    )
    reasons = []
    if not summary["drawio"].get("rebuilt_path"):
        reasons.append("drawio_rebuild")
    if not drawio_fidelity_ok:
        reasons.append("drawio_fidelity")
    if coverage < 0.55:
        reasons.append("low_coverage")
    if summary["pptx"]["status"] != "ok":
        reasons.append("pptx_generation")
    if pptx_audit.get("unresolved_count", 0) > 0:
        reasons.append("pptx_unresolved")
    if pptx_audit.get("oversize_ref_count", 0) > 0:
        reasons.append("pptx_oversize")
    if not pptx_fidelity_ok:
        reasons.append("pptx_fidelity")
    result = {
        "case_id": case_id,
        "title": entry["title"],
        "url": entry["url"],
        "date": entry.get("date"),
        "tags": entry.get("tags") or [],
        "services": entry.get("services") or [],
        "assets": metadata,
        "coverage": coverage,
        "reasons": reasons,
        "status": "PASS" if overall else "FAIL",
        "preflight": preflight,
        "summary": summary,
    }
    (case_dir / "evidence" / "case-result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def run(
    limit: int,
    output_root: Path,
    threshold: float,
    fidelity_threshold: float = 0.90,
    include_multicloud: bool = False,
) -> dict:
    if not output_root.is_absolute():
        output_root = PROJECT_ROOT / output_root
    output_root.mkdir(parents=True, exist_ok=True)
    results = []
    skipped = []
    candidates = select_candidates(limit, include_multicloud=include_multicloud)
    for index, candidate in enumerate(candidates, 1):
        entry = candidate["entry"]
        try:
            result = process_case(candidate, index, output_root, threshold, fidelity_threshold)
        except Exception as exc:
            result = {
                "case_id": f"{index:02d}-{slugify(entry['title'])}",
                "title": entry.get("title", ""),
                "url": entry.get("url", ""),
                "status": "FAIL",
                "error": str(exc),
            }
        if result.get("status") == "SKIP":
            skipped.append(result)
            continue
        results.append(result)
        if len(results) >= limit:
            break

    passed = sum(1 for item in results if item.get("status") == "PASS")
    failed = len(results) - passed
    summary = {
        "output_root": str(output_root.relative_to(PROJECT_ROOT)),
        "requested": limit,
        "considered": len(results) + len(skipped),
        "processed": len(results),
        "skipped": len(skipped),
        "pass": passed,
        "fail": failed,
        "threshold": threshold,
        "fidelity_threshold": fidelity_threshold,
        "selection_note": "ZIP-backed, non-multicloud OCI-oriented cases are preferred by default to benchmark native OCI render fidelity.",
        "skip_note": "Text-heavy conceptual diagrams and cases with multiple unsupported draw.io icon families are skipped from the native editable benchmark pool.",
        "skipped_cases": skipped,
        "results": results,
    }
    (output_root / "batch-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Architecture Center Native 20-Case Benchmark",
        "",
        f"- Requested: {limit}",
        f"- Considered: {len(results) + len(skipped)}",
        f"- Processed: {len(results)}",
        f"- Skipped: {len(skipped)}",
        f"- PASS: {passed}",
        f"- FAIL: {failed}",
        f"- Layout threshold: {threshold}",
        f"- draw.io/PPTX fidelity threshold: {fidelity_threshold}",
        "",
        "| # | Status | Coverage | Architecture |",
        "|---:|---|---:|---|",
    ]
    for index, item in enumerate(results, 1):
        coverage = item.get("coverage")
        coverage_text = f"{coverage:.2f}" if isinstance(coverage, (int, float)) else "-"
        lines.append(
            f"| {index} | {item.get('status')} | {coverage_text} | {item.get('title', '').replace('|', '/')} |"
        )
    lines.extend([
        "",
        "PASS requires all of the following:",
        "- ZIP-backed reference acquisition and staged assets",
        "- rebuilt draw.io output produced successfully",
        "- draw.io fidelity above threshold (primary: draw.io.exe export of rebuilt .drawio; fallback: official SVG render)",
        "- icon-cluster classification coverage >= 0.55",
        "- PPTX generated with no unresolved or oversize icon references",
        "- native PPTX raster render similarity above threshold",
        "",
        "SKIP is used only for benchmark-pool curation when a case is dominated by annotations or depends on multiple icon families not present in the draw.io icon cache.",
    ])
    (output_root / "batch-summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a 20-case native Architecture Center benchmark.")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--threshold", type=float, default=0.82)
    parser.add_argument("--fidelity-threshold", type=float, default=0.90)
    parser.add_argument("--include-multicloud", action="store_true")
    args = parser.parse_args()
    summary = run(
        args.limit,
        args.output_root,
        args.threshold,
        fidelity_threshold=args.fidelity_threshold,
        include_multicloud=args.include_multicloud,
    )
    print(json.dumps(summary, indent=2))
    if summary["processed"] < args.limit or summary["fail"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
