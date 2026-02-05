"""Tests for edit command."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from supekku.cli.common import get_editor
from supekku.cli.edit import app

runner = CliRunner()


class TestGetEditor:
  """Tests for get_editor function."""

  def test_returns_editor_env_var(self, monkeypatch: pytest.MonkeyPatch) -> None:
    """Returns $EDITOR when set."""
    monkeypatch.setenv("EDITOR", "my-editor")
    assert get_editor() == "my-editor"

  def test_returns_visual_env_var(self, monkeypatch: pytest.MonkeyPatch) -> None:
    """Returns $VISUAL when $EDITOR unset."""
    monkeypatch.delenv("EDITOR", raising=False)
    monkeypatch.setenv("VISUAL", "my-visual-editor")
    assert get_editor() == "my-visual-editor"

  def test_falls_back_to_vi(self, monkeypatch: pytest.MonkeyPatch) -> None:
    """Falls back to vi when env vars unset."""
    monkeypatch.delenv("EDITOR", raising=False)
    monkeypatch.delenv("VISUAL", raising=False)
    with patch("shutil.which") as mock_which:
      mock_which.return_value = "/usr/bin/vi"
      assert get_editor() == "vi"

  def test_returns_none_when_no_editor(self, monkeypatch: pytest.MonkeyPatch) -> None:
    """Returns None when no editor available."""
    monkeypatch.delenv("EDITOR", raising=False)
    monkeypatch.delenv("VISUAL", raising=False)
    with patch("shutil.which", return_value=None):
      assert get_editor() is None


class TestEditAdr:
  """Tests for edit adr command."""

  def test_edit_adr_calls_editor(
    self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    """Edit adr opens file in editor."""
    monkeypatch.setenv("EDITOR", "vim")

    with patch("supekku.cli.edit.DecisionRegistry") as mock_registry_class:
      mock_registry = MagicMock()
      mock_decision = MagicMock()
      mock_decision.path = tmp_path / "test.md"
      mock_decision.path.write_text("# Test ADR\n")
      mock_registry.find.return_value = mock_decision
      mock_registry_class.return_value = mock_registry

      with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        result = runner.invoke(app, ["adr", "ADR-001"])
        assert result.exit_code == 0
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "vim"

  def test_edit_adr_not_found(self, monkeypatch: pytest.MonkeyPatch) -> None:
    """Edit adr shows error when not found."""
    monkeypatch.setenv("EDITOR", "vim")

    with patch("supekku.cli.edit.DecisionRegistry") as mock_registry_class:
      mock_registry = MagicMock()
      mock_registry.find.return_value = None
      mock_registry_class.return_value = mock_registry

      result = runner.invoke(app, ["adr", "ADR-999"])
      assert result.exit_code == 1
      assert "not found" in result.output.lower()


class TestEditSpec:
  """Tests for edit spec command."""

  def test_edit_spec_calls_editor(
    self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    """Edit spec opens file in editor."""
    monkeypatch.setenv("EDITOR", "vim")

    with patch("supekku.cli.edit.SpecRegistry") as mock_registry_class:
      mock_registry = MagicMock()
      mock_spec = MagicMock()
      mock_spec.path = tmp_path / "spec.md"
      mock_spec.path.write_text("# Test Spec\n")
      mock_registry.get.return_value = mock_spec
      mock_registry_class.return_value = mock_registry

      with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        result = runner.invoke(app, ["spec", "SPEC-001"])
        assert result.exit_code == 0


class TestEditDelta:
  """Tests for edit delta command."""

  def test_edit_delta_calls_editor(
    self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    """Edit delta opens file in editor."""
    monkeypatch.setenv("EDITOR", "vim")

    with patch("supekku.cli.edit.ChangeRegistry") as mock_registry_class:
      mock_registry = MagicMock()
      mock_artifact = MagicMock()
      mock_artifact.path = tmp_path / "delta.md"
      mock_artifact.path.write_text("# Test Delta\n")
      mock_registry.collect.return_value = {"DE-001": mock_artifact}
      mock_registry_class.return_value = mock_registry

      with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        result = runner.invoke(app, ["delta", "DE-001"])
        assert result.exit_code == 0


class TestNoEditorAvailable:
  """Tests for error handling when no editor available."""

  def test_error_when_no_editor(self, monkeypatch: pytest.MonkeyPatch) -> None:
    """Shows error when no editor available."""
    monkeypatch.delenv("EDITOR", raising=False)
    monkeypatch.delenv("VISUAL", raising=False)

    with patch("supekku.cli.edit.DecisionRegistry") as mock_registry_class:
      mock_registry = MagicMock()
      mock_decision = MagicMock()
      mock_decision.path = Path("/tmp/test.md")
      mock_registry.find.return_value = mock_decision
      mock_registry_class.return_value = mock_registry

      with patch("supekku.cli.common.get_editor", return_value=None):
        result = runner.invoke(app, ["adr", "ADR-001"])
        assert result.exit_code == 1
        assert "editor" in result.output.lower()


class TestEditAdrShorthand:
  """Tests for edit adr with shorthand IDs."""

  def test_edit_adr_numeric_shorthand(
    self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    """Edit adr accepts numeric shorthand like '001'."""
    monkeypatch.setenv("EDITOR", "vim")

    with patch("supekku.cli.edit.DecisionRegistry") as mock_registry_class:
      mock_registry = MagicMock()
      mock_decision = MagicMock()
      mock_decision.path = tmp_path / "test.md"
      mock_decision.path.write_text("# Test ADR\n")
      mock_registry.find.return_value = mock_decision
      mock_registry_class.return_value = mock_registry

      with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        result = runner.invoke(app, ["adr", "001"])
        assert result.exit_code == 0
        # Verify registry was called with normalized ID
        mock_registry.find.assert_called_once_with("ADR-001")


class TestEditDeltaShorthand:
  """Tests for edit delta with shorthand IDs."""

  def test_edit_delta_numeric_shorthand(
    self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    """Edit delta accepts numeric shorthand like '23'."""
    monkeypatch.setenv("EDITOR", "vim")

    with patch("supekku.cli.edit.ChangeRegistry") as mock_registry_class:
      mock_registry = MagicMock()
      mock_artifact = MagicMock()
      mock_artifact.path = tmp_path / "delta.md"
      mock_artifact.path.write_text("# Test Delta\n")
      mock_registry.collect.return_value = {"DE-023": mock_artifact}
      mock_registry_class.return_value = mock_registry

      with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        result = runner.invoke(app, ["delta", "23"])
        assert result.exit_code == 0
