"""Preview panel widget — scrollable Markdown display for selected artifact."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from textual.containers import VerticalScroll
from textual.widgets import Markdown

logger = logging.getLogger(__name__)

_FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n?", re.DOTALL)


class PreviewPanel(VerticalScroll):
  """Scrollable container displaying markdown content of the selected artifact."""

  def compose(self):
    yield Markdown(id="preview-markdown")

  _MARKDOWN_SUFFIXES = frozenset((".md", ".markdown"))

  def show_artifact(self, path: Path) -> None:
    """Load and display the artifact file at the given path."""
    md = self.query_one("#preview-markdown", Markdown)
    if path.suffix not in self._MARKDOWN_SUFFIXES:
      md.update(f"*Non-markdown file:* `{path.name}`")
      return
    try:
      content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
      logger.warning("Failed to read %s: %s", path, exc)
      content = f"*Could not load:* `{path}`\n\n`{exc}`"
    content = _FRONTMATTER_RE.sub("", content)
    md.update(content)

  def clear_preview(self) -> None:
    """Reset to empty state."""
    self.query_one("#preview-markdown", Markdown).update("")
