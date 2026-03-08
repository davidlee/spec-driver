"""Tests for drift ledger creation."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from supekku.scripts.lib.drift.creation import create_drift_ledger


class TestCreateDriftLedger(unittest.TestCase):
  """Tests for create_drift_ledger."""

  def test_creates_ledger_file(self) -> None:
    """Creates a ledger file with correct frontmatter."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = Path(tmpdir)
      drift_dir = root / ".spec-driver" / "drift"
      drift_dir.mkdir(parents=True)

      with patch(
        "supekku.scripts.lib.drift.creation.get_drift_dir",
        return_value=drift_dir,
      ):
        path = create_drift_ledger("Test ledger", repo_root=root)

      assert path.exists()
      assert path.name.startswith("DL-001-")
      content = path.read_text()
      assert "id: DL-001" in content
      assert "name: Test ledger" in content
      assert "status: open" in content
      assert "kind: drift_ledger" in content
      assert "## Entries" in content

  def test_creates_directory_if_missing(self) -> None:
    """Creates .spec-driver/drift/ if it doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = Path(tmpdir)
      drift_dir = root / ".spec-driver" / "drift"
      assert not drift_dir.exists()

      with patch(
        "supekku.scripts.lib.drift.creation.get_drift_dir",
        return_value=drift_dir,
      ):
        path = create_drift_ledger("New ledger", repo_root=root)

      assert drift_dir.is_dir()
      assert path.exists()

  def test_increments_id(self) -> None:
    """Allocates sequential IDs."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = Path(tmpdir)
      drift_dir = root / ".spec-driver" / "drift"
      drift_dir.mkdir(parents=True)
      # Create existing ledger files
      (drift_dir / "DL-001-first.md").write_text("---\nid: DL-001\n---\n")
      (drift_dir / "DL-003-third.md").write_text("---\nid: DL-003\n---\n")

      with patch(
        "supekku.scripts.lib.drift.creation.get_drift_dir",
        return_value=drift_dir,
      ):
        path = create_drift_ledger("Fourth", repo_root=root)

      assert "DL-004" in path.name

  def test_delta_ref_included(self) -> None:
    """Includes delta_ref in frontmatter when provided."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = Path(tmpdir)
      drift_dir = root / ".spec-driver" / "drift"
      drift_dir.mkdir(parents=True)

      with patch(
        "supekku.scripts.lib.drift.creation.get_drift_dir",
        return_value=drift_dir,
      ):
        path = create_drift_ledger(
          "Delta ledger",
          delta_ref="DE-065",
          repo_root=root,
        )

      content = path.read_text()
      assert "delta_ref: DE-065" in content

  def test_empty_delta_ref(self) -> None:
    """Empty delta_ref produces empty string in frontmatter."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = Path(tmpdir)
      drift_dir = root / ".spec-driver" / "drift"
      drift_dir.mkdir(parents=True)

      with patch(
        "supekku.scripts.lib.drift.creation.get_drift_dir",
        return_value=drift_dir,
      ):
        path = create_drift_ledger("No delta", repo_root=root)

      content = path.read_text()
      assert "delta_ref: ''" in content

  def test_empty_name_raises(self) -> None:
    """Raises ValueError for empty name."""
    with self.assertRaises(ValueError, msg="empty"):
      create_drift_ledger("")

    with self.assertRaises(ValueError, msg="whitespace"):
      create_drift_ledger("   ")

  def test_slug_in_filename(self) -> None:
    """Name is slugified in the filename."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = Path(tmpdir)
      drift_dir = root / ".spec-driver" / "drift"
      drift_dir.mkdir(parents=True)

      with patch(
        "supekku.scripts.lib.drift.creation.get_drift_dir",
        return_value=drift_dir,
      ):
        path = create_drift_ledger(
          "Spec Corpus Reconciliation",
          repo_root=root,
        )

      # Should be kebab-case or underscore-separated
      assert "DL-001" in path.name
      name_lower = path.name.lower()
      assert "spec" in name_lower
      assert "reconciliation" in name_lower


if __name__ == "__main__":
  unittest.main()
