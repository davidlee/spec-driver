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


# --- Pager and Editor utilities ---


def get_pager() -> str | None:
  """Get pager command from environment or fallback.

  Resolution order: $PAGER -> less -> more

  Returns:
    Pager command string, or None if no pager available.

  """
  import os
  import shutil

  if pager := os.environ.get("PAGER"):
    return pager
  for cmd in ("less", "more"):
    if shutil.which(cmd):
      return cmd
  return None


def get_editor() -> str | None:
  """Get editor command from environment or fallback.

  Resolution order: $EDITOR -> $VISUAL -> vi

  Returns:
    Editor command string, or None if no editor available.

  """
  import os
  import shutil

  for var in ("EDITOR", "VISUAL"):
    if editor := os.environ.get(var):
      return editor
  if shutil.which("vi"):
    return "vi"
  return None


def open_in_pager(path: Path | str) -> None:
  """Open file in pager.

  Args:
    path: Path to file to open

  Raises:
    RuntimeError: If no pager is available

  """
  import subprocess

  pager = get_pager()
  if not pager:
    msg = "No pager found. Set $PAGER or install less."
    raise RuntimeError(msg)
  subprocess.run([pager, str(path)], check=True)


def open_in_editor(path: Path | str) -> None:
  """Open file in editor.

  Args:
    path: Path to file to open

  Raises:
    RuntimeError: If no editor is available

  """
  import subprocess

  editor = get_editor()
  if not editor:
    msg = "No editor found. Set $EDITOR or install vi."
    raise RuntimeError(msg)
  subprocess.run([editor, str(path)], check=True)


# --- ID normalization for shorthand support ---

# Artifact types with unambiguous prefixes (can use numeric shorthand)
ARTIFACT_PREFIXES: dict[str, str] = {
  "adr": "ADR-",
  "delta": "DE-",
  "revision": "RE-",
  "policy": "POL-",
  "standard": "STD-",
}


def normalize_id(artifact_type: str, raw_id: str) -> str:
  """Normalize artifact ID by prepending prefix if raw_id is numeric-only.

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

  """
  if artifact_type not in ARTIFACT_PREFIXES:
    return raw_id  # No normalization for ambiguous types

  prefix = ARTIFACT_PREFIXES[artifact_type]

  # Already has correct prefix
  if raw_id.upper().startswith(prefix):
    return raw_id.upper()

  # Numeric-only: prepend prefix with zero-padding
  if raw_id.isdigit():
    return f"{prefix}{int(raw_id):03d}"

  # Not numeric, return as-is (might be a slug or other format)
  return raw_id
