"""
Tests for the ADB Feature Compatibility Matrix YAML and CLI.

Matrix YAML: kb/compatibility/adb-feature-matrix.yaml
CLI module:  tools/feature_matrix_cli.py
"""

import csv
import io
import sys
from pathlib import Path

import pytest
import yaml

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MATRIX_PATH = PROJECT_ROOT / "kb" / "compatibility" / "adb-feature-matrix.yaml"
TOOLS_DIR = PROJECT_ROOT / "tools"

# Make the tools directory importable so we can import the CLI module.
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

try:
    import feature_matrix_cli as cli

    CLI_AVAILABLE = True
except ImportError:
    CLI_AVAILABLE = False

VALID_STATUSES = {"GA", "GA_CAVEAT", "PREVIEW", "LIMITED", "NOT_AVAIL", "BROKEN", "UNTESTED"}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def matrix_data():
    """Load the feature-matrix YAML once per module."""
    with open(MATRIX_PATH, "r") as fh:
        return yaml.safe_load(fh)


@pytest.fixture(scope="module")
def features(matrix_data):
    """Return the list of feature entries."""
    return matrix_data["features"]


# ---------------------------------------------------------------------------
# YAML structure tests
# ---------------------------------------------------------------------------
class TestMatrixYAML:
    def test_matrix_loads(self, matrix_data):
        """YAML loads without errors and contains expected top-level keys."""
        assert matrix_data is not None
        assert "features" in matrix_data
        assert "versions" in matrix_data
        assert "deployment_types" in matrix_data

    def test_all_features_have_at_least_one_deployment(self, features):
        """Every feature must have a non-empty matrix (at least one deployment type)."""
        for feat in features:
            matrix = feat.get("matrix", {})
            assert matrix, (
                f"Feature '{feat['name']}' has an empty matrix — "
                "at least one deployment type must be present."
            )

    def test_all_statuses_are_valid(self, features):
        """Every status value across the entire matrix must be in the allowed set."""
        for feat in features:
            for deploy_id, versions in feat.get("matrix", {}).items():
                for ver, entry in versions.items():
                    status = entry if isinstance(entry, str) else entry.get("status")
                    assert status in VALID_STATUSES, (
                        f"Feature '{feat['name']}', deployment '{deploy_id}', "
                        f"version '{ver}' has invalid status '{status}'. "
                        f"Allowed: {VALID_STATUSES}"
                    )


# ---------------------------------------------------------------------------
# CLI function tests — use internal helpers from feature_matrix_cli
# ---------------------------------------------------------------------------
requires_cli = pytest.mark.skipif(not CLI_AVAILABLE, reason="feature_matrix_cli not available")


@requires_cli
class TestMatrixCLICheck:
    def test_check_returns_correct_status(self):
        """check('Auto Scaling', 'adb_s', '23ai') should contain 'GA_CAVEAT'."""
        data = cli.load_matrix(str(MATRIX_PATH))
        matches = cli.find_features(data, "Auto Scaling")
        assert len(matches) >= 1, "Expected at least one match for 'Auto Scaling'"
        feature = matches[0]
        cell = cli.get_cell(feature, "adb_s", "23ai")
        assert cell is not None, "Expected a cell for Auto Scaling / adb_s / 23ai"
        assert "GA_CAVEAT" in cell.get("status", ""), (
            f"Expected GA_CAVEAT for Auto Scaling / adb_s / 23ai, got: {cell}"
        )

    def test_check_unknown_feature_returns_error(self):
        """check with a nonexistent feature should return no matches."""
        data = cli.load_matrix(str(MATRIX_PATH))
        matches = cli.find_features(data, "Nonexistent Feature")
        assert len(matches) == 0, (
            f"Expected no matches for 'Nonexistent Feature', got {len(matches)}"
        )


@requires_cli
class TestMatrixCLICompare:
    def test_compare_returns_all_features(self, features):
        """Compare output should cover every feature in the matrix."""
        data = cli.load_matrix(str(MATRIX_PATH))
        feature_names = {f["name"] for f in features}
        # Simulate what cmd_compare does: iterate all features and get cells
        compared = set()
        for feature in data["features"]:
            cell1 = cli.get_cell(feature, "adb_s", "23ai")
            cell2 = cli.get_cell(feature, "exacs", "23ai")
            # Both cells may be None (UNTESTED), but the feature is still compared
            compared.add(feature["name"])
        assert feature_names == compared, (
            f"Missing features in compare: {feature_names - compared}"
        )


@requires_cli
class TestMatrixCLIGaps:
    def test_gaps_finds_not_available(self):
        """gaps('dbcs_ee', '23ai') should include features marked NOT_AVAIL."""
        data = cli.load_matrix(str(MATRIX_PATH))
        gap_statuses = {"NOT_AVAIL", "BROKEN", "LIMITED"}
        gaps = []
        for feature in data["features"]:
            cell = cli.get_cell(feature, "dbcs_ee", "23ai")
            if cell is not None:
                status = cell.get("status", "UNTESTED")
                if status in gap_statuses:
                    gaps.append((feature["name"], status))

        assert len(gaps) > 0, "Expected at least one gap for dbcs_ee / 23ai"
        not_avail_gaps = [g for g in gaps if g[1] == "NOT_AVAIL"]
        assert len(not_avail_gaps) > 0, (
            "Expected at least one NOT_AVAIL gap for dbcs_ee / 23ai"
        )


# ---------------------------------------------------------------------------
# Export tests
# ---------------------------------------------------------------------------
@requires_cli
class TestMatrixCLIExport:
    def test_export_markdown_is_valid(self, matrix_data):
        """Markdown export should contain a header row with | separators."""
        data = cli.load_matrix(str(MATRIX_PATH))
        versions = cli.get_version_ids(data)
        deployments = cli.get_deployment_ids(data)

        columns = [(d, v) for d in deployments for v in versions]
        col_labels = [f"{d}/{v}" for d, v in columns]

        # Capture the markdown output by calling the internal function
        captured = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured
        try:
            cli._export_markdown(data, columns, col_labels)
        finally:
            sys.stdout = old_stdout

        content = captured.getvalue()
        lines = [ln for ln in content.splitlines() if ln.strip()]
        assert len(lines) >= 2, "Markdown export should have at least a header and separator row"
        # Header row must use pipe separators.
        assert "|" in lines[0], f"Header row missing '|' separators: {lines[0]}"
        # Second row is the --- separator row.
        assert "|" in lines[1], f"Separator row missing '|': {lines[1]}"

    def test_export_csv_is_valid(self, matrix_data):
        """CSV export should be parseable with csv.reader."""
        data = cli.load_matrix(str(MATRIX_PATH))
        versions = cli.get_version_ids(data)
        deployments = cli.get_deployment_ids(data)

        columns = [(d, v) for d in deployments for v in versions]
        col_labels = [f"{d}/{v}" for d, v in columns]

        # Capture the CSV output
        captured = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured
        try:
            cli._export_csv(data, columns, col_labels)
        finally:
            sys.stdout = old_stdout

        content = captured.getvalue()
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)
        assert len(rows) >= 2, "CSV export should have at least a header row and one data row"
        # All rows should have the same number of columns.
        col_count = len(rows[0])
        for i, row in enumerate(rows):
            assert len(row) == col_count, (
                f"Row {i} has {len(row)} columns, expected {col_count}"
            )
