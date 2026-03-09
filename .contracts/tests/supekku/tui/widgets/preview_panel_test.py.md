# supekku.tui.widgets.preview_panel_test

Tests for PreviewPanel widget (VT-061-04).

## Classes

### PreviewApp

Minimal app for testing PreviewPanel.

**Inherits from:** App

#### Methods

- `compose(self) -> ComposeResult`

### TestPreviewPanelNonMarkdown

PreviewPanel shows placeholder for non-markdown files (VT-061-04).

#### Methods

- `test_markdown_extension_variant(self, tmp_path) -> None`
- `test_markdown_file_renders_content(self, tmp_path) -> None`
- `test_no_extension_shows_placeholder(self, tmp_path) -> None`
- `test_non_markdown_shows_placeholder(self, tmp_path) -> None`
- `test_yaml_file_shows_placeholder(self, tmp_path) -> None`
