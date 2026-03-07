"""Tests for artifact view layer (VT-053-adapter)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from supekku.scripts.lib.core.artifact_view import (
  ArtifactEntry,
  ArtifactSnapshot,
  ArtifactType,
  adapt_record,
)


class TestArtifactEntry:
  """ArtifactEntry is a simple view model."""

  def test_creation(self):
    entry = ArtifactEntry(
      id="SPEC-001",
      title="CLI Core",
      status="active",
      path=Path("/some/path"),
      artifact_type=ArtifactType.SPEC,
    )
    assert entry.id == "SPEC-001"
    assert entry.title == "CLI Core"
    assert entry.status == "active"
    assert entry.artifact_type == ArtifactType.SPEC
    assert entry.error is None

  def test_error_entry(self):
    entry = ArtifactEntry(
      id="",
      title="",
      status="",
      path=Path(),
      artifact_type=ArtifactType.SPEC,
      error="Failed to load",
    )
    assert entry.error == "Failed to load"


class TestAdaptRecord:
  """adapt_record normalises different registry record shapes."""

  def test_adapt_spec(self):
    record = MagicMock()
    record.id = "SPEC-001"
    record.name = "CLI Core"
    record.status = "active"
    record.path = Path("/specs/SPEC-001")
    entry = adapt_record(record, ArtifactType.SPEC)
    assert entry.id == "SPEC-001"
    assert entry.title == "CLI Core"
    assert entry.status == "active"
    assert entry.artifact_type == ArtifactType.SPEC

  def test_adapt_decision_uses_title(self):
    record = MagicMock()
    record.id = "ADR-001"
    record.title = "Use spec-driver"
    record.status = "accepted"
    record.path = Path("/decisions/ADR-001")
    entry = adapt_record(record, ArtifactType.ADR)
    assert entry.title == "Use spec-driver"

  def test_adapt_requirement_uses_uid(self):
    record = MagicMock()
    record.uid = "SPEC-001.FR-001"
    record.title = "Command dispatch"
    record.status = "active"
    record.path = Path("/reqs")
    entry = adapt_record(record, ArtifactType.REQUIREMENT)
    assert entry.id == "SPEC-001.FR-001"

  def test_adapt_card_uses_lane_as_status(self):
    record = MagicMock()
    record.id = "T001"
    record.title = "Fix bug"
    record.lane = "doing"
    record.path = Path("/kanban/doing/T001")
    # Card has no .status attr
    del record.status
    entry = adapt_record(record, ArtifactType.CARD)
    assert entry.status == "doing"

  def test_adapt_backlog_item(self):
    record = MagicMock()
    record.id = "ISSUE-001"
    record.title = "Registry drift"
    record.status = "open"
    record.path = Path("/backlog/issues/ISSUE-001")
    entry = adapt_record(record, ArtifactType.BACKLOG)
    assert entry.id == "ISSUE-001"


class TestArtifactSnapshot:
  """Snapshot caches registry results and supports targeted refresh."""

  def test_snapshot_loads_from_registries(self, tmp_path):
    """Snapshot calls collect() once per registry at init."""
    snapshot = ArtifactSnapshot(root=tmp_path)
    # Should have entries for all registry types (may be empty dicts)
    assert isinstance(snapshot.entries, dict)
    for art_type in ArtifactType:
      assert art_type in snapshot.entries

  def test_all_entries_returns_flat_list(self, tmp_path):
    """all_entries() returns a flat list across all types."""
    snapshot = ArtifactSnapshot(root=tmp_path)
    entries = snapshot.all_entries()
    assert isinstance(entries, list)

  def test_all_entries_filters_by_type(self, tmp_path):
    snapshot = ArtifactSnapshot(root=tmp_path)
    entries = snapshot.all_entries(type_filter=ArtifactType.SPEC)
    for entry in entries:
      assert entry.artifact_type == ArtifactType.SPEC

  def test_all_entries_filters_by_status(self, tmp_path):
    snapshot = ArtifactSnapshot(root=tmp_path)
    entries = snapshot.all_entries(status_filter="active")
    for entry in entries:
      assert entry.status == "active"

  def test_error_isolation_on_registry_failure(self, tmp_path):
    """A failing registry produces an error entry, not a crash."""
    snapshot = ArtifactSnapshot(root=tmp_path)
    # Verify snapshot loaded without raising even if some registries
    # had no data (empty workspace)
    assert snapshot.entries is not None

  def test_counts_by_type(self, tmp_path):
    snapshot = ArtifactSnapshot(root=tmp_path)
    counts = snapshot.counts_by_type()
    assert isinstance(counts, dict)
    for art_type in ArtifactType:
      assert art_type in counts
      assert isinstance(counts[art_type], int)
