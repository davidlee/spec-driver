"""Tests for the search overlay widget."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from textual.widgets import DataTable, Input

from supekku.scripts.lib.core.artifact_view import (
  ArtifactEntry,
  ArtifactSnapshot,
  ArtifactType,
)
from supekku.tui.app import SpecDriverApp
from supekku.tui.browser import BrowserScreen
from supekku.tui.widgets.search_overlay import SearchOverlay


def _mock_snapshot() -> ArtifactSnapshot:
  """Create a mock ArtifactSnapshot with minimal test data."""
  snapshot = MagicMock(spec=ArtifactSnapshot)
  entries: dict[ArtifactType, dict[str, ArtifactEntry]] = {}
  for art_type in ArtifactType:
    entries[art_type] = {}
  entries[ArtifactType.ADR] = {
    "ADR-001": ArtifactEntry(
      id="ADR-001",
      title="Use spec-driver",
      status="accepted",
      path=Path("/tmp/test-adr-001.md"),
      artifact_type=ArtifactType.ADR,
    ),
  }
  entries[ArtifactType.DELTA] = {
    "DE-087": ArtifactEntry(
      id="DE-087",
      title="Cross-artifact search",
      status="in-progress",
      path=Path("/tmp/test-de-087.md"),
      artifact_type=ArtifactType.DELTA,
    ),
  }
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
  snapshot.find_entry.return_value = None
  return snapshot


def _make_app(snapshot: ArtifactSnapshot | None = None):
  """Create a SpecDriverApp with a mock snapshot and empty search index."""
  snap = snapshot or _mock_snapshot()
  app = SpecDriverApp(
    root=Path("/tmp"),
    snapshot=snap,
    listen=False,
    watch=False,
  )
  # Pre-populate search index cache to avoid real registry access.
  app._search_index = []  # noqa: SLF001
  return app


class TestSearchOverlayLifecycle:
  """Overlay opens, accepts input, and dismisses."""

  @pytest.mark.asyncio()
  async def test_slash_opens_overlay(self):
    """Pressing / should push the search overlay."""
    app = _make_app()
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      assert isinstance(app.screen, BrowserScreen)

      await pilot.press("slash")
      await pilot.pause()
      assert isinstance(app.screen, SearchOverlay)

  @pytest.mark.asyncio()
  async def test_escape_dismisses_overlay(self):
    """Pressing Escape should dismiss the overlay."""
    app = _make_app()
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      await pilot.press("slash")
      await pilot.pause()
      assert isinstance(app.screen, SearchOverlay)

      await pilot.press("escape")
      await pilot.pause()
      assert isinstance(app.screen, BrowserScreen)

  @pytest.mark.asyncio()
  async def test_overlay_has_search_input(self):
    """Overlay should contain a search input box."""
    app = _make_app()
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      await pilot.press("slash")
      await pilot.pause()
      search_input = app.screen.query_one(
        "#search-box",
        Input,
      )
      assert search_input is not None

  @pytest.mark.asyncio()
  async def test_overlay_has_results_table(self):
    """Overlay should contain a results DataTable."""
    app = _make_app()
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      await pilot.press("slash")
      await pilot.pause()
      table = app.screen.query_one(
        "#search-results",
        DataTable,
      )
      assert table is not None


class TestSearchOverlayCtrlF:
  """Ctrl+F should focus per-type search, not open overlay."""

  @pytest.mark.asyncio()
  async def test_ctrl_f_does_not_open_overlay(self):
    app = _make_app()
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      await pilot.press("ctrl+f")
      await pilot.pause()
      # Should still be on BrowserScreen, not SearchOverlay.
      assert isinstance(app.screen, BrowserScreen)
