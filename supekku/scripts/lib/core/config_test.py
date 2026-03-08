"""Tests for workflow config loading."""

from __future__ import annotations

import tomllib
from pathlib import Path
from unittest.mock import patch

import pytest

from supekku.scripts.lib.core.config import (
  DEFAULT_CONFIG,
  _is_project_dependency,
  detect_exec_command,
  generate_default_workflow_toml,
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
  assert config["kanban"] == DEFAULT_CONFIG["kanban"]
  assert config["policy"] == DEFAULT_CONFIG["policy"]
  assert config["contracts"] == DEFAULT_CONFIG["contracts"]
  assert config["tool"] == DEFAULT_CONFIG["tool"]


def test_partial_section_fills_missing_keys(tmp_path: Path) -> None:
  """Keys not present in a section are filled with defaults."""
  toml_path = tmp_path / SPEC_DRIVER_DIR / "workflow.toml"
  toml_path.parent.mkdir(parents=True)
  toml_path.write_text(
    "[kanban]\nenabled = false\n",
    encoding="utf-8",
  )

  config = load_workflow_config(tmp_path)

  assert config["kanban"]["enabled"] is False
  assert config["kanban"]["root"] == DEFAULT_CONFIG["kanban"]["root"]
  assert config["kanban"]["lanes"] == DEFAULT_CONFIG["kanban"]["lanes"]


def test_full_config_values_preserved(tmp_path: Path) -> None:
  """A complete config file preserves all values."""
  toml_content = """\
ceremony = "settler"

[tool]
exec = "npx"

[verification]
command = "make test"

[kanban]
enabled = false
root = "tasks"
lanes = ["todo", "doing", "done"]
id_prefix = "TSK"
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
  assert config["kanban"]["enabled"] is False
  assert config["kanban"]["root"] == "tasks"
  assert config["kanban"]["lanes"] == ["todo", "doing", "done"]
  assert config["kanban"]["id_prefix"] == "TSK"
  assert config["kanban"]["artefacts_root"] == "docs/design"
  assert config["kanban"]["plans_root"] == "docs/plans"
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
  assert DEFAULT_CONFIG["ceremony"] == "town_planner"
  assert isinstance(DEFAULT_CONFIG["tool"], dict)
  assert isinstance(DEFAULT_CONFIG["kanban"], dict)
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


# --- legacy [cards]/[docs] migration ---


def test_legacy_cards_migrated_to_kanban(tmp_path: Path) -> None:
  """Legacy [cards] section is migrated to [kanban]."""
  toml_path = tmp_path / SPEC_DRIVER_DIR / "workflow.toml"
  toml_path.parent.mkdir(parents=True)
  toml_path.write_text(
    '[cards]\nenabled = false\nroot = "tasks"\n',
    encoding="utf-8",
  )

  config = load_workflow_config(tmp_path)

  assert "cards" not in config
  assert config["kanban"]["enabled"] is False
  assert config["kanban"]["root"] == "tasks"
  # Defaults filled for keys not in legacy section
  expected = DEFAULT_CONFIG["kanban"]["artefacts_root"]
  assert config["kanban"]["artefacts_root"] == expected


def test_legacy_docs_merged_into_kanban(tmp_path: Path) -> None:
  """Legacy [docs] section is merged into [kanban]."""
  toml_path = tmp_path / SPEC_DRIVER_DIR / "workflow.toml"
  toml_path.parent.mkdir(parents=True)
  toml_path.write_text(
    '[docs]\nartefacts_root = "my/artefacts"\nplans_root = "my/plans"\n',
    encoding="utf-8",
  )

  config = load_workflow_config(tmp_path)

  assert "docs" not in config
  assert config["kanban"]["artefacts_root"] == "my/artefacts"
  assert config["kanban"]["plans_root"] == "my/plans"
  # Kanban defaults filled
  assert config["kanban"]["enabled"] is False


def test_legacy_cards_and_docs_both_migrate(tmp_path: Path) -> None:
  """Legacy [cards] + [docs] both merge into [kanban]."""
  toml_path = tmp_path / SPEC_DRIVER_DIR / "workflow.toml"
  toml_path.parent.mkdir(parents=True)
  toml_path.write_text(
    '[cards]\nenabled = false\nid_prefix = "X"\n\n'
    '[docs]\nartefacts_root = "custom/art"\n',
    encoding="utf-8",
  )

  config = load_workflow_config(tmp_path)

  assert "cards" not in config
  assert "docs" not in config
  assert config["kanban"]["enabled"] is False
  assert config["kanban"]["id_prefix"] == "X"
  assert config["kanban"]["artefacts_root"] == "custom/art"


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


# --- generate_default_workflow_toml tests ---


class TestGenerateDefaultWorkflowToml:
  """Tests for the default workflow.toml template generator."""

  def test_contains_all_default_config_keys(self) -> None:
    """Every key in DEFAULT_CONFIG appears in the generated template."""
    template = generate_default_workflow_toml()
    for key, val in DEFAULT_CONFIG.items():
      if isinstance(val, dict):
        assert f"[{key}]" in template, f"missing section [{key}]"
        for sub_key in val:
          assert sub_key in template, f"missing key {key}.{sub_key}"
      else:
        assert key in template, f"missing top-level key {key}"

  def test_uncommented_is_valid_toml(self) -> None:
    """Stripping single-# config comments yields valid TOML.

    Prose comments use ## and stay as TOML comments when config lines
    (single #) are uncommented.
    """
    template = generate_default_workflow_toml()
    uncommented_lines = []
    for line in template.splitlines():
      if line.startswith("## ") or line == "##":
        # Prose comment — keep as TOML comment
        uncommented_lines.append(line)
      elif line.startswith("# "):
        uncommented_lines.append(line[2:])
      else:
        uncommented_lines.append(line)
    toml_text = "\n".join(uncommented_lines)
    parsed = tomllib.loads(toml_text)
    # Verify a sample of parsed values match defaults
    assert parsed["ceremony"] == "town_planner"
    assert parsed["kanban"]["enabled"] is False
    assert parsed["dirs"]["memory"] == "memory"

  def test_tool_section_is_uncommented(self) -> None:
    """The [tool] section is active (not commented) since exec is install-specific."""
    template = generate_default_workflow_toml("custom-cmd")
    assert "[tool]" in template
    assert "# [tool]" not in template
    assert 'exec = "custom-cmd"' in template

  def test_exec_cmd_substitution(self) -> None:
    """The exec_cmd argument is used in the [tool] section."""
    template = generate_default_workflow_toml("uvx spec-driver")
    assert 'exec = "uvx spec-driver"' in template

  def test_other_sections_are_commented(self) -> None:
    """All sections except [tool] are commented out with single #."""
    template = generate_default_workflow_toml()
    for key, val in DEFAULT_CONFIG.items():
      if key == "tool" or not isinstance(val, dict):
        continue
      # Section header should be commented with single #
      assert f"# [{key}]" in template, f"[{key}] should be commented"

  def test_has_explanatory_comments(self) -> None:
    """Template includes human-readable prose comments (## prefix)."""
    template = generate_default_workflow_toml()
    # Check a few signature phrases from _SECTION_COMMENTS
    assert "## Ceremony mode" in template
    assert "governance posture" in template
    assert "## Kanban-style" in template
    assert "## Generated API contracts" in template

  def test_roundtrip_through_load(self, tmp_path: Path) -> None:
    """Generated template loads correctly and yields expected config."""
    template = generate_default_workflow_toml("test-cmd")
    toml_path = tmp_path / SPEC_DRIVER_DIR / "workflow.toml"
    toml_path.parent.mkdir(parents=True)
    toml_path.write_text(template, encoding="utf-8")
    config = load_workflow_config(tmp_path)
    # Only [tool] is active, so only exec should differ from defaults
    assert config["tool"]["exec"] == "test-cmd"
    assert config["ceremony"] == DEFAULT_CONFIG["ceremony"]
    assert config["kanban"] == DEFAULT_CONFIG["kanban"]


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
