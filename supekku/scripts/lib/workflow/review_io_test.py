"""Tests for review I/O (DR-102 §3.3, §3.4, §5)."""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import yaml

from supekku.scripts.lib.workflow.review_io import (
  FindingsNotFoundError,
  FindingsValidationError,
  ReviewIndexNotFoundError,
  ReviewIndexValidationError,
  bootstrap_path,
  build_findings,
  build_review_index,
  findings_path,
  index_path,
  next_round_number,
  read_findings,
  read_review_index,
  write_findings,
  write_review_index,
)

# ---------------------------------------------------------------------------
# Minimal valid payloads
# ---------------------------------------------------------------------------


def _minimal_index() -> dict:
  """Return minimal valid review-index dict."""
  return {
    "schema": "supekku.workflow.review-index",
    "version": 1,
    "artifact": {"id": "DE-090", "kind": "delta"},
    "review": {
      "bootstrap_status": "warm",
      "last_bootstrapped_at": "2026-03-21T10:00:00+00:00",
    },
    "domain_map": [
      {"area": "cli", "purpose": "command routing", "files": ["supekku/cli/main.py"]},
    ],
    "staleness": {
      "cache_key": {
        "phase_id": "IP-090.PHASE-01",
        "head": "abc12345",
      },
    },
  }


def _minimal_findings() -> dict:
  """Return minimal valid review-findings dict."""
  return {
    "schema": "supekku.workflow.review-findings",
    "version": 1,
    "artifact": {"id": "DE-090", "kind": "delta"},
    "review": {
      "round": 1,
      "status": "changes_requested",
    },
    "timestamps": {
      "updated": "2026-03-21T10:00:00+00:00",
    },
  }


# ---------------------------------------------------------------------------
# Path tests
# ---------------------------------------------------------------------------


class PathTest(unittest.TestCase):
  def test_index_path_default(self) -> None:
    assert index_path(Path("/tmp/delta")) == Path(
      "/tmp/delta/workflow/review-index.yaml",
    )

  def test_findings_path_default(self) -> None:
    assert findings_path(Path("/tmp/delta")) == Path(
      "/tmp/delta/workflow/review-findings.yaml",
    )

  def test_bootstrap_path_default(self) -> None:
    assert bootstrap_path(Path("/tmp/delta")) == Path(
      "/tmp/delta/workflow/review-bootstrap.md",
    )


# ---------------------------------------------------------------------------
# Review Index I/O
# ---------------------------------------------------------------------------


class WriteReviewIndexTest(unittest.TestCase):
  def test_write_valid(self) -> None:
    with TemporaryDirectory() as tmp:
      path = write_review_index(Path(tmp), _minimal_index())
      assert path.exists()
      loaded = yaml.safe_load(path.read_text())
      assert loaded["review"]["bootstrap_status"] == "warm"

  def test_write_rejects_invalid(self) -> None:
    with TemporaryDirectory() as tmp, self.assertRaises(ReviewIndexValidationError):
      write_review_index(Path(tmp), {"schema": "supekku.workflow.review-index"})

  def test_atomic_no_temp_files(self) -> None:
    with TemporaryDirectory() as tmp:
      write_review_index(Path(tmp), _minimal_index())
      files = list((Path(tmp) / "workflow").iterdir())
      assert len(files) == 1
      assert files[0].name == "review-index.yaml"


class ReadReviewIndexTest(unittest.TestCase):
  def test_read_valid(self) -> None:
    with TemporaryDirectory() as tmp:
      write_review_index(Path(tmp), _minimal_index())
      data = read_review_index(Path(tmp))
      assert data["artifact"]["id"] == "DE-090"

  def test_read_missing_raises(self) -> None:
    with TemporaryDirectory() as tmp, self.assertRaises(ReviewIndexNotFoundError):
      read_review_index(Path(tmp))


class BuildReviewIndexTest(unittest.TestCase):
  def test_minimal_build(self) -> None:
    data = build_review_index(
      artifact_id="DE-100",
      phase_id="IP-100.PHASE-01",
      git_head="abc12345",
      domain_map=[
        {"area": "cli", "purpose": "commands", "files": ["main.py"]},
      ],
    )
    assert data["schema"] == "supekku.workflow.review-index"
    assert data["review"]["bootstrap_status"] == "warm"
    assert data["staleness"]["cache_key"]["head"] == "abc12345"
    assert "timestamps" not in data  # review-index uses last_bootstrapped_at

  def test_build_validates_on_write(self) -> None:
    with TemporaryDirectory() as tmp:
      data = build_review_index(
        artifact_id="DE-100",
        phase_id="IP-100.PHASE-01",
        git_head="abc12345",
        domain_map=[
          {"area": "workflow", "purpose": "state", "files": ["state.py"]},
        ],
      )
      path = write_review_index(Path(tmp), data)
      assert path.exists()

  def test_build_with_optionals(self) -> None:
    data = build_review_index(
      artifact_id="DE-100",
      phase_id="IP-100.PHASE-01",
      git_head="abc12345",
      domain_map=[
        {"area": "cli", "purpose": "commands", "files": ["main.py"]},
      ],
      session_scope="artifact",
      source_handoff="workflow/handoff.current.yaml",
      invariants=[{"id": "INV-001", "summary": "JSON output stable"}],
      risk_areas=[{"id": "RA-001", "summary": "Reverse lookup"}],
      review_focus=["schema validation"],
      known_decisions=[{"id": "KD-001", "summary": "use uid"}],
      invalidation_triggers=["major_scope_change"],
    )
    assert data["review"]["session_scope"] == "artifact"
    assert len(data["invariants"]) == 1
    assert len(data["risk_areas"]) == 1
    assert len(data["review_focus"]) == 1
    assert len(data["known_decisions"]) == 1
    assert "major_scope_change" in data["staleness"]["invalidation_triggers"]

  def test_build_omits_empty_optionals(self) -> None:
    data = build_review_index(
      artifact_id="DE-100",
      phase_id="IP-100.PHASE-01",
      git_head="abc12345",
      domain_map=[
        {"area": "cli", "purpose": "commands", "files": ["main.py"]},
      ],
    )
    assert "invariants" not in data
    assert "risk_areas" not in data
    assert "review_focus" not in data
    assert "known_decisions" not in data


# ---------------------------------------------------------------------------
# Review Findings I/O
# ---------------------------------------------------------------------------


class WriteFindingsTest(unittest.TestCase):
  def test_write_valid(self) -> None:
    with TemporaryDirectory() as tmp:
      path = write_findings(Path(tmp), _minimal_findings())
      assert path.exists()
      loaded = yaml.safe_load(path.read_text())
      assert loaded["review"]["round"] == 1

  def test_write_rejects_invalid(self) -> None:
    with TemporaryDirectory() as tmp, self.assertRaises(FindingsValidationError):
      write_findings(Path(tmp), {"schema": "supekku.workflow.review-findings"})

  def test_atomic_no_temp_files(self) -> None:
    with TemporaryDirectory() as tmp:
      write_findings(Path(tmp), _minimal_findings())
      files = list((Path(tmp) / "workflow").iterdir())
      assert len(files) == 1
      assert files[0].name == "review-findings.yaml"


class ReadFindingsTest(unittest.TestCase):
  def test_read_valid(self) -> None:
    with TemporaryDirectory() as tmp:
      write_findings(Path(tmp), _minimal_findings())
      data = read_findings(Path(tmp))
      assert data["artifact"]["id"] == "DE-090"

  def test_read_missing_raises(self) -> None:
    with TemporaryDirectory() as tmp, self.assertRaises(FindingsNotFoundError):
      read_findings(Path(tmp))


class BuildFindingsTest(unittest.TestCase):
  def test_minimal_build(self) -> None:
    data = build_findings(
      artifact_id="DE-100",
      round_number=1,
      status="changes_requested",
    )
    assert data["schema"] == "supekku.workflow.review-findings"
    assert data["review"]["round"] == 1
    assert data["review"]["status"] == "changes_requested"
    assert "timestamps" in data

  def test_build_validates_on_write(self) -> None:
    with TemporaryDirectory() as tmp:
      data = build_findings(
        artifact_id="DE-100",
        round_number=1,
        status="approved",
      )
      path = write_findings(Path(tmp), data)
      assert path.exists()

  def test_build_with_findings(self) -> None:
    data = build_findings(
      artifact_id="DE-100",
      round_number=2,
      status="changes_requested",
      reviewer_role="reviewer",
      blocking=[
        {
          "id": "R2-001",
          "title": "Missing validation",
          "summary": "Schema check absent",
          "status": "open",
        },
      ],
      non_blocking=[
        {
          "id": "R2-002",
          "title": "Style nit",
          "summary": "Inconsistent naming",
          "status": "open",
        },
      ],
      resolved=[
        {
          "id": "R1-001",
          "title": "Fixed bug",
          "status": "resolved",
        },
      ],
      history=[
        {"round": 1, "summary": "Initial review"},
      ],
    )
    assert len(data["blocking"]) == 1
    assert len(data["non_blocking"]) == 1
    assert len(data["resolved"]) == 1
    assert len(data["history"]) == 1
    assert data["review"]["reviewer_role"] == "reviewer"

  def test_build_omits_empty_optionals(self) -> None:
    data = build_findings(
      artifact_id="DE-100",
      round_number=1,
      status="approved",
    )
    assert "blocking" not in data
    assert "non_blocking" not in data
    assert "resolved" not in data
    assert "waived" not in data
    assert "history" not in data


# ---------------------------------------------------------------------------
# Round number
# ---------------------------------------------------------------------------


class NextRoundNumberTest(unittest.TestCase):
  def test_no_findings_returns_1(self) -> None:
    with TemporaryDirectory() as tmp:
      assert next_round_number(Path(tmp)) == 1

  def test_increments_from_existing(self) -> None:
    with TemporaryDirectory() as tmp:
      write_findings(Path(tmp), _minimal_findings())  # round=1
      assert next_round_number(Path(tmp)) == 2

  def test_increments_from_round_3(self) -> None:
    with TemporaryDirectory() as tmp:
      data = _minimal_findings()
      data["review"]["round"] = 3
      write_findings(Path(tmp), data)
      assert next_round_number(Path(tmp)) == 4


if __name__ == "__main__":
  unittest.main()
