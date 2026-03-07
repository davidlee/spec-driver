"""VT-053-pilot — headless pilot tests for the TUI artifact browser."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from textual.widgets import DataTable, Input, Select

from supekku.scripts.lib.core.artifact_view import (
  ArtifactEntry,
  ArtifactSnapshot,
  ArtifactType,
)
from supekku.tui.app import SpecDriverApp
from supekku.tui.browser import BrowserScreen
from supekku.tui.widgets.artifact_list import ArtifactList
from supekku.tui.widgets.preview_panel import PreviewPanel
from supekku.tui.widgets.type_selector import TypeSelector

# --- Test fixtures ---

_TEST_ENTRIES: dict[ArtifactType, dict[str, ArtifactEntry]] = {
  ArtifactType.ADR: {
    "ADR-001": ArtifactEntry(
      id="ADR-001",
      title="Use spec-driver",
      status="accepted",
      path=Path("/tmp/test-adr-001.md"),
      artifact_type=ArtifactType.ADR,
    ),
    "ADR-002": ArtifactEntry(
      id="ADR-002",
      title="No backlinks",
      status="draft",
      path=Path("/tmp/test-adr-002.md"),
      artifact_type=ArtifactType.ADR,
    ),
  },
  ArtifactType.SPEC: {
    "SPEC-001": ArtifactEntry(
      id="SPEC-001",
      title="CLI Core",
      status="active",
      path=Path("/tmp/test-spec-001.md"),
      artifact_type=ArtifactType.SPEC,
    ),
  },
}


def _mock_snapshot() -> ArtifactSnapshot:
  """Create a mock ArtifactSnapshot with test data."""
  snapshot = MagicMock(spec=ArtifactSnapshot)
  entries: dict[ArtifactType, dict[str, ArtifactEntry]] = {}
  for art_type in ArtifactType:
    entries[art_type] = _TEST_ENTRIES.get(art_type, {})
  snapshot.entries = entries
  snapshot.counts_by_type.return_value = {
    art_type: len(entries[art_type]) for art_type in ArtifactType
  }
  snapshot.all_entries.side_effect = lambda **kw: [
    e
    for e in entries.get(
      kw.get("type_filter", ArtifactType.ADR),
      {},
    ).values()
    if kw.get("status_filter") is None or e.status == kw["status_filter"]
  ]
  return snapshot


def _make_app(snapshot: ArtifactSnapshot | None = None):
  """Create a SpecDriverApp with a mock snapshot."""
  snap = snapshot or _mock_snapshot()
  return SpecDriverApp(root=Path("/tmp"), snapshot=snap)


# --- Tests ---


class TestAppMounts:
  """App mounts with all expected widgets."""

  @pytest.mark.asyncio()
  async def test_app_mounts_browser_screen(self):
    app = _make_app()
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      assert isinstance(app.screen, BrowserScreen)

  @pytest.mark.asyncio()
  async def test_type_selector_has_11_options(self):
    app = _make_app()
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      ts = app.screen.query_one("#type-selector", TypeSelector)
      assert ts.option_count == len(ArtifactType)

  @pytest.mark.asyncio()
  async def test_artifact_list_mounted(self):
    app = _make_app()
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      al = app.screen.query_one(
        "#artifact-panel",
        ArtifactList,
      )
      assert al is not None

  @pytest.mark.asyncio()
  async def test_preview_panel_mounted(self):
    app = _make_app()
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      pp = app.screen.query_one(
        "#preview-panel",
        PreviewPanel,
      )
      assert pp is not None


class TestTypeSelection:
  """Selecting a type populates the artifact list."""

  @pytest.mark.asyncio()
  async def test_selecting_type_populates_table(self):
    app = _make_app()
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      ts = app.screen.query_one("#type-selector", TypeSelector)
      ts.highlighted = 0  # ADR
      ts.action_select()
      await pilot.pause()
      table = app.screen.query_one(
        "#artifact-table",
        DataTable,
      )
      assert table.row_count == 2  # 2 test ADRs

  @pytest.mark.asyncio()
  async def test_selecting_empty_type_shows_no_rows(self):
    app = _make_app()
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      ts = app.screen.query_one("#type-selector", TypeSelector)
      # DELTA = index 3, has 0 entries in test data
      ts.highlighted = 3
      ts.action_select()
      await pilot.pause()
      table = app.screen.query_one(
        "#artifact-table",
        DataTable,
      )
      assert table.row_count == 0

  @pytest.mark.asyncio()
  async def test_type_selector_shows_counts(self):
    app = _make_app()
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      ts = app.screen.query_one("#type-selector", TypeSelector)
      # ADR option should show count of 2
      opt = ts.get_option_at_index(0)
      prompt_str = str(opt.prompt)
      assert "2" in prompt_str


class TestArtifactSelection:
  """Selecting an artifact updates the preview."""

  @pytest.mark.asyncio()
  async def test_selecting_row_updates_preview(self, tmp_path):
    test_file = tmp_path / "test-adr.md"
    test_file.write_text("# Test ADR\n\nSome content.")

    snapshot = _mock_snapshot()
    snapshot.entries[ArtifactType.ADR]["ADR-001"] = ArtifactEntry(
      id="ADR-001",
      title="Test",
      status="accepted",
      path=test_file,
      artifact_type=ArtifactType.ADR,
    )
    snapshot.all_entries.side_effect = lambda **kw: list(
      snapshot.entries.get(
        kw.get("type_filter", ArtifactType.ADR),
        {},
      ).values(),
    )

    app = _make_app(snapshot)
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      ts = app.screen.query_one("#type-selector", TypeSelector)
      ts.highlighted = 0
      ts.action_select()
      await pilot.pause()

      table = app.screen.query_one(
        "#artifact-table",
        DataTable,
      )
      table.focus()
      await pilot.pause()
      table.move_cursor(row=0)
      await pilot.press("enter")
      await pilot.pause()

      pp = app.screen.query_one(
        "#preview-panel",
        PreviewPanel,
      )
      assert len(pp.children) > 0


class TestStatusFilter:
  """Status filter controls the visible artifacts."""

  @pytest.mark.asyncio()
  async def test_status_filter_present_after_type_select(self):
    app = _make_app()
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      ts = app.screen.query_one("#type-selector", TypeSelector)
      ts.highlighted = 0  # ADR
      ts.action_select()
      await pilot.pause()
      status_sel = app.screen.query_one(
        "#status-filter",
        Select,
      )
      assert status_sel is not None


class TestSearchFilter:
  """Fuzzy search filters the artifact list (DEC-053-12)."""

  @pytest.mark.asyncio()
  async def test_search_filters_entries(self):
    app = _make_app()
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      ts = app.screen.query_one("#type-selector", TypeSelector)
      ts.highlighted = 0  # ADR
      ts.action_select()
      await pilot.pause()

      search = app.screen.query_one("#search-input", Input)
      search.focus()
      await pilot.pause()
      search.value = "backlink"
      await pilot.pause()

      table = app.screen.query_one(
        "#artifact-table",
        DataTable,
      )
      # Only ADR-002 "No backlinks" matches
      assert table.row_count == 1


class TestKeybindings:
  """Keybinding dispatch works."""

  @pytest.mark.asyncio()
  async def test_quit_binding(self):
    app = _make_app()
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      await pilot.press("q")

  @pytest.mark.asyncio()
  async def test_search_focus_binding(self):
    app = _make_app()
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      await pilot.press("slash")
      await pilot.pause()
      search = app.screen.query_one("#search-input", Input)
      assert search.has_focus
