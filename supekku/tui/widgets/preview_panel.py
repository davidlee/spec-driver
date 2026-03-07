"""Preview panel widget — Markdown display for selected artifact."""

from __future__ import annotations

import logging
from pathlib import Path

from textual.widgets import Markdown

logger = logging.getLogger(__name__)


class PreviewPanel(Markdown):
  """Displays markdown content of the selected artifact."""

  def show_artifact(self, path: Path) -> None:
    """Load and display the artifact file at the given path."""
    try:
      content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
      logger.warning("Failed to read %s: %s", path, exc)
      content = f"*Could not load:* `{path}`\n\n`{exc}`"
    self.update(content)

  def clear_preview(self) -> None:
    """Reset to empty state."""
    self.update("")
