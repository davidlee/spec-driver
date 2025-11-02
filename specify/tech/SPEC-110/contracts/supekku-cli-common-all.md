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

- `matches_regexp(pattern, text_fields, case_insensitive) -> bool`: Check if any of the text fields match the given regexp pattern.

Args:
  pattern: Regular expression pattern (None means no filtering)
  text_fields: List of text fields to search
  case_insensitive: Whether to perform case-insensitive matching

Returns:
  True if pattern is None (no filter) or if any field matches the pattern

Raises:
  re.error: If the pattern is invalid
- `root_option_callback(value) -> Path`: Callback to process root directory option with auto-detection.

Args:
    value: The provided root path, or None to auto-detect

Returns:
    Resolved root path
- `version_callback(value) -> None`: Print version and exit if --version flag is provided.

Args:
    value: Whether --version was specified
