"""Tests for schema CLI commands (via show schema / list schemas)."""

from __future__ import annotations

import unittest

from typer.testing import CliRunner

from supekku.cli.main import app


class SchemaCommandsTest(unittest.TestCase):
  """Test cases for schema CLI commands."""

  def setUp(self) -> None:
    self.runner = CliRunner()

  def test_list_schemas(self) -> None:
    """Test listing all schemas via 'list schemas'."""
    result = self.runner.invoke(app, ["list", "schemas"])

    assert result.exit_code == 0
    assert "Available Block Schemas" in result.stdout
    assert "delta.relationships" in result.stdout
    assert "plan.overview" in result.stdout
    assert "phase.overview" in result.stdout
    assert "verification.coverage" in result.stdout
    assert "spec.relationships" in result.stdout
    assert "spec.capabilities" in result.stdout
    assert "revision.change" in result.stdout

  def test_show_schema_markdown_delta_relationships(self) -> None:
    result = self.runner.invoke(
      app,
      ["show", "schema", "delta.relationships", "--format", "markdown"],
    )

    assert result.exit_code == 0
    assert "delta.relationships" in result.stdout
    assert "supekku:delta.relationships@v1" in result.stdout
    assert "delta_id" in result.stdout
    assert "primary_specs" in result.stdout

  def test_show_schema_markdown_plan_overview(self) -> None:
    result = self.runner.invoke(
      app,
      ["show", "schema", "plan.overview", "--format", "markdown"],
    )

    assert result.exit_code == 0
    assert "plan.overview" in result.stdout
    assert "supekku:plan.overview@v1" in result.stdout
    assert "plan_id" in result.stdout
    assert "delta_id" in result.stdout

  def test_show_schema_markdown_phase_overview(self) -> None:
    result = self.runner.invoke(
      app,
      ["show", "schema", "phase.overview", "--format", "markdown"],
    )

    assert result.exit_code == 0
    assert "phase.overview" in result.stdout
    assert "supekku:phase.overview@v1" in result.stdout
    assert "phase_id" in result.stdout

  def test_show_schema_markdown_verification_coverage(self) -> None:
    result = self.runner.invoke(
      app,
      ["show", "schema", "verification.coverage", "--format", "markdown"],
    )

    assert result.exit_code == 0
    assert "verification.coverage" in result.stdout
    assert "supekku:verification.coverage@v1" in result.stdout
    assert "subject_id" in result.stdout
    assert "entries" in result.stdout

  def test_show_schema_markdown_spec_relationships(self) -> None:
    result = self.runner.invoke(
      app,
      ["show", "schema", "spec.relationships", "--format", "markdown"],
    )

    assert result.exit_code == 0
    assert "spec.relationships" in result.stdout
    assert "supekku:spec.relationships@v1" in result.stdout
    assert "spec_id" in result.stdout

  def test_show_schema_markdown_spec_capabilities(self) -> None:
    result = self.runner.invoke(
      app,
      ["show", "schema", "spec.capabilities", "--format", "markdown"],
    )

    assert result.exit_code == 0
    assert "spec.capabilities" in result.stdout
    assert "supekku:spec.capabilities@v1" in result.stdout
    assert "spec_id" in result.stdout
    assert "capabilities" in result.stdout

  def test_show_schema_markdown_revision_change(self) -> None:
    result = self.runner.invoke(
      app,
      ["show", "schema", "revision.change", "--format", "markdown"],
    )

    assert result.exit_code == 0
    assert "revision.change" in result.stdout
    assert "supekku:revision.change@v1" in result.stdout
    assert "revision_id" in result.stdout

  def test_show_schema_json(self) -> None:
    result = self.runner.invoke(
      app,
      ["show", "schema", "delta.relationships", "--format", "json"],
    )

    assert result.exit_code == 0
    assert '"name": "delta.relationships"' in result.stdout
    assert '"marker": "supekku:delta.relationships@v1"' in result.stdout
    assert '"version": 1' in result.stdout

  def test_show_schema_yaml_example(self) -> None:
    result = self.runner.invoke(
      app,
      ["show", "schema", "delta.relationships", "--format", "yaml-example"],
    )

    assert result.exit_code == 0
    assert "```yaml" in result.stdout or "Example:" in result.stdout

  def test_show_unknown_block_type(self) -> None:
    result = self.runner.invoke(
      app,
      ["show", "schema", "nonexistent.block"],
    )

    assert result.exit_code == 1
    assert "Unknown block type" in result.stdout
    assert "nonexistent.block" in result.stdout

  def test_show_unknown_format(self) -> None:
    result = self.runner.invoke(
      app,
      ["show", "schema", "delta.relationships", "--format", "invalid"],
    )

    assert result.exit_code == 1
    assert "Unknown format" in result.stdout

  def test_list_contains_all_expected_schemas(self) -> None:
    result = self.runner.invoke(app, ["list", "schemas"])

    assert result.exit_code == 0

    expected_schemas = [
      "delta.relationships",
      "plan.overview",
      "phase.overview",
      "phase.tracking",
      "verification.coverage",
      "spec.relationships",
      "spec.capabilities",
      "revision.change",
      "workflow.state",
      "workflow.handoff",
      "workflow.review-index",
      "workflow.review-findings",
      "workflow.sessions",
      "workflow.notes-bridge",
      "workflow.phase-bridge",
    ]

    for schema_name in expected_schemas:
      assert schema_name in result.stdout, f"Missing schema: {schema_name}"

  def test_show_format_short_option(self) -> None:
    result = self.runner.invoke(
      app,
      ["show", "schema", "delta.relationships", "-f", "json"],
    )

    assert result.exit_code == 0
    assert '"name": "delta.relationships"' in result.stdout

  def test_list_frontmatter_schemas(self) -> None:
    result = self.runner.invoke(app, ["list", "schemas", "frontmatter"])

    assert result.exit_code == 0
    assert "Available Frontmatter Schemas" in result.stdout
    assert "frontmatter.prod" in result.stdout
    assert "frontmatter.delta" in result.stdout
    assert "frontmatter.spec" in result.stdout

  def test_list_all_schemas(self) -> None:
    result = self.runner.invoke(app, ["list", "schemas"])

    assert result.exit_code == 0
    assert "Available Block Schemas" in result.stdout
    assert "Available Frontmatter Schemas" in result.stdout
    assert "delta.relationships" in result.stdout
    assert "frontmatter.prod" in result.stdout

  def test_show_frontmatter_json_schema(self) -> None:
    result = self.runner.invoke(
      app,
      ["show", "schema", "frontmatter.prod", "--format", "json-schema"],
    )

    assert result.exit_code == 0
    assert "JSON Schema: frontmatter.prod" in result.stdout
    assert '"$schema"' in result.stdout or "$schema" in result.stdout
    assert "properties" in result.stdout
    assert "required" in result.stdout

  def test_show_frontmatter_yaml_example(self) -> None:
    result = self.runner.invoke(
      app,
      ["show", "schema", "frontmatter.delta", "--format", "yaml-example"],
    )

    assert result.exit_code == 0
    assert "Example: frontmatter.delta" in result.stdout
    assert "id:" in result.stdout or "kind:" in result.stdout

  def test_show_all_frontmatter_kinds_json_schema(self) -> None:
    from supekku.scripts.lib.core.frontmatter_metadata import (
      FRONTMATTER_METADATA_REGISTRY,
    )

    for kind in FRONTMATTER_METADATA_REGISTRY:
      result = self.runner.invoke(
        app,
        ["show", "schema", f"frontmatter.{kind}", "--format", "json-schema"],
      )

      assert result.exit_code == 0, f"Failed for frontmatter.{kind}"
      assert f"JSON Schema: frontmatter.{kind}" in result.stdout

  def test_show_all_frontmatter_kinds_yaml_example(self) -> None:
    from supekku.scripts.lib.core.frontmatter_metadata import (
      FRONTMATTER_METADATA_REGISTRY,
    )

    for kind in FRONTMATTER_METADATA_REGISTRY:
      result = self.runner.invoke(
        app,
        ["show", "schema", f"frontmatter.{kind}", "--format", "yaml-example"],
      )

      assert result.exit_code == 0, f"Failed for frontmatter.{kind}"
      assert f"Example: frontmatter.{kind}" in result.stdout

  def test_show_unknown_frontmatter_kind(self) -> None:
    result = self.runner.invoke(
      app,
      ["show", "schema", "frontmatter.nonexistent"],
    )

    assert result.exit_code == 1
    assert "Unknown frontmatter kind" in result.stdout
    assert "nonexistent" in result.stdout

  def test_show_frontmatter_invalid_format(self) -> None:
    result = self.runner.invoke(
      app,
      ["show", "schema", "frontmatter.prod", "--format", "markdown"],
    )

    assert result.exit_code == 1
    assert "Unsupported format for frontmatter" in result.stdout

  def test_list_blocks_only(self) -> None:
    result = self.runner.invoke(app, ["list", "schemas", "blocks"])

    assert result.exit_code == 0
    assert "Available Block Schemas" in result.stdout
    assert "Available Frontmatter Schemas" not in result.stdout


ALL_BLOCK_TYPES = [
  "delta.relationships",
  "plan.overview",
  "phase.overview",
  "phase.tracking",
  "revision.change",
  "verification.coverage",
  "spec.relationships",
  "spec.capabilities",
  "workflow.state",
  "workflow.handoff",
  "workflow.review-index",
  "workflow.review-findings",
  "workflow.sessions",
  "workflow.notes-bridge",
  "workflow.phase-bridge",
]


class AllBlocksJsonSchemaTest(unittest.TestCase):
  """Every registered block type must produce valid JSON Schema."""

  def setUp(self) -> None:
    self.runner = CliRunner()

  def test_all_blocks_json_schema(self) -> None:
    for block_type in ALL_BLOCK_TYPES:
      with self.subTest(block_type=block_type):
        result = self.runner.invoke(
          app,
          ["show", "schema", block_type, "--format", "json-schema"],
        )
        assert result.exit_code == 0, (
          f"json-schema failed for {block_type}: {result.stdout}"
        )
        assert f"JSON Schema: {block_type}" in result.stdout
        assert '"$schema"' in result.stdout or "$schema" in result.stdout
        assert '"properties"' in result.stdout or "properties" in result.stdout


class AllBlocksYamlExampleTest(unittest.TestCase):
  """Every registered block type must produce a YAML example."""

  def setUp(self) -> None:
    self.runner = CliRunner()

  def test_all_blocks_yaml_example(self) -> None:
    for block_type in ALL_BLOCK_TYPES:
      with self.subTest(block_type=block_type):
        result = self.runner.invoke(
          app,
          ["show", "schema", block_type, "--format", "yaml-example"],
        )
        assert result.exit_code == 0, (
          f"yaml-example failed for {block_type}: {result.stdout}"
        )
        assert f"Example: {block_type}" in result.stdout


class EnumIntrospectionTest(unittest.TestCase):
  """Test cases for show schema enums.* commands."""

  def setUp(self) -> None:
    self.runner = CliRunner()

  def test_show_enums_bare_lists_all(self) -> None:
    result = self.runner.invoke(app, ["show", "schema", "enums"])
    assert result.exit_code == 0
    assert "delta.status" in result.stdout
    assert "requirement.status" in result.stdout
    assert "verification.kind" in result.stdout
    assert "verification.status" in result.stdout
    assert "spec.kind" in result.stdout
    assert "requirement.kind" in result.stdout
    assert "command.format" in result.stdout

  def test_show_enums_delta_status(self) -> None:
    result = self.runner.invoke(app, ["show", "schema", "enums.delta.status"])
    assert result.exit_code == 0
    import json

    values = json.loads(result.stdout)
    assert isinstance(values, list)
    assert "draft" in values
    assert "in-progress" in values
    assert "completed" in values
    assert "deferred" in values
    assert "complete" not in values
    assert values == sorted(values)

  def test_show_enums_requirement_status(self) -> None:
    result = self.runner.invoke(app, ["show", "schema", "enums.requirement.status"])
    assert result.exit_code == 0
    import json

    values = json.loads(result.stdout)
    assert "pending" in values
    assert "active" in values
    assert "in-progress" in values
    assert "retired" in values
    assert values == sorted(values)

  def test_show_enums_verification_status(self) -> None:
    result = self.runner.invoke(app, ["show", "schema", "enums.verification.status"])
    assert result.exit_code == 0
    import json

    values = json.loads(result.stdout)
    assert "planned" in values
    assert "verified" in values
    assert "failed" in values
    assert "blocked" in values
    assert values == sorted(values)

  def test_show_enums_verification_kind(self) -> None:
    result = self.runner.invoke(app, ["show", "schema", "enums.verification.kind"])
    assert result.exit_code == 0
    import json

    values = json.loads(result.stdout)
    assert values == ["VA", "VH", "VT"]

  def test_show_enums_spec_kind(self) -> None:
    result = self.runner.invoke(app, ["show", "schema", "enums.spec.kind"])
    assert result.exit_code == 0
    import json

    values = json.loads(result.stdout)
    assert values == ["prod", "tech"]

  def test_show_enums_requirement_kind(self) -> None:
    result = self.runner.invoke(app, ["show", "schema", "enums.requirement.kind"])
    assert result.exit_code == 0
    import json

    values = json.loads(result.stdout)
    assert values == ["FR", "NF"]

  def test_show_enums_command_format(self) -> None:
    result = self.runner.invoke(app, ["show", "schema", "enums.command.format"])
    assert result.exit_code == 0
    import json

    values = json.loads(result.stdout)
    assert values == ["json", "table", "tsv"]

  def test_show_enums_invalid_path(self) -> None:
    result = self.runner.invoke(app, ["show", "schema", "enums.nonexistent.field"])
    assert result.exit_code == 1
    assert "Unknown enum" in result.stdout
    assert "delta.status" in result.stdout

  def test_show_enums_values_match_lifecycle_constants(self) -> None:
    import json

    from supekku.scripts.lib.blocks.verification import (
      VALID_KINDS as VER_KINDS,
    )
    from supekku.scripts.lib.blocks.verification import (
      VALID_STATUSES as VER_STATUSES,
    )
    from supekku.scripts.lib.changes.lifecycle import (
      VALID_STATUSES as CHANGE_STATUSES,
    )
    from supekku.scripts.lib.requirements.lifecycle import (
      VALID_STATUSES as REQ_STATUSES,
    )

    result = self.runner.invoke(app, ["show", "schema", "enums.delta.status"])
    delta_values = set(json.loads(result.stdout))
    assert delta_values <= CHANGE_STATUSES

    result = self.runner.invoke(app, ["show", "schema", "enums.requirement.status"])
    req_values = set(json.loads(result.stdout))
    assert req_values == REQ_STATUSES

    result = self.runner.invoke(app, ["show", "schema", "enums.verification.status"])
    ver_status_values = set(json.loads(result.stdout))
    assert ver_status_values == VER_STATUSES

    result = self.runner.invoke(app, ["show", "schema", "enums.verification.kind"])
    ver_kind_values = set(json.loads(result.stdout))
    assert ver_kind_values == VER_KINDS


if __name__ == "__main__":
  unittest.main()
