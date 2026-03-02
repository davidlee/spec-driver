"""Tests for workflow config loading."""

from __future__ import annotations

from pathlib import Path

import pytest

from supekku.scripts.lib.core.config import (
  DEFAULT_CONFIG,
  load_workflow_config,
)
from supekku.scripts.lib.core.paths import SPEC_DRIVER_DIR


def test_missing_file_returns_defaults(tmp_path: Path) -> None:
  """When workflow.toml is absent, return full defaults without error."""
  config = load_workflow_config(tmp_path)
  assert config == DEFAULT_CONFIG


def test_partial_config_fills_missing_sections(tmp_path: Path) -> None:
  """Sections not present in the TOML are filled with defaults."""
  toml_path = tmp_path / SPEC_DRIVER_DIR / "workflow.toml"
  toml_path.parent.mkdir(parents=True)
  toml_path.write_text('ceremony = "town_planner"\n', encoding="utf-8")

  config = load_workflow_config(tmp_path)

  assert config["ceremony"] == "town_planner"
  # Missing sections should have defaults
  assert config["cards"] == DEFAULT_CONFIG["cards"]
  assert config["policy"] == DEFAULT_CONFIG["policy"]
  assert config["contracts"] == DEFAULT_CONFIG["contracts"]
  assert config["tool"] == DEFAULT_CONFIG["tool"]


def test_partial_section_fills_missing_keys(tmp_path: Path) -> None:
  """Keys not present in a section are filled with defaults."""
  toml_path = tmp_path / SPEC_DRIVER_DIR / "workflow.toml"
  toml_path.parent.mkdir(parents=True)
  toml_path.write_text(
    "[cards]\nenabled = false\n",
    encoding="utf-8",
  )

  config = load_workflow_config(tmp_path)

  assert config["cards"]["enabled"] is False
  assert config["cards"]["root"] == DEFAULT_CONFIG["cards"]["root"]
  assert config["cards"]["lanes"] == DEFAULT_CONFIG["cards"]["lanes"]


def test_full_config_values_preserved(tmp_path: Path) -> None:
  """A complete config file preserves all values."""
  toml_content = """\
ceremony = "settler"

[tool]
exec = "npx"

[verification]
command = "make test"

[cards]
enabled = false
root = "tasks"
lanes = ["todo", "doing", "done"]
id_prefix = "TSK"

[docs]
artefacts_root = "docs/design"
plans_root = "docs/plans"

[policy]
adrs = false
policies = true
standards = true

[contracts]
enabled = false
root = "api-contracts"

[bootstrap]
doctrine_path = "custom/doctrine.md"

[authoring]
engine = "spec_driver"

[integration]
agents_md = false
claude_md = false
"""
  toml_path = tmp_path / SPEC_DRIVER_DIR / "workflow.toml"
  toml_path.parent.mkdir(parents=True)
  toml_path.write_text(toml_content, encoding="utf-8")

  config = load_workflow_config(tmp_path)

  assert config["ceremony"] == "settler"
  assert config["tool"]["exec"] == "npx"
  assert config["verification"]["command"] == "make test"
  assert config["cards"]["enabled"] is False
  assert config["cards"]["root"] == "tasks"
  assert config["cards"]["lanes"] == ["todo", "doing", "done"]
  assert config["cards"]["id_prefix"] == "TSK"
  assert config["docs"]["artefacts_root"] == "docs/design"
  assert config["policy"]["policies"] is True
  assert config["contracts"]["root"] == "api-contracts"
  assert config["bootstrap"]["doctrine_path"] == "custom/doctrine.md"
  assert config["authoring"]["engine"] == "spec_driver"
  assert config["integration"]["agents_md"] is False


def test_invalid_toml_warns_and_returns_defaults(
  tmp_path: Path,
) -> None:
  """Malformed TOML triggers a warning and returns defaults."""
  toml_path = tmp_path / SPEC_DRIVER_DIR / "workflow.toml"
  toml_path.parent.mkdir(parents=True)
  toml_path.write_text("this is [not valid toml ===", encoding="utf-8")

  with pytest.warns(UserWarning, match="workflow.toml"):
    config = load_workflow_config(tmp_path)

  assert config == DEFAULT_CONFIG


def test_defaults_have_expected_structure() -> None:
  """DEFAULT_CONFIG has all expected top-level keys and section shapes."""
  assert DEFAULT_CONFIG["ceremony"] == "pioneer"
  assert isinstance(DEFAULT_CONFIG["tool"], dict)
  assert isinstance(DEFAULT_CONFIG["cards"], dict)
  assert isinstance(DEFAULT_CONFIG["docs"], dict)
  assert isinstance(DEFAULT_CONFIG["policy"], dict)
  assert isinstance(DEFAULT_CONFIG["contracts"], dict)
  assert isinstance(DEFAULT_CONFIG["bootstrap"], dict)
  assert isinstance(DEFAULT_CONFIG["authoring"], dict)
  assert isinstance(DEFAULT_CONFIG["verification"], dict)
  assert isinstance(DEFAULT_CONFIG["integration"], dict)
