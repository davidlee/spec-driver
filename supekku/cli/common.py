"""Common utilities, options, and callbacks for CLI commands."""

from __future__ import annotations

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
    from importlib.metadata import version

    try:
      pkg_version = version("spec-driver")
    except Exception:  # pragma: no cover
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
