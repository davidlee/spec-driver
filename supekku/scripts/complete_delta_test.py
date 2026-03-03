"""Tests for complete-delta prompt behavior."""

from __future__ import annotations

import unittest
from unittest.mock import patch

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


if __name__ == "__main__":
  unittest.main()
