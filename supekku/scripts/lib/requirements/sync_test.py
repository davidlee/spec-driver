"""Tests for requirement synchronization."""

from __future__ import annotations

import io
import os
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from supekku.scripts.lib.core.paths import (
  AUDITS_SUBDIR,
  DELTAS_SUBDIR,
  REVISIONS_SUBDIR,
  SPEC_DRIVER_DIR,
  TECH_SPECS_SUBDIR,
  get_registry_dir,
)
from supekku.scripts.lib.core.spec_utils import dump_markdown_file
from supekku.scripts.lib.relations.manager import add_relation
from supekku.scripts.lib.requirements.coverage import _compute_status_from_coverage
from supekku.scripts.lib.requirements.lifecycle import (
  STATUS_ACTIVE,
  STATUS_IN_PROGRESS,
  STATUS_PENDING,
)
from supekku.scripts.lib.requirements.registry import (
  RequirementRecord,
  RequirementsRegistry,
  SyncStats,
)
from supekku.scripts.lib.requirements.sync import _iter_spec_files, _upsert_record
from supekku.scripts.lib.specs.registry import SpecRegistry


class RequirementsRegistryTest(unittest.TestCase):
  """Test cases for RequirementsRegistry functionality."""

  def setUp(self) -> None:
    self._cwd = Path.cwd()

  def tearDown(self) -> None:
    os.chdir(self._cwd)

  def _write_spec(self, root: Path, spec_id: str, body: str) -> Path:
    spec_dir = root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR / f"{spec_id.lower()}-example"
    spec_dir.mkdir(parents=True, exist_ok=True)
    spec_path = spec_dir / f"{spec_id}.md"
    frontmatter = {
      "id": spec_id,
      "slug": spec_id.lower(),
      "name": f"Spec {spec_id}",
      "created": "2024-06-01",
      "updated": "2024-06-01",
      "status": "draft",
      "kind": "spec",
    }
    dump_markdown_file(spec_path, frontmatter, body)
    return spec_path

  def _make_repo(self) -> Path:
    tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.addCleanup(tmpdir.cleanup)
    root = Path(tmpdir.name)
    (root / ".git").mkdir()
    body = (
      "# SPEC-001\n\n"
      "## 6. Quality & Operational Requirements\n\n"
      "- FR-001: First functional requirement\n"
      "- NF-020: Non functional requirement\n"
    )
    self._write_spec(root, "SPEC-001", body)
    os.chdir(root)
    return root

  def test_sync_creates_entries(self) -> None:
    """Test that syncing from specs creates registry entries for requirements."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    spec_registry = SpecRegistry(root)

    stats = registry.sync_from_specs(
      [root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR],
      spec_registry=spec_registry,
    )
    registry.save()

    assert stats.created == 2
    assert stats.updated == 0
    assert registry_path.exists()
    records = registry.search()
    assert len(records) == 2
    assert records[0].status == STATUS_PENDING

  def _create_change_bundle(
    self,
    root: Path,
    bundle: str,
    file_id: str,
    kind: str,
  ) -> Path:
    bundle_dir = root / SPEC_DRIVER_DIR / bundle
    bundle_dir.mkdir(parents=True, exist_ok=True)
    file_path = bundle_dir / f"{file_id}.md"
    frontmatter = {
      "id": file_id,
      "slug": file_id.lower(),
      "name": file_id,
      "created": "2024-06-01",
      "updated": "2024-06-01",
      "status": "draft",
      "kind": kind,
      "relations": [],
    }
    dump_markdown_file(file_path, frontmatter, f"# {file_id}\n")
    return file_path

  def test_sync_collects_change_relations(self) -> None:
    """Test syncing collects relations from delta, revision, audit artifacts."""
    root = self._make_repo()
    delta_path = self._create_change_bundle(
      root,
      "deltas/DE-001-example",
      "DE-001",
      "delta",
    )
    revision_path = self._create_change_bundle(
      root,
      "revisions/RE-001-example",
      "RE-001",
      "revision",
    )
    audit_path = self._create_change_bundle(
      root,
      "audits/AUD-001-example",
      "AUD-001",
      "audit",
    )

    add_relation(delta_path, relation_type="implements", target="SPEC-001.FR-001")
    add_relation(
      revision_path,
      relation_type="introduces",
      target="SPEC-001.FR-001",
    )
    add_relation(audit_path, relation_type="verifies", target="SPEC-001.FR-001")

    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    spec_registry = SpecRegistry(root)
    registry.sync_from_specs(
      [root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR],
      spec_registry=spec_registry,
      delta_dirs=[root / SPEC_DRIVER_DIR / DELTAS_SUBDIR],
      revision_dirs=[root / SPEC_DRIVER_DIR / REVISIONS_SUBDIR],
      audit_dirs=[root / SPEC_DRIVER_DIR / AUDITS_SUBDIR],
    )
    registry.save()

    record = registry.records["SPEC-001.FR-001"]
    assert record.implemented_by == ["DE-001"]
    assert record.introduced == "RE-001"
    assert record.verified_by == ["AUD-001"]

    results = registry.search(implemented_by="DE-001")
    assert [r.uid for r in results] == ["SPEC-001.FR-001"]
    assert [r.uid for r in registry.search(introduced_by="RE-001")] == [
      "SPEC-001.FR-001",
    ]
    assert [r.uid for r in registry.search(verified_by="AUD-001")] == [
      "SPEC-001.FR-001",
    ]

  def test_sync_preserves_status(self) -> None:
    """Test that re-syncing preserves manually set requirement statuses."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    spec_registry = SpecRegistry(root)
    registry.sync_from_specs(
      [root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR],
      spec_registry=spec_registry,
    )
    registry.set_status("SPEC-001.FR-001", STATUS_ACTIVE)
    registry.save()

    # re-sync after modifying spec body
    spec_path = (
      root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR / "spec-001-example" / "SPEC-001.md"
    )
    text = spec_path.read_text(encoding="utf-8")
    text += "- FR-002: Second requirement\n"
    spec_path.write_text(text, encoding="utf-8")

    registry = RequirementsRegistry(registry_path)
    spec_registry.reload()
    stats = registry.sync_from_specs(
      [root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR],
      spec_registry=spec_registry,
    )
    registry.save()

    assert stats.created == 1
    assert registry.records["SPEC-001.FR-001"].status == STATUS_ACTIVE

  def test_search_filters(self) -> None:
    """Test that search can filter requirements by text query."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    spec_registry = SpecRegistry(root)
    registry.sync_from_specs(
      [root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR],
      spec_registry=spec_registry,
    )

    results = registry.search(query="non functional")
    assert len(results) == 1
    assert results[0].label.startswith("NF-")

  def test_move_requirement_updates_primary_spec(self) -> None:
    """Test that moving a requirement updates its primary spec and UID."""
    root = self._make_repo()
    self._write_spec(
      root,
      "SPEC-002",
      "# SPEC-002\n\n- FR-002: Second requirement\n",
    )

    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    spec_registry = SpecRegistry(root)
    registry.sync_from_specs(
      [root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR],
      spec_registry=spec_registry,
    )

    new_uid = registry.move_requirement(
      "SPEC-001.FR-001",
      "SPEC-002",
      spec_registry=spec_registry,
    )
    registry.save()

    assert "SPEC-001.FR-001" not in registry.records
    assert new_uid == "SPEC-002.FR-001"
    moved = registry.records[new_uid]
    assert moved.primary_spec == "SPEC-002"
    assert moved.path == ".spec-driver/tech/spec-002-example/SPEC-002.md"

  def test_relationship_block_adds_collaborators(self) -> None:
    """Test that spec relationship blocks add collaborator specs to requirements."""
    root = self._make_repo()
    collaborator_body = """```yaml supekku:spec.relationships@v1
schema: supekku.spec.relationships
version: 1
spec: SPEC-002
requirements:
  primary:
    - SPEC-002.FR-001
  collaborators:
    - SPEC-001.FR-001
interactions: []
```

# SPEC-002

- FR-001: Collab requirement
"""
    self._write_spec(root, "SPEC-002", collaborator_body)

    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    spec_registry = SpecRegistry(root)
    spec_registry.reload()
    registry.sync_from_specs(
      [root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR],
      spec_registry=spec_registry,
    )

    record = registry.records["SPEC-001.FR-001"]
    assert record.primary_spec == "SPEC-001"
    assert "SPEC-002" in record.specs
    assert "SPEC-001" in record.specs

  def test_delta_relationships_block_marks_implemented_by(self) -> None:
    """Test that delta relationship blocks mark requirements as implemented."""
    root = self._make_repo()

    delta_dir = root / SPEC_DRIVER_DIR / DELTAS_SUBDIR / "DE-002-example"
    delta_dir.mkdir(parents=True, exist_ok=True)
    delta_path = delta_dir / "DE-002.md"
    frontmatter = {
      "id": "DE-002",
      "slug": "example",
      "name": "Delta – Example",
      "created": "2024-06-01",
      "updated": "2024-06-01",
      "status": "draft",
      "kind": "delta",
      "relations": [],
      "applies_to": {"specs": ["SPEC-001"], "requirements": []},
    }
    body = (
      "```yaml supekku:delta.relationships@v1\n"
      "schema: supekku.delta.relationships\n"
      "version: 1\n"
      "delta: DE-002\n"
      "revision_links:\n"
      "  introduces:\n"
      "    - RE-001\n"
      "  supersedes: []\n"
      "specs:\n"
      "  primary:\n"
      "    - SPEC-001\n"
      "  collaborators: []\n"
      "requirements:\n"
      "  implements:\n"
      "    - SPEC-001.FR-001\n"
      "  updates: []\n"
      "  verifies: []\n"
      "phases: []\n"
      "```\n\n"
      "# DE-002 – Example\n"
    )
    dump_markdown_file(delta_path, frontmatter, body)

    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    spec_registry = SpecRegistry(root)
    registry.sync_from_specs(
      [root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR],
      spec_registry=spec_registry,
      delta_dirs=[root / SPEC_DRIVER_DIR / DELTAS_SUBDIR],
    )

    record = registry.records["SPEC-001.FR-001"]
    assert "DE-002" in record.implemented_by

  def _write_revision_with_block(
    self,
    root: Path,
    revision_id: str,
    block_yaml: str,
  ) -> Path:
    slug = f"{revision_id.lower()}-bundle"
    bundle_dir = root / SPEC_DRIVER_DIR / REVISIONS_SUBDIR / slug
    bundle_dir.mkdir(parents=True, exist_ok=True)
    revision_path = bundle_dir / f"{revision_id}.md"
    frontmatter = {
      "id": revision_id,
      "slug": revision_id.lower(),
      "name": revision_id,
      "created": "2024-06-01",
      "updated": "2024-06-01",
      "status": "draft",
      "kind": "revision",
    }
    body = f"# {revision_id}\n\n```yaml supekku:revision.change@v1\n{block_yaml}\n```\n"
    dump_markdown_file(revision_path, frontmatter, body)
    return revision_path

  def test_revision_block_moves_requirement_and_sets_collaborators(self) -> None:
    """Test that revision blocks can move requirements and set collaborator specs."""
    root = self._make_repo()
    # Additional specs to support destination/collaborator lookups
    self._write_spec(
      root,
      "SPEC-002",
      "# SPEC-002\n\n- FR-100: Placeholder\n",
    )
    self._write_spec(
      root,
      "SPEC-003",
      "# SPEC-003\n",
    )

    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    spec_registry = SpecRegistry(root)
    registry.sync_from_specs(
      [root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR],
      spec_registry=spec_registry,
    )
    registry.save()

    block_yaml = """schema: supekku.revision.change
version: 1
metadata:
  revision: RE-002
specs: []
requirements:
  - requirement_id: SPEC-002.FR-001
    kind: functional
    action: move
    origin:
      - kind: requirement
        ref: SPEC-001.FR-001
    destination:
      spec: SPEC-002
      requirement_id: SPEC-002.FR-001
      additional_specs:
        - SPEC-003
    lifecycle:
      status: in-progress
      introduced_by: RE-002
"""
    self._write_revision_with_block(root, "RE-002", block_yaml)

    spec_registry.reload()
    stats = registry.sync_from_specs(
      [root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR],
      spec_registry=spec_registry,
      revision_dirs=[root / SPEC_DRIVER_DIR / REVISIONS_SUBDIR],
    )
    registry.save()

    assert stats.updated >= 1
    assert "SPEC-001.FR-001" not in registry.records
    record = registry.records["SPEC-002.FR-001"]
    assert record.primary_spec == "SPEC-002"
    assert record.specs == ["SPEC-002", "SPEC-003"]
    assert record.status == "in-progress"
    assert record.introduced == "RE-002"
    assert record.path == ".spec-driver/tech/spec-002-example/SPEC-002.md"

  def test_sync_processes_coverage_blocks(self) -> None:
    """VT-902: Registry sync updates lifecycle from coverage blocks."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    # Create spec with coverage blocks
    test_root = Path(__file__).parent.parent.parent.parent.parent
    fixtures_dir = test_root / "tests" / "fixtures"
    coverage_dir = fixtures_dir / "requirements" / "coverage"

    # Debug: Check if files exist
    assert coverage_dir.exists(), f"Coverage dir does not exist: {coverage_dir}"
    spec_files = list(_iter_spec_files([coverage_dir]))
    assert len(spec_files) > 0, f"No spec files found in {coverage_dir}"

    stats = registry.sync_from_specs(
      spec_dirs=[coverage_dir],
      plan_dirs=[coverage_dir],
    )
    registry.save()

    # Verify requirements were created
    assert stats.created >= 3, (
      f"Expected >=3 created, got {stats.created}. "
      f"Records: {list(registry.records.keys())}"
    )
    assert "SPEC-900.FR-001" in registry.records
    assert "SPEC-900.FR-002" in registry.records
    assert "SPEC-900.FR-003" in registry.records

    # Check coverage_evidence populated from coverage (not verified_by)
    fr001 = registry.records["SPEC-900.FR-001"]
    assert "VT-900" in fr001.coverage_evidence
    assert fr001.status == STATUS_ACTIVE  # All verified

    fr002 = registry.records["SPEC-900.FR-002"]
    assert "VT-901" in fr002.coverage_evidence
    assert fr002.status == STATUS_IN_PROGRESS  # In progress

    fr003 = registry.records["SPEC-900.FR-003"]
    assert "VT-902" in fr003.coverage_evidence
    assert fr003.status == STATUS_PENDING  # Planned

  def test_coverage_drift_detection(self) -> None:
    """Registry emits warnings for coverage conflicts."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    test_root = Path(__file__).parent.parent.parent.parent.parent
    fixtures_dir = test_root / "tests" / "fixtures"
    coverage_dir = fixtures_dir / "requirements" / "coverage"

    # Capture stderr to check for drift warnings
    old_stderr = sys.stderr
    sys.stderr = io.StringIO()

    try:
      registry.sync_from_specs(
        spec_dirs=[coverage_dir],
        plan_dirs=[coverage_dir],
      )

      stderr_output = sys.stderr.getvalue()

      # Check that drift warning was emitted for SPEC-901.FR-001
      assert "Coverage drift detected for SPEC-901.FR-001" in stderr_output
      assert "SPEC-901.md" in stderr_output
      assert "IP-901.md" in stderr_output
    finally:
      sys.stderr = old_stderr

  def test_compute_status_from_coverage(self) -> None:
    """Unit test for status computation from coverage entries."""
    self._make_repo()

    # All verified → active
    entries = [{"status": "verified"}, {"status": "verified"}]
    assert _compute_status_from_coverage(entries) == STATUS_ACTIVE

    # In-progress → in-progress
    entries = [{"status": "in-progress"}]
    assert _compute_status_from_coverage(entries) == STATUS_IN_PROGRESS

    # All planned → pending
    entries = [{"status": "planned"}]
    assert _compute_status_from_coverage(entries) == STATUS_PENDING

    # Failed → in-progress (needs attention)
    entries = [{"status": "failed"}]
    assert _compute_status_from_coverage(entries) == STATUS_IN_PROGRESS

    # Blocked → in-progress
    entries = [{"status": "blocked"}]
    assert _compute_status_from_coverage(entries) == STATUS_IN_PROGRESS

    # Mixed → in-progress
    entries = [{"status": "verified"}, {"status": "planned"}]
    assert _compute_status_from_coverage(entries) == STATUS_IN_PROGRESS

    # Empty → None
    entries = []
    assert _compute_status_from_coverage(entries) is None

  def test_compute_status_from_coverage_ignores_unknown_statuses(self) -> None:
    """VT-043-002: Unknown statuses are filtered out of derivation."""
    self._make_repo()

    # Unknown status alone → None (no valid statuses to derive from)
    entries = [{"status": "deferred"}]
    assert _compute_status_from_coverage(entries) is None

    # All unknown → None
    entries = [{"status": "deferred"}, {"status": "acknowledged"}]
    assert _compute_status_from_coverage(entries) is None

    # Valid + unknown: unknown is ignored, valid drives derivation
    entries = [{"status": "verified"}, {"status": "deferred"}]
    assert _compute_status_from_coverage(entries) == STATUS_ACTIVE

    # Multiple valid + unknown: derives from valid entries only
    entries = [
      {"status": "verified"},
      {"status": "deferred"},
      {"status": "planned"},
    ]
    assert _compute_status_from_coverage(entries) == STATUS_IN_PROGRESS

  def test_coverage_evidence_field_serialization(self) -> None:
    """VT-910: RequirementRecord with coverage_evidence serializes correctly."""
    # Create record with coverage_evidence
    record = RequirementRecord(
      uid="SPEC-001.FR-001",
      label="FR-001",
      title="Test requirement",
      coverage_evidence=["VT-910", "VT-911", "VA-321"],
      verified_by=["AUD-001"],
    )

    # Test to_dict serialization
    data = record.to_dict()
    assert "coverage_evidence" in data
    assert data["coverage_evidence"] == ["VT-910", "VT-911", "VA-321"]
    assert data["verified_by"] == ["AUD-001"]

    # Test from_dict deserialization
    reconstructed = RequirementRecord.from_dict("SPEC-001.FR-001", data)
    assert reconstructed.coverage_evidence == ["VT-910", "VT-911", "VA-321"]
    assert reconstructed.verified_by == ["AUD-001"]
    assert reconstructed.uid == "SPEC-001.FR-001"

  def test_coverage_evidence_merge(self) -> None:
    """VT-910: RequirementRecord.merge() combines coverage_evidence correctly."""
    record1 = RequirementRecord(
      uid="SPEC-001.FR-001",
      label="FR-001",
      title="Original title",
      coverage_evidence=["VT-910", "VT-911"],
      verified_by=["AUD-001"],
    )

    record2 = RequirementRecord(
      uid="SPEC-001.FR-001",
      label="FR-001",
      title="Updated title",
      coverage_evidence=["VT-911", "VA-321"],  # Overlapping + new
      verified_by=["AUD-002"],  # Different verified_by
    )

    # Merge preserves lifecycle fields from self, merges coverage_evidence
    merged = record1.merge(record2)
    assert merged.title == "Updated title"
    # coverage_evidence should be union, sorted
    assert merged.coverage_evidence == ["VA-321", "VT-910", "VT-911"]
    # verified_by preserved from self (lifecycle field)
    assert merged.verified_by == ["AUD-001"]

  def test_coverage_sync_populates_coverage_evidence(self) -> None:
    """VT-911: Coverage sync populates coverage_evidence, not verified_by."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    # Create spec with coverage blocks
    test_root = Path(__file__).parent.parent.parent.parent.parent
    fixtures_dir = test_root / "tests" / "fixtures"
    coverage_dir = fixtures_dir / "requirements" / "coverage"

    stats = registry.sync_from_specs(
      spec_dirs=[coverage_dir],
      plan_dirs=[coverage_dir],
    )
    registry.save()

    # Verify requirements were created
    assert stats.created >= 3
    assert "SPEC-900.FR-001" in registry.records
    assert "SPEC-900.FR-002" in registry.records

    # NEW: Check coverage_evidence populated (not verified_by)
    fr001 = registry.records["SPEC-900.FR-001"]
    assert "VT-900" in fr001.coverage_evidence, (
      f"Expected VT-900 in coverage_evidence, got {fr001.coverage_evidence}"
    )
    # verified_by should remain empty (no audits in fixtures)
    assert fr001.verified_by == [], (
      f"Expected empty verified_by, got {fr001.verified_by}"
    )

    fr002 = registry.records["SPEC-900.FR-002"]
    assert "VT-901" in fr002.coverage_evidence
    assert fr002.verified_by == []

  def test_qualified_requirement_format(self) -> None:
    """Test extraction of requirements with fully-qualified IDs (SPEC-XXX.FR-001)."""
    root = self._make_repo()

    # Create spec with qualified format (as used in PROD-010, SPEC-110, etc.)
    qualified_body = (
      "# SPEC-002\n\n"
      "## 3. Requirements\n\n"
      "**Priority 1: Critical**\n\n"
      "- **SPEC-002.FR-001**: All list commands MUST support JSON output\n"
      "- **SPEC-002.FR-002**: System MUST validate input schemas\n"
      "- **SPEC-002.NF-001**: Commands MUST complete in <2 seconds\n"
    )
    self._write_spec(root, "SPEC-002", qualified_body)

    # Also test mixed format in same file
    mixed_body = (
      "# SPEC-003\n\n"
      "## Legacy format\n\n"
      "- **FR-001**: Short format requirement\n"
      "- **NF-001**: Short format non-functional\n\n"
      "## New format\n\n"
      "- **SPEC-003.FR-002**: Qualified format requirement\n"
      "- **SPEC-003.NF-002**: Qualified format non-functional\n"
    )
    self._write_spec(root, "SPEC-003", mixed_body)

    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    spec_registry = SpecRegistry(root)
    spec_registry.reload()

    stats = registry.sync_from_specs(
      [root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR],
      spec_registry=spec_registry,
    )
    registry.save()

    # Verify SPEC-002 qualified requirements extracted
    assert "SPEC-002.FR-001" in registry.records
    assert "SPEC-002.FR-002" in registry.records
    assert "SPEC-002.NF-001" in registry.records

    fr001 = registry.records["SPEC-002.FR-001"]
    assert fr001.label == "FR-001"
    assert fr001.title == "All list commands MUST support JSON output"
    assert fr001.kind == "functional"

    nf001 = registry.records["SPEC-002.NF-001"]
    assert nf001.label == "NF-001"
    assert nf001.kind == "non-functional"

    # Verify SPEC-003 mixed format works
    assert "SPEC-003.FR-001" in registry.records  # Short format
    assert "SPEC-003.FR-002" in registry.records  # Qualified format
    assert "SPEC-003.NF-001" in registry.records  # Short format
    assert "SPEC-003.NF-002" in registry.records  # Qualified format

    # All should have correct spec association
    for uid in [
      "SPEC-003.FR-001",
      "SPEC-003.FR-002",
      "SPEC-003.NF-001",
      "SPEC-003.NF-002",
    ]:
      record = registry.records[uid]
      assert record.primary_spec == "SPEC-003"
      assert "SPEC-003" in record.specs

    # Total extracted: 2 from SPEC-001, 3 from SPEC-002, 4 from SPEC-003
    assert stats.created == 9

  def test_category_parsing_inline_syntax(self) -> None:
    """VT-017-001: Test category extraction from inline syntax."""
    root = self._make_repo()

    # Test various inline category formats
    category_body = (
      "# SPEC-004\n\n"
      "## 6. Requirements\n\n"
      "- **FR-001**(auth): Authentication requirement\n"
      "- **FR-002**(security/auth): Nested category with slash\n"
      "- **NF-001**(perf.db): Category with dot delimiter\n"
      "- **FR-003**( whitespace ): Category with whitespace\n"
      "- **FR-004**: No category\n"
      "- **SPEC-004.FR-005**(storage): Qualified with category\n"
    )
    self._write_spec(root, "SPEC-004", category_body)

    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    spec_registry = SpecRegistry(root)
    spec_registry.reload()

    _stats = registry.sync_from_specs(
      [root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR],
      spec_registry=spec_registry,
    )
    registry.save()

    # Verify inline categories extracted correctly
    fr001 = registry.records["SPEC-004.FR-001"]
    assert fr001.category == "auth"
    assert fr001.title == "Authentication requirement"

    fr002 = registry.records["SPEC-004.FR-002"]
    assert fr002.category == "security/auth"

    nf001 = registry.records["SPEC-004.NF-001"]
    assert nf001.category == "perf.db"

    # Whitespace should be stripped
    fr003 = registry.records["SPEC-004.FR-003"]
    assert fr003.category == "whitespace"

    # No category should be None
    fr004 = registry.records["SPEC-004.FR-004"]
    assert fr004.category is None

    # Qualified format with category
    fr005 = registry.records["SPEC-004.FR-005"]
    assert fr005.category == "storage"

  def test_category_parsing_frontmatter(self) -> None:
    """VT-017-001: Test category extraction from frontmatter."""
    root = self._make_repo()

    # Create spec with frontmatter category
    spec_dir = root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR / "spec-005-example"
    spec_dir.mkdir(parents=True, exist_ok=True)
    spec_path = spec_dir / "SPEC-005.md"
    frontmatter = {
      "id": "SPEC-005",
      "slug": "spec-005",
      "name": "Spec with frontmatter category",
      "created": "2024-06-01",
      "updated": "2024-06-01",
      "status": "draft",
      "kind": "spec",
      "category": "security",
    }
    body = (
      "# SPEC-005\n\n"
      "## 6. Requirements\n\n"
      "- **FR-001**: Requirement inherits frontmatter category\n"
      "- **FR-002**(auth): Inline category overrides frontmatter\n"
    )
    dump_markdown_file(spec_path, frontmatter, body)

    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    spec_registry = SpecRegistry(root)
    spec_registry.reload()

    _stats = registry.sync_from_specs(
      [root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR],
      spec_registry=spec_registry,
    )
    registry.save()

    # Verify frontmatter category inheritance
    fr001 = registry.records["SPEC-005.FR-001"]
    assert fr001.category == "security"

    # Verify inline category takes precedence over frontmatter
    fr002 = registry.records["SPEC-005.FR-002"]
    assert fr002.category == "auth"

  def test_category_merge_precedence(self) -> None:
    """VT-017-002: Test category merge with body precedence."""
    # Create two RequirementRecords and test merge behavior
    existing = RequirementRecord(
      uid="SPEC-001.FR-001",
      label="FR-001",
      title="Existing requirement",
      primary_spec="SPEC-001",
      category="existing-category",
      status=STATUS_ACTIVE,
    )

    # Test 1: New record has category (should override)
    new_with_category = RequirementRecord(
      uid="SPEC-001.FR-001",
      label="FR-001",
      title="Updated requirement",
      primary_spec="SPEC-001",
      category="new-category",
    )
    merged = existing.merge(new_with_category)
    assert merged.category == "new-category"

    # Test 2: New record has no category (should keep existing)
    new_without_category = RequirementRecord(
      uid="SPEC-001.FR-001",
      label="FR-001",
      title="Updated requirement",
      primary_spec="SPEC-001",
      category=None,
    )
    merged = existing.merge(new_without_category)
    assert merged.category == "existing-category"

    # Test 3: Neither has category
    no_category_1 = RequirementRecord(
      uid="SPEC-001.FR-001",
      label="FR-001",
      title="No category 1",
      primary_spec="SPEC-001",
      category=None,
    )
    no_category_2 = RequirementRecord(
      uid="SPEC-001.FR-001",
      label="FR-001",
      title="No category 2",
      primary_spec="SPEC-001",
      category=None,
    )
    merged = no_category_1.merge(no_category_2)
    assert merged.category is None

  def test_category_serialization_round_trip(self) -> None:
    """VT-017-002: Test category survives serialization round-trip."""
    record = RequirementRecord(
      uid="SPEC-001.FR-001",
      label="FR-001",
      title="Test requirement",
      primary_spec="SPEC-001",
      category="test-category",
    )

    # Serialize to dict
    data = record.to_dict()
    assert data["category"] == "test-category"

    # Deserialize from dict
    restored = RequirementRecord.from_dict("SPEC-001.FR-001", data)
    assert restored.category == "test-category"

    # Test with None category
    record_no_cat = RequirementRecord(
      uid="SPEC-001.FR-002",
      label="FR-002",
      title="No category",
      primary_spec="SPEC-001",
      category=None,
    )
    data_no_cat = record_no_cat.to_dict()
    assert data_no_cat["category"] is None

    restored_no_cat = RequirementRecord.from_dict("SPEC-001.FR-002", data_no_cat)
    assert restored_no_cat.category is None


class TestSourceKindFields(unittest.TestCase):
  """VT-UPSERT-076-003 / VT-COMPAT-076-005: source fields."""

  def test_defaults_to_empty(self) -> None:
    record = RequirementRecord(uid="SPEC-100.FR-001", label="FR-001", title="Test")
    assert record.source_kind == ""
    assert record.source_type == ""

  def test_to_dict_omits_when_empty(self) -> None:
    record = RequirementRecord(uid="SPEC-100.FR-001", label="FR-001", title="Test")
    d = record.to_dict()
    assert "source_kind" not in d
    assert "source_type" not in d

  def test_to_dict_includes_when_set(self) -> None:
    record = RequirementRecord(
      uid="ISSUE-016.FR-016.001",
      label="FR-016.001",
      title="Test",
      source_kind="issue",
      source_type="backlog",
    )
    d = record.to_dict()
    assert d["source_kind"] == "issue"
    assert d["source_type"] == "backlog"

  def test_from_dict_defaults_missing(self) -> None:
    record = RequirementRecord.from_dict(
      "SPEC-100.FR-001",
      {"label": "FR-001", "title": "T"},
    )
    assert record.source_kind == ""
    assert record.source_type == ""

  def test_from_dict_reads_present(self) -> None:
    record = RequirementRecord.from_dict(
      "ISSUE-016.FR-016.001",
      {
        "label": "FR-016.001",
        "title": "T",
        "source_kind": "issue",
        "source_type": "backlog",
      },
    )
    assert record.source_kind == "issue"
    assert record.source_type == "backlog"

  def test_merge_incoming_wins(self) -> None:
    old = RequirementRecord(
      uid="X.FR-001",
      label="FR-001",
      title="Old",
      source_kind="",
      source_type="",
    )
    new = RequirementRecord(
      uid="X.FR-001",
      label="FR-001",
      title="New",
      source_kind="issue",
      source_type="backlog",
    )
    merged = old.merge(new)
    assert merged.source_kind == "issue"
    assert merged.source_type == "backlog"

  def test_merge_preserves_existing_when_incoming_empty(self) -> None:
    old = RequirementRecord(
      uid="X.FR-001",
      label="FR-001",
      title="Old",
      source_kind="spec",
      source_type="tech",
    )
    new = RequirementRecord(uid="X.FR-001", label="FR-001", title="New")
    merged = old.merge(new)
    assert merged.source_kind == "spec"
    assert merged.source_type == "tech"

  def test_roundtrip_serialization(self) -> None:
    original = RequirementRecord(
      uid="ISSUE-016.FR-016.001",
      label="FR-016.001",
      title="Backlog req",
      source_kind="issue",
      source_type="backlog",
    )
    d = original.to_dict()
    restored = RequirementRecord.from_dict(original.uid, d)
    assert restored.source_kind == original.source_kind
    assert restored.source_type == original.source_type


class TestUpsertRecordProvenance(unittest.TestCase):
  """VT-UPSERT-076-003: _upsert_record stamps source provenance."""

  def setUp(self) -> None:
    self._cwd = Path.cwd()
    self.tmpdir = tempfile.mkdtemp()
    os.chdir(self.tmpdir)

  def tearDown(self) -> None:
    os.chdir(self._cwd)

  def test_upsert_stamps_source_kind_on_create(self) -> None:
    registry_path = Path(self.tmpdir) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    record = RequirementRecord(uid="X.FR-001", label="FR-001", title="Test")
    seen: set[str] = set()
    stats = SyncStats()
    _upsert_record(
      registry.records,
      record,
      seen,
      stats,
      source_kind="issue",
      source_type="backlog",
    )

    assert registry.records["X.FR-001"].source_kind == "issue"
    assert registry.records["X.FR-001"].source_type == "backlog"
    assert "X.FR-001" in seen
    assert stats.created == 1

  def test_upsert_stamps_source_kind_on_merge(self) -> None:
    registry_path = Path(self.tmpdir) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    registry.records["X.FR-001"] = RequirementRecord(
      uid="X.FR-001",
      label="FR-001",
      title="Old",
    )
    record = RequirementRecord(uid="X.FR-001", label="FR-001", title="New")
    seen: set[str] = set()
    stats = SyncStats()
    _upsert_record(
      registry.records,
      record,
      seen,
      stats,
      source_kind="problem",
      source_type="backlog",
    )

    assert registry.records["X.FR-001"].source_kind == "problem"
    assert registry.records["X.FR-001"].source_type == "backlog"
    assert stats.updated == 1


class TestBacklogRequirementSync(unittest.TestCase):
  """VT-SYNC-076-002: Backlog items synced to requirements registry."""

  def setUp(self) -> None:
    self._cwd = Path.cwd()
    self.tmpdir = tempfile.mkdtemp()
    self.root = Path(self.tmpdir)
    os.chdir(self.tmpdir)

  def tearDown(self) -> None:
    os.chdir(self._cwd)

  def _make_backlog_item(self, item_id: str, kind: str, body: str) -> Path:
    """Create a minimal backlog item file and return its path."""
    backlog_dir = self.root / SPEC_DRIVER_DIR / "backlog" / f"{kind}s"
    item_dir = backlog_dir / f"{item_id}-test"
    item_dir.mkdir(parents=True, exist_ok=True)
    item_path = item_dir / f"{item_id}.md"
    frontmatter = {
      "id": item_id,
      "title": f"Test {kind}",
      "status": "open",
      "kind": kind,
    }
    dump_markdown_file(item_path, frontmatter, body)
    return item_path

  def test_sync_discovers_backlog_requirements(self) -> None:
    """Backlog items with heading-format requirements appear in registry."""

    item_path = self._make_backlog_item(
      "ISSUE-016",
      "issue",
      textwrap.dedent("""\
        ## Requirements

        ### FR-016.001: Registry discovers backlog requirements
        ### NF-016.001: Backward compatibility preserved
      """),
    )

    # Mock BacklogRegistry
    mock_backlog = MagicMock()
    mock_item = MagicMock()
    mock_item.id = "ISSUE-016"
    mock_item.kind = "issue"
    mock_item.path = item_path
    mock_backlog.iter.return_value = [mock_item]

    registry_path = self.root / SPEC_DRIVER_DIR / "registry" / "requirements.yaml"
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry = RequirementsRegistry(registry_path)

    stats = registry.sync(backlog_registry=mock_backlog)

    assert stats.created == 2
    assert "ISSUE-016.FR-016.001" in registry.records
    assert "ISSUE-016.NF-016.001" in registry.records

    fr = registry.records["ISSUE-016.FR-016.001"]
    assert fr.source_kind == "issue"
    assert fr.source_type == "backlog"
    assert fr.label == "FR-016.001"
    assert fr.title == "Registry discovers backlog requirements"

  def test_sync_backlog_records_in_seen_set(self) -> None:
    """Backlog-sourced records are added to seen and not purged by cleanup."""

    item_path = self._make_backlog_item(
      "PROB-001",
      "problem",
      "### FR-001.001: Problem requirement\n",
    )

    mock_backlog = MagicMock()
    mock_item = MagicMock()
    mock_item.id = "PROB-001"
    mock_item.kind = "problem"
    mock_item.path = item_path
    mock_backlog.iter.return_value = [mock_item]

    registry_path = self.root / SPEC_DRIVER_DIR / "registry" / "requirements.yaml"
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry = RequirementsRegistry(registry_path)

    registry.sync(backlog_registry=mock_backlog)

    # Record exists after sync (not purged by cleanup)
    assert "PROB-001.FR-001.001" in registry.records
    assert registry.records["PROB-001.FR-001.001"].source_kind == "problem"


class TestBreakoutFrontmatterSync(unittest.TestCase):
  """DE-095: Sync reads tags/ext_id/ext_url from breakout requirement files."""

  def _make_repo(self) -> Path:
    root = Path(tempfile.mkdtemp())
    (root / ".git").mkdir()
    return root

  def _write_spec(self, root: Path, spec_id: str, body: str) -> Path:
    spec_dir = root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR / spec_id.lower()
    spec_dir.mkdir(parents=True, exist_ok=True)
    dump_markdown_file(
      spec_dir / f"{spec_id}.md",
      {"id": spec_id, "status": "draft", "kind": "spec"},
      body,
    )
    return root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR

  def _write_breakout(
    self,
    root: Path,
    spec_id: str,
    req_id: str,
    frontmatter: dict,
  ) -> None:
    spec_dir = root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR / spec_id.lower()
    req_dir = spec_dir / "requirements"
    req_dir.mkdir(parents=True, exist_ok=True)
    fm = {
      "id": f"{spec_id}.{req_id}",
      "status": "draft",
      "kind": "requirement",
      **frontmatter,
    }
    dump_markdown_file(req_dir / f"{req_id}.md", fm, f"# {req_id}\n")

  def test_breakout_tags_merged_with_inline(self) -> None:
    """Frontmatter tags from breakout file merge with inline tags."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    body = textwrap.dedent("""\
      ## Requirements
      - **FR-001**[inline-tag]: Requirement with inline tag
    """)
    specs_root = self._write_spec(root, "SPEC-900", body)
    self._write_breakout(
      root, "SPEC-900", "FR-001", {"tags": ["breakout-tag", "inline-tag"]}
    )

    registry.sync(spec_dirs=[specs_root])

    record = registry.records["SPEC-900.FR-001"]
    assert record.tags == ["breakout-tag", "inline-tag"]

  def test_breakout_ext_id_and_ext_url(self) -> None:
    """ext_id/ext_url from breakout frontmatter populate the record."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    body = textwrap.dedent("""\
      ## Requirements
      - **FR-001**: A requirement
    """)
    specs_root = self._write_spec(root, "SPEC-901", body)
    self._write_breakout(
      root,
      "SPEC-901",
      "FR-001",
      {"ext_id": "JIRA-42", "ext_url": "https://jira.example.com/JIRA-42"},
    )

    registry.sync(spec_dirs=[specs_root])

    record = registry.records["SPEC-901.FR-001"]
    assert record.ext_id == "JIRA-42"
    assert record.ext_url == "https://jira.example.com/JIRA-42"

  def test_breakout_without_metadata_no_effect(self) -> None:
    """Breakout file without tags/ext_id/ext_url leaves record unchanged."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    body = textwrap.dedent("""\
      ## Requirements
      - **FR-001**: Plain requirement
    """)
    specs_root = self._write_spec(root, "SPEC-902", body)
    self._write_breakout(root, "SPEC-902", "FR-001", {})

    registry.sync(spec_dirs=[specs_root])

    record = registry.records["SPEC-902.FR-001"]
    assert record.tags == []
    assert record.ext_id == ""
    assert record.ext_url == ""

  def test_breakout_tags_only(self) -> None:
    """Breakout with tags but no ext fields."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    body = textwrap.dedent("""\
      ## Requirements
      - **FR-001**: Tagged requirement
    """)
    specs_root = self._write_spec(root, "SPEC-903", body)
    self._write_breakout(root, "SPEC-903", "FR-001", {"tags": ["security", "auth"]})

    registry.sync(spec_dirs=[specs_root])

    record = registry.records["SPEC-903.FR-001"]
    assert record.tags == ["auth", "security"]
    assert record.ext_id == ""

  def test_breakout_via_spec_registry(self) -> None:
    """Breakout enrichment works through spec_registry path too."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    body = textwrap.dedent("""\
      ## Requirements
      - **FR-001**: Requirement
    """)
    # Write spec with full frontmatter for SpecRegistry
    spec_dir = root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR / "spec-904"
    spec_dir.mkdir(parents=True, exist_ok=True)
    dump_markdown_file(
      spec_dir / "SPEC-904.md",
      {
        "id": "SPEC-904",
        "slug": "spec-904",
        "name": "Test Spec",
        "status": "draft",
        "kind": "spec",
        "created": "2025-01-01",
        "updated": "2025-01-01",
      },
      body,
    )
    self._write_breakout(
      root,
      "SPEC-904",
      "FR-001",
      {"ext_id": "GH-77", "tags": ["ci"]},
    )

    spec_registry = SpecRegistry(root)
    registry.sync(spec_registry=spec_registry)

    record = registry.records["SPEC-904.FR-001"]
    assert record.ext_id == "GH-77"
    assert record.tags == ["ci"]


class TestSyncStatsFields(unittest.TestCase):
  """DE-129 Phase 2: SyncStats has pruned and warnings fields."""

  def test_defaults_to_zero(self) -> None:
    stats = SyncStats()
    assert stats.pruned == 0
    assert stats.warnings == 0

  def test_fields_are_mutable(self) -> None:
    stats = SyncStats()
    stats.pruned = 3
    stats.warnings = 2
    assert stats.pruned == 3
    assert stats.warnings == 2


class TestStaleRequirementPruning(unittest.TestCase):
  """DE-129 Phase 2: Post-relation stale requirement pruning."""

  def setUp(self) -> None:
    self._cwd = Path.cwd()

  def tearDown(self) -> None:
    os.chdir(self._cwd)

  def _write_spec(self, root: Path, spec_id: str, body: str) -> Path:
    spec_dir = root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR / f"{spec_id.lower()}-test"
    spec_dir.mkdir(parents=True, exist_ok=True)
    spec_path = spec_dir / f"{spec_id}.md"
    frontmatter = {
      "id": spec_id,
      "slug": spec_id.lower(),
      "name": f"Spec {spec_id}",
      "created": "2024-06-01",
      "updated": "2024-06-01",
      "status": "draft",
      "kind": "spec",
    }
    dump_markdown_file(spec_path, frontmatter, body)
    return spec_path

  def _make_repo(self, body: str = "") -> Path:
    tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.addCleanup(tmpdir.cleanup)
    root = Path(tmpdir.name)
    (root / ".git").mkdir()
    if not body:
      body = (
        "# SPEC-001\n\n"
        "- **FR-001**: First requirement\n"
        "- **FR-002**: Second requirement\n"
      )
    self._write_spec(root, "SPEC-001", body)
    os.chdir(root)
    return root

  def test_deleted_requirement_is_pruned(self) -> None:
    """Requirement removed from spec body is pruned from registry."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    spec_registry = SpecRegistry(root)

    # First sync — both requirements present
    stats = registry.sync(spec_registry=spec_registry)
    registry.save()
    assert stats.created == 2
    assert "SPEC-001.FR-001" in registry.records
    assert "SPEC-001.FR-002" in registry.records

    # Remove FR-002 from spec body
    spec_path = (
      root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR / "spec-001-test" / "SPEC-001.md"
    )
    dump_markdown_file(
      spec_path,
      {
        "id": "SPEC-001",
        "slug": "spec-001",
        "name": "Spec SPEC-001",
        "created": "2024-06-01",
        "updated": "2024-06-01",
        "status": "draft",
        "kind": "spec",
      },
      "# SPEC-001\n\n- **FR-001**: First requirement\n",
    )

    # Re-sync — FR-002 should be pruned
    registry = RequirementsRegistry(registry_path)
    spec_registry.reload()
    stats = registry.sync(spec_registry=spec_registry)
    registry.save()

    assert stats.pruned == 1
    assert "SPEC-001.FR-001" in registry.records
    assert "SPEC-001.FR-002" not in registry.records

  def test_revision_introduced_requirement_not_pruned(self) -> None:
    """Requirements with `introduced` set are preserved even when absent from body."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    spec_registry = SpecRegistry(root)

    # First sync
    registry.sync(spec_registry=spec_registry)
    registry.save()

    # Manually set `introduced` on FR-002 (simulating revision block)
    registry.records["SPEC-001.FR-002"].introduced = "RE-050"
    registry.save()

    # Remove FR-002 from spec body
    spec_path = (
      root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR / "spec-001-test" / "SPEC-001.md"
    )
    dump_markdown_file(
      spec_path,
      {
        "id": "SPEC-001",
        "slug": "spec-001",
        "name": "Spec SPEC-001",
        "created": "2024-06-01",
        "updated": "2024-06-01",
        "status": "draft",
        "kind": "spec",
      },
      "# SPEC-001\n\n- **FR-001**: First requirement\n",
    )

    # Re-sync — FR-002 should NOT be pruned (has introduced)
    registry = RequirementsRegistry(registry_path)
    spec_registry.reload()
    stats = registry.sync(spec_registry=spec_registry)
    registry.save()

    assert stats.pruned == 0
    assert "SPEC-001.FR-001" in registry.records
    assert "SPEC-001.FR-002" in registry.records

  def test_backlog_sourced_requirement_not_pruned(self) -> None:
    """Backlog-sourced requirements are not pruned (primary_spec is backlog ID)."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    # Pre-populate a backlog-sourced requirement
    registry.records["ISSUE-016.FR-016.001"] = RequirementRecord(
      uid="ISSUE-016.FR-016.001",
      label="FR-016.001",
      title="Backlog requirement",
      primary_spec="ISSUE-016",
      source_type="backlog",
    )
    registry.save()

    spec_registry = SpecRegistry(root)
    registry.sync(spec_registry=spec_registry)
    registry.save()

    # Backlog requirement should survive — its primary_spec doesn't match any spec
    assert "ISSUE-016.FR-016.001" in registry.records

  def test_pruning_idempotent(self) -> None:
    """Re-running sync after pruning produces no further changes (NF-002)."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    spec_registry = SpecRegistry(root)

    # First sync
    registry.sync(spec_registry=spec_registry)
    registry.save()

    # Remove FR-002
    spec_path = (
      root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR / "spec-001-test" / "SPEC-001.md"
    )
    dump_markdown_file(
      spec_path,
      {
        "id": "SPEC-001",
        "slug": "spec-001",
        "name": "Spec SPEC-001",
        "created": "2024-06-01",
        "updated": "2024-06-01",
        "status": "draft",
        "kind": "spec",
      },
      "# SPEC-001\n\n- **FR-001**: First requirement\n",
    )

    # First prune
    registry = RequirementsRegistry(registry_path)
    spec_registry.reload()
    stats1 = registry.sync(spec_registry=spec_registry)
    registry.save()
    assert stats1.pruned == 1

    # Second sync — should be idempotent
    registry = RequirementsRegistry(registry_path)
    spec_registry.reload()
    stats2 = registry.sync(spec_registry=spec_registry)
    registry.save()
    assert stats2.pruned == 0
    assert stats2.created == 0

  def test_revision_moved_requirement_not_pruned_from_old_spec(self) -> None:
    """Requirement moved by revision block is not pruned from old spec.

    This is the critical test for ext. review F1: pruning runs after
    revision blocks have updated primary_spec, so the moved requirement
    no longer belongs to the source spec's pruning scope.
    """
    root = self._make_repo(
      body="# SPEC-001\n\n- **FR-001**: First requirement\n",
    )
    self._write_spec(
      root,
      "SPEC-002",
      "# SPEC-002\n\n- **FR-010**: Other requirement\n",
    )

    # Write a revision that moves SPEC-001.FR-001 → SPEC-002.FR-001
    slug = "re-050-bundle"
    bundle_dir = root / SPEC_DRIVER_DIR / REVISIONS_SUBDIR / slug
    bundle_dir.mkdir(parents=True, exist_ok=True)
    revision_path = bundle_dir / "RE-050.md"
    block_yaml = textwrap.dedent("""\
      schema: supekku.revision.change
      version: 1
      metadata:
        revision: RE-050
      specs: []
      requirements:
        - requirement_id: SPEC-002.FR-001
          kind: functional
          action: move
          origin:
            - kind: requirement
              ref: SPEC-001.FR-001
          destination:
            spec: SPEC-002
            requirement_id: SPEC-002.FR-001
          lifecycle:
            status: in-progress
            introduced_by: RE-050
    """)
    dump_markdown_file(
      revision_path,
      {
        "id": "RE-050",
        "slug": "re-050",
        "name": "RE-050",
        "created": "2024-06-01",
        "updated": "2024-06-01",
        "status": "draft",
        "kind": "revision",
      },
      f"# RE-050\n\n```yaml supekku:revision.change@v1\n{block_yaml}```\n",
    )

    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    spec_registry = SpecRegistry(root)
    registry.sync(
      spec_registry=spec_registry,
      revision_dirs=[root / SPEC_DRIVER_DIR / REVISIONS_SUBDIR],
    )
    registry.save()

    # The moved requirement should exist under SPEC-002, not be pruned
    assert "SPEC-002.FR-001" in registry.records
    record = registry.records["SPEC-002.FR-001"]
    assert record.primary_spec == "SPEC-002"
    assert record.introduced == "RE-050"
    # Original SPEC-001.FR-001 was renamed/moved, should not exist
    assert "SPEC-001.FR-001" not in registry.records

  def test_pruning_via_spec_dirs_path(self) -> None:
    """Pruning works through the spec_dirs fallback extraction path."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    # Sync via spec_dirs (no spec_registry)
    spec_dirs = [root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR]
    stats = registry.sync(spec_dirs=spec_dirs)
    registry.save()
    assert stats.created == 2

    # Remove FR-002
    spec_path = (
      root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR / "spec-001-test" / "SPEC-001.md"
    )
    dump_markdown_file(
      spec_path,
      {
        "id": "SPEC-001",
        "slug": "spec-001",
        "name": "Spec SPEC-001",
        "created": "2024-06-01",
        "updated": "2024-06-01",
        "status": "draft",
        "kind": "spec",
      },
      "# SPEC-001\n\n- **FR-001**: First requirement\n",
    )

    # Re-sync via spec_dirs
    registry = RequirementsRegistry(registry_path)
    stats = registry.sync(spec_dirs=spec_dirs)
    registry.save()

    assert stats.pruned == 1
    assert "SPEC-001.FR-001" in registry.records
    assert "SPEC-001.FR-002" not in registry.records


class TestPlaceholderRecordSourceType(unittest.TestCase):
  """DE-129 Phase 2: _create_placeholder_record stamps source_type='revision'."""

  def setUp(self) -> None:
    self._cwd = Path.cwd()

  def tearDown(self) -> None:
    os.chdir(self._cwd)

  def test_placeholder_has_revision_source_type(self) -> None:
    """Revision-created placeholder records have source_type='revision'."""
    tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.addCleanup(tmpdir.cleanup)
    root = Path(tmpdir.name)
    (root / ".git").mkdir()
    os.chdir(root)

    # Create a minimal spec
    spec_dir = root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR / "spec-001-test"
    spec_dir.mkdir(parents=True, exist_ok=True)
    dump_markdown_file(
      spec_dir / "SPEC-001.md",
      {
        "id": "SPEC-001",
        "slug": "spec-001",
        "name": "Spec SPEC-001",
        "created": "2024-06-01",
        "updated": "2024-06-01",
        "status": "draft",
        "kind": "spec",
      },
      "# SPEC-001\n",
    )

    # Revision that introduces a new requirement (not in spec body)
    slug = "re-060-bundle"
    bundle_dir = root / SPEC_DRIVER_DIR / REVISIONS_SUBDIR / slug
    bundle_dir.mkdir(parents=True, exist_ok=True)
    block_yaml = textwrap.dedent("""\
      schema: supekku.revision.change
      version: 1
      metadata:
        revision: RE-060
      specs: []
      requirements:
        - requirement_id: SPEC-001.FR-099
          kind: functional
          action: introduce
          destination:
            spec: SPEC-001
            requirement_id: SPEC-001.FR-099
          lifecycle:
            status: pending
            introduced_by: RE-060
    """)
    dump_markdown_file(
      bundle_dir / "RE-060.md",
      {
        "id": "RE-060",
        "slug": "re-060",
        "name": "RE-060",
        "created": "2024-06-01",
        "updated": "2024-06-01",
        "status": "draft",
        "kind": "revision",
      },
      f"# RE-060\n\n```yaml supekku:revision.change@v1\n{block_yaml}```\n",
    )

    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    spec_registry = SpecRegistry(root)
    registry.sync(
      spec_registry=spec_registry,
      revision_dirs=[root / SPEC_DRIVER_DIR / REVISIONS_SUBDIR],
    )

    record = registry.records["SPEC-001.FR-099"]
    assert record.source_type == "revision"
    assert record.introduced == "RE-060"


class TestSyncSummaryLine(unittest.TestCase):
  """DE-129 Phase 2: Sync summary line with log-level discipline."""

  def setUp(self) -> None:
    self._cwd = Path.cwd()

  def tearDown(self) -> None:
    os.chdir(self._cwd)

  def test_clean_sync_emits_info(self) -> None:
    """When no warnings/pruning, summary is at info level."""
    tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.addCleanup(tmpdir.cleanup)
    root = Path(tmpdir.name)
    (root / ".git").mkdir()
    os.chdir(root)

    spec_dir = root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR / "spec-001-test"
    spec_dir.mkdir(parents=True, exist_ok=True)
    dump_markdown_file(
      spec_dir / "SPEC-001.md",
      {
        "id": "SPEC-001",
        "slug": "spec-001",
        "name": "Spec SPEC-001",
        "created": "2024-06-01",
        "updated": "2024-06-01",
        "status": "draft",
        "kind": "spec",
      },
      "# SPEC-001\n\n- **FR-001**: First requirement\n",
    )

    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    spec_registry = SpecRegistry(root)

    import logging  # noqa: PLC0415

    with self.assertLogs(
      "supekku.scripts.lib.requirements.registry",
      level=logging.INFO,
    ) as cm:
      stats = registry.sync(spec_registry=spec_registry)

    assert stats.warnings == 0
    assert stats.pruned == 0
    # Summary should be at INFO, not WARNING
    summary_logs = [r for r in cm.output if "Sync complete" in r]
    assert len(summary_logs) == 1
    assert summary_logs[0].startswith("INFO:")

  def test_sync_with_warnings_emits_warning(self) -> None:
    """When warnings exist, summary is at warning level."""
    tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.addCleanup(tmpdir.cleanup)
    root = Path(tmpdir.name)
    (root / ".git").mkdir()
    os.chdir(root)

    # Spec with compound IDs that produce a collision warning
    spec_dir = root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR / "spec-001-test"
    spec_dir.mkdir(parents=True, exist_ok=True)
    dump_markdown_file(
      spec_dir / "SPEC-001.md",
      {
        "id": "SPEC-001",
        "slug": "spec-001",
        "name": "Spec SPEC-001",
        "created": "2024-06-01",
        "updated": "2024-06-01",
        "status": "draft",
        "kind": "spec",
      },
      "# SPEC-001\n\n"
      "- **FR-001**: First requirement\n"
      "- **FR-001**: Duplicate requirement\n",
    )

    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    spec_registry = SpecRegistry(root)

    import logging  # noqa: PLC0415

    with self.assertLogs(
      "supekku.scripts.lib.requirements",
      level=logging.INFO,
    ) as cm:
      stats = registry.sync(spec_registry=spec_registry)

    assert stats.warnings >= 1
    summary_logs = [r for r in cm.output if "Sync complete" in r]
    assert len(summary_logs) == 1
    assert summary_logs[0].startswith("WARNING:")
    assert "warnings" in summary_logs[0]

  def test_sync_with_pruning_emits_warning(self) -> None:
    """When pruning occurs, summary is at warning level."""
    tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.addCleanup(tmpdir.cleanup)
    root = Path(tmpdir.name)
    (root / ".git").mkdir()
    os.chdir(root)

    spec_dir = root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR / "spec-001-test"
    spec_dir.mkdir(parents=True, exist_ok=True)
    dump_markdown_file(
      spec_dir / "SPEC-001.md",
      {
        "id": "SPEC-001",
        "slug": "spec-001",
        "name": "Spec SPEC-001",
        "created": "2024-06-01",
        "updated": "2024-06-01",
        "status": "draft",
        "kind": "spec",
      },
      "# SPEC-001\n\n- **FR-001**: First\n- **FR-002**: Second\n",
    )

    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    spec_registry = SpecRegistry(root)

    # First sync
    registry.sync(spec_registry=spec_registry)
    registry.save()

    # Remove FR-002
    dump_markdown_file(
      spec_dir / "SPEC-001.md",
      {
        "id": "SPEC-001",
        "slug": "spec-001",
        "name": "Spec SPEC-001",
        "created": "2024-06-01",
        "updated": "2024-06-01",
        "status": "draft",
        "kind": "spec",
      },
      "# SPEC-001\n\n- **FR-001**: First\n",
    )

    import logging  # noqa: PLC0415

    registry = RequirementsRegistry(registry_path)
    spec_registry.reload()
    with self.assertLogs(
      "supekku.scripts.lib.requirements.registry",
      level=logging.INFO,
    ) as cm:
      stats = registry.sync(spec_registry=spec_registry)

    assert stats.pruned == 1
    summary_logs = [r for r in cm.output if "Sync complete" in r]
    assert len(summary_logs) == 1
    assert summary_logs[0].startswith("WARNING:")


class TestWarningCounting(unittest.TestCase):
  """DE-129 Phase 2: SyncStats.warnings incremented by parser diagnostics."""

  def setUp(self) -> None:
    self._cwd = Path.cwd()

  def tearDown(self) -> None:
    os.chdir(self._cwd)

  def test_collision_increments_warnings(self) -> None:
    """Duplicate requirement ID increments stats.warnings."""
    tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.addCleanup(tmpdir.cleanup)
    root = Path(tmpdir.name)
    (root / ".git").mkdir()
    os.chdir(root)

    spec_dir = root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR / "spec-001-test"
    spec_dir.mkdir(parents=True, exist_ok=True)
    dump_markdown_file(
      spec_dir / "SPEC-001.md",
      {
        "id": "SPEC-001",
        "slug": "spec-001",
        "name": "Spec SPEC-001",
        "created": "2024-06-01",
        "updated": "2024-06-01",
        "status": "draft",
        "kind": "spec",
      },
      "# SPEC-001\n\n- **FR-001**: First\n- **FR-001**: Duplicate\n",
    )

    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    spec_registry = SpecRegistry(root)
    stats = registry.sync(spec_registry=spec_registry)

    assert stats.warnings >= 1

  def test_frontmatter_definitions_increments_warnings(self) -> None:
    """Frontmatter requirement definitions increment stats.warnings."""
    tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.addCleanup(tmpdir.cleanup)
    root = Path(tmpdir.name)
    (root / ".git").mkdir()
    os.chdir(root)

    spec_dir = root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR / "spec-001-test"
    spec_dir.mkdir(parents=True, exist_ok=True)
    dump_markdown_file(
      spec_dir / "SPEC-001.md",
      {
        "id": "SPEC-001",
        "slug": "spec-001",
        "name": "Spec SPEC-001",
        "created": "2024-06-01",
        "updated": "2024-06-01",
        "status": "draft",
        "kind": "spec",
        "requirements": [
          {"id": "FR-001", "description": "Ignored requirement"},
        ],
      },
      "# SPEC-001\n\n- **FR-001**: Body requirement\n",
    )

    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    spec_registry = SpecRegistry(root)
    stats = registry.sync(spec_registry=spec_registry)

    assert stats.warnings >= 1


if __name__ == "__main__":
  unittest.main()
