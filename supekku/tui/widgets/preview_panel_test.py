"""Tests for PreviewPanel widget (VT-061-04)."""

from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Markdown

from supekku.tui.widgets.preview_panel import PreviewPanel


class PreviewApp(App):
  """Minimal app for testing PreviewPanel."""

  def compose(self) -> ComposeResult:
    yield PreviewPanel(id="preview")


class TestPreviewPanelNonMarkdown:
  """PreviewPanel shows placeholder for non-markdown files (VT-061-04)."""

  async def test_markdown_file_renders_content(self, tmp_path: Path) -> None:
    md_file = tmp_path / "test.md"
    md_file.write_text("---\nid: test\n---\n# Hello\n", encoding="utf-8")

    async with PreviewApp().run_test() as pilot:
      panel = pilot.app.query_one("#preview", PreviewPanel)
      panel.show_artifact(md_file)
      md_widget = panel.query_one("#preview-markdown", Markdown)
      # Frontmatter should be stripped, content should remain
      assert "Hello" in md_widget._markdown

  async def test_non_markdown_shows_placeholder(self, tmp_path: Path) -> None:
    txt_file = tmp_path / "data.txt"
    txt_file.write_text("plain text\n", encoding="utf-8")

    async with PreviewApp().run_test() as pilot:
      panel = pilot.app.query_one("#preview", PreviewPanel)
      panel.show_artifact(txt_file)
      md_widget = panel.query_one("#preview-markdown", Markdown)
      assert "data.txt" in md_widget._markdown
      assert "Non-markdown" in md_widget._markdown

  async def test_yaml_file_shows_placeholder(self, tmp_path: Path) -> None:
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text("key: value\n", encoding="utf-8")

    async with PreviewApp().run_test() as pilot:
      panel = pilot.app.query_one("#preview", PreviewPanel)
      panel.show_artifact(yaml_file)
      md_widget = panel.query_one("#preview-markdown", Markdown)
      assert "config.yaml" in md_widget._markdown

  async def test_no_extension_shows_placeholder(self, tmp_path: Path) -> None:
    no_ext = tmp_path / "Makefile"
    no_ext.write_text("all:\n\techo hi\n", encoding="utf-8")

    async with PreviewApp().run_test() as pilot:
      panel = pilot.app.query_one("#preview", PreviewPanel)
      panel.show_artifact(no_ext)
      md_widget = panel.query_one("#preview-markdown", Markdown)
      assert "Makefile" in md_widget._markdown

  async def test_markdown_extension_variant(self, tmp_path: Path) -> None:
    md_file = tmp_path / "doc.markdown"
    md_file.write_text("# Doc\n", encoding="utf-8")

    async with PreviewApp().run_test() as pilot:
      panel = pilot.app.query_one("#preview", PreviewPanel)
      panel.show_artifact(md_file)
      md_widget = panel.query_one("#preview-markdown", Markdown)
      assert "Doc" in md_widget._markdown
      assert "Non-markdown" not in md_widget._markdown
