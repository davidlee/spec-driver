"""Main CLI entry point for spec-driver unified interface."""

from __future__ import annotations

import sys

if sys.version_info < (3, 12):  # noqa: UP036 — defensive guard for broken installs
  sys.exit(
    f"spec-driver requires Python >= 3.12 "
    f"(running {sys.version_info.major}.{sys.version_info.minor}). "
    f"Install with: uv tool install spec-driver --python 3.12"
  )

import click
import typer

from supekku.cli import (
  admin,
  complete,
  create,
  edit,
  find,
  show,
  sync,
  view,
  workflow,
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


def _init_paths_from_config() -> dict | None:
  """Initialize path constants from workflow.toml if in a repo.

  Silently skips if not in a repo — commands like --help and install
  must work without a workspace.

  Returns the loaded config dict, or ``None`` if not in a workspace.
  """
  from supekku.scripts.lib.core.config import load_workflow_config  # noqa: PLC0415
  from supekku.scripts.lib.core.paths import init_paths  # noqa: PLC0415
  from supekku.scripts.lib.core.repo import find_repo_root  # noqa: PLC0415

  try:
    root = find_repo_root()
  except RuntimeError:
    return None
  config = load_workflow_config(root)
  init_paths(config)
  return config


def _warn_if_version_stale(config: dict) -> None:
  """Emit a stderr warning when the installed version has drifted.

  Compares ``spec_driver_installed_version`` in *config* (from
  ``workflow.toml``) against the running package version.  Skipped
  when the active command is ``install`` (which will stamp the version
  itself).
  """
  if "install" in sys.argv[1:2]:
    return

  from supekku.scripts.lib.core.version import get_package_version  # noqa: PLC0415

  installed = config.get("spec_driver_installed_version")
  current = get_package_version()

  if installed == current:
    return

  if installed is None:
    detail = "no version stamp found in workflow.toml"
  else:
    detail = f"workflow.toml has {installed}, running {current}"

  sys.stderr.write(
    f"Warning: spec-driver may need re-install ({detail}).\n"
    "  Run: spec-driver install\n"
  )


@app.callback()
def _app_callback(_version: VersionOption = None) -> None:
  """Process global options and initialize path configuration."""
  config = _init_paths_from_config()
  if config is not None:
    _warn_if_version_stale(config)


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
  help="View artifacts (rendered markdown; use -p for pager)",
)

app.add_typer(
  view.app,
  name="read",
  help="Read artifacts (alias for view)",
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
  admin.app,
  name="admin",
  help="Workspace maintenance commands",
)

app.add_typer(
  workflow.phase_app,
  name="phase",
  help="Workflow phase operations",
)

app.add_typer(
  workflow.workflow_app,
  name="workflow",
  help="Workflow orchestration commands",
)

app.add_typer(
  workflow.accept_app,
  name="accept",
  help="Accept workflow artifacts (handoffs)",
)

app.add_typer(
  workflow.review_app,
  name="review",
  help="Review lifecycle commands",
)

app.command("block", help="Block a workflow (transitions to blocked state)")(
  workflow.block_command
)

app.command("unblock", help="Unblock a workflow (restores previous state)")(
  workflow.unblock_command
)


@app.command("tui", help="Launch the TUI artifact browser")
def tui_command() -> None:
  """Launch the interactive TUI artifact browser."""
  from supekku.scripts.lib.core.repo import find_repo_root  # noqa: PLC0415
  from supekku.tui.app import SpecDriverApp  # noqa: PLC0415

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
