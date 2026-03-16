# OCI DEAL ACCELERATOR — Architecture Center Catalog Builder

## CRITICAL: Git Branching Rule

```bash
git checkout main && git pull origin main && git checkout -b feature/architecture-center-catalog
```

---

## Objective

Build a comprehensive catalog of Oracle Architecture Center content (reference architectures, solution playbooks, built & deployed) from the last 2 years. Each entry has ONLY: title, URL, type, date, tags, and a 2-3 sentence summary focused on Architecture Recommendations and Considerations.

This catalog enables the Deal Accelerator to say: "Your architecture matches this Oracle reference architecture: [title] — [url]" when composing a proposal.

---

## Step 1: Fetch the What's New Pages

These pages list ALL published/updated content by date:

```
https://docs.oracle.com/en/solutions/oracle-architecture-center/whats-new-20251.html
https://docs.oracle.com/en/solutions/oracle-architecture-center/whats-new-2024.html
```

From each page, extract every entry title and its link. These are the master lists.

Also fetch the filtered views to catch anything missed:

```
https://docs.oracle.com/solutions/?q=&cType=reference-architectures&sort=date-desc&lang=en
https://docs.oracle.com/solutions/?q=&cType=built-deployed&sort=date-desc&lang=en  
https://docs.oracle.com/solutions/?q=&cType=solution-playbook&sort=date-desc&lang=en
```

If the filtered views are JavaScript-rendered and don't return content via fetch, rely on the What's New pages as the master source.

---

## Step 2: For Each Entry, Fetch the Detail Page

Each reference architecture has a URL like:
```
https://docs.oracle.com/en/solutions/{slug}/index.html
```

Fetch each page and extract:
- **Title**: the H1
- **Summary**: the first 2-3 sentences of the description (before the diagram)
- **Architecture Recommendations**: from the "Recommendations" or "Considerations" section — summarize in 2-3 sentences MAX
- **Services used**: list the OCI services mentioned (ADB-S, ExaCS, OKE, VCN, etc.)
- **Tags**: auto-generate from services and topic (database, networking, security, migration, ha-dr, multicloud, etc.)
- **Date**: from the What's New page or the page footer copyright
- **Terraform/GitHub link**: if present

---

## Step 3: Write the Catalog File

### Output format: `kb/architecture-center/catalog.yaml`

```yaml
# =============================================================================
# ORACLE ARCHITECTURE CENTER — REFERENCE CATALOG
# =============================================================================
# 
# Auto-generated index of Oracle Architecture Center content.
# Used by the Deal Accelerator to match customer architectures with 
# official Oracle reference architectures and solution playbooks.
#
# Entry format is intentionally minimal — title, summary, tags, URL.
# The skill references the URL; the architect reads the full doc.
#
# To refresh: python tools/refresh_arch_catalog.py
# =============================================================================

---
last_refreshed: "2026-03-16"
source: "https://docs.oracle.com/en/solutions/oracle-architecture-center/"
entry_count: 0  # UPDATE with actual count
---

entries:

  # ===== DATABASE =====

  - title: "Deploy Oracle Autonomous Database on Oracle Database@Azure"
    url: "https://docs.oracle.com/en/solutions/deploy-autonomous-database-db-at-azure/index.html"
    type: reference-architecture
    date: "2024-10"
    services: [adb-s, adg, azure]
    tags: [database, multicloud, azure, ha-dr, autonomous]
    summary: >
      Multi-AZ deployment of ADB-S on Database@Azure with Autonomous Data Guard.
      Recommends VNet peering between app and DB VNets, TAC for availability,
      and ADG standby in a different AZ for automatic failover.
    terraform: null

  - title: "Oracle MAA for Oracle Database@Azure"
    url: "https://docs.oracle.com/en/solutions/oracle-maa-db-at-azure/index.html"
    type: reference-architecture
    date: "2025-05"
    services: [exacs, adg, vault, azure]
    tags: [database, multicloud, azure, ha-dr, maa, exadata]
    summary: >
      Cross-AZ Data Guard on ExaCS in Database@Azure. Active Data Guard 
      recommended for cross-AZ replication (block repair, app continuity, 
      read offload). Backups to Autonomous Recovery Service.
    terraform: null

  - title: "Deploy Oracle Autonomous Database on Oracle Database@Google Cloud"
    url: "https://docs.oracle.com/en/solutions/deploy-adb-db-at-google-cloud/index.html"
    type: reference-architecture
    date: "2025-03"
    services: [adb-s, adg, google-cloud]
    tags: [database, multicloud, google, ha-dr, autonomous]
    summary: >
      ADB-S on Database@Google Cloud with cross-region ADG. Non-overlapping 
      CIDR between VPC and VCN required. App tier should span 2+ AZs with 
      Google Global Load Balancer for failover.
    terraform: null

  - title: "Deploy Oracle Database@Google Cloud"
    url: "https://docs.oracle.com/en/solutions/deploy-oracle-database-at-google-cloud/index.html"
    type: reference-architecture
    date: "2025-10"
    services: [exacs, adb-d, google-cloud]
    tags: [database, multicloud, google, exadata, autonomous-dedicated]
    summary: >
      ExaCS and ADB-D on Database@Google Cloud. RAC for active-active HA, 
      ASM for storage redundancy. Backups to OCI Object Storage via 
      Autonomous Recovery Service.
    terraform: null

  - title: "Deploy Oracle Database@AWS"
    url: "https://docs.oracle.com/en/solutions/deploy-oracle-db-aws/index.html"
    type: reference-architecture
    date: "2025-07"
    services: [exacs, adb-d, aws]
    tags: [database, multicloud, aws, exadata, autonomous-dedicated]
    summary: >
      ExaCS and ADB-D colocated in AWS data centers. ODB peering between
      VPC and ODB network in same AZ. Default limit of 2 DB servers and 
      3 storage servers — request increase early.
    terraform: null

  - title: "Migrate on-premises Oracle Database to Autonomous Database"
    url: "https://docs.oracle.com/en/solutions/migrate-to-atp/index.html"
    type: reference-architecture
    date: "2024-01"
    services: [adb-s, object-storage, compute, vpn]
    tags: [database, migration, autonomous, data-pump]
    summary: >
      MV2ADB tool for on-prem EE to ADB-S migration using Data Pump.
      Requires HTTP to Object Storage + SQL*Net to ADB. Terraform code 
      available on GitHub for networking + compute + ADB provisioning.
    terraform: "https://github.com/oracle-quickstart/oci-arch-atp"

  - title: "Migrate Oracle RAC Databases to OCI"
    url: "https://docs.oracle.com/en/solutions/ensure-ha-migrate-vmware-workloads-to-oci/migrate-oracle-rac-databases1.html"
    type: reference-architecture
    date: "2025-01"
    services: [exacs, exascale, adb-d, base-db]
    tags: [database, migration, rac, exadata, ha-dr]
    summary: >
      Compares 4 RAC migration targets: ExaCS Dedicated, Exascale, ADB-D, 
      and 2-node RAC on Base DB. ExaCS recommended for full RAC feature 
      parity. Exascale for 23ai-only without dedicated infra commitment.
    terraform: null

  - title: "Deploy ORDS with High Availability on OCI"
    url: "https://docs.oracle.com/en/solutions/deploy-ords-ha-oci/index.html"
    type: reference-architecture
    date: "2025-06"
    services: [compute, load-balancer, adb-s, bastion]
    tags: [database, application, ords, ha-dr, rest-api]
    summary: >
      Multi-instance ORDS behind OCI Load Balancer for HA REST access to 
      Oracle DB. Works with ADB-S, DBCS, or ExaCS. Recommends DB in 
      private subnet, ORDS in public with granular NSG rules.
    terraform: null

  - title: "Deploy secure ADB and APEX application"
    url: "https://docs.oracle.com/en/solutions/deploy-autonomous-database-and-app/index.html"
    type: reference-architecture
    date: "2024-06"
    services: [adb-s, apex, load-balancer, bastion, cloud-guard]
    tags: [database, application, apex, security, autonomous]
    summary: >
      APEX on ADB-S with private endpoint behind Load Balancer. OCI 
      Landing Zone via Terraform provisions in minutes. Recommends NSGs 
      over Security Lists, Cloud Guard with custom detector recipes.
    terraform: "https://github.com/oracle-quickstart/oci-arch-apex-atp"

  # ===== NETWORKING & INTEGRATION =====

  - title: "Design network architecture for data and application integration"
    url: "https://docs.oracle.com/en/solutions/data-application-integration-workloads/index.html"
    type: reference-architecture
    date: "2025-11"
    services: [vcn, drg, fastconnect, oic, data-integration, adb]
    tags: [networking, integration, multicloud, data-integration]
    summary: >
      4 integration patterns: single VCN, cross-VCN, cross-region, and 
      multicloud. FastConnect+DRG for on-prem, RPC for cross-region. 
      Multicloud via FastConnect+ExpressRoute/DirectConnect/PartnerInterconnect.
    terraform: null

  # ===== DATA PLATFORM =====

  - title: "Data platform - decentralized data platform"
    url: "https://docs.oracle.com/en/solutions/data-platform-decentralized/index.html"
    type: reference-architecture
    date: "2025-03"
    services: [adw, data-catalog, data-integration, object-storage]
    tags: [data-platform, data-lake, data-sharing, autonomous]
    summary: >
      Decentralized data lakehouse with domain-level ADB-S instances 
      sharing data via Cloud Links or Delta Sharing. Centralized catalog, 
      IaC onboarding per domain. Hub-spoke model with OCI backbone routing.
    terraform: null

  - title: "Cloud data lake house - process enterprise and streaming data"
    url: "https://docs.oracle.com/en/solutions/oci-curated-analysis/index.html"
    type: reference-architecture
    date: "2024-02"
    services: [adw, streaming, goldengate-stream-analytics, data-integration, object-storage]
    tags: [data-platform, data-lake, streaming, analytics, machine-learning]
    summary: >
      Full data lakehouse with batch and streaming ingestion. ADW with 
      auto-scaling for curated layer. Hybrid partitioned tables to move 
      cold data to Object Storage transparently. GoldenGate Stream Analytics 
      for real-time event processing.
    terraform: null

  - title: "Multicloud data lake integration"
    url: "https://docs.oracle.com/en/solutions/oci-multicloud-datalake/index.html"
    type: reference-architecture
    date: "2024-03"
    services: [data-integration, oic, object-storage, adw, streaming]
    tags: [data-platform, multicloud, integration, data-lake]
    summary: >
      Bring data from AWS/Azure/on-prem into OCI data lake. OCI Data 
      Integration for batch ETL, OIC for app integration with pre-built 
      adapters. Read-only credentials for source systems recommended.
    terraform: null

  # ===================================================================
  # CONTINUE ADDING ALL REMAINING ENTRIES FROM THE WHAT'S NEW PAGES
  # Follow the same format: title, url, type, date, services, tags, summary
  # 
  # Fetch and process ALL entries from:
  #   - whats-new-20251.html (2025 entries)
  #   - whats-new-2024.html (2024 entries)
  #
  # For each entry:
  #   1. Fetch the detail page
  #   2. Extract the summary (first 2-3 sentences)
  #   3. Extract Architecture Recommendations (summarize in 2-3 sentences)
  #   4. Combine into the summary field
  #   5. Auto-tag based on services and topic
  # ===================================================================
```

---

## Step 4: Build the Refresh Script

### `tools/refresh_arch_catalog.py`

```python
#!/usr/bin/env python3
"""
Refresh the Architecture Center catalog from Oracle docs.

Usage:
    python tools/refresh_arch_catalog.py
    python tools/refresh_arch_catalog.py --url https://docs.oracle.com/en/solutions/{slug}/index.html
    python tools/refresh_arch_catalog.py --whats-new

This script:
1. Fetches the What's New pages for 2024 and 2025
2. Extracts all reference architecture links
3. For each link, fetches the detail page
4. Extracts title, summary, services, recommendations
5. Writes/updates kb/architecture-center/catalog.yaml

IMPORTANT: This is a semi-automated tool. It generates DRAFT entries
that should be reviewed by a human before committing. The auto-generated
summaries may miss nuance or include irrelevant detail.
"""

import requests
import yaml
import re
import argparse
from bs4 import BeautifulSoup
from datetime import datetime
import os
import time

# Service name detection patterns
SERVICE_PATTERNS = {
    "adb-s": r"Autonomous\s+(Database|Transaction|Data\s+Warehouse)(?!.*Dedicated)",
    "adb-d": r"Autonomous\s+Database\s+on\s+Dedicated|ADB-D",
    "exacs": r"Exadata\s+(Cloud|Database)\s+Service|ExaCS|ExaDB",
    "exascale": r"Exascale",
    "base-db": r"Base\s+Database|VM\s+DB|DB\s+System",
    "oke": r"Kubernetes\s+Engine|OKE|Container\s+Engine",
    "compute": r"Compute\s+(Instance|VM)|Virtual\s+Machine",
    "functions": r"OCI\s+Functions|Functions\s+Service",
    "vcn": r"Virtual\s+Cloud\s+Network|VCN",
    "load-balancer": r"Load\s+Balanc",
    "waf": r"Web\s+Application\s+Firewall|WAF",
    "fastconnect": r"FastConnect",
    "drg": r"Dynamic\s+Routing\s+Gateway|DRG",
    "object-storage": r"Object\s+Storage",
    "data-safe": r"Data\s+Safe",
    "vault": r"OCI\s+Vault|Key\s+Management",
    "cloud-guard": r"Cloud\s+Guard",
    "goldengate": r"GoldenGate",
    "oic": r"Oracle\s+Integration|OIC",
    "data-integration": r"Data\s+Integration",
    "streaming": r"OCI\s+Streaming|Streaming\s+Service",
    "monitoring": r"OCI\s+Monitoring",
    "logging": r"Logging\s+Analytics",
    "bastion": r"Bastion",
    "apex": r"Oracle\s+APEX|APEX\s+application",
    "mysql": r"MySQL\s+(Database\s+)?Service|MySQL\s+HeatWave",
    "nosql": r"NoSQL\s+Database",
    "adw": r"Autonomous\s+Data\s+Warehouse|ADW",
    "azure": r"Database@Azure|Azure",
    "aws": r"Database@AWS|AWS",
    "google-cloud": r"Database@Google|Google\s+Cloud",
}

TAG_PATTERNS = {
    "database": r"database|autonomous|exadata|rac|mysql|nosql",
    "migration": r"migrat|move\s+to|zero\s+downtime",
    "ha-dr": r"high\s+availability|disaster\s+recovery|data\s+guard|failover|MAA",
    "security": r"secur|encrypt|vault|data\s+safe|cloud\s+guard|compliance",
    "networking": r"network|vcn|subnet|fastconnect|vpn|drg|load\s+balanc",
    "multicloud": r"multicloud|multi-cloud|azure|aws|google\s+cloud|database@",
    "integration": r"integrat|oic|streaming|goldengate|data\s+flow",
    "data-platform": r"data\s+lake|data\s+warehouse|analytics|data\s+platform",
    "application": r"apex|ords|kubernetes|container|weblogic|tomcat",
    "ai-ml": r"machine\s+learning|ai\s+|generative|vector|select\s+ai",
    "autonomous": r"autonomous\s+database|adb|auto-scal",
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
        
        # Extract first 2-3 sentences as summary
        paragraphs = soup.find_all("p")
        summary_parts = []
        for p in paragraphs[:5]:
            text = p.get_text(strip=True)
            if len(text) > 50 and "Copyright" not in text:
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
        elif "built and deployed" in body.lower() or "customer" in title_text.lower():
            entry_type = "built-deployed"
        
        # Find terraform/github links
        terraform = None
        for a in soup.find_all("a", href=True):
            if "github" in a["href"].lower():
                terraform = a["href"]
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
        print(f"  ERROR fetching {url}: {e}")
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="Fetch a single URL")
    parser.add_argument("--whats-new", action="store_true", help="Fetch from What's New pages")
    parser.add_argument("--output", default="kb/architecture-center/catalog.yaml")
    args = parser.parse_args()
    
    if args.url:
        entry = extract_entry(args.url)
        if entry:
            print(yaml.dump([entry], default_flow_style=False))
    elif args.whats_new:
        # Fetch What's New pages and extract all links
        # ... implement the full crawl
        pass
    else:
        print("Usage: --url <url> or --whats-new")


if __name__ == "__main__":
    main()
```

**Requirements:** `pip install requests beautifulsoup4`

---

## Step 5: Integration with the Skill

### Update `kb/INDEX.yaml`

Add:

```yaml
architecture_center:
  catalog:
    path: "kb/architecture-center/catalog.yaml"
    keywords: ["reference architecture", "oracle architecture center", "solution playbook", "built deployed"]
    load_when: "composing architecture or generating ADRs — match customer workload against known Oracle patterns"
```

### How the Skill Uses It

During Phase 2 (Architecture Composition), after selecting services and patterns, the skill scans the catalog for matching entries:

```
Matching logic:
1. Compare selected services against entry.services
2. Compare workload tags against entry.tags
3. If ≥2 service matches + ≥1 tag match → STRONG MATCH
4. If ≥1 service match + ≥2 tag matches → MODERATE MATCH

Output in the deck:
- Architecture Decisions slide: "Based on Oracle Reference Architecture: [title] ([url])"
- Technical document: Full reference with link
- Risk register: Note any deviations from the reference architecture
```

Example match for the Laboratorios Farma case:
```
Customer: ADB-S + ADG + VPN + private subnet + APEX
Matches:
  ✅ STRONG: "Deploy secure ADB and APEX application" (adb-s, apex, load-balancer)
  ✅ MODERATE: "Deploy ORDS with High Availability on OCI" (adb-s, load-balancer)
  ✅ MODERATE: "Migrate on-premises Oracle Database to ADB" (adb-s, migration)
```

---

## Build Order

1. Create `kb/architecture-center/` directory
2. Run the refresh script to generate `catalog.yaml` (or build manually from What's New pages)
3. Review and curate the auto-generated entries (fix summaries, verify tags)
4. Update `kb/INDEX.yaml` with the architecture-center reference
5. Update `SKILL.md` / `SKILL_COMPACT.md` with matching logic instructions
6. Add `tools/refresh_arch_catalog.py` to the repo
7. Add tests: verify catalog loads, entries have required fields, no broken URLs

## Refresh Cadence

- **Monthly**: Run `python tools/refresh_arch_catalog.py --whats-new` to pick up new entries
- **On Oracle release**: Check for new reference architectures related to new features
- **Manual add**: For entries the scraper misses, add manually following the format

## When Done

```bash
git add .
git commit -m "feat: Architecture Center catalog — reference architectures index"
git push -u origin feature/architecture-center-catalog
```
