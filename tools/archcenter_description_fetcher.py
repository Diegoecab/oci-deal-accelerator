#!/usr/bin/env python3
"""
archcenter_description_fetcher — fetch each Oracle Architecture Center
reference's textual description ("About this architecture", components,
recommendations) and save as Markdown next to the cached .drawio.

Why: the catalog in ``kb/architecture-center/catalog.yaml`` only carries
a 1-line summary per entry. The full description on the source page
contains the topology rationale, networking decisions, services list,
and recommendations — exactly the context a spec author needs when
choosing/adapting a reference. Caching it locally:

  1. Enriches ``archcenter_pattern_lookup.py`` scoring (more context
     to match against).
  2. Lets the SKILL.md option 10 ("Reference architecture lookup")
     answer with full Oracle text rather than just title + URL.
  3. Removes the runtime dependency on docs.oracle.com for spec
     authoring sessions.

Output layout:
  kb/diagram/assets/archcenter-refs/<slug>/_description.md

Idempotent: skips entries whose ``_description.md`` already exists.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from html import unescape
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CATALOG = PROJECT_ROOT / "kb" / "architecture-center" / "catalog.yaml"
CACHE_DIR = PROJECT_ROOT / "kb" / "diagram" / "assets" / "archcenter-refs"
USER_AGENT = "Mozilla/5.0 (oci-deal-accelerator archcenter_description_fetcher)"


def _fetch(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _slug_from_url(url: str) -> str:
    m = re.search(r"/solutions/([^/]+)/", url)
    return m.group(1) if m else ""


def _strip_html_to_text(html: str) -> str:
    """Coarse HTML→text: drop tags, collapse whitespace, decode entities."""
    text = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    # Convert <li> to "- " markers, <h*> to newlines
    text = re.sub(r"<li[^>]*>", "\n- ", text, flags=re.IGNORECASE)
    text = re.sub(r"</?(h[1-6]|p|div|section|article)[^>]*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _extract_main_section(html: bytes) -> str:
    """Grab the page's main content article. Oracle's solution pages
    wrap the architecture description in a <main> or <article>; we
    capture the largest such block and strip nav/footer noise.
    """
    raw = html.decode("utf-8", errors="ignore")
    main_match = re.search(r"<main\b[^>]*>(.*?)</main>", raw, re.DOTALL | re.IGNORECASE)
    section = main_match.group(1) if main_match else raw
    # Try to find the "Architecture" / "About this architecture" heading
    arch_match = re.search(
        r"<h\d[^>]*>\s*(?:About this )?Architecture\s*</h\d>(.*?)(?:<h\d|$)",
        section, re.DOTALL | re.IGNORECASE,
    )
    if arch_match:
        # Include the architecture section + a wider window for components
        idx = arch_match.start()
        section = section[idx: idx + 20000]
    text = _strip_html_to_text(section)
    # Trim boilerplate
    boilerplate_markers = [
        "Send Us Your Comments",
        "Documentation Accessibility",
        "Use the OCI region",  # privacy banner
    ]
    for m in boilerplate_markers:
        idx = text.find(m)
        if idx > 200:
            text = text[:idx].rstrip()
    return text[:8000]  # cap at 8KB per entry — plenty for context


def _save_markdown(folder: Path, entry: dict, body_text: str) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    md = (
        f"# {entry.get('title','')}\n\n"
        f"- Source: {entry.get('url','')}\n"
        f"- Date: {entry.get('date','')}\n"
        f"- Type: {entry.get('type','reference-architecture')}\n"
        f"- Services: {', '.join(entry.get('services', []))}\n"
        f"- Tags: {', '.join(entry.get('tags', []))}\n\n"
        f"## Summary (catalog)\n\n{(entry.get('summary') or '').strip()}\n\n"
        f"## Architecture (fetched from source)\n\n{body_text}\n"
    )
    (folder / "_description.md").write_text(md, encoding="utf-8")


def _fetch_one(entry: dict, sleep: float, force: bool) -> dict:
    url = entry.get("url", "")
    slug = _slug_from_url(url)
    if not slug:
        return {"status": "skipped", "reason": "no_slug", "url": url}
    folder = CACHE_DIR / slug
    description_path = folder / "_description.md"
    if description_path.exists() and not force:
        return {"status": "cached", "slug": slug}
    try:
        html = _fetch(url)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
        return {"status": "page_error", "slug": slug, "url": url, "error": str(exc)}
    body = _extract_main_section(html)
    if not body or len(body) < 200:
        return {"status": "thin_content", "slug": slug, "bytes": len(body or "")}
    _save_markdown(folder, entry, body)
    time.sleep(sleep)
    return {"status": "fetched", "slug": slug, "bytes": len(body)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=CATALOG)
    parser.add_argument("--limit", type=int, default=200)
    parser.add_argument("--sleep", type=float, default=0.5)
    parser.add_argument("--force", action="store_true",
                        help="Re-fetch even if _description.md already exists.")
    parser.add_argument("--report", type=Path,
                        default=PROJECT_ROOT / "tmp" / "_description-fetch-report.json")
    args = parser.parse_args()

    catalog = yaml.safe_load(args.catalog.read_text(encoding="utf-8"))
    entries = catalog.get("entries", [])
    results = []
    counts: dict[str, int] = {}
    for i, e in enumerate(entries[:args.limit], 1):
        r = _fetch_one(e, args.sleep, args.force)
        r["title"] = (e.get("title") or "")[:64]
        results.append(r)
        counts[r["status"]] = counts.get(r["status"], 0) + 1
        flag = {"fetched": "✓", "cached": "·", "thin_content": "?",
                "page_error": "✗", "skipped": "·"}.get(r["status"], "?")
        print(f"  {flag} [{i}/{args.limit}] {r['title']}", file=sys.stderr)

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps({"counts": counts, "results": results}, indent=2),
                           encoding="utf-8")
    print("", file=sys.stderr)
    for s, n in sorted(counts.items()):
        print(f"  {s:25s}  {n}", file=sys.stderr)
    print(f"\nReport: {args.report.relative_to(PROJECT_ROOT)}", file=sys.stderr)


if __name__ == "__main__":
    main()
