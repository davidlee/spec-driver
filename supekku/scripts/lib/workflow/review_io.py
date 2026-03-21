"""Read and write review-index.yaml and review-findings.yaml.

All mutations go through ``write_review_index`` / ``write_findings``,
which validate output against schemas before writing.  Writes are
atomic (write-to-temp + rename) per DR-102 §5.

Design authority: DR-102 §3.3, §3.4, §5, §8.
"""

from __future__ import annotations

import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from supekku.scripts.lib.blocks.metadata.validator import MetadataValidator
from supekku.scripts.lib.blocks.workflow_metadata import (
  REVIEW_FINDINGS_METADATA,
  REVIEW_INDEX_METADATA,
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


def _atomic_write(path: Path, content: str) -> Path:
  """Write content atomically via temp-file + rename."""
  path.parent.mkdir(parents=True, exist_ok=True)
  fd, tmp = tempfile.mkstemp(
    dir=path.parent, suffix=".tmp", prefix=path.stem + "_",
  )
  closed = False
  try:
    os.write(fd, content.encode("utf-8"))
    os.close(fd)
    closed = True
    Path(tmp).replace(path)
  except BaseException:
    if not closed:
      os.close(fd)
    tmp_path = Path(tmp)
    if tmp_path.exists():
      tmp_path.unlink()
    raise
  return path


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
  return _atomic_write(index_path(delta_dir, state_dir), content)


def build_review_index(
  *,
  artifact_id: str,
  artifact_kind: str = "delta",
  bootstrap_status: str = "warm",
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

  data: dict[str, Any] = {
    "schema": "supekku.workflow.review-index",
    "version": 1,
    "artifact": {
      "id": artifact_id,
      "kind": artifact_kind,
    },
    "review": {
      "bootstrap_status": bootstrap_status,
      "last_bootstrapped_at": now,
    },
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
    data["staleness"]["invalidation_triggers"] = invalidation_triggers

  return data


# ---------------------------------------------------------------------------
# Review Findings I/O
# ---------------------------------------------------------------------------


def read_findings(
  delta_dir: Path,
  state_dir: str = DEFAULT_STATE_DIR,
) -> dict[str, Any]:
  """Read and validate review-findings.yaml.

  Raises:
    FindingsNotFoundError: If the file does not exist.
    FindingsValidationError: If content fails schema validation.
  """
  path = findings_path(delta_dir, state_dir)
  if not path.exists():
    raise FindingsNotFoundError(f"review-findings not found: {path}")

  data = yaml.safe_load(path.read_text(encoding="utf-8"))
  errors = _FINDINGS_VALIDATOR.validate(data)
  if errors:
    raise FindingsValidationError(errors)
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
  return _atomic_write(findings_path(delta_dir, state_dir), content)


def build_findings(
  *,
  artifact_id: str,
  artifact_kind: str = "delta",
  round_number: int,
  status: str,
  reviewer_role: str | None = None,
  blocking: list[dict[str, Any]] | None = None,
  non_blocking: list[dict[str, Any]] | None = None,
  resolved: list[dict[str, Any]] | None = None,
  waived: list[dict[str, Any]] | None = None,
  history: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
  """Build a review-findings payload dict.

  Returns a dict ready for ``write_findings``.
  """
  data: dict[str, Any] = {
    "schema": "supekku.workflow.review-findings",
    "version": 1,
    "artifact": {
      "id": artifact_id,
      "kind": artifact_kind,
    },
    "review": {
      "round": round_number,
      "status": status,
    },
    "timestamps": {
      "updated": _now_iso(),
    },
  }

  if reviewer_role:
    data["review"]["reviewer_role"] = reviewer_role

  if blocking:
    data["blocking"] = blocking
  if non_blocking:
    data["non_blocking"] = non_blocking
  if resolved:
    data["resolved"] = resolved
  if waived:
    data["waived"] = waived
  if history:
    data["history"] = history

  return data


def next_round_number(
  delta_dir: Path,
  state_dir: str = DEFAULT_STATE_DIR,
) -> int:
  """Return the next round number for review findings.

  If no findings exist, returns 1. Otherwise, returns current round + 1.
  """
  try:
    data = read_findings(delta_dir, state_dir)
    return data["review"]["round"] + 1
  except FindingsNotFoundError:
    return 1
  except FindingsValidationError:
    # Corrupt findings — start fresh
    return 1
