# supekku.scripts.lib.workflow.bridge_test

Tests for bridge block extraction and rendering (DR-102 §7).

## Classes

### ExtractNotesBridgeTest

Test notes-bridge extraction from markdown.

**Inherits from:** unittest.TestCase

#### Methods

- `test_extracts_valid_block(self) -> None`
- `test_returns_none_when_absent(self) -> None`

### ExtractPhaseBridgeTest

Test phase-bridge extraction from markdown.

**Inherits from:** unittest.TestCase

#### Methods

- `test_extracts_valid_block(self) -> None`
- `test_minimal_block(self) -> None`
- `test_returns_none_on_invalid_yaml(self) -> None`
- `test_returns_none_when_absent(self) -> None`

### RenderNotesBridgeTest

Test notes-bridge rendering.

**Inherits from:** unittest.TestCase

#### Methods

- `test_minimal_render(self) -> None`
- `test_roundtrip(self) -> None`: Rendered block can be extracted back.
- `test_with_optionals(self) -> None`

### RenderPhaseBridgeTest

Test phase-bridge rendering.

**Inherits from:** unittest.TestCase

#### Methods

- `test_handoff_not_ready(self) -> None`
- `test_minimal_render(self) -> None`
- `test_roundtrip(self) -> None`
- `test_with_review_required(self) -> None`
