"""Show commands for displaying detailed information about artifacts."""

from __future__ import annotations

from typing import Annotated

import typer

from supekku.cli.common import EXIT_FAILURE, EXIT_SUCCESS, RootOption
from supekku.scripts.lib.changes.registry import ChangeRegistry
from supekku.scripts.lib.core.repo import find_repo_root
from supekku.scripts.lib.decisions.registry import DecisionRegistry
from supekku.scripts.lib.formatters.change_formatters import (
  format_delta_details,
  format_revision_details,
)
from supekku.scripts.lib.formatters.decision_formatters import format_decision_details
from supekku.scripts.lib.formatters.requirement_formatters import (
  format_requirement_details,
)
from supekku.scripts.lib.formatters.spec_formatters import format_spec_details
from supekku.scripts.lib.requirements.registry import RequirementsRegistry
from supekku.scripts.lib.specs.registry import SpecRegistry

app = typer.Typer(help="Show detailed artifact information", no_args_is_help=True)


@app.command("spec")
def show_spec(
  spec_id: Annotated[str, typer.Argument(help="Spec ID (e.g., SPEC-009, PROD-042)")],
  root: RootOption = None,
) -> None:
  """Show detailed information about a specification."""
  try:
    registry = SpecRegistry(root=root)
    spec = registry.get(spec_id)

    if not spec:
      typer.echo(f"Error: Specification not found: {spec_id}", err=True)
      raise typer.Exit(EXIT_FAILURE)

    typer.echo(format_spec_details(spec, root=root))
    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("delta")
def show_delta(
  delta_id: Annotated[str, typer.Argument(help="Delta ID (e.g., DE-003)")],
  root: RootOption = None,
) -> None:
  """Show detailed information about a delta."""
  try:
    registry = ChangeRegistry(root=root, kind="delta")
    artifacts = registry.collect()
    artifact = artifacts.get(delta_id)

    if not artifact:
      typer.echo(f"Error: Delta not found: {delta_id}", err=True)
      raise typer.Exit(EXIT_FAILURE)

    typer.echo(format_delta_details(artifact, root=root))
    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("revision")
def show_revision(
  revision_id: Annotated[str, typer.Argument(help="Revision ID (e.g., RE-001)")],
  root: RootOption = None,
) -> None:
  """Show detailed information about a revision."""
  try:
    registry = ChangeRegistry(root=root, kind="revision")
    artifacts = registry.collect()
    artifact = artifacts.get(revision_id)

    if not artifact:
      typer.echo(f"Error: Revision not found: {revision_id}", err=True)
      raise typer.Exit(EXIT_FAILURE)

    typer.echo(format_revision_details(artifact, root=root))
    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("requirement")
def show_requirement(
  req_id: Annotated[str, typer.Argument(help="Requirement ID (e.g., SPEC-009.FR-001)")],
  root: RootOption = None,
) -> None:
  """Show detailed information about a requirement."""
  try:
    repo_root = find_repo_root(root)
    registry_path = repo_root / ".spec-driver" / "registry" / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    requirement = registry.records.get(req_id)

    if not requirement:
      typer.echo(f"Error: Requirement not found: {req_id}", err=True)
      raise typer.Exit(EXIT_FAILURE)

    typer.echo(format_requirement_details(requirement))
    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("adr")
def show_adr(
  decision_id: Annotated[str, typer.Argument(help="Decision ID (e.g., ADR-001)")],
  root: RootOption = None,
) -> None:
  """Show detailed information about a specific decision/ADR."""
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


# For direct testing
if __name__ == "__main__":  # pragma: no cover
  app()
