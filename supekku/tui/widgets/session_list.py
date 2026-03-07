"""Session list widget — session discovery and filtering (DEC-054-04)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from textual.message import Message
from textual.widgets import OptionList
from textual.widgets.option_list import Option

from supekku.scripts.lib.formatters.theme import styled_text
from supekku.tui.widgets.track_panel import session_colour_index

_ALL_SESSIONS = "__all__"
_ACTIVE_THRESHOLD = timedelta(minutes=10)


@dataclass
class SessionInfo:
  """Metadata for a discovered session."""

  session_id: str | None
  last_ts: str = ""
  count: int = 0
  _parsed_ts: datetime | None = field(default=None, repr=False)

  @property
  def parsed_ts(self) -> datetime | None:
    """Most recent parsed timestamp, or None."""
    return self._parsed_ts

  def update(self, ts: str) -> None:
    """Update with a new event timestamp."""
    self.count += 1
    try:
      parsed = datetime.fromisoformat(ts)
      if self._parsed_ts is None or parsed > self._parsed_ts:
        self._parsed_ts = parsed
        self.last_ts = ts
    except (ValueError, TypeError):
      if not self.last_ts:
        self.last_ts = ts


class SessionSelected(Message):
  """Posted when the user selects a session filter."""

  def __init__(self, session_id: str | None) -> None:
    super().__init__()
    self.session_id = session_id


class SessionList(OptionList):
  """Discovers sessions from events and lets the user filter by session."""

  def __init__(self, **kwargs) -> None:
    super().__init__(**kwargs)
    self._sessions: dict[str | None, SessionInfo] = {}

  def register_event(self, event: dict) -> None:
    """Update session metadata from an event."""
    session_id = event.get("session")
    ts = event.get("ts", "")
    if session_id not in self._sessions:
      self._sessions[session_id] = SessionInfo(session_id=session_id)
    self._sessions[session_id].update(ts)

  def rebuild(self) -> None:
    """Rebuild the option list ordered by most-recent-event-first."""
    self.clear_options()

    self.add_option(Option(styled_text("All sessions", "track.cmd"), id=_ALL_SESSIONS))

    sorted_sessions = sorted(
      self._sessions.values(),
      key=lambda s: s.last_ts,
      reverse=True,
    )

    for info in sorted_sessions:
      label = info.session_id or "unknown"
      colour_idx = session_colour_index(info.session_id)
      style_name = f"track.session.{colour_idx}"
      display = styled_text(f"{label[:12]} ({info.count})", style_name)
      option_id = info.session_id or "__none__"
      self.add_option(Option(display, id=option_id))

  def detect_active_session(self) -> str | None:
    """Return session ID if exactly one session is recently active (DEC-059-01).

    Returns None if no sessions, no recent activity, or multiple active sessions.
    """
    now = datetime.now(UTC)
    active: list[str] = []
    for info in self._sessions.values():
      if info.session_id is None or info.parsed_ts is None:
        continue
      age = now - info.parsed_ts
      if age <= _ACTIVE_THRESHOLD:
        active.append(info.session_id)
    if len(active) == 1:
      return active[0]
    return None

  def on_option_list_option_selected(
    self,
    event: OptionList.OptionSelected,
  ) -> None:
    """Post SessionSelected message when user picks a session."""
    option_id = event.option_id
    if option_id in (_ALL_SESSIONS, "__none__"):
      self.post_message(SessionSelected(None))
    else:
      self.post_message(SessionSelected(str(option_id)))
