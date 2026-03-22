"""Review operations for spec-driver orchestration layer.

Stubs — to be implemented by DE-124.
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
# New exceptions (DE-124)
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
    super().__init__(
      "Cannot approve: " + "; ".join(reasons)
    )


class FindingNotFoundError(Exception):
  """Raised when a finding ID doesn't exist in any round."""

  def __init__(
    self, finding_id: str, available: list[str]
  ) -> None:
    self.finding_id = finding_id
    self.available = available
    super().__init__(
      f"Finding {finding_id} not found. "
      f"Available: {', '.join(available)}"
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
# Stub operations — DE-124 Phase 1 fills these in
# ---------------------------------------------------------------------------


def resolve_delta_dir(
  delta_id: str, repo_root: Path,
) -> Path:
  """Locate a delta bundle directory by ID."""
  raise NotImplementedError("DE-124 Phase 1")


def prime_review(
  delta_dir: Path, repo_root: Path,
) -> PrimeResult:
  """Orchestrate review priming."""
  raise NotImplementedError("DE-124 Phase 1")


def complete_review(
  delta_dir: Path,
  repo_root: Path,
  *,
  status: ReviewStatus,
  summary: str | None = None,
  auto_teardown: bool = True,
) -> CompleteResult:
  """Complete a review round."""
  raise NotImplementedError("DE-124 Phase 1")


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
  """Disposition a review finding."""
  raise NotImplementedError("DE-124 Phase 1")


def teardown_review(delta_dir: Path) -> TeardownResult:
  """Delete reviewer state files."""
  raise NotImplementedError("DE-124 Phase 1")


def summarize_review(delta_dir: Path) -> ReviewSummary:
  """Read-only query: what happened in the review?"""
  raise NotImplementedError("DE-124 Phase 1")
