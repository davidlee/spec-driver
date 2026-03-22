# supekku.scripts.lib.formatters.diagnostic_formatters

Pure formatting functions for workspace diagnostic output.

## Functions

- `format_doctor_json(summaries) -> str`: Format diagnostic summaries as JSON.

Returns:
JSON string with categories, results, and summary.

- `format_doctor_text(summaries) -> str`: Format diagnostic summaries as human-readable text.

Args:
summaries: Category summaries from the runner.
verbose: If True, include passing results. Default hides them.
color: If True, use ANSI colour codes. Default True.

Returns:
Formatted multi-line string.
