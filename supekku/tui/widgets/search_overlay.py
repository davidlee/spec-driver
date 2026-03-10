"""Modal search overlay — fzf-style cross-artifact fuzzy search.

Design reference: DR-087 DEC-087-03, DEC-087-04.
"""

from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.events import Key
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import DataTable, Input, Static

from supekku.scripts.lib.core.artifact_view import ArtifactEntry
from supekku.scripts.lib.formatters.theme import styled_text
from supekku.tui.search.index import SearchEntry
from supekku.tui.search.scorer import search

# Column layout for results table.
_COLUMNS = (
  ("Type", "type", 12),
  ("ID", "id", 16),
  ("Title", "title", None),
)


class SearchResult(Message):
  """Posted when the user selects a search result."""

  def __init__(self, entry: ArtifactEntry) -> None:
    super().__init__()
    self.entry = entry


class _SearchInput(Input):
  """Search input that forwards navigation keys to the results table."""

  _NAV_KEYS: dict[str, str] = {
    "down": "action_cursor_down",
    "up": "action_cursor_up",
    "pagedown": "action_page_down",
    "pageup": "action_page_up",
  }

  def on_key(self, event: Key) -> None:
    """Forward navigation keys to the results table."""
    table = self.screen.query_one("#search-results", DataTable)
    if action := self._NAV_KEYS.get(event.key):
      event.prevent_default()
      getattr(table, action)()
    elif event.key == "ctrl+delete":
      event.prevent_default()
      self.action_delete_right_word()
    elif event.key == "ctrl+backspace":
      event.prevent_default()
      self.action_delete_left_word()
    elif event.key == "enter" and table.row_count > 0:
      event.prevent_default()
      table.action_select_cursor()


class SearchOverlay(ModalScreen[ArtifactEntry | None]):
  """Modal overlay for cross-artifact fuzzy search.

  Opens with an empty search input.  Results update as the user types.
  Enter selects a result and dismisses; Escape dismisses without selection.
  """

  BINDINGS = [
    Binding("escape", "dismiss_overlay", "Close", show=False),
  ]

  DEFAULT_CSS = """
  SearchOverlay {
    align: center middle;
  }

  #search-container {
    width: 80%;
    max-width: 100;
    height: 60%;
    max-height: 30;
    border: round $accent;
    background: $surface;
    padding: 1 2;
  }

  #search-box {
    margin-bottom: 1;
  }

  #search-results {
    height: 1fr;
  }

  #search-empty {
    height: 1fr;
    content-align: center middle;
    color: $text-muted;
  }
  """

  def __init__(self, *, index: list[SearchEntry], **kwargs) -> None:
    super().__init__(**kwargs)
    self._index = index

  def compose(self) -> ComposeResult:
    with Static(id="search-container"):
      yield _SearchInput(
        placeholder="Search all artifacts...",
        id="search-box",
      )
      yield DataTable(id="search-results", cursor_type="row")

  def on_mount(self) -> None:
    """Set up results table columns."""
    table = self.query_one("#search-results", DataTable)
    for label, key, width in _COLUMNS:
      table.add_column(label, key=key, width=width)

  @on(Input.Changed, "#search-box")
  def _on_search_changed(self, event: Input.Changed) -> None:
    event.stop()
    self._update_results(event.value)

  def _update_results(self, query: str) -> None:
    table = self.query_one("#search-results", DataTable)
    table.clear()
    if not query:
      return
    hits = search(query, self._index)
    for se in hits:
      entry = se.entry
      art_type = entry.artifact_type
      type_style = f"artifact.group.{art_type.group.value}"
      id_style = f"{art_type.value}.id"
      table.add_row(
        styled_text(art_type.singular, type_style),
        styled_text(entry.id, id_style),
        entry.title,
        key=entry.id,
      )

  @on(DataTable.RowSelected, "#search-results")
  def _on_result_selected(
    self,
    event: DataTable.RowSelected,
  ) -> None:
    event.stop()
    row_key = event.row_key.value
    for se in self._index:
      if se.entry.id == row_key:
        self.dismiss(se.entry)
        return
    self.dismiss(None)

  def action_dismiss_overlay(self) -> None:
    """Dismiss overlay without selection."""
    self.dismiss(None)
