"""Tests for staleness evaluation (DR-102 §8)."""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from supekku.scripts.lib.workflow.review_state_machine import BootstrapStatus
from supekku.scripts.lib.workflow.staleness import (
  check_domain_map_files_exist,
  evaluate_staleness,
)


def _cached_index(
  *,
  phase_id: str = "IP-090.PHASE-01",
  head: str = "abc12345",
  bootstrapped_at: str = "2026-03-21T10:00:00+00:00",
  files: list[str] | None = None,
) -> dict:
  """Return a cached review-index for testing."""
  return {
    "schema": "supekku.workflow.review-index",
    "version": 1,
    "artifact": {"id": "DE-090", "kind": "delta"},
    "review": {
      "bootstrap_status": "warm",
      "last_bootstrapped_at": bootstrapped_at,
    },
    "domain_map": [
      {
        "area": "cli",
        "purpose": "commands",
        "files": files or ["supekku/cli/main.py", "supekku/cli/workflow.py"],
      },
    ],
    "staleness": {
      "cache_key": {
        "phase_id": phase_id,
        "head": head,
      },
    },
  }


class EvaluateStalenessTest(unittest.TestCase):
  """Test staleness evaluation per DR-102 §8."""

  def test_warm_when_nothing_changed(self) -> None:
    result = evaluate_staleness(
      _cached_index(),
      current_phase_id="IP-090.PHASE-01",
      current_head="abc12345",
    )
    assert result.status == BootstrapStatus.WARM
    assert result.triggers == []

  def test_stale_on_commit_drift(self) -> None:
    result = evaluate_staleness(
      _cached_index(),
      current_phase_id="IP-090.PHASE-01",
      current_head="def67890",
    )
    assert result.status in (BootstrapStatus.STALE, BootstrapStatus.REUSABLE)
    assert "commit_drift" in result.triggers

  def test_stale_on_phase_boundary_crossing(self) -> None:
    result = evaluate_staleness(
      _cached_index(),
      current_phase_id="IP-090.PHASE-02",
      current_head="abc12345",
    )
    assert result.status == BootstrapStatus.STALE
    assert "phase_boundary_crossing" in result.triggers

  def test_stale_on_major_scope_change(self) -> None:
    result = evaluate_staleness(
      _cached_index(bootstrapped_at="2026-03-20T10:00:00+00:00"),
      current_phase_id="IP-090.PHASE-01",
      current_head="abc12345",
      delta_updated="2026-03-21T12:00:00+00:00",
    )
    assert "major_scope_change" in result.triggers

  def test_stale_on_dependency_surface_expansion(self) -> None:
    result = evaluate_staleness(
      _cached_index(),
      current_phase_id="IP-090.PHASE-01",
      current_head="abc12345",
      changed_files=["supekku/new_module.py"],
    )
    assert "dependency_surface_expansion" in result.triggers

  def test_no_surface_expansion_for_known_files(self) -> None:
    result = evaluate_staleness(
      _cached_index(),
      current_phase_id="IP-090.PHASE-01",
      current_head="abc12345",
      changed_files=["supekku/cli/main.py"],
    )
    assert "dependency_surface_expansion" not in result.triggers

  def test_reusable_on_commit_drift_only(self) -> None:
    """Commit drift alone makes cache reusable, not stale."""
    result = evaluate_staleness(
      _cached_index(),
      current_phase_id="IP-090.PHASE-01",
      current_head="def67890",
    )
    assert result.status == BootstrapStatus.REUSABLE
    assert result.can_incremental_update is True
    assert "commit_drift" in result.triggers

  def test_not_reusable_on_phase_crossing(self) -> None:
    """Phase boundary crossing prevents reusability."""
    result = evaluate_staleness(
      _cached_index(),
      current_phase_id="IP-090.PHASE-02",
      current_head="abc12345",
    )
    assert result.status == BootstrapStatus.STALE
    assert result.can_incremental_update is False

  def test_not_reusable_on_surface_expansion(self) -> None:
    """Dependency surface expansion prevents reusability."""
    result = evaluate_staleness(
      _cached_index(),
      current_phase_id="IP-090.PHASE-01",
      current_head="def67890",
      changed_files=["supekku/new_module.py"],
    )
    assert result.status == BootstrapStatus.STALE
    assert result.can_incremental_update is False

  def test_invalid_on_schema_version_mismatch(self) -> None:
    cached = _cached_index()
    cached["version"] = 99
    result = evaluate_staleness(
      cached,
      current_phase_id="IP-090.PHASE-01",
      current_head="def67890",
    )
    assert result.status == BootstrapStatus.INVALID
    assert "schema_version_mismatch" in result.triggers

  def test_invalid_on_schema_id_mismatch(self) -> None:
    cached = _cached_index()
    cached["schema"] = "wrong.schema"
    result = evaluate_staleness(
      cached,
      current_phase_id="IP-090.PHASE-01",
      current_head="def67890",
    )
    assert result.status == BootstrapStatus.INVALID
    assert "schema_id_mismatch" in result.triggers

  def test_multiple_triggers(self) -> None:
    result = evaluate_staleness(
      _cached_index(),
      current_phase_id="IP-090.PHASE-02",
      current_head="def67890",
    )
    assert len(result.triggers) >= 2
    assert "commit_drift" in result.triggers
    assert "phase_boundary_crossing" in result.triggers

  def test_reusable_with_subset_changed_files(self) -> None:
    """Changed files within cached domain_map are reusable."""
    result = evaluate_staleness(
      _cached_index(),
      current_phase_id="IP-090.PHASE-01",
      current_head="def67890",
      changed_files=["supekku/cli/main.py"],
    )
    assert result.status == BootstrapStatus.REUSABLE
    assert result.can_incremental_update is True


class CheckDomainMapFilesTest(unittest.TestCase):
  """Test domain_map file existence check."""

  def test_all_exist(self) -> None:
    with TemporaryDirectory() as tmp:
      root = Path(tmp)
      (root / "a.py").touch()
      (root / "b.py").touch()
      domain_map = [
        {"area": "test", "purpose": "test", "files": ["a.py", "b.py"]},
      ]
      assert check_domain_map_files_exist(domain_map, root) == []

  def test_some_deleted(self) -> None:
    with TemporaryDirectory() as tmp:
      root = Path(tmp)
      (root / "a.py").touch()
      domain_map = [
        {"area": "test", "purpose": "test", "files": ["a.py", "b.py"]},
      ]
      deleted = check_domain_map_files_exist(domain_map, root)
      assert deleted == ["b.py"]

  def test_empty_domain_map(self) -> None:
    with TemporaryDirectory() as tmp:
      assert check_domain_map_files_exist([], Path(tmp)) == []


if __name__ == "__main__":
  unittest.main()
