"""Workflow orchestration CLI commands.

Thin CLI layer for the workflow control plane (DR-102 §5).
Delegates to domain logic in ``supekku.scripts.lib.workflow``.

Commands:
  phase start  — initialise workflow/state.yaml (planned → implementing)
  workflow status — read and display human-readable workflow state
  block / unblock — transition to/from blocked
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from supekku.cli.common import EXIT_FAILURE, EXIT_SUCCESS, RootOption
from supekku.scripts.lib.core.repo import find_repo_root

# ---------------------------------------------------------------------------
# Typer groups
# ---------------------------------------------------------------------------

workflow_app = typer.Typer(help="Workflow orchestration commands", no_args_is_help=True)
phase_app = typer.Typer(help="Phase lifecycle commands", no_args_is_help=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _resolve_delta_dir(delta_id: str, root: Path) -> Path:
  """Locate a delta bundle directory by ID.

  Scans ``.spec-driver/deltas/`` for a directory whose name starts with
  the delta ID.  Returns the path to the bundle directory.

  Raises:
    typer.Exit: If the delta cannot be found.
  """
  from supekku.scripts.lib.core.paths import get_deltas_dir  # noqa: PLC0415

  deltas_dir = get_deltas_dir(root)
  if not deltas_dir.exists():
    typer.echo(f"Deltas directory not found: {deltas_dir}", err=True)
    raise typer.Exit(EXIT_FAILURE)

  prefix = delta_id.upper()
  for entry in sorted(deltas_dir.iterdir()):
    if entry.is_dir() and entry.name.upper().startswith(prefix):
      return entry

  typer.echo(f"Delta not found: {delta_id}", err=True)
  raise typer.Exit(EXIT_FAILURE)


def _find_plan_and_phase(
  delta_dir: Path,
) -> tuple[str | None, str | None, str | None, str | None]:
  """Discover plan ID, plan path, latest phase ID, and phase path in a delta bundle.

  Returns:
    (plan_id, plan_path_rel, phase_id, phase_path_rel) — any may be None.
  """
  import re  # noqa: PLC0415

  plan_id = None
  plan_path = None
  phase_id = None
  phase_path = None

  # Find IP-*.md in bundle root
  for f in sorted(delta_dir.glob("IP-*.md")):
    match = re.match(r"(IP-\d+)", f.name)
    if match:
      plan_id = match.group(1)
      plan_path = str(f)
      break

  # Find latest phase in phases/
  phases_dir = delta_dir / "phases"
  if phases_dir.is_dir():
    phase_files = sorted(phases_dir.glob("phase-*.md"))
    if phase_files:
      latest = phase_files[-1]
      # Phase ID is plan_id.PHASE-NN
      match = re.search(r"phase-(\d+)", latest.name)
      if match and plan_id:
        phase_num = int(match.group(1))
        phase_id = f"{plan_id}.PHASE-{phase_num:02d}"
        phase_path = str(latest)

  return plan_id, plan_path, phase_id, phase_path


def _load_workflow_config(root: Path) -> dict:
  """Load workflow.toml config, returning empty dict on failure."""
  try:
    from supekku.scripts.lib.core.config import load_workflow_config  # noqa: PLC0415
    return load_workflow_config(root)
  except Exception:  # noqa: BLE001
    return {}


# ---------------------------------------------------------------------------
# phase start
# ---------------------------------------------------------------------------


@phase_app.command("start")
def phase_start(
  delta: Annotated[str, typer.Argument(help="Delta ID (e.g. DE-103)")],
  phase: Annotated[
    str | None,
    typer.Option("--phase", help="Phase ID override (e.g. IP-103.PHASE-02)"),
  ] = None,
  root: RootOption = None,
) -> None:
  """Initialise workflow/state.yaml for a delta (planned → implementing)."""
  from supekku.scripts.lib.workflow.state_io import (  # noqa: PLC0415
    StateValidationError,
    init_state,
    read_state,
    state_path,
    write_state,
  )
  from supekku.scripts.lib.workflow.state_machine import (  # noqa: PLC0415
    TransitionCommand,
    TransitionError,
    WorkflowState,
    apply_transition,
  )

  repo_root = find_repo_root(root)
  delta_dir = _resolve_delta_dir(delta, repo_root)
  delta_id = delta.upper()

  # Check if state already exists
  sp = state_path(delta_dir)
  if sp.exists():
    # Re-read state to check if we need to transition or if already implementing
    try:
      existing = read_state(delta_dir)
    except Exception as exc:  # noqa: BLE001
      typer.echo(f"Error reading existing state: {exc}", err=True)
      raise typer.Exit(EXIT_FAILURE) from exc

    current_status = existing["workflow"]["status"]
    if current_status == WorkflowState.IMPLEMENTING.value:
      typer.echo(f"Already implementing: {delta_id}")
      raise typer.Exit(EXIT_SUCCESS)

    # Try transition from current state
    try:
      apply_transition(WorkflowState(current_status), TransitionCommand.PHASE_START)
    except TransitionError as exc:
      typer.echo(f"Cannot start phase: {exc}", err=True)
      raise typer.Exit(EXIT_FAILURE) from exc

  # Discover plan and phase
  plan_id, plan_path, auto_phase_id, phase_path = _find_plan_and_phase(delta_dir)
  effective_phase = phase or auto_phase_id

  if not effective_phase:
    typer.echo(
      "Cannot determine phase. Use --phase or ensure phases/ exists.",
      err=True,
    )
    raise typer.Exit(EXIT_FAILURE)

  # Compute relative paths from repo root
  artifact_path_rel = str(delta_dir.relative_to(repo_root))
  notes_path = delta_dir / "notes.md"
  notes_path_rel = (
    str(notes_path.relative_to(repo_root)) if notes_path.exists() else None
  )

  plan_path_rel = None
  if plan_path:
    plan_path_rel = str(Path(plan_path).relative_to(repo_root))

  phase_path_rel = None
  if phase_path:
    phase_path_rel = str(Path(phase_path).relative_to(repo_root))

  config = _load_workflow_config(repo_root)

  data = init_state(
    artifact_id=delta_id,
    artifact_kind="delta",
    phase_id=effective_phase,
    plan_id=plan_id,
    artifact_path=artifact_path_rel,
    notes_path=notes_path_rel,
    plan_path=plan_path_rel,
    phase_path=phase_path_rel,
    config=config,
  )

  try:
    written = write_state(delta_dir, data)
  except StateValidationError as exc:
    typer.echo(f"State validation failed: {exc}", err=True)
    raise typer.Exit(EXIT_FAILURE) from exc

  typer.echo(f"Phase started: {effective_phase}")
  typer.echo("  state: planned → implementing")
  typer.echo(f"  file: {written}")
  raise typer.Exit(EXIT_SUCCESS)


# ---------------------------------------------------------------------------
# workflow status
# ---------------------------------------------------------------------------


@workflow_app.command("status")
def workflow_status(
  delta: Annotated[str, typer.Argument(help="Delta ID (e.g. DE-103)")],
  root: RootOption = None,
) -> None:
  """Display human-readable workflow state for a delta."""
  from supekku.scripts.lib.workflow.state_io import (  # noqa: PLC0415
    StateNotFoundError,
    StateValidationError,
    read_state,
  )

  repo_root = find_repo_root(root)
  delta_dir = _resolve_delta_dir(delta, repo_root)

  try:
    data = read_state(delta_dir)
  except StateNotFoundError as exc:
    typer.echo(
      f"No workflow state for {delta.upper()} "
      "(workflow/state.yaml not found)",
    )
    raise typer.Exit(EXIT_SUCCESS) from exc
  except StateValidationError as exc:
    typer.echo(f"Invalid workflow state: {exc}", err=True)
    raise typer.Exit(EXIT_FAILURE) from exc

  _render_status(data)
  raise typer.Exit(EXIT_SUCCESS)


def _render_status(data: dict) -> None:
  """Render workflow state as human-readable output."""
  artifact = data.get("artifact", {})
  phase = data.get("phase", {})
  wf = data.get("workflow", {})
  ts = data.get("timestamps", {})

  status = wf.get("status", "unknown")
  active_role = wf.get("active_role", "unknown")
  next_role = wf.get("next_role")
  claimed_by = wf.get("claimed_by")
  previous_state = wf.get("previous_state")

  typer.echo(f"Workflow: {artifact.get('id', '?')} ({artifact.get('kind', '?')})")
  typer.echo(f"  status: {status}")
  typer.echo(f"  active_role: {active_role}")

  if status == "awaiting_handoff" and next_role:
    typer.echo(f"  → handoff to: {next_role}")
  elif next_role:
    typer.echo(f"  next_role: {next_role}")

  if claimed_by:
    typer.echo(f"  claimed_by: {claimed_by}")

  if status == "blocked" and previous_state:
    typer.echo(f"  previous_state: {previous_state}")

  typer.echo(f"  phase: {phase.get('id', '?')} ({phase.get('status', '?')})")

  plan = data.get("plan")
  if plan:
    typer.echo(f"  plan: {plan.get('id', '?')}")

  typer.echo(f"  updated: {ts.get('updated', '?')}")


# ---------------------------------------------------------------------------
# block / unblock
# ---------------------------------------------------------------------------


@workflow_app.command("block")
def block_command(
  delta: Annotated[str, typer.Argument(help="Delta ID (e.g. DE-103)")],
  reason: Annotated[
    str | None,
    typer.Option("--reason", "-r", help="Reason for blocking"),
  ] = None,
  root: RootOption = None,
) -> None:
  """Block a delta's workflow."""
  from supekku.scripts.lib.workflow.state_io import (  # noqa: PLC0415
    StateNotFoundError,
    StateValidationError,
    read_state,
    update_state_workflow,
    write_state,
  )
  from supekku.scripts.lib.workflow.state_machine import (  # noqa: PLC0415
    TransitionCommand,
    TransitionError,
    apply_transition,
  )

  repo_root = find_repo_root(root)
  delta_dir = _resolve_delta_dir(delta, repo_root)

  try:
    data = read_state(delta_dir)
  except StateNotFoundError as exc:
    typer.echo(f"No workflow state for {delta.upper()}", err=True)
    raise typer.Exit(EXIT_FAILURE) from exc
  except StateValidationError as exc:
    typer.echo(f"Invalid workflow state: {exc}", err=True)
    raise typer.Exit(EXIT_FAILURE) from exc

  from supekku.scripts.lib.workflow.state_machine import WorkflowState  # noqa: PLC0415

  current = WorkflowState(data["workflow"]["status"])

  try:
    result = apply_transition(current, TransitionCommand.BLOCK)
  except TransitionError as exc:
    typer.echo(f"Cannot block: {exc}", err=True)
    raise typer.Exit(EXIT_FAILURE) from exc

  update_state_workflow(
    data,
    status=result.new_state.value,
    previous_state=result.previous_state.value,
  )

  try:
    write_state(delta_dir, data)
  except StateValidationError as exc:
    typer.echo(f"State validation failed: {exc}", err=True)
    raise typer.Exit(EXIT_FAILURE) from exc

  typer.echo(f"Blocked: {delta.upper()} ({current.value} → blocked)")
  if reason:
    typer.echo(f"  reason: {reason}")
  raise typer.Exit(EXIT_SUCCESS)


@workflow_app.command("unblock")
def unblock_command(
  delta: Annotated[str, typer.Argument(help="Delta ID (e.g. DE-103)")],
  root: RootOption = None,
) -> None:
  """Unblock a delta's workflow, restoring previous state."""
  from supekku.scripts.lib.workflow.state_io import (  # noqa: PLC0415
    StateNotFoundError,
    StateValidationError,
    read_state,
    update_state_workflow,
    write_state,
  )
  from supekku.scripts.lib.workflow.state_machine import (  # noqa: PLC0415
    TransitionCommand,
    TransitionError,
    WorkflowState,
    apply_transition,
  )

  repo_root = find_repo_root(root)
  delta_dir = _resolve_delta_dir(delta, repo_root)

  try:
    data = read_state(delta_dir)
  except StateNotFoundError as exc:
    typer.echo(f"No workflow state for {delta.upper()}", err=True)
    raise typer.Exit(EXIT_FAILURE) from exc
  except StateValidationError as exc:
    typer.echo(f"Invalid workflow state: {exc}", err=True)
    raise typer.Exit(EXIT_FAILURE) from exc

  current = WorkflowState(data["workflow"]["status"])
  saved_previous = data["workflow"].get("previous_state")

  if not saved_previous:
    typer.echo("Cannot unblock: no previous state saved in state.yaml", err=True)
    raise typer.Exit(EXIT_FAILURE)

  try:
    result = apply_transition(
      current,
      TransitionCommand.UNBLOCK,
      previous_state=WorkflowState(saved_previous),
    )
  except TransitionError as exc:
    typer.echo(f"Cannot unblock: {exc}", err=True)
    raise typer.Exit(EXIT_FAILURE) from exc

  update_state_workflow(
    data,
    status=result.new_state.value,
    previous_state=None,  # Clear saved previous state
  )

  try:
    write_state(delta_dir, data)
  except StateValidationError as exc:
    typer.echo(f"State validation failed: {exc}", err=True)
    raise typer.Exit(EXIT_FAILURE) from exc

  typer.echo(f"Unblocked: {delta.upper()} (blocked → {result.new_state.value})")
  raise typer.Exit(EXIT_SUCCESS)
