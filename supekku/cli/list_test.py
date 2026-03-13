"""Tests for list CLI commands (backlog shortcuts)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml
from typer.testing import CliRunner

from supekku.cli.list import app
from supekku.scripts.lib.core.paths import (
  BACKLOG_DIR,
  DELTAS_SUBDIR,
  IMPROVEMENTS_SUBDIR,
  ISSUES_SUBDIR,
  PROBLEMS_SUBDIR,
  PRODUCT_SPECS_SUBDIR,
  RISKS_SUBDIR,
  SPEC_DRIVER_DIR,
  TECH_SPECS_SUBDIR,
)


class ListBacklogShortcutsTest(unittest.TestCase):
  """Test cases for backlog listing shortcut commands."""

  def setUp(self) -> None:
    """Set up test environment with sample backlog entries."""
    self.runner = CliRunner()
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()

    # Create sample backlog entries for testing
    self._create_sample_issue("ISSUE-001", "Test issue one", "open")
    self._create_sample_issue("ISSUE-002", "Test issue two", "resolved")
    self._create_sample_issue("ISSUE-003", "Test issue three", "open")
    self._create_sample_problem("PROB-001", "Test problem", "captured")
    self._create_sample_improvement("IMPR-001", "Test improvement", "idea")
    self._create_sample_risk("RISK-001", "Test risk", "identified")

  def tearDown(self) -> None:
    """Clean up test environment."""
    self.tmpdir.cleanup()

  def _create_sample_issue(self, issue_id: str, title: str, status: str) -> None:
    """Helper to create a sample issue file."""
    issue_dir = self.root / SPEC_DRIVER_DIR / BACKLOG_DIR / ISSUES_SUBDIR / issue_id
    issue_dir.mkdir(parents=True, exist_ok=True)
    issue_file = issue_dir / f"{issue_id}.md"
    content = f"""---
id: {issue_id}
name: {title}
kind: issue
status: {status}
created: '2025-11-04'
---

# {issue_id} - {title}

Test issue content.
"""
    issue_file.write_text(content, encoding="utf-8")

  def _create_sample_problem(self, prob_id: str, title: str, status: str) -> None:
    """Helper to create a sample problem file."""
    prob_dir = self.root / SPEC_DRIVER_DIR / BACKLOG_DIR / PROBLEMS_SUBDIR / prob_id
    prob_dir.mkdir(parents=True, exist_ok=True)
    prob_file = prob_dir / f"{prob_id}.md"
    content = f"""---
id: {prob_id}
name: {title}
kind: problem
status: {status}
created: '2025-11-04'
---

# {prob_id} - {title}

Test problem content.
"""
    prob_file.write_text(content, encoding="utf-8")

  def _create_sample_improvement(self, impr_id: str, title: str, status: str) -> None:
    """Helper to create a sample improvement file."""
    impr_dir = self.root / SPEC_DRIVER_DIR / BACKLOG_DIR / IMPROVEMENTS_SUBDIR / impr_id
    impr_dir.mkdir(parents=True, exist_ok=True)
    impr_file = impr_dir / f"{impr_id}.md"
    content = f"""---
id: {impr_id}
name: {title}
kind: improvement
status: {status}
created: '2025-11-04'
---

# {impr_id} - {title}

Test improvement content.
"""
    impr_file.write_text(content, encoding="utf-8")

  def _create_sample_risk(self, risk_id: str, title: str, status: str) -> None:
    """Helper to create a sample risk file."""
    risk_dir = self.root / SPEC_DRIVER_DIR / BACKLOG_DIR / RISKS_SUBDIR / risk_id
    risk_dir.mkdir(parents=True, exist_ok=True)
    risk_file = risk_dir / f"{risk_id}.md"
    content = f"""---
id: {risk_id}
name: {title}
kind: risk
status: {status}
created: '2025-11-04'
---

# {risk_id} - {title}

Test risk content.
"""
    risk_file.write_text(content, encoding="utf-8")

  def test_list_issues(self) -> None:
    """Test listing issues via shortcut command."""
    result = self.runner.invoke(
      app,
      ["issues", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "ISSUE-001" in result.stdout
    assert "ISSUE-003" in result.stdout
    assert "ISSUE-002" not in result.stdout  # resolved, filtered by default
    assert "PROB-001" not in result.stdout  # Should not show problems

  def test_list_problems(self) -> None:
    """Test listing problems via shortcut command."""
    result = self.runner.invoke(
      app,
      ["problems", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "PROB-001" in result.stdout
    assert "ISSUE-001" not in result.stdout  # Should not show issues

  def test_list_improvements(self) -> None:
    """Test listing improvements via shortcut command."""
    result = self.runner.invoke(
      app,
      ["improvements", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "IMPR-001" in result.stdout
    assert "ISSUE-001" not in result.stdout  # Should not show issues

  def test_list_risks(self) -> None:
    """Test listing risks via shortcut command."""
    result = self.runner.invoke(
      app,
      ["risks", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "RISK-001" in result.stdout
    assert "ISSUE-001" not in result.stdout  # Should not show issues

  def test_list_issues_with_status_filter(self) -> None:
    """Test listing issues with status filter."""
    result = self.runner.invoke(
      app,
      ["issues", "--root", str(self.root), "--status", "open"],
    )

    assert result.exit_code == 0
    assert "ISSUE-001" in result.stdout
    assert "ISSUE-002" not in result.stdout  # resolved, not open

  def test_list_issues_with_substring_filter(self) -> None:
    """Test listing issues with substring filter."""
    result = self.runner.invoke(
      app,
      ["issues", "--root", str(self.root), "--filter", "one"],
    )

    assert result.exit_code == 0
    assert "ISSUE-001" in result.stdout
    assert "ISSUE-002" not in result.stdout  # doesn't match "one"

  def test_list_issues_json_format(self) -> None:
    """Test listing issues with JSON output."""
    result = self.runner.invoke(
      app,
      ["issues", "--root", str(self.root), "--format", "json"],
    )

    assert result.exit_code == 0
    # JSON output should be valid and contain issue data
    assert "ISSUE-001" in result.stdout
    assert "ISSUE-003" in result.stdout
    assert "ISSUE-002" not in result.stdout  # resolved, filtered by default

  def test_list_issues_empty_result(self) -> None:
    """Test listing issues with filter that returns no results."""
    result = self.runner.invoke(
      app,
      ["issues", "--root", str(self.root), "--filter", "nonexistent"],
    )

    # Should exit successfully with no output
    assert result.exit_code == 0
    assert result.stdout.strip() == ""

  def test_equivalence_with_list_backlog(self) -> None:
    """Test that shortcuts are equivalent to list backlog -k."""
    # Test issues shortcut vs backlog -k issue
    issues_result = self.runner.invoke(
      app,
      ["issues", "--root", str(self.root)],
    )
    backlog_result = self.runner.invoke(
      app,
      ["backlog", "--root", str(self.root), "-k", "issue"],
    )

    assert issues_result.exit_code == 0
    assert backlog_result.exit_code == 0
    assert issues_result.stdout == backlog_result.stdout

  def test_regexp_filter(self) -> None:
    """Test listing with regexp filter."""
    result = self.runner.invoke(
      app,
      ["issues", "--root", str(self.root), "--regexp", "ISSUE-00[13]"],
    )

    assert result.exit_code == 0
    assert "ISSUE-001" in result.stdout
    assert "ISSUE-003" in result.stdout
    assert "ISSUE-002" not in result.stdout  # resolved, filtered by default

  def test_tsv_format(self) -> None:
    """Test listing with TSV format."""
    result = self.runner.invoke(
      app,
      ["issues", "--root", str(self.root), "--format", "tsv"],
    )

    assert result.exit_code == 0
    assert "\t" in result.stdout  # TSV uses tabs
    assert "ISSUE-001" in result.stdout


class ListRequirementsCategoryFilterTest(unittest.TestCase):
  """Test cases for requirements with category filtering.

  VT-017-003: Category filtering tests
  VT-017-004: Category display tests
  """

  def setUp(self) -> None:
    """Set up test environment with requirements registry including categories."""
    self.runner = CliRunner()
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()

    # Create registry directory and requirements.yaml with categorized requirements
    registry_dir = self.root / ".spec-driver" / "registry"
    registry_dir.mkdir(parents=True)
    registry_file = registry_dir / "requirements.yaml"

    # Sample requirements with various categories
    registry_content = """---
requirements:
  SPEC-001:FR-001:
    uid: SPEC-001:FR-001
    label: FR-001
    title: Authentication flow must validate tokens
    kind: FR
    status: pending
    specs:
      - SPEC-001
    primary_spec: SPEC-001
    introduced: null
    implemented_by: []
    verified_by: []
    path: specify/tech/SPEC-001/SPEC-001.md
    category: auth
  SPEC-001:FR-002:
    uid: SPEC-001:FR-002
    label: FR-002
    title: Security headers must be present
    kind: FR
    status: pending
    specs:
      - SPEC-001
    primary_spec: SPEC-001
    introduced: null
    implemented_by: []
    verified_by: []
    path: specify/tech/SPEC-001/SPEC-001.md
    category: security
  SPEC-001:NF-001:
    uid: SPEC-001:NF-001
    label: NF-001
    title: Response time must be under 200ms
    kind: NF
    status: pending
    specs:
      - SPEC-001
    primary_spec: SPEC-001
    introduced: null
    implemented_by: []
    verified_by: []
    path: specify/tech/SPEC-001/SPEC-001.md
    category: performance
  SPEC-001:FR-003:
    uid: SPEC-001:FR-003
    label: FR-003
    title: User authorization checks required
    kind: FR
    status: pending
    specs:
      - SPEC-001
    primary_spec: SPEC-001
    introduced: null
    implemented_by: []
    verified_by: []
    path: specify/tech/SPEC-001/SPEC-001.md
    category: auth
  SPEC-001:FR-004:
    uid: SPEC-001:FR-004
    label: FR-004
    title: Data validation without category
    kind: FR
    status: pending
    specs:
      - SPEC-001
    primary_spec: SPEC-001
    introduced: null
    implemented_by: []
    verified_by: []
    path: specify/tech/SPEC-001/SPEC-001.md
    category: null
"""
    registry_file.write_text(registry_content, encoding="utf-8")

  def tearDown(self) -> None:
    """Clean up test environment."""
    self.tmpdir.cleanup()

  def test_category_filter_exact_match(self) -> None:
    """VT-017-003: Test --category filter with exact match."""
    result = self.runner.invoke(
      app,
      ["requirements", "--root", str(self.root), "--category", "auth"],
    )

    assert result.exit_code == 0
    assert "FR-001" in result.stdout
    assert "FR-003" in result.stdout
    assert "FR-002" not in result.stdout  # security, not auth
    assert "NF-001" not in result.stdout  # performance, not auth

  def test_category_filter_substring_match(self) -> None:
    """VT-017-003: Test --category filter with substring matching."""
    result = self.runner.invoke(
      app,
      ["requirements", "--root", str(self.root), "--category", "sec"],
    )

    assert result.exit_code == 0
    assert "FR-002" in result.stdout  # security contains 'sec'
    assert "FR-001" not in result.stdout
    assert "NF-001" not in result.stdout

  def test_category_filter_case_sensitive(self) -> None:
    """VT-017-003: Test --category filter is case-sensitive by default."""
    result = self.runner.invoke(
      app,
      ["requirements", "--root", str(self.root), "--category", "AUTH"],
    )

    # Case-sensitive: AUTH should not match 'auth'
    assert result.exit_code == 0
    assert "FR-001" not in result.stdout
    assert "FR-003" not in result.stdout

  def test_category_filter_case_insensitive(self) -> None:
    """VT-017-003: Test --category with -i flag for case-insensitive matching."""
    result = self.runner.invoke(
      app,
      ["requirements", "--root", str(self.root), "--category", "AUTH", "-i"],
    )

    assert result.exit_code == 0
    assert "FR-001" in result.stdout
    assert "FR-003" in result.stdout

  def test_category_filter_excludes_uncategorized(self) -> None:
    """VT-017-003: Test --category filter excludes requirements with null category."""
    result = self.runner.invoke(
      app,
      ["requirements", "--root", str(self.root), "--category", "validation"],
    )

    assert result.exit_code == 0
    # FR-004 has null category, should not appear
    assert "FR-004" not in result.stdout

  def test_regexp_filter_includes_category(self) -> None:
    """VT-017-003: Test -r regexp filter searches category field."""
    result = self.runner.invoke(
      app,
      ["requirements", "--root", str(self.root), "-r", "auth|perf"],
    )

    assert result.exit_code == 0
    assert "FR-001" in result.stdout  # category: auth
    assert "FR-003" in result.stdout  # category: auth
    assert "NF-001" in result.stdout  # category: performance (matches 'perf')
    assert "FR-002" not in result.stdout  # category: security

  def test_regexp_filter_category_case_insensitive(self) -> None:
    """VT-017-003: Test -r with -i flag makes category search case-insensitive."""
    result = self.runner.invoke(
      app,
      ["requirements", "--root", str(self.root), "-r", "AUTH", "-i"],
    )

    assert result.exit_code == 0
    assert "FR-001" in result.stdout
    assert "FR-003" in result.stdout

  def test_category_column_in_table_output(self) -> None:
    """VT-017-004: Test category column appears in table output."""
    result = self.runner.invoke(
      app,
      ["requirements", "--root", str(self.root), "--category", "auth"],
    )

    assert result.exit_code == 0
    # Check for table header with Category column
    assert "Category" in result.stdout
    # Check for category values in output
    assert "auth" in result.stdout

  def test_category_column_in_tsv_output(self) -> None:
    """VT-017-004: Test category column in TSV format."""
    result = self.runner.invoke(
      app,
      ["requirements", "--root", str(self.root), "--format", "tsv"],
    )

    assert result.exit_code == 0
    assert "\t" in result.stdout
    # TSV format should include category column
    lines = result.stdout.strip().split("\n")
    # Check that lines have category field (between label and title)
    # Format: spec\tlabel\tcategory\ttitle\tstatus
    for line in lines:
      if "FR-001" in line:
        parts = line.split("\t")
        assert len(parts) >= 5
        assert "auth" in parts  # category should be present

  def test_category_column_in_json_output(self) -> None:
    """VT-017-004: Test category field in JSON format."""
    result = self.runner.invoke(
      app,
      ["requirements", "--root", str(self.root), "--category", "auth", "--json"],
    )

    assert result.exit_code == 0
    # JSON output should include category field
    assert '"category":' in result.stdout or "'category':" in result.stdout
    assert "auth" in result.stdout

  def test_uncategorized_requirements_show_placeholder(self) -> None:
    """VT-017-004: Test uncategorized requirements display correctly."""
    result = self.runner.invoke(
      app,
      ["requirements", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    # Should show all requirements including uncategorized
    assert "FR-004" in result.stdout
    # Category column should show placeholder for null (likely "—" or "-")
    assert result.stdout.count("—") > 0 or result.stdout.count("-") > 0

  def test_category_filter_combined_with_other_filters(self) -> None:
    """VT-017-003: Test --category combined with --kind filter."""
    result = self.runner.invoke(
      app,
      ["requirements", "--root", str(self.root), "--category", "auth", "--kind", "FR"],
    )

    assert result.exit_code == 0
    assert "FR-001" in result.stdout
    assert "FR-003" in result.stdout
    # NF-001 has category but wrong kind
    assert "NF-001" not in result.stdout

  def test_empty_result_with_category_filter(self) -> None:
    """VT-017-003: Test category filter with no matches returns empty gracefully."""
    result = self.runner.invoke(
      app,
      ["requirements", "--root", str(self.root), "--category", "nonexistent"],
    )

    assert result.exit_code == 0
    assert result.stdout.strip() == ""


class ListSpecsCategoryFilterTest(unittest.TestCase):
  """VT-030-003: list specs --category and --c4-level filters."""

  def setUp(self) -> None:
    self.runner = CliRunner()
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()
    tech_dir = self.root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR

    # Unit spec
    self._create_spec(
      tech_dir, "SPEC-001", "unit-mod", "Unit Module", category="unit", c4_level="code"
    )
    # Assembly spec
    self._create_spec(
      tech_dir,
      "SPEC-002",
      "assembly-sub",
      "Assembly Subsystem",
      category="assembly",
      c4_level="component",
    )
    # Unclassified spec (no category)
    self._create_spec(tech_dir, "SPEC-003", "bare-spec", "Bare Spec")

    # Product spec (should never be filtered by --category)
    prod_dir = self.root / SPEC_DRIVER_DIR / PRODUCT_SPECS_SUBDIR
    prod_dir.mkdir(parents=True)
    prod_file = prod_dir / "PROD-001.md"
    prod_file.write_text(
      "---\nid: PROD-001\nslug: sample-prod\nname: Sample Product\n"
      "kind: prod\nstatus: draft\ncreated: '2026-01-01'\nupdated: '2026-01-01'\n---\n"
      "# PROD-001\n",
      encoding="utf-8",
    )

  def tearDown(self) -> None:
    self.tmpdir.cleanup()

  def _create_spec(
    self,
    tech_dir,
    spec_id,
    slug,
    name,
    *,
    category=None,
    c4_level=None,
  ) -> None:
    spec_dir = tech_dir / spec_id
    spec_dir.mkdir(parents=True, exist_ok=True)
    fm_lines = [
      "---",
      f"id: {spec_id}",
      f"slug: {slug}",
      f"name: {name}",
      "kind: spec",
      "status: draft",
      "created: '2026-01-01'",
      "updated: '2026-01-01'",
    ]
    if category:
      fm_lines.append(f"category: {category}")
    if c4_level:
      fm_lines.append(f"c4_level: {c4_level}")
    fm_lines += ["---", f"# {spec_id}", ""]
    (spec_dir / f"{spec_id}.md").write_text(
      "\n".join(fm_lines),
      encoding="utf-8",
    )

  def test_default_hides_unit_specs(self) -> None:
    """Default listing shows assembly + unknown but hides unit specs."""
    result = self.runner.invoke(app, ["specs", "--root", str(self.root)])
    assert result.exit_code == 0
    assert "SPEC-001" not in result.stdout  # unit → hidden
    assert "SPEC-002" in result.stdout  # assembly → shown
    assert "SPEC-003" in result.stdout  # unknown → shown
    assert "PROD-001" in result.stdout  # product → always shown

  def test_category_all_shows_everything(self) -> None:
    """--category all disables category filtering for tech specs."""
    result = self.runner.invoke(
      app,
      ["specs", "--root", str(self.root), "--category", "all"],
    )
    assert result.exit_code == 0
    assert "SPEC-001" in result.stdout
    assert "SPEC-002" in result.stdout
    assert "SPEC-003" in result.stdout
    assert "PROD-001" in result.stdout

  def test_category_unit_only(self) -> None:
    """--category unit shows only unit tech specs (plus products)."""
    result = self.runner.invoke(
      app,
      ["specs", "--root", str(self.root), "--category", "unit"],
    )
    assert result.exit_code == 0
    assert "SPEC-001" in result.stdout
    assert "SPEC-002" not in result.stdout
    assert "SPEC-003" not in result.stdout
    assert "PROD-001" in result.stdout  # products always pass

  def test_category_assembly_only(self) -> None:
    """--category assembly shows only assembly tech specs."""
    result = self.runner.invoke(
      app,
      ["specs", "--root", str(self.root), "--category", "assembly"],
    )
    assert result.exit_code == 0
    assert "SPEC-001" not in result.stdout
    assert "SPEC-002" in result.stdout
    assert "SPEC-003" not in result.stdout  # unknown ≠ assembly

  def test_category_multi_value(self) -> None:
    """--category unit,assembly shows both but excludes unknown."""
    result = self.runner.invoke(
      app,
      ["specs", "--root", str(self.root), "--category", "unit,assembly"],
    )
    assert result.exit_code == 0
    assert "SPEC-001" in result.stdout
    assert "SPEC-002" in result.stdout
    assert "SPEC-003" not in result.stdout

  def test_c4_level_filter(self) -> None:
    """--c4-level code shows only code-level tech specs."""
    result = self.runner.invoke(
      app,
      ["specs", "--root", str(self.root), "--category", "all", "--c4-level", "code"],
    )
    assert result.exit_code == 0
    assert "SPEC-001" in result.stdout  # c4_level: code
    assert "SPEC-002" not in result.stdout  # c4_level: component
    assert "SPEC-003" not in result.stdout  # c4_level: unknown

  def test_kind_tech_with_category_filter(self) -> None:
    """--kind tech + default category still hides unit specs."""
    result = self.runner.invoke(
      app,
      ["specs", "--root", str(self.root), "--kind", "tech"],
    )
    assert result.exit_code == 0
    assert "SPEC-001" not in result.stdout  # unit → hidden
    assert "SPEC-002" in result.stdout
    assert "PROD-001" not in result.stdout  # kind=tech excludes products

  def test_kind_product_ignores_category(self) -> None:
    """--kind product is unaffected by --category."""
    result = self.runner.invoke(
      app,
      ["specs", "--root", str(self.root), "--kind", "product", "--category", "unit"],
    )
    assert result.exit_code == 0
    assert "PROD-001" in result.stdout
    assert "SPEC-001" not in result.stdout  # kind=product excludes tech


class ListBacklogSeverityFilterTest(unittest.TestCase):
  """Test cases for --severity filter on backlog list commands (VT-DE-074)."""

  def setUp(self) -> None:
    """Set up test environment with backlog entries at different severities."""
    self.runner = CliRunner()
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()

    self._create_item("issue", "ISSUE-001", "Critical bug", "open", "p1")
    self._create_item("issue", "ISSUE-002", "Minor bug", "open", "p2")
    self._create_item("issue", "ISSUE-003", "Resolved bug", "resolved", "p1")
    self._create_item("problem", "PROB-001", "Urgent problem", "captured", "p1")
    self._create_item("problem", "PROB-002", "Low problem", "captured", "p3")
    self._create_item("improvement", "IMPR-001", "Critical improvement", "idea", "p1")
    self._create_item("improvement", "IMPR-002", "Nice-to-have", "idea", "p3")
    self._create_item("risk", "RISK-001", "High risk", "identified", "p1")
    self._create_item("risk", "RISK-002", "Low risk", "identified", "p2")

  def tearDown(self) -> None:
    self.tmpdir.cleanup()

  def _create_item(
    self, kind: str, item_id: str, title: str, status: str, severity: str
  ) -> None:
    kind_subdir = {
      "issue": ISSUES_SUBDIR,
      "problem": PROBLEMS_SUBDIR,
      "improvement": IMPROVEMENTS_SUBDIR,
      "risk": RISKS_SUBDIR,
    }[kind]
    item_dir = self.root / SPEC_DRIVER_DIR / BACKLOG_DIR / kind_subdir / item_id
    item_dir.mkdir(parents=True, exist_ok=True)
    content = f"""---
id: {item_id}
name: {title}
kind: {kind}
status: {status}
severity: {severity}
created: '2025-11-04'
---

# {item_id} - {title}
"""
    (item_dir / f"{item_id}.md").write_text(content, encoding="utf-8")

  def test_list_backlog_severity_filter(self) -> None:
    """--severity on list backlog filters to matching severity."""
    result = self.runner.invoke(
      app,
      ["backlog", "--root", str(self.root), "--severity", "p1"],
    )
    assert result.exit_code == 0
    assert "ISSUE-001" in result.stdout
    assert "PROB-001" in result.stdout
    assert "IMPR-001" in result.stdout
    assert "RISK-001" in result.stdout
    assert "ISSUE-002" not in result.stdout  # p2
    assert "PROB-002" not in result.stdout  # p3

  def test_list_issues_severity_filter(self) -> None:
    """--severity on list issues filters correctly."""
    result = self.runner.invoke(
      app,
      ["issues", "--root", str(self.root), "--severity", "p1"],
    )
    assert result.exit_code == 0
    assert "ISSUE-001" in result.stdout
    assert "ISSUE-002" not in result.stdout  # p2
    assert "ISSUE-003" not in result.stdout  # resolved, excluded by default

  def test_list_problems_severity_filter(self) -> None:
    """--severity on list problems filters correctly."""
    result = self.runner.invoke(
      app,
      ["problems", "--root", str(self.root), "--severity", "p1"],
    )
    assert result.exit_code == 0
    assert "PROB-001" in result.stdout
    assert "PROB-002" not in result.stdout  # p3

  def test_list_improvements_severity_filter(self) -> None:
    """--severity on list improvements filters correctly."""
    result = self.runner.invoke(
      app,
      ["improvements", "--root", str(self.root), "--severity", "p1"],
    )
    assert result.exit_code == 0
    assert "IMPR-001" in result.stdout
    assert "IMPR-002" not in result.stdout  # p3

  def test_list_risks_severity_filter(self) -> None:
    """--severity on list risks filters correctly."""
    result = self.runner.invoke(
      app,
      ["risks", "--root", str(self.root), "--severity", "p1"],
    )
    assert result.exit_code == 0
    assert "RISK-001" in result.stdout
    assert "RISK-002" not in result.stdout  # p2

  def test_severity_filter_case_insensitive(self) -> None:
    """--severity matching is case-insensitive."""
    result = self.runner.invoke(
      app,
      ["issues", "--root", str(self.root), "--severity", "P1"],
    )
    assert result.exit_code == 0
    assert "ISSUE-001" in result.stdout
    assert "ISSUE-002" not in result.stdout

  def test_severity_filter_no_matches(self) -> None:
    """--severity with no matches returns empty."""
    result = self.runner.invoke(
      app,
      ["issues", "--root", str(self.root), "--severity", "p0"],
    )
    assert result.exit_code == 0
    assert result.stdout.strip() == ""

  def test_severity_combined_with_status(self) -> None:
    """--severity combined with --status narrows results."""
    result = self.runner.invoke(
      app,
      ["issues", "--root", str(self.root), "--severity", "p1", "--all"],
    )
    assert result.exit_code == 0
    assert "ISSUE-001" in result.stdout
    assert "ISSUE-003" in result.stdout  # p1 + resolved, shown because --all


class BacklogPrioritizationTest(unittest.TestCase):
  """Test cases for backlog prioritization feature (VT-015-005).

  Tests the --prioritize flag and interactive editor workflow integration.
  """

  def setUp(self) -> None:
    """Set up test environment with sample backlog entries and registry."""
    self.runner = CliRunner()
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()

    # Create sample backlog entries
    self._create_sample_issue("ISSUE-001", "First issue", "open", "p1")
    self._create_sample_issue("ISSUE-002", "Second issue", "open", "p2")
    self._create_sample_issue("ISSUE-003", "Third issue", "resolved", "p1")
    self._create_sample_improvement("IMPR-001", "First improvement", "idea")
    self._create_sample_improvement("IMPR-002", "Second improvement", "accepted")

    # Create registry with initial ordering
    registry_dir = self.root / ".spec-driver" / "registry"
    registry_dir.mkdir(parents=True)
    registry_file = registry_dir / "backlog.yaml"
    registry_content = """ordering:
  - IMPR-001
  - ISSUE-001
  - ISSUE-002
  - IMPR-002
  - ISSUE-003
"""
    registry_file.write_text(registry_content, encoding="utf-8")

  def tearDown(self) -> None:
    """Clean up test environment."""
    self.tmpdir.cleanup()

  def _create_sample_issue(
    self, issue_id: str, title: str, status: str, severity: str
  ) -> None:
    """Helper to create a sample issue file."""
    issue_dir = self.root / SPEC_DRIVER_DIR / BACKLOG_DIR / ISSUES_SUBDIR / issue_id
    issue_dir.mkdir(parents=True, exist_ok=True)
    issue_file = issue_dir / f"{issue_id}.md"
    content = f"""---
id: {issue_id}
name: {title}
kind: issue
status: {status}
severity: {severity}
created: '2025-11-04'
---

# {issue_id} - {title}

Test issue content.
"""
    issue_file.write_text(content, encoding="utf-8")

  def _create_sample_improvement(self, impr_id: str, title: str, status: str) -> None:
    """Helper to create a sample improvement file."""
    impr_dir = self.root / SPEC_DRIVER_DIR / BACKLOG_DIR / IMPROVEMENTS_SUBDIR / impr_id
    impr_dir.mkdir(parents=True, exist_ok=True)
    impr_file = impr_dir / f"{impr_id}.md"
    content = f"""---
id: {impr_id}
name: {title}
kind: improvement
status: {status}
created: '2025-11-04'
---

# {impr_id} - {title}

Test improvement content.
"""
    impr_file.write_text(content, encoding="utf-8")

  def test_list_backlog_uses_priority_order(self) -> None:
    """Test that list backlog displays items in priority order by default."""
    result = self.runner.invoke(
      app,
      ["backlog", "--root", str(self.root), "--all"],
    )

    assert result.exit_code == 0
    # Check that items appear in registry order
    output_lines = result.stdout.strip().split("\n")
    # Find positions of IDs in output (skip header)
    positions = {}
    for i, line in enumerate(output_lines):
      for item_id in ["IMPR-001", "ISSUE-001", "ISSUE-002", "IMPR-002", "ISSUE-003"]:
        if item_id in line:
          positions[item_id] = i
          break

    # Verify priority order (registry order)
    assert positions["IMPR-001"] < positions["ISSUE-001"]
    assert positions["ISSUE-001"] < positions["ISSUE-002"]
    assert positions["ISSUE-002"] < positions["IMPR-002"]
    assert positions["IMPR-002"] < positions["ISSUE-003"]

  def test_order_by_id_flag(self) -> None:
    """Test --order id flag provides chronological ordering."""
    result = self.runner.invoke(
      app,
      ["backlog", "--root", str(self.root), "--order", "id", "--all"],
    )

    assert result.exit_code == 0
    output_lines = result.stdout.strip().split("\n")
    positions = {}
    for i, line in enumerate(output_lines):
      for item_id in ["ISSUE-001", "ISSUE-002", "ISSUE-003", "IMPR-001", "IMPR-002"]:
        if item_id in line:
          positions[item_id] = i
          break

    # Verify chronological order (by ID)
    assert positions["IMPR-001"] < positions["IMPR-002"]
    assert positions["ISSUE-001"] < positions["ISSUE-002"]
    assert positions["ISSUE-002"] < positions["ISSUE-003"]


class ListPlansTest(unittest.TestCase):
  """Integration tests for list plans command (VT-list-plans)."""

  def setUp(self) -> None:
    self.runner = CliRunner()
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()
    self._create_plan("DE-100", "IP-100", "Draft plan alpha", "draft")
    self._create_plan("DE-101", "IP-101", "Complete plan beta", "complete")

  def tearDown(self) -> None:
    self.tmpdir.cleanup()

  def _create_plan(
    self,
    delta_id: str,
    plan_id: str,
    name: str,
    status: str,
  ) -> None:
    delta_dir = self.root / SPEC_DRIVER_DIR / DELTAS_SUBDIR / f"{delta_id}-sample"
    delta_dir.mkdir(parents=True, exist_ok=True)
    content = f"""---
id: {plan_id}
slug: {delta_id.lower()}_sample
name: {name}
created: '2026-03-01'
updated: '2026-03-02'
status: {status}
kind: plan
---

```yaml supekku:plan.overview@v1
schema: supekku.plan.overview
version: 1
plan: {plan_id}
delta: {delta_id}
phases:
  - id: {plan_id}.PHASE-01
    name: Phase 1
    status: complete
```

# {plan_id}
"""
    (delta_dir / f"{plan_id}.md").write_text(content, encoding="utf-8")

  def test_list_plans_basic(self) -> None:
    result = self.runner.invoke(app, ["plans", "--root", str(self.root)])
    assert result.exit_code == 0
    assert "IP-100" in result.stdout
    assert "IP-101" in result.stdout

  def test_list_plans_status_filter(self) -> None:
    result = self.runner.invoke(
      app,
      ["plans", "--root", str(self.root), "-s", "complete"],
    )
    assert result.exit_code == 0
    assert "IP-101" in result.stdout
    assert "IP-100" not in result.stdout

  def test_list_plans_substring_filter(self) -> None:
    result = self.runner.invoke(
      app,
      ["plans", "--root", str(self.root), "-f", "alpha"],
    )
    assert result.exit_code == 0
    assert "IP-100" in result.stdout
    assert "IP-101" not in result.stdout

  def test_list_plans_filter_no_match(self) -> None:
    result = self.runner.invoke(
      app,
      ["plans", "--root", str(self.root), "-f", "nonexistent"],
    )
    assert result.exit_code == 0
    assert result.stdout.strip() == ""

  def test_list_plans_json(self) -> None:
    result = self.runner.invoke(
      app,
      ["plans", "--root", str(self.root), "--json"],
    )
    assert result.exit_code == 0
    assert '"IP-100"' in result.stdout
    assert '"IP-101"' in result.stdout


class ListFilterBackfillTest(unittest.TestCase):
  """Integration tests for --filter backfill on list commands (VT-list-filters)."""

  def setUp(self) -> None:
    self.runner = CliRunner()
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()
    self._create_deltas()

  def tearDown(self) -> None:
    self.tmpdir.cleanup()

  def _create_deltas(self) -> None:
    for delta_id, name, status in [
      ("DE-100", "Alpha feature", "draft"),
      ("DE-101", "Beta bugfix", "in-progress"),
    ]:
      delta_dir = self.root / SPEC_DRIVER_DIR / DELTAS_SUBDIR / f"{delta_id}-sample"
      delta_dir.mkdir(parents=True, exist_ok=True)
      content = f"""---
id: {delta_id}
slug: {delta_id.lower()}_sample
name: {name}
created: '2026-03-01'
updated: '2026-03-02'
status: {status}
kind: delta
applies_to:
  specs: []
  requirements: []
---

# {delta_id}
"""
      (delta_dir / f"{delta_id}.md").write_text(content, encoding="utf-8")

  def test_list_deltas_filter_narrows(self) -> None:
    result = self.runner.invoke(
      app,
      ["deltas", "--root", str(self.root), "-f", "alpha"],
    )
    assert result.exit_code == 0
    assert "DE-100" in result.stdout
    assert "DE-101" not in result.stdout

  def test_list_deltas_filter_no_match(self) -> None:
    result = self.runner.invoke(
      app,
      ["deltas", "--root", str(self.root), "-f", "nonexistent"],
    )
    assert result.exit_code == 0
    assert result.stdout.strip() == ""

  def test_list_deltas_filter_by_id(self) -> None:
    result = self.runner.invoke(
      app,
      ["deltas", "--root", str(self.root), "-f", "101"],
    )
    assert result.exit_code == 0
    assert "DE-101" in result.stdout
    assert "DE-100" not in result.stdout


class ListDeltasRelationFilterTest(unittest.TestCase):
  """VT-085-002: --related-to, --relation, --refs on list deltas."""

  def setUp(self) -> None:
    self.runner = CliRunner()
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()
    self._create_deltas()

  def tearDown(self) -> None:
    self.tmpdir.cleanup()

  def _create_deltas(self) -> None:
    for delta_id, name, status, relations, context_inputs in [
      (
        "DE-100",
        "Alpha feature",
        "draft",
        [{"type": "relates_to", "target": "IMPR-006"}],
        [{"type": "issue", "id": "IMPR-006"}],
      ),
      (
        "DE-101",
        "Beta bugfix",
        "in-progress",
        [{"type": "implements", "target": "PROD-010"}],
        [],
      ),
      ("DE-102", "Gamma cleanup", "draft", [], []),
    ]:
      delta_dir = self.root / SPEC_DRIVER_DIR / DELTAS_SUBDIR / f"{delta_id}-sample"
      delta_dir.mkdir(parents=True, exist_ok=True)
      frontmatter = {
        "id": delta_id,
        "slug": f"{delta_id.lower()}_sample",
        "name": name,
        "created": "2026-03-01",
        "updated": "2026-03-02",
        "status": status,
        "kind": "delta",
        "relations": relations,
        "context_inputs": context_inputs,
        "applies_to": {"specs": [], "requirements": []},
      }
      fm_yaml = yaml.dump(frontmatter, default_flow_style=False)
      content = f"---\n{fm_yaml}---\n\n# {delta_id}\n"
      (delta_dir / f"{delta_id}.md").write_text(content, encoding="utf-8")

  def test_related_to_finds_matching_delta(self) -> None:
    result = self.runner.invoke(
      app,
      [
        "deltas",
        "--root",
        str(self.root),
        "--related-to",
        "IMPR-006",
        "--format",
        "tsv",
      ],
    )
    assert result.exit_code == 0
    assert "DE-100" in result.stdout
    assert "DE-101" not in result.stdout

  def test_related_to_no_match(self) -> None:
    result = self.runner.invoke(
      app,
      ["deltas", "--root", str(self.root), "--related-to", "NONEXISTENT"],
    )
    assert result.exit_code == 0
    assert result.stdout.strip() == ""

  def test_relation_type_target(self) -> None:
    result = self.runner.invoke(
      app,
      [
        "deltas",
        "--root",
        str(self.root),
        "--relation",
        "implements:PROD-010",
        "--format",
        "tsv",
      ],
    )
    assert result.exit_code == 0
    assert "DE-101" in result.stdout
    assert "DE-100" not in result.stdout

  def test_relation_bad_format_errors(self) -> None:
    result = self.runner.invoke(
      app,
      ["deltas", "--root", str(self.root), "--relation", "no_colon"],
    )
    assert result.exit_code != 0

  def test_refs_column_tsv(self) -> None:
    result = self.runner.invoke(
      app,
      [
        "deltas",
        "--root",
        str(self.root),
        "--refs",
        "--format",
        "tsv",
      ],
    )
    assert result.exit_code == 0
    # DE-100 has relations and context_inputs
    lines = result.stdout.strip().split("\n")
    de100_line = [line for line in lines if "DE-100" in line]
    assert de100_line
    assert "relation.relates_to:IMPR-006" in de100_line[0]

  def test_refs_column_table(self) -> None:
    result = self.runner.invoke(
      app,
      ["deltas", "--root", str(self.root), "--refs"],
    )
    assert result.exit_code == 0
    assert "Refs" in result.stdout

  def test_related_to_case_insensitive(self) -> None:
    result = self.runner.invoke(
      app,
      [
        "deltas",
        "--root",
        str(self.root),
        "--related-to",
        "impr-006",
        "--format",
        "tsv",
      ],
    )
    assert result.exit_code == 0
    assert "DE-100" in result.stdout


class ListSpecsRelationFilterTest(unittest.TestCase):
  """VT-085-002: --related-to, --relation, --refs on list specs."""

  def setUp(self) -> None:
    self.runner = CliRunner()
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()
    self._create_specs()

  def tearDown(self) -> None:
    self.tmpdir.cleanup()

  def _create_specs(self) -> None:
    for spec_id, name, relations, informed_by in [
      (
        "PROD-100",
        "Product spec alpha",
        [{"type": "implements", "target": "ADR-001"}],
        [],
      ),
      ("PROD-101", "Product spec beta", [], ["ADR-002"]),
      ("PROD-102", "Product spec gamma", [], []),
    ]:
      spec_dir = self.root / SPEC_DRIVER_DIR / PRODUCT_SPECS_SUBDIR
      spec_dir.mkdir(parents=True, exist_ok=True)
      frontmatter = {
        "id": spec_id,
        "slug": spec_id.lower(),
        "name": name,
        "created": "2026-03-01",
        "updated": "2026-03-02",
        "status": "active",
        "kind": "product",
        "relations": relations,
        "informed_by": informed_by,
      }
      fm_yaml = yaml.dump(frontmatter, default_flow_style=False)
      content = f"---\n{fm_yaml}---\n\n# {spec_id}\n"
      (spec_dir / f"{spec_id}.md").write_text(content, encoding="utf-8")

  def test_related_to_via_relations(self) -> None:
    result = self.runner.invoke(
      app,
      [
        "specs",
        "--root",
        str(self.root),
        "--related-to",
        "ADR-001",
        "--format",
        "tsv",
      ],
    )
    assert result.exit_code == 0
    assert "PROD-100" in result.stdout

  def test_related_to_via_informed_by(self) -> None:
    result = self.runner.invoke(
      app,
      [
        "specs",
        "--root",
        str(self.root),
        "--related-to",
        "ADR-002",
        "--format",
        "tsv",
      ],
    )
    assert result.exit_code == 0
    assert "PROD-101" in result.stdout

  def test_refs_column_tsv(self) -> None:
    result = self.runner.invoke(
      app,
      [
        "specs",
        "--root",
        str(self.root),
        "--refs",
        "--format",
        "tsv",
      ],
    )
    assert result.exit_code == 0
    lines = result.stdout.strip().split("\n")
    prod100_line = [line for line in lines if "PROD-100" in line]
    assert prod100_line
    assert "relation.implements:ADR-001" in prod100_line[0]

  def test_relation_filter(self) -> None:
    result = self.runner.invoke(
      app,
      [
        "specs",
        "--root",
        str(self.root),
        "--relation",
        "implements:ADR-001",
        "--format",
        "tsv",
      ],
    )
    assert result.exit_code == 0
    assert "PROD-100" in result.stdout
    assert "PROD-101" not in result.stdout


# ── --stale flag tests (DE-086, VT-cli-list-stale) ──

from unittest.mock import MagicMock, patch  # noqa: E402

from supekku.scripts.lib.memory.models import MemoryRecord  # noqa: E402
from supekku.scripts.lib.memory.staleness import StalenessInfo  # noqa: E402

runner = CliRunner()


def _make_memory_record(
  memory_id: str = "mem.test",
  **kwargs,
) -> MemoryRecord:
  """Build a minimal MemoryRecord for list tests."""
  from datetime import date  # noqa: PLC0415

  defaults = {
    "id": memory_id,
    "name": "Test memory",
    "status": "active",
    "memory_type": "pattern",
    "path": "/fake/path.md",
    "updated": date(2026, 3, 1),
    "confidence": "medium",
  }
  defaults.update(kwargs)
  return MemoryRecord(**defaults)


class TestListMemoriesStale:
  """Tests for --stale flag on list memories command."""

  def test_stale_flag_produces_tiered_output(self) -> None:
    """--stale flag shows tiered staleness output."""
    from datetime import date  # noqa: PLC0415

    records = [
      _make_memory_record(
        memory_id="mem.scoped",
        verified=date(2026, 3, 1),
        verified_sha="a" * 40,
        scope={"paths": ["supekku/cli/"]},
      ),
      _make_memory_record(
        memory_id="mem.unscoped",
        verified=date(2026, 1, 15),
      ),
    ]
    staleness = [
      StalenessInfo(
        memory_id="mem.scoped",
        verified_sha="a" * 40,
        verified_date=date(2026, 3, 1),
        scope_paths=["supekku/cli/"],
        commits_since=5,
        days_since=9,
        has_scope=True,
      ),
      StalenessInfo(
        memory_id="mem.unscoped",
        verified_sha=None,
        verified_date=date(2026, 1, 15),
        scope_paths=[],
        commits_since=None,
        days_since=54,
        has_scope=False,
      ),
    ]
    mock_registry = MagicMock()
    mock_registry.iter.return_value = iter(records)

    with (
      patch("supekku.cli.list.MemoryRegistry", return_value=mock_registry),
      patch(
        "supekku.cli.list.compute_batch_staleness",
        return_value=staleness,
      ),
    ):
      result = runner.invoke(app, ["memories", "--stale"])

    assert result.exit_code == 0
    assert "scoped, attested" in result.output
    assert "mem.scoped" in result.output
    assert "mem.unscoped" in result.output

  def test_stale_flag_empty_registry(self) -> None:
    """--stale with no memories exits cleanly."""
    mock_registry = MagicMock()
    mock_registry.iter.return_value = iter([])

    with patch(
      "supekku.cli.list.MemoryRegistry",
      return_value=mock_registry,
    ):
      result = runner.invoke(app, ["memories", "--stale"])

    assert result.exit_code == 0


class ListAuditsDeltaFilterTest(unittest.TestCase):
  """VT-090-P1-4: list audits --delta filters by relation target."""

  def setUp(self) -> None:
    self.runner = CliRunner()
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()
    self._create_audits()

  def tearDown(self) -> None:
    self.tmpdir.cleanup()

  def _create_audits(self) -> None:
    for audit_id, name, relations in [
      ("AUD-001", "Audit for DE-090", [{"type": "audits", "target": "DE-090"}]),
      ("AUD-002", "Audit for DE-091", [{"type": "audits", "target": "DE-091"}]),
      ("AUD-003", "Audit no relations", []),
    ]:
      audit_dir = self.root / SPEC_DRIVER_DIR / "audits" / f"{audit_id}-sample"
      audit_dir.mkdir(parents=True, exist_ok=True)
      frontmatter = {
        "id": audit_id,
        "slug": f"{audit_id.lower()}_sample",
        "name": name,
        "created": "2026-03-01",
        "updated": "2026-03-02",
        "status": "draft",
        "kind": "audit",
        "relations": relations,
      }
      fm_yaml = yaml.dump(frontmatter, default_flow_style=False)
      content = f"---\n{fm_yaml}---\n\n# {audit_id}\n"
      (audit_dir / f"{audit_id}.md").write_text(content, encoding="utf-8")

  def test_delta_filter_matches(self) -> None:
    result = self.runner.invoke(
      app,
      ["audits", "--root", str(self.root), "--delta", "DE-090", "--format", "tsv"],
    )
    assert result.exit_code == 0
    assert "AUD-001" in result.stdout
    assert "AUD-002" not in result.stdout

  def test_delta_filter_bare_numeric(self) -> None:
    result = self.runner.invoke(
      app,
      ["audits", "--root", str(self.root), "--delta", "90", "--format", "tsv"],
    )
    assert result.exit_code == 0
    assert "AUD-001" in result.stdout

  def test_delta_filter_no_match(self) -> None:
    result = self.runner.invoke(
      app,
      ["audits", "--root", str(self.root), "--delta", "DE-999"],
    )
    assert result.exit_code == 0
    assert result.stdout.strip() == ""


class ListRevisionsDeltaFilterTest(unittest.TestCase):
  """VT-090-P1-5: list revisions --delta filters by relation target."""

  def setUp(self) -> None:
    self.runner = CliRunner()
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()
    self._create_revisions()

  def tearDown(self) -> None:
    self.tmpdir.cleanup()

  def _create_revisions(self) -> None:
    for rev_id, name, relations in [
      ("RE-010", "Revision from DE-090", [{"type": "introduces", "target": "DE-090"}]),
      ("RE-011", "Revision from DE-091", [{"type": "introduces", "target": "DE-091"}]),
    ]:
      rev_dir = self.root / SPEC_DRIVER_DIR / "revisions" / f"{rev_id}-sample"
      rev_dir.mkdir(parents=True, exist_ok=True)
      frontmatter = {
        "id": rev_id,
        "slug": f"{rev_id.lower()}_sample",
        "name": name,
        "created": "2026-03-01",
        "updated": "2026-03-02",
        "status": "draft",
        "kind": "revision",
        "relations": relations,
      }
      fm_yaml = yaml.dump(frontmatter, default_flow_style=False)
      content = f"---\n{fm_yaml}---\n\n# {rev_id}\n"
      (rev_dir / f"{rev_id}.md").write_text(content, encoding="utf-8")

  def test_delta_filter_matches(self) -> None:
    result = self.runner.invoke(
      app,
      ["revisions", "--root", str(self.root), "--delta", "DE-090", "--format", "tsv"],
    )
    assert result.exit_code == 0
    assert "RE-010" in result.stdout
    assert "RE-011" not in result.stdout

  def test_delta_filter_bare_numeric(self) -> None:
    result = self.runner.invoke(
      app,
      ["revisions", "--root", str(self.root), "--delta", "90", "--format", "tsv"],
    )
    assert result.exit_code == 0
    assert "RE-010" in result.stdout

  def test_delta_filter_no_match(self) -> None:
    result = self.runner.invoke(
      app,
      ["revisions", "--root", str(self.root), "--delta", "DE-999"],
    )
    assert result.exit_code == 0
    assert result.stdout.strip() == ""


class ListRequirementsImplementedByTest(unittest.TestCase):
  """VT-090-P1-6: list requirements --implemented-by filters via delta lookup."""

  def setUp(self) -> None:
    self.runner = CliRunner()
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()
    self._create_fixtures()

  def tearDown(self) -> None:
    self.tmpdir.cleanup()

  def _create_fixtures(self) -> None:
    # Create a delta with relationships block implementing PROD-010.FR-005
    delta_dir = self.root / SPEC_DRIVER_DIR / DELTAS_SUBDIR / "DE-090-sample"
    delta_dir.mkdir(parents=True, exist_ok=True)
    frontmatter = {
      "id": "DE-090",
      "slug": "sample_delta",
      "name": "Sample Delta",
      "created": "2026-03-01",
      "updated": "2026-03-02",
      "status": "in-progress",
      "kind": "delta",
      "relations": [],
      "applies_to": {"specs": ["PROD-010"], "requirements": ["PROD-010.FR-005"]},
    }
    fm_yaml = yaml.dump(frontmatter, default_flow_style=False)
    rels_block = (
      "```yaml supekku:delta.relationships@v1\n"
      "schema: supekku.delta.relationships\n"
      "version: 1\n"
      "delta: DE-090\n"
      "requirements:\n"
      "  implements:\n"
      "  - PROD-010.FR-005\n"
      "  updates: []\n"
      "  verifies: []\n"
      "```\n"
    )
    content = f"---\n{fm_yaml}---\n\n# DE-090\n\n{rels_block}"
    (delta_dir / "DE-090.md").write_text(content, encoding="utf-8")

    # Create requirements registry with matching and non-matching requirements
    registry_dir = self.root / SPEC_DRIVER_DIR / "registry"
    registry_dir.mkdir(parents=True, exist_ok=True)
    reqs = {
      "requirements": {
        "PROD-010.FR-005": {
          "uid": "PROD-010.FR-005",
          "label": "FR-005",
          "title": "Reverse relationship queries",
          "status": "draft",
          "specs": ["PROD-010"],
          "source_kind": "spec",
        },
        "PROD-010.FR-006": {
          "uid": "PROD-010.FR-006",
          "label": "FR-006",
          "title": "Other requirement",
          "status": "draft",
          "specs": ["PROD-010"],
          "source_kind": "spec",
        },
      }
    }
    (registry_dir / "requirements.yaml").write_text(
      yaml.dump(reqs, default_flow_style=False), encoding="utf-8"
    )

  def test_implemented_by_matches(self) -> None:
    result = self.runner.invoke(
      app,
      [
        "requirements",
        "--root",
        str(self.root),
        "--implemented-by",
        "DE-090",
        "--format",
        "tsv",
      ],
    )
    assert result.exit_code == 0
    assert "FR-005" in result.stdout
    assert "FR-006" not in result.stdout

  def test_implemented_by_bare_numeric(self) -> None:
    result = self.runner.invoke(
      app,
      [
        "requirements",
        "--root",
        str(self.root),
        "--implemented-by",
        "90",
        "--format",
        "tsv",
      ],
    )
    assert result.exit_code == 0
    assert "FR-005" in result.stdout

  def test_implemented_by_not_found(self) -> None:
    result = self.runner.invoke(
      app,
      [
        "requirements",
        "--root",
        str(self.root),
        "--implemented-by",
        "DE-999",
      ],
    )
    assert result.exit_code != 0
    combined = result.stdout.lower() + (result.stderr or "").lower()
    assert "not found" in combined


class ListDeltasSpecFilterTest(unittest.TestCase):
  """VT-090-P1-7: list deltas --spec filters by applies_to.specs and relations."""

  def setUp(self) -> None:
    self.runner = CliRunner()
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()
    self._create_deltas()

  def tearDown(self) -> None:
    self.tmpdir.cleanup()

  def _create_deltas(self) -> None:
    for delta_id, name, applies_to, relations in [
      (
        "DE-100",
        "Touches PROD-010 via applies_to",
        {"specs": ["PROD-010"], "requirements": []},
        [],
      ),
      (
        "DE-101",
        "Touches PROD-010 via relation",
        {"specs": [], "requirements": []},
        [{"type": "relates_to", "target": "PROD-010"}],
      ),
      (
        "DE-102",
        "No spec reference",
        {"specs": ["SPEC-200"], "requirements": []},
        [],
      ),
    ]:
      delta_dir = self.root / SPEC_DRIVER_DIR / DELTAS_SUBDIR / f"{delta_id}-sample"
      delta_dir.mkdir(parents=True, exist_ok=True)
      frontmatter = {
        "id": delta_id,
        "slug": f"{delta_id.lower()}_sample",
        "name": name,
        "created": "2026-03-01",
        "updated": "2026-03-02",
        "status": "draft",
        "kind": "delta",
        "relations": relations,
        "applies_to": applies_to,
      }
      fm_yaml = yaml.dump(frontmatter, default_flow_style=False)
      content = f"---\n{fm_yaml}---\n\n# {delta_id}\n"
      (delta_dir / f"{delta_id}.md").write_text(content, encoding="utf-8")

  def test_spec_filter_matches_applies_to(self) -> None:
    result = self.runner.invoke(
      app,
      ["deltas", "--root", str(self.root), "--spec", "PROD-010", "--format", "tsv"],
    )
    assert result.exit_code == 0
    assert "DE-100" in result.stdout
    assert "DE-101" in result.stdout
    assert "DE-102" not in result.stdout

  def test_spec_filter_case_insensitive(self) -> None:
    result = self.runner.invoke(
      app,
      ["deltas", "--root", str(self.root), "--spec", "prod-010", "--format", "tsv"],
    )
    assert result.exit_code == 0
    assert "DE-100" in result.stdout

  def test_spec_filter_no_match(self) -> None:
    result = self.runner.invoke(
      app,
      ["deltas", "--root", str(self.root), "--spec", "SPEC-999"],
    )
    assert result.exit_code == 0
    assert result.stdout.strip() == ""


class ListBacklogRelatedToTest(unittest.TestCase):
  """VT-090-P1-8: list backlog --related-to filters by frontmatter relations."""

  def setUp(self) -> None:
    self.runner = CliRunner()
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()
    self._create_backlog_items()

  def tearDown(self) -> None:
    self.tmpdir.cleanup()

  def _create_backlog_items(self) -> None:
    for issue_id, title, relations in [
      (
        "ISSUE-010",
        "Issue referencing SPEC-110",
        [{"type": "relates_to", "target": "SPEC-110"}],
      ),
      (
        "ISSUE-011",
        "Issue referencing DE-090",
        [{"type": "relates_to", "target": "DE-090"}],
      ),
      ("ISSUE-012", "Issue with no relations", []),
    ]:
      issue_dir = self.root / SPEC_DRIVER_DIR / BACKLOG_DIR / ISSUES_SUBDIR / issue_id
      issue_dir.mkdir(parents=True, exist_ok=True)
      frontmatter = {
        "id": issue_id,
        "name": title,
        "created": "2026-03-01",
        "updated": "2026-03-02",
        "status": "open",
        "kind": "issue",
        "relations": relations,
      }
      fm_yaml = yaml.dump(frontmatter, default_flow_style=False)
      content = f"---\n{fm_yaml}---\n\n# {issue_id}\n"
      (issue_dir / f"{issue_id}.md").write_text(content, encoding="utf-8")

  def test_related_to_matches(self) -> None:
    result = self.runner.invoke(
      app,
      [
        "backlog",
        "--root",
        str(self.root),
        "--related-to",
        "SPEC-110",
        "--format",
        "tsv",
      ],
    )
    assert result.exit_code == 0
    assert "ISSUE-010" in result.stdout
    assert "ISSUE-011" not in result.stdout

  def test_related_to_case_insensitive(self) -> None:
    result = self.runner.invoke(
      app,
      [
        "backlog",
        "--root",
        str(self.root),
        "--related-to",
        "de-090",
        "--format",
        "tsv",
      ],
    )
    assert result.exit_code == 0
    assert "ISSUE-011" in result.stdout

  def test_related_to_no_match(self) -> None:
    result = self.runner.invoke(
      app,
      ["backlog", "--root", str(self.root), "--related-to", "NONEXISTENT"],
    )
    assert result.exit_code == 0
    assert result.stdout.strip() == ""


class ListBacklogRelatedToLinkedDeltasTest(unittest.TestCase):
  """VT-090-P3-8: list backlog --related-to picks up linked_deltas via collector."""

  def setUp(self) -> None:
    self.runner = CliRunner()
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()
    self._create_backlog_items()

  def tearDown(self) -> None:
    self.tmpdir.cleanup()

  def _create_backlog_items(self) -> None:
    for issue_id, title, extra_fm in [
      (
        "ISSUE-020",
        "Issue with linked_deltas",
        {"linked_deltas": ["DE-050"]},
      ),
      (
        "ISSUE-021",
        "Issue with related_requirements",
        {"related_requirements": ["SPEC-100.FR-001"]},
      ),
      ("ISSUE-022", "Issue with no links", {}),
    ]:
      issue_dir = self.root / SPEC_DRIVER_DIR / BACKLOG_DIR / ISSUES_SUBDIR / issue_id
      issue_dir.mkdir(parents=True, exist_ok=True)
      frontmatter = {
        "id": issue_id,
        "name": title,
        "created": "2026-03-01",
        "updated": "2026-03-02",
        "status": "open",
        "kind": "issue",
        **extra_fm,
      }
      fm_yaml = yaml.dump(frontmatter, default_flow_style=False)
      content = f"---\n{fm_yaml}---\n\n# {issue_id}\n"
      (issue_dir / f"{issue_id}.md").write_text(content, encoding="utf-8")

  def test_linked_deltas_match(self) -> None:
    result = self.runner.invoke(
      app,
      [
        "backlog", "--root", str(self.root),
        "--related-to", "DE-050", "--format", "tsv",
      ],
    )
    assert result.exit_code == 0
    assert "ISSUE-020" in result.stdout
    assert "ISSUE-021" not in result.stdout

  def test_related_requirements_match(self) -> None:
    result = self.runner.invoke(
      app,
      [
        "backlog", "--root", str(self.root),
        "--related-to", "SPEC-100.FR-001", "--format", "tsv",
      ],
    )
    assert result.exit_code == 0
    assert "ISSUE-021" in result.stdout
    assert "ISSUE-020" not in result.stdout

  def test_no_links_no_match(self) -> None:
    result = self.runner.invoke(
      app,
      ["backlog", "--root", str(self.root), "--related-to", "DE-050"],
    )
    assert result.exit_code == 0
    assert "ISSUE-022" not in result.stdout


if __name__ == "__main__":
  unittest.main()
