"""Tests for sync preference persistence (marker file)."""

# pylint: disable=redefined-outer-name

from __future__ import annotations

from pathlib import Path

import pytest

from supekku.scripts.lib.core.sync_preferences import (
  MARKER_FILENAME,
  persist_spec_autocreate,
  spec_autocreate_enabled,
)


@pytest.fixture
def repo_root(tmp_path: Path) -> Path:
  """Create a minimal repo root with .spec-driver/ directory."""
  (tmp_path / ".spec-driver").mkdir()
  return tmp_path


def _marker_path(root: Path) -> Path:
  return root / ".spec-driver" / MARKER_FILENAME


class TestSpecAutocreateEnabled:
  """Tests for spec_autocreate_enabled()."""

  def test_returns_false_when_marker_absent(self, repo_root: Path) -> None:
    assert spec_autocreate_enabled(repo_root) is False

  def test_returns_true_when_marker_present(self, repo_root: Path) -> None:
    _marker_path(repo_root).touch()
    assert spec_autocreate_enabled(repo_root) is True

  def test_returns_false_when_spec_driver_dir_missing(self, tmp_path: Path) -> None:
    assert spec_autocreate_enabled(tmp_path) is False


class TestPersistSpecAutocreate:
  """Tests for persist_spec_autocreate()."""

  def test_creates_marker_file(self, repo_root: Path) -> None:
    persist_spec_autocreate(repo_root)
    assert _marker_path(repo_root).exists()

  def test_marker_is_zero_bytes(self, repo_root: Path) -> None:
    persist_spec_autocreate(repo_root)
    assert _marker_path(repo_root).stat().st_size == 0

  def test_idempotent(self, repo_root: Path) -> None:
    persist_spec_autocreate(repo_root)
    persist_spec_autocreate(repo_root)
    assert _marker_path(repo_root).exists()

  def test_creates_spec_driver_dir_if_missing(self, tmp_path: Path) -> None:
    persist_spec_autocreate(tmp_path)
    assert _marker_path(tmp_path).exists()
