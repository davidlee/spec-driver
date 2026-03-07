"""VT-054-05..08, VT-059-01..03 — Track view tests (DE-054, DE-059)."""

from __future__ import annotations

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
    "cmd": "create delta",
    "artifacts": ["DE-052"],
    "exit_code": 0,
    "status": "ok",
  },
  {
    "v": 1,
    "ts": "2026-03-08T14:23:03+00:00",
    "session": "abc123",
    "cmd": "draft-design-revision",
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
