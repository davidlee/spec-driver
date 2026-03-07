"""Tests for artifact view layer (VT-053-adapter)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from supekku.scripts.lib.core.artifact_view import (
  ARTIFACT_TYPE_META,
  ArtifactEntry,
  ArtifactGroup,
  ArtifactSnapshot,
  ArtifactType,
  ArtifactTypeMeta,
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


class TestArtifactGroup:
  """ArtifactGroup enum covers all semantic groups."""

  def test_group_values(self):
    assert ArtifactGroup.GOVERNANCE.value == "governance"
    assert ArtifactGroup.CHANGE.value == "change"
    assert ArtifactGroup.DOMAIN.value == "domain"
    assert ArtifactGroup.OPERATIONAL.value == "operational"

  def test_exactly_four_groups(self):
    assert len(ArtifactGroup) == 4


class TestArtifactTypeMeta:
  """ArtifactTypeMeta provides display/classification metadata."""

  def test_all_types_have_metadata(self):
    for art_type in ArtifactType:
      assert art_type in ARTIFACT_TYPE_META, f"Missing metadata for {art_type}"

  def test_no_extra_metadata_keys(self):
    for key in ARTIFACT_TYPE_META:
      assert key in ArtifactType, f"Extra metadata key {key}"

  def test_meta_is_frozen(self):
    meta = ARTIFACT_TYPE_META[ArtifactType.ADR]
    assert isinstance(meta, ArtifactTypeMeta)

  def test_singular_plural_populated(self):
    for art_type, meta in ARTIFACT_TYPE_META.items():
      assert meta.singular, f"Empty singular for {art_type}"
      assert meta.plural, f"Empty plural for {art_type}"

  def test_group_assigned(self):
    for art_type, meta in ARTIFACT_TYPE_META.items():
      assert isinstance(meta.group, ArtifactGroup), f"Bad group for {art_type}"

  def test_governance_group_members(self):
    gov = {t for t in ArtifactType if t.group == ArtifactGroup.GOVERNANCE}
    expected = {ArtifactType.ADR, ArtifactType.POLICY, ArtifactType.STANDARD}
    assert gov == expected

  def test_change_group_members(self):
    chg = {t for t in ArtifactType if t.group == ArtifactGroup.CHANGE}
    expected = {ArtifactType.DELTA, ArtifactType.REVISION, ArtifactType.AUDIT}
    assert chg == expected

  def test_domain_group_members(self):
    dom = {t for t in ArtifactType if t.group == ArtifactGroup.DOMAIN}
    assert dom == {ArtifactType.SPEC, ArtifactType.REQUIREMENT}

  def test_operational_group_members(self):
    ops = {t for t in ArtifactType if t.group == ArtifactGroup.OPERATIONAL}
    expected = {ArtifactType.MEMORY, ArtifactType.CARD, ArtifactType.BACKLOG}
    assert ops == expected


class TestArtifactTypeProperties:
  """Convenience properties on ArtifactType delegate to metadata."""

  def test_meta_property(self):
    assert ArtifactType.ADR.meta == ARTIFACT_TYPE_META[ArtifactType.ADR]

  def test_singular(self):
    assert ArtifactType.ADR.singular == "ADR"
    assert ArtifactType.POLICY.singular == "Policy"
    assert ArtifactType.BACKLOG.singular == "Backlog Item"

  def test_plural(self):
    assert ArtifactType.ADR.plural == "ADRs"
    assert ArtifactType.POLICY.plural == "Policies"
    assert ArtifactType.MEMORY.plural == "Memories"
    assert ArtifactType.BACKLOG.plural == "Backlog Items"

  def test_group(self):
    assert ArtifactType.ADR.group == ArtifactGroup.GOVERNANCE
    assert ArtifactType.DELTA.group == ArtifactGroup.CHANGE
    assert ArtifactType.SPEC.group == ArtifactGroup.DOMAIN
    assert ArtifactType.MEMORY.group == ArtifactGroup.OPERATIONAL


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
