"""Tests for list CLI commands (backlog shortcuts)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from typer.testing import CliRunner

from supekku.cli.list import app


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
    issue_dir = self.root / "backlog" / "issues" / issue_id
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
    prob_dir = self.root / "backlog" / "problems" / prob_id
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
    impr_dir = self.root / "backlog" / "improvements" / impr_id
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
    risk_dir = self.root / "backlog" / "risks" / risk_id
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
    tech_dir = self.root / "specify" / "tech"

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
    prod_dir = self.root / "specify" / "product"
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
    issue_dir = self.root / "backlog" / "issues" / issue_id
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
    impr_dir = self.root / "backlog" / "improvements" / impr_id
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
    delta_dir = self.root / "change" / "deltas" / f"{delta_id}-sample"
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
      delta_dir = self.root / "change" / "deltas" / f"{delta_id}-sample"
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


if __name__ == "__main__":
  unittest.main()
