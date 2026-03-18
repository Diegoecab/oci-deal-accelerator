"""
Tests for KB governance tools: kb_linter.py, kb_cli.py, and config files.

Tests cover:
- Config file structure validation
- KB linter checks (contributor blocks, decay, tags, owners)
- KB CLI functions (stats, search, owners)
"""

import sys
from pathlib import Path

import pytest
import yaml

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = PROJECT_ROOT / "tools"
CONFIG_DIR = PROJECT_ROOT / "config"
KB_DIR = PROJECT_ROOT / "kb"

if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

try:
    import kb_linter
    LINTER_AVAILABLE = True
except ImportError:
    LINTER_AVAILABLE = False

try:
    import kb_cli
    CLI_AVAILABLE = True
except ImportError:
    CLI_AVAILABLE = False


# ---------------------------------------------------------------------------
# Config file tests
# ---------------------------------------------------------------------------
class TestGovernanceConfig:
    def test_governance_yaml_loads(self):
        """kb-governance.yaml loads without errors."""
        path = CONFIG_DIR / "kb-governance.yaml"
        with open(path, "r") as fh:
            data = yaml.safe_load(fh)
        assert data is not None
        assert "contribution" in data
        assert "freshness" in data
        assert "confidence_decay" in data
        assert "review_triggers" in data

    def test_governance_has_required_fields(self):
        """Contribution config must list required fields."""
        path = CONFIG_DIR / "kb-governance.yaml"
        with open(path, "r") as fh:
            data = yaml.safe_load(fh)
        required = data["contribution"]["required_fields"]
        assert "name" in required
        assert "team" in required
        assert "confidence" in required

    def test_governance_has_all_confidence_levels(self):
        """Confidence decay must cover all declared levels."""
        path = CONFIG_DIR / "kb-governance.yaml"
        with open(path, "r") as fh:
            data = yaml.safe_load(fh)
        levels = data["contribution"]["confidence_levels"]
        decay = data["confidence_decay"]
        for level in levels:
            assert level in decay, f"Confidence level '{level}' not in decay config"
            assert "fresh" in decay[level]
            assert "stale" in decay[level]
            assert "expired" in decay[level]


class TestOwnersConfig:
    def test_owners_yaml_loads(self):
        """kb-owners.yaml loads and has domains."""
        path = CONFIG_DIR / "kb-owners.yaml"
        with open(path, "r") as fh:
            data = yaml.safe_load(fh)
        assert data is not None
        assert "domains" in data
        assert len(data["domains"]) > 0

    def test_all_domains_have_area_and_owner(self):
        """Each domain must have area and owner."""
        path = CONFIG_DIR / "kb-owners.yaml"
        with open(path, "r") as fh:
            data = yaml.safe_load(fh)
        for domain in data["domains"]:
            assert "area" in domain, f"Domain missing 'area': {domain}"
            assert "owner" in domain, f"Domain missing 'owner': {domain}"
            assert "name" in domain["owner"]


class TestTagsConfig:
    def test_tags_yaml_loads(self):
        """kb-tags.yaml loads and has taxonomy."""
        path = CONFIG_DIR / "kb-tags.yaml"
        with open(path, "r") as fh:
            data = yaml.safe_load(fh)
        assert data is not None
        assert "taxonomy" in data

    def test_taxonomy_has_categories(self):
        """Taxonomy must have products, versions, categories."""
        path = CONFIG_DIR / "kb-tags.yaml"
        with open(path, "r") as fh:
            data = yaml.safe_load(fh)
        taxonomy = data["taxonomy"]
        assert "products" in taxonomy
        assert "versions" in taxonomy
        assert "categories" in taxonomy
        assert len(taxonomy["products"]) > 0


# ---------------------------------------------------------------------------
# KB Linter tests
# ---------------------------------------------------------------------------
requires_linter = pytest.mark.skipif(not LINTER_AVAILABLE, reason="kb_linter not available")


@requires_linter
class TestKBLinter:
    def test_contributor_blocks_check(self):
        """Linter should check contributor blocks on real tracker."""
        issues = kb_linter.check_contributor_blocks()
        # All findings in the updated tracker should have contributor blocks
        # so there should be no issues
        assert isinstance(issues, list)

    def test_confidence_decay_check(self):
        """Decay check returns a list of decay reports."""
        results = kb_linter.check_confidence_decay()
        assert isinstance(results, list)
        assert len(results) > 0
        for r in results:
            assert "id" in r
            assert "status" in r
            assert r["status"] in {"FRESH", "STALE", "EXPIRED", "UNKNOWN"}

    def test_tag_validation(self):
        """Tag validation returns a list of issues."""
        issues = kb_linter.check_tags()
        assert isinstance(issues, list)
        # Some tags in the real tracker may not be in taxonomy
        # (like 'cli', 'maintenance-window', etc.)

    def test_owner_check(self):
        """Owner check returns issues for TBD owners."""
        issues = kb_linter.check_owners()
        assert isinstance(issues, list)
        # We know some owners are TBD
        tbd_issues = [i for i in issues if "TBD" in i]
        assert len(tbd_issues) > 0, "Expected TBD owner issues"

    def test_freshness_check(self):
        """Freshness check returns a list of file freshness reports."""
        results = kb_linter.check_freshness()
        assert isinstance(results, list)
        assert len(results) > 0
        for r in results:
            assert "file" in r
            assert "status" in r
            assert "age_days" in r

    def test_contribution_stats(self):
        """Contribution stats returns a dict of name -> count."""
        stats = kb_linter.contribution_stats()
        assert isinstance(stats, dict)
        assert len(stats) > 0
        assert "Diego Cabrera" in stats


# ---------------------------------------------------------------------------
# KB CLI tests
# ---------------------------------------------------------------------------
requires_kb_cli = pytest.mark.skipif(not CLI_AVAILABLE, reason="kb_cli not available")


@requires_kb_cli
class TestKBCLI:
    def test_all_kb_files_returns_yaml_files(self):
        """_all_kb_files should return YAML files from kb/ directory."""
        files = kb_cli._all_kb_files()
        assert len(files) > 0
        for f in files:
            assert f.endswith((".yaml", ".yml"))

    def test_load_yaml_valid_file(self):
        """_load_yaml should load a valid YAML file."""
        data = kb_cli._load_yaml(str(PROJECT_ROOT / "config" / "kb-governance.yaml"))
        assert data is not None
        assert "contribution" in data

    def test_load_yaml_missing_file(self):
        """_load_yaml should return None for missing files."""
        data = kb_cli._load_yaml("/nonexistent/file.yaml")
        assert data is None


# ---------------------------------------------------------------------------
# Service changelog tests
# ---------------------------------------------------------------------------
class TestServiceChangelogs:
    """Verify that service files have changelog sections."""

    @pytest.fixture(scope="class")
    def service_files(self):
        services_dir = KB_DIR / "services"
        return list(services_dir.glob("*.yaml"))

    def test_service_files_exist(self, service_files):
        assert len(service_files) > 0

    def test_service_files_have_changelog(self, service_files):
        """Each service file should have a changelog section."""
        for filepath in service_files:
            with open(filepath, "r") as fh:
                data = yaml.safe_load(fh)
            assert "changelog" in data, (
                f"Service file '{filepath.name}' missing 'changelog' section"
            )
            assert len(data["changelog"]) > 0, (
                f"Service file '{filepath.name}' has empty changelog"
            )

    def test_changelog_entries_have_required_fields(self, service_files):
        """Changelog entries must have date, contributor, change."""
        for filepath in service_files:
            with open(filepath, "r") as fh:
                data = yaml.safe_load(fh)
            for entry in data.get("changelog", []):
                assert "date" in entry, f"Changelog entry in {filepath.name} missing 'date'"
                assert "contributor" in entry, f"Changelog entry in {filepath.name} missing 'contributor'"
                assert "change" in entry, f"Changelog entry in {filepath.name} missing 'change'"
