"""Main CLI entry point for spec-driver unified interface."""

from __future__ import annotations

import typer

from supekku.cli import complete, create, show, sync, workspace
from supekku.cli import list as list_module
from supekku.cli.common import VersionOption

# Main Typer application
app = typer.Typer(
  name="spec-driver",
  help="Specification-driven development toolkit with multi-language spec sync",
  no_args_is_help=True,
)


def version_callback(_value: bool | None = None) -> None:
  """Handle version option."""
  # Version is handled by common.VersionOption


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
  complete.app,
  name="complete",
  help="Complete artifacts (mark deltas as completed)",
)


# Main entry point
def main(_version: VersionOption = None) -> None:
  """Spec-driver CLI main entry point."""
  app()


if __name__ == "__main__":
  main()
