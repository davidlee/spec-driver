"""Async event listener for TUI track mode (DE-054).

Receives CLI events via Unix domain socket (primary) or log-tail fallback.
Provides JSONL replay on startup with bootstrap drain to close the
replay-to-live gap.

Design: DEC-054-02, DEC-054-03, DEC-054-05.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import socket
from pathlib import Path
from typing import TYPE_CHECKING

from textual.message import Message

from supekku.scripts.lib.core.events import LOG_FILENAME, SOCKET_FILENAME

if TYPE_CHECKING:
  from textual.app import App

logger = logging.getLogger(__name__)

REPLAY_LIMIT = 200
DISPLAY_BUFFER_LIMIT = 500
_PROBE_PAYLOAD = b'{"v":0}'


# --- Messages ---


class TrackEvent(Message):
  """Posted when a CLI event is received (socket or log-tail)."""

  def __init__(self, event: dict) -> None:
    super().__init__()
    self.event = event


# --- Replay ---


def replay_events(run_dir: Path) -> tuple[list[dict], int]:
  """Read last N events from the JSONL log.

  Returns (events, file_offset) where file_offset is the byte position
  at EOF after reading — used by the bootstrap drain to detect events
  emitted during the gap between replay and listener activation.
  """
  log_path = run_dir / LOG_FILENAME
  if not log_path.is_file():
    return [], 0

  try:
    with open(log_path, encoding="utf-8") as f:
      lines = f.readlines()
      offset = f.tell()
  except OSError:
    logger.debug("Failed to read event log for replay", exc_info=True)
    return [], 0

  events: list[dict] = []
  for raw in lines[-REPLAY_LIMIT:]:
    stripped = raw.strip()
    if not stripped:
      continue
    try:
      event = json.loads(stripped)
      if isinstance(event, dict):
        events.append(event)
    except (json.JSONDecodeError, ValueError):
      logger.debug("Skipping malformed replay line: %s", stripped[:80])
  return events, offset


# --- Socket probe ---


def probe_socket(sock_path: str) -> bool:
  """Return True if a live listener exists at sock_path.

  Sends a probe datagram (v:0) to distinguish live sockets from stale
  ones left by crashed TUI instances. Design: DEC-054-02.
  """
  try:
    probe = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    try:
      probe.sendto(_PROBE_PAYLOAD, sock_path)
      return True  # someone is listening
    finally:
      probe.close()
  except (ConnectionRefusedError, FileNotFoundError):
    return False
  except OSError:
    return True  # assume live on unexpected errors (defensive)


# --- Socket-mode protocol ---


class _EventProtocol(asyncio.DatagramProtocol):
  """Receives event datagrams and posts TrackEvent messages to the app."""

  def __init__(self, app: App) -> None:
    self._app = app

  def datagram_received(self, data: bytes, addr: object) -> None:
    try:
      event = json.loads(data)
    except (json.JSONDecodeError, ValueError):
      logger.debug("Malformed socket datagram: %s", data[:80])
      return
    if not isinstance(event, dict):
      return
    # Discard probe datagrams (v:0)
    if event.get("v") == 0:
      return
    self._app.post_message(TrackEvent(event))


# --- Log-tail mode ---


async def _tail_log(
  app: App,
  run_dir: Path,
  initial_offset: int,
  stop_event: asyncio.Event,
) -> None:
  """Watch the run directory for appended lines and post events.

  Uses watchfiles to detect changes to events.jsonl. Reads from
  initial_offset forward. Design: DEC-054-02, DEC-054-05.
  """
  from watchfiles import awatch  # noqa: PLC0415

  log_path = run_dir / LOG_FILENAME
  offset = initial_offset

  def _log_filter(_change: int, path: str) -> bool:
    return path.endswith(LOG_FILENAME)

  try:
    async for _changes in awatch(
      run_dir,
      watch_filter=_log_filter,
      stop_event=stop_event,
    ):
      offset = _drain_from_offset(app, log_path, offset)
  except asyncio.CancelledError:
    pass
  except Exception:  # noqa: BLE001
    logger.debug("Log-tail watcher stopped", exc_info=True)


def _drain_from_offset(app: App, log_path: Path, offset: int) -> int:
  """Read new lines from offset, post events, return new offset."""
  try:
    with open(log_path, encoding="utf-8") as f:
      f.seek(offset)
      new_lines = f.readlines()
      new_offset = f.tell()
  except OSError:
    return offset

  for raw in new_lines:
    stripped = raw.strip()
    if not stripped:
      continue
    try:
      event = json.loads(stripped)
      if isinstance(event, dict):
        app.post_message(TrackEvent(event))
    except (json.JSONDecodeError, ValueError):
      logger.debug("Skipping malformed log-tail line: %s", stripped[:80])
  return new_offset


# --- EventListener ---


class EventListener:
  """Async event listener — socket or log-tail mode.

  Public API:
    replay_events() -> list[dict]   — call before start
    start(app) -> None              — begin listening
    stop() -> None                  — stop and clean up

  Design: DEC-054-05.
  """

  def __init__(self, run_dir: Path) -> None:
    self._run_dir = run_dir
    self._sock_path = str(run_dir / SOCKET_FILENAME)
    self._owns_socket = False
    self._transport: asyncio.DatagramTransport | None = None
    self._task: asyncio.Task | None = None
    self._stop_event: asyncio.Event | None = None
    self._replay_offset = 0

  def get_replay_events(self) -> list[dict]:
    """Replay last N events from log. Records offset for bootstrap drain."""
    events, self._replay_offset = replay_events(self._run_dir)
    return events

  async def start(self, app: App) -> None:
    """Begin listening. Posts TrackEvent messages to the app."""
    self._run_dir.mkdir(parents=True, exist_ok=True)

    if self._can_bind_socket():
      await self._start_socket_mode(app)
    else:
      await self._start_logtail_mode(app)

    # Bootstrap drain: read any events emitted between replay and listener start
    log_path = self._run_dir / LOG_FILENAME
    self._replay_offset = _drain_from_offset(app, log_path, self._replay_offset)

  async def stop(self) -> None:
    """Stop listening and clean up resources."""
    if self._transport is not None:
      self._transport.close()
      self._transport = None

    if self._stop_event is not None:
      self._stop_event.set()

    if self._task is not None:
      self._task.cancel()
      with contextlib.suppress(asyncio.CancelledError):
        await self._task
      self._task = None

    if self._owns_socket:
      with contextlib.suppress(OSError):
        Path(self._sock_path).unlink()
      self._owns_socket = False

  def _can_bind_socket(self) -> bool:
    """Determine if we can bind the socket (probe existing, check path length)."""
    if len(self._sock_path) > 104:
      logger.debug("Socket path too long (%d), using log-tail", len(self._sock_path))
      return False

    sock_file = Path(self._sock_path)
    if sock_file.exists():
      if probe_socket(self._sock_path):
        logger.debug("Live socket detected, falling back to log-tail")
        return False
      # Stale socket — safe to remove
      try:
        sock_file.unlink()
      except OSError:
        logger.debug("Failed to remove stale socket", exc_info=True)
        return False

    return True

  async def _start_socket_mode(self, app: App) -> None:
    """Bind socket and register with asyncio event loop."""
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    try:
      sock.bind(self._sock_path)
      sock.setblocking(False)
      self._owns_socket = True
    except OSError:
      logger.debug("Failed to bind socket, falling back to log-tail", exc_info=True)
      sock.close()
      await self._start_logtail_mode(app)
      return

    loop = asyncio.get_running_loop()
    transport, _protocol = await loop.create_datagram_endpoint(
      lambda: _EventProtocol(app),
      sock=sock,
    )
    self._transport = transport

  async def _start_logtail_mode(self, app: App) -> None:
    """Start watching the log file for new events."""
    self._stop_event = asyncio.Event()
    self._task = asyncio.create_task(
      _tail_log(app, self._run_dir, self._replay_offset, self._stop_event),
    )
