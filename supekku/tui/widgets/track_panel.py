"""Track panel widget — DataTable event stream with row selection (DEC-054-07)."""

from __future__ import annotations

import hashlib
from datetime import datetime

from textual.widgets import DataTable

from supekku.scripts.lib.formatters.theme import styled_text
from supekku.tui.event_listener import DISPLAY_BUFFER_LIMIT

_COLUMNS = (
  ("Time", "time", 10),
  ("Session", "session", 10),
  ("Command", "cmd", None),
  ("Artifact", "artifact", 16),
  ("Status", "status", 8),
)

SESSION_COLOUR_COUNT = 8


def session_colour_index(session_id: str | None) -> int:
  """Deterministic colour index for a session ID (DEC-054-04)."""
  if not session_id:
    return 0
  digest = hashlib.md5(session_id.encode(), usedforsecurity=False).digest()
  return int.from_bytes(digest[:2]) % SESSION_COLOUR_COUNT


def format_timestamp(ts: str | None) -> str:
  """Extract HH:MM:SS from an ISO 8601 timestamp."""
  if not ts:
    return ""
  try:
    dt = datetime.fromisoformat(ts)
    return dt.strftime("%H:%M:%S")
  except (ValueError, TypeError):
    return ts[:8] if len(ts) >= 8 else ts


class TrackPanel(DataTable):
  """Scrolling event stream with row selection for artifact navigation."""

  def __init__(self, **kwargs) -> None:
    super().__init__(cursor_type="row", **kwargs)
    self._row_counter = 0
    self._row_artifacts: dict[str, str] = {}

  def on_mount(self) -> None:
    for label, key, width in _COLUMNS:
      self.add_column(label, key=key, width=width)

  def artifact_for_row(self, row_key_value: str) -> str:
    """Return the artifact ID associated with a row key, or empty string."""
    return self._row_artifacts.get(row_key_value, "")

  def append_event(self, event: dict) -> None:
    """Add a styled event row, pruning oldest if over capacity."""
    ts = format_timestamp(event.get("ts"))
    session = event.get("session") or ""
    cmd = event.get("cmd", "")
    artifacts = event.get("artifacts", [])
    artifact = artifacts[0] if artifacts else ""
    status = event.get("status", "")

    colour_idx = session_colour_index(event.get("session"))
    session_style = f"track.session.{colour_idx}"
    status_style = f"track.status.{status}" if status in ("ok", "error") else ""

    self._row_counter += 1
    row_key = f"evt-{self._row_counter}"
    if artifact:
      self._row_artifacts[row_key] = artifact

    self.add_row(
      styled_text(ts, "track.timestamp"),
      styled_text(session[:8], session_style),
      styled_text(cmd, "track.cmd"),
      styled_text(artifact, "track.artifact") if artifact else "",
      styled_text(status, status_style) if status_style else status,
      key=row_key,
    )

    while self.row_count > DISPLAY_BUFFER_LIMIT:
      first_key = list(self.rows)[0]
      self._row_artifacts.pop(first_key.value, None)
      self.remove_row(first_key)

  def clear_and_replay(
    self,
    events: list[dict],
    session_filter: str | None = None,
  ) -> None:
    """Clear table and replay filtered events from buffer."""
    self.clear()
    self._row_artifacts.clear()
    for event in events:
      if session_filter is None or event.get("session") == session_filter:
        self.append_event(event)
