"""Tests for view command.

VT-073-02: render_file / render_file_paged cascades.
VT-073-04: read alias dispatches identically to view.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from supekku.cli.common import (
  ArtifactNotFoundError,
  ArtifactRef,
  get_pager,
  normalize_id,
  render_file,
  render_file_paged,
)
from supekku.cli.view import app

runner = CliRunner()


# ── render_file cascade ──────────────────────────────────────────


class TestRenderFile:
  """render_file renders markdown to stdout: glow → rich → raw."""

  def test_uses_glow_when_available(self, tmp_path: Path) -> None:
    f = tmp_path / "test.md"
    f.write_text("# Hello\n")
    with (
      patch(
        "shutil.which",
        side_effect=lambda c: "/usr/bin/glow" if c == "glow" else None,
      ),
      patch("subprocess.run") as mock_run,
    ):
      render_file(f)
      mock_run.assert_called_once()
      assert mock_run.call_args[0][0] == ["glow", str(f)]

  def test_uses_rich_when_no_glow(self, tmp_path: Path) -> None:
    f = tmp_path / "test.md"
    f.write_text("# Hello\n")
    with (
      patch(
        "shutil.which",
        side_effect=lambda c: "/usr/bin/rich" if c == "rich" else None,
      ),
      patch("subprocess.run") as mock_run,
    ):
      render_file(f)
      mock_run.assert_called_once()
      assert mock_run.call_args[0][0] == ["rich", str(f)]

  def test_falls_back_to_raw_stdout(
    self, tmp_path: Path, capsys: pytest.CaptureFixture
  ) -> None:
    f = tmp_path / "test.md"
    f.write_text("# Hello\n")
    with patch("shutil.which", return_value=None):
      render_file(f)
    assert "# Hello" in capsys.readouterr().out


# ── render_file_paged cascade ───────────────────────────────────


class TestRenderFilePaged:
  """render_file_paged pages markdown: $PAGER → glow -p → ov → less → more."""

  def test_uses_pager_env(
    self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    f = tmp_path / "test.md"
    f.write_text("# Hello\n")
    monkeypatch.setenv("PAGER", "my-pager")
    with patch("subprocess.run") as mock_run:
      render_file_paged(f)
      mock_run.assert_called_once()
      assert mock_run.call_args[0][0] == ["my-pager", str(f)]

  def test_uses_glow_pager_when_no_env(
    self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    f = tmp_path / "test.md"
    f.write_text("# Hello\n")
    monkeypatch.delenv("PAGER", raising=False)
    with (
      patch(
        "shutil.which",
        side_effect=lambda c: "/usr/bin/glow" if c == "glow" else None,
      ),
      patch("subprocess.run") as mock_run,
    ):
      render_file_paged(f)
      mock_run.assert_called_once()
      assert mock_run.call_args[0][0] == ["glow", "-p", str(f)]

  def test_falls_back_to_less(
    self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    f = tmp_path / "test.md"
    f.write_text("# Hello\n")
    monkeypatch.delenv("PAGER", raising=False)
    with (
      patch(
        "shutil.which",
        side_effect=lambda c: "/usr/bin/less" if c == "less" else None,
      ),
      patch("subprocess.run") as mock_run,
    ):
      render_file_paged(f)
      mock_run.assert_called_once()
      assert mock_run.call_args[0][0] == ["less", str(f)]

  def test_raises_when_no_pager(
    self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    f = tmp_path / "test.md"
    f.write_text("# Hello\n")
    monkeypatch.delenv("PAGER", raising=False)
    with (
      patch("shutil.which", return_value=None),
      pytest.raises(RuntimeError, match="No pager found"),
    ):
      render_file_paged(f)


# ── get_pager ────────────────────────────────────────────────────


class TestGetPager:
  """Tests for get_pager function."""

  def test_returns_pager_env_var(self, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PAGER", "my-pager")
    assert get_pager() == "my-pager"

  def test_falls_back_to_less(self, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PAGER", raising=False)
    with patch("shutil.which") as mock_which:
      mock_which.side_effect = lambda cmd: "/usr/bin/less" if cmd == "less" else None
      assert get_pager() == "less"

  def test_falls_back_to_more(self, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PAGER", raising=False)
    with patch("shutil.which") as mock_which:
      mock_which.side_effect = lambda cmd: "/usr/bin/more" if cmd == "more" else None
      assert get_pager() == "more"

  def test_returns_none_when_no_pager(self, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PAGER", raising=False)
    with patch("shutil.which", return_value=None):
      assert get_pager() is None


# ── view subcommands ─────────────────────────────────────────────


def _mock_ref(tmp_path: Path, artifact_id: str) -> ArtifactRef:
  f = tmp_path / f"{artifact_id}.md"
  f.write_text(f"# {artifact_id}\n")
  return ArtifactRef(id=artifact_id, path=f, record=None)


class TestViewDefaultRendersToStdout:
  """view <artifact> renders to stdout by default (no pager)."""

  def test_view_adr_renders_to_stdout(self, tmp_path: Path) -> None:
    ref = _mock_ref(tmp_path, "ADR-001")
    with (
      patch("supekku.cli.view.resolve_artifact", return_value=ref),
      patch("supekku.cli.view.render_file") as mock_render,
    ):
      result = runner.invoke(app, ["adr", "ADR-001"])
      assert result.exit_code == 0
      mock_render.assert_called_once_with(ref.path)

  def test_view_delta_renders_to_stdout(self, tmp_path: Path) -> None:
    ref = _mock_ref(tmp_path, "DE-001")
    with (
      patch("supekku.cli.view.resolve_artifact", return_value=ref),
      patch("supekku.cli.view.render_file") as mock_render,
    ):
      result = runner.invoke(app, ["delta", "DE-001"])
      assert result.exit_code == 0
      mock_render.assert_called_once_with(ref.path)

  def test_view_spec_renders_to_stdout(self, tmp_path: Path) -> None:
    ref = _mock_ref(tmp_path, "SPEC-001")
    with (
      patch("supekku.cli.view.resolve_artifact", return_value=ref),
      patch("supekku.cli.view.render_file") as mock_render,
    ):
      result = runner.invoke(app, ["spec", "SPEC-001"])
      assert result.exit_code == 0
      mock_render.assert_called_once_with(ref.path)


class TestViewPagerFlag:
  """view --pager/-p invokes pager instead of stdout render."""

  def test_pager_flag_pages(self, tmp_path: Path) -> None:
    ref = _mock_ref(tmp_path, "ADR-001")
    with (
      patch("supekku.cli.view.resolve_artifact", return_value=ref),
      patch("supekku.cli.view.render_file_paged") as mock_paged,
    ):
      result = runner.invoke(app, ["adr", "ADR-001", "--pager"])
      assert result.exit_code == 0
      mock_paged.assert_called_once_with(ref.path)

  def test_pager_short_flag(self, tmp_path: Path) -> None:
    ref = _mock_ref(tmp_path, "DE-001")
    with (
      patch("supekku.cli.view.resolve_artifact", return_value=ref),
      patch("supekku.cli.view.render_file_paged") as mock_paged,
    ):
      result = runner.invoke(app, ["delta", "DE-001", "-p"])
      assert result.exit_code == 0
      mock_paged.assert_called_once_with(ref.path)


class TestViewNotFound:
  """view shows error when artifact not found."""

  def test_adr_not_found(self) -> None:
    with patch(
      "supekku.cli.view.resolve_artifact",
      side_effect=ArtifactNotFoundError("adr", "ADR-999"),
    ):
      result = runner.invoke(app, ["adr", "ADR-999"])
      assert result.exit_code == 1
      assert "not found" in result.output.lower()

  def test_delta_not_found(self) -> None:
    with patch(
      "supekku.cli.view.resolve_artifact",
      side_effect=ArtifactNotFoundError("delta", "DE-999"),
    ):
      result = runner.invoke(app, ["delta", "DE-999"])
      assert result.exit_code == 1
      assert "not found" in result.output.lower()


class TestViewSubcommands:
  """All view subcommands using resolve_artifact dispatch correctly."""

  @pytest.mark.parametrize(
    ("subcommand", "artifact_id"),
    [
      ("plan", "IP-001"),
      ("audit", "AUD-001"),
      ("memory", "mem.pattern.cli.skinny"),
      ("issue", "ISSUE-001"),
      ("problem", "PROB-001"),
      ("improvement", "IMPR-001"),
      ("risk", "RISK-001"),
      ("revision", "RE-001"),
      ("policy", "POL-001"),
      ("standard", "STD-001"),
    ],
  )
  def test_subcommand_renders(
    self, tmp_path: Path, subcommand: str, artifact_id: str
  ) -> None:
    ref = _mock_ref(tmp_path, artifact_id)
    with (
      patch("supekku.cli.view.resolve_artifact", return_value=ref),
      patch("supekku.cli.view.render_file") as mock_render,
    ):
      result = runner.invoke(app, [subcommand, artifact_id])
      assert result.exit_code == 0
      mock_render.assert_called_once_with(ref.path)


# ── normalize_id ─────────────────────────────────────────────────


class TestNormalizeId:
  """Tests for normalize_id function."""

  def test_numeric_only_gets_prefix_and_padding(self) -> None:
    assert normalize_id("adr", "1") == "ADR-001"
    assert normalize_id("adr", "12") == "ADR-012"
    assert normalize_id("adr", "123") == "ADR-123"

  def test_already_prefixed_unchanged(self) -> None:
    assert normalize_id("adr", "ADR-001") == "ADR-001"
    assert normalize_id("adr", "adr-001") == "ADR-001"

  def test_all_artifact_types(self) -> None:
    assert normalize_id("adr", "5") == "ADR-005"
    assert normalize_id("delta", "23") == "DE-023"
    assert normalize_id("revision", "1") == "RE-001"
    assert normalize_id("policy", "42") == "POL-042"
    assert normalize_id("standard", "7") == "STD-007"

  def test_ambiguous_types_unchanged(self) -> None:
    assert normalize_id("spec", "001") == "001"
    assert normalize_id("requirement", "001") == "001"
    assert normalize_id("card", "123") == "123"
    assert normalize_id("unknown", "456") == "456"

  def test_non_numeric_unchanged(self) -> None:
    assert normalize_id("adr", "foo") == "foo"
    assert normalize_id("delta", "my-delta") == "my-delta"


# ── view revision regression ─────────────────────────────────────


class TestViewRevisionRegression:
  """Regression tests for view revision."""

  def test_view_revision_renders(self, tmp_path: Path) -> None:
    """view revision RE-001 renders the file."""
    ref = _mock_ref(tmp_path, "RE-001")
    with (
      patch("supekku.cli.view.resolve_artifact", return_value=ref),
      patch("supekku.cli.view.render_file") as mock_render,
    ):
      result = runner.invoke(app, ["revision", "RE-001"])
      assert result.exit_code == 0
      mock_render.assert_called_once_with(ref.path)

  def test_view_revision_numeric_shorthand(self, tmp_path: Path) -> None:
    """view revision 1 resolves via resolve_artifact."""
    ref = _mock_ref(tmp_path, "RE-001")
    with (
      patch("supekku.cli.view.resolve_artifact", return_value=ref),
      patch("supekku.cli.view.render_file"),
    ):
      result = runner.invoke(app, ["revision", "1"])
      assert result.exit_code == 0

  def test_view_revision_not_found(self) -> None:
    with patch(
      "supekku.cli.view.resolve_artifact",
      side_effect=ArtifactNotFoundError("revision", "RE-999"),
    ):
      result = runner.invoke(app, ["revision", "RE-999"])
      assert result.exit_code == 1
      assert "not found" in result.output.lower()


# ── read alias (VT-073-04) ──────────────────────────────────────


class TestReadAlias:
  """VT-073-04: 'read' alias dispatches identically to 'view'."""

  def test_read_alias_registered(self) -> None:
    """read appears in the main app."""
    from supekku.cli.main import app as main_app  # noqa: PLC0415

    commands = [info.name for info in main_app.registered_groups]
    assert "read" in commands
    assert "view" in commands

  def test_read_invokes_same_app(self) -> None:
    """read and view reference the same Typer app instance."""
    from supekku.cli.main import app as main_app  # noqa: PLC0415

    groups_by_name = {info.name: info for info in main_app.registered_groups}
    read_app = groups_by_name["read"].typer_instance
    view_app = groups_by_name["view"].typer_instance
    assert read_app is view_app


# ── view card (special --anywhere flag) ──────────────────────────


class TestViewCard:
  """view card preserves --anywhere flag."""

  def test_view_card_renders(self, tmp_path: Path) -> None:
    card_file = tmp_path / "T001-task.md"
    card_file.write_text("# Task\n")
    with (
      patch("supekku.scripts.lib.cards.CardRegistry") as mock_cls,
      patch("supekku.cli.view.render_file") as mock_render,
    ):
      mock_cls.return_value.resolve_path.return_value = str(card_file)
      result = runner.invoke(app, ["card", "T001"])
      assert result.exit_code == 0
      mock_render.assert_called_once()

  def test_view_card_pager(self, tmp_path: Path) -> None:
    card_file = tmp_path / "T001-task.md"
    card_file.write_text("# Task\n")
    with (
      patch("supekku.scripts.lib.cards.CardRegistry") as mock_cls,
      patch("supekku.cli.view.render_file_paged") as mock_paged,
    ):
      mock_cls.return_value.resolve_path.return_value = str(card_file)
      result = runner.invoke(app, ["card", "T001", "-p"])
      assert result.exit_code == 0
      mock_paged.assert_called_once()

  def test_view_card_not_found(self) -> None:
    with patch("supekku.scripts.lib.cards.CardRegistry") as mock_cls:
      mock_cls.return_value.resolve_path.side_effect = FileNotFoundError("not found")
      result = runner.invoke(app, ["card", "T999"])
      assert result.exit_code == 1
      assert "not found" in result.output.lower()
