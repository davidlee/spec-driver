"""Tests for view command."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from supekku.cli.common import get_pager, normalize_id
from supekku.cli.view import app

runner = CliRunner()


class TestGetPager:
  """Tests for get_pager function."""

  def test_returns_pager_env_var(self, monkeypatch: pytest.MonkeyPatch) -> None:
    """Returns $PAGER when set."""
    monkeypatch.setenv("PAGER", "my-pager")
    assert get_pager() == "my-pager"

  def test_falls_back_to_less(self, monkeypatch: pytest.MonkeyPatch) -> None:
    """Falls back to less when $PAGER unset."""
    monkeypatch.delenv("PAGER", raising=False)
    with patch("shutil.which") as mock_which:
      mock_which.side_effect = lambda cmd: "/usr/bin/less" if cmd == "less" else None
      assert get_pager() == "less"

  def test_falls_back_to_more(self, monkeypatch: pytest.MonkeyPatch) -> None:
    """Falls back to more when less unavailable."""
    monkeypatch.delenv("PAGER", raising=False)
    with patch("shutil.which") as mock_which:
      mock_which.side_effect = lambda cmd: "/usr/bin/more" if cmd == "more" else None
      assert get_pager() == "more"

  def test_returns_none_when_no_pager(self, monkeypatch: pytest.MonkeyPatch) -> None:
    """Returns None when no pager available."""
    monkeypatch.delenv("PAGER", raising=False)
    with patch("shutil.which", return_value=None):
      assert get_pager() is None


class TestViewAdr:
  """Tests for view adr command."""

  def test_view_adr_calls_pager(
    self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    """View adr opens file in pager."""
    # Set up test environment
    monkeypatch.setenv("PAGER", "cat")

    with patch("supekku.cli.view.DecisionRegistry") as mock_registry_class:
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
        assert call_args[0] == "cat"

  def test_view_adr_not_found(self, monkeypatch: pytest.MonkeyPatch) -> None:
    """View adr shows error when not found."""
    monkeypatch.setenv("PAGER", "cat")

    with patch("supekku.cli.view.DecisionRegistry") as mock_registry_class:
      mock_registry = MagicMock()
      mock_registry.find.return_value = None
      mock_registry_class.return_value = mock_registry

      result = runner.invoke(app, ["adr", "ADR-999"])
      assert result.exit_code == 1
      assert "not found" in result.output.lower()


class TestViewSpec:
  """Tests for view spec command."""

  def test_view_spec_calls_pager(
    self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    """View spec opens file in pager."""
    monkeypatch.setenv("PAGER", "cat")

    with patch("supekku.cli.view.SpecRegistry") as mock_registry_class:
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


class TestViewDelta:
  """Tests for view delta command."""

  def test_view_delta_calls_pager(
    self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    """View delta opens file in pager."""
    monkeypatch.setenv("PAGER", "cat")

    with patch("supekku.cli.view.ChangeRegistry") as mock_registry_class:
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


class TestNoPagerAvailable:
  """Tests for error handling when no pager available."""

  def test_error_when_no_pager(self, monkeypatch: pytest.MonkeyPatch) -> None:
    """Shows error when no pager available."""
    monkeypatch.delenv("PAGER", raising=False)

    with patch("supekku.cli.view.DecisionRegistry") as mock_registry_class:
      mock_registry = MagicMock()
      mock_decision = MagicMock()
      mock_decision.path = Path("/tmp/test.md")
      mock_registry.find.return_value = mock_decision
      mock_registry_class.return_value = mock_registry

      with patch("supekku.cli.common.get_pager", return_value=None):
        result = runner.invoke(app, ["adr", "ADR-001"])
        assert result.exit_code == 1
        assert "pager" in result.output.lower()


class TestNormalizeId:
  """Tests for normalize_id function."""

  def test_numeric_only_gets_prefix_and_padding(self) -> None:
    """Numeric-only ID gets prefix and zero-padding."""
    assert normalize_id("adr", "1") == "ADR-001"
    assert normalize_id("adr", "12") == "ADR-012"
    assert normalize_id("adr", "123") == "ADR-123"

  def test_already_prefixed_unchanged(self) -> None:
    """ID with prefix is returned unchanged (uppercased)."""
    assert normalize_id("adr", "ADR-001") == "ADR-001"
    assert normalize_id("adr", "adr-001") == "ADR-001"

  def test_all_artifact_types(self) -> None:
    """All unambiguous artifact types normalize correctly."""
    assert normalize_id("adr", "5") == "ADR-005"
    assert normalize_id("delta", "23") == "DE-023"
    assert normalize_id("revision", "1") == "RE-001"
    assert normalize_id("policy", "42") == "POL-042"
    assert normalize_id("standard", "7") == "STD-007"

  def test_ambiguous_types_unchanged(self) -> None:
    """Ambiguous artifact types are not normalized."""
    assert normalize_id("spec", "001") == "001"
    assert normalize_id("requirement", "001") == "001"
    assert normalize_id("card", "123") == "123"
    assert normalize_id("unknown", "456") == "456"

  def test_non_numeric_unchanged(self) -> None:
    """Non-numeric IDs are returned unchanged."""
    assert normalize_id("adr", "foo") == "foo"
    assert normalize_id("delta", "my-delta") == "my-delta"


class TestViewAdrShorthand:
  """Tests for view adr with shorthand IDs."""

  def test_view_adr_numeric_shorthand(
    self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    """View adr accepts numeric shorthand like '001'."""
    monkeypatch.setenv("PAGER", "cat")

    with patch("supekku.cli.view.DecisionRegistry") as mock_registry_class:
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


class TestViewDeltaShorthand:
  """Tests for view delta with shorthand IDs."""

  def test_view_delta_numeric_shorthand(
    self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    """View delta accepts numeric shorthand like '23'."""
    monkeypatch.setenv("PAGER", "cat")

    with patch("supekku.cli.view.ChangeRegistry") as mock_registry_class:
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
