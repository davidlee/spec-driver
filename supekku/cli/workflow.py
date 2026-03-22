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
  staleness: dict = {"phase_id": phase.get("id", "unknown"), "head": "unknown", "triggers": []}

  try:
    index = read_review_index(delta_dir)
    bootstrap_status = index.get("review", {}).get(
      "bootstrap_status", BootstrapStatus.WARM.value,
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
      for finding in round_data.get("blocking", []) + round_data.get("non_blocking", []):
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
  from supekku.scripts.lib.core.git import (  # noqa: PLC0415
    get_changed_files,
    get_head_sha,
    short_sha,
  )
  from supekku.scripts.lib.workflow.review_io import (  # noqa: PLC0415
    ReviewIndexNotFoundError,
    ReviewIndexValidationError,
    bootstrap_path,
    build_review_index,
    read_review_index,
    write_review_index,
  )
  from supekku.scripts.lib.workflow.review_state_machine import (  # noqa: PLC0415
    BootstrapStatus,
  )
  from supekku.scripts.lib.workflow.staleness import (  # noqa: PLC0415
    check_domain_map_files_exist,
    evaluate_staleness,
  )
  from supekku.scripts.lib.workflow.state_io import (  # noqa: PLC0415
    StateNotFoundError,
    StateValidationError,
    read_state,
  )

  json_mode = format_type == "json"
  cmd = "review.prime"

  repo_root = find_repo_root(root)
  delta_dir = _resolve_delta_dir(delta, repo_root)
  delta_id = delta.upper()

  # Read current state
  try:
    state_data = read_state(delta_dir)
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

  phase_id = state_data.get("phase", {}).get("id", "unknown")
  head_sha = get_head_sha(repo_root)
  full_head = head_sha or "unknown"
  git_head = short_sha(head_sha) if head_sha else "unknown"

  config = _load_workflow_config(repo_root)
  review_config = config.get("review", {})
  bootstrap_config = review_config.get("bootstrap", {})
  session_scope = review_config.get("session_scope")

  # Check existing cache
  existing_index = None
  cache_status = BootstrapStatus.COLD

  try:
    existing_index = read_review_index(delta_dir)
  except ReviewIndexNotFoundError:
    pass  # Cold start
  except ReviewIndexValidationError:
    cache_status = BootstrapStatus.INVALID

  if existing_index:
    # Evaluate staleness
    changed_files = None
    cached_head = (
      existing_index.get("staleness", {})
      .get(
        "cache_key",
        {},
      )
      .get("head", "")
    )
    if cached_head and cached_head != full_head:
      changed_files = get_changed_files(cached_head, "HEAD", repo_root)

    # Check for deleted domain_map files
    deleted = check_domain_map_files_exist(
      existing_index.get("domain_map", []),
      repo_root,
    )
    if deleted:
      cache_status = BootstrapStatus.INVALID
      if not json_mode:
        typer.echo(f"  invalidated: {len(deleted)} domain_map files deleted")
    else:
      result = evaluate_staleness(
        existing_index,
        current_phase_id=phase_id,
        current_head=full_head,
        changed_files=changed_files,
      )
      cache_status = result.status
      if result.triggers and not json_mode:
        typer.echo(f"  staleness triggers: {', '.join(result.triggers)}")

  # Build domain_map from delta bundle context
  domain_map = _build_domain_map(delta_dir, repo_root, bootstrap_config)

  # Carry forward optional sections from existing index when doing incremental update
  invariants = None
  risk_areas = None
  review_focus = None
  known_decisions = None

  if cache_status == BootstrapStatus.REUSABLE and existing_index:
    invariants = existing_index.get("invariants")
    risk_areas = existing_index.get("risk_areas")
    review_focus = existing_index.get("review_focus")
    known_decisions = existing_index.get("known_decisions")

  # Build review index
  source_handoff = None
  handoff_file = delta_dir / "workflow" / "handoff.current.yaml"
  if handoff_file.exists():
    source_handoff = "workflow/handoff.current.yaml"

  # Set judgment to in_progress via review transition (DR-109 §4.3)
  from supekku.scripts.lib.workflow.review_state_machine import (  # noqa: PLC0415
    ReviewStatus,
    ReviewTransitionCommand,
    apply_review_transition,
  )

  judgment_status = apply_review_transition(
    ReviewStatus.NOT_STARTED,
    ReviewTransitionCommand.BEGIN_REVIEW,
  )

  index_data = build_review_index(
    artifact_id=delta_id,
    bootstrap_status=BootstrapStatus.WARM.value,
    judgment_status=judgment_status.value,
    phase_id=phase_id,
    git_head=full_head,
    domain_map=domain_map,
    session_scope=session_scope,
    source_handoff=source_handoff,
    invariants=invariants,
    risk_areas=risk_areas,
    review_focus=review_focus,
    known_decisions=known_decisions,
  )

  # Write order per DR-102 §5: 1. review-index, 2. bootstrap.md, 3. state
  try:
    idx_path = write_review_index(delta_dir, index_data)
  except ReviewIndexValidationError as exc:
    msg = f"Review index validation failed: {exc}"
    if json_mode:
      emit_json_and_exit(cli_json_error(cmd, EXIT_PRECONDITION, "validation", msg))
    typer.echo(msg, err=True)
    raise typer.Exit(EXIT_FAILURE) from exc

  # Generate bootstrap markdown
  bootstrap_md = _generate_bootstrap_markdown(
    delta_id=delta_id,
    state_data=state_data,
    index_data=index_data,
    delta_dir=delta_dir,
    repo_root=repo_root,
    config=bootstrap_config,
    cache_status=cache_status,
  )
  bp = bootstrap_path(delta_dir)
  bp.parent.mkdir(parents=True, exist_ok=True)
  bp.write_text(bootstrap_md, encoding="utf-8")

  # Determine action (DEC-108-006)
  action = _prime_action(cache_status)

  # Determine review round
  from supekku.scripts.lib.workflow.review_io import (  # noqa: PLC0415
    next_round_number,
  )

  review_round = next_round_number(delta_dir)

  if json_mode:
    emit_json_and_exit(cli_json_success(cmd, {
      "delta_id": delta_id,
      "action": action,
      "bootstrap_status": BootstrapStatus.WARM.value,
      "judgment_status": judgment_status.value,
      "review_round": review_round,
      "index_path": str(idx_path.relative_to(repo_root)),
      "bootstrap_path": str(bp.relative_to(repo_root)),
    }))

  typer.echo(f"Review primed: {delta_id} ({action})")
  typer.echo(f"  index: {idx_path}")
  typer.echo(f"  bootstrap: {bp}")
  raise typer.Exit(EXIT_SUCCESS)


def _prime_action(cache_status: str) -> str:
  """Map bootstrap cache status to a prime action label (DEC-108-006).

  - created: first-ever prime (cold, no prior review-index)
  - rebuilt: re-prime after teardown/invalid/stale
  - refreshed: reusable cache with incremental update
  """
  from supekku.scripts.lib.workflow.review_state_machine import (  # noqa: PLC0415
    BootstrapStatus,
  )

  if cache_status == BootstrapStatus.COLD:
    return "created"
  if cache_status in (BootstrapStatus.INVALID, BootstrapStatus.STALE):
    return "rebuilt"
  if cache_status == BootstrapStatus.REUSABLE:
    return "refreshed"
  return "created"


def _build_domain_map(
  delta_dir: Path,
  repo_root: Path,
  bootstrap_config: dict,
) -> list[dict]:
  """Build domain_map from delta bundle files.

  Assembles areas from the delta's key files: DE, IP, phase sheets,
  notes, and workflow artifacts.
  """
  areas: list[dict] = []

  # Delta documentation area
  doc_files: list[str] = []
  for f in sorted(delta_dir.glob("*.md")):
    doc_files.append(str(f.relative_to(repo_root)))
  if doc_files:
    areas.append(
      {
        "area": "delta_docs",
        "purpose": "delta and plan documentation",
        "files": doc_files,
      }
    )

  # Phase sheets
  phases_dir = delta_dir / "phases"
  if phases_dir.is_dir():
    phase_files = [
      str(f.relative_to(repo_root)) for f in sorted(phases_dir.glob("*.md"))
    ]
    if phase_files:
      areas.append(
        {
          "area": "phase_sheets",
          "purpose": "per-phase execution records",
          "files": phase_files,
        }
      )

  # Workflow artifacts
  wf_dir = delta_dir / "workflow"
  if wf_dir.is_dir():
    wf_files = [
      str(f.relative_to(repo_root)) for f in sorted(wf_dir.iterdir()) if f.is_file()
    ]
    if wf_files:
      areas.append(
        {
          "area": "workflow_state",
          "purpose": "orchestration control plane files",
          "files": wf_files,
        }
      )

  # Ensure at least one area (schema requires min 1)
  if not areas:
    areas.append(
      {
        "area": "delta_root",
        "purpose": "delta bundle",
        "files": [str(delta_dir.relative_to(repo_root))],
      }
    )

  return areas


def _generate_bootstrap_markdown(
  *,
  delta_id: str,
  state_data: dict,
  index_data: dict,
  delta_dir: Path,
  repo_root: Path,
  config: dict,
  cache_status: str,
) -> str:
  """Generate review-bootstrap.md content."""
  lines: list[str] = []
  lines.append(f"# Review Bootstrap — {delta_id}")
  lines.append("")
  lines.append(f"**Cache status:** {cache_status} → warm")
  lines.append(f"**Phase:** {state_data.get('phase', {}).get('id', '?')}")
  lines.append(
    f"**Workflow status:** {state_data.get('workflow', {}).get('status', '?')}",
  )
  lines.append("")

  # Required reading
  lines.append("## Required Reading")
  lines.append("")
  artifact = state_data.get("artifact", {})
  plan = state_data.get("plan", {})
  phase = state_data.get("phase", {})

  if artifact.get("path"):
    lines.append(f"- Delta: `{artifact['path']}/{delta_id}.md`")
  if plan.get("path"):
    lines.append(f"- Plan: `{plan['path']}`")
  if phase.get("path"):
    lines.append(f"- Active phase: `{phase['path']}`")
  if artifact.get("notes_path"):
    lines.append(f"- Notes: `{artifact['notes_path']}`")

  # Domain map
  lines.append("")
  lines.append("## Domain Map")
  lines.append("")
  for entry in index_data.get("domain_map", []):
    lines.append(f"### {entry['area']}")
    lines.append(f"**Purpose:** {entry['purpose']}")
    lines.append("")
    for f in entry.get("files", []):
      lines.append(f"- `{f}`")
    lines.append("")

  # Invariants
  invariants = index_data.get("invariants", [])
  if invariants:
    lines.append("## Invariants")
    lines.append("")
    for inv in invariants:
      lines.append(f"- **{inv['id']}**: {inv['summary']}")
    lines.append("")

  # Risk areas
  risk_areas = index_data.get("risk_areas", [])
  if risk_areas:
    lines.append("## Risk Areas")
    lines.append("")
    for ra in risk_areas:
      lines.append(f"- **{ra['id']}**: {ra['summary']}")
    lines.append("")

  # Review focus
  review_focus = index_data.get("review_focus", [])
  if review_focus:
    lines.append("## Review Focus")
    lines.append("")
    for rf in review_focus:
      lines.append(f"- {rf}")
    lines.append("")

  # Staleness info
  cache_key = index_data.get("staleness", {}).get("cache_key", {})
  lines.append("## Cache Key")
  lines.append("")
  lines.append(f"- Phase: `{cache_key.get('phase_id', '?')}`")
  lines.append(f"- HEAD: `{cache_key.get('head', '?')}`")
  lines.append("")

  return "\n".join(lines)


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
  from supekku.scripts.lib.workflow.review_io import (  # noqa: PLC0415
    FindingsNotFoundError,
    FindingsValidationError,
    FindingsVersionError,
    ReviewIndexNotFoundError,
    ReviewIndexValidationError,
    append_round,
    build_findings,
    read_findings,
    read_review_index,
    write_findings,
    write_review_index,
  )
  from supekku.scripts.lib.workflow.review_state_machine import (  # noqa: PLC0415
    can_approve,
    collect_blocking_findings,
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

  # Read state
  try:
    state_data = read_state(delta_dir)
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

  # Validate workflow transition
  current = WorkflowState(state_data["workflow"]["status"])
  command = (
    TransitionCommand.REVIEW_COMPLETE_APPROVED
    if status == "approved"
    else TransitionCommand.REVIEW_COMPLETE_CHANGES_REQUESTED
  )

  try:
    result = apply_transition(current, command)
  except TransitionError as exc:
    msg = f"Cannot complete review: {exc}"
    if json_mode:
      emit_json_and_exit(cli_json_error(cmd, EXIT_PRECONDITION, "precondition", msg))
    typer.echo(msg, err=True)
    raise typer.Exit(EXIT_FAILURE) from exc

  # Approval guard: check blocking findings (DR-109 §4.3)
  if status == "approved":
    try:
      existing_findings = read_findings(delta_dir)
      blocking = collect_blocking_findings(existing_findings.get("rounds", []))
      allowed, reasons = can_approve(blocking)
      if not allowed:
        msg = "Cannot approve: " + "; ".join(reasons)
        if json_mode:
          emit_json_and_exit(cli_json_error(
            cmd, EXIT_GUARD_VIOLATION, "guard_violation", msg,
          ))
        typer.echo("Cannot approve: blocking findings remain:", err=True)
        for reason in reasons:
          typer.echo(f"  - {reason}", err=True)
        raise typer.Exit(EXIT_FAILURE)
    except FindingsNotFoundError:
      pass  # No findings = no blocking findings = guard passes
    except FindingsVersionError as exc:
      msg = str(exc)
      if json_mode:
        emit_json_and_exit(cli_json_error(cmd, EXIT_PRECONDITION, "precondition", msg))
      typer.echo(msg, err=True)
      raise typer.Exit(EXIT_FAILURE) from exc

  # Build or append round (v2 accumulative model, DR-109 §3.5)
  reviewer_role = state_data["workflow"].get("active_role")
  try:
    findings_data = read_findings(delta_dir)
    append_round(
      findings_data,
      status=status,
      reviewer_role=reviewer_role,
      summary=summary,
    )
  except (FindingsNotFoundError, FindingsVersionError):
    findings_data = build_findings(
      artifact_id=delta_id,
      round_number=1,
      status=status,
      reviewer_role=reviewer_role,
      summary=summary,
    )

  # Write order per DR-102 §5: 1. findings, 2. review-index, 3. state
  try:
    fp = write_findings(delta_dir, findings_data)
  except FindingsValidationError as exc:
    typer.echo(f"Findings validation failed: {exc}", err=True)
    raise typer.Exit(EXIT_FAILURE) from exc

  # Write judgment_status to review-index (DR-109 §4.3)
  try:
    index_data = read_review_index(delta_dir)
    index_data.setdefault("review", {})["judgment_status"] = status
    write_review_index(delta_dir, index_data)
  except ReviewIndexNotFoundError:
    pass  # No review-index — skip judgment write
  except ReviewIndexValidationError as exc:
    typer.echo(f"Review index update failed: {exc}", err=True)
    # Non-fatal — findings and state are more important

  # Auto-teardown on approved if policy says so
  config = _load_workflow_config(repo_root)
  review_config = config.get("review", {})
  teardown_on = review_config.get("teardown_on", ["approved", "abandoned"])
  should_teardown = status == "approved" and "approved" in teardown_on

  update_state_workflow(
    state_data,
    status=result.new_state.value,
  )

  try:
    write_state(delta_dir, state_data)
  except StateValidationError as exc:
    typer.echo(f"State update failed: {exc}", err=True)
    raise typer.Exit(EXIT_FAILURE) from exc

  current_round = findings_data["review"]["current_round"]

  if json_mode:
    emit_json_and_exit(cli_json_success(cmd, {
      "delta_id": delta_id,
      "round": current_round,
      "outcome": status,
      "previous_state": current.value,
      "new_state": result.new_state.value,
      "findings_path": str(fp.relative_to(repo_root)),
      "teardown": should_teardown,
    }))

  typer.echo(
    f"Review complete: {delta_id} round {current_round} → {status} "
    f"({current.value} → {result.new_state.value})",
  )
  typer.echo(f"  findings: {fp}")

  if should_teardown:
    _do_teardown(delta_dir, delta_id)

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
  json_mode = format_type == "json"
  cmd = "review.teardown"

  repo_root = find_repo_root(root)
  delta_dir = _resolve_delta_dir(delta, repo_root)
  delta_id = delta.upper()

  removed = _do_teardown(delta_dir, delta_id, silent=json_mode)

  if json_mode:
    emit_json_and_exit(cli_json_success(cmd, {
      "delta_id": delta_id,
      "removed": removed,
    }))

  raise typer.Exit(EXIT_SUCCESS)


# ---------------------------------------------------------------------------
# review finding — disposition subcommands (DR-109 §4.1)
# ---------------------------------------------------------------------------

finding_app = typer.Typer(
  help="Disposition review findings",
  no_args_is_help=True,
)
review_app.add_typer(finding_app, name="finding")


def _available_finding_ids(data: dict) -> list[str]:
  """Collect all finding IDs from all rounds for error messages."""
  ids: list[str] = []
  for round_data in data.get("rounds", []):
    for category in ("blocking", "non_blocking"):
      for f in round_data.get(category, []):
        if f.get("id"):
          ids.append(f["id"])
  return ids


def _disposition_finding(
  delta: str,
  finding_id: str,
  disposition: dict,
  root: Path | None,
  *,
  json_mode: bool = False,
) -> None:
  """Shared orchestration for all disposition commands.

  Reads findings, updates disposition in-place, writes back.
  Exits non-zero if finding not found.
  """
  from supekku.scripts.lib.workflow.review_io import (  # noqa: PLC0415
    FindingsNotFoundError,
    FindingsValidationError,
    FindingsVersionError,
    find_finding,
    read_findings,
    update_finding_disposition,
    write_findings,
  )

  cmd = f"review.finding.{disposition['action']}"
  repo_root = find_repo_root(root)
  delta_dir = _resolve_delta_dir(delta, repo_root)
  delta_id = delta.upper()

  try:
    data = read_findings(delta_dir)
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

  # Capture previous status before disposition
  previous_finding = find_finding(data, finding_id)
  previous_status = previous_finding.status.value if previous_finding else "unknown"

  if not update_finding_disposition(data, finding_id, disposition):
    available = _available_finding_ids(data)
    msg = f"Finding {finding_id} not found. Available: {', '.join(available)}"
    if json_mode:
      emit_json_and_exit(cli_json_error(cmd, EXIT_PRECONDITION, "precondition", msg))
    typer.echo(msg, err=True)
    raise typer.Exit(EXIT_FAILURE)

  try:
    write_findings(delta_dir, data)
  except FindingsValidationError as exc:
    msg = f"Findings validation failed: {exc}"
    if json_mode:
      emit_json_and_exit(cli_json_error(cmd, EXIT_PRECONDITION, "validation", msg))
    typer.echo(msg, err=True)
    raise typer.Exit(EXIT_FAILURE) from exc

  # Get the new status after disposition
  updated_finding = find_finding(data, finding_id)
  new_status = updated_finding.status.value if updated_finding else "unknown"

  if json_mode:
    emit_json_and_exit(cli_json_success(cmd, {
      "delta_id": delta_id,
      "finding_id": finding_id,
      "action": disposition["action"],
      "previous_status": previous_status,
      "new_status": new_status,
    }))

  typer.echo(
    f"Finding {finding_id}: {disposition['action']} "
    f"(delta {delta_id})",
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
  from supekku.scripts.lib.workflow.review_state_machine import (  # noqa: PLC0415
    DispositionAuthority,
    FindingDispositionAction,
  )

  disposition: dict = {
    "action": FindingDispositionAction.FIX.value,
    "authority": DispositionAuthority.AGENT.value,
  }
  if resolved_at:
    disposition["resolved_at"] = resolved_at
  _disposition_finding(delta, finding_id, disposition, root, json_mode=format_type == "json")


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
  from supekku.scripts.lib.workflow.review_state_machine import (  # noqa: PLC0415
    DispositionAuthority,
    FindingDispositionAction,
  )

  disposition: dict = {
    "action": FindingDispositionAction.DEFER.value,
    "authority": DispositionAuthority.AGENT.value,
    "rationale": rationale,
  }
  if backlog_ref:
    disposition["backlog_ref"] = backlog_ref
  _disposition_finding(delta, finding_id, disposition, root, json_mode=format_type == "json")


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
  from supekku.scripts.lib.workflow.review_state_machine import (  # noqa: PLC0415
    DispositionAuthority,
    FindingDispositionAction,
  )

  disposition: dict = {
    "action": FindingDispositionAction.WAIVE.value,
    "authority": (
      DispositionAuthority(authority).value
      if authority
      else DispositionAuthority.AGENT.value
    ),
    "rationale": rationale,
  }
  _disposition_finding(delta, finding_id, disposition, root, json_mode=format_type == "json")


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
  from supekku.scripts.lib.workflow.review_state_machine import (  # noqa: PLC0415
    DispositionAuthority,
    FindingDispositionAction,
  )

  disposition: dict = {
    "action": FindingDispositionAction.SUPERSEDE.value,
    "authority": DispositionAuthority.AGENT.value,
    "superseded_by": superseded_by,
  }
  _disposition_finding(delta, finding_id, disposition, root, json_mode=format_type == "json")


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
      emit_json_and_exit(cli_json_success(cmd, {
        "delta_id": delta_id,
        "findings": [],
      }))
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
        findings.append({
          "id": finding.get("id", "?"),
          "round": round_num,
          "title": finding.get("title", ""),
          "status": finding.get("status", "open"),
          "severity": category,
          "disposition": finding.get("disposition"),
        })

  if json_mode:
    emit_json_and_exit(cli_json_success(cmd, {
      "delta_id": delta_id,
      "findings": findings,
    }))

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


# ---------------------------------------------------------------------------
# Teardown helper
# ---------------------------------------------------------------------------


def _do_teardown(
  delta_dir: Path,
  delta_id: str,
  *,
  silent: bool = False,
) -> list[str]:
  """Delete reviewer state files. Returns list of deleted file names."""
  from supekku.scripts.lib.workflow.review_io import (  # noqa: PLC0415
    bootstrap_path,
    findings_path,
    index_path,
  )

  deleted: list[str] = []
  for path_fn, name in [
    (index_path, "review-index"),
    (findings_path, "review-findings"),
    (bootstrap_path, "review-bootstrap"),
  ]:
    p = path_fn(delta_dir)
    if p.exists():
      p.unlink()
      deleted.append(name)

  if not silent:
    if deleted:
      typer.echo(f"Teardown: {delta_id} — deleted {', '.join(deleted)}")
    else:
      typer.echo(f"Teardown: {delta_id} — no reviewer state to delete")

  return deleted
