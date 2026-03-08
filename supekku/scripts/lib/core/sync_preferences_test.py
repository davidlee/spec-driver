"""Tests for sync preference persistence (workflow.toml + legacy marker migration)."""

# pylint: disable=redefined-outer-name

from __future__ import annotations

from pathlib import Path

import pytest
import tomlkit

from supekku.scripts.lib.core.sync_preferences import (
  persist_spec_autocreate,
  spec_autocreate_enabled,
)

_SPEC_DRIVER = ".spec-driver"
_WORKFLOW_TOML = "workflow.toml"
_LEGACY_MARKER = "enable_spec_autocreate"


@pytest.fixture
def repo_root(tmp_path: Path) -> Path:
  """Create a minimal repo root with .spec-driver/ and workflow.toml."""
  sd = tmp_path / _SPEC_DRIVER
  sd.mkdir()
  (sd / _WORKFLOW_TOML).write_text('ceremony = "settler"\n', encoding="utf-8")
  return tmp_path


def _toml_path(root: Path) -> Path:
  return root / _SPEC_DRIVER / _WORKFLOW_TOML


def _marker_path(root: Path) -> Path:
  return root / _SPEC_DRIVER / _LEGACY_MARKER


class TestSpecAutocreateEnabled:
  """Tests for spec_autocreate_enabled()."""

  def test_true_when_no_toml_key_and_no_marker(self, repo_root: Path) -> None:
    """Default is now True (town_planner defaults)."""
    assert spec_autocreate_enabled(repo_root) is True

  def test_true_when_toml_key_set(self, repo_root: Path) -> None:
    doc = tomlkit.parse(_toml_path(repo_root).read_text(encoding="utf-8"))
    doc.add("sync", tomlkit.table())
    doc["sync"]["spec_autocreate"] = True
    _toml_path(repo_root).write_text(tomlkit.dumps(doc), encoding="utf-8")

    assert spec_autocreate_enabled(repo_root) is True

  def test_false_when_toml_key_explicitly_false(self, repo_root: Path) -> None:
    doc = tomlkit.parse(_toml_path(repo_root).read_text(encoding="utf-8"))
    doc.add("sync", tomlkit.table())
    doc["sync"]["spec_autocreate"] = False
    _toml_path(repo_root).write_text(tomlkit.dumps(doc), encoding="utf-8")

    # No marker either
    assert spec_autocreate_enabled(repo_root) is False

  def test_falls_back_to_marker_when_toml_key_absent(self, repo_root: Path) -> None:
    _marker_path(repo_root).touch()
    assert spec_autocreate_enabled(repo_root) is True

  def test_falls_back_to_marker_when_toml_key_false(self, repo_root: Path) -> None:
    """Marker file overrides TOML false — backward compat until migration."""
    _marker_path(repo_root).touch()
    assert spec_autocreate_enabled(repo_root) is True

  def test_true_when_spec_driver_dir_missing(self, tmp_path: Path) -> None:
    """Falls back to DEFAULT_CONFIG which has spec_autocreate=True."""
    assert spec_autocreate_enabled(tmp_path) is True


class TestPersistSpecAutocreate:
  """Tests for persist_spec_autocreate()."""

  def test_writes_toml_key(self, repo_root: Path) -> None:
    persist_spec_autocreate(repo_root)

    doc = tomlkit.parse(_toml_path(repo_root).read_text(encoding="utf-8"))
    assert doc["sync"]["spec_autocreate"] is True

  def test_preserves_existing_toml_content(self, repo_root: Path) -> None:
    persist_spec_autocreate(repo_root)

    doc = tomlkit.parse(_toml_path(repo_root).read_text(encoding="utf-8"))
    assert doc["ceremony"] == "settler"

  def test_removes_legacy_marker(self, repo_root: Path) -> None:
    _marker_path(repo_root).touch()
    persist_spec_autocreate(repo_root)

    assert not _marker_path(repo_root).exists()

  def test_idempotent(self, repo_root: Path) -> None:
    persist_spec_autocreate(repo_root)
    persist_spec_autocreate(repo_root)

    doc = tomlkit.parse(_toml_path(repo_root).read_text(encoding="utf-8"))
    assert doc["sync"]["spec_autocreate"] is True

  def test_migration_marker_to_toml(self, repo_root: Path) -> None:
    """Full migration: marker exists → persist → marker gone, TOML key set."""
    _marker_path(repo_root).touch()
    assert spec_autocreate_enabled(repo_root) is True  # via marker

    persist_spec_autocreate(repo_root)

    assert not _marker_path(repo_root).exists()
    assert spec_autocreate_enabled(repo_root) is True  # now via TOML

  def test_creates_spec_driver_dir_if_missing(self, tmp_path: Path) -> None:
    persist_spec_autocreate(tmp_path)

    doc = tomlkit.parse(_toml_path(tmp_path).read_text(encoding="utf-8"))
    assert doc["sync"]["spec_autocreate"] is True
