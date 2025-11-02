"""Tests for schema CLI commands."""

from __future__ import annotations

import unittest

from typer.testing import CliRunner

from supekku.cli.schema import app


class SchemaCommandsTest(unittest.TestCase):
  """Test cases for schema CLI commands."""

  def setUp(self) -> None:
    """Set up test environment."""
    self.runner = CliRunner()

  def test_list_schemas(self) -> None:
    """Test listing all schemas."""
    result = self.runner.invoke(app, ["list"])

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
    """Test showing delta.relationships schema in markdown format."""
    result = self.runner.invoke(
      app,
      ["show", "delta.relationships", "--format", "markdown"],
    )

    assert result.exit_code == 0
    assert "delta.relationships" in result.stdout
    assert "supekku:delta.relationships@v1" in result.stdout
    assert "delta_id" in result.stdout
    assert "primary_specs" in result.stdout

  def test_show_schema_markdown_plan_overview(self) -> None:
    """Test showing plan.overview schema in markdown format."""
    result = self.runner.invoke(
      app,
      ["show", "plan.overview", "--format", "markdown"],
    )

    assert result.exit_code == 0
    assert "plan.overview" in result.stdout
    assert "supekku:plan.overview@v1" in result.stdout
    assert "plan_id" in result.stdout
    assert "delta_id" in result.stdout

  def test_show_schema_markdown_phase_overview(self) -> None:
    """Test showing phase.overview schema in markdown format."""
    result = self.runner.invoke(
      app,
      ["show", "phase.overview", "--format", "markdown"],
    )

    assert result.exit_code == 0
    assert "phase.overview" in result.stdout
    assert "supekku:phase.overview@v1" in result.stdout
    assert "phase_id" in result.stdout

  def test_show_schema_markdown_verification_coverage(self) -> None:
    """Test showing verification.coverage schema in markdown format."""
    result = self.runner.invoke(
      app,
      ["show", "verification.coverage", "--format", "markdown"],
    )

    assert result.exit_code == 0
    assert "verification.coverage" in result.stdout
    assert "supekku:verification.coverage@v1" in result.stdout
    assert "subject_id" in result.stdout
    assert "entries" in result.stdout

  def test_show_schema_markdown_spec_relationships(self) -> None:
    """Test showing spec.relationships schema in markdown format."""
    result = self.runner.invoke(
      app,
      ["show", "spec.relationships", "--format", "markdown"],
    )

    assert result.exit_code == 0
    assert "spec.relationships" in result.stdout
    assert "supekku:spec.relationships@v1" in result.stdout
    assert "spec_id" in result.stdout

  def test_show_schema_markdown_spec_capabilities(self) -> None:
    """Test showing spec.capabilities schema in markdown format."""
    result = self.runner.invoke(
      app,
      ["show", "spec.capabilities", "--format", "markdown"],
    )

    assert result.exit_code == 0
    assert "spec.capabilities" in result.stdout
    assert "supekku:spec.capabilities@v1" in result.stdout
    assert "spec_id" in result.stdout
    assert "capabilities" in result.stdout

  def test_show_schema_markdown_revision_change(self) -> None:
    """Test showing revision.change schema in markdown format."""
    result = self.runner.invoke(
      app,
      ["show", "revision.change", "--format", "markdown"],
    )

    assert result.exit_code == 0
    assert "revision.change" in result.stdout
    assert "supekku:revision.change@v1" in result.stdout
    assert "revision_id" in result.stdout

  def test_show_schema_json(self) -> None:
    """Test showing schema in JSON format."""
    result = self.runner.invoke(
      app,
      ["show", "delta.relationships", "--format", "json"],
    )

    assert result.exit_code == 0
    assert '"name": "delta.relationships"' in result.stdout
    assert '"marker": "supekku:delta.relationships@v1"' in result.stdout
    assert '"version": 1' in result.stdout

  def test_show_schema_yaml_example(self) -> None:
    """Test showing schema as YAML example."""
    result = self.runner.invoke(
      app,
      ["show", "delta.relationships", "--format", "yaml-example"],
    )

    assert result.exit_code == 0
    # Should contain YAML block markers
    assert "```yaml" in result.stdout or "Example:" in result.stdout

  def test_show_unknown_block_type(self) -> None:
    """Test error for unknown block type."""
    result = self.runner.invoke(
      app,
      ["show", "nonexistent.block"],
    )

    assert result.exit_code == 1
    assert "Unknown block type" in result.stdout
    assert "nonexistent.block" in result.stdout

  def test_show_unknown_format(self) -> None:
    """Test error for unknown format type."""
    result = self.runner.invoke(
      app,
      ["show", "delta.relationships", "--format", "invalid"],
    )

    assert result.exit_code == 1
    assert "Unknown format" in result.stdout

  def test_list_contains_all_expected_schemas(self) -> None:
    """Test that list contains all 7 expected schemas."""
    result = self.runner.invoke(app, ["list"])

    assert result.exit_code == 0

    # Count occurrences - each schema should appear once
    expected_schemas = [
      "delta.relationships",
      "plan.overview",
      "phase.overview",
      "verification.coverage",
      "spec.relationships",
      "spec.capabilities",
      "revision.change",
    ]

    for schema in expected_schemas:
      assert schema in result.stdout, f"Missing schema: {schema}"

  def test_show_format_short_option(self) -> None:
    """Test using -f short option for format."""
    result = self.runner.invoke(
      app,
      ["show", "delta.relationships", "-f", "json"],
    )

    assert result.exit_code == 0
    assert '"name": "delta.relationships"' in result.stdout

  def test_list_frontmatter_schemas(self) -> None:
    """Test listing only frontmatter schemas."""
    result = self.runner.invoke(app, ["list", "frontmatter"])

    assert result.exit_code == 0
    assert "Available Frontmatter Schemas" in result.stdout
    assert "frontmatter.prod" in result.stdout
    assert "frontmatter.delta" in result.stdout
    assert "frontmatter.spec" in result.stdout

  def test_list_all_schemas(self) -> None:
    """Test listing both block and frontmatter schemas."""
    result = self.runner.invoke(app, ["list"])

    assert result.exit_code == 0
    assert "Available Block Schemas" in result.stdout
    assert "Available Frontmatter Schemas" in result.stdout
    assert "delta.relationships" in result.stdout
    assert "frontmatter.prod" in result.stdout

  def test_show_frontmatter_json_schema(self) -> None:
    """Test showing frontmatter prod schema as JSON Schema."""
    result = self.runner.invoke(
      app,
      ["show", "frontmatter.prod", "--format", "json-schema"],
    )

    assert result.exit_code == 0
    assert "JSON Schema: frontmatter.prod" in result.stdout
    # Check for JSON Schema standard fields
    assert '"$schema"' in result.stdout or "$schema" in result.stdout
    assert "properties" in result.stdout
    assert "required" in result.stdout

  def test_show_frontmatter_yaml_example(self) -> None:
    """Test showing frontmatter delta schema as YAML example."""
    result = self.runner.invoke(
      app,
      ["show", "frontmatter.delta", "--format", "yaml-example"],
    )

    assert result.exit_code == 0
    assert "Example: frontmatter.delta" in result.stdout
    # Should contain YAML content
    assert "id:" in result.stdout or "kind:" in result.stdout

  def test_show_all_frontmatter_kinds_json_schema(self) -> None:
    """Test that all frontmatter kinds can be shown as JSON Schema."""
    from supekku.scripts.lib.core.frontmatter_metadata import (
      FRONTMATTER_METADATA_REGISTRY,
    )

    for kind in FRONTMATTER_METADATA_REGISTRY:
      result = self.runner.invoke(
        app,
        ["show", f"frontmatter.{kind}", "--format", "json-schema"],
      )

      assert result.exit_code == 0, f"Failed for frontmatter.{kind}"
      assert f"JSON Schema: frontmatter.{kind}" in result.stdout

  def test_show_all_frontmatter_kinds_yaml_example(self) -> None:
    """Test that all frontmatter kinds can be shown as YAML example."""
    from supekku.scripts.lib.core.frontmatter_metadata import (
      FRONTMATTER_METADATA_REGISTRY,
    )

    for kind in FRONTMATTER_METADATA_REGISTRY:
      result = self.runner.invoke(
        app,
        ["show", f"frontmatter.{kind}", "--format", "yaml-example"],
      )

      assert result.exit_code == 0, f"Failed for frontmatter.{kind}"
      assert f"Example: frontmatter.{kind}" in result.stdout

  def test_show_unknown_frontmatter_kind(self) -> None:
    """Test error for unknown frontmatter kind."""
    result = self.runner.invoke(
      app,
      ["show", "frontmatter.nonexistent"],
    )

    assert result.exit_code == 1
    assert "Unknown frontmatter kind" in result.stdout
    assert "nonexistent" in result.stdout

  def test_show_frontmatter_invalid_format(self) -> None:
    """Test error for invalid format with frontmatter."""
    result = self.runner.invoke(
      app,
      ["show", "frontmatter.prod", "--format", "markdown"],
    )

    assert result.exit_code == 1
    assert "Unsupported format for frontmatter" in result.stdout

  def test_list_blocks_only(self) -> None:
    """Test listing only block schemas."""
    result = self.runner.invoke(app, ["list", "blocks"])

    assert result.exit_code == 0
    assert "Available Block Schemas" in result.stdout
    # Should not contain frontmatter table
    assert "Available Frontmatter Schemas" not in result.stdout


if __name__ == "__main__":
  unittest.main()
