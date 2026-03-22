"""Common utilities, options, and callbacks for CLI commands.

This module provides reusable CLI option types, shared data types for artifact
resolution, and consistent flag behavior across all CLI commands.

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

import enum
import re
from pathlib import Path
from typing import Annotated, NoReturn

import click
import typer

# Exit codes
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_PRECONDITION = 2
EXIT_GUARD_VIOLATION = 3

# JSON envelope version — increment when envelope shape changes (DE-108)
CLI_JSON_ENVELOPE_VERSION = 1


def cli_json_success(command: str, data: dict) -> dict:
  """Build a success JSON envelope for structured CLI output.

  Args:
    command: Dotted command name (e.g. 'review.prime').
    data: Command-specific payload.
  """
  return {
    "version": CLI_JSON_ENVELOPE_VERSION,
    "command": command,
    "status": "ok",
    "exit_code": EXIT_SUCCESS,
    "data": data,
  }


def cli_json_error(
  command: str,
  exit_code: int,
  kind: str,
  message: str,
) -> dict:
  """Build an error JSON envelope for structured CLI output.

  Args:
    command: Dotted command name (e.g. 'review.prime').
    exit_code: One of EXIT_FAILURE, EXIT_PRECONDITION, EXIT_GUARD_VIOLATION.
    kind: Error category — 'precondition', 'guard_violation', 'validation',
          or 'unexpected'.
    message: Human-readable error description.
  """
  return {
    "version": CLI_JSON_ENVELOPE_VERSION,
    "command": command,
    "status": "error",
    "exit_code": exit_code,
    "error": {
      "kind": kind,
      "message": message,
    },
  }


def emit_json_and_exit(payload: dict) -> NoReturn:
  """Print a JSON envelope to stdout and exit with the embedded exit code.

  In JSON mode, this is the sole output path — nothing goes to stderr.
  """
  import json  # noqa: PLC0415

  typer.echo(json.dumps(payload, indent=2))
  raise typer.Exit(payload["exit_code"])


class ContentType(str, enum.Enum):
  """Unified output content-type selector for show commands."""

  markdown = "markdown"
  frontmatter = "frontmatter"
  yaml = "yaml"


ContentTypeOption = Annotated[
  ContentType | None,
  typer.Option(
    "--content-type",
    "-c",
    help=(
      "Output content type: markdown (full file),"
      " frontmatter (metadata), yaml (raw YAML block)"
    ),
  ),
]


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

ExternalOption = Annotated[
  bool,
  typer.Option(
    "--external",
    "-e",
    help="Show external system ID column (ext_id)",
  ),
]

PagerOption = Annotated[
  bool,
  typer.Option(
    "--pager",
    "-p",
    help="Open in pager instead of rendering to stdout",
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


class InferringGroup(typer.core.TyperGroup):
  """Typer Group that infers artifact type from bare IDs.

  When resolve_command() encounters an unknown subcommand name, it stores
  the name as an inferred artifact ID and routes to the hidden "inferred"
  command for resolution.
  """

  def resolve_command(
    self, ctx: click.Context, args: list[str]
  ) -> tuple[str | None, click.Command | None, list[str]]:
    """Resolve command, falling back to ID inference for unknown names."""
    try:
      return super().resolve_command(ctx, args)
    except click.UsageError:
      if not args:
        raise
      # First arg is not a known subcommand — treat as artifact ID
      cmd_name = args[0]
      ctx.ensure_object(dict)
      ctx.obj["inferred_id"] = cmd_name
      cmd = self.get_command(ctx, "inferred")
      if cmd is None:
        raise
      return "inferred", cmd, args[1:]


# ---------------------------------------------------------------------------
# Re-exports for backward compatibility (DE-114)
#
# Importers can continue using `from supekku.cli.common import X` for symbols
# that now live in artifacts.py, ids.py, or io.py. A follow-up will update
# importers to use canonical paths and remove these re-exports.
# ---------------------------------------------------------------------------

from supekku.cli.artifacts import (  # noqa: E402, F401
  AmbiguousArtifactError,
  ArtifactNotFoundError,
  ArtifactRef,
  _matches_pattern,
  emit_artifact,
  extract_yaml_frontmatter,
  find_artifacts,
  load_all_artifacts,
  resolve_artifact,
  resolve_by_id,
)
from supekku.cli.ids import (  # noqa: E402, F401
  ARTIFACT_PREFIXES,
  ARTIFACT_PREFIXES_PLAN,
  PREFIX_TO_TYPE,
  _normalize_plan_id,
  _parse_prefix,
  normalize_id,
)
from supekku.cli.io import (  # noqa: E402, F401
  get_editor,
  get_pager,
  open_in_editor,
  open_in_pager,
  render_file,
  render_file_paged,
)
