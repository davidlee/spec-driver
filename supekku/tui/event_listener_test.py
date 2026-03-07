"""Tests for event_listener.py — VT-054-01 through VT-054-04."""

from __future__ import annotations

import json
import socket
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from supekku.scripts.lib.core.events import LOG_FILENAME, SOCKET_FILENAME
from supekku.tui.event_listener import (
  EventListener,
  TrackEvent,
  _drain_from_offset,
  probe_socket,
  replay_events,
)

# --- Helpers ---


def _write_events(log_path: Path, events: list[dict]) -> None:
  """Write events as JSONL lines."""
  with open(log_path, "w", encoding="utf-8") as f:
    for event in events:
      f.write(json.dumps(event) + "\n")


def _make_event(cmd: str = "list specs", **overrides) -> dict:
  """Create a minimal valid event dict."""
  base = {
    "v": 1,
    "ts": "2026-03-07T14:23:01Z",
    "session": "test-session",
    "cmd": cmd,
    "argv": [cmd],
    "artifacts": [],
    "exit_code": 0,
    "status": "ok",
  }
  base.update(overrides)
  return base


def _mock_app() -> MagicMock:
  """Create a mock app that records posted messages."""
  app = MagicMock()
  app.posted_messages = []

  def _post_message(msg):
    app.posted_messages.append(msg)

  app.post_message = _post_message
  return app


# --- VT-054-01: Replay ---


class TestReplayEvents:
  """VT-054-01: Event log replay."""

  def test_parses_valid_jsonl(self, tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    events = [_make_event("list specs"), _make_event("show delta")]
    _write_events(run_dir / LOG_FILENAME, events)

    result, offset = replay_events(run_dir)

    assert len(result) == 2
    assert result[0]["cmd"] == "list specs"
    assert result[1]["cmd"] == "show delta"
    assert offset > 0

  def test_respects_bound(self, tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    events = [_make_event(f"cmd-{i}") for i in range(300)]
    _write_events(run_dir / LOG_FILENAME, events)

    result, _offset = replay_events(run_dir)

    assert len(result) == 200
    # Should be the last 200 events
    assert result[0]["cmd"] == "cmd-100"
    assert result[-1]["cmd"] == "cmd-299"

  def test_skips_malformed_lines(self, tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    log_path = run_dir / LOG_FILENAME
    with open(log_path, "w", encoding="utf-8") as f:
      f.write(json.dumps(_make_event("good-1")) + "\n")
      f.write("not valid json\n")
      f.write("[1, 2, 3]\n")  # valid JSON but not a dict
      f.write(json.dumps(_make_event("good-2")) + "\n")
      f.write("\n")  # empty line

    result, _offset = replay_events(run_dir)

    assert len(result) == 2
    assert result[0]["cmd"] == "good-1"
    assert result[1]["cmd"] == "good-2"

  def test_missing_file_returns_empty(self, tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()

    result, offset = replay_events(run_dir)

    assert result == []
    assert offset == 0

  def test_empty_file_returns_empty(self, tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / LOG_FILENAME).write_text("")

    result, offset = replay_events(run_dir)

    assert result == []
    assert offset == 0

  def test_records_offset_at_eof(self, tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    events = [_make_event("cmd-1")]
    _write_events(run_dir / LOG_FILENAME, events)

    _result, offset = replay_events(run_dir)
    file_size = (run_dir / LOG_FILENAME).stat().st_size

    assert offset == file_size


# --- VT-054-02: Socket listener ---


class TestEventProtocol:
  """VT-054-02: Socket listener receives datagrams."""

  def test_valid_event_posts_track_event(self):
    from supekku.tui.event_listener import _EventProtocol  # noqa: PLC0415

    app = _mock_app()
    protocol = _EventProtocol(app)
    event = _make_event("create delta")

    protocol.datagram_received(json.dumps(event).encode(), None)

    assert len(app.posted_messages) == 1
    assert isinstance(app.posted_messages[0], TrackEvent)
    assert app.posted_messages[0].event["cmd"] == "create delta"

  def test_malformed_json_is_skipped(self):
    from supekku.tui.event_listener import _EventProtocol  # noqa: PLC0415

    app = _mock_app()
    protocol = _EventProtocol(app)

    protocol.datagram_received(b"not json", None)

    assert len(app.posted_messages) == 0

  def test_non_dict_json_is_skipped(self):
    from supekku.tui.event_listener import _EventProtocol  # noqa: PLC0415

    app = _mock_app()
    protocol = _EventProtocol(app)

    protocol.datagram_received(b"[1, 2, 3]", None)

    assert len(app.posted_messages) == 0

  def test_probe_datagram_is_discarded(self):
    from supekku.tui.event_listener import _EventProtocol  # noqa: PLC0415

    app = _mock_app()
    protocol = _EventProtocol(app)

    protocol.datagram_received(b'{"v":0}', None)

    assert len(app.posted_messages) == 0


# --- VT-054-03: Socket probe ---


class TestProbeSocket:
  """VT-054-03: Socket probe detects live vs stale vs absent."""

  def test_absent_socket_returns_false(self, tmp_path):
    sock_path = str(tmp_path / "nonexistent.sock")

    assert probe_socket(sock_path) is False

  def test_live_socket_returns_true(self, tmp_path):
    sock_path = str(tmp_path / "live.sock")
    # Create a listening socket
    listener = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    try:
      listener.bind(sock_path)
      assert probe_socket(sock_path) is True
    finally:
      listener.close()
      Path(sock_path).unlink(missing_ok=True)

  def test_stale_socket_returns_false(self, tmp_path):
    sock_path = str(tmp_path / "stale.sock")
    # Create and immediately close a socket (leaves stale file)
    listener = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    listener.bind(sock_path)
    listener.close()

    assert probe_socket(sock_path) is False


# --- VT-054-04: Log-tail / drain ---


class TestDrainFromOffset:
  """VT-054-04: Drain reads new lines from offset."""

  def test_reads_new_lines_from_offset(self, tmp_path):
    log_path = tmp_path / LOG_FILENAME
    # Write initial content
    events = [_make_event("initial")]
    _write_events(log_path, events)
    initial_offset = log_path.stat().st_size

    # Append new events
    with open(log_path, "a", encoding="utf-8") as f:
      f.write(json.dumps(_make_event("new-1")) + "\n")
      f.write(json.dumps(_make_event("new-2")) + "\n")

    app = _mock_app()
    new_offset = _drain_from_offset(app, log_path, initial_offset)

    assert len(app.posted_messages) == 2
    assert app.posted_messages[0].event["cmd"] == "new-1"
    assert app.posted_messages[1].event["cmd"] == "new-2"
    assert new_offset > initial_offset

  def test_skips_malformed_lines(self, tmp_path):
    log_path = tmp_path / LOG_FILENAME
    with open(log_path, "w", encoding="utf-8") as f:
      f.write(json.dumps(_make_event("good")) + "\n")
      f.write("bad line\n")
      f.write(json.dumps(_make_event("also-good")) + "\n")

    app = _mock_app()
    _drain_from_offset(app, log_path, 0)

    assert len(app.posted_messages) == 2

  def test_missing_file_returns_same_offset(self, tmp_path):
    log_path = tmp_path / "nonexistent.jsonl"
    app = _mock_app()

    result = _drain_from_offset(app, log_path, 42)

    assert result == 42
    assert len(app.posted_messages) == 0

  def test_no_new_content_returns_same_offset(self, tmp_path):
    log_path = tmp_path / LOG_FILENAME
    events = [_make_event("only")]
    _write_events(log_path, events)
    offset = log_path.stat().st_size

    app = _mock_app()
    result = _drain_from_offset(app, log_path, offset)

    assert result == offset
    assert len(app.posted_messages) == 0


# --- EventListener integration ---


class TestEventListenerCanBind:
  """EventListener mode selection and lifecycle."""

  def test_can_bind_fresh_socket(self, tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    listener = EventListener(run_dir)

    assert listener._can_bind_socket() is True  # noqa: SLF001

  def test_cannot_bind_when_live_socket_exists(self, tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    sock_path = str(run_dir / SOCKET_FILENAME)
    live = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    try:
      live.bind(sock_path)
      listener = EventListener(run_dir)
      assert listener._can_bind_socket() is False  # noqa: SLF001
    finally:
      live.close()
      Path(sock_path).unlink(missing_ok=True)

  def test_can_bind_after_removing_stale_socket(self, tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    sock_path = str(run_dir / SOCKET_FILENAME)
    # Create stale socket
    stale = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    stale.bind(sock_path)
    stale.close()

    listener = EventListener(run_dir)
    assert listener._can_bind_socket() is True  # noqa: SLF001
    # Stale socket should have been removed
    assert not Path(sock_path).exists()

  def test_path_too_long_falls_back(self, tmp_path):
    # Create a path that exceeds 104 chars
    deep = tmp_path
    while len(str(deep / SOCKET_FILENAME)) <= 104:
      deep = deep / ("a" * 20)
    deep.mkdir(parents=True, exist_ok=True)

    listener = EventListener(deep)
    assert listener._can_bind_socket() is False  # noqa: SLF001

  @pytest.mark.asyncio()
  async def test_get_replay_events_returns_events(self, tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    _write_events(run_dir / LOG_FILENAME, [_make_event("test")])

    listener = EventListener(run_dir)
    events = listener.get_replay_events()

    assert len(events) == 1
    assert events[0]["cmd"] == "test"

  @pytest.mark.asyncio()
  async def test_start_and_stop_socket_mode(self, tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    app = _mock_app()

    listener = EventListener(run_dir)
    await listener.start(app)

    assert listener._owns_socket is True  # noqa: SLF001
    sock_path = run_dir / SOCKET_FILENAME
    assert sock_path.exists()

    await listener.stop()

    assert not sock_path.exists()
    assert listener._owns_socket is False  # noqa: SLF001

  @pytest.mark.asyncio()
  async def test_socket_receives_events(self, tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    app = _mock_app()

    listener = EventListener(run_dir)
    await listener.start(app)

    try:
      # Send an event via socket (like events.py emitter would)
      sender = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
      event = _make_event("from-emitter")
      sender.sendto(json.dumps(event).encode(), str(run_dir / SOCKET_FILENAME))
      sender.close()

      # Give the event loop a moment to process
      import asyncio  # noqa: PLC0415

      await asyncio.sleep(0.05)

      assert len(app.posted_messages) == 1
      assert app.posted_messages[0].event["cmd"] == "from-emitter"
    finally:
      await listener.stop()
