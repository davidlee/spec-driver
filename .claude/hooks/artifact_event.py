#!/usr/bin/env python3
"""Claude Code PostToolUse hook — emit events for spec-driver artifact touches.

Self-contained: no supekku imports. Reads PostToolUse JSON from stdin,
classifies the file path against spec-driver artifact patterns, and emits
a v1 event to the JSONL log + Unix socket.

Fail-silent: all exceptions are swallowed. This script must never interfere
with Claude Code operation.

Design: DE-060, DR-060 (DEC-060-01, DEC-060-02, DEC-060-03).
"""

from __future__ import annotations

import contextlib
import json
import os
import re
import socket
import sys
from datetime import UTC, datetime
from pathlib import Path

# --- Constants (mirrored from events.py, intentionally self-contained) ---

_EVENT_SCHEMA_VERSION = 1
_LOG_FILENAME = "events.jsonl"
_SOCKET_FILENAME = "tui.sock"
_MAX_SOCKET_PATH_LEN = 104

# --- Artifact path patterns ---
# Each tuple: (regex pattern against relative path, artifact_type, ID group index)
# SYNC: mirrored in supekku/pi.extensions/spec-driver-artifact-events.ts
#       see mem.artifact-pattern-sync

_ARTIFACT_PATTERNS: list[tuple[re.Pattern[str], str]] = [
  (re.compile(r"\.spec-driver/deltas/(DE-\d+)[^/]*/phases/"), "phase"),
  (re.compile(r"\.spec-driver/deltas/(DE-\d+)[^/]*/DR-\d+"), "design_revision"),
  (re.compile(r"\.spec-driver/deltas/(DE-\d+)[^/]*/IP-\d+"), "plan"),
  (re.compile(r"\.spec-driver/deltas/(DE-\d+)"), "delta"),
  (re.compile(r"\.spec-driver/tech/(SPEC-\d+)"), "spec"),
  (re.compile(r"\.spec-driver/decisions/(ADR-\d+)"), "adr"),
  (re.compile(r"\.spec-driver/revisions/(RE-\d+)"), "revision"),
  (re.compile(r"\.spec-driver/audits/(AUD-\d+)"), "audit"),
  (re.compile(r"\.spec-driver/backlog/"), "backlog"),
  (re.compile(r"\.spec-driver/product/(PROD-\d+)"), "product_spec"),
  (re.compile(r"\.spec-driver/policies/(POL-\d+)"), "policy"),
  (re.compile(r"\.spec-driver/standards/(STD-\d+)"), "standard"),
]

_TOOL_TO_ACTION = {
  "Read": "read",
  "Edit": "edit",
  "Write": "write",
}


# --- Public API (for testing) ---


def classify_path(file_path: str) -> tuple[str, str | None] | None:
  """Classify a file path as a spec-driver artifact.

  Returns (artifact_type, artifact_id) or None if not a spec-driver artifact.
  artifact_id may be None for pattern-matched paths without a capture group
  (e.g. backlog items).
  """
  for pattern, artifact_type in _ARTIFACT_PATTERNS:
    m = pattern.search(file_path)
    if m:
      artifact_id = m.group(1) if m.lastindex else None
      return artifact_type, artifact_id
  return None


def build_event(
  *,
  session_id: str | None,
  tool_name: str,
  file_path: str,
  artifact_type: str,
  artifact_id: str | None,
  cwd: str | None = None,
) -> dict:
  """Build a v1 event dict for an artifact touch."""
  action = _TOOL_TO_ACTION.get(tool_name, tool_name.lower())
  rel_path = file_path
  # Use hook-provided cwd for deterministic repo-root-relative paths (DEC-061-04)
  base = Path(cwd) if cwd else Path.cwd()
  with contextlib.suppress(ValueError):
    rel_path = str(Path(file_path).relative_to(base))

  return {
    "v": _EVENT_SCHEMA_VERSION,
    "ts": datetime.now(UTC).isoformat(),
    "session": session_id,
    "cmd": f"artifact.{action}",
    "argv": [f"artifact.{action}", rel_path],
    "artifacts": [artifact_id] if artifact_id else [],
    "exit_code": 0,
    "status": "ok",
    "artifact_type": artifact_type,
  }


def write_log(event: dict, run_dir: Path) -> None:
  """Append a JSON line to the event log. Creates run_dir lazily."""
  run_dir.mkdir(parents=True, exist_ok=True)
  log_path = run_dir / _LOG_FILENAME
  line = json.dumps(event, separators=(",", ":")) + "\n"
  fd = os.open(str(log_path), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
  try:
    os.write(fd, line.encode())
  finally:
    os.close(fd)


def send_socket(event: dict, run_dir: Path) -> None:
  """Fire-and-forget a JSON datagram to the TUI socket."""
  sock_path = str(run_dir / _SOCKET_FILENAME)
  if len(sock_path) > _MAX_SOCKET_PATH_LEN:
    return
  sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
  try:
    data = json.dumps(event, separators=(",", ":")).encode()
    sock.sendto(data, sock_path)
  finally:
    sock.close()


# --- Main ---


def main() -> None:
  """Entry point: read PostToolUse JSON from stdin, classify, emit."""
  hook_input = json.load(sys.stdin)

  tool_name = hook_input.get("tool_name", "")
  file_path = hook_input.get("tool_input", {}).get("file_path", "")
  if not file_path:
    return

  classification = classify_path(file_path)
  if classification is None:
    return

  artifact_type, artifact_id = classification
  session_id = hook_input.get("session_id")
  cwd = hook_input.get("cwd", "")

  event = build_event(
    session_id=session_id,
    tool_name=tool_name,
    file_path=file_path,
    artifact_type=artifact_type,
    artifact_id=artifact_id,
    cwd=cwd or None,
  )

  # Resolve run dir from project root (cwd in hook JSON)
  run_dir = Path(cwd) / ".spec-driver" / "run" if cwd else Path(".spec-driver/run")

  write_log(event, run_dir)
  with contextlib.suppress(Exception):
    send_socket(event, run_dir)


if __name__ == "__main__":
  with contextlib.suppress(Exception):
    main()
