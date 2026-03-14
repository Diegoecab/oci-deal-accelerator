#!/usr/bin/env python3
"""
OCI Well-Architected Framework Validation Engine

Validates an OCI architecture against the 5 Well-Architected pillars
and generates a scorecard with auto-detected gaps and recommendations.

Usage:
    python validate-architecture.py --profile workload-profile.yaml --architecture architecture.yaml

The validation is automatic — it infers check results from the composed
architecture and workload profile flags. No manual checklist required.
"""

import yaml
import sys
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Any


# Pillar YAML files
PILLAR_FILES = [
    "security-compliance.yaml",
    "reliability-resilience.yaml",
    "performance-cost.yaml",
    "operational-efficiency.yaml",
    "distributed-cloud.yaml",
]

KB_DIR = Path(__file__).parent.parent / "kb" / "well-architected"


def load_yaml(filepath: str) -> dict:
    """Load a YAML file and return its contents."""
    with open(filepath, "r") as f:
        return yaml.safe_load(f)


def check_applies(applies_when: str, flags: dict) -> bool:
    """Determine if a check applies based on the workload profile flags."""
    if applies_when == "always":
        return True

    # Handle OR conditions
    if " OR " in applies_when:
        conditions = [c.strip() for c in applies_when.split(" OR ")]
        return any(flags.get(c, False) for c in conditions)

    # Handle AND conditions
    if " AND " in applies_when:
        conditions = [c.strip() for c in applies_when.split(" AND ")]
        return all(flags.get(c, False) for c in conditions)

    # Handle 'or' conditions (lowercase)
    if " or " in applies_when:
        conditions = [c.strip() for c in applies_when.split(" or ")]
        return any(flags.get(c, False) for c in conditions)

    # Single flag check
    return flags.get(applies_when, False)


def evaluate_check(check: dict, architecture: dict, flags: dict) -> dict:
    """
    Evaluate a single check against the architecture.

    Returns a result dict with status (pass/gap/not_applicable) and details.
    """
    check_id = check["id"]
    applies_when = check.get("applies_when", "always")

    # Check if this check applies to the workload
    if not check_applies(applies_when, flags):
        return {
            "check_id": check_id,
            "status": "not_applicable",
            "name": check["name"],
        }

    # Look for the check_id or related keywords in the architecture
    arch_str = json.dumps(architecture).lower()
    auto_detect = check.get("auto_detect", {})
    pass_keywords = _extract_keywords(auto_detect.get("pass_if", ""))

    # Check if architecture satisfies the check
    matched = any(kw in arch_str for kw in pass_keywords if kw)

    if matched:
        return {
            "check_id": check_id,
            "status": "pass",
            "name": check["name"],
        }
    else:
        return {
            "check_id": check_id,
            "status": "gap",
            "name": check["name"],
            "severity": check.get("severity", "MEDIUM"),
            "finding": auto_detect.get("gap_if", check["description"]),
            "recommendation": auto_detect.get("pass_if", ""),
            "description": check["description"],
        }


def _extract_keywords(text: str) -> list[str]:
    """Extract searchable keywords from auto_detect conditions."""
    if not text:
        return []
    # Extract key service/feature names from the condition text
    keywords = []
    key_terms = [
        # Identity & Access
        "iam", "mfa", "instance principal", "resource principal",
        "instance_principal", "resource_principal",
        "identity domain", "identity_domain", "federation", "idp",
        "compartment", "least-privilege", "least_privilege",
        "admin_restriction", "break-glass", "break_glass",
        # Resource Isolation
        "tag", "tags", "defined_namespace", "cost_center", "costcenter",
        "security zone", "security_zone",
        # Database Security
        "private subnet", "private_subnet", "private", "tde",
        "vault", "vault_key", "key_management", "customer-managed",
        "data safe", "data_safe", "private endpoint", "private_endpoint",
        "key_rotation", "rotation", "patching", "patch",
        # Network Security
        "nsg", "waf", "service gateway", "service_gateway",
        "network firewall", "network_firewall",
        "tls", "ssl", "ztpr", "zero trust", "zero_trust",
        "bastion", "ssh_restricted",
        # Monitoring
        "cloud guard", "cloud_guard", "audit", "flow log", "flow_log",
        "vulnerability scan", "vulnerability_scanning", "siem",
        "logging_analytics", "logging analytics",
        # Scalability
        "auto-scaling", "autoscaling", "auto_scaling",
        "capacity reservation", "capacity_reservation",
        # Networking
        "fastconnect", "fast_connect", "vpn", "vpn_backup",
        "drg", "health check", "health_check",
        "fault domain", "fault_domain", "fault domains",
        "availability domain", "availability_domain",
        "redundant", "diverse_path",
        # Backup & DR
        "backup", "automated_backup", "data guard", "data_guard",
        "replication", "cross_region", "cross-region",
        "rpo", "rto", "dr region", "dr_region",
        "disaster recovery", "disaster_recovery",
        "traffic management", "traffic_management",
        "dns failover", "dns_failover", "drill",
        # Operations
        "terraform", "resource manager", "resource_manager",
        "ci/cd", "cicd", "ci_cd", "devops",
        "blue/green", "blue_green", "canary", "rolling",
        "monitoring", "alarm", "alarms", "custom_metric",
        "apm", "database management", "database_management",
        "ops insights", "ops_insights",
        "os management", "os_management", "os_management_hub",
        "notification", "runbook", "event", "function",
        "environment_parity", "parity",
        # Compute
        "flex", "flex shape", "flex_shape",
        "ampere", "arm", "burstable", "preemptible",
        # Cost
        "reserved capacity", "reserved_capacity",
        "budget", "budgets", "byol", "alert_threshold",
        "scheduling", "scheduled",
        # Storage
        "auto_tiering", "auto-tiering", "tiering",
        "retention", "retention_rule",
    ]
    text_lower = text.lower()
    for term in key_terms:
        if term in text_lower:
            keywords.append(term)
    return keywords


def validate_pillar(pillar_file: str, architecture: dict, flags: dict) -> dict:
    """Validate architecture against a single pillar."""
    pillar_data = load_yaml(str(KB_DIR / pillar_file))
    pillar_info = pillar_data["pillar"]
    categories = pillar_data.get("categories", [])

    # Check if pillar is conditional (e.g., Distributed Cloud)
    if pillar_info.get("conditional", False):
        applies = pillar_info.get("applies_when", "")
        if not check_applies(applies, flags):
            return {
                "pillar_id": pillar_info["id"],
                "pillar_name": pillar_info["name"],
                "status": "NOT_APPLICABLE",
                "reason": "Conditions not met for this pillar",
                "checks_passed": 0,
                "checks_total": 0,
                "categories": {},
                "gaps": [],
            }

    all_gaps = []
    category_results = {}
    total_checks = 0
    total_passed = 0

    for category in categories:
        cat_id = category["id"]
        cat_passed = 0
        cat_total = 0
        cat_gaps = []

        for check in category.get("checks", []):
            result = evaluate_check(check, architecture, flags)

            if result["status"] == "not_applicable":
                continue

            cat_total += 1
            if result["status"] == "pass":
                cat_passed += 1
            else:
                gap = {
                    "check_id": result["check_id"],
                    "area": category["name"],
                    "finding": result.get("finding", ""),
                    "severity": result.get("severity", "MEDIUM"),
                    "recommendation": result.get("recommendation", ""),
                    "wa_reference": pillar_info.get("reference", ""),
                }
                cat_gaps.append(gap)
                all_gaps.append(gap)

        category_results[cat_id] = {
            "passed": cat_passed,
            "total": cat_total,
            "gaps": cat_gaps,
        }
        total_checks += cat_total
        total_passed += cat_passed

    # Determine pillar status
    high_gaps = sum(1 for g in all_gaps if g["severity"] == "HIGH")
    if high_gaps > 0:
        status = "GAPS_IDENTIFIED"
    elif all_gaps:
        status = "PASS_WITH_RECOMMENDATIONS"
    else:
        status = "PASS"

    return {
        "pillar_id": pillar_info["id"],
        "pillar_name": pillar_info["name"],
        "status": status,
        "checks_passed": total_passed,
        "checks_total": total_checks,
        "categories": category_results,
        "gaps": all_gaps,
    }


def generate_scorecard(
    architecture: dict,
    profile: dict,
    customer_name: str = "",
    arch_name: str = "",
) -> dict:
    """Generate a complete Well-Architected scorecard."""
    flags = profile.get("workload_profile", {}).get("flags", {})

    pillar_results = {}
    total_checks = 0
    total_passed = 0
    all_gaps = []

    for pillar_file in PILLAR_FILES:
        result = validate_pillar(pillar_file, architecture, flags)
        pillar_results[result["pillar_id"]] = result
        total_checks += result["checks_total"]
        total_passed += result["checks_passed"]
        all_gaps.extend(result.get("gaps", []))

    # Overall status
    high_gaps = [g for g in all_gaps if g["severity"] == "HIGH"]
    medium_gaps = [g for g in all_gaps if g["severity"] == "MEDIUM"]
    low_gaps = [g for g in all_gaps if g["severity"] == "LOW"]

    if high_gaps:
        overall_status = "GAPS_IDENTIFIED"
    elif medium_gaps:
        overall_status = "PASS_WITH_RECOMMENDATIONS"
    else:
        overall_status = "PASS"

    # Build action items
    action_items = {
        "high_priority": [
            {
                "check_id": g["check_id"],
                "pillar": g.get("area", ""),
                "finding": g["finding"],
                "recommendation": g["recommendation"],
            }
            for g in high_gaps
        ],
        "medium_priority": [
            {
                "check_id": g["check_id"],
                "pillar": g.get("area", ""),
                "finding": g["finding"],
                "recommendation": g["recommendation"],
            }
            for g in medium_gaps
        ],
        "low_priority": [
            {
                "check_id": g["check_id"],
                "pillar": g.get("area", ""),
                "finding": g["finding"],
                "recommendation": g["recommendation"],
            }
            for g in low_gaps
        ],
    }

    scorecard = {
        "well_architected_scorecard": {
            "overall_status": overall_status,
            "generated_date": datetime.now().isoformat(),
            "architecture_name": arch_name,
            "customer": customer_name,
            "summary": {
                "total_checks": total_checks,
                "total_passed": total_passed,
                "total_gaps": len(all_gaps),
                "high_severity_gaps": len(high_gaps),
                "medium_severity_gaps": len(medium_gaps),
                "low_severity_gaps": len(low_gaps),
            },
            "pillars": {
                pid: {
                    "status": p["status"],
                    "checks_passed": p["checks_passed"],
                    "checks_total": p["checks_total"],
                    "categories": p["categories"],
                }
                for pid, p in pillar_results.items()
            },
            "action_items": action_items,
            "references": {
                "framework": "https://docs.oracle.com/en/solutions/oci-best-practices/index.html",
                "security": "https://docs.oracle.com/en/solutions/oci-best-practices/effective-strategies-security-and-compliance1.html",
                "reliability": "https://docs.oracle.com/en/solutions/oci-best-practices/reliable-and-resilient-cloud-topology-practices1.html",
                "operations": "https://docs.oracle.com/en/solutions/oci-best-practices/best-practices-operating-cloud-deployments-efficiency.html",
                "distributed": "https://docs.oracle.com/en/solutions/oci-best-practices/effective-strategies-distributed-cloud-implementation1.html",
            },
        }
    }

    return scorecard


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate OCI architecture against Well-Architected Framework"
    )
    parser.add_argument(
        "--profile",
        required=True,
        help="Path to workload profile YAML",
    )
    parser.add_argument(
        "--architecture",
        required=True,
        help="Path to architecture YAML",
    )
    parser.add_argument(
        "--output",
        default="scorecard-output.yaml",
        help="Output scorecard file path",
    )
    parser.add_argument(
        "--format",
        choices=["yaml", "json"],
        default="yaml",
        help="Output format",
    )

    args = parser.parse_args()

    profile = load_yaml(args.profile)
    architecture = load_yaml(args.architecture)

    customer = (
        profile.get("workload_profile", {})
        .get("business_context", {})
        .get("customer_name", "Unknown")
    )

    scorecard = generate_scorecard(
        architecture=architecture,
        profile=profile,
        customer_name=customer,
        arch_name=args.architecture,
    )

    if args.format == "json":
        output = json.dumps(scorecard, indent=2)
    else:
        output = yaml.dump(scorecard, default_flow_style=False, sort_keys=False)

    with open(args.output, "w") as f:
        f.write(output)

    # Print summary
    sc = scorecard["well_architected_scorecard"]
    print(f"\nOCI Well-Architected Scorecard")
    print(f"{'=' * 50}")
    print(f"Overall Status: {sc['overall_status']}")
    print(f"Checks: {sc['summary']['total_passed']}/{sc['summary']['total_checks']} passed")
    print(f"Gaps: {sc['summary']['total_gaps']} "
          f"(HIGH: {sc['summary']['high_severity_gaps']}, "
          f"MEDIUM: {sc['summary']['medium_severity_gaps']}, "
          f"LOW: {sc['summary']['low_severity_gaps']})")
    print(f"\nPillar Results:")
    for pid, p in sc["pillars"].items():
        print(f"  {pid}: {p['status']} ({p['checks_passed']}/{p['checks_total']})")
    print(f"\nScorecard written to: {args.output}")


if __name__ == "__main__":
    main()
