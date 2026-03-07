"""Artifact list widget — DataTable + status cycle + fuzzy search."""

from __future__ import annotations

from textual import on
from textual.containers import Vertical
from textual.events import Key
from textual.fuzzy import Matcher
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import DataTable, Input, Label

from supekku.scripts.lib.core.artifact_view import (
  ArtifactEntry,
  ArtifactType,
)
from supekku.scripts.lib.formatters.theme import styled_text

# Columns: (label, key, width). None width = auto-size to content.
_LIST_COLUMNS = (
  ("ID", "id", 16),
  ("Title", "title", None),
  ("Status", "status", 14),
)

_ALL = "all"


class ArtifactSelected(Message):
  """Posted when the user selects an artifact row."""

  def __init__(self, entry: ArtifactEntry) -> None:
    super().__init__()
    self.entry = entry


class StatusCycler(Label):
  """1-line status filter that cycles on click or keybinding."""

  current = reactive(_ALL)

  class Changed(Message):
    """Posted when the status filter value changes."""

    def __init__(self, status_cycler: StatusCycler, value: str) -> None:
      super().__init__()
      self.value = value
      self.status_cycler = status_cycler

    @property
    def control(self) -> StatusCycler:
      """The StatusCycler that sent the message."""
      return self.status_cycler

  def __init__(self, **kwargs) -> None:
    super().__init__(**kwargs)
    self._options: list[str] = []

  def set_statuses(self, statuses: list[str]) -> None:
    """Update the available status values."""
    self._options = [_ALL, *statuses]
    self.current = _ALL

  def watch_current(self, value: str) -> None:
    self.update(f" Status: {value} ▸")
    self.post_message(self.Changed(self, value))

  def on_click(self) -> None:
    self.cycle()

  def cycle(self) -> None:
    """Advance to the next status value."""
    if not self._options:
      return
    try:
      idx = self._options.index(self.current)
    except ValueError:
      idx = 0
    self.current = self._options[(idx + 1) % len(self._options)]


class _SearchInput(Input):
  """Search input that forwards navigation keys to the artifact table."""

  def on_key(self, event: Key) -> None:
    table = self.screen.query_one("#artifact-table", DataTable)
    if event.key == "down":
      event.prevent_default()
      table.action_cursor_down()
    elif event.key == "up":
      event.prevent_default()
      table.action_cursor_up()
    elif event.key == "enter" and table.row_count > 0:
      event.prevent_default()
      table.action_select_cursor()
      preview = self.screen.query_one("#preview-panel")
      preview.focus()


class ArtifactList(Vertical):
  """Artifact list panel with status filter and fuzzy search."""

  def __init__(self, **kwargs) -> None:
    super().__init__(**kwargs)
    self._entries: list[ArtifactEntry] = []
    self._current_type: ArtifactType | None = None
    self._search_text: str = ""

  @property
  def current_type(self) -> ArtifactType | None:
    """Currently displayed artifact type."""
    return self._current_type

  def compose(self):
    yield StatusCycler(id="status-filter")
    yield _SearchInput(placeholder="/ search", id="search-input")
    yield DataTable(id="artifact-table", cursor_type="row")

  def on_mount(self) -> None:
    table = self.query_one("#artifact-table", DataTable)
    for label, key, width in _LIST_COLUMNS:
      table.add_column(label, key=key, width=width)

  def show_entries(
    self,
    entries: list[ArtifactEntry],
    artifact_type: ArtifactType,
  ) -> None:
    """Populate the list with entries for a given type."""
    self._entries = entries
    self._current_type = artifact_type
    self._search_text = ""

    # Reset search input
    search = self.query_one("#search-input", Input)
    search.value = ""

    # Rebuild status filter options
    statuses = sorted({e.status for e in entries if e.status})
    cycler = self.query_one("#status-filter", StatusCycler)
    cycler.set_statuses(statuses)

    self._refresh_table()

  def _filtered_entries(self) -> list[ArtifactEntry]:
    """Apply status filter and search text to entries."""
    entries = self._entries
    cycler = self.query_one("#status-filter", StatusCycler)
    if cycler.current != _ALL:
      entries = [e for e in entries if e.status == cycler.current]
    if self._search_text:
      matcher = Matcher(self._search_text)
      scored = [
        (e, max(matcher.match(e.id), matcher.match(e.title), matcher.match(e.status)))
        for e in entries
      ]
      return [e for e, score in sorted(scored, key=lambda x: -x[1]) if score > 0]
    return sorted(entries, key=lambda e: e.id)

  def _refresh_table(self) -> None:
    table = self.query_one("#artifact-table", DataTable)
    table.clear()
    for entry in self._filtered_entries():
      id_style = f"{self._current_type.value}.id" if self._current_type else ""
      table.add_row(
        styled_text(entry.id, id_style),
        entry.title,
        entry.status,
        key=entry.id,
      )

  @on(StatusCycler.Changed, "#status-filter")
  def _on_status_changed(self, event: StatusCycler.Changed) -> None:
    event.stop()
    self._refresh_table()

  @on(Input.Changed, "#search-input")
  def _on_search_changed(self, event: Input.Changed) -> None:
    event.stop()
    self._search_text = event.value
    self._refresh_table()

  @on(DataTable.RowSelected, "#artifact-table")
  def _on_row_selected(self, event: DataTable.RowSelected) -> None:
    event.stop()
    row_key = event.row_key.value
    for entry in self._entries:
      if entry.id == row_key:
        self.post_message(ArtifactSelected(entry))
        break
