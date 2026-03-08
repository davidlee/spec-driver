"""Tests for structure checks."""

from __future__ import annotations

import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path

from supekku.scripts.lib.diagnostics.checks.structure import (
  _check_orphaned_bundles,
  check_structure,
)


@dataclass
class _FakeWorkspace:
  root: Path


def _make_workspace(tmp_path: Path) -> _FakeWorkspace:
  """Create a minimal valid workspace structure."""
  sd = tmp_path / ".spec-driver"
  for subdir in (
    "tech", "deltas", "decisions",
    "backlog", "memory", "registry", "templates",
  ):
    (sd / subdir).mkdir(parents=True)
  return _FakeWorkspace(root=tmp_path)


class TestCheckStructure(unittest.TestCase):
  """Tests for check_structure function."""

  def test_valid_workspace(self) -> None:
    """All directories present produces all-pass."""
    with tempfile.TemporaryDirectory() as td:
      ws = _make_workspace(Path(td))
      results = check_structure(ws)
      statuses = {r.name: r.status for r in results}
      assert statuses["spec-driver-root"] == "pass"
      fail_or_warn = [r for r in results if r.status != "pass"]
      assert not fail_or_warn, fail_or_warn

  def test_missing_spec_driver_root(self) -> None:
    """Missing .spec-driver/ should fail and short-circuit."""
    with tempfile.TemporaryDirectory() as td:
      ws = _FakeWorkspace(root=Path(td))
      results = check_structure(ws)
      assert len(results) == 1
      assert results[0].status == "fail"
      assert results[0].name == "spec-driver-root"

  def test_missing_subdirectory_warns(self) -> None:
    """Missing required subdirectory should warn."""
    with tempfile.TemporaryDirectory() as td:
      root = Path(td)
      sd = root / ".spec-driver"
      for subdir in (
        "tech", "decisions", "backlog", "memory", "registry",
      ):
        (sd / subdir).mkdir(parents=True)
      # Missing: deltas, templates

      ws = _FakeWorkspace(root=root)
      results = check_structure(ws)
      statuses = {r.name: r.status for r in results}
      assert statuses["deltas"] == "warn"
      assert statuses["templates"] == "warn"
      assert statuses["decisions"] == "pass"


class TestCheckOrphanedBundles(unittest.TestCase):
  """Tests for orphaned bundle detection."""

  def test_no_orphans_in_normal_structure(self) -> None:
    """Normal delta bundle with DE-*.md is not orphaned."""
    with tempfile.TemporaryDirectory() as td:
      deltas = Path(td) / "deltas"
      bundle = deltas / "DE-001-my-delta"
      bundle.mkdir(parents=True)
      (bundle / "DE-001.md").write_text("# DE-001")

      results = _check_orphaned_bundles(deltas, "delta")
      assert not results

  def test_empty_bundle_warns(self) -> None:
    """Empty bundle directory should warn."""
    with tempfile.TemporaryDirectory() as td:
      deltas = Path(td) / "deltas"
      bundle = deltas / "DE-002-empty"
      bundle.mkdir(parents=True)

      results = _check_orphaned_bundles(deltas, "delta")
      assert len(results) == 1
      assert results[0].status == "warn"
      assert "Empty" in results[0].message

  def test_bundle_with_non_primary_md_warns(self) -> None:
    """Bundle with .md files but no primary artifact warns."""
    with tempfile.TemporaryDirectory() as td:
      deltas = Path(td) / "deltas"
      bundle = deltas / "some-dir"
      bundle.mkdir(parents=True)
      (bundle / "random-notes.md").write_text("# Notes")

      results = _check_orphaned_bundles(deltas, "delta")
      assert len(results) == 1
      assert results[0].status == "warn"
      assert "orphaned" in results[0].message.lower()

  def test_nonexistent_parent_returns_empty(self) -> None:
    """Non-existent parent directory returns no results."""
    results = _check_orphaned_bundles(Path("/nonexistent"), "delta")
    assert results == []

  def test_bundle_with_dr_and_ip_is_not_orphaned(self) -> None:
    """Bundle with DR/IP files is not orphaned."""
    with tempfile.TemporaryDirectory() as td:
      deltas = Path(td) / "deltas"
      bundle = deltas / "DE-003-thing"
      bundle.mkdir(parents=True)
      (bundle / "DR-003.md").write_text("# DR")
      (bundle / "IP-003.md").write_text("# IP")

      results = _check_orphaned_bundles(deltas, "delta")
      assert not results


if __name__ == "__main__":
  unittest.main()
