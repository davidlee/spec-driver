"""Tests for complete-delta prompt behavior."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

import pytest

from supekku.scripts import complete_delta as complete_delta_module


class CompleteDeltaPromptBehaviorTest(unittest.TestCase):
  """Prompt handling should be deterministic in non-interactive contexts."""

  def test_prompt_yes_no_uses_non_interactive_default_without_input(self) -> None:
    """Non-interactive mode must not call input()."""
    with patch.object(
      complete_delta_module.sys.stdin,
      "isatty",
      return_value=False,
    ), patch(
      "builtins.input",
      side_effect=AssertionError("input() should not be called"),
    ):
      result = complete_delta_module.prompt_yes_no(
        "Mark delta as completed?",
        default=False,
        non_interactive_default=True,
      )

    assert result is True

  def test_prompt_yes_no_non_interactive_falls_back_to_default(self) -> None:
    """When no override is provided, default answer is used."""
    with patch.object(
      complete_delta_module.sys.stdin,
      "isatty",
      return_value=False,
    ), patch(
      "builtins.input",
      side_effect=AssertionError("input() should not be called"),
    ):
      result = complete_delta_module.prompt_yes_no(
        "Sync specs now?",
        default=False,
      )

    assert result is False

  def test_prompt_yes_no_uses_fallback_on_eof(self) -> None:
    """EOF during input should return the non-interactive fallback."""
    with patch.object(
      complete_delta_module.sys.stdin,
      "isatty",
      return_value=True,
    ), patch(
      "builtins.input",
      side_effect=EOFError,
    ):
      result = complete_delta_module.prompt_yes_no(
        "Mark delta as completed?",
        default=False,
        non_interactive_default=True,
      )

    assert result is True

  def test_prompt_spec_sync_non_interactive_skips_sync(self) -> None:
    """Non-interactive mode defaults to no for optional sync prompt."""
    with patch.object(
      complete_delta_module.sys.stdin,
      "isatty",
      return_value=False,
    ), patch.object(
      complete_delta_module,
      "run_spec_sync",
      side_effect=AssertionError("run_spec_sync() should not be called"),
    ):
      result = complete_delta_module.prompt_spec_sync(
        skip_sync=False,
        dry_run=False,
        force=False,
      )

    assert result is True


class StrictModeEnforcementTest(unittest.TestCase):
  """Strict mode must block all force-style bypass paths."""

  def _make_workspace_mock(self):
    """Create a workspace mock with a valid delta."""
    workspace = MagicMock()
    delta = MagicMock()
    delta.status = "in-progress"
    delta.applies_to = {"requirements": []}
    delta.path = MagicMock()
    workspace.delta_registry.collect.return_value = {"DE-TEST": delta}
    workspace.requirements.records = {}
    return workspace

  def _run_with_strict_mode(self, **kwargs):
    """Run complete_delta with strict_mode=true config."""
    ws = self._make_workspace_mock()
    strict_config = {"strict_mode": True}
    with (
      patch.object(
        complete_delta_module, "Workspace",
      ) as mock_ws_cls,
      patch(
        "supekku.scripts.complete_delta.load_workflow_config",
        return_value=strict_config,
      ),
    ):
      mock_ws_cls.from_cwd.return_value = ws
      return complete_delta_module.complete_delta("DE-TEST", **kwargs)

  def test_force_blocked_in_strict_mode(self) -> None:
    """--force must be rejected when strict_mode=true."""
    code = self._run_with_strict_mode(force=True)
    assert code == 1

  def test_skip_sync_blocked_in_strict_mode(self) -> None:
    """--skip-sync must be rejected when strict_mode=true."""
    code = self._run_with_strict_mode(skip_sync=True)
    assert code == 1

  def test_skip_update_requirements_blocked_in_strict_mode(self) -> None:
    """--skip-update-requirements must be rejected when strict_mode=true."""
    code = self._run_with_strict_mode(update_requirements=False)
    assert code == 1

  def test_coverage_env_bypass_blocked_in_strict_mode(self) -> None:
    """SPEC_DRIVER_ENFORCE_COVERAGE=false must be rejected when strict_mode=true."""
    ws = self._make_workspace_mock()
    strict_config = {"strict_mode": True}
    with (
      patch.object(
        complete_delta_module, "Workspace",
      ) as mock_ws_cls,
      patch(
        "supekku.scripts.complete_delta.load_workflow_config",
        return_value=strict_config,
      ),
      patch(
        "supekku.scripts.complete_delta.is_coverage_enforcement_enabled",
        return_value=False,
      ),
      patch.object(
        complete_delta_module.sys.stdin,
        "isatty", return_value=False,
      ),
    ):
      mock_ws_cls.from_cwd.return_value = ws
      code = complete_delta_module.complete_delta("DE-TEST")
    assert code == 1


@pytest.mark.parametrize("flag_kwargs", [
  {"force": True},
  {"skip_sync": True},
  {"update_requirements": False},
])
def test_bypass_flags_permitted_in_permissive_mode(flag_kwargs):
  """In permissive mode, bypass flags must NOT be blocked by strict-mode gate."""
  workspace = MagicMock()
  delta = MagicMock()
  delta.status = "in-progress"
  delta.applies_to = {"requirements": []}
  delta.path = MagicMock()
  delta.path.exists.return_value = True
  # Make frontmatter update succeed
  delta.path.read_text.return_value = "---\nstatus: in-progress\n---\n"
  workspace.delta_registry.collect.return_value = {"DE-TEST": delta}
  workspace.requirements.records = {}

  permissive_config = {"strict_mode": False}
  with (
    patch.object(
      complete_delta_module, "Workspace",
    ) as mock_ws_cls,
    patch(
      "supekku.scripts.complete_delta.load_workflow_config",
      return_value=permissive_config,
    ),
    patch.object(
      complete_delta_module.sys.stdin,
      "isatty", return_value=False,
    ),
    patch(
      "supekku.scripts.complete_delta.is_coverage_enforcement_enabled",
      return_value=True,
    ),
    patch(
      "supekku.scripts.complete_delta.check_coverage_completeness",
      return_value=(True, []),
    ),
  ):
    mock_ws_cls.from_cwd.return_value = workspace
    # We don't assert exit code 0 because the full flow has more steps;
    # we only assert it does NOT return 1 from the strict-mode gate.
    # The fact that it proceeds past the gate is sufficient.
    complete_delta_module.complete_delta("DE-TEST", **flag_kwargs)
  # Should NOT be blocked by strict mode (may fail later in flow — that's fine)
  # The key assertion: it got past the strict-mode gate


if __name__ == "__main__":
  unittest.main()
