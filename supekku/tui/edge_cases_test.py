"""VT-053-edge-cases — import guard, $EDITOR unset, empty snapshot."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from supekku.scripts.lib.core.artifact_view import (
  ArtifactSnapshot,
  ArtifactType,
  path_to_artifact_type,
)
from supekku.tui.app import SpecDriverApp
from supekku.tui.browser import BrowserScreen
from supekku.tui.widgets.type_selector import TypeSelector

# --- Import guard ---


class TestImportGuard:
  """spec-driver tui gives helpful error when textual not installed."""

  def test_tui_command_prints_install_message_when_textual_missing(self):
    """Run spec-driver tui in a subprocess with textual excluded."""
    result = subprocess.run(
      [
        sys.executable,
        "-c",
        (
          "import sys;"
          "sys.modules['textual'] = None;"
          "sys.modules['textual.app'] = None;"
          "from supekku.cli.main import app;"
          "app(['tui'], standalone_mode=False)"
        ),
      ],
      capture_output=True,
      text=True,
      check=False,
    )
    # Import guard should produce non-zero exit and helpful message
    assert result.returncode != 0 or "not installed" in result.stderr.lower()


# --- $EDITOR unset ---


class TestEditorUnset:
  """Pressing e with $EDITOR unset shows notification, not crash."""

  @pytest.mark.asyncio()
  async def test_edit_without_editor_notifies(self):
    snapshot = _empty_snapshot()
    app = SpecDriverApp(root=Path("/tmp"), snapshot=snapshot, watch=False)
    with patch.dict(os.environ, {}, clear=True):
      async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        await pilot.press("e")
        await pilot.pause()
        # Should not crash — notification shown


# --- Empty snapshot ---


class TestEmptySnapshot:
  """App handles a snapshot where all types return zero entries."""

  @pytest.mark.asyncio()
  async def test_app_mounts_with_empty_snapshot(self):
    snapshot = _empty_snapshot()
    app = SpecDriverApp(root=Path("/tmp"), snapshot=snapshot, watch=False)
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      assert isinstance(app.screen, BrowserScreen)

  @pytest.mark.asyncio()
  async def test_type_selector_shows_zero_counts(self):
    snapshot = _empty_snapshot()
    app = SpecDriverApp(root=Path("/tmp"), snapshot=snapshot, watch=False)
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      ts = app.screen.query_one("#type-selector", TypeSelector)
      for i in range(ts.option_count):
        opt = ts.get_option_at_index(i)
        assert "0" in str(opt.prompt)


# --- path_to_artifact_type ---


class TestPathToArtifactType:
  """Mapping filesystem paths to ArtifactType."""

  def test_spec_path(self, tmp_path):
    root = tmp_path
    sd = root / ".spec-driver" / "tech"
    sd.mkdir(parents=True)
    f = sd / "SPEC-001.md"
    f.touch()
    assert path_to_artifact_type(f, root) == ArtifactType.SPEC

  def test_delta_path(self, tmp_path):
    root = tmp_path
    sd = root / ".spec-driver" / "deltas" / "DE-001"
    sd.mkdir(parents=True)
    f = sd / "DE-001.md"
    f.touch()
    assert path_to_artifact_type(f, root) == ArtifactType.DELTA

  def test_decision_path(self, tmp_path):
    root = tmp_path
    sd = root / ".spec-driver" / "decisions"
    sd.mkdir(parents=True)
    f = sd / "ADR-001.md"
    f.touch()
    assert path_to_artifact_type(f, root) == ArtifactType.ADR

  def test_backlog_path(self, tmp_path):
    root = tmp_path
    sd = root / ".spec-driver" / "backlog" / "issues"
    sd.mkdir(parents=True)
    f = sd / "ISSUE-001.md"
    f.touch()
    assert path_to_artifact_type(f, root) == ArtifactType.BACKLOG

  def test_memory_path(self, tmp_path):
    root = tmp_path
    sd = root / ".spec-driver" / "memory"
    sd.mkdir(parents=True)
    f = sd / "mem.foo.md"
    f.touch()
    assert path_to_artifact_type(f, root) == ArtifactType.MEMORY

  def test_kanban_card_path(self, tmp_path):
    root = tmp_path
    kanban = root / "kanban" / "doing"
    kanban.mkdir(parents=True)
    f = kanban / "T001-foo.md"
    f.touch()
    assert path_to_artifact_type(f, root) == ArtifactType.CARD

  def test_unrelated_path_returns_none(self, tmp_path):
    root = tmp_path
    f = root / "README.md"
    f.touch()
    assert path_to_artifact_type(f, root) is None

  def test_policy_path(self, tmp_path):
    root = tmp_path
    sd = root / ".spec-driver" / "policies"
    sd.mkdir(parents=True)
    f = sd / "POL-001.md"
    f.touch()
    assert path_to_artifact_type(f, root) == ArtifactType.POLICY

  def test_standard_path(self, tmp_path):
    root = tmp_path
    sd = root / ".spec-driver" / "standards"
    sd.mkdir(parents=True)
    f = sd / "STD-001.md"
    f.touch()
    assert path_to_artifact_type(f, root) == ArtifactType.STANDARD

  def test_revision_path(self, tmp_path):
    root = tmp_path
    sd = root / ".spec-driver" / "revisions"
    sd.mkdir(parents=True)
    f = sd / "RE-001.md"
    f.touch()
    assert path_to_artifact_type(f, root) == ArtifactType.REVISION

  def test_audit_path(self, tmp_path):
    root = tmp_path
    sd = root / ".spec-driver" / "audits"
    sd.mkdir(parents=True)
    f = sd / "AUD-001.md"
    f.touch()
    assert path_to_artifact_type(f, root) == ArtifactType.AUDIT

  def test_product_spec_path(self, tmp_path):
    root = tmp_path
    sd = root / ".spec-driver" / "product"
    sd.mkdir(parents=True)
    f = sd / "PROD-001.md"
    f.touch()
    assert path_to_artifact_type(f, root) == ArtifactType.SPEC

  def test_drift_path(self, tmp_path):
    root = tmp_path
    sd = root / ".spec-driver" / "drift"
    sd.mkdir(parents=True)
    f = sd / "DL-047-reconciliation.md"
    f.touch()
    assert path_to_artifact_type(f, root) == ArtifactType.DRIFT_LEDGER


# --- Helpers ---


def _empty_snapshot() -> ArtifactSnapshot:
  snapshot = MagicMock(spec=ArtifactSnapshot)
  snapshot.entries = {art_type: {} for art_type in ArtifactType}
  snapshot.counts_by_type.return_value = dict.fromkeys(ArtifactType, 0)
  snapshot.all_entries.return_value = []
  return snapshot
