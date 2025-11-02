"""Tests for show CLI commands."""

from __future__ import annotations

import json
import unittest

from typer.testing import CliRunner

from supekku.cli.show import app


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


if __name__ == "__main__":
  unittest.main()
