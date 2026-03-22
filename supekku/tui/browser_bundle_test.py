"""VT-061-02 — BrowserScreen bundle tree integration tests."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from rich.text import Text
from textual.widgets import DataTable

from supekku.scripts.lib.core.artifact_view import (
  ArtifactEntry,
  ArtifactSnapshot,
  ArtifactType,
)
from supekku.tui.app import SpecDriverApp
from supekku.tui.browser import BrowserScreen
from supekku.tui.widgets.bundle_tree import BundleTree
from supekku.tui.widgets.preview_panel import PreviewPanel
from supekku.tui.widgets.type_selector import TypeSelector


def _plain(label: str | Text) -> str:
  """Extract plain text from a tree node label."""
  return label.plain if isinstance(label, Text) else label


# --- Fixtures ---


@pytest.fixture()
def bundle_dir(tmp_path: Path) -> Path:
  """Create a realistic delta bundle directory."""
  bd = tmp_path / "DE-061-tui_bundle_file_browser"
  bd.mkdir()
  (bd / "DE-061.md").write_text("# Delta\n\nDelta content.", encoding="utf-8")
  (bd / "DR-061.md").write_text("# Design\n\nDesign content.", encoding="utf-8")
  (bd / "IP-061.md").write_text("# Plan\n\nPlan content.", encoding="utf-8")
  phases = bd / "phases"
  phases.mkdir()
  (phases / "phase-01.md").write_text("# Phase 1\n", encoding="utf-8")
  return bd


def _make_entries(
  tmp_path: Path, bundle_dir: Path | None = None
) -> dict[ArtifactType, dict[str, ArtifactEntry]]:
  """Build test entries — one bundle delta, one non-bundle ADR."""
  adr_file = tmp_path / "ADR-001.md"
  adr_file.write_text("# ADR\n\nSome decision.", encoding="utf-8")

  entries: dict[ArtifactType, dict[str, ArtifactEntry]] = {}
  for art_type in ArtifactType:
    entries[art_type] = {}

  entries[ArtifactType.ADR]["ADR-001"] = ArtifactEntry(
    id="ADR-001",
    title="Test ADR",
    status="accepted",
    path=adr_file,
    artifact_type=ArtifactType.ADR,
  )

  if bundle_dir is not None:
    entries[ArtifactType.DELTA]["DE-061"] = ArtifactEntry(
      id="DE-061",
      title="TUI bundle browser",
      status="in-progress",
      path=bundle_dir / "DE-061.md",
      artifact_type=ArtifactType.DELTA,
      bundle_dir=bundle_dir,
    )

  return entries


def _mock_snapshot(
  entries: dict[ArtifactType, dict[str, ArtifactEntry]],
) -> ArtifactSnapshot:
  """Create a mock ArtifactSnapshot."""
  snapshot = MagicMock(spec=ArtifactSnapshot)
  snapshot.entries = entries
  snapshot.counts_by_type.return_value = {
    art_type: len(entries[art_type]) for art_type in ArtifactType
  }
  snapshot.all_entries.side_effect = lambda **kw: list(
    entries.get(kw.get("type_filter", ArtifactType.ADR), {}).values()
  )

  def find_entry(artifact_id: str) -> ArtifactEntry | None:
    for type_entries in entries.values():
      if artifact_id in type_entries:
        return type_entries[artifact_id]
    return None

  snapshot.find_entry.side_effect = find_entry
  return snapshot


def _make_app(snapshot: ArtifactSnapshot) -> SpecDriverApp:
  return SpecDriverApp(root=Path("/tmp"), snapshot=snapshot, listen=False)


# --- Layout tests (2.1) ---


class TestLeftColumnLayout:
  """BrowserScreen composes #left-column with TypeSelector + BundleTree."""

  @pytest.mark.asyncio()
  async def test_left_column_exists(self, tmp_path: Path) -> None:
    entries = _make_entries(tmp_path)
    app = _make_app(_mock_snapshot(entries))
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      left = app.screen.query_one("#left-column")
      assert left is not None

  @pytest.mark.asyncio()
  async def test_type_selector_inside_left_column(self, tmp_path: Path) -> None:
    entries = _make_entries(tmp_path)
    app = _make_app(_mock_snapshot(entries))
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      left = app.screen.query_one("#left-column")
      ts = left.query_one("#type-selector", TypeSelector)
      assert ts is not None

  @pytest.mark.asyncio()
  async def test_bundle_tree_inside_left_column(self, tmp_path: Path) -> None:
    entries = _make_entries(tmp_path)
    app = _make_app(_mock_snapshot(entries))
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      left = app.screen.query_one("#left-column")
      tree = left.query_one("#bundle-tree", BundleTree)
      assert tree is not None

  @pytest.mark.asyncio()
  async def test_bundle_tree_hidden_by_default(self, tmp_path: Path) -> None:
    entries = _make_entries(tmp_path)
    app = _make_app(_mock_snapshot(entries))
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      tree = app.screen.query_one("#bundle-tree", BundleTree)
      assert not tree.display


# --- Tree visibility on artifact selection (2.3) ---


class TestTreeVisibility:
  """Tree shows for bundle artifacts, hides for non-bundle."""

  @pytest.mark.asyncio()
  async def test_bundle_artifact_shows_tree(
    self, tmp_path: Path, bundle_dir: Path
  ) -> None:
    entries = _make_entries(tmp_path, bundle_dir)
    app = _make_app(_mock_snapshot(entries))
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()

      # Select DELTA type
      ts = app.screen.query_one("#type-selector", TypeSelector)
      delta_idx = ts.get_option_index(ArtifactType.DELTA.value)
      ts.highlighted = delta_idx
      ts.action_select()
      await pilot.pause()

      # Select the delta row
      table = app.screen.query_one("#artifact-table", DataTable)
      table.focus()
      await pilot.pause()
      table.move_cursor(row=0)
      await pilot.press("enter")
      await pilot.pause()

      # Tree should be visible
      tree = app.screen.query_one("#bundle-tree", BundleTree)
      assert tree.display
      left = app.screen.query_one("#left-column")
      assert left.has_class("has-bundle")

  @pytest.mark.asyncio()
  async def test_non_bundle_artifact_hides_tree(
    self, tmp_path: Path, bundle_dir: Path
  ) -> None:
    entries = _make_entries(tmp_path, bundle_dir)
    app = _make_app(_mock_snapshot(entries))
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()

      # First show bundle tree by selecting delta
      ts = app.screen.query_one("#type-selector", TypeSelector)
      delta_idx = ts.get_option_index(ArtifactType.DELTA.value)
      ts.highlighted = delta_idx
      ts.action_select()
      await pilot.pause()
      table = app.screen.query_one("#artifact-table", DataTable)
      table.focus()
      await pilot.pause()
      table.move_cursor(row=0)
      await pilot.press("enter")
      await pilot.pause()

      # Now switch to ADR type (non-bundle)
      ts.highlighted = ts.get_option_index(ArtifactType.ADR.value)
      ts.action_select()
      await pilot.pause()
      table.move_cursor(row=0)
      await pilot.press("enter")
      await pilot.pause()

      tree = app.screen.query_one("#bundle-tree", BundleTree)
      assert not tree.display
      left = app.screen.query_one("#left-column")
      assert not left.has_class("has-bundle")

  @pytest.mark.asyncio()
  async def test_type_change_clears_tree(
    self, tmp_path: Path, bundle_dir: Path
  ) -> None:
    entries = _make_entries(tmp_path, bundle_dir)
    app = _make_app(_mock_snapshot(entries))
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()

      # Show tree via delta
      ts = app.screen.query_one("#type-selector", TypeSelector)
      delta_idx = ts.get_option_index(ArtifactType.DELTA.value)
      ts.highlighted = delta_idx
      ts.action_select()
      await pilot.pause()
      table = app.screen.query_one("#artifact-table", DataTable)
      table.focus()
      await pilot.pause()
      table.move_cursor(row=0)
      await pilot.press("enter")
      await pilot.pause()

      # Switch type
      ts.highlighted = ts.get_option_index(ArtifactType.ADR.value)
      ts.action_select()
      await pilot.pause()

      tree = app.screen.query_one("#bundle-tree", BundleTree)
      assert tree.bundle_dir is None
      left = app.screen.query_one("#left-column")
      assert not left.has_class("has-bundle")

  @pytest.mark.asyncio()
  async def test_tree_populated_with_bundle_files(
    self, tmp_path: Path, bundle_dir: Path
  ) -> None:
    entries = _make_entries(tmp_path, bundle_dir)
    app = _make_app(_mock_snapshot(entries))
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()

      ts = app.screen.query_one("#type-selector", TypeSelector)
      delta_idx = ts.get_option_index(ArtifactType.DELTA.value)
      ts.highlighted = delta_idx
      ts.action_select()
      await pilot.pause()
      table = app.screen.query_one("#artifact-table", DataTable)
      table.focus()
      await pilot.pause()
      table.move_cursor(row=0)
      await pilot.press("enter")
      await pilot.pause()

      tree = app.screen.query_one("#bundle-tree", BundleTree)
      leaf_names = [(_plain(n.label)) for n in tree.root.children if not n.children]
      assert "DE-061.md" in leaf_names
      assert "DR-061.md" in leaf_names


# --- Tree file selection → preview (2.4) ---


class TestTreeFilePreview:
  """Selecting a file in the tree updates the preview panel."""

  @pytest.mark.asyncio()
  async def test_tree_file_updates_preview_title(
    self, tmp_path: Path, bundle_dir: Path
  ) -> None:
    entries = _make_entries(tmp_path, bundle_dir)
    app = _make_app(_mock_snapshot(entries))
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()

      # Select delta to show tree
      ts = app.screen.query_one("#type-selector", TypeSelector)
      delta_idx = ts.get_option_index(ArtifactType.DELTA.value)
      ts.highlighted = delta_idx
      ts.action_select()
      await pilot.pause()
      table = app.screen.query_one("#artifact-table", DataTable)
      table.focus()
      await pilot.pause()
      table.move_cursor(row=0)
      await pilot.press("enter")
      await pilot.pause()

      # Preview title should be the artifact ID initially
      preview = app.screen.query_one("#preview-panel", PreviewPanel)
      assert preview.border_title == "DE-061"

      # Select DR file in the tree via message posting
      tree = app.screen.query_one("#bundle-tree", BundleTree)
      from supekku.tui.widgets.bundle_tree import BundleFileSelected  # noqa: PLC0415

      tree.post_message(BundleFileSelected(bundle_dir / "DR-061.md"))
      await pilot.pause()

      assert preview.border_title == "DR-061.md"


# --- Focus management (2.5) ---


class TestFocusManagement:
  """f binding focuses tree; Tab from tree focuses artifact table."""

  @pytest.mark.asyncio()
  async def test_f_focuses_tree_when_visible(
    self, tmp_path: Path, bundle_dir: Path
  ) -> None:
    entries = _make_entries(tmp_path, bundle_dir)
    app = _make_app(_mock_snapshot(entries))
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()

      # Select delta to make tree visible
      ts = app.screen.query_one("#type-selector", TypeSelector)
      delta_idx = ts.get_option_index(ArtifactType.DELTA.value)
      ts.highlighted = delta_idx
      ts.action_select()
      await pilot.pause()
      table = app.screen.query_one("#artifact-table", DataTable)
      table.focus()
      await pilot.pause()
      table.move_cursor(row=0)
      await pilot.press("enter")
      await pilot.pause()

      # Press f to focus tree
      await pilot.press("f")
      await pilot.pause()

      tree = app.screen.query_one("#bundle-tree", BundleTree)
      assert tree.has_focus

  @pytest.mark.asyncio()
  async def test_f_noop_when_tree_hidden(self, tmp_path: Path) -> None:
    entries = _make_entries(tmp_path)
    app = _make_app(_mock_snapshot(entries))
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()

      # Tree should be hidden (no bundle selected)
      tree = app.screen.query_one("#bundle-tree", BundleTree)
      assert not tree.display

      # Focus something else, press f — focus should not move to tree
      ts = app.screen.query_one("#type-selector", TypeSelector)
      ts.focus()
      await pilot.pause()
      await pilot.press("f")
      await pilot.pause()
      assert not tree.has_focus

  @pytest.mark.asyncio()
  async def test_tab_from_tree_focuses_artifact_table(
    self, tmp_path: Path, bundle_dir: Path
  ) -> None:
    entries = _make_entries(tmp_path, bundle_dir)
    app = _make_app(_mock_snapshot(entries))
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()

      # Select delta to make tree visible
      ts = app.screen.query_one("#type-selector", TypeSelector)
      delta_idx = ts.get_option_index(ArtifactType.DELTA.value)
      ts.highlighted = delta_idx
      ts.action_select()
      await pilot.pause()
      table = app.screen.query_one("#artifact-table", DataTable)
      table.focus()
      await pilot.pause()
      table.move_cursor(row=0)
      await pilot.press("enter")
      await pilot.pause()

      # Focus tree
      tree = app.screen.query_one("#bundle-tree", BundleTree)
      tree.focus()
      await pilot.pause()
      assert tree.has_focus

      # Press tab — should go to artifact table
      await pilot.press("tab")
      await pilot.pause()
      # key_tab on BundleTree explicitly focuses #artifact-table
      focused = app.focused
      assert focused is table or table.has_focus, (
        f"Expected artifact-table focus, got {focused}"
      )


# --- Refresh on file watch (2.6) ---


class TestTreeRefresh:
  """Tree refreshes on file-watch events for the selected bundle."""

  @pytest.mark.asyncio()
  async def test_refresh_repopulates_tree(
    self, tmp_path: Path, bundle_dir: Path
  ) -> None:
    entries = _make_entries(tmp_path, bundle_dir)
    snapshot = _mock_snapshot(entries)
    app = _make_app(snapshot)
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()

      # Select delta
      ts = app.screen.query_one("#type-selector", TypeSelector)
      delta_idx = ts.get_option_index(ArtifactType.DELTA.value)
      ts.highlighted = delta_idx
      ts.action_select()
      await pilot.pause()
      table = app.screen.query_one("#artifact-table", DataTable)
      table.focus()
      await pilot.pause()
      table.move_cursor(row=0)
      await pilot.press("enter")
      await pilot.pause()

      tree = app.screen.query_one("#bundle-tree", BundleTree)
      initial_count = len(tree.root.children)

      # Add a new file to the bundle dir
      (bundle_dir / "notes.md").write_text("# Notes\n", encoding="utf-8")

      # Trigger refresh
      screen = app.screen
      assert isinstance(screen, BrowserScreen)
      screen.refresh_snapshot(ArtifactType.DELTA)
      await pilot.pause()

      # Tree should have been repopulated with the new file
      new_count = len(tree.root.children)
      assert new_count > initial_count
      leaf_names = [(_plain(n.label)) for n in tree.root.children if not n.children]
      assert "notes.md" in leaf_names
