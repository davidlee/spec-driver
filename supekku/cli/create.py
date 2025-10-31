"""Create commands for specs, deltas, requirements, revisions, and ADRs."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from supekku.cli.common import EXIT_FAILURE, EXIT_SUCCESS
from supekku.scripts.lib.changes.creation import (
  create_delta,
  create_requirement_breakout,
  create_revision,
)
from supekku.scripts.lib.decisions.creation import (
  ADRAlreadyExistsError,
  ADRCreationOptions,
)
from supekku.scripts.lib.decisions.creation import (
  create_adr as create_adr_impl,
)
from supekku.scripts.lib.decisions.registry import DecisionRegistry
from supekku.scripts.lib.specs.creation import (
  CreateSpecOptions,
  SpecCreationError,
)
from supekku.scripts.lib.specs.creation import (
  create_spec as create_spec_impl,
)

app = typer.Typer(help="Create new artifacts")


@app.command("spec")
def create_spec(
  spec_name: Annotated[
    list[str],
    typer.Argument(help="Name of the spec to create"),
  ],
  spec_type: Annotated[
    str,
    typer.Option(
      "--type",
      "-t",
      help="Spec type (tech or product)",
    ),
  ] = "tech",
  testing: Annotated[
    bool,
    typer.Option(
      "--testing/--no-testing",
      help="Include companion testing guide (tech specs only)",
    ),
  ] = True,
  json_output: Annotated[
    bool,
    typer.Option(
      "--json",
      help="Emit machine-readable JSON output",
    ),
  ] = False,
) -> None:
  """Create a new SPEC or PROD document bundle from templates."""
  if not spec_name:
    typer.echo("Error: spec name is required", err=True)
    raise typer.Exit(EXIT_FAILURE)

  name = " ".join(spec_name).strip()
  if spec_type not in ["tech", "product"]:
    typer.echo(f"Error: invalid spec type: {spec_type}", err=True)
    raise typer.Exit(EXIT_FAILURE)

  options = CreateSpecOptions(
    spec_type=spec_type,
    include_testing=testing,
    emit_json=json_output,
  )

  try:
    result = create_spec_impl(name, options)
    if options.emit_json or result.test_path:
      pass  # JSON output handled by create_spec_impl
    typer.echo(f"Spec created: {result.spec_id}")
    raise typer.Exit(EXIT_SUCCESS)
  except SpecCreationError as e:
    typer.echo(f"Error creating spec: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("delta")
def create_delta_cmd(
  name: Annotated[str, typer.Argument(help="Delta title")],
  specs: Annotated[
    list[str] | None,
    typer.Option(
      "--spec",
      "-s",
      help="Spec ID impacted (repeatable)",
    ),
  ] = None,
  requirements: Annotated[
    list[str] | None,
    typer.Option(
      "--requirement",
      "-r",
      help="Requirement ID impacted (repeatable)",
    ),
  ] = None,
  allow_missing_plan: Annotated[
    bool,
    typer.Option(
      "--allow-missing-plan",
      help="Skip implementation plan and phase scaffolding",
    ),
  ] = False,
) -> None:
  """Create a Delta bundle with optional plan scaffolding."""
  try:
    result = create_delta(
      name,
      specs=specs,
      requirements=requirements,
      allow_missing_plan=allow_missing_plan,
    )
    typer.echo(f"Delta created: {result.artifact_id}")
    for extra in result.extras:
      typer.echo(f"  Created: {extra}")
    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error creating delta: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("requirement")
def create_requirement(
  spec: Annotated[str, typer.Argument(help="Spec ID (e.g. SPEC-200)")],
  requirement: Annotated[str, typer.Argument(help="Requirement code (e.g. FR-010)")],
  title: Annotated[str, typer.Argument(help="Requirement title")],
  kind: Annotated[
    str | None,
    typer.Option(
      "--kind",
      "-k",
      help="Requirement kind (functional, non-functional, policy, standard)",
    ),
  ] = None,
) -> None:
  """Create a breakout requirement file under a spec."""
  if kind and kind not in ["functional", "non-functional", "policy", "standard"]:
    typer.echo(f"Error: invalid requirement kind: {kind}", err=True)
    raise typer.Exit(EXIT_FAILURE)

  try:
    create_requirement_breakout(
      spec,
      requirement,
      title=title,
      kind=kind,
    )
    typer.echo(f"Requirement created: {requirement} under {spec}")
    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error creating requirement: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("revision")
def create_revision_cmd(
  name: Annotated[str, typer.Argument(help="Revision title (summary)")],
  source_specs: Annotated[
    list[str] | None,
    typer.Option(
      "--source",
      "-s",
      help="Source spec ID (repeatable)",
    ),
  ] = None,
  destination_specs: Annotated[
    list[str] | None,
    typer.Option(
      "--destination",
      "-d",
      help="Destination spec ID (repeatable)",
    ),
  ] = None,
  requirements: Annotated[
    list[str] | None,
    typer.Option(
      "--requirement",
      "-r",
      help="Requirement ID affected (repeatable)",
    ),
  ] = None,
) -> None:
  """Create a Spec Revision bundle."""
  try:
    result = create_revision(
      name,
      source_specs=source_specs,
      destination_specs=destination_specs,
      requirements=requirements,
    )
    typer.echo(f"Revision created: {result.artifact_id}")
    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error creating revision: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("adr")
def create_adr(
  title: Annotated[str, typer.Argument(help="Title for the new ADR")],
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
  root: Annotated[
    Path | None,
    typer.Option(
      "--root",
      help="Repository root (auto-detected if omitted)",
    ),
  ] = None,
) -> None:
  """Create a new ADR with the next available ID."""
  try:
    repo_root = root if root else Path.cwd()
    registry = DecisionRegistry(root=repo_root)
    options = ADRCreationOptions(
      title=title,
      status=status,
      author=author,
      author_email=author_email,
    )

    result = create_adr_impl(registry, options, sync_registry=True)
    typer.echo(f"Created ADR: {result.path}")
    raise typer.Exit(EXIT_SUCCESS)

  except ADRAlreadyExistsError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error creating ADR: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


# For direct testing
if __name__ == "__main__":  # pragma: no cover
  app()
