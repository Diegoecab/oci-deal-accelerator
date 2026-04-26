#!/usr/bin/env python3
"""
archcenter_zip_downloader — fetch every Oracle Architecture Center
reference's downloadable assets and stage them under
``kb/diagram/assets/archcenter-refs/`` so the pattern lookup tool can resolve
``cached_assets[drawio]`` for as many entries as possible.

How Oracle ships these: every reference page (e.g.
https://docs.oracle.com/en/solutions/<slug>/index.html) has zero or
more "Download diagram" links pointing to a .zip in
https://docs.oracle.com/en/solutions/<slug>/img/<name>.zip. This tool:

  1. Reads kb/architecture-center/catalog.yaml.
  2. Fetches each entry's page HTML.
  3. Finds .zip URLs under the page's /img/ subtree.
  4. Downloads + extracts under kb/diagram/assets/archcenter-refs/<slug>/.
  5. Records what worked vs failed.

Skips entries whose folder already has a .drawio so the tool is
idempotent across runs (and respects the pre-existing cache).
"""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CATALOG = PROJECT_ROOT / "kb" / "architecture-center" / "catalog.yaml"
CACHE_DIR = PROJECT_ROOT / "kb" / "diagram" / "assets" / "archcenter-refs"
USER_AGENT = "Mozilla/5.0 (oci-deal-accelerator archcenter_zip_downloader)"


def _fetch(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _slug_from_url(url: str) -> str:
    # https://docs.oracle.com/en/solutions/<slug>/index.html → <slug>
    m = re.search(r"/solutions/([^/]+)/", url)
    return m.group(1) if m else ""


def _direct_asset_links(html: bytes, base_url: str, ext: str = "svg") -> list[str]:
    """Find direct <img src> / <a href> links to .svg/.png in the page.

    Used when no .zip download is offered — Oracle still embeds the
    architecture diagram inline as SVG/PNG that we can save.
    """
    text = html.decode("utf-8", errors="ignore")
    pattern_a = rf'href="([^"]+\.{ext})"'
    pattern_img = rf'(?:src|data-src)="([^"]+\.{ext})"'
    hits = re.findall(pattern_a, text) + re.findall(pattern_img, text)
    base = base_url.rsplit("/", 1)[0] + "/"
    out: list[str] = []
    seen: set[str] = set()
    for h in hits:
        if "/img/" not in h and "/Resources/" not in h:
            continue
        if h.startswith("http"):
            url = h
        elif h.startswith("/"):
            url = "https://docs.oracle.com" + h
        else:
            url = base + h
        if url not in seen:
            seen.add(url)
            out.append(url)
    return out


def _zip_links(html: bytes, base_url: str) -> list[str]:
    text = html.decode("utf-8", errors="ignore")
    # Find href attributes pointing at .zip under /img/ or /downloads/
    hits = re.findall(r'href="([^"]+\.zip)"', text)
    base = base_url.rsplit("/", 1)[0] + "/"
    abs_urls: list[str] = []
    for h in hits:
        if h.startswith("http"):
            abs_urls.append(h)
        elif h.startswith("/"):
            abs_urls.append("https://docs.oracle.com" + h)
        else:
            abs_urls.append(base + h)
    # De-dup, prefer architecture-named zips first
    seen: set[str] = set()
    ordered: list[str] = []
    for u in abs_urls:
        if u in seen:
            continue
        seen.add(u)
        ordered.append(u)
    ordered.sort(key=lambda u: (
        0 if any(k in u.lower() for k in ("arch", "topology", "physical", "logical")) else 1,
        len(u),
    ))
    return ordered


def _has_drawio(folder: Path) -> bool:
    if not folder.exists():
        return False
    return any(folder.rglob("*.drawio"))


def _download_one(entry: dict, dest_root: Path, sleep: float) -> dict:
    url = entry.get("url", "")
    slug = _slug_from_url(url)
    if not slug:
        return {"status": "skipped", "reason": "no_slug", "url": url}
    folder = dest_root / slug
    if _has_drawio(folder):
        return {"status": "cached", "slug": slug, "folder": str(folder.relative_to(PROJECT_ROOT))}
    try:
        html = _fetch(url)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
        return {"status": "page_error", "slug": slug, "url": url, "error": str(exc)}
    zip_urls = _zip_links(html, url)
    if not zip_urls:
        # No .zip on the page — fall back to direct SVG/PNG download.
        # Some Oracle reference pages ship only inline SVG/PNG assets
        # (no "Download diagram" zip). Those assets are still useful as
        # the visual source-of-truth even without an editable .drawio.
        svg_urls = _direct_asset_links(html, url, ext="svg")
        png_urls = _direct_asset_links(html, url, ext="png")
        if not (svg_urls or png_urls):
            return {"status": "no_zip", "slug": slug, "url": url}
        folder.mkdir(parents=True, exist_ok=True)
        fetched: list[str] = []
        for asset_url in (svg_urls + png_urls)[:3]:
            try:
                blob = _fetch(asset_url)
                name = asset_url.split("/")[-1]
                (folder / name).write_bytes(blob)
                fetched.append(name)
                time.sleep(sleep)
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as exc:
                continue
        if fetched:
            return {"status": "downloaded_assets_only", "slug": slug, "fetched": fetched,
                    "folder": str(folder.relative_to(PROJECT_ROOT))}
        return {"status": "no_zip", "slug": slug, "url": url}
    folder.mkdir(parents=True, exist_ok=True)
    fetched: list[str] = []
    for zip_url in zip_urls[:2]:  # cap at 2 zips per page
        try:
            blob = _fetch(zip_url)
            with zipfile.ZipFile(io.BytesIO(blob)) as z:
                z.extractall(folder)
            fetched.append(zip_url.split("/")[-1])
            time.sleep(sleep)
        except (urllib.error.HTTPError, urllib.error.URLError, zipfile.BadZipFile,
                TimeoutError, OSError) as exc:
            return {"status": "zip_error", "slug": slug, "url": zip_url, "error": str(exc)}
    if not _has_drawio(folder):
        return {"status": "no_drawio_after_extract", "slug": slug, "fetched": fetched}
    return {"status": "downloaded", "slug": slug, "fetched": fetched,
            "folder": str(folder.relative_to(PROJECT_ROOT))}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=CATALOG)
    parser.add_argument("--cache-dir", type=Path, default=CACHE_DIR)
    parser.add_argument("--limit", type=int, default=60,
                        help="Max number of catalog entries to attempt this run.")
    parser.add_argument("--sleep", type=float, default=1.0,
                        help="Seconds between zip downloads (be polite).")
    parser.add_argument("--report", type=Path,
                        default=PROJECT_ROOT / "kb" / "diagram" / "assets" / "archcenter-refs" / "_download-report.json")
    args = parser.parse_args()

    catalog = yaml.safe_load(args.catalog.read_text(encoding="utf-8"))
    entries = catalog.get("entries", [])

    args.cache_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict] = []
    counts: dict[str, int] = {}
    for i, e in enumerate(entries[:args.limit], 1):
        r = _download_one(e, args.cache_dir, args.sleep)
        r.setdefault("title", e.get("title", ""))
        results.append(r)
        counts[r["status"]] = counts.get(r["status"], 0) + 1
        flag = {"downloaded": "✓", "cached": "·", "no_zip": "—",
                "page_error": "✗", "zip_error": "✗",
                "no_drawio_after_extract": "?",
                "skipped": "·"}.get(r["status"], "?")
        title = (e.get("title") or "")[:64]
        print(f"  {flag} [{i}/{args.limit}] {title}", file=sys.stderr)

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps({
        "counts": counts,
        "results": results,
    }, indent=2), encoding="utf-8")
    print("", file=sys.stderr)
    for status, n in sorted(counts.items()):
        print(f"  {status:30s}  {n}", file=sys.stderr)
    print(f"\nReport: {args.report.relative_to(PROJECT_ROOT)}", file=sys.stderr)


if __name__ == "__main__":
    main()
