"""Main CLI entry point for spec-driver unified interface."""

from __future__ import annotations

import sys

import click
import typer

from supekku.cli import (
  backfill,
  compact,
  complete,
  create,
  edit,
  find,
  resolve,
  schema,
  show,
  skills,
  sync,
  view,
  workspace,
)
from supekku.cli import list as list_module
from supekku.cli.common import VersionOption
from supekku.scripts.lib.core.events import (
  command_was_invoked,
  emit_event,
  mark_command_invoked,
)

# Intercept leaf Command.invoke to set the command-invocation flag (DEC-052-01).
# Groups (click.Group) are excluded so help/no-args paths don't trigger emission.
_original_command_invoke = click.Command.invoke


def _tracking_invoke(self, ctx):  # type: ignore[no-untyped-def]
  if not isinstance(self, click.Group):
    mark_command_invoked()
  return _original_command_invoke(self, ctx)


click.Command.invoke = _tracking_invoke  # type: ignore[assignment]

# Main Typer application
app = typer.Typer(
  name="spec-driver",
  help="The specification-driving development toolkit.",
  no_args_is_help=True,
)


def _init_paths_from_config() -> None:
  """Initialize path constants from workflow.toml if in a repo.

  Silently skips if not in a repo — commands like --help and install
  must work without a workspace.
  """
  from supekku.scripts.lib.core.config import load_workflow_config  # noqa: PLC0415
  from supekku.scripts.lib.core.paths import init_paths  # noqa: PLC0415
  from supekku.scripts.lib.core.repo import find_repo_root  # noqa: PLC0415

  try:
    root = find_repo_root()
  except RuntimeError:
    return
  config = load_workflow_config(root)
  init_paths(config)


@app.callback()
def _app_callback(_version: VersionOption = None) -> None:
  """Process global options and initialize path configuration."""
  _init_paths_from_config()


# Top-level commands
app.command(
  "install",
  help="Initialize spec-driver workspace structure and registry files",
)(workspace.install)

app.command(
  "validate",
  help="Validate workspace metadata and relationships",
)(workspace.validate)

app.command(
  "doctor",
  help="Run workspace health diagnostics",
)(workspace.doctor)

app.command(
  "sync",
  help="Synchronize specifications and registries with source code",
)(sync.sync)

# Add command groups with verb-noun structure
app.add_typer(
  create.app,
  name="create",
  help="Create new artifacts (specs, deltas, requirements, revisions, ADRs)",
)

app.add_typer(
  list_module.app,
  name="list",
  help="List artifacts (specs, deltas, changes, adrs)",
)

app.add_typer(
  show.app,
  name="show",
  help="Show detailed artifact information",
)

app.add_typer(
  view.app,
  name="view",
  help="View artifacts in pager ($PAGER)",
)

app.add_typer(
  edit.app,
  name="edit",
  help="Edit artifacts in editor ($EDITOR)",
)

app.add_typer(
  find.app,
  name="find",
  help="Find artifacts by ID across the repository",
)

app.add_typer(
  complete.app,
  name="complete",
  help="Complete artifacts (mark deltas as completed)",
)

app.add_typer(
  schema.app,
  name="schema",
  help="Show YAML block schemas",
)

app.add_typer(
  resolve.app,
  name="resolve",
  help="Resolve cross-artifact references",
)

app.add_typer(
  backfill.app,
  name="backfill",
  help="Backfill incomplete stub specifications",
)

app.add_typer(
  skills.app,
  name="skills",
  help="Manage agent skill exposure",
)

app.add_typer(
  compact.app,
  name="compact",
  help="Compact artifact frontmatter by stripping default/derived fields",
)


@app.command("tui", help="Launch the TUI artifact browser")
def tui_command() -> None:
  """Launch the interactive TUI artifact browser."""
  try:
    from supekku.tui.app import SpecDriverApp  # noqa: PLC0415
  except ImportError:
    typer.echo(
      "TUI dependencies not installed. Install with:\n"
      '  uv pip install -e ".[tui]"\n'
      "  # or: uv sync --extra tui",
      err=True,
    )
    raise typer.Exit(code=1) from None

  from supekku.scripts.lib.core.repo import find_repo_root  # noqa: PLC0415

  root = find_repo_root()
  app_instance = SpecDriverApp(root=root)
  app_instance.run()


# Main entry point — process-boundary wrapper (DEC-052-01)


def _emit(argv: list[str], exit_code: int | None) -> None:
  """Emit event if a leaf command was invoked and events are enabled."""
  if not command_was_invoked():
    return
  try:
    from supekku.scripts.lib.core.config import load_workflow_config  # noqa: PLC0415
    from supekku.scripts.lib.core.repo import find_repo_root  # noqa: PLC0415

    config = load_workflow_config(find_repo_root())
    if not config.get("events", {}).get("enabled", True):
      return
  except Exception:  # noqa: BLE001
    pass  # Outside workspace or config error — still emit (fail-open)

  code = exit_code if isinstance(exit_code, int) else (1 if exit_code else 0)
  status = "ok" if code == 0 else "error"
  emit_event(argv=argv, exit_code=code, status=status)


def main() -> None:
  """Spec-driver CLI main entry point."""
  try:
    app()
  except SystemExit as exc:
    _emit(sys.argv[1:], exc.code)
    raise
  except BaseException:
    _emit(sys.argv[1:], 1)
    raise


if __name__ == "__main__":
  main()
