"""Tests for shared CLI helpers: data types, resolve, emit, find.

VT-resolve, VT-emit, VT-find-artifacts verification artifacts.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
import typer

from supekku.cli.common import (
  AmbiguousArtifactError,
  ArtifactNotFoundError,
  ArtifactRef,
  emit_artifact,
  resolve_artifact,
)

# ── ArtifactRef ─────────────────────────────────────────────────


class TestArtifactRef:
  """ArtifactRef is a frozen dataclass holding resolved artifact info."""

  def test_construction(self) -> None:
    ref = ArtifactRef(id="RE-001", path=Path("/tmp/re.md"), record={"mock": True})
    assert ref.id == "RE-001"
    assert ref.path == Path("/tmp/re.md")
    assert ref.record == {"mock": True}

  def test_frozen(self) -> None:
    ref = ArtifactRef(id="RE-001", path=Path("/tmp/re.md"), record=None)
    with pytest.raises(AttributeError):
      ref.id = "RE-002"  # type: ignore[misc]

  def test_equality(self) -> None:
    a = ArtifactRef(id="X", path=Path("/a"), record=None)
    b = ArtifactRef(id="X", path=Path("/a"), record=None)
    assert a == b

  def test_inequality_different_id(self) -> None:
    a = ArtifactRef(id="X", path=Path("/a"), record=None)
    b = ArtifactRef(id="Y", path=Path("/a"), record=None)
    assert a != b


# ── ArtifactNotFoundError ───────────────────────────────────────


class TestArtifactNotFoundError:
  """ArtifactNotFoundError carries type and id for consistent messaging."""

  def test_attributes(self) -> None:
    err = ArtifactNotFoundError("revision", "RE-999")
    assert err.artifact_type == "revision"
    assert err.artifact_id == "RE-999"

  def test_message(self) -> None:
    err = ArtifactNotFoundError("delta", "DE-001")
    assert "delta" in str(err)
    assert "DE-001" in str(err)

  def test_is_exception(self) -> None:
    with pytest.raises(ArtifactNotFoundError):
      raise ArtifactNotFoundError("spec", "SPEC-001")


# ── AmbiguousArtifactError ──────────────────────────────────────


class TestAmbiguousArtifactError:
  """AmbiguousArtifactError lists all matching paths for disambiguation."""

  def test_attributes(self) -> None:
    paths = [Path("/a/IMPR-003.md"), Path("/b/IMPR-003.md")]
    err = AmbiguousArtifactError("improvement", "IMPR-003", paths)
    assert err.artifact_type == "improvement"
    assert err.artifact_id == "IMPR-003"
    assert err.paths == paths

  def test_message_contains_paths(self) -> None:
    paths = [Path("/a.md"), Path("/b.md")]
    err = AmbiguousArtifactError("issue", "ISSUE-019", paths)
    msg = str(err)
    assert "ISSUE-019" in msg
    assert "/a.md" in msg
    assert "/b.md" in msg

  def test_is_exception(self) -> None:
    with pytest.raises(AmbiguousArtifactError):
      raise AmbiguousArtifactError("risk", "RISK-001", [Path("/x.md")])


# ── resolve_artifact ────────────────────────────────────────────


def _mock_change_artifact(artifact_id: str, path: str) -> SimpleNamespace:
  return SimpleNamespace(id=artifact_id, path=Path(path))


def _mock_registry_collect(artifacts: dict) -> MagicMock:
  """Create a mock ChangeRegistry whose collect() returns artifacts dict."""
  registry = MagicMock()
  registry.collect.return_value = artifacts
  return registry


class TestResolveArtifactRevision:
  """resolve_artifact for revision type — PoC migration target."""

  @patch("supekku.scripts.lib.changes.registry.ChangeRegistry")
  def test_resolves_revision_by_full_id(self, mock_cls: MagicMock) -> None:
    art = _mock_change_artifact("RE-001", "/repo/change/revisions/RE-001.md")
    mock_cls.return_value = _mock_registry_collect({"RE-001": art})

    ref = resolve_artifact("revision", "RE-001", Path("/repo"))
    assert ref.id == "RE-001"
    assert ref.path == Path("/repo/change/revisions/RE-001.md")
    assert ref.record is art
    mock_cls.assert_called_once_with(root=Path("/repo"), kind="revision")

  @patch("supekku.scripts.lib.changes.registry.ChangeRegistry")
  def test_resolves_revision_by_numeric_shorthand(
    self, mock_cls: MagicMock
  ) -> None:
    art = _mock_change_artifact("RE-001", "/repo/re.md")
    mock_cls.return_value = _mock_registry_collect({"RE-001": art})

    ref = resolve_artifact("revision", "1", Path("/repo"))
    assert ref.id == "RE-001"

  @patch("supekku.scripts.lib.changes.registry.ChangeRegistry")
  def test_raises_not_found_for_missing_revision(
    self, mock_cls: MagicMock
  ) -> None:
    mock_cls.return_value = _mock_registry_collect({})

    with pytest.raises(ArtifactNotFoundError) as exc_info:
      resolve_artifact("revision", "RE-999", Path("/repo"))
    assert exc_info.value.artifact_type == "revision"
    assert exc_info.value.artifact_id == "RE-999"


class TestResolveArtifactDelta:
  """resolve_artifact for delta type."""

  @patch("supekku.scripts.lib.changes.registry.ChangeRegistry")
  def test_resolves_delta(self, mock_cls: MagicMock) -> None:
    art = _mock_change_artifact("DE-041", "/repo/change/deltas/DE-041/DE-041.md")
    mock_cls.return_value = _mock_registry_collect({"DE-041": art})

    ref = resolve_artifact("delta", "41", Path("/repo"))
    assert ref.id == "DE-041"
    mock_cls.assert_called_once_with(root=Path("/repo"), kind="delta")


class TestResolveArtifactAudit:
  """resolve_artifact for audit type."""

  @patch("supekku.scripts.lib.changes.registry.ChangeRegistry")
  def test_resolves_audit(self, mock_cls: MagicMock) -> None:
    art = _mock_change_artifact("AUD-001", "/repo/change/audits/AUD-001.md")
    mock_cls.return_value = _mock_registry_collect({"AUD-001": art})

    ref = resolve_artifact("audit", "AUD-001", Path("/repo"))
    assert ref.id == "AUD-001"
    mock_cls.assert_called_once_with(root=Path("/repo"), kind="audit")


class TestResolveArtifactSpec:
  """resolve_artifact for spec type."""

  @patch("supekku.scripts.lib.specs.registry.SpecRegistry")
  def test_resolves_spec(self, mock_cls: MagicMock) -> None:
    spec = SimpleNamespace(path=Path("/repo/specify/tech/SPEC-009/SPEC-009.md"))
    mock_cls.return_value.get.return_value = spec

    ref = resolve_artifact("spec", "SPEC-009", Path("/repo"))
    assert ref.id == "SPEC-009"
    assert ref.record is spec

  @patch("supekku.scripts.lib.specs.registry.SpecRegistry")
  def test_raises_not_found_for_missing_spec(self, mock_cls: MagicMock) -> None:
    mock_cls.return_value.get.return_value = None

    with pytest.raises(ArtifactNotFoundError):
      resolve_artifact("spec", "SPEC-999", Path("/repo"))


class TestResolveArtifactAdr:
  """resolve_artifact for ADR type."""

  @patch("supekku.scripts.lib.decisions.registry.DecisionRegistry")
  def test_resolves_adr(self, mock_cls: MagicMock) -> None:
    decision = SimpleNamespace(
      id="ADR-001", path="/repo/specify/decisions/ADR-001-foo.md"
    )
    mock_cls.return_value.find.return_value = decision

    ref = resolve_artifact("adr", "1", Path("/repo"))
    assert ref.id == "ADR-001"
    assert ref.path == Path("/repo/specify/decisions/ADR-001-foo.md")

  @patch("supekku.scripts.lib.decisions.registry.DecisionRegistry")
  def test_raises_not_found_for_missing_adr(
    self, mock_cls: MagicMock
  ) -> None:
    mock_cls.return_value.find.return_value = None

    with pytest.raises(ArtifactNotFoundError):
      resolve_artifact("adr", "ADR-999", Path("/repo"))


class TestResolveArtifactMemory:
  """resolve_artifact for memory type."""

  @patch("supekku.scripts.lib.memory.registry.MemoryRegistry")
  def test_resolves_memory(self, mock_cls: MagicMock) -> None:
    record = SimpleNamespace(
      id="mem.fact.auth", path=Path("/repo/memory/mem.fact.auth.md")
    )
    mock_cls.return_value.find.return_value = record

    ref = resolve_artifact("memory", "mem.fact.auth", Path("/repo"))
    assert ref.id == "mem.fact.auth"
    assert ref.record is record


class TestResolveArtifactRequirement:
  """resolve_artifact for requirement type."""

  @patch("supekku.scripts.lib.core.paths.get_registry_dir")
  @patch("supekku.scripts.lib.requirements.registry.RequirementsRegistry")
  def test_resolves_requirement(
    self, mock_cls: MagicMock, mock_dir: MagicMock
  ) -> None:
    mock_dir.return_value = Path("/repo/.spec-driver/registry")
    record = SimpleNamespace(uid="SPEC-009.FR-001", path="specify/tech/SPEC-009.md")
    mock_cls.return_value.records = {"SPEC-009.FR-001": record}

    ref = resolve_artifact("requirement", "SPEC-009.FR-001", Path("/repo"))
    assert ref.id == "SPEC-009.FR-001"

  @patch("supekku.scripts.lib.core.paths.get_registry_dir")
  @patch("supekku.scripts.lib.requirements.registry.RequirementsRegistry")
  def test_normalizes_colon_to_dot(
    self, mock_cls: MagicMock, mock_dir: MagicMock
  ) -> None:
    """Colon-separated ID is normalized to dot per DEC-041-05."""
    mock_dir.return_value = Path("/repo/.spec-driver/registry")
    record = SimpleNamespace(uid="SPEC-009.FR-001", path="specify/tech/SPEC-009.md")
    mock_cls.return_value.records = {"SPEC-009.FR-001": record}

    ref = resolve_artifact("requirement", "SPEC-009:FR-001", Path("/repo"))
    assert ref.id == "SPEC-009.FR-001"


class TestResolveArtifactCard:
  """resolve_artifact for card type."""

  @patch("supekku.scripts.lib.cards.CardRegistry")
  def test_resolves_card(self, mock_cls: MagicMock) -> None:
    card = SimpleNamespace(id="T001", path=Path("/repo/kanban/doing/T001-task.md"))
    mock_cls.return_value.resolve_card.return_value = card

    ref = resolve_artifact("card", "T001", Path("/repo"))
    assert ref.id == "T001"
    assert ref.record is card

  @patch("supekku.scripts.lib.cards.CardRegistry")
  def test_raises_not_found_for_missing_card(
    self, mock_cls: MagicMock
  ) -> None:
    mock_cls.return_value.resolve_card.side_effect = FileNotFoundError("nope")

    with pytest.raises(ArtifactNotFoundError):
      resolve_artifact("card", "T999", Path("/repo"))


class TestResolveArtifactUnsupportedType:
  """resolve_artifact raises ValueError for unknown types."""

  def test_raises_value_error(self) -> None:
    with pytest.raises(ValueError, match="Unknown artifact type"):
      resolve_artifact("bogus", "X-001", Path("/repo"))


# ── emit_artifact ───────────────────────────────────────────────


def _make_ref(content: str = "raw content") -> ArtifactRef:
  """Create a test ArtifactRef with a real temp-ish path."""
  return ArtifactRef(
    id="RE-001",
    path=Path("/tmp/test-artifact.md"),
    record={"id": "RE-001", "status": "draft"},
  )


class TestEmitArtifactDefault:
  """emit_artifact default output mode uses format_fn."""

  def test_default_calls_format_fn(self, capsys: pytest.CaptureFixture) -> None:
    ref = _make_ref()
    with pytest.raises(typer.Exit):
      emit_artifact(
        ref,
        format_fn=lambda r: f"formatted:{r['id']}",
        json_fn=lambda r: "{}",
      )
    assert "formatted:RE-001" in capsys.readouterr().out


class TestEmitArtifactJson:
  """emit_artifact --json mode uses json_fn."""

  def test_json_calls_json_fn(self, capsys: pytest.CaptureFixture) -> None:
    ref = _make_ref()
    with pytest.raises(typer.Exit):
      emit_artifact(
        ref,
        json_output=True,
        format_fn=lambda r: "nope",
        json_fn=lambda r: '{"id":"RE-001"}',
      )
    out = capsys.readouterr().out
    assert '"id"' in out
    assert "nope" not in out


class TestEmitArtifactPath:
  """emit_artifact --path mode echoes the path."""

  def test_path_only(self, capsys: pytest.CaptureFixture) -> None:
    ref = _make_ref()
    with pytest.raises(typer.Exit):
      emit_artifact(
        ref,
        path_only=True,
        format_fn=lambda r: "nope",
        json_fn=lambda r: "nope",
      )
    assert "/tmp/test-artifact.md" in capsys.readouterr().out


class TestEmitArtifactRaw:
  """emit_artifact --raw mode reads the file content."""

  def test_raw_reads_file(
    self, tmp_path: Path, capsys: pytest.CaptureFixture
  ) -> None:
    artifact_file = tmp_path / "artifact.md"
    artifact_file.write_text("---\nid: RE-001\n---\nBody here.\n")
    ref = ArtifactRef(id="RE-001", path=artifact_file, record={})
    with pytest.raises(typer.Exit):
      emit_artifact(
        ref,
        raw_output=True,
        format_fn=lambda r: "nope",
        json_fn=lambda r: "nope",
      )
    assert "Body here." in capsys.readouterr().out


class TestEmitArtifactMutualExclusivity:
  """emit_artifact rejects multiple output modes."""

  def test_json_and_path_rejected(
    self, capsys: pytest.CaptureFixture
  ) -> None:
    ref = _make_ref()
    with pytest.raises(typer.Exit):
      emit_artifact(
        ref,
        json_output=True,
        path_only=True,
        format_fn=lambda r: "",
        json_fn=lambda r: "",
      )
    assert "mutually exclusive" in capsys.readouterr().err

  def test_json_and_raw_rejected(
    self, capsys: pytest.CaptureFixture
  ) -> None:
    ref = _make_ref()
    with pytest.raises(typer.Exit):
      emit_artifact(
        ref,
        json_output=True,
        raw_output=True,
        format_fn=lambda r: "",
        json_fn=lambda r: "",
      )
    assert "mutually exclusive" in capsys.readouterr().err

  def test_all_three_rejected(
    self, capsys: pytest.CaptureFixture
  ) -> None:
    ref = _make_ref()
    with pytest.raises(typer.Exit):
      emit_artifact(
        ref,
        json_output=True,
        path_only=True,
        raw_output=True,
        format_fn=lambda r: "",
        json_fn=lambda r: "",
      )
    assert "mutually exclusive" in capsys.readouterr().err
