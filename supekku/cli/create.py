"""Create commands for specs, deltas, requirements, revisions, and ADRs."""

from __future__ import annotations

import json
import re
from typing import Annotated

import typer

from supekku.cli.common import EXIT_FAILURE, EXIT_SUCCESS, RootOption
from supekku.cli.hints import print_schema_hints
from supekku.scripts.lib.backlog.registry import create_backlog_entry
from supekku.scripts.lib.cards import CardRegistry
from supekku.scripts.lib.changes.creation import (
  PhaseCreationError,
  create_audit,
  create_delta,
  create_phase,
  create_plan,
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
from supekku.scripts.lib.memory.creation import (
  MemoryAlreadyExistsError,
  MemoryCreationOptions,
)
from supekku.scripts.lib.memory.creation import (
  create_memory as create_memory_impl,
)
from supekku.scripts.lib.memory.registry import MemoryRegistry
from supekku.scripts.lib.policies.creation import (
  PolicyAlreadyExistsError,
  PolicyCreationOptions,
)
from supekku.scripts.lib.policies.creation import (
  create_policy as create_policy_impl,
)
from supekku.scripts.lib.policies.registry import PolicyRegistry
from supekku.scripts.lib.specs.creation import (
  CreateSpecOptions,
  SpecCreationError,
)
from supekku.scripts.lib.specs.creation import (
  create_spec as create_spec_impl,
)
from supekku.scripts.lib.standards.creation import (
  StandardAlreadyExistsError,
  StandardCreationOptions,
)
from supekku.scripts.lib.standards.creation import (
  create_standard as create_standard_impl,
)
from supekku.scripts.lib.standards.registry import StandardRegistry

app = typer.Typer(help="Create new artifacts", no_args_is_help=True)

_BACKLOG_ID_RE = re.compile(r"^(ISSUE|PROB|IMPR|RISK)-\d+$")



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
    hint_kind = "prod" if spec_type == "product" else "spec"
    print_schema_hints(hint_kind)
    raise typer.Exit(EXIT_SUCCESS)
  except SpecCreationError as e:
    typer.echo(f"Error creating spec: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("delta")
def create_delta_cmd(
  name: Annotated[str | None, typer.Argument(help="Delta title")] = None,
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
  from_backlog: Annotated[
    bool,
    typer.Option(
      "--from-backlog",
      help="Treat name argument as a backlog item ID to pre-populate from",
    ),
  ] = False,
) -> None:
  """Create a Delta bundle with optional plan scaffolding.

  Can create from scratch with a title, or populate from a backlog item
  using --from-backlog ITEM-ID (where ITEM-ID is passed as the name argument).
  """
  try:
    # If --from-backlog, treat name as a backlog item ID
    if from_backlog:
      if not name or not _BACKLOG_ID_RE.match(name):
        typer.echo(
          "Error: --from-backlog requires a backlog item ID as the name argument "
          "(e.g., create delta --from-backlog ISSUE-123)",
          err=True,
        )
        raise typer.Exit(EXIT_FAILURE)

      from supekku.scripts.lib.backlog.registry import BacklogRegistry

      registry = BacklogRegistry(root=None)
      item = registry.find(name)

      if not item:
        typer.echo(f"Error: backlog item '{name}' not found", err=True)
        raise typer.Exit(EXIT_FAILURE)

      # Pre-populate from backlog item
      name = item.title

      if not requirements and item.frontmatter:
        related_reqs = item.frontmatter.get("related_requirements", [])
        if related_reqs:
          requirements = related_reqs

      typer.echo(f"Creating delta from backlog item: {item.id}")
      typer.echo(f"  Title: {item.title}")
      if requirements:
        typer.echo(f"  Requirements: {', '.join(requirements)}")
      typer.echo("")

    # Name is required
    if not name:
      typer.echo(
        "Error: delta name is required (or use --from-backlog ITEM-ID)",
        err=True,
      )
      raise typer.Exit(EXIT_FAILURE)

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
    print_schema_hints("delta")
    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error creating delta: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("plan")
def create_plan_cmd(
  delta: Annotated[
    str,
    typer.Option("--delta", help="Delta ID (e.g., DE-041)"),
  ],
  root: RootOption = None,
) -> None:
  """Create an implementation plan for an existing delta."""
  try:
    plan_path = create_plan(delta, repo_root=root)
    typer.echo(f"Plan created: {plan_path.stem}")
    typer.echo(str(plan_path))
    print_schema_hints("plan")
    raise typer.Exit(EXIT_SUCCESS)
  except FileExistsError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
  except FileNotFoundError as e:
    typer.echo(f"Error: {e}", err=True)
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
    print_schema_hints("phase")
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
    print_schema_hints("revision")
    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error creating revision: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("audit")
def create_audit_cmd(
  title: Annotated[str, typer.Argument(help="Audit title")],
  mode: Annotated[
    str,
    typer.Option(
      "--mode",
      help="Audit mode: conformance or discovery",
    ),
  ] = "conformance",
  delta: Annotated[
    str | None,
    typer.Option(
      "--delta",
      help="Owning delta ID (e.g. DE-079)",
    ),
  ] = None,
  specs: Annotated[
    list[str] | None,
    typer.Option(
      "--spec",
      help="Spec ID referenced (repeatable)",
    ),
  ] = None,
  prods: Annotated[
    list[str] | None,
    typer.Option(
      "--prod",
      help="Product spec ID referenced (repeatable)",
    ),
  ] = None,
  code_scope: Annotated[
    list[str] | None,
    typer.Option(
      "--code-scope",
      help="Code scope pattern (repeatable)",
    ),
  ] = None,
) -> None:
  """Create an Audit bundle."""
  try:
    result = create_audit(
      title,
      mode=mode,
      delta_ref=delta,
      spec_refs=specs,
      prod_refs=prods,
      code_scope=code_scope,
    )
    typer.echo(f"Audit created: {result.artifact_id}")
    typer.echo(str(result.primary_path))
    print_schema_hints("audit")
    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error creating audit: {e}", err=True)
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


@app.command("policy")
def create_policy(
  title: Annotated[str, typer.Argument(help="Title for the new policy")],
  status: Annotated[
    str,
    typer.Option(
      "--status",
      "-s",
      help="Initial status (draft, required; default: draft)",
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
  """Create a new policy with the next available ID."""
  try:
    registry = PolicyRegistry(root=root)
    options = PolicyCreationOptions(
      title=title,
      status=status,
      author=author,
      author_email=author_email,
    )

    result = create_policy_impl(registry, options, sync_registry=True)
    typer.echo(f"Created policy: {result.policy_id}")
    typer.echo(str(result.path))
    print_schema_hints("policy")
    raise typer.Exit(EXIT_SUCCESS)

  except PolicyAlreadyExistsError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error creating policy: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("standard")
def create_standard(
  title: Annotated[str, typer.Argument(help="Title for the new standard")],
  status: Annotated[
    str,
    typer.Option(
      "--status",
      "-s",
      help="Initial status (draft, required, default; default: draft)",
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
  """Create a new standard with the next available ID."""
  try:
    registry = StandardRegistry(root=root)
    options = StandardCreationOptions(
      title=title,
      status=status,
      author=author,
      author_email=author_email,
    )

    result = create_standard_impl(registry, options, sync_registry=True)
    typer.echo(f"Created standard: {result.standard_id}")
    typer.echo(str(result.path))
    print_schema_hints("standard")
    raise typer.Exit(EXIT_SUCCESS)

  except StandardAlreadyExistsError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error creating standard: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("issue")
def create_issue(
  title: Annotated[str, typer.Argument(help="Issue title")],
  json_output: Annotated[
    bool,
    typer.Option(
      "--json",
      help="Output result as JSON",
    ),
  ] = False,
  root: RootOption = None,
) -> None:
  """Create a new issue backlog entry."""
  try:
    path = create_backlog_entry("issue", title, repo_root=root)
    # Extract ID from filename (e.g., ISSUE-001.md -> ISSUE-001)
    issue_id = path.stem

    if json_output:
      result = {
        "id": issue_id,
        "path": str(path),
        "kind": "issue",
        "status": "open",
      }
      typer.echo(json.dumps(result, indent=2))
    else:
      typer.echo(f"Issue created: {issue_id}")
      typer.echo(str(path))
    raise typer.Exit(EXIT_SUCCESS)
  except (ValueError, FileNotFoundError) as e:
    typer.echo(f"Error creating issue: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("problem")
def create_problem(
  title: Annotated[str, typer.Argument(help="Problem title")],
  json_output: Annotated[
    bool,
    typer.Option(
      "--json",
      help="Output result as JSON",
    ),
  ] = False,
  root: RootOption = None,
) -> None:
  """Create a new problem backlog entry."""
  try:
    path = create_backlog_entry("problem", title, repo_root=root)
    # Extract ID from filename (e.g., PROB-001.md -> PROB-001)
    problem_id = path.stem

    if json_output:
      result = {
        "id": problem_id,
        "path": str(path),
        "kind": "problem",
        "status": "open",
      }
      typer.echo(json.dumps(result, indent=2))
    else:
      typer.echo(f"Problem created: {problem_id}")
      typer.echo(str(path))
    raise typer.Exit(EXIT_SUCCESS)
  except (ValueError, FileNotFoundError) as e:
    typer.echo(f"Error creating problem: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("improvement")
def create_improvement(
  title: Annotated[str, typer.Argument(help="Improvement title")],
  json_output: Annotated[
    bool,
    typer.Option(
      "--json",
      help="Output result as JSON",
    ),
  ] = False,
  root: RootOption = None,
) -> None:
  """Create a new improvement backlog entry."""
  try:
    path = create_backlog_entry("improvement", title, repo_root=root)
    # Extract ID from filename (e.g., IMPR-001.md -> IMPR-001)
    improvement_id = path.stem

    if json_output:
      result = {
        "id": improvement_id,
        "path": str(path),
        "kind": "improvement",
        "status": "open",
      }
      typer.echo(json.dumps(result, indent=2))
    else:
      typer.echo(f"Improvement created: {improvement_id}")
      typer.echo(str(path))
    raise typer.Exit(EXIT_SUCCESS)
  except (ValueError, FileNotFoundError) as e:
    typer.echo(f"Error creating improvement: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("risk")
def create_risk(
  title: Annotated[str, typer.Argument(help="Risk title")],
  json_output: Annotated[
    bool,
    typer.Option(
      "--json",
      help="Output result as JSON",
    ),
  ] = False,
  root: RootOption = None,
) -> None:
  """Create a new risk backlog entry."""
  try:
    path = create_backlog_entry("risk", title, repo_root=root)
    # Extract ID from filename (e.g., RISK-001.md -> RISK-001)
    risk_id = path.stem

    if json_output:
      result = {
        "id": risk_id,
        "path": str(path),
        "kind": "risk",
        "status": "open",
      }
      typer.echo(json.dumps(result, indent=2))
    else:
      typer.echo(f"Risk created: {risk_id}")
      typer.echo(str(path))
    raise typer.Exit(EXIT_SUCCESS)
  except (ValueError, FileNotFoundError) as e:
    typer.echo(f"Error creating risk: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("drift")
def create_drift_cmd(
  name: Annotated[str, typer.Argument(help="Drift ledger name")],
  delta: Annotated[
    str | None,
    typer.Option("--delta", help="Owning delta (e.g. DE-065)"),
  ] = None,
  root: RootOption = None,
) -> None:
  """Create a new drift ledger."""
  try:
    from supekku.scripts.lib.drift.creation import create_drift_ledger

    path = create_drift_ledger(name, delta_ref=delta or "", repo_root=root)
    ledger_id = path.stem.split("-", 2)
    dl_id = f"{ledger_id[0]}-{ledger_id[1]}" if len(ledger_id) >= 2 else path.stem
    typer.echo(f"Drift ledger created: {dl_id}")
    typer.echo(str(path))
    raise typer.Exit(EXIT_SUCCESS)
  except (ValueError, FileNotFoundError, OSError) as e:
    typer.echo(f"Error creating drift ledger: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("card")
def create_card(
  description: Annotated[str, typer.Argument(help="Card description/title")],
  lane: Annotated[
    str,
    typer.Option(
      "--lane",
      "-l",
      help="Target lane (backlog/doing/done, default: backlog)",
    ),
  ] = "backlog",
  root: RootOption = None,
) -> None:
  """Create a new kanban card with the next available ID."""
  try:
    registry = CardRegistry(root=root)
    card = registry.create_card(description, lane=lane)

    typer.echo(f"Created card: {card.id}")
    typer.echo(str(card.path))
    raise typer.Exit(EXIT_SUCCESS)

  except ValueError as e:
    typer.echo(f"Error creating card: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
  except FileNotFoundError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("memory")
def create_memory_cmd(
  memory_id: Annotated[
    str,
    typer.Argument(
      help="Semantic ID (e.g., mem.pattern.cli.skinny or pattern.cli.skinny)",
    ),
  ],
  name: Annotated[str, typer.Option("--name", "-n", help="Display name")],
  memory_type: Annotated[
    str,
    typer.Option(
      "--type",
      "-t",
      help="Memory type (concept, fact, pattern, signpost, system, thread)",
    ),
  ],
  status: Annotated[
    str,
    typer.Option("--status", "-s", help="Initial status (default: active)"),
  ] = "active",
  tag: Annotated[
    list[str] | None,
    typer.Option("--tag", help="Tag (repeatable)"),
  ] = None,
  summary: Annotated[
    str,
    typer.Option("--summary", help="Brief summary"),
  ] = "",
  root: RootOption = None,
) -> None:
  """Create a new memory record with a semantic ID.

  ID format: mem.<type>.<domain>.<subject>[.<purpose>]
  The 'mem.' prefix is prepended automatically if omitted.
  """
  try:
    registry = MemoryRegistry(root=root)
    options = MemoryCreationOptions(
      memory_id=memory_id,
      name=name,
      memory_type=memory_type,
      status=status,
      tags=tag or [],
      summary=summary,
    )

    result = create_memory_impl(registry, options)

    if result.warnings:
      for w in result.warnings:
        typer.echo(f"Warning: {w}", err=True)

    typer.echo(f"Created memory: {result.memory_id}")
    typer.echo(str(result.path))
    print_schema_hints("memory")
    raise typer.Exit(EXIT_SUCCESS)

  except MemoryAlreadyExistsError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error creating memory: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


# For direct testing
if __name__ == "__main__":  # pragma: no cover
  app()
