# supekku.tui.widgets.preview_panel

Preview panel widget — scrollable Markdown display for selected artifact.

## Constants

- `_FRONTMATTER_RE`
- `logger`

## Classes

### PreviewPanel

Scrollable container displaying markdown content of the selected artifact.

**Inherits from:** VerticalScroll

#### Methods

- `clear_preview(self) -> None`: Reset to empty state.
- `compose(self)`
- `show_artifact(self, path) -> None`: Load and display the artifact file at the given path.
