#!/usr/bin/env python3
"""
SonarQube Quality Gate Check Script with LLM Governance Integration

This script:
1. Queries SonarQube API for quality gate status
2. Maps SonarQube conditions to LLM governance tags
3. Generates unified governance report
4. Exits with appropriate code for CI/CD

Usage:
    python scripts/check_quality_gate.py --project-key <key> --token <token>

Environment Variables:
    SONAR_TOKEN: SonarQube authentication token
    SONAR_HOST_URL: SonarQube server URL (default: https://sonarcloud.io)
    SONAR_ORG: SonarQube organization (for SonarCloud)

Exit Codes:
    0: Quality gate passed
    1: Quality gate failed (blocks PR)
    2: Configuration error
"""

import argparse
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

# Allowed URL schemes for security (B310)
ALLOWED_SCHEMES = frozenset({"http", "https"})


class SonarQubeClient:
    """Simple SonarQube API client."""

    def __init__(self, host_url: str, token: str, org: str | None = None):
        self.host_url = host_url.rstrip("/")
        self.token = token
        self.org = org
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def _make_request(self, endpoint: str, params: dict | None = None) -> dict:
        """Make HTTP request to SonarQube API."""
        url = urljoin(self.host_url, endpoint)

        if params:
            query_string = "&".join(f"{k}={v}" for k, v in params.items())
            url = f"{url}?{query_string}"

        # Validate URL scheme to prevent file:// or custom scheme attacks (B310)
        parsed = urlparse(url)
        if parsed.scheme not in ALLOWED_SCHEMES:
            print(
                f"Error: Invalid URL scheme '{parsed.scheme}'. Only http/https allowed.",
                file=sys.stderr,
            )
            sys.exit(2)

        request = Request(url, headers=self.headers)

        try:
            with urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode())
        except HTTPError as e:
            print(f"HTTP Error {e.code}: {e.reason}", file=sys.stderr)
            print(f"URL: {url}", file=sys.stderr)
            sys.exit(2)
        except URLError as e:
            print(f"URL Error: {e.reason}", file=sys.stderr)
            sys.exit(2)

    def get_quality_gate_status(self, project_key: str) -> dict:
        """Get quality gate status for a project."""
        return self._make_request(
            "/api/qualitygates/project_status", {"projectKey": project_key}
        )

    def get_measures(self, project_key: str, metrics: list[str]) -> dict:
        """Get project measures for specified metrics."""
        return self._make_request(
            "/api/measures/component",
            {"component": project_key, "metricKeys": ",".join(metrics)},
        )

    def get_issues(self, project_key: str, severities: list[str] | None = None) -> dict:
        """Get project issues filtered by severity."""
        params = {"componentKeys": project_key}
        if severities:
            params["severities"] = ",".join(severities)

        return self._make_request("/api/issues/search", params)


class LLMGovernanceMapper:
    """Maps SonarQube findings to LLM governance tags."""

    # Mapping: SonarQube rule/metric -> LLM Tag
    RULE_TO_TAG_MAP = {
        # Security issues -> #CRITICAL: Security
        "S2068": "#CRITICAL: Security (Hardcoded credentials)",
        "S2092": "#CRITICAL: Security (Cookie security)",
        "S2631": "#CRITICAL: Security (SQL Injection)",
        "S5131": "#CRITICAL: Security (XSS)",
        "S3330": "#CRITICAL: Security (HTTP without TLS)",
        # Hardcoded values -> #LLM-PLACEHOLDER
        "S1313": "#LLM-PLACEHOLDER (Hardcoded IP address)",
        "S1075": "#LLM-PLACEHOLDER (Hardcoded URI)",
        "S4784": "#LLM-PLACEHOLDER (Unsafe regex)",
        # Logic issues -> #LLM-LOGIC
        "S3776": "#LLM-LOGIC (Complex cognitive complexity)",
        "S1541": "#LLM-LOGIC (Complex cyclomatic complexity)",
        # Code duplications -> #LLM-SCAFFOLD
        "duplicated_blocks": "#LLM-SCAFFOLD (Code duplication)",
        "duplicated_lines_density": "#LLM-SCAFFOLD (Code duplication)",
        # Test coverage -> #LLM-TEST-FIRST
        "coverage": "#LLM-TEST-FIRST (Insufficient coverage)",
        "new_coverage": "#LLM-TEST-FIRST (New code not covered)",
    }

    @classmethod
    def map_condition_to_tag(cls, metric_key: str, condition_status: str) -> str | None:
        """Map a quality gate condition to an LLM tag."""
        if condition_status == "OK":
            return None

        for rule_pattern, tag in cls.RULE_TO_TAG_MAP.items():
            if rule_pattern in metric_key.lower():
                return tag

        return None

    @classmethod
    def map_issue_to_tag(cls, rule_key: str) -> str | None:
        """Map a SonarQube rule to an LLM tag."""
        return cls.RULE_TO_TAG_MAP.get(rule_key)


def format_report(
    quality_gate_status: dict, issues: dict, rad_tags: int, llm_tags: int
) -> str:
    """Generate unified three-layer governance report."""

    qg = quality_gate_status["projectStatus"]
    status = qg["status"]
    conditions = qg.get("conditions", [])

    report = []
    report.append("=" * 80)
    report.append("THREE-LAYER GOVERNANCE REPORT")
    report.append("=" * 80)
    report.append("")

    # Layer 1: Production Runtime Risks (RAD)
    report.append("Layer 1: Production Runtime Risks (RAD)")
    report.append("-" * 80)
    if rad_tags > 0:
        report.append(f"❌ FOUND {rad_tags} unverified production risk tags")
        report.append("   Status: BLOCKED")
    else:
        report.append("✅ No unverified production risk tags")
        report.append("   Status: PASSED")
    report.append("")

    # Layer 2: LLM Development Debt
    report.append("Layer 2: LLM Development Debt")
    report.append("-" * 80)
    if llm_tags > 0:
        report.append(f"⚠️  FOUND {llm_tags} unverified LLM debt tags")
        report.append("   Status: WARNING")
    else:
        report.append("✅ No unverified LLM debt tags")
        report.append("   Status: PASSED")
    report.append("")

    # Layer 3: Automated Code Quality (SonarQube)
    report.append("Layer 3: Automated Code Quality (SonarQube)")
    report.append("-" * 80)

    if status == "OK":
        report.append("✅ Quality Gate: PASSED")
    elif status == "ERROR":
        report.append("❌ Quality Gate: FAILED")
    elif status == "WARN":
        report.append("⚠️  Quality Gate: WARNING")
    else:
        report.append(f"❓ Quality Gate: {status}")

    report.append("")
    report.append("Quality Gate Conditions:")
    for condition in conditions:
        metric = condition["metricKey"]
        status_icon = "✅" if condition["status"] == "OK" else "❌"
        actual = condition.get("actualValue", "N/A")

        # Map to LLM tag if failed
        llm_tag = ""
        if condition["status"] != "OK":
            tag = LLMGovernanceMapper.map_condition_to_tag(metric, condition["status"])
            if tag:
                llm_tag = f" -> {tag}"

        report.append(f"  {status_icon} {metric}: {actual}{llm_tag}")

    report.append("")

    # Critical/Blocker issues
    total_issues = issues.get("total", 0)
    if total_issues > 0:
        report.append(f"Found {total_issues} critical/blocker issues:")
        for issue in issues.get("issues", [])[:10]:  # Show first 10
            rule_key = issue["rule"]
            severity = issue["severity"]
            message = issue["message"]
            llm_tag = LLMGovernanceMapper.map_issue_to_tag(rule_key) or ""
            report.append(f"  • [{severity}] {message}")
            if llm_tag:
                report.append(f"    {llm_tag}")

    report.append("")
    report.append("=" * 80)
    report.append("OVERALL STATUS")
    report.append("=" * 80)

    # Determine overall status
    blocked = rad_tags > 0 or status == "ERROR"

    if blocked:
        report.append("❌ PR BLOCKED - Fix issues before merging")
        report.append("")
        report.append("Next Steps:")
        if rad_tags > 0:
            report.append("  1. Verify and remove all #CRITICAL and #ASSUME tags")
        if status == "ERROR":
            report.append("  2. Fix all BLOCKER and CRITICAL SonarQube issues")
            report.append("  3. Ensure test coverage meets threshold")
        if llm_tags > 0:
            report.append("  4. Review and resolve LLM debt tags")
    else:
        report.append("✅ READY TO MERGE")
        if llm_tags > 0:
            report.append("")
            report.append("Note: LLM debt tags found (warnings only)")

    report.append("=" * 80)

    return "\n".join(report)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check SonarQube quality gate with LLM governance integration"
    )
    parser.add_argument(
        "--project-key",
        default="ByronWilliamsCPA_mtg_ai",
        help="SonarQube project key (default: ByronWilliamsCPA_mtg_ai)",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("SONAR_TOKEN"),
        help="SonarQube token (default: SONAR_TOKEN env var)",
    )
    parser.add_argument(
        "--host-url",
        default=os.environ.get("SONAR_HOST_URL", "https://sonarcloud.io"),
        help="SonarQube server URL (default: https://sonarcloud.io)",
    )
    parser.add_argument(
        "--org",
        default=os.environ.get("SONAR_ORG", "ByronWilliamsCPA"),
        help="SonarQube organization (default: ByronWilliamsCPA)",
    )
    parser.add_argument(
        "--rad-tags", type=int, default=0, help="Number of RAD tags found in codebase"
    )
    parser.add_argument(
        "--llm-tags",
        type=int,
        default=0,
        help="Number of LLM debt tags found in codebase",
    )

    args = parser.parse_args()

    if not args.token:
        print("Error: SONAR_TOKEN not provided", file=sys.stderr)
        print("Set SONAR_TOKEN environment variable or use --token", file=sys.stderr)
        sys.exit(2)

    # Initialize client
    client = SonarQubeClient(args.host_url, args.token, args.org)

    print(f"Checking quality gate for project: {args.project_key}")
    print(f"SonarQube URL: {args.host_url}")
    if args.org:
        print(f"Organization: {args.org}")
    print()

    # Get quality gate status
    qg_status = client.get_quality_gate_status(args.project_key)

    # Get critical/blocker issues
    issues = client.get_issues(args.project_key, ["CRITICAL", "BLOCKER"])

    # Generate and print report
    report = format_report(qg_status, issues, args.rad_tags, args.llm_tags)
    print(report)

    # Exit with appropriate code
    project_status = qg_status["projectStatus"]["status"]

    if args.rad_tags > 0:
        print("\nExiting with code 1: RAD tags found (PR blocked)", file=sys.stderr)
        sys.exit(1)
    elif project_status == "ERROR":
        print(
            "\nExiting with code 1: Quality gate failed (PR blocked)", file=sys.stderr
        )
        sys.exit(1)
    elif project_status == "WARN":
        print(
            "\nExiting with code 0: Quality gate passed with warnings", file=sys.stderr
        )
        sys.exit(0)
    else:
        print("\nExiting with code 0: All checks passed", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
