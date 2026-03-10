# supekku.tui.widgets.search_overlay_test

Tests for the search overlay widget.

## Functions

- `_make_app(snapshot)`: Create a SpecDriverApp with a mock snapshot and empty search index.
- `_mock_snapshot() -> ArtifactSnapshot`: Create a mock ArtifactSnapshot with minimal test data.

## Classes

### TestSearchOverlayCtrlF

Ctrl+F should focus per-type search, not open overlay.

#### Methods

- @pytest.mark.asyncio `test_ctrl_f_does_not_open_overlay(self)`

### TestSearchOverlayLifecycle

Overlay opens, accepts input, and dismisses.

#### Methods

- @pytest.mark.asyncio `test_escape_dismisses_overlay(self)`: Pressing Escape should dismiss the overlay.
- @pytest.mark.asyncio `test_overlay_has_results_table(self)`: Overlay should contain a results DataTable.
- @pytest.mark.asyncio `test_overlay_has_search_input(self)`: Overlay should contain a search input box.
- @pytest.mark.asyncio `test_slash_opens_overlay(self)`: Pressing / should push the search overlay.
