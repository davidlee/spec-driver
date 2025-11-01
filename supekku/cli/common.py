"""Common utilities, options, and callbacks for CLI commands.

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
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Annotated

import typer

# Exit codes
EXIT_SUCCESS = 0
EXIT_FAILURE = 1


def root_option_callback(value: Path | None) -> Path:
  """Callback to process root directory option with auto-detection.

  Args:
      value: The provided root path, or None to auto-detect

  Returns:
      Resolved root path

  """
  if value is None:
    return Path.cwd()
  return value.resolve()


# Common option definitions for reuse
RootOption = Annotated[
  Path | None,
  typer.Option(
    "--root",
    help="Repository root (auto-detected if omitted)",
    callback=root_option_callback,
    exists=True,
    file_okay=False,
    dir_okay=True,
    resolve_path=True,
  ),
]


def version_callback(value: bool) -> None:
  """Print version and exit if --version flag is provided.

  Args:
      value: Whether --version was specified

  """
  if value:
    from importlib.metadata import PackageNotFoundError, version

    try:
      pkg_version = version("spec-driver")
    except PackageNotFoundError:  # pragma: no cover
      pkg_version = "unknown"
    typer.echo(f"spec-driver {pkg_version}")
    raise typer.Exit(EXIT_SUCCESS)


# Version option for main app
VersionOption = Annotated[
  bool | None,
  typer.Option(
    "--version",
    callback=version_callback,
    is_eager=True,
    help="Show version and exit",
  ),
]

# Standardized list command options
FormatOption = Annotated[
  str,
  typer.Option(
    "--format",
    help="Output format: table (rich), json (structured), or tsv (tabs)",
  ),
]

TruncateOption = Annotated[
  bool,
  typer.Option(
    "--truncate",
    help="Truncate long fields to fit terminal width",
  ),
]

RegexpOption = Annotated[
  str | None,
  typer.Option(
    "--regexp",
    "-r",
    help="Regular expression pattern for filtering on title/name/summary",
  ),
]

CaseInsensitiveOption = Annotated[
  bool,
  typer.Option(
    "--case-insensitive",
    "-i",
    help="Make regexp matching case-insensitive",
  ),
]


def matches_regexp(
  pattern: str | None,
  text_fields: list[str],
  case_insensitive: bool = False,
) -> bool:
  """Check if any of the text fields match the given regexp pattern.

  Args:
    pattern: Regular expression pattern (None means no filtering)
    text_fields: List of text fields to search
    case_insensitive: Whether to perform case-insensitive matching

  Returns:
    True if pattern is None (no filter) or if any field matches the pattern

  Raises:
    re.error: If the pattern is invalid

  """
  if pattern is None:
    return True

  flags = re.IGNORECASE if case_insensitive else 0
  compiled_pattern = re.compile(pattern, flags)

  return any(compiled_pattern.search(field) for field in text_fields if field)
