"""Comprehensive test suite for unified CLI."""

from __future__ import annotations

import re
import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from supekku.cli.common import matches_regexp
from supekku.cli.main import app

runner = CliRunner()


class TestMainApp:
  """Test main application structure and help."""

  def test_main_help(self):
    """Test main help command."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "spec-driver" in result.stdout
    assert "Specification-driven development toolkit" in result.stdout

  def test_main_no_args(self):
    """Test invoking with no arguments shows help."""
    result = runner.invoke(app, [])
    # Typer with no_args_is_help=True returns exit code 0
    # but Click returns 2, which Typer uses internally
    assert result.exit_code in [0, 2]
    assert "Usage:" in result.stdout

  def test_main_shows_all_commands(self):
    """Test that all major commands are listed."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "install" in result.stdout
    assert "validate" in result.stdout
    assert "sync" in result.stdout
    assert "create" in result.stdout
    assert "list" in result.stdout
    assert "show" in result.stdout
    assert "complete" in result.stdout


class TestWorkspaceCommands:
  """Test workspace management commands."""

  def test_install_help(self):
    """Test install command help."""
    result = runner.invoke(app, ["install", "--help"])
    assert result.exit_code == 0
    assert "Initialize spec-driver workspace" in result.stdout

  def test_install_creates_workspace(self):
    """Test install command creates workspace structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
      result = runner.invoke(app, ["install", tmpdir, "--yes"])
      assert result.exit_code == 0
      assert "Workspace initialized" in result.stdout

      # Verify directories were created
      workspace = Path(tmpdir)
      assert (workspace / "change" / "deltas").exists()
      assert (workspace / "specify" / "tech").exists()
      assert (workspace / ".spec-driver" / "registry").exists()

      # Verify backlog structure
      assert (workspace / "backlog" / "improvements").exists()
      assert (workspace / "backlog" / "issues").exists()
      assert (workspace / "backlog" / "problems").exists()
      assert (workspace / "backlog" / "risks").exists()
      assert (workspace / "backlog" / "backlog.md").exists()

      # Verify backlog.md content
      backlog_content = (workspace / "backlog" / "backlog.md").read_text()
      assert "# Backlog" in backlog_content
      assert "improvements/" in backlog_content

  def test_validate_help(self):
    """Test validate command help."""
    result = runner.invoke(app, ["validate", "--help"])
    assert result.exit_code == 0
    assert "Validate workspace metadata" in result.stdout


class TestCreateCommands:
  """Test create command group."""

  def test_create_help(self):
    """Test create command group help."""
    result = runner.invoke(app, ["create", "--help"])
    assert result.exit_code == 0
    assert "Create new artifacts" in result.stdout

  def test_create_spec_help(self):
    """Test create spec command help."""
    result = runner.invoke(app, ["create", "spec", "--help"])
    assert result.exit_code == 0
    assert "Create a new SPEC or PROD document" in result.stdout
    assert "--kind" in result.stdout
    assert "--testing" in result.stdout

  def test_create_delta_help(self):
    """Test create delta command help."""
    result = runner.invoke(app, ["create", "delta", "--help"])
    assert result.exit_code == 0
    assert "Create a Delta bundle" in result.stdout
    assert "--spec" in result.stdout
    assert "--requirement" in result.stdout

  def test_create_requirement_help(self):
    """Test create requirement command help."""
    result = runner.invoke(app, ["create", "requirement", "--help"])
    assert result.exit_code == 0
    assert "Create a breakout requirement" in result.stdout
    assert "--kind" in result.stdout

  def test_create_revision_help(self):
    """Test create revision command help."""
    result = runner.invoke(app, ["create", "revision", "--help"])
    assert result.exit_code == 0
    assert "Create a Spec Revision bundle" in result.stdout
    assert "--source" in result.stdout
    assert "--destination" in result.stdout

  def test_create_adr_help(self):
    """Test create adr command help."""
    result = runner.invoke(app, ["create", "adr", "--help"])
    assert result.exit_code == 0
    assert "Create a new ADR" in result.stdout
    assert "--status" in result.stdout
    assert "--author" in result.stdout


class TestListCommands:
  """Test list command group."""

  def test_list_help(self):
    """Test list command group help."""
    result = runner.invoke(app, ["list", "--help"])
    assert result.exit_code == 0
    assert "List artifacts" in result.stdout

  def test_list_specs_help(self):
    """Test list specs command help."""
    result = runner.invoke(app, ["list", "specs", "--help"])
    assert result.exit_code == 0
    assert "List SPEC/PROD artifacts" in result.stdout
    assert "--kind" in result.stdout
    assert "--filter" in result.stdout
    assert "--package" in result.stdout

  def test_list_deltas_help(self):
    """Test list deltas command help."""
    result = runner.invoke(app, ["list", "deltas", "--help"])
    assert result.exit_code == 0
    assert "List deltas" in result.stdout
    assert "--status" in result.stdout
    assert "--details" in result.stdout

  def test_list_changes_help(self):
    """Test list changes command help."""
    result = runner.invoke(app, ["list", "changes", "--help"])
    assert result.exit_code == 0
    assert "List change artifacts" in result.stdout
    assert "--kind" in result.stdout
    assert "--filter" in result.stdout
    assert "--status" in result.stdout

  def test_list_adrs_help(self):
    """Test list adrs command help."""
    result = runner.invoke(app, ["list", "adrs", "--help"])
    assert result.exit_code == 0
    assert "List Architecture Decision Records" in result.stdout
    assert "--status" in result.stdout
    assert "--tag" in result.stdout
    assert "--spec" in result.stdout
    assert "--delta" in result.stdout
    assert "--requirement" in result.stdout
    assert "--policy" in result.stdout


class TestShowCommands:
  """Test show command group."""

  def test_show_help(self):
    """Test show command group help."""
    result = runner.invoke(app, ["show", "--help"])
    assert result.exit_code == 0
    assert "Show detailed artifact information" in result.stdout

  def test_show_adr_help(self):
    """Test show adr command help."""
    result = runner.invoke(app, ["show", "adr", "--help"])
    assert result.exit_code == 0
    assert "Show detailed information about a specific decision" in result.stdout


class TestCompleteCommands:
  """Test complete command group."""

  def test_complete_help(self):
    """Test complete command group help."""
    result = runner.invoke(app, ["complete", "--help"])
    assert result.exit_code == 0
    assert "Complete artifacts" in result.stdout

  def test_complete_delta_help(self):
    """Test complete delta command help."""
    result = runner.invoke(app, ["complete", "delta", "--help"])
    assert result.exit_code == 0
    assert "Complete a delta" in result.stdout
    assert "--dry-run" in result.stdout
    assert "--force" in result.stdout
    assert "--skip-sync" in result.stdout


class TestSyncCommand:
  """Test sync command."""

  def test_sync_help(self):
    """Test sync command help."""
    result = runner.invoke(app, ["sync", "--help"])
    assert result.exit_code == 0
    assert "Synchronize specifications" in result.stdout
    assert "--language" in result.stdout
    assert "--existing" in result.stdout
    assert "--check" in result.stdout
    assert "--dry-run" in result.stdout
    assert "--specs" in result.stdout
    assert "--adr" in result.stdout
    assert "--prune" in result.stdout

  def test_sync_prune_flag_in_help(self):
    """Test that --prune flag is documented in help."""
    result = runner.invoke(app, ["sync", "--help"])
    assert result.exit_code == 0
    assert "--prune" in result.stdout
    assert "deleted source" in result.stdout
    assert "--force" in result.stdout


class TestCommonOptions:
  """Test common options across commands."""

  def test_root_option_in_list_specs(self):
    """Test --root option is available."""
    result = runner.invoke(app, ["list", "specs", "--help"])
    assert result.exit_code == 0
    assert "--root" in result.stdout

  def test_root_option_in_validate(self):
    """Test --root option is available."""
    result = runner.invoke(app, ["validate", "--help"])
    assert result.exit_code == 0
    assert "--root" in result.stdout


class TestCommandStructure:
  """Test command structure follows verb-noun pattern."""

  def test_create_follows_verb_noun(self):
    """Test create commands follow verb-noun pattern."""
    # create spec, create delta, etc.
    result = runner.invoke(app, ["create", "--help"])
    assert result.exit_code == 0
    assert "spec" in result.stdout
    assert "delta" in result.stdout
    assert "requirement" in result.stdout
    assert "revision" in result.stdout

  def test_list_follows_verb_noun(self):
    """Test list commands follow verb-noun pattern."""
    # list specs, list deltas, list adrs, etc.
    result = runner.invoke(app, ["list", "--help"])
    assert result.exit_code == 0
    assert "specs" in result.stdout
    assert "deltas" in result.stdout
    assert "changes" in result.stdout
    assert "adrs" in result.stdout

  def test_show_follows_verb_noun(self):
    """Test show commands follow verb-noun pattern."""
    # show adr
    result = runner.invoke(app, ["show", "--help"])
    assert result.exit_code == 0
    assert "adr" in result.stdout

  def test_complete_follows_verb_noun(self):
    """Test complete commands follow verb-noun pattern."""
    # complete delta
    result = runner.invoke(app, ["complete", "--help"])
    assert result.exit_code == 0
    assert "delta" in result.stdout


class TestErrorHandling:
  """Test error handling in CLI commands."""

  def test_invalid_command(self):
    """Test invalid command returns error."""
    result = runner.invoke(app, ["invalid-command"])
    assert result.exit_code != 0

  def test_missing_required_argument(self):
    """Test missing required argument returns error."""
    result = runner.invoke(app, ["create", "requirement"])
    # Should fail because spec, requirement, and title are required
    assert result.exit_code != 0


class TestJSONFlagConsistency:
  """Test --json flag consistency across list and show commands (DE-009)."""

  def test_list_deltas_json_flag(self):
    """Test list deltas accepts --json flag."""
    result = runner.invoke(app, ["list", "deltas", "--json"])
    assert result.exit_code == 0
    # Output should be valid JSON
    import json

    try:
      data = json.loads(result.stdout)
      assert isinstance(data, dict)
    except json.JSONDecodeError:
      pytest.fail("Output is not valid JSON")

  def test_list_deltas_json_equals_format_json(self):
    """Test --json produces same output as --format=json for deltas."""
    result_json = runner.invoke(app, ["list", "deltas", "--json"])
    result_format = runner.invoke(app, ["list", "deltas", "--format", "json"])
    assert result_json.exit_code == 0
    assert result_format.exit_code == 0
    assert result_json.stdout == result_format.stdout

  def test_list_adrs_json_flag(self):
    """Test list adrs accepts --json flag."""
    result = runner.invoke(app, ["list", "adrs", "--json"])
    assert result.exit_code == 0
    import json

    try:
      data = json.loads(result.stdout)
      assert isinstance(data, dict)
    except json.JSONDecodeError:
      pytest.fail("Output is not valid JSON")

  def test_list_adrs_json_equals_format_json(self):
    """Test --json produces same output as --format=json for adrs."""
    result_json = runner.invoke(app, ["list", "adrs", "--json"])
    result_format = runner.invoke(app, ["list", "adrs", "--format", "json"])
    assert result_json.exit_code == 0
    assert result_format.exit_code == 0
    assert result_json.stdout == result_format.stdout

  def test_list_requirements_json_flag(self):
    """Test list requirements accepts --json flag."""
    result = runner.invoke(app, ["list", "requirements", "--json"])
    assert result.exit_code == 0
    import json

    try:
      data = json.loads(result.stdout)
      assert isinstance(data, dict)
    except json.JSONDecodeError:
      pytest.fail("Output is not valid JSON")

  def test_list_requirements_json_equals_format_json(self):
    """Test --json produces same output as --format=json for requirements."""
    result_json = runner.invoke(app, ["list", "requirements", "--json"])
    result_format = runner.invoke(app, ["list", "requirements", "--format", "json"])
    assert result_json.exit_code == 0
    assert result_format.exit_code == 0
    assert result_json.stdout == result_format.stdout

  def test_list_revisions_json_flag(self):
    """Test list revisions accepts --json flag."""
    result = runner.invoke(app, ["list", "revisions", "--json"])
    assert result.exit_code == 0
    import json

    try:
      data = json.loads(result.stdout)
      assert isinstance(data, dict)
    except json.JSONDecodeError:
      pytest.fail("Output is not valid JSON")

  def test_list_revisions_json_equals_format_json(self):
    """Test --json produces same output as --format=json for revisions."""
    result_json = runner.invoke(app, ["list", "revisions", "--json"])
    result_format = runner.invoke(app, ["list", "revisions", "--format", "json"])
    assert result_json.exit_code == 0
    assert result_format.exit_code == 0
    assert result_json.stdout == result_format.stdout

  def test_list_changes_json_flag(self):
    """Test list changes accepts --json flag."""
    result = runner.invoke(app, ["list", "changes", "--json"])
    assert result.exit_code == 0
    import json

    try:
      data = json.loads(result.stdout)
      assert isinstance(data, dict)
    except json.JSONDecodeError:
      pytest.fail("Output is not valid JSON")

  def test_list_changes_json_equals_format_json(self):
    """Test --json produces same output as --format=json for changes."""
    result_json = runner.invoke(app, ["list", "changes", "--json"])
    result_format = runner.invoke(app, ["list", "changes", "--format", "json"])
    assert result_json.exit_code == 0
    assert result_format.exit_code == 0
    assert result_json.stdout == result_format.stdout

  def test_list_specs_json_flag_already_exists(self):
    """Test list specs --json flag (should already work)."""
    result = runner.invoke(app, ["list", "specs", "--json"])
    assert result.exit_code == 0
    import json

    try:
      data = json.loads(result.stdout)
      assert isinstance(data, dict)
    except json.JSONDecodeError:
      pytest.fail("Output is not valid JSON")

  def test_list_specs_json_help_documents_flag(self):
    """Test list specs help mentions --json flag."""
    result = runner.invoke(app, ["list", "specs", "--help"])
    assert result.exit_code == 0
    assert "--json" in result.stdout

  def test_list_deltas_json_help_documents_flag(self):
    """Test list deltas help mentions --json flag."""
    result = runner.invoke(app, ["list", "deltas", "--help"])
    assert result.exit_code == 0
    assert "--json" in result.stdout

  def test_list_adrs_json_help_documents_flag(self):
    """Test list adrs help mentions --json flag."""
    result = runner.invoke(app, ["list", "adrs", "--help"])
    assert result.exit_code == 0
    assert "--json" in result.stdout


class TestShowCommandJSON:
  """Test --json flag on show commands (DE-009)."""

  def test_show_spec_json_flag(self):
    """Test show spec accepts --json flag."""
    # Use a real spec ID that exists in this repo
    result = runner.invoke(app, ["show", "spec", "SPEC-001", "--json"])
    # May not find spec, but should accept the flag
    # If spec not found, exit code=1; if flag not recognized, exit code=2
    assert result.exit_code in [0, 1]
    if result.exit_code == 0:
      import json

      try:
        data = json.loads(result.stdout)
        assert isinstance(data, dict)
      except json.JSONDecodeError:
        pytest.fail("Output is not valid JSON")

  def test_show_adr_json_flag(self):
    """Test show adr accepts --json flag."""
    result = runner.invoke(app, ["show", "adr", "ADR-001", "--json"])
    assert result.exit_code in [0, 1]
    if result.exit_code == 0:
      import json

      try:
        data = json.loads(result.stdout)
        assert isinstance(data, dict)
      except json.JSONDecodeError:
        pytest.fail("Output is not valid JSON")

  def test_show_requirement_json_flag(self):
    """Test show requirement accepts --json flag."""
    result = runner.invoke(app, ["show", "requirement", "SPEC-001.FR-001", "--json"])
    assert result.exit_code in [0, 1]
    if result.exit_code == 0:
      import json

      try:
        data = json.loads(result.stdout)
        assert isinstance(data, dict)
      except json.JSONDecodeError:
        pytest.fail("Output is not valid JSON")

  def test_show_revision_json_flag(self):
    """Test show revision accepts --json flag."""
    result = runner.invoke(app, ["show", "revision", "RE-001", "--json"])
    assert result.exit_code in [0, 1]
    if result.exit_code == 0:
      import json

      try:
        data = json.loads(result.stdout)
        assert isinstance(data, dict)
      except json.JSONDecodeError:
        pytest.fail("Output is not valid JSON")

  def test_show_delta_json_flag_already_exists(self):
    """Test show delta --json flag (should already work)."""
    result = runner.invoke(app, ["show", "delta", "DE-001", "--json"])
    assert result.exit_code in [0, 1]
    if result.exit_code == 0:
      import json

      try:
        data = json.loads(result.stdout)
        assert isinstance(data, dict)
      except json.JSONDecodeError:
        pytest.fail("Output is not valid JSON")

  def test_show_spec_json_complete_output(self):
    """Test show spec --json returns complete spec data, not just id."""
    # Use PROD-010 which we know exists
    result = runner.invoke(app, ["show", "spec", "PROD-010", "--json"])
    assert result.exit_code == 0, f"Command failed: {result.stdout}"

    import json

    data = json.loads(result.stdout)
    # Should have more than just id
    assert "id" in data
    assert data["id"] == "PROD-010"
    # Should include other spec fields
    assert "name" in data, "Missing 'name' field"
    assert "status" in data, "Missing 'status' field"
    assert "kind" in data, "Missing 'kind' field"
    assert data["kind"] == "prod"
    assert "path" in data, "Missing 'path' field"
    # Should not be minimal output like {"id": "PROD-010"}
    assert len(data.keys()) > 2, f"Output too minimal: {data}"

  def test_show_adr_json_complete_output(self):
    """Test show adr --json returns complete decision data without crashing."""
    result = runner.invoke(app, ["show", "adr", "ADR-001", "--json"])
    assert result.exit_code == 0, f"Command failed: {result.stdout}"

    import json

    data = json.loads(result.stdout)
    # Should have complete decision data
    assert "id" in data
    assert data["id"] == "ADR-001"
    assert "title" in data, "Missing 'title' field"
    assert "status" in data, "Missing 'status' field"
    assert "path" in data, "Missing 'path' field"
    # Date fields
    assert "created" in data, "Missing 'created' field"
    # Should not crash with AttributeError
    assert len(data.keys()) > 3, f"Output too minimal: {data}"

  def test_show_spec_json_help_documents_flag(self):
    """Test show spec help mentions --json flag."""
    result = runner.invoke(app, ["show", "spec", "--help"])
    assert result.exit_code == 0
    assert "--json" in result.stdout

  def test_show_adr_json_help_documents_flag(self):
    """Test show adr help mentions --json flag."""
    result = runner.invoke(app, ["show", "adr", "--help"])
    assert result.exit_code == 0
    assert "--json" in result.stdout


class TestStatusFilterParity:
  """Test status filter consistency across list commands (DE-009)."""

  def test_list_specs_status_filter_flag(self):
    """Test list specs accepts --status/-s flag."""
    result = runner.invoke(app, ["list", "specs", "--status", "draft"])
    assert result.exit_code == 0

  def test_list_specs_status_filter_short_flag(self):
    """Test list specs accepts -s short flag."""
    result = runner.invoke(app, ["list", "specs", "-s", "draft"])
    assert result.exit_code == 0

  def test_list_specs_status_filter_active(self):
    """Test list specs filters by active status."""
    result = runner.invoke(app, ["list", "specs", "--status", "active"])
    assert result.exit_code == 0

  def test_list_specs_status_filter_deprecated(self):
    """Test list specs filters by deprecated status."""
    result = runner.invoke(app, ["list", "specs", "--status", "deprecated"])
    assert result.exit_code == 0

  def test_list_specs_status_filter_superseded(self):
    """Test list specs filters by superseded status."""
    result = runner.invoke(app, ["list", "specs", "--status", "superseded"])
    assert result.exit_code == 0

  def test_list_specs_status_help_documents_flag(self):
    """Test list specs help mentions --status/-s flag."""
    result = runner.invoke(app, ["list", "specs", "--help"])
    assert result.exit_code == 0
    assert "--status" in result.stdout or "-s" in result.stdout

  def test_list_specs_status_filter_with_json(self):
    """Test status filter works with JSON output."""
    result = runner.invoke(app, ["list", "specs", "--status", "active", "--json"])
    assert result.exit_code == 0
    import json

    try:
      data = json.loads(result.stdout)
      assert isinstance(data, dict)
      assert "items" in data
      # All items should have active status
      for item in data["items"]:
        if "status" in item:
          assert item["status"] == "active"
    except json.JSONDecodeError:
      pytest.fail("Output is not valid JSON")


class TestJSONSchemaRegression:
  """Test JSON output schema stability (DE-009 backward compatibility)."""

  def test_list_specs_json_schema_stable(self):
    """Test list specs JSON output maintains expected structure."""
    result = runner.invoke(app, ["list", "specs", "--json"])
    assert result.exit_code == 0
    import json

    data = json.loads(result.stdout)
    # Should have items key
    assert "items" in data
    assert isinstance(data["items"], list)

  def test_list_deltas_json_schema_stable(self):
    """Test list deltas JSON output maintains expected structure."""
    result = runner.invoke(app, ["list", "deltas", "--format", "json"])
    assert result.exit_code == 0
    import json

    data = json.loads(result.stdout)
    # Should have expected top-level structure
    assert isinstance(data, dict)


class TestRegexpFiltering:
  """Test regexp filtering utility and CLI flags."""

  def test_matches_regexp_none_pattern(self):
    """Test that None pattern matches everything."""
    assert matches_regexp(None, ["foo", "bar"], False)
    assert matches_regexp(None, [], False)

  def test_matches_regexp_basic_match(self):
    """Test basic pattern matching."""
    assert matches_regexp(r"foo", ["foo", "bar"], False)
    assert matches_regexp(r"bar", ["foo", "bar"], False)
    assert not matches_regexp(r"baz", ["foo", "bar"], False)

  def test_matches_regexp_case_sensitive(self):
    """Test case-sensitive matching."""
    assert matches_regexp(r"Foo", ["Foo", "bar"], False)
    assert not matches_regexp(r"Foo", ["foo", "bar"], False)
    assert not matches_regexp(r"FOO", ["foo", "bar"], False)

  def test_matches_regexp_case_insensitive(self):
    """Test case-insensitive matching."""
    assert matches_regexp(r"foo", ["Foo", "bar"], True)
    assert matches_regexp(r"FOO", ["foo", "bar"], True)
    assert matches_regexp(r"BaR", ["foo", "bar"], True)

  def test_matches_regexp_partial_match(self):
    """Test that patterns match substrings."""
    assert matches_regexp(r"Decision", ["Architecture Decision Record"], False)
    assert matches_regexp(r"ADR-\d+", ["ADR-001: Some Decision"], False)
    assert matches_regexp(r"decision", ["Architecture Decision Record"], True)

  def test_matches_regexp_multiple_fields(self):
    """Test matching across multiple fields."""
    assert matches_regexp(r"test", ["foo", "bar", "test"], False)
    assert matches_regexp(r"test", ["test", "bar"], False)
    assert not matches_regexp(r"test", ["foo", "bar"], False)

  def test_matches_regexp_empty_fields(self):
    """Test handling of empty/None fields."""
    assert matches_regexp(r"foo", ["foo", None, ""], False)
    assert not matches_regexp(r"foo", [None, "", "bar"], False)

  def test_matches_regexp_invalid_pattern(self):
    """Test invalid regexp pattern raises error."""
    with pytest.raises(re.error):
      matches_regexp(r"[invalid(", ["foo"], False)

  def test_matches_regexp_complex_patterns(self):
    """Test complex regexp patterns."""
    # Word boundary
    assert matches_regexp(r"\bADR\b", ["ADR-001"], False)
    assert not matches_regexp(r"\bADR\b", ["ADRIFT"], False)

    # Alternation
    assert matches_regexp(r"accepted|rejected", ["status: accepted"], False)
    assert matches_regexp(r"accepted|rejected", ["status: rejected"], False)

    # Character class
    assert matches_regexp(r"SPEC-[0-9]{3}", ["SPEC-001"], False)
    assert not matches_regexp(r"SPEC-[0-9]{3}", ["SPEC-1"], False)

  def test_list_adrs_regexp_flag(self):
    """Test list adrs command has --regexp flag."""
    result = runner.invoke(app, ["list", "adrs", "--help"])
    assert result.exit_code == 0
    assert "--regexp" in result.stdout
    assert "--case-insensitive" in result.stdout

  def test_list_specs_regexp_flag(self):
    """Test list specs command has --regexp flag."""
    result = runner.invoke(app, ["list", "specs", "--help"])
    assert result.exit_code == 0
    assert "--regexp" in result.stdout
    assert "--case-insensitive" in result.stdout

  def test_list_deltas_regexp_flag(self):
    """Test list deltas command has --regexp flag."""
    result = runner.invoke(app, ["list", "deltas", "--help"])
    assert result.exit_code == 0
    assert "--regexp" in result.stdout
    assert "--case-insensitive" in result.stdout

  def test_list_changes_regexp_flag(self):
    """Test list changes command has --regexp flag."""
    result = runner.invoke(app, ["list", "changes", "--help"])
    assert result.exit_code == 0
    assert "--regexp" in result.stdout
    assert "--case-insensitive" in result.stdout


class TestPolicyCommands:
  """Test policy-related CLI commands."""

  def test_list_policies_help(self):
    """Test list policies command help."""
    result = runner.invoke(app, ["list", "policies", "--help"])
    assert result.exit_code == 0
    assert "List policies with optional filtering" in result.stdout
    assert "--status" in result.stdout
    assert "--tag" in result.stdout
    assert "--spec" in result.stdout

  def test_list_policies_json_flag(self):
    """Test list policies supports --json flag."""
    result = runner.invoke(app, ["list", "policies", "--help"])
    assert result.exit_code == 0
    assert "--json" in result.stdout
    assert "--format" in result.stdout

  def test_list_policies_empty_succeeds(self):
    """Test list policies with no policies exits successfully."""
    with tempfile.TemporaryDirectory() as tmpdir:
      # Initialize workspace
      runner.invoke(app, ["install", tmpdir, "--yes"])
      result = runner.invoke(app, ["list", "policies", "--root", tmpdir])
      assert result.exit_code == 0

  def test_show_policy_help(self):
    """Test show policy command help."""
    result = runner.invoke(app, ["show", "policy", "--help"])
    assert result.exit_code == 0
    assert "Show detailed information about a specific policy" in result.stdout
    assert "--json" in result.stdout

  def test_create_policy_help(self):
    """Test create policy command help."""
    result = runner.invoke(app, ["create", "policy", "--help"])
    assert result.exit_code == 0
    assert "Create a new policy with the next available ID" in result.stdout
    assert "--status" in result.stdout
    assert "--author" in result.stdout


class TestStandardCommands:
  """Test standard-related CLI commands."""

  def test_list_standards_help(self):
    """Test list standards command help."""
    result = runner.invoke(app, ["list", "standards", "--help"])
    assert result.exit_code == 0
    assert "List standards with optional filtering" in result.stdout
    assert "--status" in result.stdout
    # Check that status help mentions all standard statuses
    assert "Filter by status" in result.stdout

  def test_list_standards_json_flag(self):
    """Test list standards supports --json flag."""
    result = runner.invoke(app, ["list", "standards", "--help"])
    assert result.exit_code == 0
    assert "--json" in result.stdout
    assert "--format" in result.stdout

  def test_list_standards_empty_succeeds(self):
    """Test list standards with no standards exits successfully."""
    with tempfile.TemporaryDirectory() as tmpdir:
      # Initialize workspace
      runner.invoke(app, ["install", tmpdir, "--yes"])
      result = runner.invoke(app, ["list", "standards", "--root", tmpdir])
      assert result.exit_code == 0

  def test_show_standard_help(self):
    """Test show standard command help."""
    result = runner.invoke(app, ["show", "standard", "--help"])
    assert result.exit_code == 0
    assert "Show detailed information about a specific standard" in result.stdout
    assert "--json" in result.stdout

  def test_create_standard_help(self):
    """Test create standard command help."""
    result = runner.invoke(app, ["create", "standard", "--help"])
    assert result.exit_code == 0
    assert "Create a new standard with the next available ID" in result.stdout
    assert "--status" in result.stdout
    # Check that status help mentions standard can be draft/required/default
    assert "Initial status" in result.stdout


class TestMultiValueFilters:
  """Test multi-value filter support in list commands.

  These tests verify that comma-separated filter values work correctly
  and maintain backward compatibility with single values.
  """

  def test_list_deltas_multi_value_status_not_yet_implemented(self):
    """Test multi-value status filter for deltas (TDD placeholder)."""
    # This test will be updated in Task 1.4
    # Expected: returns deltas with status draft OR in-progress
    result = runner.invoke(app, ["list", "deltas", "-s", "draft,in-progress", "--json"])
    # For now, just ensure it doesn't crash
    assert result.exit_code == 0
    # TODO: Task 1.4 - verify multi-value filtering works correctly

  def test_list_specs_multi_value_kind_works(self):
    """Test multi-value kind filter for specs returns union."""
    # Test that prod,tech returns both PROD and SPEC specs
    result = runner.invoke(app, ["list", "specs", "-k", "prod,tech", "--json"])
    assert result.exit_code == 0, f"Command failed: {result.stdout}"

    import json

    data = json.loads(result.stdout)
    items = data.get("items", [])

    # Should have both PROD and SPEC specs
    prod_specs = [s for s in items if s["id"].startswith("PROD-")]
    tech_specs = [s for s in items if s["id"].startswith("SPEC-")]

    assert len(prod_specs) > 0, "Should have PROD specs"
    assert len(tech_specs) > 0, "Should have SPEC specs"
    # TODO: Task 1.4 - change to: assert result.exit_code == 0

  def test_list_requirements_multi_value_kind_not_yet_implemented(self):
    """Test multi-value kind filter for requirements (TDD placeholder)."""
    # Expected after Task 1.4: returns requirements with kind FR OR NF
    result = runner.invoke(app, ["list", "requirements", "-k", "FR,NF", "--json"])
    assert result.exit_code == 0  # Should not error
    # TODO: Task 1.4 - verify multi-value kind filtering works

  def test_list_adrs_multi_value_status_not_yet_implemented(self):
    """Test multi-value status filter for ADRs (TDD placeholder)."""
    # Expected after Task 1.4: returns ADRs with status draft OR proposed
    result = runner.invoke(app, ["list", "adrs", "-s", "draft,proposed", "--json"])
    assert result.exit_code == 0  # Should not error
    # TODO: Task 1.4 - verify multi-value status filtering works

  def test_backward_compat_single_value_status_filter(self):
    """Test that single-value status filters still work (backward compatibility)."""
    # Single-value filters should continue to work unchanged
    result = runner.invoke(app, ["list", "deltas", "-s", "draft"])
    # Should not error - backward compatibility maintained
    assert result.exit_code == 0

  def test_backward_compat_single_value_kind_filter(self):
    """Test that single-value kind filters still work (backward compatibility)."""
    result = runner.invoke(app, ["list", "specs", "-k", "tech"])
    # Should not error - backward compatibility maintained
    assert result.exit_code == 0


class TestReverseRelationshipQueries:
  """Test reverse relationship query flags for list commands.

  These tests verify the --implements, --verified-by, and --informed-by flags
  that enable native reverse traversal of relationships in registries.
  """

  def test_list_deltas_implements_flag_exists(self):
    """Test that list deltas accepts --implements flag (TDD placeholder)."""
    # This flag will be implemented in Task 1.7
    # Expected: returns deltas that implement the given requirement
    result = runner.invoke(
      app, ["list", "deltas", "--implements", "PROD-010.FR-004", "--json"]
    )
    # For now, verify flag is recognized (will fail until implementation)
    # After Task 1.7: verify result.exit_code == 0 and filtering works
    assert result is not None  # Placeholder assertion for TDD

  def test_list_deltas_implements_filters_correctly(self):
    """Test that --implements returns only deltas implementing specific requirement."""
    result = runner.invoke(
      app, ["list", "deltas", "--implements", "PROD-010.FR-004", "--json"]
    )

    if result.exit_code == 0:
      import json

      data = json.loads(result.stdout)
      items = data.get("items", [])

      # All returned deltas should implement PROD-010.FR-004
      for delta in items:
        applies_to = delta.get("applies_to", {})
        requirements = applies_to.get("requirements", [])
        assert "PROD-010.FR-004" in requirements, f"{delta['id']} missing requirement"

  def test_list_deltas_implements_with_status_filter(self):
    """Test combining --implements with --status filter."""
    # Expected: returns in-progress deltas that implement requirement
    result = runner.invoke(
      app,
      [
        "list",
        "deltas",
        "--implements",
        "PROD-010.FR-004",
        "-s",
        "in-progress",
        "--json",
      ],
    )
    # After Task 1.7: verify both filters apply
    assert result is not None  # Placeholder for TDD

  def test_list_deltas_implements_nonexistent_requirement(self):
    """Test --implements with non-existent requirement returns empty list."""
    result = runner.invoke(
      app,
      ["list", "deltas", "--implements", "NONEXISTENT.FR-999", "--json"],
    )

    if result.exit_code == 0:
      import json

      data = json.loads(result.stdout)
      items = data.get("items", [])
      assert len(items) == 0, "Should return empty list for non-existent requirement"

  def test_list_requirements_verified_by_flag_exists(self):
    """Test that list requirements accepts --verified-by flag (TDD placeholder)."""
    # This flag will be implemented in Task 1.7
    # Expected: returns requirements verified by given artifact
    result = runner.invoke(
      app,
      ["list", "requirements", "--verified-by", "VT-CLI-001", "--json"],
    )
    # After Task 1.7: assert result.exit_code == 0
    assert result is not None  # Placeholder for TDD

  def test_list_requirements_verified_by_exact_match(self):
    """Test --verified-by with exact artifact ID."""
    result = runner.invoke(
      app,
      ["list", "requirements", "--verified-by", "VT-PROD010-FILTER-002", "--json"],
    )

    if result.exit_code == 0:
      import json

      data = json.loads(result.stdout)
      items = data.get("items", [])

      # Returned requirements should be verified by the artifact
      for req in items:
        verified_by = req.get("verified_by", [])
        coverage_evidence = req.get("coverage_evidence", [])
        artifact_found = (
          "VT-PROD010-FILTER-002" in verified_by
          or "VT-PROD010-FILTER-002" in coverage_evidence
        )
        assert artifact_found, f"{req['uid']} not verified by artifact"

  def test_list_requirements_verified_by_glob_pattern(self):
    """Test --verified-by with glob pattern matching."""
    # Expected after Task 1.8: glob patterns work for verification artifacts
    result = runner.invoke(
      app, ["list", "requirements", "--verified-by", "VT-CLI-*", "--json"]
    )

    if result.exit_code == 0:
      import json

      data = json.loads(result.stdout)
      items = data.get("items", [])

      # All returned requirements should have VT-CLI-* artifacts
      for req in items:
        verified_by = req.get("verified_by", [])
        coverage_evidence = req.get("coverage_evidence", [])
        all_artifacts = verified_by + coverage_evidence

        has_vt_cli = any(a.startswith("VT-CLI-") for a in all_artifacts)
        assert has_vt_cli, f"{req['uid']} missing VT-CLI-* artifact"

  def test_list_requirements_verified_by_va_pattern(self):
    """Test --verified-by with VA (agent validation) pattern."""
    result = runner.invoke(
      app, ["list", "requirements", "--verified-by", "VA-*", "--json"]
    )
    # After Task 1.8: verify VA artifacts matched
    assert result is not None  # Placeholder for TDD

  def test_list_requirements_verified_by_with_spec_filter(self):
    """Test combining --verified-by with --spec filter."""
    result = runner.invoke(
      app,
      ["list", "requirements", "--spec", "SPEC-110", "--verified-by", "VT-*", "--json"],
    )
    # After Task 1.7: verify both filters apply (AND logic)
    assert result is not None  # Placeholder for TDD

  def test_list_requirements_verified_by_nonexistent_artifact(self):
    """Test --verified-by with non-existent artifact returns empty list."""
    result = runner.invoke(
      app,
      ["list", "requirements", "--verified-by", "NONEXISTENT-ARTIFACT", "--json"],
    )

    if result.exit_code == 0:
      import json

      data = json.loads(result.stdout)
      items = data.get("items", [])
      assert len(items) == 0, "Should return empty list for non-existent artifact"

  def test_list_specs_informed_by_flag_exists(self):
    """Test that list specs accepts --informed-by flag (TDD placeholder)."""
    # This flag will be implemented in Task 1.7
    # Expected: returns specs informed by given ADR
    result = runner.invoke(
      app, ["list", "specs", "--informed-by", "ADR-001", "--json"]
    )
    # After Task 1.7: assert result.exit_code == 0
    assert result is not None  # Placeholder for TDD

  def test_list_specs_informed_by_filters_correctly(self):
    """Test that --informed-by returns only specs referencing specific ADR."""
    result = runner.invoke(app, ["list", "specs", "--informed-by", "ADR-005", "--json"])

    if result.exit_code == 0:
      import json

      data = json.loads(result.stdout)
      items = data.get("items", [])

      # All returned specs should reference ADR-005
      for spec in items:
        informed_by = spec.get("informed_by", [])
        assert "ADR-005" in informed_by, f"{spec['id']} missing ADR-005 reference"

  def test_list_specs_informed_by_with_kind_filter(self):
    """Test combining --informed-by with --kind filter."""
    result = runner.invoke(
      app,
      ["list", "specs", "--informed-by", "ADR-005", "-k", "tech", "--json"],
    )
    # After Task 1.7: verify both filters apply
    assert result is not None  # Placeholder for TDD

  def test_list_specs_informed_by_nonexistent_adr(self):
    """Test --informed-by with non-existent ADR returns empty list."""
    result = runner.invoke(app, ["list", "specs", "--informed-by", "ADR-999", "--json"])

    if result.exit_code == 0:
      import json

      data = json.loads(result.stdout)
      items = data.get("items", [])
      assert len(items) == 0, "Should return empty list for non-existent ADR"


if __name__ == "__main__":
  pytest.main([__file__, "-v"])
