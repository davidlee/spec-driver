# supekku.cli.common

Common utilities, options, and callbacks for CLI commands.

This module provides reusable CLI option types for consistent flag behavior.

## Standardized Flags

Across all list commands, we use consistent flag patterns:
- `--format`: Output format (table|json|tsv)
- `--truncate`: Enable field truncation in table output (default: off, full content)
- `--filter`: Substring filter (case-insensitive)
- `--regexp`: Regular expression pattern for filtering
- `--case-insensitive`: Make regexp matching case-insensitive
- `--status`: Filter by status (entity-specific values)
- `--root`: Repository root directory

## Module Notes

- # Standardized Flags

## Constants

- `CaseInsensitiveOption`
- `EXIT_FAILURE` - Exit codes
- `EXIT_SUCCESS` - Exit codes
- `FormatOption` - Standardized list command options
- `RegexpOption`
- `RootOption` - Common option definitions for reuse
- `TruncateOption`
- `VersionOption` - Version option for main app

## Functions

- `get_editor() -> <BinOp>`: Get editor command from environment or fallback.

Resolution order: $EDITOR -> $VISUAL -> vi

Returns:
  Editor command string, or None if no editor available.
- `get_pager() -> <BinOp>`: Get pager command from environment or fallback.

Resolution order: $PAGER -> less -> more

Returns:
  Pager command string, or None if no pager available.
- `matches_regexp(pattern, text_fields, case_insensitive) -> bool`: Check if any of the text fields match the given regexp pattern.

Args:
  pattern: Regular expression pattern (None means no filtering)
  text_fields: List of text fields to search
  case_insensitive: Whether to perform case-insensitive matching

Returns:
  True if pattern is None (no filter) or if any field matches the pattern

Raises:
  re.error: If the pattern is invalid
- `normalize_id(artifact_type, raw_id) -> str`: Normalize artifact ID by prepending prefix if raw_id is numeric-only.

For artifact types with unambiguous prefixes, allows shorthand like '001' or '1'
to be expanded to 'ADR-001' etc. Numeric IDs are zero-padded to 3 digits.

Args:
  artifact_type: The artifact type key (e.g., 'adr', 'delta')
  raw_id: The user-provided ID (e.g., '001', 'ADR-001', 'foo')

Returns:
  Normalized ID with prefix, or original ID if not applicable.

Examples:
  >>> normalize_id("adr", "1")
  'ADR-001'
  >>> normalize_id("adr", "001")
  'ADR-001'
  >>> normalize_id("adr", "ADR-001")
  'ADR-001'
  >>> normalize_id("spec", "001")
  '001'
- `open_in_editor(path) -> None`: Open file in editor.

Args:
  path: Path to file to open

Raises:
  RuntimeError: If no editor is available
- `open_in_pager(path) -> None`: Open file in pager.

Args:
  path: Path to file to open

Raises:
  RuntimeError: If no pager is available
- `root_option_callback(value) -> Path`: Callback to process root directory option with auto-detection.

Args:
    value: The provided root path, or None to auto-detect

Returns:
    Resolved root path
- `version_callback(value) -> None`: Print version and exit if --version flag is provided.

Args:
    value: Whether --version was specified
