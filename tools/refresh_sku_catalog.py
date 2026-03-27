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
    parser.add_argument("--validate", action="store_true",
                        help="Validate catalog prices against API")
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
    elif args.refresh:
        refresh_catalog(verbose=args.verbose or args.diff)
    elif args.validate:
        validate_catalog(verbose=args.verbose)
    elif args.dump:
        dump_all(args.dump, verbose=args.verbose)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
