"""Review lifecycle state machine with explicit transitions and guards.

Implements two sub-lifecycles from DR-109:
  - Bootstrap: derived status with validity invariants (§3.2)
  - Judgment: command-driven state machine (§3.3)

Plus finding disposition model (§3.4) and approval guard (§3.3).

Design authority: DR-109.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict

# ---------------------------------------------------------------------------
# Enums (DR-109 §3.2–§3.4)
# ---------------------------------------------------------------------------


class BootstrapStatus(StrEnum):
  """Bootstrap status values (DR-109 §3.2).

  Derived, not command-driven. The stored value is a snapshot —
  true status comes from observable context.
  """

  COLD = "cold"
  WARM = "warm"
  STALE = "stale"
  REUSABLE = "reusable"
  INVALID = "invalid"


class ReviewStatus(StrEnum):
  """Judgment lifecycle states (DR-109 §3.3)."""

  NOT_STARTED = "not_started"
  IN_PROGRESS = "in_progress"
  APPROVED = "approved"
  CHANGES_REQUESTED = "changes_requested"


class FindingStatus(StrEnum):
  """Finding status — derived from disposition action (DR-109 §3.4)."""

  OPEN = "open"
  RESOLVED = "resolved"
  WAIVED = "waived"
  SUPERSEDED = "superseded"


class FindingDispositionAction(StrEnum):
  """Actions that can be taken on a finding (DR-109 §3.4)."""

  FIX = "fix"
  DEFER = "defer"
  WAIVE = "waive"
  SUPERSEDE = "supersede"


class DispositionAuthority(StrEnum):
  """Who made the disposition decision (DR-109 §3.4)."""

  USER = "user"
  AGENT = "agent"


class ReviewTransitionCommand(StrEnum):
  """Judgment transition commands (DR-109 §3.3)."""

  BEGIN_REVIEW = "begin_review"
  APPROVE = "approve"
  REQUEST_CHANGES = "request_changes"


# ---------------------------------------------------------------------------
# Pydantic models (DR-109 §3.4)
# ---------------------------------------------------------------------------


class FindingDisposition(BaseModel):
  """Structured disposition record for a review finding."""

  model_config = ConfigDict(extra="ignore")

  action: FindingDispositionAction
  authority: DispositionAuthority
  actor_id: str | None = None
  rationale: str | None = None
  backlog_ref: str | None = None
  resolved_at: str | None = None
  superseded_by: str | None = None
  timestamp: str | None = None


class ReviewFinding(BaseModel):
  """A single review finding with optional disposition."""

  model_config = ConfigDict(extra="ignore")

  id: str
  title: str
  summary: str | None = None
  status: FindingStatus = FindingStatus.OPEN
  disposition: FindingDisposition | None = None


# ---------------------------------------------------------------------------
# Bootstrap validity matrix (DR-109 §3.2)
# ---------------------------------------------------------------------------

_BS = BootstrapStatus

VALID_BOOTSTRAP_TRANSITIONS: set[tuple[BootstrapStatus, BootstrapStatus]] = {
  (_BS.COLD, _BS.COLD),  # idempotent re-derivation (no index)
  (_BS.COLD, _BS.WARM),  # prime: fresh build
  (_BS.WARM, _BS.WARM),  # re-prime (idempotent) or no drift
  (_BS.WARM, _BS.STALE),  # drift detected
  (_BS.STALE, _BS.WARM),  # re-prime after staleness
  (_BS.STALE, _BS.STALE),  # idempotent re-derivation (still stale)
  (_BS.STALE, _BS.INVALID),  # invalidation detected
  (_BS.STALE, _BS.REUSABLE),  # minor drift only
  (_BS.REUSABLE, _BS.WARM),  # prime: incremental update
  (_BS.INVALID, _BS.WARM),  # prime: full rebuild
  (_BS.INVALID, _BS.INVALID),  # idempotent re-derivation (still invalid)
}


# ---------------------------------------------------------------------------
# Judgment transition table (DR-109 §3.3)
# ---------------------------------------------------------------------------

_RS = ReviewStatus
_RC = ReviewTransitionCommand

_REVIEW_TRANSITIONS: dict[
  tuple[ReviewStatus, ReviewTransitionCommand], ReviewStatus
] = {
  (_RS.NOT_STARTED, _RC.BEGIN_REVIEW): _RS.IN_PROGRESS,
  (_RS.IN_PROGRESS, _RC.APPROVE): _RS.APPROVED,
  (_RS.IN_PROGRESS, _RC.REQUEST_CHANGES): _RS.CHANGES_REQUESTED,
  (_RS.CHANGES_REQUESTED, _RC.BEGIN_REVIEW): _RS.IN_PROGRESS,
}


class ReviewTransitionError(Exception):
  """Raised when a review judgment transition is invalid."""

  def __init__(
    self,
    current: ReviewStatus,
    command: ReviewTransitionCommand,
    message: str = "",
  ) -> None:
    self.current = current
    self.command = command
    detail = f": {message}" if message else ""
    super().__init__(
      f"invalid review transition: cannot apply {command.value} "
      f"in state {current.value}{detail}"
    )


# ---------------------------------------------------------------------------
# Status derivation (DR-109 §3.4)
# ---------------------------------------------------------------------------

_STATUS_FROM_ACTION: dict[FindingDispositionAction, FindingStatus] = {
  FindingDispositionAction.FIX: FindingStatus.RESOLVED,
  FindingDispositionAction.DEFER: FindingStatus.OPEN,
  FindingDispositionAction.WAIVE: FindingStatus.WAIVED,
  FindingDispositionAction.SUPERSEDE: FindingStatus.SUPERSEDED,
}


def derive_finding_status(
  disposition: FindingDisposition | None,
) -> FindingStatus:
  """Derive finding status from disposition action.

  Status is a convenience projection — disposition is authoritative.
  """
  if disposition is None:
    return FindingStatus.OPEN
  return _STATUS_FROM_ACTION[disposition.action]


# ---------------------------------------------------------------------------
# Bootstrap derivation (DR-109 §3.2)
# ---------------------------------------------------------------------------


def derive_bootstrap_status(
  index: dict | None,
  *,
  current_phase_id: str,
  current_head: str,
  changed_files: list[str] | None = None,
  deleted_domain_files: list[str] | None = None,
  previous_status: BootstrapStatus | None = None,
) -> BootstrapStatus:
  """Derive current bootstrap status from observable context.

  Deterministic — no I/O, no mutation. The only code that writes
  bootstrap_status is review prime, which always writes WARM.

  When previous_status is provided, raises AssertionError if the
  derived transition is illegal (indicates a derivation logic bug).
  """
  if index is None:
    derived = BootstrapStatus.COLD
  else:
    derived = _derive_from_index(
      index,
      current_phase_id=current_phase_id,
      current_head=current_head,
      changed_files=changed_files,
      deleted_domain_files=deleted_domain_files,
    )

  if previous_status is not None:
    pair = (previous_status, derived)
    assert pair in VALID_BOOTSTRAP_TRANSITIONS, (
      f"illegal bootstrap transition: {previous_status.value} → {derived.value}"
    )

  return derived


def _derive_from_index(
  index: dict,
  *,
  current_phase_id: str,
  current_head: str,
  changed_files: list[str] | None = None,
  deleted_domain_files: list[str] | None = None,
) -> BootstrapStatus:
  """Derive status from an existing review-index.

  Mirrors the staleness evaluation logic from staleness.py but
  returns a BootstrapStatus rather than StalenessResult.
  """
  cache_key = index.get("staleness", {}).get("cache_key", {})
  cached_phase = cache_key.get("phase_id", "")
  cached_head = cache_key.get("head", "")

  # Check invalidation first (most severe)
  if index.get("version") != 1:
    return BootstrapStatus.INVALID
  if index.get("schema") != "supekku.workflow.review-index":
    return BootstrapStatus.INVALID
  if deleted_domain_files:
    return BootstrapStatus.INVALID

  # Detect staleness triggers
  triggers: list[str] = []
  if cached_head != current_head:
    triggers.append("commit_drift")
  if cached_phase != current_phase_id:
    triggers.append("phase_boundary_crossing")
  if changed_files:
    cached_files = _extract_cached_files(index)
    new_files = set(changed_files) - cached_files
    if new_files:
      triggers.append("dependency_surface_expansion")

  if not triggers:
    return BootstrapStatus.WARM

  # Check reusability (minor staleness only)
  severe = {"phase_boundary_crossing", "dependency_surface_expansion"}
  if not (severe & set(triggers)) and (
    not changed_files or set(changed_files).issubset(_extract_cached_files(index))
  ):
    return BootstrapStatus.REUSABLE

  return BootstrapStatus.STALE


def _extract_cached_files(index: dict) -> set[str]:
  """Extract file paths from cached domain_map."""
  files: set[str] = set()
  for entry in index.get("domain_map", []):
    files.update(entry.get("files", []))
  return files


# ---------------------------------------------------------------------------
# Judgment transitions (DR-109 §3.3)
# ---------------------------------------------------------------------------


def apply_review_transition(
  current: ReviewStatus,
  command: ReviewTransitionCommand,
) -> ReviewStatus:
  """Apply a judgment transition command.

  Returns the new ReviewStatus.

  Raises:
    ReviewTransitionError: If the transition is invalid.
  """
  key = (current, command)
  target = _REVIEW_TRANSITIONS.get(key)
  if target is None:
    raise ReviewTransitionError(current, command)
  return target


# ---------------------------------------------------------------------------
# Approval guard (DR-109 §3.3)
# ---------------------------------------------------------------------------


def can_approve(
  blocking_findings: list[ReviewFinding],
) -> tuple[bool, list[str]]:
  """Check whether approval is permitted.

  Evaluates disposition constraints on all blocking findings.
  The guard checks disposition, not status — status is derived from
  disposition and checking both creates short-circuit bugs.

  Returns (allowed, reasons) where reasons lists blocking violations.
  """
  reasons: list[str] = []
  for f in blocking_findings:
    if f.disposition is None:
      reasons.append(f"blocking finding {f.id} has no disposition")
    else:
      reasons.extend(_check_disposition(f.id, f.disposition))
  return (not reasons, reasons)


def _check_disposition(
  finding_id: str,
  d: FindingDisposition,
) -> list[str]:
  """Validate a single finding's disposition for approval."""
  reasons: list[str] = []
  if d.action == FindingDispositionAction.FIX:
    if not d.resolved_at:
      reasons.append(
        f"blocking finding {finding_id} marked fixed without resolved_at sha"
      )
  elif d.action == FindingDispositionAction.WAIVE:
    if d.authority != DispositionAuthority.USER:
      reasons.append(f"blocking finding {finding_id} waived without user authority")
    if not d.rationale:
      reasons.append(f"blocking finding {finding_id} waived without rationale")
  elif d.action == FindingDispositionAction.DEFER:
    if d.authority != DispositionAuthority.USER:
      reasons.append(f"blocking finding {finding_id} deferred without user authority")
    if not d.backlog_ref:
      reasons.append(
        f"blocking finding {finding_id} deferred without backlog reference"
      )
  return reasons


# ---------------------------------------------------------------------------
# Cross-round collection (DR-109 §3.7)
# ---------------------------------------------------------------------------


def collect_blocking_findings(
  rounds: list[dict],
) -> list[ReviewFinding]:
  """Collect all blocking findings from all rounds.

  Finding IDs are round-scoped (R{round}-{seq}) and unique across
  rounds — no deduplication is needed. Dispositions are applied
  in-place within the originating round, so each finding's current
  disposition state is always in its originating entry.
  """
  findings: list[ReviewFinding] = []
  for round_data in rounds:
    for raw in round_data.get("blocking", []):
      findings.append(ReviewFinding.model_validate(raw))
  return findings
