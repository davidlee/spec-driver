"""Tests for show CLI commands."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from typer.testing import CliRunner

from supekku.cli.show import app
from supekku.scripts.lib.core.paths import (
  DECISIONS_SUBDIR,
  DELTAS_SUBDIR,
  SPEC_DRIVER_DIR,
  TECH_SPECS_SUBDIR,
)
from supekku.scripts.lib.core.repo import find_repo_root


class ShowTemplateCommandTest(unittest.TestCase):
  """Test cases for show template CLI command."""

  def setUp(self) -> None:
    """Set up test environment."""
    self.runner = CliRunner()

  def test_show_template_tech(self) -> None:
    """Test showing tech specification template."""
    result = self.runner.invoke(app, ["template", "tech"])

    assert result.exit_code == 0, f"Command failed: {result.stderr}"
    assert "# SPEC-XXX" in result.stdout
    assert "specification name" in result.stdout
    # Tech-specific content
    assert "Scope / Boundaries" in result.stdout
    assert "Systems / Integrations" in result.stdout
    assert "Component MUST" in result.stdout
    # Should NOT have product-specific content
    assert "Problem / Purpose" not in result.stdout
    assert "Personas / Actors" not in result.stdout

  def test_show_template_product(self) -> None:
    """Test showing product specification template."""
    result = self.runner.invoke(app, ["template", "product"])

    assert result.exit_code == 0, f"Command failed: {result.stderr}"
    assert "# PROD-XXX" in result.stdout
    assert "specification name" in result.stdout
    # Product-specific content
    assert "Problem / Purpose" in result.stdout
    assert "Personas / Actors" in result.stdout
    assert "System MUST" in result.stdout
    # Should NOT have tech-specific content
    assert "Scope / Boundaries" not in result.stdout
    assert "Systems / Integrations" not in result.stdout
    assert "Component MUST" not in result.stdout

  def test_show_template_invalid_kind(self) -> None:
    """Test that invalid kind produces error."""
    result = self.runner.invoke(app, ["template", "invalid"])

    assert result.exit_code == 1
    assert "Error: Invalid kind 'invalid'" in result.stderr
    assert "Must be 'tech' or 'product'" in result.stderr

  def test_show_template_json_output_tech(self) -> None:
    """Test JSON output format for tech template."""
    result = self.runner.invoke(app, ["template", "tech", "--json"])

    assert result.exit_code == 0, f"Command failed: {result.stderr}"

    # Parse JSON output
    output = json.loads(result.stdout)
    assert "kind" in output
    assert "template" in output
    assert output["kind"] == "tech"
    assert "# SPEC-XXX" in output["template"]
    assert "Scope / Boundaries" in output["template"]

  def test_show_template_json_output_product(self) -> None:
    """Test JSON output format for product template."""
    result = self.runner.invoke(app, ["template", "product", "--json"])

    assert result.exit_code == 0, f"Command failed: {result.stderr}"

    # Parse JSON output
    output = json.loads(result.stdout)
    assert "kind" in output
    assert "template" in output
    assert output["kind"] == "product"
    assert "# PROD-XXX" in output["template"]
    assert "Problem / Purpose" in output["template"]

  def test_show_template_contains_all_sections(self) -> None:
    """Test that template contains all expected sections."""
    result = self.runner.invoke(app, ["template", "tech"])

    assert result.exit_code == 0
    # All specs should have these sections
    assert "## 1. Intent & Summary" in result.stdout
    assert "## 2. Stakeholders & Journeys" in result.stdout
    assert "## 3. Responsibilities & Requirements" in result.stdout
    assert "## 4. Solution Outline" in result.stdout
    assert "## 5. Behaviour & Scenarios" in result.stdout
    assert "## 6. Quality & Verification" in result.stdout
    assert "## 7. Backlog Hooks & Dependencies" in result.stdout

  def test_show_template_contains_requirements_format(self) -> None:
    """Test that template shows proper requirements format."""
    result = self.runner.invoke(app, ["template", "tech"])

    assert result.exit_code == 0
    assert "### Functional Requirements" in result.stdout
    assert "- **FR-001**:" in result.stdout
    assert "### Non-Functional Requirements" in result.stdout
    assert "- **NF-001**:" in result.stdout

  def test_show_template_has_no_empty_yaml_blocks(self) -> None:
    """Test that YAML block placeholders are empty (not filled)."""
    result = self.runner.invoke(app, ["template", "tech"])

    assert result.exit_code == 0
    # Should not have YAML blocks visible (they're rendered as empty)
    # The template has placeholders for these blocks
    assert result.stdout.count("```yaml") == 0  # No YAML blocks rendered


class ShowDeltaCommandTest(unittest.TestCase):
  """Test cases for show delta CLI command."""

  def setUp(self) -> None:
    """Set up test environment."""
    self.runner = CliRunner()
    self.root = find_repo_root()

  def test_show_delta_text_output(self) -> None:
    """Test showing delta in text format (default)."""
    # Find a delta that exists in the repository
    delta_dirs = list((self.root / SPEC_DRIVER_DIR / DELTAS_SUBDIR).glob("DE-*"))
    if not delta_dirs:
      self.skipTest("No deltas found in repository")

    # Use the first delta
    delta_id = delta_dirs[0].name.split("-")[1].split("-")[0]
    delta_id = f"DE-{delta_id}"

    result = self.runner.invoke(app, ["delta", delta_id])

    assert result.exit_code == 0, f"Command failed: {result.stderr}"
    assert delta_id in result.stdout
    assert "Delta:" in result.stdout or "File:" in result.stdout

  def test_show_delta_json_output(self) -> None:
    """Test showing delta in JSON format."""
    # Find a delta that exists in the repository
    delta_dirs = list((self.root / SPEC_DRIVER_DIR / DELTAS_SUBDIR).glob("DE-*"))
    if not delta_dirs:
      self.skipTest("No deltas found in repository")

    # Use the first delta
    delta_id = delta_dirs[0].name.split("-")[1].split("-")[0]
    delta_id = f"DE-{delta_id}"

    result = self.runner.invoke(app, ["delta", delta_id, "--json"])

    assert result.exit_code == 0, f"Command failed: {result.stderr}"

    # Parse JSON output
    output = json.loads(result.stdout)

    # Verify required fields
    assert "id" in output
    assert output["id"] == delta_id
    assert "kind" in output
    assert "status" in output
    assert "name" in output
    assert "slug" in output
    assert "path" in output

    # Verify path is relative
    assert not Path(output["path"]).is_absolute()
    assert output["path"].startswith(".spec-driver/deltas/")

  def test_show_delta_json_includes_plan_paths(self) -> None:
    """Test that JSON output includes plan and phase file paths."""
    # Find DE-005 which should have a plan
    delta_id = "DE-005"
    delta_dir = (
      self.root / SPEC_DRIVER_DIR / DELTAS_SUBDIR / "DE-005-implement-spec-backfill"
    )

    if not delta_dir.exists():
      self.skipTest("DE-005 not found in repository")

    result = self.runner.invoke(app, ["delta", delta_id, "--json"])

    assert result.exit_code == 0, f"Command failed: {result.stderr}"

    # Parse JSON output
    output = json.loads(result.stdout)

    # Verify plan structure
    if "plan" in output:
      plan = output["plan"]
      assert "id" in plan
      assert "path" in plan
      assert "phases" in plan

      # Verify plan path is relative
      assert not Path(plan["path"]).is_absolute()

      # Verify phases have paths
      for phase in plan["phases"]:
        if "path" in phase:
          # Phase path should be relative
          assert not Path(phase["path"]).is_absolute()
          assert "phases/" in phase["path"]

  def test_show_delta_json_includes_applies_to(self) -> None:
    """Test that JSON output includes applies_to with specs and requirements."""
    # Find a delta with applies_to
    delta_id = "DE-005"
    delta_dir = (
      self.root / SPEC_DRIVER_DIR / DELTAS_SUBDIR / "DE-005-implement-spec-backfill"
    )

    if not delta_dir.exists():
      self.skipTest("DE-005 not found in repository")

    result = self.runner.invoke(app, ["delta", delta_id, "--json"])

    assert result.exit_code == 0, f"Command failed: {result.stderr}"

    # Parse JSON output
    output = json.loads(result.stdout)

    # Check for applies_to structure
    if "applies_to" in output:
      applies_to = output["applies_to"]
      # Should have specs and/or requirements
      assert isinstance(applies_to, dict)

  def test_show_delta_not_found(self) -> None:
    """Test error when delta ID does not exist."""
    result = self.runner.invoke(app, ["delta", "DE-999"])

    assert result.exit_code == 1
    assert "Error: Delta not found: DE-999" in result.stderr

  def test_show_delta_json_includes_other_files(self) -> None:
    """Test that JSON output includes other files in delta bundle."""
    # DE-005 has additional files like notes.md, design docs
    delta_id = "DE-005"
    delta_dir = (
      self.root / SPEC_DRIVER_DIR / DELTAS_SUBDIR / "DE-005-implement-spec-backfill"
    )

    if not delta_dir.exists():
      self.skipTest("DE-005 not found in repository")

    result = self.runner.invoke(app, ["delta", delta_id, "--json"])

    assert result.exit_code == 0, f"Command failed: {result.stderr}"

    # Parse JSON output
    output = json.loads(result.stdout)

    # Check for files array
    if "files" in output:
      files = output["files"]
      assert isinstance(files, list)

      # Files should be relative paths
      for file_path in files:
        assert not Path(file_path).is_absolute()
        assert file_path.startswith(".spec-driver/deltas/")

      # Files should NOT include the main delta, plan, or phase files
      # (those are already in other fields)
      delta_path = output["path"]
      plan_path = output.get("plan", {}).get("path")
      phase_paths = [
        p.get("path") for p in output.get("plan", {}).get("phases", []) if p.get("path")
      ]

      assert delta_path not in files
      if plan_path:
        assert plan_path not in files
      for phase_path in phase_paths:
        assert phase_path not in files

  def test_show_delta_json_includes_task_completion(self) -> None:
    """Test that JSON output includes task completion stats for phases."""
    delta_id = "DE-005"
    delta_dir = (
      self.root / SPEC_DRIVER_DIR / DELTAS_SUBDIR / "DE-005-implement-spec-backfill"
    )

    if not delta_dir.exists():
      self.skipTest("DE-005 not found in repository")

    result = self.runner.invoke(app, ["delta", delta_id, "--json"])

    assert result.exit_code == 0, f"Command failed: {result.stderr}"

    # Parse JSON output
    output = json.loads(result.stdout)

    # Check for plan and phases with task completion
    if "plan" in output and "phases" in output["plan"]:
      phases = output["plan"]["phases"]
      if phases:
        # At least one phase should have task completion data
        phase = phases[0]
        if "tasks_total" in phase:
          assert "tasks_completed" in phase
          assert isinstance(phase["tasks_completed"], int)
          assert isinstance(phase["tasks_total"], int)
          assert phase["tasks_completed"] >= 0
          assert phase["tasks_total"] >= phase["tasks_completed"]

  def test_show_delta_text_includes_task_completion(self) -> None:
    """Test that text output includes task completion stats for phases."""
    delta_id = "DE-005"
    delta_dir = (
      self.root / SPEC_DRIVER_DIR / DELTAS_SUBDIR / "DE-005-implement-spec-backfill"
    )

    if not delta_dir.exists():
      self.skipTest("DE-005 not found in repository")

    result = self.runner.invoke(app, ["delta", delta_id])

    assert result.exit_code == 0, f"Command failed: {result.stderr}"

    # Check for table format with task completion stats (format: "25/25 (100%)")
    # The new format uses a table with Status column showing completion
    assert "phase" in result.stdout.lower()
    assert "status" in result.stdout.lower()
    # Check for completion ratio pattern (e.g., "25/25" or "22/25")
    assert re.search(r"\d+/\d+\s+\(\d+%\)", result.stdout), (
      "Expected task completion stats in format 'X/Y (Z%)'"
    )

  def test_show_delta_json_flag_in_help(self) -> None:
    """Test that --json flag is documented in help."""
    result = self.runner.invoke(app, ["delta", "--help"])

    assert result.exit_code == 0
    assert "--json" in result.stdout
    assert "Output as JSON" in result.stdout


class ShowPathFlagTest(unittest.TestCase):
  """Test cases for --path flag on show commands."""

  def setUp(self) -> None:
    """Set up test environment."""
    self.runner = CliRunner()
    self.root = find_repo_root()

  def test_show_delta_path_flag(self) -> None:
    """Test --path flag returns only the path."""
    delta_dirs = list((self.root / SPEC_DRIVER_DIR / DELTAS_SUBDIR).glob("DE-*"))
    if not delta_dirs:
      self.skipTest("No deltas found in repository")

    delta_id = f"DE-{delta_dirs[0].name.split('-')[1]}"
    result = self.runner.invoke(app, ["delta", delta_id, "--path"])

    assert result.exit_code == 0, f"Command failed: {result.stderr}"
    # Should output just a path (single line, ends with .md)
    output = result.stdout.strip()
    assert output.endswith(".md")
    assert ".spec-driver/deltas/" in output
    assert "\n" not in output  # Single line

  def test_show_adr_path_flag(self) -> None:
    """Test --path flag on show adr."""
    adr_files = list((self.root / SPEC_DRIVER_DIR / DECISIONS_SUBDIR).glob("ADR-*.md"))
    if not adr_files:
      self.skipTest("No ADRs found in repository")

    adr_id = adr_files[0].stem.split("-")[0] + "-" + adr_files[0].stem.split("-")[1]
    result = self.runner.invoke(app, ["adr", adr_id, "--path"])

    assert result.exit_code == 0, f"Command failed: {result.stderr}"
    output = result.stdout.strip()
    assert output.endswith(".md")
    assert "\n" not in output

  def test_show_spec_path_flag(self) -> None:
    """Test --path flag on show spec."""
    spec_dirs = list((self.root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR).glob("SPEC-*"))
    if not spec_dirs:
      self.skipTest("No specs found in repository")

    spec_id = spec_dirs[0].name
    result = self.runner.invoke(app, ["spec", spec_id, "--path"])

    assert result.exit_code == 0, f"Command failed: {result.stderr}"
    output = result.stdout.strip()
    assert output.endswith(".md")
    assert "\n" not in output

  def test_path_and_json_mutually_exclusive(self) -> None:
    """Test that --path and --json are mutually exclusive."""
    result = self.runner.invoke(app, ["delta", "DE-001", "--path", "--json"])

    assert result.exit_code == 1
    assert "mutually exclusive" in result.stderr.lower()


class ShowCardJsonFlagTest(unittest.TestCase):
  """Test cases for --json flag on show card command."""

  def setUp(self) -> None:
    """Set up test environment."""
    self.runner = CliRunner()
    self.root = find_repo_root()

  def test_show_card_json_flag(self) -> None:
    """Test --json flag on show card."""
    card_files = list((self.root / "kanban").rglob("T*.md"))
    if not card_files:
      self.skipTest("No cards found in repository")

    card_id = card_files[0].stem.split("-")[0]
    result = self.runner.invoke(app, ["card", card_id, "--json"])

    assert result.exit_code == 0, f"Command failed: {result.stderr}"
    output = json.loads(result.stdout)
    assert "id" in output
    assert "title" in output
    assert "path" in output

  def test_show_card_path_flag_alias(self) -> None:
    """Test -q alias still works for --path flag."""
    card_files = list((self.root / "kanban").rglob("T*.md"))
    if not card_files:
      self.skipTest("No cards found in repository")

    card_id = card_files[0].stem.split("-")[0]
    result = self.runner.invoke(app, ["card", card_id, "-q"])

    assert result.exit_code == 0, f"Command failed: {result.stderr}"
    output = result.stdout.strip()
    assert output.endswith(".md")
    assert "\n" not in output


class ShowRawFlagTest(unittest.TestCase):
  """Test cases for --raw flag on show commands."""

  def setUp(self) -> None:
    """Set up test environment."""
    self.runner = CliRunner()
    self.root = find_repo_root()

  def test_show_delta_raw_flag(self) -> None:
    """Test --raw flag outputs raw file content."""
    delta_dirs = list((self.root / SPEC_DRIVER_DIR / DELTAS_SUBDIR).glob("DE-*"))
    if not delta_dirs:
      self.skipTest("No deltas found in repository")

    delta_id = f"DE-{delta_dirs[0].name.split('-')[1]}"
    result = self.runner.invoke(app, ["delta", delta_id, "--raw"])

    assert result.exit_code == 0, f"Command failed: {result.stderr}"
    # Raw output should contain frontmatter (starts with ---)
    assert result.stdout.startswith("---")
    # Should contain YAML frontmatter fields
    assert "id:" in result.stdout or "name:" in result.stdout

  def test_show_adr_raw_flag(self) -> None:
    """Test --raw flag on show adr."""
    adr_files = list((self.root / SPEC_DRIVER_DIR / DECISIONS_SUBDIR).glob("ADR-*.md"))
    if not adr_files:
      self.skipTest("No ADRs found in repository")

    adr_id = adr_files[0].stem.split("-")[0] + "-" + adr_files[0].stem.split("-")[1]
    result = self.runner.invoke(app, ["adr", adr_id, "--raw"])

    assert result.exit_code == 0, f"Command failed: {result.stderr}"
    # Raw output should match file content
    expected = adr_files[0].read_text()
    # Strip trailing newline since typer.echo adds one
    assert result.stdout.strip() == expected.strip()

  def test_show_spec_raw_flag(self) -> None:
    """Test --raw flag on show spec."""
    spec_dirs = list((self.root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR).glob("SPEC-*"))
    if not spec_dirs:
      self.skipTest("No specs found in repository")

    spec_id = spec_dirs[0].name
    spec_path = spec_dirs[0] / f"{spec_id}.md"
    if not spec_path.exists():
      self.skipTest(f"Spec file not found: {spec_path}")

    result = self.runner.invoke(app, ["spec", spec_id, "--raw"])

    assert result.exit_code == 0, f"Command failed: {result.stderr}"
    # Raw output should match file content
    expected = spec_path.read_text()
    assert result.stdout.strip() == expected.strip()

  def test_raw_and_json_mutually_exclusive(self) -> None:
    """Test that --raw and --json are mutually exclusive."""
    result = self.runner.invoke(app, ["delta", "DE-001", "--raw", "--json"])

    assert result.exit_code == 1
    assert "mutually exclusive" in result.stderr.lower()

  def test_raw_and_path_mutually_exclusive(self) -> None:
    """Test that --raw and --path are mutually exclusive."""
    result = self.runner.invoke(app, ["delta", "DE-001", "--raw", "--path"])

    assert result.exit_code == 1
    assert "mutually exclusive" in result.stderr.lower()

  def test_all_three_flags_mutually_exclusive(self) -> None:
    """Test that --raw, --json, and --path together fail."""
    result = self.runner.invoke(app, ["delta", "DE-001", "--raw", "--json", "--path"])

    assert result.exit_code == 1
    assert "mutually exclusive" in result.stderr.lower()

  def test_show_raw_flag_in_help(self) -> None:
    """Test that --raw flag is documented in help."""
    result = self.runner.invoke(app, ["delta", "--help"])

    assert result.exit_code == 0
    assert "--raw" in result.stdout
    assert "raw file content" in result.stdout.lower()


# ── Pre-migration regression tests for show revision (VT-migration) ──


class ShowRevisionRegressionTest(unittest.TestCase):
  """Regression tests for show revision — must pass before AND after migration."""

  def setUp(self) -> None:
    self.runner = CliRunner()
    self.root = find_repo_root()

  def test_show_revision_default(self) -> None:
    """show revision RE-001 outputs formatted details."""
    result = self.runner.invoke(app, ["revision", "RE-001"])
    assert result.exit_code == 0, f"Failed: {result.stderr}"
    assert "RE-001" in result.stdout

  def test_show_revision_numeric_shorthand(self) -> None:
    """show revision 1 resolves to RE-001."""
    result = self.runner.invoke(app, ["revision", "1"])
    assert result.exit_code == 0, f"Failed: {result.stderr}"
    assert "RE-001" in result.stdout

  def test_show_revision_path(self) -> None:
    """show revision --path outputs file path."""
    result = self.runner.invoke(app, ["revision", "RE-001", "--path"])
    assert result.exit_code == 0, f"Failed: {result.stderr}"
    path = result.stdout.strip()
    assert path.endswith(".md")
    assert Path(path).exists()

  def test_show_revision_raw(self) -> None:
    """show revision --raw outputs raw file content."""
    result = self.runner.invoke(app, ["revision", "RE-001", "--raw"])
    assert result.exit_code == 0, f"Failed: {result.stderr}"
    assert "---" in result.stdout  # frontmatter

  def test_show_revision_json(self) -> None:
    """show revision --json outputs valid JSON with expected fields."""
    result = self.runner.invoke(app, ["revision", "RE-001", "--json"])
    assert result.exit_code == 0, f"Failed: {result.stderr}"
    parsed = json.loads(result.stdout)
    assert isinstance(parsed, dict)
    assert parsed.get("kind") == "revision"
    assert "path" in parsed

  def test_show_revision_not_found(self) -> None:
    """show revision with nonexistent ID fails gracefully."""
    result = self.runner.invoke(app, ["revision", "RE-999"])
    assert result.exit_code == 1
    assert "not found" in result.stderr.lower()

  def test_show_revision_mutual_exclusivity(self) -> None:
    """show revision --json --path fails with mutual exclusivity error."""
    result = self.runner.invoke(app, ["revision", "RE-001", "--json", "--path"])
    assert result.exit_code == 1
    assert "mutually exclusive" in result.stderr.lower()


class ShowNewSubcommandsTest(unittest.TestCase):
  """Integration tests for Phase 2 show subcommands."""

  def setUp(self) -> None:
    self.runner = CliRunner()

  def test_show_plan_default(self) -> None:
    result = self.runner.invoke(app, ["plan", "IP-041"])
    assert result.exit_code == 0, f"Failed: {result.stderr}"
    assert "IP-041" in result.stdout

  def test_show_plan_path(self) -> None:
    result = self.runner.invoke(app, ["plan", "41", "--path"])
    assert result.exit_code == 0, f"Failed: {result.stderr}"
    assert result.stdout.strip().endswith(".md")

  def test_show_plan_not_found(self) -> None:
    result = self.runner.invoke(app, ["plan", "IP-999"])
    assert result.exit_code == 1
    assert "not found" in result.stderr.lower()

  def test_show_audit_default(self) -> None:
    result = self.runner.invoke(app, ["audit", "AUD-001"])
    assert result.exit_code == 0, f"Failed: {result.stderr}"
    assert "AUD-001" in result.stdout

  def test_show_audit_not_found(self) -> None:
    result = self.runner.invoke(app, ["audit", "AUD-999"])
    assert result.exit_code == 1

  def test_show_issue_default(self) -> None:
    result = self.runner.invoke(app, ["issue", "ISSUE-004"])
    assert result.exit_code == 0, f"Failed: {result.stderr}"
    assert "ISSUE-004" in result.stdout

  def test_show_issue_not_found(self) -> None:
    result = self.runner.invoke(app, ["issue", "ISSUE-999"])
    assert result.exit_code == 1

  def test_show_problem_default(self) -> None:
    result = self.runner.invoke(app, ["problem", "PROB-002"])
    assert result.exit_code == 0, f"Failed: {result.stderr}"
    assert "PROB-002" in result.stdout

  def test_show_improvement_default(self) -> None:
    result = self.runner.invoke(app, ["improvement", "IMPR-001"])
    assert result.exit_code == 0, f"Failed: {result.stderr}"
    assert "IMPR-001" in result.stdout

  def test_show_improvement_not_found(self) -> None:
    result = self.runner.invoke(app, ["improvement", "IMPR-999"])
    assert result.exit_code == 1


# ── VT-063-02: ID inference integration tests ─────────────────


class ShowInferredTest(unittest.TestCase):
  """Integration tests for show with bare ID inference (InferringGroup)."""

  def setUp(self) -> None:
    self.runner = CliRunner()

  def test_existing_subcommand_passthrough(self) -> None:
    """Existing show <type> <id> still works."""
    result = self.runner.invoke(app, ["delta", "DE-063"])
    assert result.exit_code == 0
    assert "DE-063" in result.stdout

  def test_bare_prefixed_id_resolves(self) -> None:
    """show DE-063 resolves without specifying 'delta'."""
    result = self.runner.invoke(app, ["DE-063"])
    assert result.exit_code == 0
    assert "DE-063" in result.stdout

  def test_bare_adr_id_resolves(self) -> None:
    """show ADR-001 resolves without specifying 'adr'."""
    result = self.runner.invoke(app, ["ADR-001"])
    assert result.exit_code == 0
    assert "ADR-001" in result.stdout

  def test_bare_id_with_path_flag(self) -> None:
    """show DE-063 --path returns the file path."""
    result = self.runner.invoke(app, ["DE-063", "--path"])
    assert result.exit_code == 0
    assert "DE-063" in result.stdout
    assert result.stdout.strip().endswith(".md")

  def test_bare_id_with_raw_flag(self) -> None:
    """show DE-063 --raw returns raw file content."""
    result = self.runner.invoke(app, ["DE-063", "--raw"])
    assert result.exit_code == 0
    assert "id: DE-063" in result.stdout

  def test_numeric_id_resolves(self) -> None:
    """show 63 resolves to DE-063 (or disambiguates)."""
    result = self.runner.invoke(app, ["63"])
    # Should either show the delta or list disambiguation
    assert result.exit_code in [0, 1]
    assert "63" in (result.stdout + (result.stderr or ""))

  def test_unknown_id_gives_error(self) -> None:
    """show NONEXISTENT-999 gives clear error."""
    result = self.runner.invoke(app, ["NONEXISTENT-999"])
    assert result.exit_code == 1
    assert "no artifact found" in (result.stderr or "")

  def test_no_args_shows_help(self) -> None:
    """show with no arguments prints help."""
    result = self.runner.invoke(app, [])
    assert "Usage:" in result.stdout

  def test_hidden_command_not_in_help(self) -> None:
    """The 'inferred' command does not appear in --help output."""
    result = self.runner.invoke(app, ["--help"])
    assert "inferred" not in result.stdout


# ── VT-073-01: --content-type flag tests ───────────────────────


class ShowContentTypeFlagTest(unittest.TestCase):
  """Tests for --content-type/-c flag on show subcommands."""

  def setUp(self) -> None:
    self.runner = CliRunner()
    self.root = find_repo_root()

  def test_show_delta_content_type_markdown(self) -> None:
    """show delta -c markdown outputs full file content."""
    delta_dirs = list((self.root / SPEC_DRIVER_DIR / DELTAS_SUBDIR).glob("DE-*"))
    if not delta_dirs:
      self.skipTest("No deltas found")
    delta_id = f"DE-{delta_dirs[0].name.split('-')[1]}"
    result = self.runner.invoke(app, ["delta", delta_id, "-c", "markdown"])
    assert result.exit_code == 0, f"Failed: {result.stderr}"
    assert "---" in result.stdout
    assert "id:" in result.stdout

  def test_show_delta_content_type_yaml(self) -> None:
    """show delta -c yaml outputs only YAML frontmatter."""
    delta_dirs = list((self.root / SPEC_DRIVER_DIR / DELTAS_SUBDIR).glob("DE-*"))
    if not delta_dirs:
      self.skipTest("No deltas found")
    delta_id = f"DE-{delta_dirs[0].name.split('-')[1]}"
    result = self.runner.invoke(app, ["delta", delta_id, "-c", "yaml"])
    assert result.exit_code == 0, f"Failed: {result.stderr}"
    assert "id:" in result.stdout
    # Should NOT contain markdown body
    assert "---" not in result.stdout

  def test_show_delta_content_type_frontmatter(self) -> None:
    """show delta -c frontmatter outputs formatted metadata."""
    delta_dirs = list((self.root / SPEC_DRIVER_DIR / DELTAS_SUBDIR).glob("DE-*"))
    if not delta_dirs:
      self.skipTest("No deltas found")
    delta_id = f"DE-{delta_dirs[0].name.split('-')[1]}"
    result = self.runner.invoke(app, ["delta", delta_id, "-c", "frontmatter"])
    assert result.exit_code == 0, f"Failed: {result.stderr}"
    assert delta_id in result.stdout

  def test_show_adr_content_type_markdown(self) -> None:
    """show adr -c markdown outputs full file content."""
    adr_files = list((self.root / SPEC_DRIVER_DIR / DECISIONS_SUBDIR).glob("ADR-*.md"))
    if not adr_files:
      self.skipTest("No ADRs found")
    adr_id = adr_files[0].stem.split("-")[0] + "-" + adr_files[0].stem.split("-")[1]
    result = self.runner.invoke(app, ["adr", adr_id, "-c", "markdown"])
    assert result.exit_code == 0, f"Failed: {result.stderr}"
    assert "---" in result.stdout

  def test_content_type_overrides_raw_with_warning(self) -> None:
    """--content-type overrides --raw with a warning."""
    delta_dirs = list((self.root / SPEC_DRIVER_DIR / DELTAS_SUBDIR).glob("DE-*"))
    if not delta_dirs:
      self.skipTest("No deltas found")
    delta_id = f"DE-{delta_dirs[0].name.split('-')[1]}"
    result = self.runner.invoke(app, ["delta", delta_id, "--raw", "-c", "yaml"])
    assert result.exit_code == 0, f"Failed: {result.stderr}"
    assert "Warning" in (result.stderr or "")
    assert "id:" in result.stdout

  def test_content_type_in_help(self) -> None:
    """--content-type/-c flag appears in help."""
    result = self.runner.invoke(app, ["delta", "--help"])
    assert result.exit_code == 0
    assert "--content-type" in result.stdout or "-c" in result.stdout

  def test_show_spec_content_type_yaml(self) -> None:
    """show spec -c yaml outputs YAML frontmatter."""
    spec_dirs = list((self.root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR).glob("SPEC-*"))
    if not spec_dirs:
      self.skipTest("No specs found")
    spec_id = spec_dirs[0].name
    result = self.runner.invoke(app, ["spec", spec_id, "-c", "yaml"])
    assert result.exit_code == 0, f"Failed: {result.stderr}"
    assert "id:" in result.stdout

  def test_show_revision_content_type_markdown(self) -> None:
    """show revision -c markdown via emit_artifact path."""
    result = self.runner.invoke(app, ["revision", "RE-001", "-c", "markdown"])
    assert result.exit_code == 0, f"Failed: {result.stderr}"
    assert "---" in result.stdout


if __name__ == "__main__":
  unittest.main()
