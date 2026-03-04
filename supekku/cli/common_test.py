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
  find_artifacts,
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
  def test_resolves_revision_by_numeric_shorthand(self, mock_cls: MagicMock) -> None:
    art = _mock_change_artifact("RE-001", "/repo/re.md")
    mock_cls.return_value = _mock_registry_collect({"RE-001": art})

    ref = resolve_artifact("revision", "1", Path("/repo"))
    assert ref.id == "RE-001"

  @patch("supekku.scripts.lib.changes.registry.ChangeRegistry")
  def test_raises_not_found_for_missing_revision(self, mock_cls: MagicMock) -> None:
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
  def test_raises_not_found_for_missing_adr(self, mock_cls: MagicMock) -> None:
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
  def test_resolves_requirement(self, mock_cls: MagicMock, mock_dir: MagicMock) -> None:
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
  def test_raises_not_found_for_missing_card(self, mock_cls: MagicMock) -> None:
    mock_cls.return_value.resolve_card.side_effect = FileNotFoundError("nope")

    with pytest.raises(ArtifactNotFoundError):
      resolve_artifact("card", "T999", Path("/repo"))


class TestResolveArtifactPolicy:
  """resolve_artifact for policy type."""

  @patch("supekku.scripts.lib.policies.registry.PolicyRegistry")
  def test_resolves_policy(self, mock_cls: MagicMock) -> None:
    record = SimpleNamespace(id="POL-001", path="/repo/specify/policies/POL-001.md")
    mock_cls.return_value.find.return_value = record

    ref = resolve_artifact("policy", "1", Path("/repo"))
    assert ref.id == "POL-001"
    assert ref.path == Path("/repo/specify/policies/POL-001.md")

  @patch("supekku.scripts.lib.policies.registry.PolicyRegistry")
  def test_raises_not_found(self, mock_cls: MagicMock) -> None:
    mock_cls.return_value.find.return_value = None

    with pytest.raises(ArtifactNotFoundError):
      resolve_artifact("policy", "POL-999", Path("/repo"))


class TestResolveArtifactStandard:
  """resolve_artifact for standard type."""

  @patch("supekku.scripts.lib.standards.registry.StandardRegistry")
  def test_resolves_standard(self, mock_cls: MagicMock) -> None:
    record = SimpleNamespace(id="STD-001", path="/repo/specify/standards/STD-001.md")
    mock_cls.return_value.find.return_value = record

    ref = resolve_artifact("standard", "1", Path("/repo"))
    assert ref.id == "STD-001"

  @patch("supekku.scripts.lib.standards.registry.StandardRegistry")
  def test_raises_not_found(self, mock_cls: MagicMock) -> None:
    mock_cls.return_value.find.return_value = None

    with pytest.raises(ArtifactNotFoundError):
      resolve_artifact("standard", "STD-999", Path("/repo"))


class TestResolveArtifactDispatchCoverage:
  """All types in dispatch table are exercised."""

  @pytest.mark.parametrize(
    "artifact_type",
    [
      "spec",
      "delta",
      "revision",
      "audit",
      "adr",
      "policy",
      "standard",
      "requirement",
      "card",
      "memory",
      "plan",
      "issue",
      "problem",
      "improvement",
      "risk",
    ],
  )
  def test_known_type_does_not_raise_value_error(self, artifact_type: str) -> None:
    """Every registered type should dispatch (may raise NotFound, not ValueError)."""
    with pytest.raises((ArtifactNotFoundError, FileNotFoundError, Exception)):
      resolve_artifact(artifact_type, "NONEXISTENT-999", Path("/tmp/no-repo"))


class TestResolveArtifactPlan:
  """Tests for plan resolver (VT-plan-resolve)."""

  def test_resolves_plan_by_full_id(self, tmp_path: Path) -> None:
    delta_dir = tmp_path / "change" / "deltas" / "DE-041-slug"
    delta_dir.mkdir(parents=True)
    plan_file = delta_dir / "IP-041.md"
    plan_file.write_text(
      "---\nid: IP-041\nname: Test Plan\nstatus: draft\nkind: plan\n---\n",
    )
    ref = resolve_artifact("plan", "IP-041", tmp_path)
    assert ref.id == "IP-041"
    assert ref.path == plan_file
    assert ref.record["id"] == "IP-041"

  def test_resolves_plan_by_numeric_shorthand(self, tmp_path: Path) -> None:
    delta_dir = tmp_path / "change" / "deltas" / "DE-041-slug"
    delta_dir.mkdir(parents=True)
    (delta_dir / "IP-041.md").write_text(
      "---\nid: IP-041\nname: P\nstatus: draft\nkind: plan\n---\n",
    )
    ref = resolve_artifact("plan", "41", tmp_path)
    assert ref.id == "IP-041"

  def test_raises_not_found_for_missing_plan(self, tmp_path: Path) -> None:
    (tmp_path / "change" / "deltas").mkdir(parents=True)
    with pytest.raises(ArtifactNotFoundError):
      resolve_artifact("plan", "IP-999", tmp_path)

  def test_raises_not_found_when_no_deltas_dir(self, tmp_path: Path) -> None:
    with pytest.raises(ArtifactNotFoundError):
      resolve_artifact("plan", "IP-041", tmp_path)


class TestResolveArtifactBacklog:
  """Tests for backlog resolvers (issue, problem, improvement, risk)."""

  def _create_backlog_item(
    self, root: Path, subdir: str, item_id: str, slug: str
  ) -> Path:
    entry_dir = root / "backlog" / subdir / f"{item_id}-{slug}"
    entry_dir.mkdir(parents=True, exist_ok=True)
    md = entry_dir / f"{item_id}.md"
    kind = subdir.rstrip("s")
    fm = f"---\nid: {item_id}\nname: {slug}\nkind: {kind}\nstatus: open\n---\n"
    md.write_text(fm)
    return md

  @pytest.mark.parametrize(
    ("artifact_type", "subdir", "item_id"),
    [
      ("issue", "issues", "ISSUE-001"),
      ("problem", "problems", "PROB-001"),
      ("improvement", "improvements", "IMPR-001"),
      ("risk", "risks", "RISK-001"),
    ],
  )
  def test_resolves_backlog_item(
    self, tmp_path: Path, artifact_type: str, subdir: str, item_id: str
  ) -> None:
    md = self._create_backlog_item(tmp_path, subdir, item_id, "test")
    ref = resolve_artifact(artifact_type, item_id, tmp_path)
    assert ref.id == item_id
    assert ref.path == md

  def test_raises_not_found_for_missing_backlog(self, tmp_path: Path) -> None:
    with pytest.raises(ArtifactNotFoundError):
      resolve_artifact("issue", "ISSUE-999", tmp_path)

  def test_raises_ambiguous_for_duplicates(self, tmp_path: Path) -> None:
    self._create_backlog_item(tmp_path, "issues", "ISSUE-001", "first")
    self._create_backlog_item(tmp_path, "issues", "ISSUE-001", "second")
    with pytest.raises(AmbiguousArtifactError):
      resolve_artifact("issue", "ISSUE-001", tmp_path)


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

  def test_raw_reads_file(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
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

  def test_json_and_path_rejected(self, capsys: pytest.CaptureFixture) -> None:
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

  def test_json_and_raw_rejected(self, capsys: pytest.CaptureFixture) -> None:
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

  def test_all_three_rejected(self, capsys: pytest.CaptureFixture) -> None:
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


# ── find_artifacts ──────────────────────────────────────────────


class TestFindArtifactsRevision:
  """find_artifacts for revision type — returns matching ArtifactRefs."""

  @patch("supekku.scripts.lib.changes.registry.ChangeRegistry")
  def test_finds_matching_revisions(self, mock_cls: MagicMock) -> None:
    arts = {
      "RE-001": _mock_change_artifact("RE-001", "/repo/re-001.md"),
      "RE-002": _mock_change_artifact("RE-002", "/repo/re-002.md"),
      "RE-010": _mock_change_artifact("RE-010", "/repo/re-010.md"),
    }
    mock_cls.return_value = _mock_registry_collect(arts)

    refs = list(find_artifacts("revision", "RE-00*", Path("/repo")))
    ids = [r.id for r in refs]
    assert "RE-001" in ids
    assert "RE-002" in ids
    assert "RE-010" not in ids

  @patch("supekku.scripts.lib.changes.registry.ChangeRegistry")
  def test_empty_results(self, mock_cls: MagicMock) -> None:
    mock_cls.return_value = _mock_registry_collect({})

    refs = list(find_artifacts("revision", "RE-*", Path("/repo")))
    assert refs == []

  @patch("supekku.scripts.lib.changes.registry.ChangeRegistry")
  def test_numeric_pattern_normalized(self, mock_cls: MagicMock) -> None:
    arts = {"RE-001": _mock_change_artifact("RE-001", "/repo/re.md")}
    mock_cls.return_value = _mock_registry_collect(arts)

    refs = list(find_artifacts("revision", "1", Path("/repo")))
    assert len(refs) == 1
    assert refs[0].id == "RE-001"


class TestFindArtifactsSpec:
  """find_artifacts for spec type."""

  @patch("supekku.scripts.lib.specs.registry.SpecRegistry")
  def test_finds_matching_specs(self, mock_cls: MagicMock) -> None:
    specs = [
      SimpleNamespace(id="SPEC-009", path=Path("/repo/spec-009.md")),
      SimpleNamespace(id="SPEC-010", path=Path("/repo/spec-010.md")),
      SimpleNamespace(id="PROD-001", path=Path("/repo/prod-001.md")),
    ]
    mock_cls.return_value.all_specs.return_value = specs

    refs = list(find_artifacts("spec", "SPEC-*", Path("/repo")))
    ids = [r.id for r in refs]
    assert ids == ["SPEC-009", "SPEC-010"]


class TestFindArtifactsMemory:
  """find_artifacts for memory type — auto-prepends mem. prefix."""

  @patch("supekku.scripts.lib.memory.registry.MemoryRegistry")
  def test_finds_with_prefix_normalization(self, mock_cls: MagicMock) -> None:
    records = {
      "mem.pattern.cli.skinny": SimpleNamespace(
        id="mem.pattern.cli.skinny",
        path=Path("/repo/memory/mem.pattern.cli.skinny.md"),
      ),
      "mem.fact.auth": SimpleNamespace(
        id="mem.fact.auth",
        path=Path("/repo/memory/mem.fact.auth.md"),
      ),
    }
    mock_cls.return_value.collect.return_value = records

    refs = list(find_artifacts("memory", "pattern.*", Path("/repo")))
    assert len(refs) == 1
    assert refs[0].id == "mem.pattern.cli.skinny"

  @patch("supekku.scripts.lib.memory.registry.MemoryRegistry")
  def test_pattern_already_prefixed(self, mock_cls: MagicMock) -> None:
    records = {
      "mem.fact.auth": SimpleNamespace(
        id="mem.fact.auth",
        path=Path("/repo/memory/mem.fact.auth.md"),
      ),
    }
    mock_cls.return_value.collect.return_value = records

    refs = list(find_artifacts("memory", "mem.fact.*", Path("/repo")))
    assert len(refs) == 1


class TestFindArtifactsCard:
  """find_artifacts for card type uses rglob."""

  def test_finds_matching_cards(self, tmp_path: Path) -> None:
    kanban = tmp_path / "kanban" / "doing"
    kanban.mkdir(parents=True)
    (kanban / "T001-task.md").write_text("card")
    (kanban / "T002-other.md").write_text("card")

    refs = list(find_artifacts("card", "T001", tmp_path))
    assert len(refs) == 1
    assert "T001-task.md" in str(refs[0].path)

  def test_no_matches(self, tmp_path: Path) -> None:
    refs = list(find_artifacts("card", "T999", tmp_path))
    assert refs == []


class TestFindArtifactsRequirement:
  """find_artifacts for requirement type."""

  @patch("supekku.scripts.lib.core.paths.get_registry_dir")
  @patch("supekku.scripts.lib.requirements.registry.RequirementsRegistry")
  def test_finds_matching_requirements(
    self, mock_cls: MagicMock, mock_dir: MagicMock
  ) -> None:
    mock_dir.return_value = Path("/repo/.spec-driver/registry")
    records = {
      "SPEC-009.FR-001": SimpleNamespace(
        uid="SPEC-009.FR-001", path="specify/tech/SPEC-009.md"
      ),
      "SPEC-009.FR-002": SimpleNamespace(
        uid="SPEC-009.FR-002", path="specify/tech/SPEC-009.md"
      ),
      "SPEC-010.FR-001": SimpleNamespace(
        uid="SPEC-010.FR-001", path="specify/tech/SPEC-010.md"
      ),
    }
    mock_cls.return_value.records = records

    refs = list(find_artifacts("requirement", "SPEC-009.*", Path("/repo")))
    ids = [r.id for r in refs]
    assert "SPEC-009.FR-001" in ids
    assert "SPEC-009.FR-002" in ids
    assert "SPEC-010.FR-001" not in ids

  @patch("supekku.scripts.lib.core.paths.get_registry_dir")
  @patch("supekku.scripts.lib.requirements.registry.RequirementsRegistry")
  def test_colon_normalization(self, mock_cls: MagicMock, mock_dir: MagicMock) -> None:
    """DEC-041-05: colon in pattern normalized to dot."""
    mock_dir.return_value = Path("/repo/.spec-driver/registry")
    records = {
      "SPEC-009.FR-001": SimpleNamespace(uid="SPEC-009.FR-001", path="x.md"),
    }
    mock_cls.return_value.records = records

    refs = list(find_artifacts("requirement", "SPEC-009:FR-*", Path("/repo")))
    assert len(refs) == 1


class TestFindArtifactsPlan:
  """find_artifacts for plan type scans delta dirs."""

  def test_finds_matching_plans(self, tmp_path: Path) -> None:
    d1 = tmp_path / "change" / "deltas" / "DE-041-slug"
    d1.mkdir(parents=True)
    (d1 / "IP-041.md").write_text(
      "---\nid: IP-041\nname: P1\nstatus: draft\nkind: plan\n---\n",
    )
    d2 = tmp_path / "change" / "deltas" / "DE-042-other"
    d2.mkdir(parents=True)
    (d2 / "IP-042.md").write_text(
      "---\nid: IP-042\nname: P2\nstatus: draft\nkind: plan\n---\n",
    )

    refs = list(find_artifacts("plan", "IP-04*", tmp_path))
    ids = {r.id for r in refs}
    assert "IP-041" in ids
    assert "IP-042" in ids

  def test_numeric_shorthand_pattern(self, tmp_path: Path) -> None:
    d = tmp_path / "change" / "deltas" / "DE-041-slug"
    d.mkdir(parents=True)
    (d / "IP-041.md").write_text(
      "---\nid: IP-041\nstatus: draft\nkind: plan\n---\n",
    )
    refs = list(find_artifacts("plan", "41", tmp_path))
    assert len(refs) == 1

  def test_no_deltas_dir(self, tmp_path: Path) -> None:
    refs = list(find_artifacts("plan", "IP-*", tmp_path))
    assert refs == []


class TestFindArtifactsBacklog:
  """find_artifacts for backlog types uses discover_backlog_items."""

  def _create_item(self, root: Path, subdir: str, item_id: str) -> None:
    entry_dir = root / "backlog" / subdir / f"{item_id}-test"
    entry_dir.mkdir(parents=True, exist_ok=True)
    kind = subdir.rstrip("s")
    fm = f"---\nid: {item_id}\nname: test\nkind: {kind}\nstatus: open\n---\n"
    (entry_dir / f"{item_id}.md").write_text(fm)

  @pytest.mark.parametrize(
    ("artifact_type", "subdir", "item_id"),
    [
      ("issue", "issues", "ISSUE-001"),
      ("problem", "problems", "PROB-001"),
      ("improvement", "improvements", "IMPR-001"),
      ("risk", "risks", "RISK-001"),
    ],
  )
  def test_finds_backlog_items(
    self, tmp_path: Path, artifact_type: str, subdir: str, item_id: str
  ) -> None:
    (tmp_path / ".git").mkdir()
    self._create_item(tmp_path, subdir, item_id)
    refs = list(find_artifacts(artifact_type, f"{item_id[:4]}*", tmp_path))
    assert len(refs) >= 1
    assert any(r.id == item_id for r in refs)

  def test_no_matches(self, tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    refs = list(find_artifacts("issue", "ISSUE-999", tmp_path))
    assert refs == []


class TestFindArtifactsUnsupportedType:
  """find_artifacts raises ValueError for unknown types."""

  def test_raises_value_error(self) -> None:
    with pytest.raises(ValueError, match="Unknown artifact type"):
      list(find_artifacts("bogus", "*", Path("/repo")))
