"""
Tests for the Field Findings Tracker YAML and CLI.

Tracker YAML: kb/field-findings/tracker.yaml
CLI module:   tools/findings_cli.py
"""

import re
import sys
from datetime import datetime
from pathlib import Path

import pytest
import yaml

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRACKER_PATH = PROJECT_ROOT / "kb" / "field-findings" / "tracker.yaml"
TOOLS_DIR = PROJECT_ROOT / "tools"

if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

try:
    import findings_cli as cli

    CLI_AVAILABLE = True
except ImportError:
    CLI_AVAILABLE = False

VALID_SEVERITIES = {"CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"}
VALID_STATUSES = {"open", "resolved", "wontfix", "acknowledged", "monitoring"}
VALID_CONFIDENCE = {"validated", "observed", "reported", "inferred"}
ID_PATTERN = re.compile(r"^FF-\d{6}-\d{3}$")
REQUIRED_FIELDS = {"id", "date", "summary", "severity", "status"}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def tracker_data():
    """Load the tracker YAML once per module."""
    with open(TRACKER_PATH, "r") as fh:
        return yaml.safe_load(fh)


@pytest.fixture(scope="module")
def findings(tracker_data):
    """Return the list of findings."""
    return tracker_data["findings"]


# ---------------------------------------------------------------------------
# YAML structure tests
# ---------------------------------------------------------------------------
class TestTrackerYAML:
    def test_tracker_loads(self, tracker_data):
        """YAML loads without errors and contains the findings key."""
        assert tracker_data is not None
        assert "findings" in tracker_data
        assert isinstance(tracker_data["findings"], list)
        assert len(tracker_data["findings"]) > 0

    def test_all_findings_have_required_fields(self, findings):
        """Each finding must have id, date, summary, severity, status."""
        for finding in findings:
            missing = REQUIRED_FIELDS - set(finding.keys())
            assert not missing, (
                f"Finding '{finding.get('id', '???')}' is missing required fields: {missing}"
            )

    def test_all_findings_have_contributor_or_reported_by(self, findings):
        """Each finding must have either a contributor block or reported_by."""
        for finding in findings:
            has_contributor = isinstance(finding.get("contributor"), dict)
            has_reported_by = bool(finding.get("reported_by"))
            assert has_contributor or has_reported_by, (
                f"Finding '{finding.get('id', '???')}' has neither contributor block nor reported_by"
            )

    def test_contributor_blocks_have_required_fields(self, findings):
        """Contributor blocks must have name, team, confidence."""
        for finding in findings:
            contributor = finding.get("contributor")
            if not isinstance(contributor, dict):
                continue
            assert contributor.get("name"), (
                f"Finding '{finding['id']}' contributor missing 'name'"
            )
            assert contributor.get("team"), (
                f"Finding '{finding['id']}' contributor missing 'team'"
            )
            assert contributor.get("confidence") in VALID_CONFIDENCE, (
                f"Finding '{finding['id']}' has invalid confidence "
                f"'{contributor.get('confidence')}'"
            )

    def test_ids_are_unique(self, findings):
        """No duplicate finding IDs."""
        ids = [f["id"] for f in findings]
        duplicates = [fid for fid in ids if ids.count(fid) > 1]
        assert not duplicates, f"Duplicate finding IDs: {set(duplicates)}"

    def test_ids_follow_format(self, findings):
        """All IDs must match FF-YYYYMM-NNN."""
        for finding in findings:
            fid = finding["id"]
            assert ID_PATTERN.match(fid), (
                f"Finding ID '{fid}' does not match expected format FF-YYYYMM-NNN"
            )

    def test_severities_are_valid(self, findings):
        """All severities must be in the allowed set."""
        for finding in findings:
            sev = finding["severity"]
            assert sev in VALID_SEVERITIES, (
                f"Finding '{finding['id']}' has invalid severity '{sev}'. "
                f"Allowed: {VALID_SEVERITIES}"
            )

    def test_statuses_are_valid(self, findings):
        """All statuses must be in the allowed set."""
        for finding in findings:
            status = finding["status"]
            assert status in VALID_STATUSES, (
                f"Finding '{finding['id']}' has invalid status '{status}'. "
                f"Allowed: {VALID_STATUSES}"
            )

    def test_dates_are_valid(self, findings):
        """All dates must parse as valid YYYY-MM-DD dates."""
        for finding in findings:
            date_val = finding["date"]
            # yaml.safe_load may auto-parse dates into datetime.date objects.
            if isinstance(date_val, str):
                try:
                    datetime.strptime(date_val, "%Y-%m-%d")
                except ValueError:
                    pytest.fail(
                        f"Finding '{finding['id']}' has unparseable date '{date_val}'. "
                        "Expected format: YYYY-MM-DD"
                    )
            else:
                # datetime.date object returned by YAML parser is valid.
                assert hasattr(date_val, "year"), (
                    f"Finding '{finding['id']}' date field is not a string or date: {date_val!r}"
                )


# ---------------------------------------------------------------------------
# CLI function tests — use internal helpers from findings_cli
# ---------------------------------------------------------------------------
requires_cli = pytest.mark.skipif(not CLI_AVAILABLE, reason="findings_cli not available")


@requires_cli
class TestFindingsCLISearch:
    def test_search_finds_by_tag(self, findings):
        """Search for 'dep' returns findings that have 'dep' in tags."""
        query = "dep"
        results = []
        for f in findings:
            searchable = " ".join([
                str(f.get("summary", "")),
                str(f.get("detail", "")),
                str(f.get("workaround", "")),
                " ".join(str(t) for t in f.get("tags", [])),
            ]).lower()
            if query in searchable:
                results.append(f)

        assert len(results) > 0, "Expected at least one finding with 'dep' in searchable fields"

    def test_search_finds_by_text(self, findings):
        """Search for 'maintenance' returns maintenance-related findings."""
        query = "maintenance"
        results = []
        for f in findings:
            searchable = " ".join([
                str(f.get("summary", "")),
                str(f.get("detail", "")),
                str(f.get("workaround", "")),
                " ".join(str(t) for t in f.get("tags", [])),
            ]).lower()
            if query in searchable:
                results.append(f)

        assert len(results) > 0, "Expected at least one finding related to 'maintenance'"


@requires_cli
class TestFindingsCLIFilter:
    def test_filter_by_severity(self, findings):
        """Filter by severity HIGH returns only HIGH findings."""
        results = cli.filter_by_severity("HIGH")
        assert len(results) > 0, "Expected at least one HIGH severity finding"
        for r in results:
            assert r["severity"] == "HIGH", f"Expected severity HIGH, got '{r['severity']}'"

    def test_filter_by_client(self):
        """Filter by client 'Pepe' returns Pepe findings."""
        results = cli.filter_by_client("Pepe")
        assert len(results) > 0, "Expected at least one finding for client 'Pepe'"
        for r in results:
            client = cli._get_client(r)
            assert "Pepe" in client, f"Expected client containing 'Pepe', got '{client}'"


@requires_cli
class TestFindingsCLIAdd:
    def test_add_creates_valid_entry(self, tmp_path):
        """Programmatic add produces an entry with all required fields."""
        tmp_tracker = tmp_path / "tracker.yaml"
        tmp_tracker.write_text(yaml.dump({"last_updated": "2026-03-14", "findings": []}))

        entry = cli.add(
            tracker_path=str(tmp_tracker),
            name="Test User",
            team="Test Team",
            confidence="validated",
            client="Test Client",
            product="ADB-S",
            severity="LOW",
            category="gotcha",
            summary="Test finding for unit tests",
            detail="This is a test finding.",
            status="open",
        )

        assert isinstance(entry, dict)
        missing = REQUIRED_FIELDS - set(entry.keys())
        assert not missing, f"Added entry missing fields: {missing}"
        assert entry["severity"] in VALID_SEVERITIES
        assert entry["status"] in VALID_STATUSES
        assert isinstance(entry.get("contributor"), dict)
        assert entry["contributor"]["name"] == "Test User"
        assert entry["contributor"]["team"] == "Test Team"
        assert entry["contributor"]["confidence"] == "validated"

    def test_add_with_legacy_reported_by(self, tmp_path):
        """Legacy reported_by parameter is supported for backward compat."""
        tmp_tracker = tmp_path / "tracker.yaml"
        tmp_tracker.write_text(yaml.dump({"last_updated": "2026-03-14", "findings": []}))

        entry = cli.add(
            tracker_path=str(tmp_tracker),
            reported_by="Legacy User",
            product="ADB-S",
            severity="INFO",
            summary="Legacy add test",
            status="open",
        )

        assert entry["contributor"]["name"] == "Legacy User"
        assert entry["reported_by"] == "Legacy User"

    def test_auto_id_generation(self, tmp_path):
        """Generated ID should use current year-month format (FF-YYYYMM-NNN)."""
        tmp_tracker = tmp_path / "tracker.yaml"
        tmp_tracker.write_text(yaml.dump({"last_updated": "2026-03-14", "findings": []}))

        entry = cli.add(
            tracker_path=str(tmp_tracker),
            name="Test User",
            team="Test Team",
            product="ADB-S",
            severity="INFO",
            category="gotcha",
            summary="Auto-ID test",
            detail="Testing auto ID generation.",
            status="open",
        )

        fid = entry["id"]
        assert ID_PATTERN.match(fid), f"Generated ID '{fid}' does not match FF-YYYYMM-NNN"
        now = datetime.now()
        expected_prefix = f"FF-{now.strftime('%Y%m')}-"
        assert fid.startswith(expected_prefix), (
            f"Generated ID '{fid}' does not start with '{expected_prefix}'"
        )
        assert fid.endswith("-001"), f"Expected first generated ID to end with '-001', got '{fid}'"


@requires_cli
class TestFindingsCLIConfirm:
    def test_confirm_adds_confirmation(self, tmp_path):
        """Confirm command adds a confirmation entry to a finding."""
        tmp_tracker = tmp_path / "tracker.yaml"
        tmp_tracker.write_text(yaml.dump({"last_updated": "2026-03-14", "findings": []}))

        # First add a finding
        entry = cli.add(
            tracker_path=str(tmp_tracker),
            name="Original Author",
            team="Team A",
            product="ADB-S",
            severity="HIGH",
            summary="Test finding to confirm",
            status="open",
        )

        # Confirm it
        confirmation = cli.confirm(
            finding_id=entry["id"],
            name="Reviewer Name",
            team="Team B",
            note="Confirmed same behavior in my environment.",
            tracker_path=str(tmp_tracker),
        )

        assert confirmation["name"] == "Reviewer Name"
        assert confirmation["team"] == "Team B"
        assert confirmation["note"] == "Confirmed same behavior in my environment."

        # Verify it was persisted
        data = yaml.safe_load(tmp_tracker.read_text())
        finding = data["findings"][0]
        assert len(finding["confirmations"]) == 1
        assert finding["confirmations"][0]["name"] == "Reviewer Name"

    def test_confirm_nonexistent_finding_raises(self, tmp_path):
        """Confirming a nonexistent finding should raise LookupError."""
        tmp_tracker = tmp_path / "tracker.yaml"
        tmp_tracker.write_text(yaml.dump({"last_updated": "2026-03-14", "findings": []}))

        with pytest.raises(LookupError):
            cli.confirm(
                finding_id="FF-999999-999",
                name="Test",
                team="Test",
                tracker_path=str(tmp_tracker),
            )


@requires_cli
class TestFindingsCLIStats:
    def test_stats_counts_correct(self, findings):
        """Stats should return correct totals per category."""
        s = cli.stats()
        assert s["total"] == len(findings), (
            f"Stats total ({s['total']}) does not match findings count ({len(findings)})"
        )
        total_by_severity = sum(s["by_severity"].values())
        total_by_status = sum(s["by_status"].values())
        assert total_by_severity == len(findings), (
            f"Severity counts ({total_by_severity}) do not sum to total findings ({len(findings)})"
        )
        assert total_by_status == len(findings), (
            f"Status counts ({total_by_status}) do not sum to total findings ({len(findings)})"
        )


@requires_cli
class TestTagValidation:
    def test_valid_tags_pass(self):
        """Known taxonomy tags should not produce warnings."""
        warnings = cli.validate_tags(["adb-s", "ha", "dr"])
        assert len(warnings) == 0

    def test_unknown_tags_produce_warnings(self):
        """Unknown tags should produce warning messages."""
        warnings = cli.validate_tags(["totally-fake-tag-xyz"])
        assert len(warnings) > 0
        assert "Unknown tag" in warnings[0]

    def test_fuzzy_match_suggestion(self):
        """Tags close to valid ones should suggest corrections."""
        warnings = cli.validate_tags(["adb_s"])
        # Should suggest 'adb-s'
        assert len(warnings) > 0
        assert "adb-s" in warnings[0]
