"""View commands for rendering artifacts to stdout (or pager with -p)."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from supekku.cli.common import (
  EXIT_FAILURE,
  ArtifactNotFoundError,
  InferringGroup,
  PagerOption,
  RootOption,
  render_file,
  render_file_paged,
  resolve_artifact,
  resolve_by_id,
)

app = typer.Typer(
  help="View artifacts (rendered markdown; use -p for pager)",
  no_args_is_help=True,
  cls=InferringGroup,
)


def _view_artifact(
  artifact_type: str,
  raw_id: str,
  root: Path,
  *,
  pager: bool = False,
) -> None:
  """Resolve an artifact and render it to stdout or pager."""
  try:
    ref = resolve_artifact(artifact_type, raw_id, root)
    if pager:
      render_file_paged(ref.path)
    else:
      render_file(ref.path)
  except ArtifactNotFoundError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
  except RuntimeError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("spec")
def view_spec(
  spec_id: Annotated[str, typer.Argument(help="Spec ID (e.g., SPEC-009, PROD-042)")],
  pager: PagerOption = False,
  root: RootOption = None,
) -> None:
  """View specification."""
  _view_artifact("spec", spec_id, root, pager=pager)


@app.command("delta")
def view_delta(
  delta_id: Annotated[str, typer.Argument(help="Delta ID (e.g., DE-003 or 003)")],
  pager: PagerOption = False,
  root: RootOption = None,
) -> None:
  """View delta."""
  _view_artifact("delta", delta_id, root, pager=pager)


@app.command("revision")
def view_revision(
  revision_id: Annotated[str, typer.Argument(help="Revision ID (e.g., RE-001 or 001)")],
  pager: PagerOption = False,
  root: RootOption = None,
) -> None:
  """View revision."""
  _view_artifact("revision", revision_id, root, pager=pager)


@app.command("adr")
def view_adr(
  decision_id: Annotated[str, typer.Argument(help="Decision ID (e.g., ADR-001, 001)")],
  pager: PagerOption = False,
  root: RootOption = None,
) -> None:
  """View ADR."""
  _view_artifact("adr", decision_id, root, pager=pager)


@app.command("policy")
def view_policy(
  policy_id: Annotated[str, typer.Argument(help="Policy ID (e.g., POL-001 or 001)")],
  pager: PagerOption = False,
  root: RootOption = None,
) -> None:
  """View policy."""
  _view_artifact("policy", policy_id, root, pager=pager)


@app.command("standard")
def view_standard(
  standard_id: Annotated[str, typer.Argument(help="Standard ID (e.g., STD-001, 001)")],
  pager: PagerOption = False,
  root: RootOption = None,
) -> None:
  """View standard."""
  _view_artifact("standard", standard_id, root, pager=pager)


@app.command("plan")
def view_plan(
  plan_id: Annotated[str, typer.Argument(help="Plan ID (e.g., IP-041, 041)")],
  pager: PagerOption = False,
  root: RootOption = None,
) -> None:
  """View implementation plan."""
  _view_artifact("plan", plan_id, root, pager=pager)


@app.command("audit")
def view_audit(
  audit_id: Annotated[str, typer.Argument(help="Audit ID (e.g., AUD-001, 001)")],
  pager: PagerOption = False,
  root: RootOption = None,
) -> None:
  """View audit."""
  _view_artifact("audit", audit_id, root, pager=pager)


@app.command("memory")
def view_memory(
  memory_id: Annotated[
    str, typer.Argument(help="Memory ID (e.g., mem.pattern.cli.skinny)")
  ],
  pager: PagerOption = False,
  root: RootOption = None,
) -> None:
  """View memory record."""
  _view_artifact("memory", memory_id, root, pager=pager)


@app.command("drift")
def view_drift(
  ledger_id: Annotated[str, typer.Argument(help="Drift ledger ID (e.g., DL-047)")],
  pager: PagerOption = False,
  root: RootOption = None,
) -> None:
  """View drift ledger."""
  _view_artifact("drift_ledger", ledger_id, root, pager=pager)


@app.command("issue")
def view_issue(
  issue_id: Annotated[str, typer.Argument(help="Issue ID (e.g., ISSUE-001)")],
  pager: PagerOption = False,
  root: RootOption = None,
) -> None:
  """View issue."""
  _view_artifact("issue", issue_id, root, pager=pager)


@app.command("problem")
def view_problem(
  problem_id: Annotated[str, typer.Argument(help="Problem ID (e.g., PROB-001)")],
  pager: PagerOption = False,
  root: RootOption = None,
) -> None:
  """View problem."""
  _view_artifact("problem", problem_id, root, pager=pager)


@app.command("improvement")
def view_improvement(
  improvement_id: Annotated[
    str, typer.Argument(help="Improvement ID (e.g., IMPR-001)")
  ],
  pager: PagerOption = False,
  root: RootOption = None,
) -> None:
  """View improvement."""
  _view_artifact("improvement", improvement_id, root, pager=pager)


@app.command("risk")
def view_risk(
  risk_id: Annotated[str, typer.Argument(help="Risk ID (e.g., RISK-001)")],
  pager: PagerOption = False,
  root: RootOption = None,
) -> None:
  """View risk."""
  _view_artifact("risk", risk_id, root, pager=pager)


@app.command("requirement")
def view_requirement(
  req_id: Annotated[str, typer.Argument(help="Requirement ID (e.g., SPEC-009.FR-001)")],
  pager: PagerOption = False,
  root: RootOption = None,
) -> None:
  """View requirement's spec file."""
  _view_artifact("requirement", req_id, root, pager=pager)


@app.command("backlog")
def view_backlog(
  item_id: Annotated[str, typer.Argument(help="Backlog item ID (e.g., ISSUE-009)")],
  pager: PagerOption = False,
  root: RootOption = None,
) -> None:
  """View a backlog item (issue, problem, improvement, or risk)."""
  _view_artifact("backlog", item_id, root, pager=pager)


@app.command("card")
def view_card(
  card_id: Annotated[str, typer.Argument(help="Card ID (e.g., T123)")],
  anywhere: Annotated[
    bool,
    typer.Option(
      "--anywhere",
      "-a",
      help="Search entire repo instead of just kanban/",
    ),
  ] = False,
  pager: PagerOption = False,
  root: RootOption = None,
) -> None:
  """View card."""
  from supekku.scripts.lib.cards import CardRegistry  # noqa: PLC0415

  try:
    registry = CardRegistry(root=root)
    path = Path(registry.resolve_path(card_id, anywhere=anywhere))
    if pager:
      render_file_paged(path)
    else:
      render_file(path)
  except (RuntimeError, FileNotFoundError, ValueError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


# --- ID inference fallback ---


@app.command("inferred", hidden=True)
def view_inferred(
  ctx: typer.Context,
  pager: PagerOption = False,
  root: RootOption = None,
) -> None:
  """View an artifact by inferring its type from the ID."""
  from supekku.scripts.lib.core.repo import find_repo_root  # noqa: PLC0415

  raw_id = ctx.obj["inferred_id"]
  repo_root = find_repo_root(root)
  matches = resolve_by_id(raw_id, repo_root)

  if not matches:
    typer.echo(f"Error: no artifact found matching '{raw_id}'", err=True)
    raise typer.Exit(EXIT_FAILURE)

  if len(matches) > 1:
    typer.echo(f"Ambiguous ID '{raw_id}' matches:", err=True)
    for kind, ref in matches:
      typer.echo(f"  {ref.id} ({kind})", err=True)
    typer.echo("Specify the type: e.g. 'view delta ...'", err=True)
    raise typer.Exit(EXIT_FAILURE)

  _kind, ref = matches[0]
  try:
    if pager:
      render_file_paged(ref.path)
    else:
      render_file(ref.path)
  except RuntimeError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


# For direct testing
if __name__ == "__main__":  # pragma: no cover
  app()
