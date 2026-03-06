"""Tests for workflow config loading."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from supekku.scripts.lib.core.config import (
  DEFAULT_CONFIG,
  _is_project_dependency,
  detect_exec_command,
  is_strict_mode,
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
  assert isinstance(DEFAULT_CONFIG["dirs"], dict)


# --- [dirs] config tests ---


def test_dirs_defaults_match_path_constants() -> None:
  """[dirs] defaults must mirror the constants in paths.py."""
  dirs = DEFAULT_CONFIG["dirs"]
  # Grouping keys (specs, changes) removed in DE-049
  assert "specs" not in dirs
  assert "changes" not in dirs
  assert dirs["backlog"] == "backlog"
  assert dirs["memory"] == "memory"
  assert dirs["tech_specs"] == "tech"
  assert dirs["product_specs"] == "product"
  assert dirs["decisions"] == "decisions"
  assert dirs["policies"] == "policies"
  assert dirs["standards"] == "standards"
  assert dirs["deltas"] == "deltas"
  assert dirs["revisions"] == "revisions"
  assert dirs["audits"] == "audits"
  assert dirs["issues"] == "issues"
  assert dirs["problems"] == "problems"
  assert dirs["improvements"] == "improvements"
  assert dirs["risks"] == "risks"


def test_dirs_partial_override_merges_with_defaults(tmp_path: Path) -> None:
  """Partial [dirs] overrides merge with defaults for missing keys."""
  toml_path = tmp_path / SPEC_DRIVER_DIR / "workflow.toml"
  toml_path.parent.mkdir(parents=True)
  toml_path.write_text(
    '[dirs]\ndeltas = "patches"\nmemory = "knowledge"\n',
    encoding="utf-8",
  )

  config = load_workflow_config(tmp_path)

  assert config["dirs"]["deltas"] == "patches"
  assert config["dirs"]["memory"] == "knowledge"
  # Non-overridden keys retain defaults
  assert config["dirs"]["backlog"] == "backlog"
  assert config["dirs"]["audits"] == "audits"


def test_dirs_missing_section_uses_defaults(tmp_path: Path) -> None:
  """Missing [dirs] section yields all defaults."""
  toml_path = tmp_path / SPEC_DRIVER_DIR / "workflow.toml"
  toml_path.parent.mkdir(parents=True)
  toml_path.write_text('ceremony = "settler"\n', encoding="utf-8")

  config = load_workflow_config(tmp_path)

  assert config["dirs"] == DEFAULT_CONFIG["dirs"]


# --- extra user keys ---


def test_extra_user_keys_preserved(tmp_path: Path) -> None:
  """User keys not in DEFAULT_CONFIG are passed through."""
  toml_path = tmp_path / SPEC_DRIVER_DIR / "workflow.toml"
  toml_path.parent.mkdir(parents=True)
  toml_path.write_text(
    'spec_driver_installed_version = "1.2.3"\nceremony = "settler"\n',
    encoding="utf-8",
  )
  config = load_workflow_config(tmp_path)
  assert config["spec_driver_installed_version"] == "1.2.3"
  assert config["ceremony"] == "settler"


# --- strict_mode config tests ---


def test_strict_mode_defaults_to_false() -> None:
  """strict_mode must default to False in DEFAULT_CONFIG."""
  assert DEFAULT_CONFIG["strict_mode"] is False


def test_strict_mode_false_when_toml_absent(tmp_path: Path) -> None:
  """Missing workflow.toml should yield strict_mode=False."""
  config = load_workflow_config(tmp_path)
  assert config["strict_mode"] is False


def test_strict_mode_true_loads_from_toml(tmp_path: Path) -> None:
  """strict_mode=true in workflow.toml is loaded correctly."""
  toml_path = tmp_path / SPEC_DRIVER_DIR / "workflow.toml"
  toml_path.parent.mkdir(parents=True)
  toml_path.write_text("strict_mode = true\n", encoding="utf-8")

  config = load_workflow_config(tmp_path)
  assert config["strict_mode"] is True


def test_strict_mode_false_loads_from_toml(tmp_path: Path) -> None:
  """Explicit strict_mode=false in workflow.toml is respected."""
  toml_path = tmp_path / SPEC_DRIVER_DIR / "workflow.toml"
  toml_path.parent.mkdir(parents=True)
  toml_path.write_text("strict_mode = false\n", encoding="utf-8")

  config = load_workflow_config(tmp_path)
  assert config["strict_mode"] is False


def test_is_strict_mode_returns_true_when_enabled() -> None:
  """is_strict_mode() returns True when strict_mode=true in config."""
  assert is_strict_mode({"strict_mode": True}) is True


def test_is_strict_mode_returns_false_when_disabled() -> None:
  """is_strict_mode() returns False when strict_mode=false in config."""
  assert is_strict_mode({"strict_mode": False}) is False


def test_is_strict_mode_returns_false_when_key_missing() -> None:
  """is_strict_mode() returns False when strict_mode key is absent."""
  assert is_strict_mode({}) is False


# --- exec detection tests ---


class TestIsProjectDependency:
  """Tests for _is_project_dependency."""

  def test_no_pyproject(self, tmp_path: Path) -> None:
    """Returns False when pyproject.toml is absent."""
    assert _is_project_dependency(tmp_path) is False

  def test_project_dependency(self, tmp_path: Path) -> None:
    """Detects spec-driver in [project.dependencies]."""
    (tmp_path / "pyproject.toml").write_text(
      '[project]\ndependencies = ["spec-driver>=0.6"]\n',
      encoding="utf-8",
    )
    assert _is_project_dependency(tmp_path) is True

  def test_dependency_group(self, tmp_path: Path) -> None:
    """Detects spec-driver in [dependency-groups]."""
    (tmp_path / "pyproject.toml").write_text(
      '[dependency-groups]\ndev = ["spec-driver>=0.6"]\n',
      encoding="utf-8",
    )
    assert _is_project_dependency(tmp_path) is True

  def test_unrelated_project(self, tmp_path: Path) -> None:
    """Returns False when spec-driver is not a dependency."""
    (tmp_path / "pyproject.toml").write_text(
      '[project]\ndependencies = ["requests"]\n',
      encoding="utf-8",
    )
    assert _is_project_dependency(tmp_path) is False

  def test_tool_uv_dev_dependencies(self, tmp_path: Path) -> None:
    """Detects spec-driver in [tool.uv.dev-dependencies]."""
    (tmp_path / "pyproject.toml").write_text(
      '[tool.uv]\ndev-dependencies = ["spec-driver"]\n',
      encoding="utf-8",
    )
    assert _is_project_dependency(tmp_path) is True

  def test_uv_toml_dev_dependencies(self, tmp_path: Path) -> None:
    """Detects spec-driver in uv.toml dev-dependencies."""
    (tmp_path / "uv.toml").write_text(
      'dev-dependencies = ["spec-driver>=0.6"]\n',
      encoding="utf-8",
    )
    assert _is_project_dependency(tmp_path) is True

  def test_venv_binary_exists(self, tmp_path: Path) -> None:
    """Detects .venv/bin/spec-driver as strongest signal."""
    venv_bin = tmp_path / ".venv" / "bin"
    venv_bin.mkdir(parents=True)
    binary = venv_bin / "spec-driver"
    binary.write_text("#!/bin/sh\n")
    binary.chmod(0o755)
    assert _is_project_dependency(tmp_path) is True

  def test_invalid_toml(self, tmp_path: Path) -> None:
    """Returns False on malformed pyproject.toml."""
    (tmp_path / "pyproject.toml").write_text("[[invalid", encoding="utf-8")
    assert _is_project_dependency(tmp_path) is False


class TestDetectExecCommand:
  """Tests for detect_exec_command."""

  def test_project_dep_with_uv(self, tmp_path: Path) -> None:
    """Project dependency + uv available → uv run."""
    (tmp_path / "pyproject.toml").write_text(
      '[project]\ndependencies = ["spec-driver"]\n',
      encoding="utf-8",
    )
    with patch("supekku.scripts.lib.core.config.which", return_value="/usr/bin/uv"):
      assert detect_exec_command(tmp_path) == "uv run spec-driver"

  def test_global_install(self, tmp_path: Path) -> None:
    """Binary in permanent location, no project dep → bare command."""
    with patch("sys.argv", ["/usr/local/bin/spec-driver", "install"]):
      assert detect_exec_command(tmp_path) == "spec-driver"

  def test_uvx_fallback(self, tmp_path: Path) -> None:
    """Transient binary + uvx available → uvx."""
    with (
      patch("sys.argv", ["/home/u/.cache/uv/tool/spec-driver", "install"]),
      patch(
        "supekku.scripts.lib.core.config.which",
        side_effect=lambda cmd: "/usr/bin/uvx" if cmd == "uvx" else None,
      ),
    ):
      assert detect_exec_command(tmp_path) == "uvx spec-driver"

  def test_nix_store_is_global(self, tmp_path: Path) -> None:
    """Binary in /nix/store/ is a permanent global install."""
    with patch("sys.argv", ["/nix/store/abc123/bin/spec-driver", "install"]):
      assert detect_exec_command(tmp_path) == "spec-driver"

  def test_venv_without_uvx_falls_back(self, tmp_path: Path) -> None:
    """Transient binary, no uvx → bare command as last resort."""
    with (
      patch("sys.argv", ["/proj/.venv/bin/spec-driver", "install"]),
      patch("supekku.scripts.lib.core.config.which", return_value=None),
    ):
      assert detect_exec_command(tmp_path) == "spec-driver"
