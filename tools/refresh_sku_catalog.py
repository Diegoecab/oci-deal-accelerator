#!/usr/bin/env python3
"""
OCI Deal Accelerator — SKU Catalog Refresh Tool

Fetches current OCI SKU pricing from Oracle's public pricing API and
updates kb/pricing/oci-sku-catalog.yaml with the latest prices.

API endpoint (anonymous, no auth required):
  https://itra.oraclecloud.com/itas/.anon/myservices/api/v1/products

Usage:
    # Refresh full catalog from API
    python tools/refresh_sku_catalog.py --refresh

    # Refresh and show what changed
    python tools/refresh_sku_catalog.py --refresh --diff

    # Fetch a specific SKU to inspect
    python tools/refresh_sku_catalog.py --sku B110627

    # Export raw API dump to JSON (for debugging)
    python tools/refresh_sku_catalog.py --dump oci-skus-raw.json

    # Validate current catalog against API (report stale prices)
    python tools/refresh_sku_catalog.py --validate
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import date
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: 'requests' package required. Install with: pip install requests")
    sys.exit(1)

import yaml

# ── API Configuration ─────────────────────────────────────────────
# Public Oracle pricing API (no authentication required)
# Documented: https://docs.oracle.com/en-us/iaas/Content/GSG/Tasks/signingup_topic-Estimating_Costs.htm
API_BASE = "https://apexapps.oracle.com/pls/apex/cetools/api/v1/products/"
DEFAULT_CURRENCY = "USD"

# ── Paths ─────────────────────────────────────────────────────────
TOOLS_DIR = Path(__file__).resolve().parent
CATALOG_PATH = TOOLS_DIR.parent / "kb" / "pricing" / "oci-sku-catalog.yaml"
COMPUTE_DOMAIN_PATH = TOOLS_DIR.parent / "kb" / "pricing" / "compute.yaml"

# ── Domain refresh registry ───────────────────────────────────────
# Maps a domain key (used by --refresh-domain) to its file path and
# refresher function. Add a new entry here to support more domains.
DOMAIN_REGISTRY = {
    "compute": {
        "path": COMPUTE_DOMAIN_PATH,
        "refresher": "refresh_compute_yaml",
    },
}


def fetch_all_products(currency="USD", verbose=False):
    """Fetch all OCI products from the APEX pricing API."""
    url = "{}?currencyCode={}".format(API_BASE, currency)
    if verbose:
        print("  Fetching: {}".format(url))

    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    items = data.get("items", [])
    if verbose:
        print("  Fetched {} products".format(len(items)))
        last_updated = data.get("lastUpdated", "unknown")
        print("  API last updated: {}".format(last_updated))
    return items


def fetch_single_sku(part_number, currency="USD"):
    """Fetch a single SKU by part number."""
    url = "{}?partNumber={}&currencyCode={}".format(API_BASE, part_number, currency)
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return data.get("items", [])


def extract_payg_price(product, currency="USD"):
    """Extract the Pay As You Go price from a product's prices structure.

    APEX API format:
      currencyCodeLocalizations: [
        { currencyCode: "USD", prices: [ {model: "PAY_AS_YOU_GO", value: 2.9032} ] }
      ]
    """
    localizations = product.get("currencyCodeLocalizations", [])
    for loc in localizations:
        if loc.get("currencyCode") == currency:
            for price in loc.get("prices", []):
                if price.get("model") == "PAY_AS_YOU_GO":
                    return price.get("value", 0)
            # Fallback: take first price in this currency
            prices = loc.get("prices", [])
            if prices:
                return prices[0].get("value", 0)

    # Legacy format fallback (itra API)
    for price in product.get("prices", []):
        if price.get("model") == "PAY_AS_YOU_GO":
            return price.get("value", 0)

    return 0


def load_current_catalog():
    """Load the current YAML catalog and build a SKU lookup."""
    if not CATALOG_PATH.exists():
        return {}, {}

    with open(str(CATALOG_PATH), "r") as f:
        raw = yaml.safe_load(f)

    sku_map = {}  # sku -> {product, category, ...}
    categories = raw.get("categories", {})
    for cat_key, cat_data in categories.items():
        for entry in cat_data.get("skus", []):
            sku_map[str(entry["sku"])] = {
                "category": cat_key,
                "product": entry.get("product", ""),
                "list_price_usd": entry.get("list_price_usd", 0),
            }

    return raw, sku_map


def refresh_catalog(verbose=False):
    """Refresh the catalog YAML with latest API prices."""
    print("Fetching current prices from Oracle API...")
    products = fetch_all_products(currency=DEFAULT_CURRENCY, verbose=verbose)

    # Build API lookup: partNumber -> product data
    api_map = {}
    for p in products:
        pn = p.get("partNumber", "")
        if pn:
            api_map[pn] = p

    print("  {} products from API".format(len(api_map)))

    # Load current catalog
    raw, sku_map = load_current_catalog()
    if not raw:
        print("Error: Could not load catalog at {}".format(CATALOG_PATH))
        return

    updated = 0
    not_found = 0
    unchanged = 0

    categories = raw.get("categories", {})
    for cat_key, cat_data in categories.items():
        for entry in cat_data.get("skus", []):
            sku = str(entry["sku"])
            if sku in api_map:
                api_price = extract_payg_price(api_map[sku])
                old_price = entry.get("list_price_usd", 0)

                # Skip $0 API prices when catalog has a real price
                # (API returns $0 for tiered/free-tier SKUs where
                # the base tier is free but usage above free tier costs)
                if api_price == 0 and old_price > 0:
                    if verbose:
                        print("  {} SKIP: API=$0 but catalog=${} (tiered/free-tier SKU)".format(
                            sku, old_price
                        ))
                    unchanged += 1
                elif abs(api_price - old_price) > 0.0001:
                    if verbose:
                        print("  {} price: {} -> {} ({})".format(
                            sku, old_price, api_price, entry.get("product", "")[:50]
                        ))
                    entry["list_price_usd"] = api_price
                    updated += 1
                else:
                    unchanged += 1

                # Also update product name if different
                api_name = api_map[sku].get("displayName", "")
                if api_name and api_name != entry.get("product", ""):
                    # Keep our shorter names, but log the difference
                    pass

                # Update metric from API
                api_metric = api_map[sku].get("metricDisplayName", "")
                if api_metric and api_metric != entry.get("metric", ""):
                    pass  # Keep our curated metrics
            else:
                not_found += 1
                if verbose:
                    print("  {} NOT in API (may be retired): {}".format(
                        sku, entry.get("product", "")[:50]
                    ))

    # Update last_verified date
    raw["last_verified"] = date.today().isoformat()

    # Write back
    with open(str(CATALOG_PATH), "w") as f:
        yaml.dump(raw, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120)

    print("\nRefresh complete:")
    print("  Updated:   {}".format(updated))
    print("  Unchanged: {}".format(unchanged))
    print("  Not in API (possibly retired): {}".format(not_found))
    print("  Catalog saved: {}".format(CATALOG_PATH))

    # Reverse-direction check: SKUs in API we haven't catalogued yet.
    catalog_skus_after = {str(e["sku"]) for cat in raw.get("categories", {}).values()
                         for e in cat.get("skus", [])}
    stub_map = {s: {} for s in catalog_skus_after}
    new_skus = discover_missing_skus(api_map, stub_map, verbose=verbose)
    print_missing_skus(new_skus, limit=None if verbose else 20)


def validate_catalog(verbose=False):
    """Compare current catalog prices against API and report differences."""
    print("Validating catalog against Oracle API...")
    products = fetch_all_products(currency=DEFAULT_CURRENCY, verbose=verbose)

    api_map = {}
    for p in products:
        pn = p.get("partNumber", "")
        if pn:
            api_map[pn] = p

    raw, sku_map = load_current_catalog()
    if not raw:
        print("Error: Could not load catalog")
        return

    diffs = []
    missing = []

    categories = raw.get("categories", {})
    for cat_key, cat_data in categories.items():
        for entry in cat_data.get("skus", []):
            sku = str(entry["sku"])
            if sku in api_map:
                api_price = extract_payg_price(api_map[sku])
                cat_price = entry.get("list_price_usd", 0)
                # Skip $0 API prices for tiered/free-tier SKUs
                if api_price == 0 and cat_price > 0:
                    continue
                if abs(api_price - cat_price) > 0.0001:
                    diffs.append({
                        "sku": sku,
                        "product": entry.get("product", "")[:60],
                        "catalog_price": cat_price,
                        "api_price": api_price,
                        "diff_pct": ((api_price - cat_price) / cat_price * 100) if cat_price else 0,
                    })
            else:
                missing.append(sku)

    if diffs:
        print("\nPrice differences found ({}):\n".format(len(diffs)))
        print("{:<10} {:<60} {:>12} {:>12} {:>8}".format(
            "SKU", "Product", "Catalog", "API", "Diff %"
        ))
        print("-" * 102)
        for d in diffs:
            print("{:<10} {:<60} ${:>10.4f} ${:>10.4f} {:>7.1f}%".format(
                d["sku"], d["product"], d["catalog_price"], d["api_price"], d["diff_pct"]
            ))
        print("\nRun with --refresh to update the catalog.")
    else:
        print("\nAll prices match the API. Catalog is up to date.")

    if missing:
        print("\n{} SKUs not found in API (possibly retired):".format(len(missing)))
        for s in missing[:10]:
            print("  - {}".format(s))
        if len(missing) > 10:
            print("  ... and {} more".format(len(missing) - 10))

    # Reverse-direction check: SKUs in API we haven't catalogued yet.
    new_skus = discover_missing_skus(api_map, sku_map, verbose=verbose)
    print_missing_skus(new_skus, limit=None if verbose else 20)


def discover_missing_skus(api_map, catalog_sku_map, verbose=False):
    """Find SKUs present in the API but missing from the catalog.

    The filter is auto-derived: we collect every `serviceCategory` value for
    SKUs already in the catalog and only report new SKUs whose serviceCategory
    falls within that curated set. This keeps the report relevant — as new
    categories are added to the catalog, the discovery scope expands.
    """
    curated_categories = set()
    for sku in catalog_sku_map:
        if sku in api_map:
            sc = api_map[sku].get("serviceCategory", "") or ""
            if sc:
                curated_categories.add(sc)

    if verbose:
        print("  Curated serviceCategory values ({}): {}".format(
            len(curated_categories), ", ".join(sorted(curated_categories))
        ))

    missing = []
    for sku, product in api_map.items():
        if sku in catalog_sku_map:
            continue
        sc = product.get("serviceCategory", "") or ""
        if sc not in curated_categories:
            continue
        missing.append({
            "sku": sku,
            "product": product.get("displayName", ""),
            "service_category": sc,
            "metric": product.get("metricName", ""),
            "price": extract_payg_price(product),
        })
    missing.sort(key=lambda x: (x["service_category"], x["sku"]))
    return missing


def print_missing_skus(missing, limit=None):
    """Print a readable report of missing SKUs, grouped by serviceCategory."""
    if not missing:
        print("\nNo new SKUs discovered in curated categories. Catalog covers the API well.")
        return

    print("\n{} SKUs present in API but missing from catalog".format(len(missing)))
    print("(filtered to serviceCategory values already represented in our catalog)\n")

    by_cat = {}
    for m in missing:
        by_cat.setdefault(m["service_category"], []).append(m)

    shown = 0
    truncated = False
    for cat, items in sorted(by_cat.items()):
        print("  [{}]  ({} new)".format(cat, len(items)))
        for m in items:
            if limit is not None and shown >= limit:
                truncated = True
                break
            price_str = "${:.4f}".format(m["price"]) if m["price"] else "    -"
            print("    {:<10} {:>10}  {}".format(
                m["sku"], price_str, m["product"][:70]
            ))
            shown += 1
        if truncated:
            break

    if truncated:
        print("\n  ... and {} more (re-run with -v to list all)".format(len(missing) - shown))

    print("\nNext step: review and add relevant entries to kb/pricing/oci-sku-catalog.yaml")
    print("           under the appropriate category block.")


def discover_catalog(verbose=False):
    """Stand-alone --discover entry point: report new API SKUs not yet in catalog."""
    print("Fetching current products from Oracle API...")
    products = fetch_all_products(currency=DEFAULT_CURRENCY, verbose=verbose)
    api_map = {}
    for p in products:
        pn = p.get("partNumber", "")
        if pn:
            api_map[pn] = p

    raw, sku_map = load_current_catalog()
    if not raw:
        print("Error: Could not load catalog at {}".format(CATALOG_PATH))
        return 1

    missing = discover_missing_skus(api_map, sku_map, verbose=verbose)
    print_missing_skus(missing, limit=None if verbose else 40)
    # Machine-readable summary for CI/automation — always last line on stdout.
    print("\nDISCOVER_MISSING_COUNT={}".format(len(missing)))
    return 0


def inspect_sku(part_number):
    """Fetch and display a single SKU from the API."""
    print("Fetching SKU {} from API...".format(part_number))
    items = fetch_single_sku(part_number)
    if not items:
        print("  SKU not found in API")
        return

    for item in items:
        print("\n  Part Number:  {}".format(item.get("partNumber", "")))
        print("  Display Name: {}".format(item.get("displayName", "")))
        print("  Category:     {}".format(item.get("serviceCategory", "N/A")))
        print("  Metric:       {}".format(item.get("metricName", "N/A")))
        print("  Prices:")
        for loc in item.get("currencyCodeLocalizations", []):
            cc = loc.get("currencyCode", "?")
            for price in loc.get("prices", []):
                print("    - {} {} : {}".format(
                    cc, price.get("model", "?"), price.get("value", "?")
                ))


# ── Domain refresh: compute ───────────────────────────────────────

# Compute family token regex. Matches the family token (E3-E6, A1/A2/A4, X9)
# inside shape names like VM.Standard.E6.Flex, BM.Standard.E5, BM.Standard.x9.
_COMPUTE_FAMILY_RE = re.compile(r'\b(E[3-6]|A[1-4]|X9|x9)\b')


def _shape_family(shape_name):
    """Return the family token (E5, A2, X9, ...) used in API displayName,
    or None if the shape can't be mapped automatically.

    Special case: VM.Optimized3.Flex maps to the 'Optimized X9' product line.
    """
    if "Optimized3" in shape_name or "Optimized" in shape_name:
        return "X9_OPTIMIZED"
    m = _COMPUTE_FAMILY_RE.search(shape_name)
    if m:
        return m.group(1).upper()
    return None


def build_compute_family_lookup(api_map):
    """Scan the API for Compute Standard / Optimized OCPU and Memory products,
    return {family: {'ocpu': price, 'memory': price, 'ocpu_sku': sku, 'memory_sku': sku}}.
    """
    lookup = {}
    for sku, product in api_map.items():
        name = product.get("displayName", "")
        if "Compute" not in name:
            continue
        if "Cloud@Customer" in name:
            continue
        if "Dense I/O" in name or "Dense IO" in name:
            continue  # different pricing tier
        if "HPC" in name:
            continue
        if "VMware" in name:
            continue
        if "GPU" in name:
            continue  # GPU shapes not handled in this domain refresher

        is_optimized = "Optimized" in name
        is_standard = "Standard" in name
        if not (is_optimized or is_standard):
            continue

        # Find the family token in the displayName
        m = _COMPUTE_FAMILY_RE.search(name)
        if not m:
            continue
        family = m.group(1).upper()
        if is_optimized:
            family = "X9_OPTIMIZED"

        metric = product.get("metricName", "")
        price = extract_payg_price(product)

        slot = lookup.setdefault(family, {})
        if "OCPU" in metric.upper():
            # Prefer the first match (deterministic across runs since API order is stable)
            slot.setdefault("ocpu", price)
            slot.setdefault("ocpu_sku", sku)
        elif "GIGABYTE" in metric.upper() or "Gigabytes" in metric:
            slot.setdefault("memory", price)
            slot.setdefault("memory_sku", sku)

    return lookup


def _load_multidoc_yaml(path):
    """Load a multi-doc YAML file (frontmatter + body) and return both as dicts."""
    with open(str(path), "r", encoding="utf-8") as fh:
        docs = list(yaml.safe_load_all(fh))
    frontmatter = {}
    body = {}
    for d in docs:
        if not isinstance(d, dict):
            continue
        # Frontmatter typically has last_verified, source, description, currency
        if "last_verified" in d or "source" in d or "currency" in d:
            frontmatter.update(d)
        else:
            body.update(d)
    return frontmatter, body


def _save_multidoc_yaml(path, frontmatter, body):
    """Write frontmatter + body as a two-doc YAML file."""
    with open(str(path), "w", encoding="utf-8") as fh:
        yaml.safe_dump(frontmatter, fh, default_flow_style=False, sort_keys=False, allow_unicode=True)
        fh.write("---\n")
        yaml.safe_dump(body, fh, default_flow_style=False, sort_keys=False, allow_unicode=True, width=120)


def refresh_compute_yaml(verbose=False):
    """Refresh kb/pricing/compute.yaml from the live API.

    Updates ocpu_per_hour, memory_per_gb_hour, and monthly_730h for shapes
    in flexible_shapes and bare_metal_shapes. Skips GPU shapes (out of scope).
    Preserves notes, free_tier, gpu_model, and other manual fields.
    """
    print("Fetching current prices from Oracle API...")
    products = fetch_all_products(currency=DEFAULT_CURRENCY, verbose=verbose)
    api_map = {p.get("partNumber", ""): p for p in products if p.get("partNumber")}
    print("  {} products from API".format(len(api_map)))

    family_prices = build_compute_family_lookup(api_map)
    if verbose:
        print("\n  Family lookup built:")
        for fam, prices in sorted(family_prices.items()):
            print("    {:<14} OCPU=${:.4f}  Memory=${:.4f}".format(
                fam, prices.get("ocpu", 0), prices.get("memory", 0)
            ))

    print("\nLoading {}...".format(COMPUTE_DOMAIN_PATH))
    frontmatter, body = _load_multidoc_yaml(COMPUTE_DOMAIN_PATH)

    updated = []
    skipped = []

    def update_shape(section_name, shape_name, shape_data, has_memory=True):
        family = _shape_family(shape_name)
        if not family or family not in family_prices:
            skipped.append((section_name, shape_name, "no API match"))
            return
        prices = family_prices[family]
        new_ocpu = prices.get("ocpu")
        new_memory = prices.get("memory")
        if new_ocpu is None:
            skipped.append((section_name, shape_name, "no OCPU price"))
            return

        old_ocpu = shape_data.get("ocpu_per_hour") or 0
        old_memory = shape_data.get("memory_per_gb_hour") or 0

        # Protect against API returning $0 for tiered/free-tier SKUs (e.g. A1 Always Free).
        # Same convention as refresh_catalog(): keep the existing value if it's > 0.
        if new_ocpu == 0 and old_ocpu > 0:
            skipped.append((section_name, shape_name, "API returned $0 (free tier) — kept existing"))
            return
        if has_memory and new_memory == 0 and old_memory > 0:
            skipped.append((section_name, shape_name, "API returned $0 memory (free tier) — kept existing"))
            return

        shape_data["ocpu_per_hour"] = new_ocpu

        if has_memory and new_memory is not None:
            shape_data["memory_per_gb_hour"] = new_memory

            # Recompute monthly_730h block if present
            if "monthly_730h" in shape_data:
                shape_data["monthly_730h"] = {
                    "ocpu": round(new_ocpu * 730, 2),
                    "memory_per_gb": round(new_memory * 730, 2),
                }
            updated.append((section_name, shape_name, family, old_ocpu, new_ocpu, old_memory, new_memory))
        else:
            updated.append((section_name, shape_name, family, old_ocpu, new_ocpu, None, None))

    for shape_name, shape_data in (body.get("flexible_shapes") or {}).items():
        if isinstance(shape_data, dict):
            update_shape("flexible_shapes", shape_name, shape_data, has_memory=True)

    for shape_name, shape_data in (body.get("bare_metal_shapes") or {}).items():
        if isinstance(shape_data, dict):
            update_shape("bare_metal_shapes", shape_name, shape_data, has_memory=False)

    # Update frontmatter: bump last_verified, replace stale source, drop NEEDS REVIEW
    # (the comment block lives only in the source text and is dropped on round-trip)
    frontmatter["last_verified"] = date.today().isoformat()
    frontmatter["source"] = API_BASE
    frontmatter["description"] = (
        "OCI Compute pricing for estimation purposes. Auto-refreshed from the "
        "Oracle public pricing API by tools/refresh_sku_catalog.py --refresh-domain compute. "
        "GPU shapes, secure desktops, estimation_helpers, and discounts are NOT auto-refreshed."
    )

    # Recompute estimation_helpers from the new E5 / A1 prices, since the
    # hardcoded `monthly` values are derived from them.
    _recompute_compute_estimation_helpers(body)

    _save_multidoc_yaml(COMPUTE_DOMAIN_PATH, frontmatter, body)

    print("\nRefresh complete:")
    print("  Shapes updated: {}".format(len(updated)))
    print("  Shapes skipped: {}".format(len(skipped)))
    if verbose or updated:
        print("\nUpdated shapes:")
        for section, name, family, old_o, new_o, old_m, new_m in updated:
            mem = ""
            if old_m is not None:
                mem = "  mem ${:.4f}->${:.4f}".format(old_m, new_m)
            print("  [{}] {} ({}): OCPU ${:.4f}->${:.4f}{}".format(
                section, name, family, old_o or 0, new_o, mem
            ))
    if skipped:
        print("\nSkipped shapes (no API match — preserve existing values):")
        for section, name, reason in skipped:
            print("  [{}] {}  ({})".format(section, name, reason))
    print("\nFile saved: {}".format(COMPUTE_DOMAIN_PATH))


def _recompute_compute_estimation_helpers(body):
    """Recompute the hardcoded `monthly` values in estimation_helpers from
    the (now fresh) E5 and A1 prices. Best-effort: if the referenced shape
    is missing, leave the helper unchanged.
    """
    helpers = body.get("estimation_helpers") or {}
    flex = body.get("flexible_shapes") or {}

    # Configs are: (helper_key, shape_name, ocpu_count, memory_gb)
    rules = [
        ("typical_app_server", "VM.Standard.E5.Flex", 4, 64),
        ("typical_web_server", "VM.Standard.E5.Flex", 2, 16),
        ("typical_bastion", "VM.Standard.E5.Flex", 1, 8),
        ("typical_arm_app_server", "VM.Standard.A1.Flex", 4, 24),
    ]

    for helper_key, shape_name, ocpus, mem_gb in rules:
        if helper_key not in helpers:
            continue
        shape = flex.get(shape_name)
        if not isinstance(shape, dict):
            continue
        ocpu_h = shape.get("ocpu_per_hour")
        mem_h = shape.get("memory_per_gb_hour")
        if ocpu_h is None or mem_h is None:
            continue
        # 730 hours per month convention (matches the rest of the file)
        monthly = round((ocpus * ocpu_h * 730) + (mem_gb * mem_h * 730), 2)
        helpers[helper_key]["monthly"] = monthly


def refresh_domain(domain_key, verbose=False):
    """Dispatch to the registered domain refresher."""
    if domain_key not in DOMAIN_REGISTRY:
        print("Unknown domain: {}. Available: {}".format(
            domain_key, ", ".join(sorted(DOMAIN_REGISTRY.keys()))
        ))
        return 1
    refresher_name = DOMAIN_REGISTRY[domain_key]["refresher"]
    refresher = globals()[refresher_name]
    refresher(verbose=verbose)
    return 0


def dump_all(output_path, verbose=False):
    """Dump raw API response to JSON file."""
    products = fetch_all_products(currency=DEFAULT_CURRENCY, verbose=verbose)
    with open(output_path, "w") as f:
        json.dump(products, f, indent=2)
    print("Dumped {} products to {}".format(len(products), output_path))


def main():
    parser = argparse.ArgumentParser(
        description="OCI Deal Accelerator — SKU Catalog Refresh Tool"
    )
    parser.add_argument("--refresh", action="store_true",
                        help="Refresh catalog prices from Oracle API")
    parser.add_argument("--refresh-domain", type=str, metavar="DOMAIN",
                        choices=sorted(DOMAIN_REGISTRY.keys()),
                        help="Refresh a domain pricing file from the API "
                             "(currently: compute)")
    parser.add_argument("--validate", action="store_true",
                        help="Validate catalog prices against API")
    parser.add_argument("--discover", action="store_true",
                        help="Report SKUs present in API but missing from catalog "
                             "(filtered to serviceCategory values already curated)")
    parser.add_argument("--sku", type=str,
                        help="Inspect a single SKU from the API")
    parser.add_argument("--dump", type=str, metavar="FILE",
                        help="Dump raw API data to JSON file")
    parser.add_argument("--diff", action="store_true",
                        help="Show detailed price changes during refresh")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Verbose output")
    args = parser.parse_args()

    if args.sku:
        inspect_sku(args.sku)
    elif args.refresh_domain:
        return refresh_domain(args.refresh_domain, verbose=args.verbose or args.diff)
    elif args.refresh:
        refresh_catalog(verbose=args.verbose or args.diff)
    elif args.validate:
        validate_catalog(verbose=args.verbose)
    elif args.discover:
        return discover_catalog(verbose=args.verbose)
    elif args.dump:
        dump_all(args.dump, verbose=args.verbose)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
