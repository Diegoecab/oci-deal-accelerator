#!/usr/bin/env python3
"""
Refresh the Architecture Center catalog from Oracle docs.

Usage:
    python tools/refresh_arch_catalog.py --url https://docs.oracle.com/en/solutions/{slug}/index.html
    python tools/refresh_arch_catalog.py --whats-new
    python tools/refresh_arch_catalog.py --validate

This script:
1. Fetches the What's New pages for 2024 and 2025
2. Extracts all reference architecture links
3. For each link, fetches the detail page
4. Extracts title, summary, services, recommendations
5. Writes/updates kb/architecture-center/catalog.yaml

IMPORTANT: This is a semi-automated tool. It generates DRAFT entries
that should be reviewed by a human before committing. The auto-generated
summaries may miss nuance or include irrelevant detail.

Requirements: pip install requests beautifulsoup4 pyyaml
"""

import argparse
import os
import re
import sys
import time
from datetime import datetime
from urllib.parse import urljoin

import requests
import yaml
from bs4 import BeautifulSoup

CATALOG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "kb", "architecture-center", "catalog.yaml",
)

WHATS_NEW_URLS = [
    "https://docs.oracle.com/en/solutions/oracle-architecture-center/whats-new-20251.html",
    "https://docs.oracle.com/en/solutions/oracle-architecture-center/whats-new-2024.html",
]

# ---------------------------------------------------------------------------
# Service name detection patterns
# ---------------------------------------------------------------------------
SERVICE_PATTERNS = {
    "adb-s": r"Autonomous\s+(Database|Transaction|Data\s+Warehouse)\s+Serverless|ADB-S|ATP\s+Serverless|Autonomous\s+(Database|Transaction|Data\s+Warehouse)(?!.*Dedicated)",
    "adb-d": r"Autonomous\s+Database\s+on\s+Dedicated|ADB-D|Dedicated\s+Exadata\s+Infrastructure",
    "exacs": r"Exadata\s+(Cloud|Database)\s+Service|ExaCS|ExaDB-D",
    "exascale": r"Exascale",
    "base-db": r"Base\s+Database|VM\s+DB|DB\s+System|Oracle\s+Database\s+Service",
    "oke": r"Kubernetes\s+Engine|OKE|Container\s+Engine\s+for\s+Kubernetes",
    "compute": r"Compute\s+(Instance|VM)|Virtual\s+Machine|Bare\s+Metal",
    "functions": r"OCI\s+Functions|Functions\s+Service",
    "vcn": r"Virtual\s+Cloud\s+Network|VCN",
    "load-balancer": r"Load\s+Balanc",
    "waf": r"Web\s+Application\s+Firewall|WAF",
    "fastconnect": r"FastConnect",
    "drg": r"Dynamic\s+Routing\s+Gateway|DRG",
    "object-storage": r"Object\s+Storage",
    "block-storage": r"Block\s+Volume|Block\s+Storage",
    "file-storage": r"File\s+Storage|FSS",
    "data-safe": r"Data\s+Safe",
    "vault": r"OCI\s+Vault|Key\s+Management|Key\s+Vault",
    "cloud-guard": r"Cloud\s+Guard",
    "goldengate": r"GoldenGate",
    "oic": r"Oracle\s+Integration(?!\s+3)|OIC",
    "oic3": r"Oracle\s+Integration\s+3",
    "data-integration": r"Data\s+Integration",
    "streaming": r"OCI\s+Streaming|Streaming\s+Service",
    "monitoring": r"OCI\s+Monitoring|Stack\s+Monitoring",
    "logging": r"Logging\s+Analytics",
    "bastion": r"Bastion",
    "apex": r"Oracle\s+APEX|APEX\s+application",
    "mysql": r"MySQL\s+(Database\s+)?Service|MySQL\s+HeatWave",
    "nosql": r"NoSQL\s+Database",
    "postgresql": r"PostgreSQL",
    "opensearch": r"OpenSearch",
    "redis": r"OCI\s+Cache|Redis",
    "adw": r"Autonomous\s+Data\s+Warehouse|ADW",
    "api-gateway": r"API\s+Gateway",
    "dns": r"OCI\s+DNS|DNS\s+Service",
    "wls": r"WebLogic",
    "soa": r"SOA\s+Suite",
    "genai": r"Generative\s+AI|GenAI|OCI\s+AI\s+Agent",
    "ai-services": r"OCI\s+AI\s+Services|Vision\s+AI|Language\s+AI|Speech\s+AI|Document\s+Understanding",
    "data-science": r"Data\s+Science|ML\s+Pipeline",
    "data-catalog": r"Data\s+Catalog",
    "ops-insights": r"Ops\s+Insights|Operations\s+Insights",
    "apm": r"Application\s+Performance\s+Monitoring|APM",
    "fsdr": r"Full\s+Stack\s+Disaster\s+Recovery|FSDR",
    "ocvs": r"VMware\s+Solution|OCVS",
    "secure-desktops": r"Secure\s+Desktops",
    "azure": r"Database@Azure|Oracle\s+Database@Azure",
    "aws": r"Database@AWS|Oracle\s+Database@AWS",
    "google-cloud": r"Database@Google|Oracle\s+Database@Google",
}

TAG_PATTERNS = {
    "database": r"database|autonomous|exadata|rac|mysql|nosql|postgresql|base\s+db",
    "migration": r"migrat|move\s+to|zero\s+downtime\s+migration|zdm|data\s+pump",
    "ha-dr": r"high\s+availability|disaster\s+recovery|data\s+guard|failover|MAA|standby|far\s+sync",
    "security": r"secur|encrypt|vault|data\s+safe|cloud\s+guard|compliance|zero.trust|tls|certificate",
    "networking": r"network|vcn|subnet|fastconnect|vpn|drg|load\s+balanc|dns|hub.spoke",
    "multicloud": r"multicloud|multi-cloud|azure|aws|google\s+cloud|database@",
    "integration": r"integrat|oic|streaming|goldengate|data\s+flow|kafka",
    "data-platform": r"data\s+lake|data\s+warehouse|analytics|data\s+platform|lakehouse",
    "application": r"apex|ords|kubernetes|container|weblogic|tomcat|microservice|e-business|peoplesoft|siebel|jd\s+edwards",
    "ai-ml": r"machine\s+learning|ai\s+|generative|vector|select\s+ai|llm|rag|chatbot|agent",
    "autonomous": r"autonomous\s+database|adb|auto-scal",
    "observability": r"monitor|logging|apm|ops\s+insights|observability|stack\s+monitoring",
    "devops": r"ci/cd|devops|github|gitlab|jenkins|pipeline|gitops",
    "hpc": r"hpc|gpu|bare\s+metal\s+gpu|high.performance\s+computing",
    "iot": r"iot|internet\s+of\s+things",
    "healthcare": r"healthcare|dicom|hl7|fhir",
    "ebs": r"e-business\s+suite|ebs",
    "peoplesoft": r"peoplesoft",
    "vmware": r"vmware|ocvs|vsan",
}


def detect_services(text):
    """Auto-detect OCI services mentioned in text."""
    found = []
    for svc, pattern in SERVICE_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            found.append(svc)
    return sorted(set(found))


def detect_tags(text):
    """Auto-detect topic tags from text."""
    found = []
    for tag, pattern in TAG_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            found.append(tag)
    return sorted(set(found))


def fetch_page(url, delay=1.0):
    """Fetch a page with rate limiting."""
    time.sleep(delay)
    headers = {"User-Agent": "OCI-Deal-Accelerator-CatalogBuilder/1.0"}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def extract_entry(url):
    """Extract catalog entry from a reference architecture page."""
    try:
        soup = fetch_page(url)

        title = soup.find("h1")
        title_text = title.get_text(strip=True) if title else "Unknown"

        # Get all text for service/tag detection
        body = soup.get_text(" ", strip=True)

        # Extract first 2-3 meaningful sentences as summary
        paragraphs = soup.find_all("p")
        summary_parts = []
        for p in paragraphs[:8]:
            text = p.get_text(strip=True)
            if len(text) > 50 and "Copyright" not in text and "cookie" not in text.lower():
                summary_parts.append(text)
                if len(" ".join(summary_parts)) > 300:
                    break

        summary = " ".join(summary_parts)[:500]

        # Detect services and tags
        services = detect_services(body)
        tags = detect_tags(body)

        # Detect type
        entry_type = "reference-architecture"
        if "playbook" in body.lower():
            entry_type = "solution-playbook"
        elif "built and deployed" in body.lower():
            entry_type = "built-deployed"

        # Find terraform/github links
        terraform = None
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "github.com" in href.lower() and "oracle" in href.lower():
                terraform = href
                break

        return {
            "title": title_text,
            "url": url,
            "type": entry_type,
            "services": services,
            "tags": tags,
            "summary": summary,
            "terraform": terraform,
        }
    except Exception as e:
        print(f"  ERROR fetching {url}: {e}", file=sys.stderr)
        return None


def extract_whats_new_links(url):
    """Extract all reference architecture links from a What's New page."""
    soup = fetch_page(url, delay=0.5)
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/en/solutions/" in href and href not in (
            "https://docs.oracle.com/en/solutions/oracle-architecture-center/",
        ):
            # Normalize URL
            if href.startswith("/"):
                href = urljoin("https://docs.oracle.com", href)
            if not href.endswith("/index.html") and not href.endswith("/"):
                href = href.rstrip("/") + "/index.html"
            title = a.get_text(strip=True)
            if title and len(title) > 10:
                links.append({"url": href, "title": title})
    return links


def load_catalog():
    """Load existing catalog if present."""
    if os.path.exists(CATALOG_PATH):
        with open(CATALOG_PATH, "r") as f:
            data = yaml.safe_load(f)
        return data if data else {"entries": []}
    return {"entries": []}


def save_catalog(data):
    """Save catalog to YAML."""
    os.makedirs(os.path.dirname(CATALOG_PATH), exist_ok=True)
    with open(CATALOG_PATH, "w") as f:
        f.write("# =============================================================================\n")
        f.write("# ORACLE ARCHITECTURE CENTER — REFERENCE CATALOG\n")
        f.write("# =============================================================================\n")
        f.write("#\n")
        f.write("# Index of Oracle Architecture Center content for the Deal Accelerator.\n")
        f.write("# Used to match customer architectures with official Oracle reference designs.\n")
        f.write("#\n")
        f.write(f"# Last refreshed: {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write(f"# Entry count: {len(data.get('entries', []))}\n")
        f.write("# To refresh: python tools/refresh_arch_catalog.py --whats-new\n")
        f.write("# =============================================================================\n\n")
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120)
    print(f"Saved {len(data.get('entries', []))} entries to {CATALOG_PATH}")


def validate_catalog():
    """Validate catalog entries have required fields."""
    data = load_catalog()
    entries = data.get("entries", [])
    errors = 0
    required = ["title", "url", "type", "tags", "summary"]

    for i, entry in enumerate(entries):
        for field in required:
            if not entry.get(field):
                print(f"  Entry {i}: missing '{field}' — {entry.get('title', 'UNKNOWN')}")
                errors += 1
        if entry.get("type") not in ("reference-architecture", "solution-playbook", "built-deployed"):
            print(f"  Entry {i}: invalid type '{entry.get('type')}' — {entry.get('title')}")
            errors += 1

    print(f"\nValidated {len(entries)} entries, {errors} errors found.")
    return errors == 0


def main():
    parser = argparse.ArgumentParser(description="Refresh Architecture Center catalog")
    parser.add_argument("--url", help="Fetch a single URL and print YAML entry")
    parser.add_argument("--whats-new", action="store_true", help="Crawl What's New pages for new entries")
    parser.add_argument("--validate", action="store_true", help="Validate existing catalog")
    parser.add_argument("--output", default=CATALOG_PATH, help="Output file path")
    args = parser.parse_args()

    if args.validate:
        ok = validate_catalog()
        sys.exit(0 if ok else 1)

    if args.url:
        entry = extract_entry(args.url)
        if entry:
            print(yaml.dump([entry], default_flow_style=False, allow_unicode=True))
        else:
            print("Failed to extract entry.", file=sys.stderr)
            sys.exit(1)

    elif args.whats_new:
        catalog = load_catalog()
        existing_urls = {e["url"] for e in catalog.get("entries", [])}
        new_count = 0

        for wn_url in WHATS_NEW_URLS:
            print(f"Fetching: {wn_url}")
            links = extract_whats_new_links(wn_url)
            print(f"  Found {len(links)} links")

            for link in links:
                url = link["url"]
                if url in existing_urls:
                    continue
                print(f"  Processing: {link['title'][:60]}...")
                entry = extract_entry(url)
                if entry:
                    catalog.setdefault("entries", []).append(entry)
                    existing_urls.add(url)
                    new_count += 1

        catalog["last_verified"] = datetime.now().strftime("%Y-%m-%d")
        catalog["source"] = "https://docs.oracle.com/en/solutions/oracle-architecture-center/"
        catalog["entry_count"] = len(catalog.get("entries", []))
        save_catalog(catalog)
        print(f"Added {new_count} new entries.")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
