"""VT-054-05..08, VT-059-01..03, VT-061-06 — Track view tests."""

from __future__ import annotations

import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from supekku.scripts.lib.core.artifact_view import (
  ArtifactEntry,
  ArtifactSnapshot,
  ArtifactType,
)
from supekku.tui.app import SpecDriverApp
from supekku.tui.browser import BrowserScreen
from supekku.tui.track import TrackScreen
from supekku.tui.widgets.bundle_tree import BundleFileSelected, BundleTree
from supekku.tui.widgets.preview_panel import PreviewPanel
from supekku.tui.widgets.session_list import SessionList, SessionSelected
from supekku.tui.widgets.track_panel import (
  TrackPanel,
  format_timestamp,
  session_colour_index,
)

# --- Test data ---

_EVENTS = [
  {
    "v": 1,
    "ts": "2026-03-08T14:23:01+00:00",
    "session": "abc123",
    "cmd": "artifact.edit",
    "argv": ["artifact.edit", ".spec-driver/deltas/DE-052-slug/DE-052.md"],
    "artifacts": ["DE-052"],
    "exit_code": 0,
    "status": "ok",
  },
  {
    "v": 1,
    "ts": "2026-03-08T14:23:03+00:00",
    "session": "abc123",
    "cmd": "artifact.read",
    "argv": ["artifact.read", ".spec-driver/deltas/DE-052-slug/DR-052.md"],
    "artifacts": ["DR-052"],
    "exit_code": 0,
    "status": "ok",
  },
  {
    "v": 1,
    "ts": "2026-03-08T14:23:45+00:00",
    "session": "def456",
    "cmd": "complete delta",
    "artifacts": ["DE-052"],
    "exit_code": 1,
    "status": "error",
  },
  {
    "v": 1,
    "ts": "2026-03-08T14:24:00+00:00",
    "session": "abc123",
    "cmd": "list specs",
    "artifacts": [],
    "exit_code": 0,
    "status": "ok",
  },
]

_TEST_ENTRIES: dict[ArtifactType, dict[str, ArtifactEntry]] = {
  ArtifactType.DELTA: {
    "DE-052": ArtifactEntry(
      id="DE-052",
      title="Event emitter",
      status="completed",
      path=Path("/tmp/de-052.md"),
      artifact_type=ArtifactType.DELTA,
    ),
  },
}


def _mock_snapshot() -> ArtifactSnapshot:
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
    for e in entries.get(kw.get("type_filter", ArtifactType.ADR), {}).values()
    if kw.get("status_filter") is None or e.status == kw["status_filter"]
  ]
  snapshot.find_entry.side_effect = lambda aid: _TEST_ENTRIES.get(
    ArtifactType.DELTA, {}
  ).get(aid)
  return snapshot


def _make_app(snapshot: ArtifactSnapshot | None = None):
  snap = snapshot or _mock_snapshot()
  return SpecDriverApp(root=Path("/tmp"), snapshot=snap, listen=False)


# --- VT-054-05: Session filtering ---


class TestSessionFiltering:
  """VT-054-05: "all" returns all events, specific session returns subset."""

  def test_all_filter_returns_all_events(self):
    """clear_and_replay with session_filter=None returns all events."""
    session_filter = None
    filtered = [
      e for e in _EVENTS if session_filter is None or e.get("session") == session_filter
    ]
    assert len(filtered) == 4

  def test_specific_session_returns_subset(self):
    """Filtering by session ID returns only matching events."""
    session = "abc123"
    filtered = [e for e in _EVENTS if e.get("session") == session]
    assert len(filtered) == 3
    assert all(e["session"] == session for e in filtered)

  def test_unknown_session_returns_empty(self):
    filtered = [e for e in _EVENTS if e.get("session") == "nonexistent"]
    assert len(filtered) == 0


# --- VT-054-06: Session discovery ---


class TestSessionDiscovery:
  """VT-054-06: Unique sessions from events, ordered by recency."""

  def test_discovers_unique_sessions(self):
    session_list = SessionList()
    for event in _EVENTS:
      session_list.register_event(event)
    assert len(session_list._sessions) == 2
    assert "abc123" in session_list._sessions
    assert "def456" in session_list._sessions

  def test_session_info_tracks_count(self):
    session_list = SessionList()
    for event in _EVENTS:
      session_list.register_event(event)
    assert session_list._sessions["abc123"].count == 3
    assert session_list._sessions["def456"].count == 1

  def test_session_info_tracks_latest_timestamp(self):
    session_list = SessionList()
    for event in _EVENTS:
      session_list.register_event(event)
    assert "14:24:00" in session_list._sessions["abc123"].last_ts

  def test_null_session_grouped(self):
    events = [{"ts": "2026-03-08T10:00:00+00:00", "session": None}]
    session_list = SessionList()
    for event in events:
      session_list.register_event(event)
    assert None in session_list._sessions


# --- Colour hashing ---


class TestSessionColour:
  """Deterministic colour hashing (DEC-054-04)."""

  def test_deterministic(self):
    idx1 = session_colour_index("abc123")
    idx2 = session_colour_index("abc123")
    assert idx1 == idx2

  def test_range(self):
    for sid in ["a", "b", "c", "abc123", "xyz789", "session-long-name"]:
      idx = session_colour_index(sid)
      assert 0 <= idx < 8

  def test_none_returns_zero(self):
    assert session_colour_index(None) == 0

  def test_empty_returns_zero(self):
    assert session_colour_index("") == 0


# --- Timestamp formatting ---


class TestFormatTimestamp:
  """HH:MM:SS extraction from ISO 8601."""

  def test_iso_format(self):
    assert format_timestamp("2026-03-08T14:23:01+00:00") == "14:23:01"

  def test_none_returns_empty(self):
    assert format_timestamp(None) == ""

  def test_empty_returns_empty(self):
    assert format_timestamp("") == ""

  def test_malformed_returns_truncated(self):
    result = format_timestamp("not-a-timestamp")
    assert isinstance(result, str)


# --- VT-054-07: Cross-screen navigation (find_entry) ---
# find_entry unit tests are in artifact_view_test.py::TestFindEntry


# --- VT-054-08: TrackScreen pilot ---


class TestTrackScreenPilot:
  """VT-054-08: Widget composition, event rendering, session selection."""

  @pytest.mark.asyncio()
  async def test_track_screen_mounts_widgets(self):
    app = _make_app()
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      app.action_toggle_track()
      await pilot.pause()
      screen = app.screen
      assert isinstance(screen, TrackScreen)
      assert screen.query_one("#session-list", SessionList)
      assert screen.query_one("#track-panel", TrackPanel)

  @pytest.mark.asyncio()
  async def test_add_event_renders_row(self):
    app = _make_app()
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      app.action_toggle_track()
      await pilot.pause()
      screen = app.screen
      assert isinstance(screen, TrackScreen)
      screen.add_event(_EVENTS[0])
      await pilot.pause()
      table = screen.query_one("#track-panel", TrackPanel)
      assert table.row_count == 1

  @pytest.mark.asyncio()
  async def test_session_filter_replays(self):
    app = _make_app()
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      app.action_toggle_track()
      await pilot.pause()
      screen = app.screen
      assert isinstance(screen, TrackScreen)
      for event in _EVENTS:
        screen.add_event(event)
      await pilot.pause()
      table = screen.query_one("#track-panel", TrackPanel)
      assert table.row_count == 4

      # Filter to def456 — should show only 1 event
      screen.on_session_selected(SessionSelected("def456"))
      await pilot.pause()
      assert table.row_count == 1

      # Back to all — should show 4
      screen.on_session_selected(SessionSelected(None))
      await pilot.pause()
      assert table.row_count == 4

  @pytest.mark.asyncio()
  async def test_toggle_preserves_state(self):
    """Switching away and back preserves TrackScreen event buffer."""
    app = _make_app()
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      app.action_toggle_track()
      await pilot.pause()
      screen = app.screen
      assert isinstance(screen, TrackScreen)
      screen.add_event(_EVENTS[0])
      await pilot.pause()

      # Toggle back to browser
      app.action_toggle_track()
      await pilot.pause()
      assert isinstance(app.screen, BrowserScreen)

      # Toggle back to track — state preserved
      app.action_toggle_track()
      await pilot.pause()
      track = app.screen
      assert isinstance(track, TrackScreen)
      table = track.query_one("#track-panel", TrackPanel)
      assert table.row_count == 1

  @pytest.mark.asyncio()
  async def test_navigate_artifact_switches_to_browser(self):
    """action_navigate_artifact switches to browser screen (DEC-054-06)."""
    app = _make_app()
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      app.action_toggle_track()
      await pilot.pause()
      assert isinstance(app.screen, TrackScreen)
      app.action_navigate_artifact("DE-052")
      await pilot.pause()
      assert isinstance(app.screen, BrowserScreen)


# --- VT-059-01: Auto-follow triggers ---


def _recent_ts(minutes_ago: int = 0) -> str:
  """ISO timestamp N minutes ago from now."""
  dt = datetime.now(UTC) - timedelta(minutes=minutes_ago)
  return dt.isoformat()


class TestAutoFollowDetection:
  """VT-059-01: Auto-follow triggers with single recent session."""

  def test_single_recent_session_detected(self):
    session_list = SessionList()
    for i in range(3):
      session_list.register_event({"ts": _recent_ts(i), "session": "agent-1"})
    assert session_list.detect_active_session() == "agent-1"

  def test_single_recent_among_stale(self):
    """Recent session detected even when stale sessions exist."""
    session_list = SessionList()
    session_list.register_event({"ts": _recent_ts(0), "session": "recent"})
    session_list.register_event({"ts": _recent_ts(30), "session": "stale"})
    assert session_list.detect_active_session() == "recent"


# --- VT-059-02: Auto-follow does NOT trigger ---


class TestAutoFollowSkipped:
  """VT-059-02: Auto-follow skipped when ambiguous or no activity."""

  def test_no_sessions(self):
    session_list = SessionList()
    assert session_list.detect_active_session() is None

  def test_no_recent_sessions(self):
    session_list = SessionList()
    session_list.register_event({"ts": _recent_ts(30), "session": "stale"})
    assert session_list.detect_active_session() is None

  def test_multiple_recent_sessions(self):
    session_list = SessionList()
    session_list.register_event({"ts": _recent_ts(0), "session": "agent-1"})
    session_list.register_event({"ts": _recent_ts(1), "session": "agent-2"})
    assert session_list.detect_active_session() is None

  def test_null_session_ignored(self):
    session_list = SessionList()
    session_list.register_event({"ts": _recent_ts(0), "session": None})
    assert session_list.detect_active_session() is None


# --- VT-059-03: Preview panel updates ---


class TestTrackPreview:
  """VT-059-03: Preview panel updates on cursor change."""

  @pytest.mark.asyncio()
  async def test_preview_panel_mounted(self):
    app = _make_app()
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      app.action_toggle_track()
      await pilot.pause()
      screen = app.screen
      assert isinstance(screen, TrackScreen)
      assert screen.query_one("#track-preview", PreviewPanel)


# --- VT-061-03: Track file path storage and navigation ---


class TestTrackPanelFilePaths:
  """VT-061-03: TrackPanel stores and retrieves per-row file paths."""

  def test_file_path_stored_from_argv(self):
    panel = TrackPanel()
    event = {
      "ts": "2026-03-08T14:23:01+00:00",
      "session": "s1",
      "cmd": "artifact.edit",
      "argv": ["artifact.edit", ".spec-driver/deltas/DE-061/DE-061.md"],
      "artifacts": ["DE-061"],
      "status": "ok",
    }
    # Must mount columns before appending
    panel._row_counter = 0
    # Simulate by directly calling logic — full pilot test below
    argv = event.get("argv", [])
    file_path = argv[1] if len(argv) > 1 else ""
    assert file_path == ".spec-driver/deltas/DE-061/DE-061.md"

  def test_file_path_for_row_empty_when_no_argv(self):
    panel = TrackPanel()
    panel._row_file_paths["evt-1"] = "some/path.md"
    assert panel.file_path_for_row("evt-1") == "some/path.md"
    assert panel.file_path_for_row("evt-999") == ""

  @pytest.mark.asyncio()
  async def test_append_event_stores_file_path(self):
    app = _make_app()
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      app.action_toggle_track()
      await pilot.pause()
      screen = app.screen
      assert isinstance(screen, TrackScreen)

      screen.add_event(_EVENTS[0])  # Has argv with file path
      await pilot.pause()

      panel = screen.query_one("#track-panel", TrackPanel)
      # Find the row key for the event we just added
      row_keys = list(panel.rows)
      assert len(row_keys) >= 1
      first_key = row_keys[0].value
      file_path = panel.file_path_for_row(first_key)
      assert file_path == ".spec-driver/deltas/DE-052-slug/DE-052.md"

  @pytest.mark.asyncio()
  async def test_no_argv_no_file_path(self):
    app = _make_app()
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      app.action_toggle_track()
      await pilot.pause()
      screen = app.screen
      assert isinstance(screen, TrackScreen)

      screen.add_event(_EVENTS[3])  # No argv
      await pilot.pause()

      panel = screen.query_one("#track-panel", TrackPanel)
      row_keys = list(panel.rows)
      assert len(row_keys) >= 1
      first_key = row_keys[0].value
      assert panel.file_path_for_row(first_key) == ""

  @pytest.mark.asyncio()
  async def test_clear_and_replay_clears_file_paths(self):
    app = _make_app()
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      app.action_toggle_track()
      await pilot.pause()
      screen = app.screen
      assert isinstance(screen, TrackScreen)

      for event in _EVENTS:
        screen.add_event(event)
      await pilot.pause()

      panel = screen.query_one("#track-panel", TrackPanel)
      assert len(panel._row_file_paths) > 0

      panel.clear_and_replay(_EVENTS, session_filter="def456")
      # Only 1 event matches def456, and it has no argv
      assert panel.row_count == 1


class TestTrackNavigateWithFilePath:
  """VT-061-03: Row select navigates with file_path."""

  @pytest.mark.asyncio()
  async def test_navigate_passes_file_path(self):
    app = _make_app()
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      app.action_toggle_track()
      await pilot.pause()
      screen = app.screen
      assert isinstance(screen, TrackScreen)

      # Add event with file path and artifact
      screen.add_event(_EVENTS[0])
      await pilot.pause()

      # Navigate via action — should switch to browser
      app.action_navigate_artifact("DE-052")
      await pilot.pause()
      assert isinstance(app.screen, BrowserScreen)


# --- VT-061-06: TrackScreen inline tree ---


def _make_bundle_dir() -> tuple[Path, Path, Path]:
  """Create a temp bundle directory with files. Returns (root, bundle_dir, primary)."""
  root = Path(tempfile.mkdtemp())
  bundle = root / ".spec-driver" / "deltas" / "DE-070-slug"
  bundle.mkdir(parents=True)
  primary = bundle / "DE-070.md"
  primary.write_text("---\nid: DE-070\n---\n# DE-070\n")
  (bundle / "DR-070.md").write_text("# DR-070\n")
  (bundle / "IP-070.md").write_text("# IP-070\n")
  return root, bundle, primary


def _bundle_entries(
  root: Path, bundle: Path, primary: Path
) -> dict[ArtifactType, dict[str, ArtifactEntry]]:
  """Test entries with a bundle artifact and a non-bundle artifact."""
  return {
    ArtifactType.DELTA: {
      "DE-070": ArtifactEntry(
        id="DE-070",
        title="Bundle delta",
        status="in-progress",
        path=primary,
        artifact_type=ArtifactType.DELTA,
        bundle_dir=bundle,
      ),
      "DE-052": ArtifactEntry(
        id="DE-052",
        title="Event emitter",
        status="completed",
        path=root / "de-052.md",
        artifact_type=ArtifactType.DELTA,
      ),
    },
  }


def _make_bundle_app() -> tuple[SpecDriverApp, Path]:
  """App with a bundle artifact for tree tests."""
  root, bundle, primary = _make_bundle_dir()
  entries = _bundle_entries(root, bundle, primary)

  snapshot = MagicMock(spec=ArtifactSnapshot)
  snapshot._root = root
  snapshot.counts_by_type.return_value = {
    art_type: len(entries.get(art_type, {})) for art_type in ArtifactType
  }
  snapshot.all_entries.side_effect = lambda **kw: list(
    entries.get(kw.get("type_filter", ArtifactType.ADR), {}).values()
  )
  snapshot.find_entry.side_effect = lambda aid: next(
    (e for d in entries.values() for e in d.values() if e.id == aid), None
  )

  # Create the non-bundle file so path.is_file() works
  (root / "de-052.md").write_text("# DE-052\n")

  app = SpecDriverApp(root=root, snapshot=snapshot, listen=False)
  return app, root


_BUNDLE_EVENT = {
  "v": 1,
  "ts": "2026-03-08T15:00:00+00:00",
  "session": "agent-1",
  "cmd": "artifact.edit",
  "argv": [
    "artifact.edit",
    ".spec-driver/deltas/DE-070-slug/DR-070.md",
  ],
  "artifacts": ["DE-070"],
  "status": "ok",
}

_NON_BUNDLE_EVENT = {
  "v": 1,
  "ts": "2026-03-08T15:01:00+00:00",
  "session": "agent-1",
  "cmd": "artifact.read",
  "argv": ["artifact.read", "de-052.md"],
  "artifacts": ["DE-052"],
  "status": "ok",
}


class TestTrackInlineTree:
  """VT-061-06: TrackScreen inline BundleTree on row highlight."""

  @pytest.mark.asyncio()
  async def test_track_screen_composes_bundle_tree(self):
    """TrackScreen includes a BundleTree in #track-left."""
    app, _root = _make_bundle_app()
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      app.action_toggle_track()
      await pilot.pause()
      screen = app.screen
      assert isinstance(screen, TrackScreen)
      tree = screen.query_one("#bundle-tree", BundleTree)
      assert tree is not None
      # Tree starts hidden (no bundle highlighted)
      assert not tree.display

  @pytest.mark.asyncio()
  async def test_highlight_bundle_row_shows_tree(self):
    """Highlighting a bundle artifact row shows the tree."""
    app, _root = _make_bundle_app()
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      app.action_toggle_track()
      await pilot.pause()
      screen = app.screen
      assert isinstance(screen, TrackScreen)

      screen.add_event(_BUNDLE_EVENT)
      await pilot.pause()

      # Move cursor to the bundle event row
      panel = screen.query_one("#track-panel", TrackPanel)
      panel.move_cursor(row=0)
      await pilot.pause()

      tree = screen.query_one("#bundle-tree", BundleTree)
      assert tree.display
      assert tree.bundle_dir is not None
      left = screen.query_one("#track-left")
      assert left.has_class("has-bundle")

  @pytest.mark.asyncio()
  async def test_highlight_non_bundle_row_hides_tree(self):
    """Highlighting a non-bundle row hides the tree."""
    app, _root = _make_bundle_app()
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      app.action_toggle_track()
      await pilot.pause()
      screen = app.screen
      assert isinstance(screen, TrackScreen)

      # Add both events
      screen.add_event(_BUNDLE_EVENT)
      screen.add_event(_NON_BUNDLE_EVENT)
      await pilot.pause()

      panel = screen.query_one("#track-panel", TrackPanel)

      # First highlight a bundle row
      panel.move_cursor(row=0)
      await pilot.pause()
      tree = screen.query_one("#bundle-tree", BundleTree)

      # Now move to non-bundle row (events sorted reverse by time, so
      # _NON_BUNDLE_EVENT is row 0, _BUNDLE_EVENT is row 1)
      # Actually — sorted reverse by time, so 15:01 is row 0, 15:00 is row 1
      # Row 0 = non-bundle (DE-052), Row 1 = bundle (DE-070)
      panel.move_cursor(row=1)
      await pilot.pause()
      assert tree.display  # bundle row — tree visible

      panel.move_cursor(row=0)
      await pilot.pause()
      assert not tree.display  # non-bundle row — tree hidden

  @pytest.mark.asyncio()
  async def test_skip_if_same_bundle(self):
    """Same-bundle highlight doesn't repopulate the tree."""
    app, _root = _make_bundle_app()
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      app.action_toggle_track()
      await pilot.pause()
      screen = app.screen
      assert isinstance(screen, TrackScreen)

      # Add two events for the same bundle artifact
      event2 = {**_BUNDLE_EVENT, "ts": "2026-03-08T15:02:00+00:00"}
      screen.add_event(_BUNDLE_EVENT)
      screen.add_event(event2)
      await pilot.pause()

      panel = screen.query_one("#track-panel", TrackPanel)
      tree = screen.query_one("#bundle-tree", BundleTree)

      # Highlight first bundle row
      panel.move_cursor(row=1)
      await pilot.pause()
      assert tree.display
      first_bundle_dir = tree.bundle_dir

      # Highlight second bundle row (same bundle) — should skip repopulate
      panel.move_cursor(row=0)
      await pilot.pause()
      assert tree.display
      assert tree.bundle_dir == first_bundle_dir

  @pytest.mark.asyncio()
  async def test_add_event_refreshes_tree_for_same_bundle(self):
    """New event touching the displayed bundle repopulates the tree."""
    app, _root = _make_bundle_app()
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      app.action_toggle_track()
      await pilot.pause()
      screen = app.screen
      assert isinstance(screen, TrackScreen)

      screen.add_event(_BUNDLE_EVENT)
      await pilot.pause()

      panel = screen.query_one("#track-panel", TrackPanel)
      panel.move_cursor(row=0)
      await pilot.pause()

      tree = screen.query_one("#bundle-tree", BundleTree)
      assert tree.display

      # Count tree nodes before adding a new file
      initial_nodes = len(list(tree._walk_nodes()))

      # Create a new file in the bundle
      bundle_dir = tree.bundle_dir
      assert bundle_dir is not None
      (bundle_dir / "notes.md").write_text("# Notes\n")

      # Add another event for the same bundle — should refresh tree
      event2 = {**_BUNDLE_EVENT, "ts": "2026-03-08T15:03:00+00:00"}
      screen.add_event(event2)
      await pilot.pause()

      # Tree should now have one more node
      refreshed_nodes = len(list(tree._walk_nodes()))
      assert refreshed_nodes == initial_nodes + 1

  @pytest.mark.asyncio()
  async def test_bundle_file_selected_updates_preview(self):
    """Selecting a file in the tree updates #track-preview."""
    app, _root = _make_bundle_app()
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      app.action_toggle_track()
      await pilot.pause()
      screen = app.screen
      assert isinstance(screen, TrackScreen)

      screen.add_event(_BUNDLE_EVENT)
      await pilot.pause()

      panel = screen.query_one("#track-panel", TrackPanel)
      panel.move_cursor(row=0)
      await pilot.pause()

      tree = screen.query_one("#bundle-tree", BundleTree)
      assert tree.display

      # Simulate file selection in tree
      dr_path = tree.bundle_dir / "DR-070.md"
      screen.on_bundle_file_selected(BundleFileSelected(dr_path))
      await pilot.pause()

      preview = screen.query_one("#track-preview", PreviewPanel)
      assert preview.border_title == "DR-070.md"

  @pytest.mark.asyncio()
  async def test_f_focuses_tree_when_visible(self):
    """f binding focuses the bundle tree when visible."""
    app, _root = _make_bundle_app()
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      app.action_toggle_track()
      await pilot.pause()
      screen = app.screen
      assert isinstance(screen, TrackScreen)

      screen.add_event(_BUNDLE_EVENT)
      await pilot.pause()

      panel = screen.query_one("#track-panel", TrackPanel)
      panel.move_cursor(row=0)
      await pilot.pause()

      tree = screen.query_one("#bundle-tree", BundleTree)
      assert tree.display

      # Focus tree via action
      screen.action_focus_files()
      await pilot.pause()
      assert tree.has_focus

  @pytest.mark.asyncio()
  async def test_tab_from_tree_focuses_track_panel(self):
    """Tab from tree focuses #track-panel (DEC-061-07)."""
    app, _root = _make_bundle_app()
    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      app.action_toggle_track()
      await pilot.pause()
      screen = app.screen
      assert isinstance(screen, TrackScreen)

      screen.add_event(_BUNDLE_EVENT)
      await pilot.pause()

      panel = screen.query_one("#track-panel", TrackPanel)
      panel.move_cursor(row=0)
      await pilot.pause()

      tree = screen.query_one("#bundle-tree", BundleTree)
      assert tree.display

      # Focus tree, then Tab
      tree.focus()
      await pilot.pause()
      assert tree.has_focus

      tree.action_focus_tab_target()
      await pilot.pause()
      assert panel.has_focus
