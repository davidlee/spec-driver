# supekku.scripts.lib.formatters.decision_formatters_test

Tests for decision_formatters module.

## Classes

### TestFormatDecisionDetails

Tests for format_decision_details function.

**Inherits from:** unittest.TestCase

#### Methods

- `test_format_full_decision(self) -> None`: Test formatting with all fields populated.
- `test_format_minimal_decision(self) -> None`: Test formatting with minimal required fields.
- `test_format_preserves_order(self) -> None`: Test that output maintains logical field ordering.
- `test_format_with_backlinks(self) -> None`: Test formatting with backlinks.
- `test_format_with_multiple_authors(self) -> None`: Test formatting with multiple authors.
