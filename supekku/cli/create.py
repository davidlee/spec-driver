"""Create commands for specs, deltas, requirements, revisions, and ADRs."""

from __future__ import annotations

from typing import Annotated

import typer

from supekku.cli.common import EXIT_FAILURE, EXIT_SUCCESS, RootOption
from supekku.scripts.lib.backlog.registry import create_backlog_entry
from supekku.scripts.lib.changes.creation import (
  PhaseCreationError,
  create_delta,
  create_phase,
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

app = typer.Typer(help="Create new artifacts", no_args_is_help=True)


@app.command("spec")
def create_spec(
  spec_name: Annotated[
    list[str],
    typer.Argument(help="Name of the spec to create"),
  ],
  spec_type: Annotated[
    str,
    typer.Option(
      "--kind",
      "-k",
      help="Spec kind (tech or product)",
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
    typer.echo(f"Error: invalid spec kind: {spec_type}", err=True)
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
    typer.echo(str(result.spec_path))
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
    typer.echo(str(result.primary_path))
    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error creating delta: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("phase")
def create_phase_cmd(
  name: Annotated[str, typer.Argument(help="Phase name")],
  plan: Annotated[str, typer.Option("--plan", help="Plan ID (e.g., IP-002)")],
  root: RootOption = None,
) -> None:
  """Create a new phase for an implementation plan."""
  try:
    result = create_phase(name, plan, repo_root=root)
    typer.echo(f"Phase created: {result.phase_id}")
    typer.echo(str(result.phase_path))
    raise typer.Exit(EXIT_SUCCESS)
  except PhaseCreationError as e:
    typer.echo(f"Error creating phase: {e}", err=True)
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
    path = create_requirement_breakout(
      spec,
      requirement,
      title=title,
      kind=kind,
    )
    typer.echo(f"Requirement created: {requirement} under {spec}")
    typer.echo(str(path))
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
    typer.echo(str(result.primary_path))
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
  root: RootOption = None,
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

    result = create_adr_impl(registry, options, sync_registry=True)
    typer.echo(f"Created ADR: {result.adr_id}")
    typer.echo(str(result.path))
    raise typer.Exit(EXIT_SUCCESS)

  except ADRAlreadyExistsError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error creating ADR: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("issue")
def create_issue(
  title: Annotated[str, typer.Argument(help="Issue title")],
  root: RootOption = None,
) -> None:
  """Create a new issue backlog entry."""
  try:
    path = create_backlog_entry("issue", title, repo_root=root)
    # Extract ID from filename (e.g., ISSUE-001.md -> ISSUE-001)
    issue_id = path.stem
    typer.echo(f"Issue created: {issue_id}")
    typer.echo(str(path))
    raise typer.Exit(EXIT_SUCCESS)
  except (ValueError, FileNotFoundError) as e:
    typer.echo(f"Error creating issue: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("problem")
def create_problem(
  title: Annotated[str, typer.Argument(help="Problem title")],
  root: RootOption = None,
) -> None:
  """Create a new problem backlog entry."""
  try:
    path = create_backlog_entry("problem", title, repo_root=root)
    # Extract ID from filename (e.g., PROB-001.md -> PROB-001)
    problem_id = path.stem
    typer.echo(f"Problem created: {problem_id}")
    typer.echo(str(path))
    raise typer.Exit(EXIT_SUCCESS)
  except (ValueError, FileNotFoundError) as e:
    typer.echo(f"Error creating problem: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("improvement")
def create_improvement(
  title: Annotated[str, typer.Argument(help="Improvement title")],
  root: RootOption = None,
) -> None:
  """Create a new improvement backlog entry."""
  try:
    path = create_backlog_entry("improvement", title, repo_root=root)
    # Extract ID from filename (e.g., IMPR-001.md -> IMPR-001)
    improvement_id = path.stem
    typer.echo(f"Improvement created: {improvement_id}")
    typer.echo(str(path))
    raise typer.Exit(EXIT_SUCCESS)
  except (ValueError, FileNotFoundError) as e:
    typer.echo(f"Error creating improvement: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("risk")
def create_risk(
  title: Annotated[str, typer.Argument(help="Risk title")],
  root: RootOption = None,
) -> None:
  """Create a new risk backlog entry."""
  try:
    path = create_backlog_entry("risk", title, repo_root=root)
    # Extract ID from filename (e.g., RISK-001.md -> RISK-001)
    risk_id = path.stem
    typer.echo(f"Risk created: {risk_id}")
    typer.echo(str(path))
    raise typer.Exit(EXIT_SUCCESS)
  except (ValueError, FileNotFoundError) as e:
    typer.echo(f"Error creating risk: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


# For direct testing
if __name__ == "__main__":  # pragma: no cover
  app()
