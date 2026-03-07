"""CLI event emission infrastructure (DE-052).

Emits structured JSONL events at the process boundary for every leaf-command
invocation. Events are written to .spec-driver/run/events.jsonl and
fire-and-forget sent to .spec-driver/run/tui.sock (AF_UNIX SOCK_DGRAM).

All emission is fail-silent — errors here must never cause a CLI command to fail.
"""

from __future__ import annotations

import contextlib
import json
import os
import socket
from datetime import UTC, datetime
from pathlib import Path

# --- Module-level state (single-threaded CLI, no contextvars needed) ---

_command_invoked: bool = False
_touched_artifacts: list[str] = []

# --- Constants ---

EVENT_SCHEMA_VERSION = 1
LOG_FILENAME = "events.jsonl"
SOCKET_FILENAME = "tui.sock"
MAX_SOCKET_PATH_LEN = 104


# --- Public API ---


def mark_command_invoked() -> None:
  """Set the command-invocation flag (called from Command.invoke intercept)."""
  global _command_invoked  # noqa: PLW0603
  _command_invoked = True


def command_was_invoked() -> bool:
  """Return whether a leaf command body actually executed."""
  return _command_invoked


def record_artifact(artifact_id: str) -> None:
  """Register an artifact ID touched by the current command."""
  _touched_artifacts.append(artifact_id)


def emit_event(
  *,
  argv: list[str],
  exit_code: int,
  status: str,
) -> None:
  """Emit a structured event to JSONL log and socket.

  Fail-silent: swallows all exceptions so CLI commands are never affected.
  No-op when no workspace is available.
  """
  with contextlib.suppress(Exception):
    _emit_event_unsafe(argv=argv, exit_code=exit_code, status=status)


# --- Internal helpers ---


def _emit_event_unsafe(
  *,
  argv: list[str],
  exit_code: int,
  status: str,
) -> None:
  """Build and write the event record. May raise."""
  run_dir = _get_run_dir()
  if run_dir is None:
    return

  event = {
    "v": EVENT_SCHEMA_VERSION,
    "ts": datetime.now(UTC).isoformat(),
    "session": _detect_session(),
    "cmd": _resolve_cmd(argv),
    "argv": argv,
    "artifacts": _drain_artifacts(),
    "exit_code": exit_code,
    "status": status,
  }

  _write_log(event, run_dir)
  _send_socket(event, run_dir)


def _get_run_dir() -> Path | None:
  """Resolve the run directory, returning None if no workspace exists."""
  try:
    from supekku.scripts.lib.core.repo import find_repo_root  # noqa: PLC0415

    root = find_repo_root()
  except (RuntimeError, Exception):  # noqa: BLE001
    return None

  from supekku.scripts.lib.core.paths import get_run_dir  # noqa: PLC0415

  return get_run_dir(root)


def _detect_session() -> str | None:
  """Detect the agent session from environment variables.

  Priority: SPEC_DRIVER_SESSION > CLAUDECODE fallback > None.
  """
  session = os.environ.get("SPEC_DRIVER_SESSION")
  if session:
    return session
  if os.environ.get("CLAUDECODE"):
    return "claude"
  return None


def _resolve_cmd(argv: list[str]) -> str:
  """Extract the command path from argv, stripping flags and arguments.

  Walks argv collecting tokens that look like subcommand names (no leading
  dash, not purely numeric or punctuated). Stops at the first flag or
  positional argument.
  """
  parts: list[str] = []
  for arg in argv:
    if arg.startswith("-"):
      break
    # Heuristic: subcommand names are lowercase alpha (possibly with hyphens)
    if arg.replace("-", "").replace("_", "").isalpha():
      parts.append(arg)
    else:
      break
  return " ".join(parts)


def _drain_artifacts() -> list[str]:
  """Return collected artifact IDs and clear the list."""
  arts = _touched_artifacts.copy()
  _touched_artifacts.clear()
  return arts


def _write_log(event: dict, run_dir: Path) -> None:
  """Append a JSON line to the event log. Creates run_dir lazily."""
  try:
    run_dir.mkdir(parents=True, exist_ok=True)
    log_path = run_dir / LOG_FILENAME
    line = json.dumps(event, separators=(",", ":")) + "\n"
    # O_APPEND for atomic single-line writes on local filesystems
    fd = os.open(str(log_path), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    try:
      os.write(fd, line.encode())
    finally:
      os.close(fd)
  except OSError:
    pass


def _send_socket(event: dict, run_dir: Path) -> None:
  """Fire-and-forget a JSON datagram to the TUI socket."""
  try:
    sock_path = str(run_dir / SOCKET_FILENAME)
    if len(sock_path) > MAX_SOCKET_PATH_LEN:
      return
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    try:
      data = json.dumps(event, separators=(",", ":")).encode()
      sock.sendto(data, sock_path)
    finally:
      sock.close()
  except Exception:  # noqa: BLE001
    pass


def _reset() -> None:
  """Reset module state (test helper only)."""
  global _command_invoked  # noqa: PLW0603
  _command_invoked = False
  _touched_artifacts.clear()
