"""Edit commands for opening artifacts in an editor or updating status."""

from __future__ import annotations

from datetime import date as date_type
from pathlib import Path
from typing import Annotated

import typer

from supekku.cli.common import (
  EXIT_FAILURE,
  ArtifactNotFoundError,
  RootOption,
  normalize_id,
  open_in_editor,
  resolve_artifact,
)
from supekku.scripts.lib.cards import CardRegistry
from supekku.scripts.lib.changes.registry import ChangeRegistry
from supekku.scripts.lib.core.enums import validate_status_for_entity
from supekku.scripts.lib.core.frontmatter_writer import (
  update_frontmatter_fields,
  update_frontmatter_status,
)
from supekku.scripts.lib.core.git import get_head_sha, short_sha
from supekku.scripts.lib.core.repo import find_repo_root
from supekku.scripts.lib.decisions.registry import DecisionRegistry
from supekku.scripts.lib.policies.registry import PolicyRegistry
from supekku.scripts.lib.requirements.registry import RequirementsRegistry
from supekku.scripts.lib.specs.registry import SpecRegistry
from supekku.scripts.lib.standards.registry import StandardRegistry

app = typer.Typer(help="Edit artifacts in editor", no_args_is_help=True)

StatusOption = Annotated[
  str | None,
  typer.Option("--status", "-s", help="Set status (skip editor)"),
]


def _apply_status(
  artifact_id: str,
  path: Path,
  entity_type: str,
  status: str,
) -> None:
  """Validate and apply a status update.

  Raises typer.Exit(EXIT_FAILURE) on validation or write failure.
  Returns normally on success.

  IMPORTANT: typer.Exit inherits from RuntimeError. Callers with
  ``except RuntimeError`` MUST guard with ``except typer.Exit: raise``
  first, or use an early ``return`` after this call.
  """
  if not status or not status.strip():
    typer.echo("Error: --status value must not be empty", err=True)
    raise typer.Exit(EXIT_FAILURE)

  try:
    validate_status_for_entity(entity_type, status)
  except ValueError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e

  if update_frontmatter_status(path, status):
    typer.echo(f"Updated {artifact_id} status to '{status}'")
    return

  typer.echo(f"Error: no status field found in {path}", err=True)
  raise typer.Exit(EXIT_FAILURE)


@app.command("spec")
def edit_spec(
  spec_id: Annotated[str, typer.Argument(help="Spec ID (e.g., SPEC-009, PROD-042)")],
  status: StatusOption = None,
  root: RootOption = None,
) -> None:
  """Edit specification in editor."""
  try:
    registry = SpecRegistry(root=root)
    spec = registry.get(spec_id)

    if not spec:
      typer.echo(f"Error: Specification not found: {spec_id}", err=True)
      raise typer.Exit(EXIT_FAILURE)

    if status is not None:
      _apply_status(spec_id, spec.path, "spec", status)
      return
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
  status: StatusOption = None,
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

    if status is not None:
      _apply_status(normalized_id, artifact.path, "delta", status)
      return
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
  status: StatusOption = None,
  root: RootOption = None,
) -> None:
  """Edit revision in editor."""
  try:
    ref = resolve_artifact("revision", revision_id, root)
    if status is not None:
      _apply_status(ref.id, ref.path, "revision", status)
      return
    open_in_editor(ref.path)
  except typer.Exit:
    raise
  except ArtifactNotFoundError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
  except RuntimeError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("requirement")
def edit_requirement(
  req_id: Annotated[str, typer.Argument(help="Requirement ID (e.g., SPEC-009.FR-001)")],
  status: StatusOption = None,
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

    if status is not None:
      _apply_status(req_id, path, "requirement", status)
      return
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
  status: StatusOption = None,
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

    if status is not None:
      _apply_status(normalized_id, decision.path, "adr", status)
      return
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
  status: StatusOption = None,
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

    if status is not None:
      _apply_status(normalized_id, policy.path, "policy", status)
      return
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
  status: StatusOption = None,
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

    if status is not None:
      _apply_status(normalized_id, standard.path, "standard", status)
      return
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
  status: StatusOption = None,
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
    path = Path(registry.resolve_path(card_id, anywhere=anywhere))

    if status is not None:
      _apply_status(card_id, path, "card", status)
      return
    open_in_editor(path)
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


@app.command("plan")
def edit_plan(
  plan_id: Annotated[str, typer.Argument(help="Plan ID (e.g., IP-041, 041)")],
  status: StatusOption = None,
  root: RootOption = None,
) -> None:
  """Edit implementation plan in editor."""
  try:
    ref = resolve_artifact("plan", plan_id, root)
    if status is not None:
      _apply_status(ref.id, ref.path, "plan", status)
      return
    open_in_editor(ref.path)
  except typer.Exit:
    raise
  except ArtifactNotFoundError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
  except RuntimeError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("audit")
def edit_audit(
  audit_id: Annotated[str, typer.Argument(help="Audit ID (e.g., AUD-001, 001)")],
  status: StatusOption = None,
  root: RootOption = None,
) -> None:
  """Edit audit in editor."""
  try:
    ref = resolve_artifact("audit", audit_id, root)
    if status is not None:
      _apply_status(ref.id, ref.path, "audit", status)
      return
    open_in_editor(ref.path)
  except typer.Exit:
    raise
  except ArtifactNotFoundError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
  except RuntimeError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("memory")
def edit_memory(
  memory_id: Annotated[
    str, typer.Argument(help="Memory ID (e.g., mem.pattern.cli.skinny)")
  ],
  status: StatusOption = None,
  verify: Annotated[
    bool,
    typer.Option("--verify", help="Attest memory accuracy at current HEAD"),
  ] = False,
  root: RootOption = None,
) -> None:
  """Edit memory record in editor."""
  try:
    if verify and status is not None:
      typer.echo("Error: --verify and --status are mutually exclusive", err=True)
      raise typer.Exit(EXIT_FAILURE)

    ref = resolve_artifact("memory", memory_id, root)

    if verify:
      _verify_memory(ref.id, ref.path)
      return

    if status is not None:
      _apply_status(ref.id, ref.path, "memory", status)
      return
    open_in_editor(ref.path)
  except typer.Exit:
    raise
  except ArtifactNotFoundError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
  except RuntimeError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


def _verify_memory(memory_id: str, path: Path) -> None:
  """Stamp verification SHA and dates on a memory artifact.

  Raises typer.Exit(EXIT_FAILURE) if git is unavailable.
  """
  sha = get_head_sha()
  if sha is None:
    typer.echo(
      "Error: cannot verify — git not available or not in a repository",
      err=True,
    )
    raise typer.Exit(EXIT_FAILURE)

  today = date_type.today().isoformat()
  update_frontmatter_fields(
    path,
    {
      "verified": f"'{today}'",
      "verified_sha": sha,
      "updated": f"'{today}'",
    },
  )
  typer.echo(f"Verified: {memory_id} at {short_sha(sha)}")


@app.command("issue")
def edit_issue(
  issue_id: Annotated[str, typer.Argument(help="Issue ID (e.g., ISSUE-001)")],
  status: StatusOption = None,
  root: RootOption = None,
) -> None:
  """Edit issue in editor."""
  try:
    ref = resolve_artifact("issue", issue_id, root)
    if status is not None:
      _apply_status(ref.id, ref.path, "issue", status)
      return
    open_in_editor(ref.path)
  except typer.Exit:
    raise
  except ArtifactNotFoundError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
  except RuntimeError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("problem")
def edit_problem(
  problem_id: Annotated[str, typer.Argument(help="Problem ID (e.g., PROB-001)")],
  status: StatusOption = None,
  root: RootOption = None,
) -> None:
  """Edit problem in editor."""
  try:
    ref = resolve_artifact("problem", problem_id, root)
    if status is not None:
      _apply_status(ref.id, ref.path, "problem", status)
      return
    open_in_editor(ref.path)
  except typer.Exit:
    raise
  except ArtifactNotFoundError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
  except RuntimeError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("improvement")
def edit_improvement(
  improvement_id: Annotated[
    str, typer.Argument(help="Improvement ID (e.g., IMPR-001)")
  ],
  status: StatusOption = None,
  root: RootOption = None,
) -> None:
  """Edit improvement in editor."""
  try:
    ref = resolve_artifact("improvement", improvement_id, root)
    if status is not None:
      _apply_status(ref.id, ref.path, "improvement", status)
      return
    open_in_editor(ref.path)
  except typer.Exit:
    raise
  except ArtifactNotFoundError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
  except RuntimeError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("risk")
def edit_risk(
  risk_id: Annotated[str, typer.Argument(help="Risk ID (e.g., RISK-001)")],
  status: StatusOption = None,
  root: RootOption = None,
) -> None:
  """Edit risk in editor."""
  try:
    ref = resolve_artifact("risk", risk_id, root)
    if status is not None:
      _apply_status(ref.id, ref.path, "risk", status)
      return
    open_in_editor(ref.path)
  except typer.Exit:
    raise
  except ArtifactNotFoundError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
  except RuntimeError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("drift")
def edit_drift(
  ledger_id: Annotated[str, typer.Argument(help="Drift ledger ID (e.g., DL-047)")],
  status: StatusOption = None,
  root: RootOption = None,
) -> None:
  """Edit drift ledger in editor."""
  try:
    ref = resolve_artifact("drift_ledger", ledger_id, root)
    if status is not None:
      _apply_status(ref.id, ref.path, "drift", status)
      return
    open_in_editor(ref.path)
  except typer.Exit:
    raise
  except ArtifactNotFoundError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
  except RuntimeError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


# For direct testing
if __name__ == "__main__":  # pragma: no cover
  app()
