"""ADR (Architecture Decision Record) management commands."""

from __future__ import annotations

from typing import Annotated

import typer

from supekku.cli.common import EXIT_FAILURE, EXIT_SUCCESS, RootOption
from supekku.scripts.lib.decision_creation import (
  ADRAlreadyExistsError,
  ADRCreationOptions,
  create_adr,
)
from supekku.scripts.lib.decision_registry import DecisionRegistry
from supekku.scripts.lib.formatters.decision_formatters import format_decision_details

app = typer.Typer(help="ADR management commands")


@app.command("sync")
def sync(
  root: RootOption = None,
) -> None:
  """Sync decision registry from ADR files."""
  try:
    registry = DecisionRegistry(root=root)
    registry.sync_with_symlinks()
    typer.echo("ADR registry synchronized successfully")
    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("list")
def list_decisions(
  root: RootOption = None,
  status: Annotated[
    str | None,
    typer.Option(
      "--status",
      "-s",
      help="Filter by status (accepted, draft, deprecated, etc.)",
    ),
  ] = None,
  tag: Annotated[
    str | None,
    typer.Option(
      "--tag",
      "-t",
      help="Filter by tag",
    ),
  ] = None,
  spec: Annotated[
    str | None,
    typer.Option(
      "--spec",
      help="Filter by spec reference",
    ),
  ] = None,
  delta: Annotated[
    str | None,
    typer.Option(
      "--delta",
      "-d",
      help="Filter by delta reference",
    ),
  ] = None,
  requirement: Annotated[
    str | None,
    typer.Option(
      "--requirement",
      "-r",
      help="Filter by requirement reference",
    ),
  ] = None,
  policy: Annotated[
    str | None,
    typer.Option(
      "--policy",
      "-p",
      help="Filter by policy reference",
    ),
  ] = None,
) -> None:
  """List decisions with optional filtering."""
  try:
    registry = DecisionRegistry(root=root)

    # Apply filters
    if any([tag, spec, delta, requirement, policy]):
      decisions = registry.filter(
        tag=tag,
        spec=spec,
        delta=delta,
        requirement=requirement,
        policy=policy,
      )
    else:
      decisions = list(registry.iter(status=status))

    if not decisions:
      raise typer.Exit(EXIT_SUCCESS)

    # Print decisions
    for decision in sorted(decisions, key=lambda d: d.id):
      updated_date = (
        decision.updated.strftime("%Y-%m-%d") if decision.updated else "N/A"
      )
      # Truncate title if too long
      title = decision.title
      if len(title) > 40:
        title = title[:37] + "..."

      typer.echo(f"{decision.id}\t{decision.status}\t{title}\t{updated_date}")

    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("show")
def show(
  decision_id: Annotated[str, typer.Argument(help="Decision ID (e.g., ADR-001)")],
  root: RootOption = None,
) -> None:
  """Show detailed information about a specific decision."""
  try:
    registry = DecisionRegistry(root=root)
    decision = registry.find(decision_id)

    if not decision:
      typer.echo(f"Error: Decision not found: {decision_id}", err=True)
      raise typer.Exit(EXIT_FAILURE)

    typer.echo(format_decision_details(decision))
    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("new")
def new(
  title: Annotated[str, typer.Argument(help="Title for the new ADR")],
  root: RootOption = None,
  status: Annotated[
    str,
    typer.Option(
      "--status",
      "-s",
      help="Initial status (default: draft)",
    ),
  ] = "draft",
  author: Annotated[
    str | None,
    typer.Option(
      "--author",
      "-a",
      help="Author name",
    ),
  ] = None,
  author_email: Annotated[
    str | None,
    typer.Option(
      "--author-email",
      "-e",
      help="Author email",
    ),
  ] = None,
) -> None:
  """Create a new ADR with the next available ID."""
  try:
    registry = DecisionRegistry(root=root)
    options = ADRCreationOptions(
      title=title,
      status=status,
      author=author,
      author_email=author_email,
    )

    result = create_adr(registry, options, sync_registry=True)
    typer.echo(f"Created ADR: {result.path}")
    raise typer.Exit(EXIT_SUCCESS)

  except ADRAlreadyExistsError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


# For direct testing
if __name__ == "__main__":  # pragma: no cover
  app()
