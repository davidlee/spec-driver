"""Review operations for spec-driver orchestration layer.

Composed domain operations extracted from CLI commands (DE-124).
Each function encapsulates a complete orchestration path:
load state → validate → mutate → write → return typed result.

CLI commands become thin wrappers that call these operations
and format the results for human/JSON output.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

from supekku.scripts.lib.workflow.review_state_machine import (
  BootstrapStatus,
  DispositionAuthority,
  FindingDispositionAction,
  FindingStatus,
  ReviewStatus,
)
from supekku.scripts.lib.workflow.state_machine import WorkflowState

# ---------------------------------------------------------------------------
# Exceptions (DE-124)
# ---------------------------------------------------------------------------


class DeltaNotFoundError(Exception):
  """Raised when a delta ID cannot be resolved to a directory."""

  def __init__(self, delta_id: str) -> None:
    self.delta_id = delta_id
    super().__init__(f"Delta not found: {delta_id}")


class ReviewApprovalGuardError(Exception):
  """Raised when approval is blocked by undispositioned findings."""

  def __init__(self, reasons: list[str]) -> None:
    self.reasons = reasons
    super().__init__("Cannot approve: " + "; ".join(reasons))


class FindingNotFoundError(Exception):
  """Raised when a finding ID doesn't exist in any round."""

  def __init__(
    self,
    finding_id: str,
    available: list[str],
  ) -> None:
    self.finding_id = finding_id
    self.available = available
    super().__init__(
      f"Finding {finding_id} not found. Available: {', '.join(available)}"
    )


class DispositionValidationError(Exception):
  """Raised when disposition params violate domain constraints."""


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


class PrimeAction(StrEnum):
  """What prime_review did with the cache."""

  CREATED = "created"
  REBUILT = "rebuilt"
  REFRESHED = "refreshed"


@dataclass
class PrimeResult:
  delta_id: str
  action: PrimeAction
  bootstrap_status: BootstrapStatus
  judgment_status: ReviewStatus
  review_round: int
  index_path: Path
  bootstrap_path: Path


@dataclass
class CompleteResult:
  delta_id: str
  round_number: int
  outcome: ReviewStatus
  previous_state: WorkflowState
  new_state: WorkflowState
  findings_path: Path
  teardown_performed: bool
  removed_files: list[str] = field(default_factory=list)


@dataclass
class DispositionResult:
  delta_id: str
  finding_id: str
  action: FindingDispositionAction
  previous_status: FindingStatus
  new_status: FindingStatus


@dataclass
class TeardownResult:
  delta_id: str
  removed: list[str] = field(default_factory=list)


@dataclass
class ReviewSummary:
  current_round: int
  judgment_status: ReviewStatus
  blocking_total: int
  blocking_dispositioned: int
  non_blocking_total: int
  all_blocking_resolved: bool
  outcome_ready: bool


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _load_config(repo_root: Path) -> dict:
  """Load workflow config without CLI dependency."""
  try:
    from supekku.scripts.lib.core.config import (  # noqa: PLC0415
      load_workflow_config,
    )

    return load_workflow_config(repo_root)
  except Exception:  # noqa: BLE001
    return {}


def _prime_action_from_cache_status(
  cache_status: BootstrapStatus,
) -> PrimeAction:
  """Map bootstrap cache status to a PrimeAction enum."""
  if cache_status == BootstrapStatus.COLD:
    return PrimeAction.CREATED
  if cache_status in (BootstrapStatus.INVALID, BootstrapStatus.STALE):
    return PrimeAction.REBUILT
  if cache_status == BootstrapStatus.REUSABLE:
    return PrimeAction.REFRESHED
  return PrimeAction.CREATED


def _build_domain_map(
  delta_dir: Path,
  repo_root: Path,
  bootstrap_config: dict,  # noqa: ARG001 — reserved for future use
) -> list[dict]:
  """Build domain_map from delta bundle files."""
  areas: list[dict] = []

  # Delta documentation area
  doc_files = [str(f.relative_to(repo_root)) for f in sorted(delta_dir.glob("*.md"))]
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
  delta_dir: Path,  # noqa: ARG001 — reserved for future use
  repo_root: Path,  # noqa: ARG001 — reserved for future use
  config: dict,  # noqa: ARG001 — reserved for future use
  cache_status: str,
) -> str:
  """Generate review-bootstrap.md content."""
  lines: list[str] = []
  lines.append(f"# Review Bootstrap — {delta_id}")
  lines.append("")
  lines.append(f"**Cache status:** {cache_status} → warm")
  lines.append(
    f"**Phase:** {state_data.get('phase', {}).get('id', '?')}",
  )
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

  # Cache key
  cache_key = index_data.get("staleness", {}).get("cache_key", {})
  lines.append("## Cache Key")
  lines.append("")
  lines.append(f"- Phase: `{cache_key.get('phase_id', '?')}`")
  lines.append(f"- HEAD: `{cache_key.get('head', '?')}`")
  lines.append("")

  return "\n".join(lines)


def _find_finding_with_category(
  data: dict,
  finding_id: str,
) -> tuple[dict | None, str | None]:
  """Locate a finding dict and its category ('blocking'/'non_blocking').

  Returns (finding_dict, category) or (None, None) if not found.
  """
  for round_data in data.get("rounds", []):
    for category in ("blocking", "non_blocking"):
      for finding_dict in round_data.get(category, []):
        if finding_dict.get("id") == finding_id:
          return finding_dict, category
  return None, None


def _collect_all_finding_ids(data: dict) -> list[str]:
  """Collect all finding IDs from all rounds."""
  ids: list[str] = []
  for round_data in data.get("rounds", []):
    for category in ("blocking", "non_blocking"):
      for f in round_data.get(category, []):
        if f.get("id"):
          ids.append(f["id"])
  return ids


def _validate_disposition(
  action: FindingDispositionAction,
  is_blocking: bool,  # noqa: ARG001 — reserved for future strict mode
  *,
  authority: DispositionAuthority,  # noqa: ARG001
  rationale: str | None,
  backlog_ref: str | None,  # noqa: ARG001
  resolved_at: str | None,  # noqa: ARG001
  superseded_by: str | None,
) -> None:
  """Validate disposition parameters against DR-109 §3.4 constraints.

  Validates hard constraints that must be satisfied for the disposition
  to be written. Blocking-specific constraints (authority=user,
  backlog_ref for defer, resolved_at for fix) are approval-time guards
  enforced by ``can_approve`` — not disposition-time gates.

  Raises DispositionValidationError on constraint violations.
  """
  errors: list[str] = []

  if action == FindingDispositionAction.WAIVE:
    if not rationale:
      errors.append("waive requires rationale")

  elif action == FindingDispositionAction.DEFER:
    if not rationale:
      errors.append("defer requires rationale")

  elif action == FindingDispositionAction.SUPERSEDE and not superseded_by:
    errors.append("supersede requires superseded_by")

  if errors:
    raise DispositionValidationError("; ".join(errors))


# ---------------------------------------------------------------------------
# Operations
# ---------------------------------------------------------------------------


def resolve_delta_dir(
  delta_id: str,
  repo_root: Path,
) -> Path:
  """Locate a delta bundle directory by ID.

  Scans ``.spec-driver/deltas/`` for a directory whose name starts
  with the delta ID (case-insensitive).

  Raises:
    DeltaNotFoundError: No matching delta directory.
  """
  from supekku.scripts.lib.core.paths import (  # noqa: PLC0415
    get_deltas_dir,
  )

  deltas_dir = get_deltas_dir(repo_root)
  if not deltas_dir.exists():
    raise DeltaNotFoundError(delta_id)

  prefix = delta_id.upper()
  for entry in sorted(deltas_dir.iterdir()):
    if entry.is_dir() and entry.name.upper().startswith(prefix):
      return entry

  raise DeltaNotFoundError(delta_id)


def prime_review(
  delta_dir: Path,
  repo_root: Path,
) -> PrimeResult:
  """Orchestrate review priming.

  Evaluates staleness of existing cache, rebuilds or incrementally
  updates as appropriate. Writes review-index.yaml and
  review-bootstrap.md.

  Raises:
    StateNotFoundError: No workflow state for this delta.
    StateValidationError: Invalid workflow state.
    ReviewIndexValidationError: Built index fails schema validation.
  """
  from supekku.scripts.lib.core.git import (  # noqa: PLC0415
    get_changed_files,
    get_head_sha,
  )
  from supekku.scripts.lib.workflow.review_io import (  # noqa: PLC0415
    ReviewIndexNotFoundError,
    ReviewIndexValidationError,
    bootstrap_path,
    build_review_index,
    next_round_number,
    read_review_index,
    write_review_index,
  )
  from supekku.scripts.lib.workflow.review_state_machine import (  # noqa: PLC0415
    ReviewTransitionCommand,
    apply_review_transition,
  )
  from supekku.scripts.lib.workflow.staleness import (  # noqa: PLC0415
    check_domain_map_files_exist,
    evaluate_staleness,
  )
  from supekku.scripts.lib.workflow.state_io import (  # noqa: PLC0415
    read_state,
  )

  state_data = read_state(delta_dir)
  delta_id = _extract_delta_id(delta_dir)

  phase_id = state_data.get("phase", {}).get("id", "unknown")
  head_sha = get_head_sha(repo_root)
  full_head = head_sha or "unknown"

  config = _load_config(repo_root)
  review_config = config.get("review", {})
  bootstrap_config = review_config.get("bootstrap", {})
  session_scope = review_config.get("session_scope")

  # Evaluate existing cache
  existing_index = None
  cache_status = BootstrapStatus.COLD

  try:
    existing_index = read_review_index(delta_dir)
  except ReviewIndexNotFoundError:
    pass
  except ReviewIndexValidationError:
    cache_status = BootstrapStatus.INVALID

  if existing_index:
    changed_files = None
    cached_head = (
      existing_index.get("staleness", {}).get("cache_key", {}).get("head", "")
    )
    if cached_head and cached_head != full_head:
      changed_files = get_changed_files(
        cached_head,
        "HEAD",
        repo_root,
      )

    deleted = check_domain_map_files_exist(
      existing_index.get("domain_map", []),
      repo_root,
    )
    if deleted:
      cache_status = BootstrapStatus.INVALID
    else:
      result = evaluate_staleness(
        existing_index,
        current_phase_id=phase_id,
        current_head=full_head,
        changed_files=changed_files,
      )
      cache_status = result.status

  # Build domain_map
  domain_map = _build_domain_map(
    delta_dir,
    repo_root,
    bootstrap_config,
  )

  # Carry forward optional sections for incremental update
  invariants = None
  risk_areas = None
  review_focus = None
  known_decisions = None

  if cache_status == BootstrapStatus.REUSABLE and existing_index:
    invariants = existing_index.get("invariants")
    risk_areas = existing_index.get("risk_areas")
    review_focus = existing_index.get("review_focus")
    known_decisions = existing_index.get("known_decisions")

  # Source handoff
  source_handoff = None
  handoff_file = delta_dir / "workflow" / "handoff.current.yaml"
  if handoff_file.exists():
    source_handoff = "workflow/handoff.current.yaml"

  # Judgment transition
  judgment_status = apply_review_transition(
    ReviewStatus.NOT_STARTED,
    ReviewTransitionCommand.BEGIN_REVIEW,
  )

  # Build index
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

  # Write order per DR-102 §5
  idx_path = write_review_index(delta_dir, index_data)

  # Generate bootstrap markdown
  bootstrap_md = _generate_bootstrap_markdown(
    delta_id=delta_id,
    state_data=state_data,
    index_data=index_data,
    delta_dir=delta_dir,
    repo_root=repo_root,
    config=bootstrap_config,
    cache_status=cache_status.value,
  )
  bp = bootstrap_path(delta_dir)
  bp.parent.mkdir(parents=True, exist_ok=True)
  bp.write_text(bootstrap_md, encoding="utf-8")

  action = _prime_action_from_cache_status(cache_status)
  review_round = next_round_number(delta_dir)

  return PrimeResult(
    delta_id=delta_id,
    action=action,
    bootstrap_status=BootstrapStatus.WARM,
    judgment_status=judgment_status,
    review_round=review_round,
    index_path=idx_path,
    bootstrap_path=bp,
  )


def complete_review(
  delta_dir: Path,
  repo_root: Path,
  *,
  status: ReviewStatus,
  summary: str | None = None,
  auto_teardown: bool = True,
) -> CompleteResult:
  """Complete a review round.

  Validates workflow transition, enforces approval guard, writes
  findings and state in correct order.

  Raises:
    StateNotFoundError: No workflow state.
    StateValidationError: Invalid workflow state.
    ReviewApprovalGuardError: Blocking findings prevent approval.
    TransitionError: Invalid workflow transition.
    FindingsValidationError: Built findings fail validation.
  """
  from supekku.scripts.lib.workflow.review_io import (  # noqa: PLC0415
    FindingsNotFoundError,
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
    read_state,
    update_state_workflow,
    write_state,
  )
  from supekku.scripts.lib.workflow.state_machine import (  # noqa: PLC0415
    TransitionCommand,
    apply_transition,
  )

  state_data = read_state(delta_dir)

  delta_id = _extract_delta_id(delta_dir)
  current = WorkflowState(state_data["workflow"]["status"])

  command = (
    TransitionCommand.REVIEW_COMPLETE_APPROVED
    if status == ReviewStatus.APPROVED
    else TransitionCommand.REVIEW_COMPLETE_CHANGES_REQUESTED
  )
  result = apply_transition(current, command)

  # Approval guard (DR-109 §4.3)
  if status == ReviewStatus.APPROVED:
    try:
      existing_findings = read_findings(delta_dir)
      blocking = collect_blocking_findings(
        existing_findings.get("rounds", []),
      )
      allowed, reasons = can_approve(blocking)
      if not allowed:
        raise ReviewApprovalGuardError(reasons)
    except FindingsNotFoundError:
      pass  # No findings = guard passes
    except FindingsVersionError:
      raise  # Propagate version errors

  # Build or append round
  reviewer_role = state_data["workflow"].get("active_role")
  try:
    findings_data = read_findings(delta_dir)
    append_round(
      findings_data,
      status=status.value,
      reviewer_role=reviewer_role,
      summary=summary,
    )
  except (FindingsNotFoundError, FindingsVersionError):
    findings_data = build_findings(
      artifact_id=delta_id,
      round_number=1,
      status=status.value,
      reviewer_role=reviewer_role,
      summary=summary,
    )

  # Write order per DR-102 §5: findings → review-index → state
  fp = write_findings(delta_dir, findings_data)

  # Write judgment_status to review-index
  try:
    index_data = read_review_index(delta_dir)
    index_data.setdefault("review", {})["judgment_status"] = status.value
    write_review_index(delta_dir, index_data)
  except (ReviewIndexNotFoundError, ReviewIndexValidationError):
    pass  # Non-fatal

  # Auto-teardown on approval if policy says so
  config = _load_config(repo_root)
  review_config = config.get("review", {})
  teardown_on = review_config.get(
    "teardown_on",
    ["approved", "abandoned"],
  )
  should_teardown = (
    auto_teardown and status == ReviewStatus.APPROVED and "approved" in teardown_on
  )

  update_state_workflow(state_data, status=result.new_state.value)
  write_state(delta_dir, state_data)

  current_round = findings_data["review"]["current_round"]

  # Perform teardown if applicable
  removed_files: list[str] = []
  if should_teardown:
    teardown_result = teardown_review(delta_dir)
    removed_files = teardown_result.removed

  return CompleteResult(
    delta_id=delta_id,
    round_number=current_round,
    outcome=status,
    previous_state=current,
    new_state=result.new_state,
    findings_path=fp,
    teardown_performed=should_teardown,
    removed_files=removed_files,
  )


def disposition_finding(
  delta_dir: Path,
  finding_id: str,
  *,
  action: FindingDispositionAction,
  authority: DispositionAuthority = DispositionAuthority.AGENT,
  rationale: str | None = None,
  backlog_ref: str | None = None,
  resolved_at: str | None = None,
  superseded_by: str | None = None,
) -> DispositionResult:
  """Disposition a review finding with domain validation.

  Validates parameters against DR-109 §3.4 constraints before
  applying the disposition.

  Raises:
    FindingsNotFoundError: No findings file.
    FindingsVersionError: v1 findings file.
    FindingNotFoundError: Finding ID not in any round.
    DispositionValidationError: Parameters violate constraints.
    FindingsValidationError: Written findings fail validation.
  """
  from supekku.scripts.lib.workflow.review_io import (  # noqa: PLC0415
    read_findings,
    update_finding_disposition,
    write_findings,
  )

  data = read_findings(delta_dir)
  delta_id = _extract_delta_id(delta_dir)

  # Find the finding and its category
  finding_dict, category = _find_finding_with_category(
    data,
    finding_id,
  )
  if finding_dict is None:
    available = _collect_all_finding_ids(data)
    raise FindingNotFoundError(finding_id, available)

  is_blocking = category == "blocking"

  # Domain validation (DEC-124-011)
  _validate_disposition(
    action,
    is_blocking,
    authority=authority,
    rationale=rationale,
    backlog_ref=backlog_ref,
    resolved_at=resolved_at,
    superseded_by=superseded_by,
  )

  # Capture previous status
  previous_status = FindingStatus(
    finding_dict.get("status", "open"),
  )

  # Build disposition dict for the building block
  disposition: dict = {
    "action": action.value,
    "authority": authority.value,
  }
  if rationale is not None:
    disposition["rationale"] = rationale
  if backlog_ref is not None:
    disposition["backlog_ref"] = backlog_ref
  if resolved_at is not None:
    disposition["resolved_at"] = resolved_at
  if superseded_by is not None:
    disposition["superseded_by"] = superseded_by

  update_finding_disposition(data, finding_id, disposition)
  write_findings(delta_dir, data)

  # Get new status after disposition
  updated_dict, _ = _find_finding_with_category(data, finding_id)
  new_status = FindingStatus(
    updated_dict["status"] if updated_dict else "open",
  )

  return DispositionResult(
    delta_id=delta_id,
    finding_id=finding_id,
    action=action,
    previous_status=previous_status,
    new_status=new_status,
  )


def teardown_review(delta_dir: Path) -> TeardownResult:
  """Delete reviewer state files.

  Removes review-index.yaml, review-findings.yaml, and
  review-bootstrap.md if they exist.
  """
  from supekku.scripts.lib.workflow.review_io import (  # noqa: PLC0415
    bootstrap_path,
    findings_path,
    index_path,
  )

  delta_id = _extract_delta_id(delta_dir)
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

  return TeardownResult(delta_id=delta_id, removed=deleted)


def summarize_review(delta_dir: Path) -> ReviewSummary:
  """Read-only query: summarize the current review state.

  Raises:
    FindingsNotFoundError: No findings file.
    FindingsVersionError: v1 findings file.
    ReviewIndexNotFoundError: No review-index file.
  """
  from supekku.scripts.lib.workflow.review_io import (  # noqa: PLC0415
    read_findings,
    read_review_index,
  )
  from supekku.scripts.lib.workflow.review_state_machine import (  # noqa: PLC0415
    can_approve,
    collect_blocking_findings,
  )

  findings_data = read_findings(delta_dir)
  index_data = read_review_index(delta_dir)

  current_round = findings_data["review"]["current_round"]
  judgment_raw = index_data.get("review", {}).get(
    "judgment_status",
    ReviewStatus.NOT_STARTED.value,
  )
  judgment_status = ReviewStatus(judgment_raw)

  # Count findings by category
  blocking_total = 0
  blocking_dispositioned = 0
  non_blocking_total = 0

  for round_data in findings_data.get("rounds", []):
    for f in round_data.get("blocking", []):
      blocking_total += 1
      if f.get("disposition"):
        blocking_dispositioned += 1
    for _f in round_data.get("non_blocking", []):
      non_blocking_total += 1

  # Approval gate check
  blocking = collect_blocking_findings(
    findings_data.get("rounds", []),
  )
  allowed, _reasons = can_approve(blocking)

  # Outcome ready: judgment has reached a terminal state
  outcome_ready = judgment_status not in (
    ReviewStatus.NOT_STARTED,
    ReviewStatus.IN_PROGRESS,
  )

  return ReviewSummary(
    current_round=current_round,
    judgment_status=judgment_status,
    blocking_total=blocking_total,
    blocking_dispositioned=blocking_dispositioned,
    non_blocking_total=non_blocking_total,
    all_blocking_resolved=allowed,
    outcome_ready=outcome_ready,
  )


# ---------------------------------------------------------------------------
# Shared utility
# ---------------------------------------------------------------------------


def _extract_delta_id(delta_dir: Path) -> str:
  """Extract delta ID (e.g. 'DE-124') from a delta directory name."""
  name = delta_dir.name
  parts = name.split("-")
  if len(parts) >= 2:
    return f"{parts[0]}-{parts[1]}".upper()
  return name.upper()
