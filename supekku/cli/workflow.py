"""Workflow orchestration CLI commands.

Thin CLI layer for the workflow control plane (DR-102 §5).
Delegates to domain logic in ``supekku.scripts.lib.workflow``.

Commands:
  phase start  — initialise workflow/state.yaml (planned → implementing)
  workflow status — read and display human-readable workflow state
  block / unblock — transition to/from blocked
  create handoff — write handoff.current.yaml, transition to awaiting_handoff
  accept handoff — claim + transition to implementing/reviewing
  review prime — generate review-index.yaml + review-bootstrap.md
  review complete — write review-findings.yaml, transition state
  review teardown — delete reviewer state files
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from supekku.cli.common import (
  EXIT_FAILURE,
  EXIT_GUARD_VIOLATION,
  EXIT_PRECONDITION,
  EXIT_SUCCESS,
  RootOption,
  cli_json_error,
  cli_json_success,
  emit_json_and_exit,
)
from supekku.scripts.lib.core.repo import find_repo_root

# ---------------------------------------------------------------------------
# Typer groups
# ---------------------------------------------------------------------------

workflow_app = typer.Typer(help="Workflow orchestration commands", no_args_is_help=True)
phase_app = typer.Typer(help="Phase lifecycle commands", no_args_is_help=True)
accept_app = typer.Typer(help="Accept workflow artifacts", no_args_is_help=True)


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

  # Update phase frontmatter (normative) before state.yaml (transient) — DEC-104-08
  if phase_path:
    from supekku.scripts.lib.changes.lifecycle import (  # noqa: PLC0415
      STATUS_IN_PROGRESS,
    )
    from supekku.scripts.lib.core.frontmatter_writer import (  # noqa: PLC0415
      update_frontmatter_status,
    )

    abs_phase = Path(phase_path)
    if abs_phase.exists():
      update_frontmatter_status(abs_phase, STATUS_IN_PROGRESS)

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
  format_type: Annotated[
    str,
    typer.Option("--format", help="Output format: table or json"),
  ] = "table",
  root: RootOption = None,
) -> None:
  """Display workflow state for a delta."""
  from supekku.scripts.lib.workflow.state_io import (  # noqa: PLC0415
    StateNotFoundError,
    StateValidationError,
    read_state,
  )

  json_mode = format_type == "json"
  cmd = "workflow.status"

  repo_root = find_repo_root(root)
  delta_dir = _resolve_delta_dir(delta, repo_root)
  delta_id = delta.upper()

  try:
    data = read_state(delta_dir)
  except StateNotFoundError as exc:
    msg = f"No workflow state for {delta_id}"
    if json_mode:
      emit_json_and_exit(cli_json_error(cmd, EXIT_PRECONDITION, "precondition", msg))
    typer.echo(f"{msg} (workflow/state.yaml not found)")
    raise typer.Exit(EXIT_SUCCESS) from exc
  except StateValidationError as exc:
    msg = f"Invalid workflow state: {exc}"
    if json_mode:
      emit_json_and_exit(cli_json_error(cmd, EXIT_PRECONDITION, "precondition", msg))
    typer.echo(msg, err=True)
    raise typer.Exit(EXIT_FAILURE) from exc

  if json_mode:
    payload = _build_status_json(data, delta_dir, delta_id, repo_root)
    emit_json_and_exit(cli_json_success(cmd, payload))

  _render_status(data)
  raise typer.Exit(EXIT_SUCCESS)


def _build_status_json(
  data: dict,
  delta_dir: Path,
  delta_id: str,
  repo_root: Path,
) -> dict:
  """Build JSON payload for workflow status (DE-108 §6.4)."""
  from supekku.scripts.lib.core.git import get_head_sha  # noqa: PLC0415
  from supekku.scripts.lib.workflow.review_io import (  # noqa: PLC0415
    FindingsNotFoundError,
    FindingsVersionError,
    ReviewIndexNotFoundError,
    ReviewIndexValidationError,
    read_findings,
    read_review_index,
  )
  from supekku.scripts.lib.workflow.review_state_machine import (  # noqa: PLC0415
    BootstrapStatus,
  )
  from supekku.scripts.lib.workflow.staleness import evaluate_staleness  # noqa: PLC0415

  wf = data.get("workflow", {})
  phase = data.get("phase", {})

  payload: dict = {
    "delta_id": delta_id,
    "workflow_status": wf.get("status", "unknown"),
    "active_role": wf.get("active_role", "unknown"),
  }

  # Review state — bootstrap + judgment + findings summary + staleness
  bootstrap_status = BootstrapStatus.COLD.value
  judgment_status = "not_started"
  review_round = 0
  findings_summary = {"blocking": 0, "non_blocking": 0, "resolved": 0, "waived": 0}
  staleness: dict = {
    "phase_id": phase.get("id", "unknown"),
    "head": "unknown",
    "triggers": [],
  }

  try:
    index = read_review_index(delta_dir)
    bootstrap_status = index.get("review", {}).get(
      "bootstrap_status",
      BootstrapStatus.WARM.value,
    )
    judgment_status = index.get("review", {}).get("judgment_status", "not_started")

    # Staleness inputs
    cache_key = index.get("staleness", {}).get("cache_key", {})
    head_sha = get_head_sha(repo_root) or "unknown"
    staleness = {
      "phase_id": cache_key.get("phase_id", "unknown"),
      "head": cache_key.get("head", "unknown"),
      "triggers": [],
    }
    # Evaluate staleness triggers
    result = evaluate_staleness(
      index,
      current_phase_id=phase.get("id", "unknown"),
      current_head=head_sha,
    )
    staleness["triggers"] = result.triggers

  except (ReviewIndexNotFoundError, ReviewIndexValidationError):
    pass  # No review index — cold state

  try:
    findings = read_findings(delta_dir)
    review_round = findings.get("review", {}).get("current_round", 0)
    for round_data in findings.get("rounds", []):
      findings_summary["blocking"] += len(round_data.get("blocking", []))
      findings_summary["non_blocking"] += len(round_data.get("non_blocking", []))
      for finding in round_data.get("blocking", []) + round_data.get(
        "non_blocking", []
      ):
        s = finding.get("status", "open")
        if s == "resolved":
          findings_summary["resolved"] += 1
        elif s == "waived":
          findings_summary["waived"] += 1
  except (FindingsNotFoundError, FindingsVersionError):
    pass  # No findings

  payload["bootstrap_status"] = bootstrap_status
  payload["judgment_status"] = judgment_status
  payload["round"] = review_round
  payload["findings_summary"] = findings_summary
  payload["staleness"] = staleness

  return payload


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


# ---------------------------------------------------------------------------
# create handoff
# ---------------------------------------------------------------------------


def create_handoff_command(
  delta: Annotated[str, typer.Argument(help="Delta ID (e.g. DE-103)")],
  to_role: Annotated[
    str,
    typer.Option("--to", help="Target role"),
  ],
  next_kind: Annotated[
    str,
    typer.Option(
      "--next-kind",
      help="Next activity kind",
    ),
  ] = "",
  next_summary: Annotated[
    str | None,
    typer.Option("--next-summary", help="Summary of next activity"),
  ] = None,
  root: RootOption = None,
) -> None:
  """Create a structured handoff, transitioning to awaiting_handoff."""
  from supekku.scripts.lib.core.git import (  # noqa: PLC0415
    get_branch,
    get_head_sha,
    has_staged_changes,
    has_uncommitted_changes,
    short_sha,
  )
  from supekku.scripts.lib.workflow.handoff_io import (  # noqa: PLC0415
    HandoffValidationError,
    build_handoff,
    write_handoff,
  )
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
  delta_id = delta.upper()

  # Read current state
  try:
    state_data = read_state(delta_dir)
  except StateNotFoundError as exc:
    typer.echo(f"No workflow state for {delta_id}", err=True)
    raise typer.Exit(EXIT_FAILURE) from exc
  except StateValidationError as exc:
    typer.echo(f"Invalid workflow state: {exc}", err=True)
    raise typer.Exit(EXIT_FAILURE) from exc

  # Validate transition
  current = WorkflowState(state_data["workflow"]["status"])
  try:
    apply_transition(current, TransitionCommand.CREATE_HANDOFF)
  except TransitionError as exc:
    typer.echo(f"Cannot create handoff: {exc}", err=True)
    raise typer.Exit(EXIT_FAILURE) from exc

  # Infer next_activity_kind if not provided
  activity_kind = next_kind or ("review" if to_role == "reviewer" else "implementation")

  # Assemble required_reading from delta bundle
  artifact = state_data.get("artifact", {})
  phase = state_data.get("phase", {})
  plan = state_data.get("plan", {})

  required_reading: list[str] = []
  if artifact.get("path"):
    # Add DE-*.md
    delta_path = artifact["path"]
    delta_md = f"{delta_path}/{delta_id}.md"
    required_reading.append(delta_md)
  if plan.get("path"):
    required_reading.append(plan["path"])
  if phase.get("path"):
    required_reading.append(phase["path"])
  if artifact.get("notes_path"):
    required_reading.append(artifact["notes_path"])

  if not required_reading:
    # Fallback — at least one entry required
    required_reading.append(f"{delta_id}")

  # Git state
  head_sha = get_head_sha(repo_root)
  git_head = short_sha(head_sha) if head_sha else None
  git_branch = get_branch(repo_root)
  uncommitted = has_uncommitted_changes(repo_root)
  staged = has_staged_changes(repo_root)

  config = _load_workflow_config(repo_root)
  boundary = config.get("workflow", {}).get(
    "handoff_boundary",
    "phase",
  )

  handoff_data = build_handoff(
    artifact_id=delta_id,
    artifact_kind=artifact.get("kind", "delta"),
    from_role=state_data["workflow"]["active_role"],
    to_role=to_role,
    phase_id=phase.get("id", "unknown"),
    phase_status=phase.get("status"),
    required_reading=required_reading,
    boundary=boundary,
    next_activity_kind=activity_kind,
    next_activity_summary=next_summary,
    git_head=git_head,
    git_branch=git_branch,
    has_uncommitted=uncommitted,
    has_staged=staged,
  )

  # Write order per DR-102 §5: 1. handoff, 2. state
  try:
    handoff_path = write_handoff(delta_dir, handoff_data)
  except HandoffValidationError as exc:
    typer.echo(f"Handoff validation failed: {exc}", err=True)
    raise typer.Exit(EXIT_FAILURE) from exc

  # Update state: transition + clear claimed_by
  update_state_workflow(
    state_data,
    status=WorkflowState.AWAITING_HANDOFF.value,
    next_role=to_role,
    claimed_by=None,  # New handoff resets claim (DR-102 §4)
  )

  try:
    write_state(delta_dir, state_data)
  except StateValidationError as exc:
    typer.echo(f"State update failed: {exc}", err=True)
    raise typer.Exit(EXIT_FAILURE) from exc

  typer.echo(
    f"Handoff created: {delta_id} → {to_role} ({current.value} → awaiting_handoff)",
  )
  typer.echo(f"  file: {handoff_path}")
  raise typer.Exit(EXIT_SUCCESS)


# ---------------------------------------------------------------------------
# accept handoff
# ---------------------------------------------------------------------------


@accept_app.command("handoff")
def accept_handoff_command(
  delta: Annotated[
    str,
    typer.Argument(help="Delta ID (e.g. DE-103)"),
  ],
  identity: Annotated[
    str | None,
    typer.Option(
      "--identity",
      help="Claiming identity (defaults to $USER)",
    ),
  ] = None,
  root: RootOption = None,
) -> None:
  """Accept a pending handoff, claiming it with identity guard."""
  import os as _os  # noqa: PLC0415

  from supekku.scripts.lib.workflow.handoff_io import (  # noqa: PLC0415
    HandoffNotFoundError,
    HandoffValidationError,
    read_handoff,
    write_handoff,
  )
  from supekku.scripts.lib.workflow.state_io import (  # noqa: PLC0415
    StateNotFoundError,
    StateValidationError,
    read_state,
    update_state_workflow,
    write_state,
  )
  from supekku.scripts.lib.workflow.state_machine import (  # noqa: PLC0415
    ClaimError,
    TransitionCommand,
    TransitionError,
    WorkflowState,
    apply_transition,
    check_claim,
  )

  repo_root = find_repo_root(root)
  delta_dir = _resolve_delta_dir(delta, repo_root)
  delta_id = delta.upper()
  caller = identity or _os.environ.get("USER", "unknown")

  # Read state
  try:
    state_data = read_state(delta_dir)
  except StateNotFoundError as exc:
    typer.echo(f"No workflow state for {delta_id}", err=True)
    raise typer.Exit(EXIT_FAILURE) from exc
  except StateValidationError as exc:
    typer.echo(f"Invalid workflow state: {exc}", err=True)
    raise typer.Exit(EXIT_FAILURE) from exc

  # Read handoff
  try:
    handoff_data = read_handoff(delta_dir)
  except HandoffNotFoundError as exc:
    typer.echo(f"No pending handoff for {delta_id}", err=True)
    raise typer.Exit(EXIT_FAILURE) from exc
  except HandoffValidationError as exc:
    typer.echo(f"Invalid handoff: {exc}", err=True)
    raise typer.Exit(EXIT_FAILURE) from exc

  # Check claim guard
  current_claimant = state_data["workflow"].get("claimed_by")
  try:
    check_claim(current_claimant, caller)
  except ClaimError as exc:
    typer.echo(f"Claim guard: {exc}", err=True)
    raise typer.Exit(EXIT_FAILURE) from exc

  # Idempotent: if already claimed by same identity, no-op
  if current_claimant == caller:
    typer.echo(f"Already claimed by {caller}: {delta_id}")
    raise typer.Exit(EXIT_SUCCESS)

  # Determine to_role from handoff
  to_role = handoff_data["transition"]["to_role"]

  # Validate transition
  current = WorkflowState(state_data["workflow"]["status"])
  try:
    result = apply_transition(
      current,
      TransitionCommand.ACCEPT_HANDOFF,
      to_role=to_role,
    )
  except TransitionError as exc:
    typer.echo(f"Cannot accept handoff: {exc}", err=True)
    raise typer.Exit(EXIT_FAILURE) from exc

  # Update state: transition + set claimed_by + set active_role
  update_state_workflow(
    state_data,
    status=result.new_state.value,
    active_role=to_role,
    claimed_by=caller,
    next_role=None,
  )
  # Clear next_role from workflow dict
  state_data["workflow"].pop("next_role", None)

  try:
    write_state(delta_dir, state_data)
  except StateValidationError as exc:
    typer.echo(f"State update failed: {exc}", err=True)
    raise typer.Exit(EXIT_FAILURE) from exc

  # Mark handoff as accepted (non-critical — state is authoritative)
  import contextlib  # noqa: PLC0415

  handoff_data["transition"]["status"] = "accepted"
  with contextlib.suppress(HandoffValidationError):
    write_handoff(delta_dir, handoff_data)

  typer.echo(
    f"Handoff accepted: {delta_id} → {to_role} (claimed by {caller})",
  )
  raise typer.Exit(EXIT_SUCCESS)


# ---------------------------------------------------------------------------
# review commands
# ---------------------------------------------------------------------------

review_app = typer.Typer(help="Review lifecycle commands", no_args_is_help=True)


@review_app.command("prime")
def review_prime_command(
  delta: Annotated[str, typer.Argument(help="Delta ID (e.g. DE-103)")],
  format_type: Annotated[
    str,
    typer.Option("--format", help="Output format: table or json"),
  ] = "table",
  root: RootOption = None,
) -> None:
  """Generate review-index.yaml + review-bootstrap.md from current state.

  Evaluates staleness of existing cache, rebuilds or incrementally
  updates as appropriate per DR-102 §8.
  """
  from spec_driver.orchestration.operations import (  # noqa: PLC0415
    prime_review,
  )
  from supekku.scripts.lib.workflow.review_state_machine import (  # noqa: PLC0415
    BootstrapStatus,
  )
  from supekku.scripts.lib.workflow.state_io import (  # noqa: PLC0415
    StateNotFoundError,
    StateValidationError,
  )

  json_mode = format_type == "json"
  cmd = "review.prime"

  repo_root = find_repo_root(root)
  delta_dir = _resolve_delta_dir(delta, repo_root)
  delta_id = delta.upper()

  try:
    result = prime_review(delta_dir, repo_root)
  except StateNotFoundError as exc:
    msg = f"No workflow state for {delta_id}"
    if json_mode:
      emit_json_and_exit(cli_json_error(cmd, EXIT_PRECONDITION, "precondition", msg))
    typer.echo(msg, err=True)
    raise typer.Exit(EXIT_FAILURE) from exc
  except StateValidationError as exc:
    msg = f"Invalid workflow state: {exc}"
    if json_mode:
      emit_json_and_exit(cli_json_error(cmd, EXIT_PRECONDITION, "precondition", msg))
    typer.echo(msg, err=True)
    raise typer.Exit(EXIT_FAILURE) from exc

  if json_mode:
    emit_json_and_exit(
      cli_json_success(
        cmd,
        {
          "delta_id": result.delta_id,
          "action": result.action.value,
          "bootstrap_status": BootstrapStatus.WARM.value,
          "judgment_status": result.judgment_status.value,
          "review_round": result.review_round,
          "index_path": str(result.index_path.relative_to(repo_root)),
          "bootstrap_path": str(result.bootstrap_path.relative_to(repo_root)),
        },
      )
    )

  typer.echo(f"Review primed: {result.delta_id} ({result.action.value})")
  typer.echo(f"  index: {result.index_path}")
  typer.echo(f"  bootstrap: {result.bootstrap_path}")
  raise typer.Exit(EXIT_SUCCESS)


# ---------------------------------------------------------------------------
# review complete
# ---------------------------------------------------------------------------


@review_app.command("complete")
def review_complete_command(
  delta: Annotated[str, typer.Argument(help="Delta ID (e.g. DE-103)")],
  status: Annotated[
    str,
    typer.Option(
      "--status",
      "-s",
      help="Review outcome: changes_requested or approved",
    ),
  ],
  summary: Annotated[
    str | None,
    typer.Option("--summary", help="Round summary"),
  ] = None,
  format_type: Annotated[
    str,
    typer.Option("--format", help="Output format: table or json"),
  ] = "table",
  root: RootOption = None,
) -> None:
  """Complete a review round, writing findings and transitioning state."""
  from spec_driver.orchestration.operations import (  # noqa: PLC0415
    ReviewApprovalGuardError,
    complete_review,
  )
  from supekku.scripts.lib.workflow.review_io import (  # noqa: PLC0415
    FindingsVersionError,
  )
  from supekku.scripts.lib.workflow.review_state_machine import (  # noqa: PLC0415
    ReviewStatus,
  )
  from supekku.scripts.lib.workflow.state_io import (  # noqa: PLC0415
    StateNotFoundError,
    StateValidationError,
  )
  from supekku.scripts.lib.workflow.state_machine import (  # noqa: PLC0415
    TransitionError,
  )

  json_mode = format_type == "json"
  cmd = "review.complete"

  if status not in ("changes_requested", "approved"):
    msg = f"Invalid status: {status} (must be 'changes_requested' or 'approved')"
    if json_mode:
      emit_json_and_exit(cli_json_error(cmd, EXIT_PRECONDITION, "precondition", msg))
    typer.echo(msg, err=True)
    raise typer.Exit(EXIT_FAILURE)

  repo_root = find_repo_root(root)
  delta_dir = _resolve_delta_dir(delta, repo_root)
  delta_id = delta.upper()

  review_status = ReviewStatus(status)

  try:
    result = complete_review(
      delta_dir,
      repo_root,
      status=review_status,
      summary=summary,
    )
  except StateNotFoundError as exc:
    msg = f"No workflow state for {delta_id}"
    if json_mode:
      emit_json_and_exit(cli_json_error(cmd, EXIT_PRECONDITION, "precondition", msg))
    typer.echo(msg, err=True)
    raise typer.Exit(EXIT_FAILURE) from exc
  except StateValidationError as exc:
    msg = f"Invalid workflow state: {exc}"
    if json_mode:
      emit_json_and_exit(cli_json_error(cmd, EXIT_PRECONDITION, "precondition", msg))
    typer.echo(msg, err=True)
    raise typer.Exit(EXIT_FAILURE) from exc
  except TransitionError as exc:
    msg = f"Cannot complete review: {exc}"
    if json_mode:
      emit_json_and_exit(cli_json_error(cmd, EXIT_PRECONDITION, "precondition", msg))
    typer.echo(msg, err=True)
    raise typer.Exit(EXIT_FAILURE) from exc
  except ReviewApprovalGuardError as exc:
    msg = str(exc)
    if json_mode:
      emit_json_and_exit(
        cli_json_error(cmd, EXIT_GUARD_VIOLATION, "guard_violation", msg),
      )
    typer.echo("Cannot approve: blocking findings remain:", err=True)
    for reason in exc.reasons:
      typer.echo(f"  - {reason}", err=True)
    raise typer.Exit(EXIT_FAILURE) from exc
  except FindingsVersionError as exc:
    msg = str(exc)
    if json_mode:
      emit_json_and_exit(cli_json_error(cmd, EXIT_PRECONDITION, "precondition", msg))
    typer.echo(msg, err=True)
    raise typer.Exit(EXIT_FAILURE) from exc

  if json_mode:
    emit_json_and_exit(
      cli_json_success(
        cmd,
        {
          "delta_id": result.delta_id,
          "round": result.round_number,
          "outcome": result.outcome.value,
          "previous_state": result.previous_state.value,
          "new_state": result.new_state.value,
          "findings_path": str(result.findings_path.relative_to(repo_root)),
          "teardown": result.teardown_performed,
        },
      )
    )

  typer.echo(
    f"Review complete: {result.delta_id} round {result.round_number} "
    f"→ {result.outcome.value} "
    f"({result.previous_state.value} → {result.new_state.value})",
  )
  typer.echo(f"  findings: {result.findings_path}")

  if result.teardown_performed:
    if result.removed_files:
      typer.echo(
        f"Teardown: {result.delta_id} — deleted {', '.join(result.removed_files)}",
      )
    else:
      typer.echo(
        f"Teardown: {result.delta_id} — no reviewer state to delete",
      )

  raise typer.Exit(EXIT_SUCCESS)


# ---------------------------------------------------------------------------
# review teardown
# ---------------------------------------------------------------------------


@review_app.command("teardown")
def review_teardown_command(
  delta: Annotated[str, typer.Argument(help="Delta ID (e.g. DE-103)")],
  format_type: Annotated[
    str,
    typer.Option("--format", help="Output format: table or json"),
  ] = "table",
  root: RootOption = None,
) -> None:
  """Delete reviewer state files (review-index, findings, bootstrap)."""
  from spec_driver.orchestration.operations import (  # noqa: PLC0415
    teardown_review,
  )

  json_mode = format_type == "json"
  cmd = "review.teardown"

  repo_root = find_repo_root(root)
  delta_dir = _resolve_delta_dir(delta, repo_root)
  delta_id = delta.upper()

  result = teardown_review(delta_dir)

  if not json_mode:
    if result.removed:
      typer.echo(
        f"Teardown: {delta_id} — deleted {', '.join(result.removed)}",
      )
    else:
      typer.echo(f"Teardown: {delta_id} — no reviewer state to delete")

  if json_mode:
    emit_json_and_exit(
      cli_json_success(
        cmd,
        {
          "delta_id": delta_id,
          "removed": result.removed,
        },
      )
    )

  raise typer.Exit(EXIT_SUCCESS)


# ---------------------------------------------------------------------------
# review finding — disposition subcommands (DR-109 §4.1)
# ---------------------------------------------------------------------------

finding_app = typer.Typer(
  help="Disposition review findings",
  no_args_is_help=True,
)
review_app.add_typer(finding_app, name="finding")


def _cli_disposition_finding(
  delta: str,
  finding_id: str,
  *,
  action: str,
  root: Path | None,
  json_mode: bool = False,
  authority: str | None = None,
  rationale: str | None = None,
  backlog_ref: str | None = None,
  resolved_at: str | None = None,
  superseded_by: str | None = None,
) -> None:
  """Thin CLI wrapper for disposition_finding operation."""
  from spec_driver.orchestration.operations import (  # noqa: PLC0415
    DispositionValidationError,
    FindingNotFoundError,
    disposition_finding,
  )
  from supekku.scripts.lib.workflow.review_io import (  # noqa: PLC0415
    FindingsNotFoundError,
    FindingsVersionError,
  )
  from supekku.scripts.lib.workflow.review_state_machine import (  # noqa: PLC0415
    DispositionAuthority,
    FindingDispositionAction,
  )

  cmd = f"review.finding.{action}"
  repo_root = find_repo_root(root)
  delta_dir = _resolve_delta_dir(delta, repo_root)
  delta_id = delta.upper()

  disp_action = FindingDispositionAction(action)
  disp_authority = (
    DispositionAuthority(authority) if authority else DispositionAuthority.AGENT
  )

  try:
    result = disposition_finding(
      delta_dir,
      finding_id,
      action=disp_action,
      authority=disp_authority,
      rationale=rationale,
      backlog_ref=backlog_ref,
      resolved_at=resolved_at,
      superseded_by=superseded_by,
    )
  except FindingsNotFoundError as exc:
    msg = f"No findings for {delta_id}"
    if json_mode:
      emit_json_and_exit(cli_json_error(cmd, EXIT_PRECONDITION, "precondition", msg))
    typer.echo(msg, err=True)
    raise typer.Exit(EXIT_FAILURE) from exc
  except FindingsVersionError as exc:
    msg = str(exc)
    if json_mode:
      emit_json_and_exit(cli_json_error(cmd, EXIT_PRECONDITION, "precondition", msg))
    typer.echo(msg, err=True)
    raise typer.Exit(EXIT_FAILURE) from exc
  except FindingNotFoundError as exc:
    msg = str(exc)
    if json_mode:
      emit_json_and_exit(cli_json_error(cmd, EXIT_PRECONDITION, "precondition", msg))
    typer.echo(msg, err=True)
    raise typer.Exit(EXIT_FAILURE) from exc
  except DispositionValidationError as exc:
    msg = str(exc)
    if json_mode:
      emit_json_and_exit(cli_json_error(cmd, EXIT_PRECONDITION, "validation", msg))
    typer.echo(msg, err=True)
    raise typer.Exit(EXIT_FAILURE) from exc

  if json_mode:
    emit_json_and_exit(
      cli_json_success(
        cmd,
        {
          "delta_id": result.delta_id,
          "finding_id": result.finding_id,
          "action": result.action.value,
          "previous_status": result.previous_status.value,
          "new_status": result.new_status.value,
        },
      )
    )

  typer.echo(
    f"Finding {finding_id}: {action} (delta {delta_id})",
  )
  raise typer.Exit(EXIT_SUCCESS)


@finding_app.command("resolve")
def finding_resolve_command(
  delta: Annotated[str, typer.Argument(help="Delta ID (e.g. DE-103)")],
  finding_id: Annotated[str, typer.Argument(help="Finding ID (e.g. R1-001)")],
  resolved_at: Annotated[
    str | None,
    typer.Option("--resolved-at", help="Commit SHA where fix landed"),
  ] = None,
  format_type: Annotated[
    str,
    typer.Option("--format", help="Output format: table or json"),
  ] = "table",
  root: RootOption = None,
) -> None:
  """Mark a finding as resolved (fixed)."""
  _cli_disposition_finding(
    delta,
    finding_id,
    action="fix",
    root=root,
    json_mode=format_type == "json",
    resolved_at=resolved_at,
  )


@finding_app.command("defer")
def finding_defer_command(
  delta: Annotated[str, typer.Argument(help="Delta ID (e.g. DE-103)")],
  finding_id: Annotated[str, typer.Argument(help="Finding ID (e.g. R1-001)")],
  rationale: Annotated[
    str,
    typer.Option("--rationale", help="Why this finding is deferred"),
  ],
  backlog_ref: Annotated[
    str | None,
    typer.Option("--backlog-ref", help="Backlog item tracking this (e.g. ISSUE-042)"),
  ] = None,
  format_type: Annotated[
    str,
    typer.Option("--format", help="Output format: table or json"),
  ] = "table",
  root: RootOption = None,
) -> None:
  """Defer a finding to a future delta or backlog item."""
  _cli_disposition_finding(
    delta,
    finding_id,
    action="defer",
    root=root,
    json_mode=format_type == "json",
    rationale=rationale,
    backlog_ref=backlog_ref,
  )


@finding_app.command("waive")
def finding_waive_command(
  delta: Annotated[str, typer.Argument(help="Delta ID (e.g. DE-103)")],
  finding_id: Annotated[str, typer.Argument(help="Finding ID (e.g. R1-001)")],
  rationale: Annotated[
    str,
    typer.Option("--rationale", help="Why this finding is waived"),
  ],
  authority: Annotated[
    str | None,
    typer.Option("--authority", help="Who made the decision: user or agent"),
  ] = None,
  format_type: Annotated[
    str,
    typer.Option("--format", help="Output format: table or json"),
  ] = "table",
  root: RootOption = None,
) -> None:
  """Waive a finding (accept the risk)."""
  _cli_disposition_finding(
    delta,
    finding_id,
    action="waive",
    root=root,
    json_mode=format_type == "json",
    rationale=rationale,
    authority=authority,
  )


@finding_app.command("supersede")
def finding_supersede_command(
  delta: Annotated[str, typer.Argument(help="Delta ID (e.g. DE-103)")],
  finding_id: Annotated[str, typer.Argument(help="Finding ID (e.g. R1-001)")],
  superseded_by: Annotated[
    str,
    typer.Option("--superseded-by", help="Finding ID that replaces this one"),
  ],
  format_type: Annotated[
    str,
    typer.Option("--format", help="Output format: table or json"),
  ] = "table",
  root: RootOption = None,
) -> None:
  """Mark a finding as superseded by another finding."""
  _cli_disposition_finding(
    delta,
    finding_id,
    action="supersede",
    root=root,
    json_mode=format_type == "json",
    superseded_by=superseded_by,
  )


@finding_app.command("list")
def finding_list_command(
  delta: Annotated[str, typer.Argument(help="Delta ID (e.g. DE-103)")],
  round_filter: Annotated[
    int | None,
    typer.Option("--round", help="Filter to a specific round number"),
  ] = None,
  format_type: Annotated[
    str,
    typer.Option("--format", help="Output format: table or json"),
  ] = "table",
  root: RootOption = None,
) -> None:
  """List all review findings across rounds."""
  from supekku.scripts.lib.workflow.review_io import (  # noqa: PLC0415
    FindingsNotFoundError,
    FindingsVersionError,
    read_findings,
  )

  json_mode = format_type == "json"
  cmd = "review.finding.list"

  repo_root = find_repo_root(root)
  delta_dir = _resolve_delta_dir(delta, repo_root)
  delta_id = delta.upper()

  try:
    data = read_findings(delta_dir)
  except FindingsNotFoundError as exc:
    msg = f"No findings for {delta_id}"
    if json_mode:
      emit_json_and_exit(
        cli_json_success(
          cmd,
          {
            "delta_id": delta_id,
            "findings": [],
          },
        )
      )
    typer.echo(msg)
    raise typer.Exit(EXIT_SUCCESS) from exc
  except FindingsVersionError as exc:
    msg = str(exc)
    if json_mode:
      emit_json_and_exit(cli_json_error(cmd, EXIT_PRECONDITION, "precondition", msg))
    typer.echo(msg, err=True)
    raise typer.Exit(EXIT_FAILURE) from exc

  # Collect findings with round and severity metadata
  findings: list[dict] = []
  for round_data in data.get("rounds", []):
    round_num = round_data.get("round", 0)
    if round_filter is not None and round_num != round_filter:
      continue
    for category in ("blocking", "non_blocking"):
      for finding in round_data.get(category, []):
        findings.append(
          {
            "id": finding.get("id", "?"),
            "round": round_num,
            "title": finding.get("title", ""),
            "status": finding.get("status", "open"),
            "severity": category,
            "disposition": finding.get("disposition"),
          }
        )

  if json_mode:
    emit_json_and_exit(
      cli_json_success(
        cmd,
        {
          "delta_id": delta_id,
          "findings": findings,
        },
      )
    )

  # Human output
  if not findings:
    typer.echo(f"No findings for {delta_id}")
  else:
    for f in findings:
      disp = f" [{f['disposition']['action']}]" if f["disposition"] else ""
      typer.echo(
        f"  {f['id']} ({f['severity']}) {f['status']}{disp} — {f['title']}",
      )
  raise typer.Exit(EXIT_SUCCESS)


# ---------------------------------------------------------------------------
# phase complete
# ---------------------------------------------------------------------------


@phase_app.command("complete")
def phase_complete_command(
  delta: Annotated[str, typer.Argument(help="Delta ID (e.g. DE-103)")],
  to_role: Annotated[
    str | None,
    typer.Option("--to", help="Target role for auto-handoff (overrides bridge/policy)"),
  ] = None,
  no_handoff: Annotated[
    bool,
    typer.Option("--no-handoff", help="Skip auto-handoff emission"),
  ] = False,
  root: RootOption = None,
) -> None:
  """Mark the current phase as complete. Emits handoff per policy/bridge."""
  from supekku.scripts.lib.core.git import (  # noqa: PLC0415
    get_branch,
    get_head_sha,
    has_staged_changes,
    has_uncommitted_changes,
    short_sha,
  )
  from supekku.scripts.lib.workflow.bridge import extract_phase_bridge  # noqa: PLC0415
  from supekku.scripts.lib.workflow.handoff_io import (  # noqa: PLC0415
    HandoffValidationError,
    build_handoff,
    write_handoff,
  )
  from supekku.scripts.lib.workflow.state_io import (  # noqa: PLC0415
    StateNotFoundError,
    StateValidationError,
    read_state,
    update_state_workflow,
    write_state,
  )
  from supekku.scripts.lib.workflow.state_machine import WorkflowState  # noqa: PLC0415

  repo_root = find_repo_root(root)
  delta_dir = _resolve_delta_dir(delta, repo_root)
  delta_id = delta.upper()

  # Read state
  try:
    state_data = read_state(delta_dir)
  except StateNotFoundError as exc:
    typer.echo(f"No workflow state for {delta_id}", err=True)
    raise typer.Exit(EXIT_FAILURE) from exc
  except StateValidationError as exc:
    typer.echo(f"Invalid workflow state: {exc}", err=True)
    raise typer.Exit(EXIT_FAILURE) from exc

  current_status = state_data["workflow"]["status"]
  if current_status not in (
    WorkflowState.IMPLEMENTING.value,
    WorkflowState.CHANGES_REQUESTED.value,
  ):
    typer.echo(
      f"Cannot complete phase in state '{current_status}' "
      "(must be implementing or changes_requested)",
      err=True,
    )
    raise typer.Exit(EXIT_FAILURE)

  from supekku.scripts.lib.changes.lifecycle import (  # noqa: PLC0415
    STATUS_COMPLETED,
  )
  from supekku.scripts.lib.core.frontmatter_writer import (  # noqa: PLC0415
    update_frontmatter_status,
  )

  phase = state_data.get("phase", {})
  phase_id = phase.get("id", "unknown")

  # Check if already complete (idempotent for handoff re-emission)
  already_complete = phase.get("status") == "complete"

  # Update phase frontmatter (normative) before state.yaml (transient) — DEC-104-08
  phase_path_val = phase.get("path")
  if phase_path_val:
    abs_phase = repo_root / phase_path_val
    if abs_phase.exists():
      update_frontmatter_status(abs_phase, STATUS_COMPLETED)

  # Step 1: Mark phase complete in state.yaml (control-plane vocabulary)
  if not already_complete:
    state_data["phase"]["status"] = "complete"

  # Determine handoff emission
  should_emit_handoff = False
  handoff_role = to_role
  config = _load_workflow_config(repo_root)

  if not no_handoff:
    # Check phase-bridge block in phase sheet
    bridge_data = None
    phase_path = phase.get("path")
    if phase_path:
      abs_phase_path = repo_root / phase_path
      if abs_phase_path.exists():
        bridge_data = extract_phase_bridge(
          abs_phase_path.read_text(encoding="utf-8"),
        )

    if bridge_data:
      # Bridge block takes precedence
      should_emit_handoff = bridge_data.get("handoff_ready", False)
      if should_emit_handoff and not handoff_role:
        handoff_role = (
          "reviewer"
          if bridge_data.get("review_required")
          else config.get("workflow", {}).get("default_next_role", "implementer")
        )
    elif config.get("workflow", {}).get("auto_handoff_on_phase_complete", True):
      # Policy fallback
      should_emit_handoff = True
      if not handoff_role:
        handoff_role = config.get("workflow", {}).get(
          "default_next_role",
          "implementer",
        )

  # Write state with phase complete (step 1)
  try:
    write_state(delta_dir, state_data)
  except StateValidationError as exc:
    typer.echo(f"State validation failed: {exc}", err=True)
    raise typer.Exit(EXIT_FAILURE) from exc

  typer.echo(f"Phase complete: {phase_id}")

  # Step 2+3: Emit handoff if requested
  if should_emit_handoff and handoff_role:
    artifact = state_data.get("artifact", {})
    plan = state_data.get("plan", {})

    # Assemble required_reading
    required_reading: list[str] = []
    if artifact.get("path"):
      required_reading.append(f"{artifact['path']}/{delta_id}.md")
    if plan.get("path"):
      required_reading.append(plan["path"])
    if phase.get("path"):
      required_reading.append(phase["path"])
    if artifact.get("notes_path"):
      required_reading.append(artifact["notes_path"])
    if not required_reading:
      required_reading.append(delta_id)

    activity_kind = "review" if handoff_role == "reviewer" else "implementation"

    head_sha = get_head_sha(repo_root)
    git_head = short_sha(head_sha) if head_sha else None
    git_branch = get_branch(repo_root)
    uncommitted = has_uncommitted_changes(repo_root)
    staged = has_staged_changes(repo_root)

    handoff_data = build_handoff(
      artifact_id=delta_id,
      artifact_kind=artifact.get("kind", "delta"),
      from_role=state_data["workflow"]["active_role"],
      to_role=handoff_role,
      phase_id=phase_id,
      phase_status="complete",
      required_reading=required_reading,
      boundary=config.get("workflow", {}).get("handoff_boundary", "phase"),
      next_activity_kind=activity_kind,
      git_head=git_head,
      git_branch=git_branch,
      has_uncommitted=uncommitted,
      has_staged=staged,
    )

    try:
      hp = write_handoff(delta_dir, handoff_data)
    except HandoffValidationError as exc:
      typer.echo(f"Handoff validation failed: {exc}", err=True)
      raise typer.Exit(EXIT_FAILURE) from exc

    # Update state to awaiting_handoff
    update_state_workflow(
      state_data,
      status=WorkflowState.AWAITING_HANDOFF.value,
      next_role=handoff_role,
      claimed_by=None,
    )

    try:
      write_state(delta_dir, state_data)
    except StateValidationError as exc:
      typer.echo(f"State update failed: {exc}", err=True)
      raise typer.Exit(EXIT_FAILURE) from exc

    typer.echo(f"  handoff emitted → {handoff_role}")
    typer.echo(f"  file: {hp}")

  raise typer.Exit(EXIT_SUCCESS)
