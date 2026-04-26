#!/usr/bin/env python3
"""
archcenter_pattern_lookup — find Oracle Architecture Center patterns
that match a topology prompt, so spec authors can base their diagram
on Oracle's canonical conventions instead of inventing layout.

Usage:
    python tools/archcenter_pattern_lookup.py "aws fastconnect exacs"
    python tools/archcenter_pattern_lookup.py "data guard cross region adb"
    python tools/archcenter_pattern_lookup.py "oke three tier"
    python tools/archcenter_pattern_lookup.py --top 10 "azure"

Sources:
    kb/architecture-center/catalog.yaml      — 123 OCI Architecture
                                                Center entries with
                                                services + tags + URL.
    kb/diagram/reference-patterns.yaml       — visual conventions
                                                (FastConnect badge, DRG
                                                position, multi-cloud
                                                styling, …)

Output for each match:
    - title + URL
    - tags + services
    - cached_assets (if we have the .drawio locally)
    - visual_conventions (if linked from reference-patterns.yaml)
    - score

Higher score = better match. Use the top result's URL/cached drawio
as the basis for your absolute_layout authoring.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CATALOG = PROJECT_ROOT / "kb" / "architecture-center" / "catalog.yaml"
PATTERNS = PROJECT_ROOT / "kb" / "diagram" / "reference-patterns.yaml"
SYNONYMS = PROJECT_ROOT / "kb" / "architecture-center" / "synonyms.yaml"
CACHE_DIR = PROJECT_ROOT / "kb" / "diagram" / "assets" / "archcenter-refs"


def _tokens(text: str) -> set[str]:
    text = (text or "").lower()
    return set(re.findall(r"[a-z0-9]+", text))


_SYNONYM_INDEX: dict[str, set[str]] | None = None


def _load_synonym_index() -> dict[str, set[str]]:
    """Build alias-token → expansion-token-set map. Loaded once.

    Each canonical phrase contributes a token set; every alias maps to
    that same set, plus the alias's own tokens. Multi-word aliases
    expand all their constituent tokens too, so 'lb' → {load, balancer}.
    """
    global _SYNONYM_INDEX
    if _SYNONYM_INDEX is not None:
        return _SYNONYM_INDEX
    index: dict[str, set[str]] = {}
    if not SYNONYMS.exists():
        _SYNONYM_INDEX = index
        return index
    try:
        doc = yaml.safe_load(SYNONYMS.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        _SYNONYM_INDEX = index
        return index
    for entry in doc.get("synonyms", []) or []:
        canonical = entry.get("canonical", "")
        canonical_tokens = _tokens(canonical)
        if not canonical_tokens:
            continue
        # Canonical tokens map to themselves (so they expand into siblings too).
        for ct in canonical_tokens:
            index.setdefault(ct, set()).update(canonical_tokens)
        for alias in entry.get("aliases", []) or []:
            alias_tokens = _tokens(alias)
            for at in alias_tokens:
                index.setdefault(at, set()).update(canonical_tokens | alias_tokens)
    _SYNONYM_INDEX = index
    return index


def _expand_query_tokens(tokens: set[str]) -> set[str]:
    """Apply the synonym index to a query token set."""
    index = _load_synonym_index()
    if not index:
        return tokens
    expanded = set(tokens)
    for tok in tokens:
        expanded.update(index.get(tok, set()))
    return expanded


def _llm_rewrite_query(query: str) -> str:
    """Rewrite ``query`` into canonical OCI/Oracle terminology via the
    Anthropic API.

    Opt-in: requires ``ANTHROPIC_API_KEY`` in the environment. Returns
    the original query unchanged on any error or when the key is
    missing — never fails the lookup. The synonym table covers the
    common abbreviations; this hook is for natural-language queries
    where rule-based expansion alone misses the intent.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[lookup] --llm-rewrite skipped: ANTHROPIC_API_KEY not set",
              file=sys.stderr)
        return query
    model = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
    payload = {
        "model": model,
        "max_tokens": 120,
        "system": (
            "Rewrite the user's free-text architecture query into a "
            "concise list of canonical OCI and cloud terms. Expand "
            "abbreviations (LB → load balancer, ADG → active data "
            "guard, AD → availability domain, etc.). Do NOT add "
            "topology elements the user did not request. Output ONLY "
            "the rewritten query as a single space-separated phrase, "
            "no preface, no quotes."
        ),
        "messages": [{"role": "user", "content": query}],
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError) as exc:
        print(f"[lookup] --llm-rewrite failed: {exc}; using original query",
              file=sys.stderr)
        return query
    blocks = body.get("content") or []
    text = " ".join(b.get("text", "") for b in blocks if b.get("type") == "text").strip()
    if not text:
        return query
    print(f"[lookup] llm-rewrote: {query!r} → {text!r}", file=sys.stderr)
    return text


def _description_text(entry: dict) -> str:
    """Read the cached `_description.md` body if present.

    Populated by ``tools/archcenter_description_fetcher.py``. Lets the
    scorer match against the full page text (rationale, components,
    recommendations) — much higher recall than the 1-line catalog
    summary alone.
    """
    if not CACHE_DIR.exists():
        return ""
    url = entry.get("url", "") or ""
    m = re.search(r"/solutions/([^/]+)/", url)
    if not m:
        return ""
    description_path = CACHE_DIR / m.group(1) / "_description.md"
    if not description_path.exists():
        return ""
    try:
        return description_path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _score(query_tokens: set[str], entry: dict, description: str = "") -> float:
    """Token-overlap scoring with weighted fields:
        title:        3.0
        tags:         2.0
        services:     1.5
        summary:      1.0
        description:  0.6 (per match, capped at 8 unique tokens)
    """
    score = 0.0
    title_tokens = _tokens(entry.get("title", ""))
    tag_tokens = {t.lower() for t in entry.get("tags", [])}
    svc_tokens = {s.lower() for s in entry.get("services", [])}
    summary_tokens = _tokens(entry.get("summary", ""))
    score += 3.0 * len(query_tokens & title_tokens)
    score += 2.0 * len(query_tokens & tag_tokens)
    score += 1.5 * len(query_tokens & svc_tokens)
    score += 1.0 * len(query_tokens & summary_tokens)
    if description:
        desc_tokens = _tokens(description)
        # Cap at 8 to avoid long descriptions dominating the score.
        score += 0.6 * min(8, len(query_tokens & desc_tokens))
    return score


_CACHE_DIR_INDEX: dict[str, dict[str, str]] | None = None
CACHE_INDEX_FILE = PROJECT_ROOT / "kb" / "diagram" / "assets" / "archcenter-refs-index.json"


def _build_cache_dir_index() -> dict[str, dict[str, str]]:
    """Scan of CACHE_DIR. Returns {folder_name: {ext: relpath}}.

    The previous implementation called ``iterdir()`` + ``rglob`` for
    EVERY catalog entry the scorer touched (123 times) — on WSL2 this
    pushed a single lookup to 75+ seconds. Now:
      1. In-memory cache for the duration of the process.
      2. Persisted JSON index next to the assets, refreshed only when
         CACHE_DIR's mtime changes — so a fresh process reads the
         index in milliseconds instead of walking 113 subdirs through
         WSL2's /mnt/c (~16 s on a typical laptop).
    """
    global _CACHE_DIR_INDEX
    if _CACHE_DIR_INDEX is not None:
        return _CACHE_DIR_INDEX
    if not CACHE_DIR.exists():
        _CACHE_DIR_INDEX = {}
        return _CACHE_DIR_INDEX

    cache_mtime = CACHE_DIR.stat().st_mtime
    if CACHE_INDEX_FILE.exists():
        try:
            payload = json.loads(CACHE_INDEX_FILE.read_text(encoding="utf-8"))
            if payload.get("cache_dir_mtime") == cache_mtime:
                _CACHE_DIR_INDEX = payload.get("entries") or {}
                return _CACHE_DIR_INDEX
        except (OSError, ValueError):
            pass  # fall through and rebuild

    index: dict[str, dict[str, str]] = {}
    for sub in CACHE_DIR.iterdir():
        if not sub.is_dir():
            continue
        bucket: dict[str, str] = {}
        for ext in ("drawio", "png", "svg"):
            for path in sub.rglob(f"*.{ext}"):
                bucket[ext] = str(path.relative_to(PROJECT_ROOT))
                break  # only the first hit per ext is enough
        # Surface the auto-extracted absolute_layout template if present.
        # Agents read this YAML as the spec scaffold (Oracle's canonical
        # geometry) — generated by tools/archcenter_drawio_to_template.py.
        template = sub / "_template.yaml"
        if template.is_file():
            bucket["yaml"] = str(template.relative_to(PROJECT_ROOT))
        if bucket:
            index[sub.name] = bucket

    try:
        CACHE_INDEX_FILE.write_text(
            json.dumps({"cache_dir_mtime": cache_mtime, "entries": index},
                       indent=2),
            encoding="utf-8",
        )
    except OSError:
        pass  # index is still useful in-memory even if we can't persist

    _CACHE_DIR_INDEX = index
    return index


def _cached_assets(entry: dict) -> dict:
    """Find .drawio / .png / .svg / _template.yaml if a matching folder
    is cached locally. Served from the one-shot in-memory index built
    by ``_build_cache_dir_index``.

    The ``yaml`` key (when present) points to ``_template.yaml`` — the
    auto-extracted absolute_layout scaffold from
    ``tools/archcenter_drawio_to_template.py``. Agents should copy this
    YAML as the starting point for a new spec instead of falling back
    to ``examples/`` (which is forbidden as a geometry source).
    """
    cache_index = _build_cache_dir_index()
    if not cache_index:
        return {}
    title_slug = re.sub(r"[^a-z0-9]+", "-", entry.get("title", "").lower()).strip("-")
    url_slug = ""
    if entry.get("url"):
        m = re.search(r"/solutions/([^/]+)/", entry["url"])
        if m:
            url_slug = m.group(1)
    for name, bucket in cache_index.items():
        if (url_slug and (url_slug == name or url_slug in name)) or (name in title_slug):
            return bucket
    return {}


_PATTERNS_BY_URL: dict[str, list[str]] | None = None


def _build_patterns_index() -> dict[str, list[str]]:
    """Load reference-patterns.yaml ONCE and index by entry URL.
    Was being reloaded for every match (125x per lookup = 5s wasted)."""
    global _PATTERNS_BY_URL
    if _PATTERNS_BY_URL is not None:
        return _PATTERNS_BY_URL
    index: dict[str, list[str]] = {}
    if not PATTERNS.exists():
        _PATTERNS_BY_URL = index
        return index
    try:
        patterns_doc = yaml.safe_load(PATTERNS.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        _PATTERNS_BY_URL = index
        return index
    for pname, pdata in (patterns_doc.get("patterns") or {}).items():
        url = (pdata or {}).get("source")
        if url:
            index.setdefault(url, []).append(pname)
    _PATTERNS_BY_URL = index
    return index


def _patterns_for(entry: dict) -> list[str]:
    """Surface visual-convention names that apply to this entry."""
    return _build_patterns_index().get(entry.get("url", ""), [])


def lookup(query: str, top: int = 5, expand_synonyms: bool = True) -> list[dict]:
    catalog = yaml.safe_load(CATALOG.read_text(encoding="utf-8"))
    entries = catalog.get("entries", [])
    qt = _tokens(query)
    if expand_synonyms:
        qt = _expand_query_tokens(qt)
    scored = []
    # Two-pass scoring: cheap fields first (title/tags/services/summary),
    # then enrich the top-K with expensive fields (description text from
    # disk, cached_assets, visual_patterns). Previously _cached_assets
    # ran for every entry whose tokens overlapped at all — 121 of 123
    # entries on a typical query — pushing the lookup to 75s+ on WSL2.
    light: list[dict] = []
    for e in entries:
        s_light = _score(qt, e, description="")
        if s_light <= 0:
            continue
        light.append({"_entry": e, "_score_light": s_light})

    # Re-rank the candidate set with description text for tie-breaking
    # accuracy, then keep ``top`` * 2 to leave room for description
    # bumps to reorder.
    pool_size = max(top * 3, 10)
    light.sort(key=lambda r: -r["_score_light"])
    candidates = light[:pool_size]
    for c in candidates:
        e = c["_entry"]
        description = _description_text(e)
        c["_description"] = description
        c["_score_full"] = _score(qt, e, description=description)
    candidates.sort(key=lambda r: -r["_score_full"])

    for c in candidates[:top]:
        e = c["_entry"]
        scored.append({
            "score": round(c["_score_full"], 1),
            "title": e.get("title"),
            "url": e.get("url"),
            "tags": e.get("tags", []),
            "services": e.get("services", []),
            "summary": (e.get("summary", "") or "").strip().split("\n")[0],
            "cached_assets": _cached_assets(e),
            "visual_patterns": _patterns_for(e),
            "has_description": bool(c.get("_description")),
        })
    return scored


def _print_results(query: str, results: list[dict]) -> None:
    if not results:
        print(f"No matches for: {query}")
        return
    print(f"Top {len(results)} matches for: {query!r}\n")
    for i, r in enumerate(results, 1):
        print(f"{i}. [{r['score']}]  {r['title']}")
        print(f"   URL: {r['url']}")
        print(f"   tags: {', '.join(r['tags'])}")
        if r["services"]:
            print(f"   services: {', '.join(r['services'])}")
        if r["cached_assets"]:
            print(f"   cached: {', '.join(f'{k}={v}' for k, v in r['cached_assets'].items())}")
        if r["visual_patterns"]:
            print(f"   visual_patterns: {', '.join(r['visual_patterns'])}")
        if r.get("has_description"):
            print(f"   has cached _description.md")
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="*",
                        help="Free-text topology prompt (e.g. 'aws fastconnect exacs').")
    parser.add_argument("--queries", action="append", default=[],
                        help="Run multiple sub-queries and report top-K for each. "
                        "Use when the desired architecture combines patterns "
                        "no single Oracle ref-arch covers (e.g. "
                        "--queries 'mysql heatwave' --queries 'load balancer ha').")
    parser.add_argument("--top", type=int, default=5,
                        help="Number of matches to return per query (default 5).")
    parser.add_argument("--format", choices=("text", "yaml"), default="text")
    parser.add_argument("--no-synonyms", action="store_true",
                        help="Disable query-token expansion via "
                        "kb/architecture-center/synonyms.yaml.")
    parser.add_argument("--llm-rewrite", action="store_true",
                        help="Rewrite the query via the Anthropic API "
                        "before scoring (opt-in; requires "
                        "ANTHROPIC_API_KEY). Useful for natural-language "
                        "queries the synonym table doesn't cover.")
    parser.add_argument("--rebuild-index", action="store_true",
                        help="Force-rebuild the cached archcenter-refs "
                        "index (kb/diagram/assets/archcenter-refs-index.json). "
                        "Use after a manual KB edit if mtime didn't bump.")
    args = parser.parse_args()
    if args.rebuild_index and CACHE_INDEX_FILE.exists():
        CACHE_INDEX_FILE.unlink()
        print(f"[lookup] removed stale index at {CACHE_INDEX_FILE.relative_to(PROJECT_ROOT)}",
              file=sys.stderr)

    queries: list[str] = list(args.queries)
    if args.query:
        queries.append(" ".join(args.query))
    if not queries:
        parser.error("Provide a positional query or --queries.")

    expand = not args.no_synonyms
    if args.llm_rewrite:
        queries = [_llm_rewrite_query(q) for q in queries]
    if args.format == "yaml":
        bundle = {q: lookup(q, top=args.top, expand_synonyms=expand) for q in queries}
        print(yaml.safe_dump(bundle if len(queries) > 1 else bundle[queries[0]],
                             sort_keys=False, allow_unicode=True))
        return

    for idx, q in enumerate(queries):
        if idx > 0:
            print("─" * 60)
        _print_results(q, lookup(q, top=args.top, expand_synonyms=expand))


if __name__ == "__main__":
    main()
