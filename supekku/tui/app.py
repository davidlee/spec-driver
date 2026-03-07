"""Textual app for browsing spec-driver artifacts."""

from __future__ import annotations

import asyncio
import logging
import os
import subprocess
from pathlib import Path

from textual.app import App
from textual.binding import Binding

from supekku.scripts.lib.core.artifact_view import (
  ArtifactSnapshot,
  ArtifactType,
  path_to_artifact_type,
)
from supekku.tui.browser import BrowserScreen

logger = logging.getLogger(__name__)

# Directories to watch for artifact changes.
# watchfiles' DefaultFilter ignores hidden dirs (.spec-driver/), so we
# use a custom filter that accepts only spec-driver-relevant paths.
_WATCH_DIRS = (".spec-driver", "kanban")


def _spec_driver_filter(_change: int, path: str) -> bool:
  """Accept only paths under .spec-driver/ or kanban/."""
  return any(f"/{d}/" in path or path.endswith(f"/{d}") for d in _WATCH_DIRS)


class SpecDriverApp(App):
  """TUI artifact browser for spec-driver workspaces."""

  TITLE = "spec-driver"
  CSS_PATH = "theme.tcss"
  ENABLE_COMMAND_PALETTE = False

  BINDINGS = [
    Binding("q", "quit", "Quit"),
    Binding("e", "edit", "Edit"),
    Binding("s", "cycle_status", "Status"),
    Binding("slash", "focus_search", "Search", key_display="/"),
  ]

  def __init__(
    self,
    *,
    root: Path | None = None,
    snapshot: ArtifactSnapshot | None = None,
    watch: bool = True,
    **kwargs,
  ) -> None:
    super().__init__(**kwargs)
    self._root = root or Path.cwd()
    self._snapshot = snapshot
    self._watch = watch
    self._watcher_task: asyncio.Task | None = None

  def on_mount(self) -> None:
    snapshot = self._snapshot or ArtifactSnapshot(root=self._root)
    self._snapshot = snapshot
    self.push_screen(BrowserScreen(snapshot))
    if self._watch and self._snapshot is not None:
      self._watcher_task = asyncio.create_task(self._watch_files())

  async def _watch_files(self) -> None:
    """Watch workspace for file changes and refresh affected registries."""
    try:
      from watchfiles import awatch  # noqa: PLC0415
    except ImportError:
      logger.debug("watchfiles not available, file watching disabled")
      return

    try:
      async for changes in awatch(self._root, watch_filter=_spec_driver_filter):
        refreshed: set[ArtifactType] = set()
        for _change_type, path_str in changes:
          art_type = path_to_artifact_type(Path(path_str), self._root)
          if art_type is not None and art_type not in refreshed:
            refreshed.add(art_type)
            screen = self.screen
            if isinstance(screen, BrowserScreen):
              screen.refresh_snapshot(art_type)
    except asyncio.CancelledError:
      pass
    except Exception:  # noqa: BLE001
      logger.debug("File watcher stopped", exc_info=True)

  def action_cycle_status(self) -> None:
    """Cycle the status filter to the next value."""
    try:
      from supekku.tui.widgets.artifact_list import StatusCycler  # noqa: PLC0415

      cycler = self.screen.query_one("#status-filter", StatusCycler)
      cycler.cycle()
    except Exception:  # noqa: BLE001
      pass

  def action_focus_search(self) -> None:
    """Focus the search input in the artifact list."""
    try:
      search = self.screen.query_one("#search-input")
      search.focus()
    except Exception:  # noqa: BLE001
      pass

  def action_edit(self) -> None:
    """Open the selected artifact in $EDITOR."""
    editor = os.environ.get("EDITOR")
    if not editor:
      self.notify("$EDITOR not set. Export EDITOR to enable editing.", severity="error")
      return

    screen = self.screen
    if not isinstance(screen, BrowserScreen):
      return

    entry = screen.selected_entry
    if entry is None or not entry.path.is_file():
      self.notify("No artifact selected.", severity="warning")
      return

    with self.suspend():
      subprocess.run([editor, str(entry.path)], check=False)  # noqa: S603
