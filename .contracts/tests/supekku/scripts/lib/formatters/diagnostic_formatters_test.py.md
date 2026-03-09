# supekku.scripts.lib.formatters.diagnostic_formatters_test

Tests for diagnostic formatters.

## Functions

- `_make_summaries() -> list[CategorySummary]`

## Classes

### TestFormatDoctorJson

Tests for JSON output formatting.

**Inherits from:** unittest.TestCase

#### Methods

- `test_all_pass_exit_code_zero(self) -> None` - warn present
- `test_category_count(self) -> None`
- `test_exit_code_reflects_worst(self) -> None`
- `test_result_fields(self) -> None`
- `test_summary_counts(self) -> None`
- `test_valid_json(self) -> None`

### TestFormatDoctorText

Tests for text output formatting.

**Inherits from:** unittest.TestCase

#### Methods

- `test_all_pass_category_shows_note(self) -> None`
- `test_color_false_no_ansi(self) -> None`: color=False should produce no ANSI escape codes.
- `test_color_pass_symbol_in_verbose(self) -> None`: Pass symbol should appear in verbose coloured output. - ⚠
- `test_color_true_has_ansi(self) -> None`: color=True should include ANSI escape codes.
- `test_color_warn_symbol_present(self) -> None`: Warning symbol should be present in coloured output.
- `test_empty_summaries(self) -> None`
- `test_header_present(self) -> None`
- `test_hides_pass_by_default(self) -> None`
- `test_suggestion_shown(self) -> None`
- `test_summary_line(self) -> None`
- `test_verbose_shows_pass(self) -> None`
