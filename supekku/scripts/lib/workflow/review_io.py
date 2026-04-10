"""Read and write review-index.yaml and review-findings.yaml.

All mutations go through ``write_review_index`` / ``write_findings``,
which validate output against schemas before writing.  Writes are
atomic (write-to-temp + rename) per DR-102 §5.

Design authority: DR-102 §3.3, §3.4, §5, §8.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import yaml

from supekku.scripts.lib.blocks.metadata.validator import MetadataValidator
from supekku.scripts.lib.blocks.workflow_metadata import (
  REVIEW_FINDINGS_METADATA,
  REVIEW_INDEX_METADATA,
)
from supekku.scripts.lib.core.io import atomic_write
from supekku.scripts.lib.workflow.review_state_machine import (
  FindingDisposition,
  ReviewFinding,
  derive_finding_status,
)

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class ReviewIndexValidationError(Exception):
  """Raised when review-index data fails schema validation."""

  def __init__(self, errors: list) -> None:
    self.errors = errors
    details = "; ".join(str(e) for e in errors[:5])
    super().__init__(f"review-index validation failed: {details}")


class ReviewIndexNotFoundError(Exception):
  """Raised when review-index.yaml does not exist."""


class FindingsValidationError(Exception):
  """Raised when review-findings data fails schema validation."""

  def __init__(self, errors: list) -> None:
    self.errors = errors
    details = "; ".join(str(e) for e in errors[:5])
    super().__init__(f"review-findings validation failed: {details}")


class FindingsNotFoundError(Exception):
  """Raised when review-findings.yaml does not exist."""


class FindingsVersionError(Exception):
  """Raised when review-findings.yaml is v1 (pre-accumulative).

  Recovery: ``review teardown`` + ``review prime`` to start fresh with v2.
  """

  def __init__(self, path: str | Path) -> None:
    super().__init__(
      f"review-findings at {path} is schema v1 (pre-accumulative). "
      "Run 'spec-driver review teardown' then 'spec-driver review prime' "
      "to start fresh with the v2 accumulative model."
    )


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------

_INDEX_VALIDATOR = MetadataValidator(REVIEW_INDEX_METADATA)
_FINDINGS_VALIDATOR = MetadataValidator(REVIEW_FINDINGS_METADATA)

DEFAULT_STATE_DIR = "workflow"
INDEX_FILENAME = "review-index.yaml"
FINDINGS_FILENAME = "review-findings.yaml"
BOOTSTRAP_FILENAME = "review-bootstrap.md"


def _now_iso() -> str:
  """Current UTC timestamp in ISO 8601 format."""
  return datetime.now(tz=UTC).isoformat(timespec="seconds")


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------


def index_path(
  delta_dir: Path,
  state_dir: str = DEFAULT_STATE_DIR,
) -> Path:
  """Return the path to workflow/review-index.yaml."""
  return delta_dir / state_dir / INDEX_FILENAME


def findings_path(
  delta_dir: Path,
  state_dir: str = DEFAULT_STATE_DIR,
) -> Path:
  """Return the path to workflow/review-findings.yaml."""
  return delta_dir / state_dir / FINDINGS_FILENAME


def bootstrap_path(
  delta_dir: Path,
  state_dir: str = DEFAULT_STATE_DIR,
) -> Path:
  """Return the path to workflow/review-bootstrap.md."""
  return delta_dir / state_dir / BOOTSTRAP_FILENAME


# ---------------------------------------------------------------------------
# Atomic write helper
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Review Index I/O
# ---------------------------------------------------------------------------


def read_review_index(
  delta_dir: Path,
  state_dir: str = DEFAULT_STATE_DIR,
) -> dict[str, Any]:
  """Read and validate review-index.yaml.

  Raises:
    ReviewIndexNotFoundError: If the file does not exist.
    ReviewIndexValidationError: If content fails schema validation.
  """
  path = index_path(delta_dir, state_dir)
  if not path.exists():
    raise ReviewIndexNotFoundError(f"review-index not found: {path}")

  data = yaml.safe_load(path.read_text(encoding="utf-8"))
  errors = _INDEX_VALIDATOR.validate(data)
  if errors:
    raise ReviewIndexValidationError(errors)
  return data


def write_review_index(
  delta_dir: Path,
  data: dict[str, Any],
  state_dir: str = DEFAULT_STATE_DIR,
) -> Path:
  """Validate and atomically write review-index.yaml.

  Raises:
    ReviewIndexValidationError: If data fails schema validation.
  """
  errors = _INDEX_VALIDATOR.validate(data)
  if errors:
    raise ReviewIndexValidationError(errors)

  content = yaml.dump(data, default_flow_style=False, sort_keys=False)
  return atomic_write(index_path(delta_dir, state_dir), content)


def build_review_index(
  *,
  artifact_id: str,
  artifact_kind: str = "delta",
  bootstrap_status: str = "warm",
  judgment_status: str | None = None,
  phase_id: str,
  git_head: str,
  domain_map: list[dict[str, Any]],
  session_scope: str | None = None,
  source_handoff: str | None = None,
  invariants: list[dict[str, Any]] | None = None,
  risk_areas: list[dict[str, Any]] | None = None,
  review_focus: list[str] | None = None,
  known_decisions: list[dict[str, Any]] | None = None,
  invalidation_triggers: list[str] | None = None,
) -> dict[str, Any]:
  """Build a review-index payload dict.

  Returns a dict ready for ``write_review_index``.
  """
  now = _now_iso()

  review: dict[str, Any] = {
    "bootstrap_status": bootstrap_status,
    "last_bootstrapped_at": now,
  }
  if judgment_status:
    review["judgment_status"] = judgment_status

  data: dict[str, Any] = {
    "schema": "supekku.workflow.review-index",
    "version": 1,
    "artifact": {
      "id": artifact_id,
      "kind": artifact_kind,
    },
    "review": review,
    "domain_map": domain_map,
    "staleness": {
      "cache_key": {
        "phase_id": phase_id,
        "head": git_head,
      },
    },
  }

  if session_scope:
    data["review"]["session_scope"] = session_scope
  if source_handoff:
    data["review"]["source_handoff"] = source_handoff

  if invariants:
    data["invariants"] = invariants
  if risk_areas:
    data["risk_areas"] = risk_areas
  if review_focus:
    data["review_focus"] = review_focus
  if known_decisions:
    data["known_decisions"] = known_decisions
  if invalidation_triggers:
    staleness = cast(dict[str, Any], data["staleness"])
    staleness["invalidation_triggers"] = invalidation_triggers

  return data


# ---------------------------------------------------------------------------
# Review Findings I/O
# ---------------------------------------------------------------------------


def read_findings(
  delta_dir: Path,
  state_dir: str = DEFAULT_STATE_DIR,
) -> dict[str, Any]:
  """Read and validate review-findings.yaml (v2 only).

  Raises:
    FindingsNotFoundError: If the file does not exist.
    FindingsVersionError: If the file is v1 (pre-accumulative).
    FindingsValidationError: If content fails schema validation.
  """
  path = findings_path(delta_dir, state_dir)
  if not path.exists():
    raise FindingsNotFoundError(f"review-findings not found: {path}")

  data = yaml.safe_load(path.read_text(encoding="utf-8"))

  # Reject v1 files — teardown + re-prime to upgrade (DR-109 §3.5)
  if data.get("version") == 1:
    raise FindingsVersionError(path)

  errors = _FINDINGS_VALIDATOR.validate(data)
  if errors:
    raise FindingsValidationError(errors)

  _rederive_finding_statuses(data)
  return data


def write_findings(
  delta_dir: Path,
  data: dict[str, Any],
  state_dir: str = DEFAULT_STATE_DIR,
) -> Path:
  """Validate and atomically write review-findings.yaml.

  Raises:
    FindingsValidationError: If data fails schema validation.
  """
  errors = _FINDINGS_VALIDATOR.validate(data)
  if errors:
    raise FindingsValidationError(errors)

  content = yaml.dump(data, default_flow_style=False, sort_keys=False)
  return atomic_write(findings_path(delta_dir, state_dir), content)


def build_findings(
  *,
  artifact_id: str,
  artifact_kind: str = "delta",
  round_number: int,
  status: str,
  reviewer_role: str | None = None,
  summary: str | None = None,
  blocking: list[dict[str, Any]] | None = None,
  non_blocking: list[dict[str, Any]] | None = None,
  session: dict[str, Any] | None = None,
) -> dict[str, Any]:
  """Build a v2 review-findings payload with a single round.

  For the first round of a new review. Use ``append_round()`` to add
  subsequent rounds to an existing findings file.
  """
  round_entry = build_round_entry(
    round_number=round_number,
    status=status,
    reviewer_role=reviewer_role,
    summary=summary,
    blocking=blocking,
    non_blocking=non_blocking,
    session=session,
  )

  return {
    "schema": "supekku.workflow.review-findings",
    "version": 2,
    "artifact": {
      "id": artifact_id,
      "kind": artifact_kind,
    },
    "review": {
      "current_round": round_number,
    },
    "rounds": [round_entry],
  }


def build_round_entry(
  *,
  round_number: int,
  status: str,
  reviewer_role: str | None = None,
  summary: str | None = None,
  blocking: list[dict[str, Any]] | None = None,
  non_blocking: list[dict[str, Any]] | None = None,
  session: dict[str, Any] | None = None,
) -> dict[str, Any]:
  """Build a single round entry for the rounds array (DR-109 §3.5)."""
  entry: dict[str, Any] = {
    "round": round_number,
    "status": status,
    "completed_at": _now_iso(),
  }
  if reviewer_role:
    entry["reviewer_role"] = reviewer_role
  if summary:
    entry["summary"] = summary
  if session is not None:
    entry["session"] = session
  entry["blocking"] = blocking or []
  entry["non_blocking"] = non_blocking or []
  return entry


def append_round(
  existing: dict[str, Any],
  *,
  status: str,
  reviewer_role: str | None = None,
  summary: str | None = None,
  blocking: list[dict[str, Any]] | None = None,
  non_blocking: list[dict[str, Any]] | None = None,
  session: dict[str, Any] | None = None,
) -> dict[str, Any]:
  """Append a new round to existing v2 findings (accumulative).

  Returns the mutated findings dict. Does NOT write to disk —
  caller must use ``write_findings()`` after.
  """
  next_num = existing["review"]["current_round"] + 1
  round_entry = build_round_entry(
    round_number=next_num,
    status=status,
    reviewer_role=reviewer_role,
    summary=summary,
    blocking=blocking,
    non_blocking=non_blocking,
    session=session,
  )
  existing["rounds"].append(round_entry)
  existing["review"]["current_round"] = next_num
  return existing


def next_round_number(
  delta_dir: Path,
  state_dir: str = DEFAULT_STATE_DIR,
) -> int:
  """Return the next round number for review findings.

  If no findings exist, returns 1. Otherwise, returns current_round + 1.
  Raises FindingsVersionError on v1 files.
  """
  try:
    data = read_findings(delta_dir, state_dir)
    return data["review"]["current_round"] + 1
  except FindingsNotFoundError:
    return 1


# ---------------------------------------------------------------------------
# Finding status re-derivation (DR-109 §3.4)
# ---------------------------------------------------------------------------


def _rederive_finding_statuses(data: dict[str, Any]) -> None:
  """Re-derive finding statuses from dispositions on read.

  Mutates finding dicts in-place. Status is a convenience projection —
  disposition is authoritative (DR-109 §3.4).
  """
  for round_data in data.get("rounds", []):
    for category in ("blocking", "non_blocking"):
      for finding_dict in round_data.get(category, []):
        raw_disp = finding_dict.get("disposition")
        if raw_disp is not None:
          disp = FindingDisposition.model_validate(raw_disp)
          finding_dict["status"] = derive_finding_status(disp).value
        elif "status" not in finding_dict:
          finding_dict["status"] = "open"


def update_finding_disposition(
  data: dict[str, Any],
  finding_id: str,
  disposition: dict[str, Any],
) -> bool:
  """Update a finding's disposition in-place within its originating round.

  Searches all rounds for the finding by ID, updates disposition and
  re-derives status. Returns True if found, False if not.
  """
  for round_data in data.get("rounds", []):
    for category in ("blocking", "non_blocking"):
      for finding_dict in round_data.get(category, []):
        if finding_dict.get("id") == finding_id:
          finding_dict["disposition"] = disposition
          disp = FindingDisposition.model_validate(disposition)
          finding_dict["status"] = derive_finding_status(disp).value
          return True
  return False


def find_finding(
  data: dict[str, Any],
  finding_id: str,
) -> ReviewFinding | None:
  """Locate a finding by ID across all rounds. Returns None if not found."""
  for round_data in data.get("rounds", []):
    for category in ("blocking", "non_blocking"):
      for finding_dict in round_data.get(category, []):
        if finding_dict.get("id") == finding_id:
          return ReviewFinding.model_validate(finding_dict)
  return None
