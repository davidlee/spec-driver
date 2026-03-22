"""Tests for edit command."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from supekku.cli.common import get_editor
from supekku.cli.edit import app
from supekku.scripts.lib.core.repo import find_repo_root

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

  def test_edit_adr_calls_editor(self, tmp_path: Path) -> None:
    """Edit adr opens file in editor."""
    with patch("supekku.cli.edit.DecisionRegistry") as mock_registry_class:
      mock_registry = MagicMock()
      mock_decision = MagicMock()
      mock_decision.path = tmp_path / "test.md"
      mock_decision.path.write_text("# Test ADR\n")
      mock_registry.find.return_value = mock_decision
      mock_registry_class.return_value = mock_registry

      with patch("supekku.cli.edit.open_in_editor") as mock_open:
        result = runner.invoke(app, ["adr", "ADR-001"])
        assert result.exit_code == 0
        mock_open.assert_called_once_with(mock_decision.path)

  def test_edit_adr_not_found(self) -> None:
    """Edit adr shows error when not found."""
    with patch("supekku.cli.edit.DecisionRegistry") as mock_registry_class:
      mock_registry = MagicMock()
      mock_registry.find.return_value = None
      mock_registry_class.return_value = mock_registry

      result = runner.invoke(app, ["adr", "ADR-999"])
      assert result.exit_code == 1
      assert "not found" in result.output.lower()


class TestEditSpec:
  """Tests for edit spec command."""

  def test_edit_spec_calls_editor(self, tmp_path: Path) -> None:
    """Edit spec opens file in editor."""
    with patch("supekku.cli.edit.SpecRegistry") as mock_registry_class:
      mock_registry = MagicMock()
      mock_spec = MagicMock()
      mock_spec.path = tmp_path / "spec.md"
      mock_spec.path.write_text("# Test Spec\n")
      mock_registry.get.return_value = mock_spec
      mock_registry_class.return_value = mock_registry

      with patch("supekku.cli.edit.open_in_editor") as mock_open:
        result = runner.invoke(app, ["spec", "SPEC-001"])
        assert result.exit_code == 0
        mock_open.assert_called_once()


class TestEditDelta:
  """Tests for edit delta command."""

  def test_edit_delta_calls_editor(self, tmp_path: Path) -> None:
    """Edit delta opens file in editor."""
    with patch("supekku.cli.edit.ChangeRegistry") as mock_registry_class:
      mock_registry = MagicMock()
      mock_artifact = MagicMock()
      mock_artifact.path = tmp_path / "delta.md"
      mock_artifact.path.write_text("# Test Delta\n")
      mock_registry.collect.return_value = {"DE-001": mock_artifact}
      mock_registry_class.return_value = mock_registry

      with patch("supekku.cli.edit.open_in_editor") as mock_open:
        result = runner.invoke(app, ["delta", "DE-001"])
        assert result.exit_code == 0
        mock_open.assert_called_once()


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

      with patch("supekku.cli.io.get_editor", return_value=None):
        result = runner.invoke(app, ["adr", "ADR-001"])
        assert result.exit_code == 1
        assert "editor" in result.output.lower()


class TestEditAdrShorthand:
  """Tests for edit adr with shorthand IDs."""

  def test_edit_adr_numeric_shorthand(self, tmp_path: Path) -> None:
    """Edit adr accepts numeric shorthand like '001'."""
    with patch("supekku.cli.edit.DecisionRegistry") as mock_registry_class:
      mock_registry = MagicMock()
      mock_decision = MagicMock()
      mock_decision.path = tmp_path / "test.md"
      mock_decision.path.write_text("# Test ADR\n")
      mock_registry.find.return_value = mock_decision
      mock_registry_class.return_value = mock_registry

      with patch("supekku.cli.edit.open_in_editor"):
        result = runner.invoke(app, ["adr", "001"])
        assert result.exit_code == 0
        # Verify registry was called with normalized ID
        mock_registry.find.assert_called_once_with("ADR-001")


class TestEditDeltaShorthand:
  """Tests for edit delta with shorthand IDs."""

  def test_edit_delta_numeric_shorthand(self, tmp_path: Path) -> None:
    """Edit delta accepts numeric shorthand like '23'."""
    with patch("supekku.cli.edit.ChangeRegistry") as mock_registry_class:
      mock_registry = MagicMock()
      mock_artifact = MagicMock()
      mock_artifact.path = tmp_path / "delta.md"
      mock_artifact.path.write_text("# Test Delta\n")
      mock_registry.collect.return_value = {"DE-023": mock_artifact}
      mock_registry_class.return_value = mock_registry

      with patch("supekku.cli.edit.open_in_editor"):
        result = runner.invoke(app, ["delta", "23"])
        assert result.exit_code == 0


# ── Pre-migration regression tests for edit revision (VT-migration) ──


class TestEditRevisionRegression:
  """Regression tests for edit revision — must pass before AND after migration."""

  def test_edit_revision_invokes_editor(self) -> None:
    """edit revision RE-001 opens editor with correct file."""
    root = find_repo_root()
    rev_paths = list(root.glob("change/revisions/RE-001-*/RE-001.md"))
    if not rev_paths:
      pytest.skip("RE-001 not found")

    with patch("supekku.cli.edit.open_in_editor") as mock_open:
      result = runner.invoke(app, ["revision", "RE-001"])
      assert result.exit_code == 0
      mock_open.assert_called_once()
      call_path = mock_open.call_args[0][0]
      assert str(call_path).endswith(".md")

  def test_edit_revision_numeric_shorthand(self) -> None:
    """edit revision 1 resolves to RE-001."""
    with patch("supekku.cli.edit.open_in_editor"):
      result = runner.invoke(app, ["revision", "1"])
      assert result.exit_code == 0

  def test_edit_revision_not_found(self) -> None:
    """edit revision with nonexistent ID fails gracefully."""
    result = runner.invoke(app, ["revision", "RE-999"])
    assert result.exit_code == 1
    assert "not found" in result.stderr.lower()


class TestEditNewSubcommands:
  """Tests for Phase 2 edit subcommands using mocked resolution."""

  def test_edit_plan(self, tmp_path: Path) -> None:
    plan_file = tmp_path / "IP-001.md"
    plan_file.write_text("# Plan\n")
    ref = MagicMock(id="IP-001", path=plan_file)
    with (
      patch("supekku.cli.edit.resolve_artifact", return_value=ref),
      patch("supekku.cli.edit.open_in_editor") as mock_open,
    ):
      result = runner.invoke(app, ["plan", "IP-001"])
      assert result.exit_code == 0
      mock_open.assert_called_once_with(plan_file)

  def test_edit_plan_not_found(self) -> None:
    from supekku.cli.common import ArtifactNotFoundError  # noqa: PLC0415

    with patch(
      "supekku.cli.edit.resolve_artifact",
      side_effect=ArtifactNotFoundError("plan", "IP-999"),
    ):
      result = runner.invoke(app, ["plan", "IP-999"])
      assert result.exit_code == 1

  def test_edit_audit(self, tmp_path: Path) -> None:
    audit_file = tmp_path / "AUD-001.md"
    audit_file.write_text("# Audit\n")
    ref = MagicMock(id="AUD-001", path=audit_file)
    with (
      patch("supekku.cli.edit.resolve_artifact", return_value=ref),
      patch("supekku.cli.edit.open_in_editor") as mock_open,
    ):
      result = runner.invoke(app, ["audit", "AUD-001"])
      assert result.exit_code == 0
      mock_open.assert_called_once_with(audit_file)

  def test_edit_issue(self, tmp_path: Path) -> None:
    issue_file = tmp_path / "ISSUE-001.md"
    issue_file.write_text("# Issue\n")
    ref = MagicMock(id="ISSUE-001", path=issue_file)
    with (
      patch("supekku.cli.edit.resolve_artifact", return_value=ref),
      patch("supekku.cli.edit.open_in_editor") as mock_open,
    ):
      result = runner.invoke(app, ["issue", "ISSUE-001"])
      assert result.exit_code == 0
      mock_open.assert_called_once_with(issue_file)

  def test_edit_improvement(self, tmp_path: Path) -> None:
    impr_file = tmp_path / "IMPR-001.md"
    impr_file.write_text("# Improvement\n")
    ref = MagicMock(id="IMPR-001", path=impr_file)
    with (
      patch("supekku.cli.edit.resolve_artifact", return_value=ref),
      patch("supekku.cli.edit.open_in_editor") as mock_open,
    ):
      result = runner.invoke(app, ["improvement", "IMPR-001"])
      assert result.exit_code == 0
      mock_open.assert_called_once_with(impr_file)


# ── --status flag tests (DE-068, VT-068-02, VT-068-03) ──

DELTA_FRONTMATTER = """\
---
id: DE-001
name: Test Delta
status: draft
kind: delta
created: '2026-01-01'
updated: '2026-01-01'
---

# DE-001 – Test Delta
"""


class TestEditStatusFlag:
  """Tests for --status flag on edit subcommands."""

  def test_status_updates_frontmatter_skips_editor(self, tmp_path: Path) -> None:
    """--status updates file and does not open editor."""
    delta_file = tmp_path / "DE-001.md"
    delta_file.write_text(DELTA_FRONTMATTER)
    mock_artifact = MagicMock()
    mock_artifact.path = delta_file

    with (
      patch("supekku.cli.edit.ChangeRegistry") as mock_cls,
      patch("supekku.cli.edit.open_in_editor") as mock_open,
    ):
      mock_registry = MagicMock()
      mock_registry.collect.return_value = {"DE-001": mock_artifact}
      mock_cls.return_value = mock_registry

      result = runner.invoke(app, ["delta", "DE-001", "--status", "in-progress"])
      assert result.exit_code == 0
      assert "in-progress" in result.output
      mock_open.assert_not_called()

    content = delta_file.read_text()
    assert "status: in-progress" in content
    assert "status: draft" not in content

  def test_status_rejects_invalid_value_for_delta(self, tmp_path: Path) -> None:
    """--status with invalid value for enum-covered entity type fails."""
    delta_file = tmp_path / "DE-001.md"
    delta_file.write_text(DELTA_FRONTMATTER)
    mock_artifact = MagicMock()
    mock_artifact.path = delta_file

    with patch("supekku.cli.edit.ChangeRegistry") as mock_cls:
      mock_registry = MagicMock()
      mock_registry.collect.return_value = {"DE-001": mock_artifact}
      mock_cls.return_value = mock_registry

      result = runner.invoke(app, ["delta", "DE-001", "--status", "bogus"])
      assert result.exit_code == 1
      assert "Invalid status" in result.output
      assert "Valid values" in result.output

    # File should be unchanged
    assert "status: draft" in delta_file.read_text()

  def test_status_accepts_valid_value_for_spec(self, tmp_path: Path) -> None:
    """--status with a valid spec status succeeds."""
    spec_file = tmp_path / "SPEC-001.md"
    spec_file.write_text(
      "---\nid: SPEC-001\nname: Test\nstatus: draft\n"
      "updated: '2026-01-01'\n---\n# Spec\n"
    )
    mock_spec = MagicMock()
    mock_spec.path = spec_file

    with patch("supekku.cli.edit.SpecRegistry") as mock_cls:
      mock_registry = MagicMock()
      mock_registry.get.return_value = mock_spec
      mock_cls.return_value = mock_registry

      result = runner.invoke(app, ["spec", "SPEC-001", "--status", "active"])
      assert result.exit_code == 0

    assert "status: active" in spec_file.read_text()

  def test_status_rejects_invalid_value_for_spec(self, tmp_path: Path) -> None:
    """--status with invalid spec status fails."""
    spec_file = tmp_path / "SPEC-001.md"
    spec_file.write_text(
      "---\nid: SPEC-001\nname: Test\nstatus: draft\n"
      "updated: '2026-01-01'\n---\n# Spec\n"
    )
    mock_spec = MagicMock()
    mock_spec.path = spec_file

    with patch("supekku.cli.edit.SpecRegistry") as mock_cls:
      mock_registry = MagicMock()
      mock_registry.get.return_value = mock_spec
      mock_cls.return_value = mock_registry

      result = runner.invoke(app, ["spec", "SPEC-001", "--status", "anything-goes"])
      assert result.exit_code != 0

  def test_status_rejects_empty_value(self, tmp_path: Path) -> None:
    """--status with empty string fails."""
    delta_file = tmp_path / "DE-001.md"
    delta_file.write_text(DELTA_FRONTMATTER)
    mock_artifact = MagicMock()
    mock_artifact.path = delta_file

    with patch("supekku.cli.edit.ChangeRegistry") as mock_cls:
      mock_registry = MagicMock()
      mock_registry.collect.return_value = {"DE-001": mock_artifact}
      mock_cls.return_value = mock_registry

      result = runner.invoke(app, ["delta", "DE-001", "--status", ""], input="")
      assert result.exit_code == 1
      assert (
        "empty" in result.output.lower() or "empty" in (result.stderr or "").lower()
      )

  def test_without_status_opens_editor(self, tmp_path: Path) -> None:
    """Default behaviour (no --status) still opens editor."""
    delta_file = tmp_path / "DE-001.md"
    delta_file.write_text(DELTA_FRONTMATTER)
    mock_artifact = MagicMock()
    mock_artifact.path = delta_file

    with (
      patch("supekku.cli.edit.ChangeRegistry") as mock_cls,
      patch("supekku.cli.edit.open_in_editor") as mock_open,
    ):
      mock_registry = MagicMock()
      mock_registry.collect.return_value = {"DE-001": mock_artifact}
      mock_cls.return_value = mock_registry

      result = runner.invoke(app, ["delta", "DE-001"])
      assert result.exit_code == 0
      mock_open.assert_called_once()


class TestEditStatusResolveArtifact:
  """Tests for --status on resolve_artifact-based subcommands."""

  def test_issue_status_update(self, tmp_path: Path) -> None:
    issue_file = tmp_path / "ISSUE-001.md"
    issue_file.write_text(
      "---\nid: ISSUE-001\nname: Test\nstatus: open\n"
      "updated: '2026-01-01'\n---\n# Issue\n"
    )
    ref = MagicMock(id="ISSUE-001", path=issue_file)
    with patch("supekku.cli.edit.resolve_artifact", return_value=ref):
      result = runner.invoke(app, ["issue", "ISSUE-001", "--status", "in-progress"])
      assert result.exit_code == 0
    assert "status: in-progress" in issue_file.read_text()

  def test_issue_status_rejects_invalid(self, tmp_path: Path) -> None:
    issue_file = tmp_path / "ISSUE-001.md"
    issue_file.write_text(
      "---\nid: ISSUE-001\nname: Test\nstatus: open\n"
      "updated: '2026-01-01'\n---\n# Issue\n"
    )
    ref = MagicMock(id="ISSUE-001", path=issue_file)
    with patch("supekku.cli.edit.resolve_artifact", return_value=ref):
      result = runner.invoke(app, ["issue", "ISSUE-001", "--status", "bogus"])
      assert result.exit_code == 1
    assert "status: open" in issue_file.read_text()


class TestEditDrift:
  """Tests for edit drift subcommand (new in DE-068)."""

  def test_edit_drift_opens_editor(self, tmp_path: Path) -> None:
    ledger_file = tmp_path / "DL-001.md"
    ledger_file.write_text("---\nstatus: open\n---\n# Ledger\n")
    ref = MagicMock(id="DL-001", path=ledger_file)
    with (
      patch("supekku.cli.edit.resolve_artifact", return_value=ref),
      patch("supekku.cli.edit.open_in_editor") as mock_open,
    ):
      result = runner.invoke(app, ["drift", "DL-001"])
      assert result.exit_code == 0
      mock_open.assert_called_once_with(ledger_file)

  def test_edit_drift_status_update(self, tmp_path: Path) -> None:
    ledger_file = tmp_path / "DL-001.md"
    ledger_file.write_text(
      "---\nid: DL-001\nstatus: open\nupdated: '2026-01-01'\n---\n# Ledger\n"
    )
    ref = MagicMock(id="DL-001", path=ledger_file)
    with patch("supekku.cli.edit.resolve_artifact", return_value=ref):
      result = runner.invoke(app, ["drift", "DL-001", "--status", "closed"])
      assert result.exit_code == 0
    assert "status: closed" in ledger_file.read_text()

  def test_edit_drift_rejects_invalid_status(self, tmp_path: Path) -> None:
    ledger_file = tmp_path / "DL-001.md"
    ledger_file.write_text(
      "---\nid: DL-001\nstatus: open\nupdated: '2026-01-01'\n---\n# Ledger\n"
    )
    ref = MagicMock(id="DL-001", path=ledger_file)
    with patch("supekku.cli.edit.resolve_artifact", return_value=ref):
      result = runner.invoke(app, ["drift", "DL-001", "--status", "bogus"])
      assert result.exit_code == 1
      assert "Invalid status" in result.output
    assert "status: open" in ledger_file.read_text()

  def test_edit_drift_resolver_key(self, tmp_path: Path) -> None:
    """Drift uses 'drift_ledger' resolver key, not 'drift'."""
    ledger_file = tmp_path / "DL-001.md"
    ledger_file.write_text("---\nstatus: open\n---\n# Ledger\n")
    ref = MagicMock(id="DL-001", path=ledger_file)
    with (
      patch("supekku.cli.edit.resolve_artifact", return_value=ref) as mock_resolve,
      patch("supekku.cli.edit.open_in_editor"),
    ):
      runner.invoke(app, ["drift", "DL-001"])
      mock_resolve.assert_called_once()
      call_args = mock_resolve.call_args[0]
      assert call_args[0] == "drift_ledger"
      assert call_args[1] == "DL-001"


# ── --verify flag tests (DE-086, VT-cli-edit-verify) ──

MEMORY_FRONTMATTER = """\
---
id: mem.test.pattern
name: Test Pattern
status: active
kind: memory
memory_type: pattern
created: '2026-03-01'
updated: '2026-03-01'
verified: '2026-03-01'
confidence: medium
---

# Test Memory
"""


class TestEditMemoryVerify:
  """Tests for --verify flag on edit memory command."""

  def test_verify_stamps_sha_and_dates(self, tmp_path: Path) -> None:
    """--verify stamps verified, verified_sha, updated in frontmatter."""
    mem_file = tmp_path / "mem.test.pattern.md"
    mem_file.write_text(MEMORY_FRONTMATTER)
    ref = MagicMock(id="mem.test.pattern", path=mem_file)
    fake_sha = "a" * 40

    with (
      patch("supekku.cli.edit.resolve_artifact", return_value=ref),
      patch("supekku.cli.edit.get_head_sha", return_value=fake_sha),
    ):
      result = runner.invoke(app, ["memory", "mem.test.pattern", "--verify"])

    assert result.exit_code == 0
    assert "Verified" in result.output
    assert "aaaaaaaa" in result.output  # short_sha

    content = mem_file.read_text()
    assert f"verified_sha: {fake_sha}" in content
    assert "verified: '2026-03-01'" not in content  # date was updated

  def test_verify_refuses_without_git(self, tmp_path: Path) -> None:
    """--verify refuses when git is unavailable."""
    mem_file = tmp_path / "mem.test.pattern.md"
    mem_file.write_text(MEMORY_FRONTMATTER)
    ref = MagicMock(id="mem.test.pattern", path=mem_file)

    with (
      patch("supekku.cli.edit.resolve_artifact", return_value=ref),
      patch("supekku.cli.edit.get_head_sha", return_value=None),
    ):
      result = runner.invoke(app, ["memory", "mem.test.pattern", "--verify"])

    assert result.exit_code == 1
    assert "git" in result.output.lower() or "git" in (result.stderr or "").lower()

  def test_verify_mutex_with_status(self) -> None:
    """--verify and --status are mutually exclusive."""
    ref = MagicMock(id="mem.test.pattern", path=Path("/fake.md"))

    with patch("supekku.cli.edit.resolve_artifact", return_value=ref):
      result = runner.invoke(
        app, ["memory", "mem.test.pattern", "--verify", "--status", "deprecated"]
      )

    assert result.exit_code == 1
    output = result.output.lower()
    assert "mutually exclusive" in output or "cannot" in output

  def test_verify_without_existing_sha_inserts_field(self, tmp_path: Path) -> None:
    """--verify inserts verified_sha when not present in frontmatter."""
    mem_file = tmp_path / "mem.test.pattern.md"
    mem_file.write_text(MEMORY_FRONTMATTER)
    ref = MagicMock(id="mem.test.pattern", path=mem_file)
    fake_sha = "b" * 40

    with (
      patch("supekku.cli.edit.resolve_artifact", return_value=ref),
      patch("supekku.cli.edit.get_head_sha", return_value=fake_sha),
    ):
      result = runner.invoke(app, ["memory", "mem.test.pattern", "--verify"])

    assert result.exit_code == 0
    content = mem_file.read_text()
    assert f"verified_sha: {fake_sha}" in content

  def test_verify_does_not_open_editor(self, tmp_path: Path) -> None:
    """--verify does not open the editor."""
    mem_file = tmp_path / "mem.test.pattern.md"
    mem_file.write_text(MEMORY_FRONTMATTER)
    ref = MagicMock(id="mem.test.pattern", path=mem_file)
    fake_sha = "c" * 40

    with (
      patch("supekku.cli.edit.resolve_artifact", return_value=ref),
      patch("supekku.cli.edit.get_head_sha", return_value=fake_sha),
      patch("supekku.cli.edit.open_in_editor") as mock_open,
    ):
      result = runner.invoke(app, ["memory", "mem.test.pattern", "--verify"])

    assert result.exit_code == 0
    mock_open.assert_not_called()
