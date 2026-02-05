"""Edit commands for opening artifacts in an editor."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from supekku.cli.common import EXIT_FAILURE, RootOption, normalize_id, open_in_editor
from supekku.scripts.lib.cards import CardRegistry
from supekku.scripts.lib.changes.registry import ChangeRegistry
from supekku.scripts.lib.core.repo import find_repo_root
from supekku.scripts.lib.decisions.registry import DecisionRegistry
from supekku.scripts.lib.policies.registry import PolicyRegistry
from supekku.scripts.lib.requirements.registry import RequirementsRegistry
from supekku.scripts.lib.specs.registry import SpecRegistry
from supekku.scripts.lib.standards.registry import StandardRegistry

app = typer.Typer(help="Edit artifacts in editor", no_args_is_help=True)


@app.command("spec")
def edit_spec(
  spec_id: Annotated[str, typer.Argument(help="Spec ID (e.g., SPEC-009, PROD-042)")],
  root: RootOption = None,
) -> None:
  """Edit specification in editor."""
  try:
    registry = SpecRegistry(root=root)
    spec = registry.get(spec_id)

    if not spec:
      typer.echo(f"Error: Specification not found: {spec_id}", err=True)
      raise typer.Exit(EXIT_FAILURE)

    open_in_editor(spec.path)
  except typer.Exit:
    raise
  except RuntimeError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("delta")
def edit_delta(
  delta_id: Annotated[str, typer.Argument(help="Delta ID (e.g., DE-003 or 003)")],
  root: RootOption = None,
) -> None:
  """Edit delta in editor."""
  try:
    normalized_id = normalize_id("delta", delta_id)
    registry = ChangeRegistry(root=root, kind="delta")
    artifacts = registry.collect()
    artifact = artifacts.get(normalized_id)

    if not artifact:
      typer.echo(f"Error: Delta not found: {normalized_id}", err=True)
      raise typer.Exit(EXIT_FAILURE)

    open_in_editor(artifact.path)
  except typer.Exit:
    raise
  except RuntimeError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("revision")
def edit_revision(
  revision_id: Annotated[str, typer.Argument(help="Revision ID (e.g., RE-001 or 001)")],
  root: RootOption = None,
) -> None:
  """Edit revision in editor."""
  try:
    normalized_id = normalize_id("revision", revision_id)
    registry = ChangeRegistry(root=root, kind="revision")
    artifacts = registry.collect()
    artifact = artifacts.get(normalized_id)

    if not artifact:
      typer.echo(f"Error: Revision not found: {normalized_id}", err=True)
      raise typer.Exit(EXIT_FAILURE)

    open_in_editor(artifact.path)
  except typer.Exit:
    raise
  except RuntimeError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("requirement")
def edit_requirement(
  req_id: Annotated[str, typer.Argument(help="Requirement ID (e.g., SPEC-009.FR-001)")],
  root: RootOption = None,
) -> None:
  """Edit requirement's spec file in editor."""
  try:
    repo_root = find_repo_root(root)
    registry_path = repo_root / ".spec-driver" / "registry" / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    requirement = registry.records.get(req_id)

    if not requirement:
      typer.echo(f"Error: Requirement not found: {req_id}", err=True)
      raise typer.Exit(EXIT_FAILURE)

    # Requirements are defined in spec files
    req_dict = requirement.to_dict()
    path_str = req_dict.get("path")
    if not path_str or not isinstance(path_str, str):
      typer.echo(f"Error: No path found for requirement: {req_id}", err=True)
      raise typer.Exit(EXIT_FAILURE)

    path = repo_root / path_str
    if not path.exists():
      typer.echo(f"Error: Spec file not found for requirement: {req_id}", err=True)
      raise typer.Exit(EXIT_FAILURE)

    open_in_editor(path)
  except typer.Exit:
    raise
  except RuntimeError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("adr")
def edit_adr(
  decision_id: Annotated[str, typer.Argument(help="Decision ID (e.g., ADR-001, 001)")],
  root: RootOption = None,
) -> None:
  """Edit ADR in editor."""
  try:
    normalized_id = normalize_id("adr", decision_id)
    registry = DecisionRegistry(root=root)
    decision = registry.find(normalized_id)

    if not decision:
      typer.echo(f"Error: Decision not found: {normalized_id}", err=True)
      raise typer.Exit(EXIT_FAILURE)

    open_in_editor(decision.path)
  except typer.Exit:
    raise
  except RuntimeError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("policy")
def edit_policy(
  policy_id: Annotated[str, typer.Argument(help="Policy ID (e.g., POL-001 or 001)")],
  root: RootOption = None,
) -> None:
  """Edit policy in editor."""
  try:
    normalized_id = normalize_id("policy", policy_id)
    registry = PolicyRegistry(root=root)
    policy = registry.find(normalized_id)

    if not policy:
      typer.echo(f"Error: Policy not found: {normalized_id}", err=True)
      raise typer.Exit(EXIT_FAILURE)

    open_in_editor(policy.path)
  except typer.Exit:
    raise
  except RuntimeError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("standard")
def edit_standard(
  standard_id: Annotated[str, typer.Argument(help="Standard ID (e.g., STD-001, 001)")],
  root: RootOption = None,
) -> None:
  """Edit standard in editor."""
  try:
    normalized_id = normalize_id("standard", standard_id)
    registry = StandardRegistry(root=root)
    standard = registry.find(normalized_id)

    if not standard:
      typer.echo(f"Error: Standard not found: {normalized_id}", err=True)
      raise typer.Exit(EXIT_FAILURE)

    open_in_editor(standard.path)
  except typer.Exit:
    raise
  except RuntimeError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("card")
def edit_card(
  card_id: Annotated[str, typer.Argument(help="Card ID (e.g., T123)")],
  anywhere: Annotated[
    bool,
    typer.Option(
      "--anywhere",
      "-a",
      help="Search entire repo instead of just kanban/",
    ),
  ] = False,
  root: RootOption = None,
) -> None:
  """Edit card in editor."""
  try:
    registry = CardRegistry(root=root)
    path = registry.resolve_path(card_id, anywhere=anywhere)

    open_in_editor(Path(path))
  except typer.Exit:
    raise
  except RuntimeError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
  except FileNotFoundError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
  except ValueError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


# For direct testing
if __name__ == "__main__":  # pragma: no cover
  app()
