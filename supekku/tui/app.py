"""Textual app for browsing spec-driver artifacts."""

from __future__ import annotations

from pathlib import Path

from textual.app import App
from textual.binding import Binding

from supekku.scripts.lib.core.artifact_view import ArtifactSnapshot
from supekku.tui.browser import BrowserScreen


class SpecDriverApp(App):
  """TUI artifact browser for spec-driver workspaces."""

  TITLE = "spec-driver"
  CSS_PATH = "theme.tcss"
  ENABLE_COMMAND_PALETTE = False

  BINDINGS = [
    Binding("q", "quit", "Quit"),
    Binding("slash", "focus_search", "Search", key_display="/"),
  ]

  def __init__(
    self,
    *,
    root: Path | None = None,
    snapshot: ArtifactSnapshot | None = None,
    **kwargs,
  ) -> None:
    super().__init__(**kwargs)
    self._root = root or Path.cwd()
    self._snapshot = snapshot

  def on_mount(self) -> None:
    snapshot = self._snapshot or ArtifactSnapshot(root=self._root)
    self.push_screen(BrowserScreen(snapshot))

  def action_focus_search(self) -> None:
    """Focus the search input in the artifact list."""
    try:
      search = self.screen.query_one("#search-input")
      search.focus()
    except Exception:  # noqa: BLE001
      pass
