"""Tests for review I/O (DR-102 §3.3/§3.4/§5, DR-109 §3.3/§3.5).

Covers: v2 accumulative rounds (VT-109-004), v1 rejection (VA-109-001),
judgment_status in review-index, and finding status re-derivation.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import yaml

from supekku.scripts.lib.workflow.review_io import (
  FindingsNotFoundError,
  FindingsValidationError,
  FindingsVersionError,
  ReviewIndexNotFoundError,
  ReviewIndexValidationError,
  append_round,
  bootstrap_path,
  build_findings,
  build_review_index,
  build_round_entry,
  find_finding,
  findings_path,
  index_path,
  next_round_number,
  read_findings,
  read_review_index,
  update_finding_disposition,
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
      {
        "area": "cli",
        "purpose": "command routing",
        "files": ["supekku/cli/main.py"],
      },
    ],
    "staleness": {
      "cache_key": {
        "phase_id": "IP-090.PHASE-01",
        "head": "abc12345",
      },
    },
  }


def _minimal_findings_v2() -> dict:
  """Return minimal valid v2 review-findings dict."""
  return {
    "schema": "supekku.workflow.review-findings",
    "version": 2,
    "artifact": {"id": "DE-090", "kind": "delta"},
    "review": {"current_round": 1},
    "rounds": [
      {
        "round": 1,
        "status": "changes_requested",
        "completed_at": "2026-03-21T10:00:00+00:00",
        "blocking": [],
        "non_blocking": [],
      }
    ],
  }


def _v1_findings() -> dict:
  """Return a v1 review-findings dict (pre-accumulative)."""
  return {
    "schema": "supekku.workflow.review-findings",
    "version": 1,
    "artifact": {"id": "DE-090", "kind": "delta"},
    "review": {"round": 1, "status": "changes_requested"},
    "timestamps": {"updated": "2026-03-21T10:00:00+00:00"},
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
    with (
      TemporaryDirectory() as tmp,
      self.assertRaises(ReviewIndexValidationError),
    ):
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
    with (
      TemporaryDirectory() as tmp,
      self.assertRaises(ReviewIndexNotFoundError),
    ):
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

  def test_build_with_judgment_status(self) -> None:
    data = build_review_index(
      artifact_id="DE-100",
      phase_id="IP-100.PHASE-01",
      git_head="abc12345",
      domain_map=[
        {"area": "cli", "purpose": "commands", "files": ["main.py"]},
      ],
      judgment_status="in_progress",
    )
    assert data["review"]["judgment_status"] == "in_progress"

  def test_build_without_judgment_status(self) -> None:
    data = build_review_index(
      artifact_id="DE-100",
      phase_id="IP-100.PHASE-01",
      git_head="abc12345",
      domain_map=[
        {"area": "cli", "purpose": "commands", "files": ["main.py"]},
      ],
    )
    assert "judgment_status" not in data["review"]

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
# VA-109-001: Schema v1 rejection
# ---------------------------------------------------------------------------


class FindingsVersionTest(unittest.TestCase):
  def test_v1_raises_findings_version_error(self) -> None:
    """v1 files are rejected with clear error directing to teardown."""
    with TemporaryDirectory() as tmp:
      path = findings_path(Path(tmp))
      path.parent.mkdir(parents=True, exist_ok=True)
      path.write_text(yaml.dump(_v1_findings()))
      with self.assertRaises(FindingsVersionError) as ctx:
        read_findings(Path(tmp))
      assert "teardown" in str(ctx.exception).lower()
      assert "prime" in str(ctx.exception).lower()

  def test_v1_error_includes_path(self) -> None:
    with TemporaryDirectory() as tmp:
      path = findings_path(Path(tmp))
      path.parent.mkdir(parents=True, exist_ok=True)
      path.write_text(yaml.dump(_v1_findings()))
      with self.assertRaises(FindingsVersionError) as ctx:
        read_findings(Path(tmp))
      assert str(path) in str(ctx.exception)


# ---------------------------------------------------------------------------
# VT-109-004: Accumulative rounds read/write
# ---------------------------------------------------------------------------


class WriteFindingsV2Test(unittest.TestCase):
  def test_write_valid_v2(self) -> None:
    with TemporaryDirectory() as tmp:
      path = write_findings(Path(tmp), _minimal_findings_v2())
      assert path.exists()
      loaded = yaml.safe_load(path.read_text())
      assert loaded["version"] == 2
      assert loaded["review"]["current_round"] == 1
      assert len(loaded["rounds"]) == 1

  def test_write_rejects_invalid(self) -> None:
    with (
      TemporaryDirectory() as tmp,
      self.assertRaises(FindingsValidationError),
    ):
      write_findings(Path(tmp), {"schema": "supekku.workflow.review-findings"})

  def test_atomic_no_temp_files(self) -> None:
    with TemporaryDirectory() as tmp:
      write_findings(Path(tmp), _minimal_findings_v2())
      files = list((Path(tmp) / "workflow").iterdir())
      assert len(files) == 1
      assert files[0].name == "review-findings.yaml"


class ReadFindingsV2Test(unittest.TestCase):
  def test_read_valid_v2(self) -> None:
    with TemporaryDirectory() as tmp:
      write_findings(Path(tmp), _minimal_findings_v2())
      data = read_findings(Path(tmp))
      assert data["artifact"]["id"] == "DE-090"
      assert data["review"]["current_round"] == 1

  def test_read_missing_raises(self) -> None:
    with (
      TemporaryDirectory() as tmp,
      self.assertRaises(FindingsNotFoundError),
    ):
      read_findings(Path(tmp))


class BuildFindingsV2Test(unittest.TestCase):
  def test_minimal_build(self) -> None:
    data = build_findings(
      artifact_id="DE-100",
      round_number=1,
      status="changes_requested",
    )
    assert data["schema"] == "supekku.workflow.review-findings"
    assert data["version"] == 2
    assert data["review"]["current_round"] == 1
    assert len(data["rounds"]) == 1
    assert data["rounds"][0]["round"] == 1
    assert data["rounds"][0]["status"] == "changes_requested"

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
      round_number=1,
      status="changes_requested",
      reviewer_role="reviewer",
      blocking=[
        {
          "id": "R1-001",
          "title": "Missing validation",
          "summary": "Schema check absent",
          "status": "open",
        },
      ],
      non_blocking=[
        {
          "id": "R1-002",
          "title": "Style nit",
          "summary": "Inconsistent naming",
          "status": "open",
        },
      ],
    )
    round_entry = data["rounds"][0]
    assert len(round_entry["blocking"]) == 1
    assert len(round_entry["non_blocking"]) == 1
    assert round_entry["reviewer_role"] == "reviewer"

  def test_build_with_session(self) -> None:
    session = {"agent_id": "autobahn-v1", "harness": "pytest"}
    data = build_findings(
      artifact_id="DE-100",
      round_number=1,
      status="in_progress",
      session=session,
    )
    assert data["rounds"][0]["session"] == session

  def test_build_omits_empty_session(self) -> None:
    data = build_findings(
      artifact_id="DE-100",
      round_number=1,
      status="approved",
    )
    assert "session" not in data["rounds"][0]


class AppendRoundTest(unittest.TestCase):
  def test_append_preserves_prior_rounds(self) -> None:
    data = build_findings(
      artifact_id="DE-100",
      round_number=1,
      status="changes_requested",
      blocking=[{"id": "R1-001", "title": "Issue", "status": "open"}],
    )
    append_round(
      data,
      status="approved",
      blocking=[],
    )
    assert data["review"]["current_round"] == 2
    assert len(data["rounds"]) == 2
    # Round 1 preserved
    assert data["rounds"][0]["round"] == 1
    assert data["rounds"][0]["status"] == "changes_requested"
    assert len(data["rounds"][0]["blocking"]) == 1
    # Round 2 appended
    assert data["rounds"][1]["round"] == 2
    assert data["rounds"][1]["status"] == "approved"

  def test_append_multiple_rounds(self) -> None:
    data = build_findings(
      artifact_id="DE-100",
      round_number=1,
      status="changes_requested",
    )
    append_round(data, status="changes_requested")
    append_round(data, status="approved")
    assert data["review"]["current_round"] == 3
    assert len(data["rounds"]) == 3
    assert [r["round"] for r in data["rounds"]] == [1, 2, 3]

  def test_append_writes_validly(self) -> None:
    with TemporaryDirectory() as tmp:
      data = build_findings(
        artifact_id="DE-100",
        round_number=1,
        status="changes_requested",
      )
      append_round(data, status="approved")
      path = write_findings(Path(tmp), data)
      reread = read_findings(Path(tmp))
      assert reread["review"]["current_round"] == 2
      assert len(reread["rounds"]) == 2
      assert path.exists()


class BuildRoundEntryTest(unittest.TestCase):
  def test_minimal_round(self) -> None:
    entry = build_round_entry(round_number=1, status="in_progress")
    assert entry["round"] == 1
    assert entry["status"] == "in_progress"
    assert "completed_at" in entry
    assert entry["blocking"] == []
    assert entry["non_blocking"] == []

  def test_round_with_findings(self) -> None:
    entry = build_round_entry(
      round_number=2,
      status="changes_requested",
      reviewer_role="reviewer",
      blocking=[{"id": "R2-001", "title": "Bug", "status": "open"}],
    )
    assert len(entry["blocking"]) == 1
    assert entry["reviewer_role"] == "reviewer"


# ---------------------------------------------------------------------------
# Round number
# ---------------------------------------------------------------------------


class NextRoundNumberTest(unittest.TestCase):
  def test_no_findings_returns_1(self) -> None:
    with TemporaryDirectory() as tmp:
      assert next_round_number(Path(tmp)) == 1

  def test_increments_from_existing_v2(self) -> None:
    with TemporaryDirectory() as tmp:
      write_findings(Path(tmp), _minimal_findings_v2())  # current_round=1
      assert next_round_number(Path(tmp)) == 2

  def test_increments_from_round_3(self) -> None:
    with TemporaryDirectory() as tmp:
      data = _minimal_findings_v2()
      data["review"]["current_round"] = 3
      data["rounds"][0]["round"] = 3
      write_findings(Path(tmp), data)
      assert next_round_number(Path(tmp)) == 4


# ---------------------------------------------------------------------------
# Finding status re-derivation (DR-109 §3.4)
# ---------------------------------------------------------------------------


class StatusRederivationTest(unittest.TestCase):
  """Status is re-derived from disposition on read."""

  def test_fix_rederives_to_resolved(self) -> None:
    with TemporaryDirectory() as tmp:
      data = _minimal_findings_v2()
      data["rounds"][0]["blocking"] = [
        {
          "id": "R1-001",
          "title": "Fixed issue",
          "status": "open",  # stale — should be resolved
          "disposition": {
            "action": "fix",
            "authority": "agent",
            "resolved_at": "abc1234",
          },
        }
      ]
      write_findings(Path(tmp), data)
      reread = read_findings(Path(tmp))
      finding = reread["rounds"][0]["blocking"][0]
      assert finding["status"] == "resolved"

  def test_no_disposition_stays_open(self) -> None:
    with TemporaryDirectory() as tmp:
      data = _minimal_findings_v2()
      data["rounds"][0]["blocking"] = [
        {"id": "R1-001", "title": "Open issue", "status": "open"}
      ]
      write_findings(Path(tmp), data)
      reread = read_findings(Path(tmp))
      assert reread["rounds"][0]["blocking"][0]["status"] == "open"

  def test_defer_rederives_to_open(self) -> None:
    with TemporaryDirectory() as tmp:
      data = _minimal_findings_v2()
      data["rounds"][0]["blocking"] = [
        {
          "id": "R1-001",
          "title": "Deferred",
          "status": "waived",  # wrong — should be open
          "disposition": {
            "action": "defer",
            "authority": "user",
            "backlog_ref": "ISSUE-047",
          },
        }
      ]
      write_findings(Path(tmp), data)
      reread = read_findings(Path(tmp))
      assert reread["rounds"][0]["blocking"][0]["status"] == "open"


# ---------------------------------------------------------------------------
# Finding disposition update and lookup
# ---------------------------------------------------------------------------


class UpdateFindingDispositionTest(unittest.TestCase):
  def test_updates_in_originating_round(self) -> None:
    data = _minimal_findings_v2()
    data["rounds"][0]["blocking"] = [
      {"id": "R1-001", "title": "Issue", "status": "open"}
    ]
    found = update_finding_disposition(
      data,
      "R1-001",
      {"action": "fix", "authority": "agent", "resolved_at": "abc"},
    )
    assert found is True
    finding = data["rounds"][0]["blocking"][0]
    assert finding["disposition"]["action"] == "fix"
    assert finding["status"] == "resolved"

  def test_not_found_returns_false(self) -> None:
    data = _minimal_findings_v2()
    found = update_finding_disposition(
      data, "NONEXISTENT", {"action": "fix", "authority": "agent"}
    )
    assert found is False

  def test_updates_across_rounds(self) -> None:
    data = build_findings(
      artifact_id="DE-100",
      round_number=1,
      status="changes_requested",
      blocking=[{"id": "R1-001", "title": "Issue", "status": "open"}],
    )
    append_round(data, status="in_progress")
    found = update_finding_disposition(
      data,
      "R1-001",
      {
        "action": "waive",
        "authority": "user",
        "rationale": "Acceptable risk",
      },
    )
    assert found is True
    # Updated in round 1 (originating round), not round 2
    finding = data["rounds"][0]["blocking"][0]
    assert finding["disposition"]["action"] == "waive"
    assert finding["status"] == "waived"


class FindFindingTest(unittest.TestCase):
  def test_finds_in_blocking(self) -> None:
    data = _minimal_findings_v2()
    data["rounds"][0]["blocking"] = [
      {"id": "R1-001", "title": "Issue", "status": "open"}
    ]
    result = find_finding(data, "R1-001")
    assert result is not None
    assert result.id == "R1-001"

  def test_finds_in_non_blocking(self) -> None:
    data = _minimal_findings_v2()
    data["rounds"][0]["non_blocking"] = [
      {"id": "R1-002", "title": "Nit", "status": "open"}
    ]
    result = find_finding(data, "R1-002")
    assert result is not None

  def test_not_found_returns_none(self) -> None:
    data = _minimal_findings_v2()
    assert find_finding(data, "NONEXISTENT") is None

  def test_finds_across_rounds(self) -> None:
    data = build_findings(
      artifact_id="DE-100",
      round_number=1,
      status="changes_requested",
      blocking=[{"id": "R1-001", "title": "Issue", "status": "open"}],
    )
    append_round(
      data,
      status="in_progress",
      blocking=[{"id": "R2-001", "title": "New issue", "status": "open"}],
    )
    assert find_finding(data, "R1-001") is not None
    assert find_finding(data, "R2-001") is not None


if __name__ == "__main__":
  unittest.main()
