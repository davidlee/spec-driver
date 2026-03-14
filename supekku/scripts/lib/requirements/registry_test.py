"""Tests for requirements module."""

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
from supekku.scripts.lib.requirements.lifecycle import (
  STATUS_ACTIVE,
  STATUS_DEPRECATED,
  STATUS_IN_PROGRESS,
  STATUS_PENDING,
  STATUS_SUPERSEDED,
  TERMINAL_STATUSES,
)
from supekku.scripts.lib.requirements.registry import (
  _REQUIREMENT_HEADING,
  RequirementRecord,
  RequirementsRegistry,
  SyncStats,
)
from supekku.scripts.lib.specs.registry import SpecRegistry


class TestRequirementRecordToDict(unittest.TestCase):
  """Tests for RequirementRecord.to_dict() serialization."""

  def test_to_dict_omits_ext_id_ext_url_when_empty(self) -> None:
    """Empty ext_id/ext_url should not appear in serialized dict."""
    record = RequirementRecord(uid="SPEC-100.FR-001", label="FR-001", title="Test")

    result = record.to_dict()

    assert "ext_id" not in result
    assert "ext_url" not in result

  def test_to_dict_includes_ext_id_ext_url_when_set(self) -> None:
    """Populated ext_id/ext_url should appear in serialized dict."""
    record = RequirementRecord(
      uid="SPEC-100.FR-002",
      label="FR-002",
      title="External Req",
      ext_id="JIRA-1234",
      ext_url="https://jira.example.com/JIRA-1234",
    )

    result = record.to_dict()

    assert result["ext_id"] == "JIRA-1234"
    assert result["ext_url"] == "https://jira.example.com/JIRA-1234"

  def test_to_dict_ext_id_only(self) -> None:
    """ext_id without ext_url — only ext_id appears."""
    record = RequirementRecord(
      uid="SPEC-100.FR-003",
      label="FR-003",
      title="ID-Only",
      ext_id="GH-99",
    )

    result = record.to_dict()

    assert result["ext_id"] == "GH-99"
    assert "ext_url" not in result


class RequirementsRegistryTest(unittest.TestCase):
  """Test cases for RequirementsRegistry functionality."""

  def setUp(self) -> None:
    self._cwd = Path.cwd()

  def tearDown(self) -> None:
    os.chdir(self._cwd)

  def _write_spec(self, root: Path, spec_id: str, body: str) -> None:
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
    spec_files = list(registry._iter_spec_files([coverage_dir]))
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
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    # All verified → active
    entries = [{"status": "verified"}, {"status": "verified"}]
    assert registry._compute_status_from_coverage(entries) == STATUS_ACTIVE

    # In-progress → in-progress
    entries = [{"status": "in-progress"}]
    assert registry._compute_status_from_coverage(entries) == STATUS_IN_PROGRESS

    # All planned → pending
    entries = [{"status": "planned"}]
    assert registry._compute_status_from_coverage(entries) == STATUS_PENDING

    # Failed → in-progress (needs attention)
    entries = [{"status": "failed"}]
    assert registry._compute_status_from_coverage(entries) == STATUS_IN_PROGRESS

    # Blocked → in-progress
    entries = [{"status": "blocked"}]
    assert registry._compute_status_from_coverage(entries) == STATUS_IN_PROGRESS

    # Mixed → in-progress
    entries = [{"status": "verified"}, {"status": "planned"}]
    assert registry._compute_status_from_coverage(entries) == STATUS_IN_PROGRESS

    # Empty → None
    entries = []
    assert registry._compute_status_from_coverage(entries) is None

  def test_compute_status_from_coverage_ignores_unknown_statuses(self) -> None:
    """VT-043-002: Unknown statuses are filtered out of derivation."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    # Unknown status alone → None (no valid statuses to derive from)
    entries = [{"status": "deferred"}]
    assert registry._compute_status_from_coverage(entries) is None

    # All unknown → None
    entries = [{"status": "deferred"}, {"status": "acknowledged"}]
    assert registry._compute_status_from_coverage(entries) is None

    # Valid + unknown: unknown is ignored, valid drives derivation
    entries = [{"status": "verified"}, {"status": "deferred"}]
    assert registry._compute_status_from_coverage(entries) == STATUS_ACTIVE

    # Multiple valid + unknown: derives from valid entries only
    entries = [
      {"status": "verified"},
      {"status": "deferred"},
      {"status": "planned"},
    ]
    assert registry._compute_status_from_coverage(entries) == STATUS_IN_PROGRESS

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


class TestRequirementsRegistryReverseQueries(unittest.TestCase):
  """Test reverse relationship query methods for RequirementsRegistry."""

  def setUp(self) -> None:
    self._cwd = Path.cwd()

  def tearDown(self) -> None:
    os.chdir(self._cwd)

  def _make_repo(self) -> Path:
    tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.addCleanup(tmpdir.cleanup)
    root = Path(tmpdir.name)
    (root / ".git").mkdir()
    os.chdir(root)
    return root

  def _write_spec_with_requirements(
    self, root: Path, spec_id: str, requirements: list[str]
  ) -> None:
    """Write a spec file with specific requirements."""
    spec_dir = root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR / f"{spec_id.lower()}-example"
    spec_dir.mkdir(parents=True, exist_ok=True)
    spec_path = spec_dir / f"{spec_id}.md"

    req_lines = "\n".join(f"- {req}" for req in requirements)
    body = f"# {spec_id}\n\n## 6. Quality & Operational Requirements\n\n{req_lines}\n"

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

  def _create_registry_with_verification(self, root: Path) -> RequirementsRegistry:
    """Create requirements registry and manually add verification metadata."""
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    spec_registry = SpecRegistry(root)

    spec_dirs = [root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR]
    registry.sync_from_specs(spec_dirs, spec_registry=spec_registry)

    # Manually add verification metadata to requirements
    # This simulates what would happen after coverage blocks are processed
    if "SPEC-001.FR-001" in registry.records:
      registry.records["SPEC-001.FR-001"].verified_by = ["VT-CLI-001"]
      registry.records["SPEC-001.FR-001"].coverage_evidence = ["VT-PROD010-001"]

    if "SPEC-001.FR-002" in registry.records:
      registry.records["SPEC-001.FR-002"].verified_by = ["VA-REVIEW-001"]
      registry.records["SPEC-001.FR-002"].coverage_evidence = []

    if "SPEC-001.NF-020" in registry.records:
      registry.records["SPEC-001.NF-020"].verified_by = []
      registry.records["SPEC-001.NF-020"].coverage_evidence = [
        "VT-CLI-001",
        "VT-CLI-002",
      ]

    return registry

  def test_find_by_verified_by_exact_match(self) -> None:
    """Test finding requirements verified by specific artifact (exact match)."""
    root = self._make_repo()
    self._write_spec_with_requirements(
      root, "SPEC-001", ["FR-001: First requirement", "FR-002: Second requirement"]
    )

    registry = self._create_registry_with_verification(root)

    # Find requirement verified by VT-CLI-001
    requirements = registry.find_by_verified_by("VT-CLI-001")

    assert isinstance(requirements, list)
    assert len(requirements) == 1
    assert requirements[0].uid == "SPEC-001.FR-001"

  def test_find_by_verified_by_searches_both_fields(self) -> None:
    """Test that find_by_verified_by searches both verified_by and coverage_evidence."""
    root = self._make_repo()
    self._write_spec_with_requirements(
      root,
      "SPEC-001",
      ["FR-001: First requirement", "NF-020: Performance requirement"],
    )

    registry = self._create_registry_with_verification(root)

    # VT-CLI-001 appears in verified_by for FR-001 and coverage_evidence for NF-020
    requirements = registry.find_by_verified_by("VT-CLI-001")

    assert isinstance(requirements, list)
    assert len(requirements) == 2
    uids = {r.uid for r in requirements}
    assert "SPEC-001.FR-001" in uids
    assert "SPEC-001.NF-020" in uids

  def test_find_by_verified_by_glob_pattern(self) -> None:
    """Test finding requirements with glob pattern matching."""
    root = self._make_repo()
    self._write_spec_with_requirements(
      root,
      "SPEC-001",
      [
        "FR-001: First requirement",
        "FR-002: Second requirement",
        "NF-020: Performance",
      ],
    )

    registry = self._create_registry_with_verification(root)

    # Find all requirements verified by VT-CLI-* pattern
    requirements = registry.find_by_verified_by("VT-CLI-*")

    assert isinstance(requirements, list)
    assert len(requirements) == 2  # FR-001 and NF-020 have VT-CLI artifacts
    uids = {r.uid for r in requirements}
    assert "SPEC-001.FR-001" in uids
    assert "SPEC-001.NF-020" in uids

  def test_find_by_verified_by_va_pattern(self) -> None:
    """Test finding requirements with VA (agent validation) artifacts."""
    root = self._make_repo()
    self._write_spec_with_requirements(root, "SPEC-001", ["FR-002: Second requirement"])

    registry = self._create_registry_with_verification(root)

    # Find requirements with VA artifacts
    requirements = registry.find_by_verified_by("VA-*")

    assert isinstance(requirements, list)
    assert len(requirements) == 1
    assert requirements[0].uid == "SPEC-001.FR-002"

  def test_find_by_verified_by_vt_prefix_pattern(self) -> None:
    """Test finding requirements with VT-PROD prefix."""
    root = self._make_repo()
    self._write_spec_with_requirements(root, "SPEC-001", ["FR-001: First requirement"])

    registry = self._create_registry_with_verification(root)

    # Find requirements verified by VT-PROD* artifacts
    requirements = registry.find_by_verified_by("VT-PROD*")

    assert isinstance(requirements, list)
    assert len(requirements) == 1
    assert requirements[0].uid == "SPEC-001.FR-001"

  def test_find_by_verified_by_nonexistent_artifact(self) -> None:
    """Test finding requirements for non-existent artifact returns empty list."""
    root = self._make_repo()
    self._write_spec_with_requirements(root, "SPEC-001", ["FR-001: First requirement"])

    registry = self._create_registry_with_verification(root)

    requirements = registry.find_by_verified_by("NONEXISTENT-ARTIFACT")

    assert isinstance(requirements, list)
    assert len(requirements) == 0

  def test_find_by_verified_by_none(self) -> None:
    """Test find_by_verified_by with None returns empty list."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    requirements = registry.find_by_verified_by(None)

    assert isinstance(requirements, list)
    assert len(requirements) == 0

  def test_find_by_verified_by_empty_string(self) -> None:
    """Test find_by_verified_by with empty string returns empty list."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    requirements = registry.find_by_verified_by("")

    assert isinstance(requirements, list)
    assert len(requirements) == 0

  def test_find_by_verified_by_returns_requirement_records(self) -> None:
    """Test that find_by_verified_by returns proper RequirementRecord objects."""
    root = self._make_repo()
    self._write_spec_with_requirements(root, "SPEC-001", ["FR-001: First requirement"])

    registry = self._create_registry_with_verification(root)

    requirements = registry.find_by_verified_by("VT-CLI-001")

    assert len(requirements) == 1
    req = requirements[0]

    # Verify it's a RequirementRecord with expected attributes
    assert isinstance(req, RequirementRecord)
    assert hasattr(req, "uid")
    assert hasattr(req, "label")
    assert hasattr(req, "title")
    assert hasattr(req, "verified_by")
    assert hasattr(req, "coverage_evidence")

  def test_find_by_verified_by_case_sensitive(self) -> None:
    """Test that artifact ID matching is case-sensitive."""
    root = self._make_repo()
    self._write_spec_with_requirements(root, "SPEC-001", ["FR-001: First requirement"])

    registry = self._create_registry_with_verification(root)

    # Correct case
    requirements_upper = registry.find_by_verified_by("VT-CLI-001")
    # Wrong case
    requirements_lower = registry.find_by_verified_by("vt-cli-001")

    assert len(requirements_upper) == 1
    assert len(requirements_lower) == 0

  def test_find_by_verified_by_glob_wildcard_positions(self) -> None:
    """Test glob patterns with wildcards in different positions."""
    root = self._make_repo()
    self._write_spec_with_requirements(
      root,
      "SPEC-001",
      ["FR-001: First", "FR-002: Second", "NF-020: Third"],
    )

    registry = self._create_registry_with_verification(root)

    # Test *-001 pattern (wildcard at start)
    requirements = registry.find_by_verified_by("*-001")
    uids = {r.uid for r in requirements}
    assert "SPEC-001.FR-001" in uids  # VT-CLI-001
    assert "SPEC-001.FR-002" in uids  # VA-REVIEW-001

    # Test VT-* pattern (wildcard at end)
    requirements = registry.find_by_verified_by("VT-*")
    uids = {r.uid for r in requirements}
    assert "SPEC-001.FR-001" in uids
    assert "SPEC-001.NF-020" in uids


class TestRequirementCoverageEntries(unittest.TestCase):
  """Test that coverage_entries field is populated during registry sync.

  After _apply_coverage_blocks(), each RequirementRecord should have a
  coverage_entries field containing the structured verification data
  (artefact, kind, status) from coverage blocks.
  """

  def setUp(self) -> None:
    self._cwd = Path.cwd()

  def tearDown(self) -> None:
    os.chdir(self._cwd)

  def _make_repo(self) -> Path:
    tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.addCleanup(tmpdir.cleanup)
    root = Path(tmpdir.name)
    (root / ".git").mkdir()
    os.chdir(root)
    return root

  def test_coverage_entries_populated_after_sync(self) -> None:
    """Syncing with coverage blocks populates coverage_entries on records."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    test_root = Path(__file__).parent.parent.parent.parent.parent
    coverage_dir = test_root / "tests" / "fixtures" / "requirements" / "coverage"

    registry.sync_from_specs(spec_dirs=[coverage_dir], plan_dirs=[coverage_dir])

    fr001 = registry.records["SPEC-900.FR-001"]
    assert hasattr(fr001, "coverage_entries"), (
      "RequirementRecord must have coverage_entries field"
    )
    assert isinstance(fr001.coverage_entries, list)
    assert len(fr001.coverage_entries) >= 1

    # Each entry should have artefact, kind, status
    entry = fr001.coverage_entries[0]
    assert "artefact" in entry
    assert "kind" in entry
    assert "status" in entry

  def test_coverage_entries_contain_correct_data(self) -> None:
    """Coverage entries preserve artefact ID, kind, and status from blocks."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    test_root = Path(__file__).parent.parent.parent.parent.parent
    coverage_dir = test_root / "tests" / "fixtures" / "requirements" / "coverage"

    registry.sync_from_specs(spec_dirs=[coverage_dir], plan_dirs=[coverage_dir])

    fr001 = registry.records["SPEC-900.FR-001"]
    artefacts = {e["artefact"] for e in fr001.coverage_entries}
    assert "VT-900" in artefacts

    kinds = {e["kind"] for e in fr001.coverage_entries}
    assert "VT" in kinds

    statuses = {e["status"] for e in fr001.coverage_entries}
    assert "verified" in statuses

  def test_coverage_entries_multiple_statuses(self) -> None:
    """Requirements with entries from multiple sources aggregate all entries."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    test_root = Path(__file__).parent.parent.parent.parent.parent
    coverage_dir = test_root / "tests" / "fixtures" / "requirements" / "coverage"

    registry.sync_from_specs(spec_dirs=[coverage_dir], plan_dirs=[coverage_dir])

    # FR-002 has entries from both SPEC-900 and IP-900
    fr002 = registry.records["SPEC-900.FR-002"]
    assert hasattr(fr002, "coverage_entries")
    assert len(fr002.coverage_entries) >= 2  # From spec + plan

  def test_coverage_entries_empty_for_no_coverage(self) -> None:
    """Requirements without coverage blocks have empty coverage_entries."""
    root = self._make_repo()

    # Create a spec with no coverage blocks
    spec_dir = root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR / "spec-001-example"
    spec_dir.mkdir(parents=True, exist_ok=True)
    spec_path = spec_dir / "SPEC-001.md"
    frontmatter = {
      "id": "SPEC-001",
      "slug": "spec-001",
      "name": "S",
      "status": "draft",
      "kind": "spec",
      "created": "2024-06-01",
      "updated": "2024-06-01",
    }
    dump_markdown_file(
      spec_path,
      frontmatter,
      "# SPEC-001\n\n- FR-001: No coverage\n",
    )

    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    spec_registry = SpecRegistry(root)
    spec_dirs = [root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR]
    registry.sync_from_specs(spec_dirs, spec_registry=spec_registry)

    fr001 = registry.records["SPEC-001.FR-001"]
    assert hasattr(fr001, "coverage_entries")
    assert fr001.coverage_entries == []

  def test_coverage_entries_serialization(self) -> None:
    """coverage_entries survives to_dict/from_dict round-trip."""
    record = RequirementRecord(
      uid="SPEC-001.FR-001",
      label="FR-001",
      title="Test",
      coverage_entries=[
        {"artefact": "VT-001", "kind": "VT", "status": "verified"},
      ],
    )

    data = record.to_dict()
    assert "coverage_entries" in data

    restored = RequirementRecord.from_dict("SPEC-001.FR-001", data)
    assert restored.coverage_entries == [
      {"artefact": "VT-001", "kind": "VT", "status": "verified"},
    ]

  def test_unknown_coverage_status_excluded_from_derivation(self) -> None:
    """VT-043-001: Entries with unknown statuses must not influence derived status."""
    root = self._make_repo()

    # Create a spec with a coverage block containing a mix of valid + unknown
    spec_dir = root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR / "spec-043-example"
    spec_dir.mkdir(parents=True, exist_ok=True)
    spec_path = spec_dir / "SPEC-043.md"
    body = textwrap.dedent("""\
      # SPEC-043

      - FR-001: A requirement with mixed coverage statuses

      ```yaml supekku:verification.coverage@v1
      schema: supekku.verification.coverage
      version: 1
      subject: SPEC-043
      entries:
        - artefact: VT-001
          kind: VT
          requirement: SPEC-043.FR-001
          status: verified
        - artefact: VH-001
          kind: VH
          requirement: SPEC-043.FR-001
          status: deferred
      ```
    """)
    frontmatter = {
      "id": "SPEC-043",
      "slug": "spec-043",
      "name": "Spec 043",
      "status": "draft",
      "kind": "spec",
      "created": "2024-06-01",
      "updated": "2024-06-01",
    }
    dump_markdown_file(spec_path, frontmatter, body)

    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    spec_registry = SpecRegistry(root)

    old_stderr = sys.stderr
    sys.stderr = io.StringIO()
    try:
      registry.sync_from_specs(
        [root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR],
        spec_registry=spec_registry,
      )
      stderr_output = sys.stderr.getvalue()
    finally:
      sys.stderr = old_stderr

    fr001 = registry.records["SPEC-043.FR-001"]

    # Unknown status should NOT drag derivation to in-progress.
    # Only the valid "verified" entry counts → status should be active.
    assert fr001.status == STATUS_ACTIVE, (
      f"Expected active (from verified entry only), got {fr001.status}"
    )

    # Warning should appear on stderr
    assert "deferred" in stderr_output, (
      "Expected warning about unknown status 'deferred' on stderr"
    )
    assert "SPEC-043.FR-001" in stderr_output or "SPEC-043" in stderr_output


class TestFindByVerificationStatus(unittest.TestCase):
  """Test RequirementsRegistry.find_by_verification_status() method."""

  def setUp(self) -> None:
    self._cwd = Path.cwd()

  def tearDown(self) -> None:
    os.chdir(self._cwd)

  def _make_registry_with_entries(self) -> RequirementsRegistry:
    """Create a registry with records having diverse coverage_entries."""
    tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.addCleanup(tmpdir.cleanup)
    root = Path(tmpdir.name)
    (root / ".git").mkdir()
    os.chdir(root)

    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    # FR-001: verified
    registry.records["SPEC-001.FR-001"] = RequirementRecord(
      uid="SPEC-001.FR-001",
      label="FR-001",
      title="Verified requirement",
      coverage_entries=[
        {"artefact": "VT-001", "kind": "VT", "status": "verified"},
      ],
    )
    # FR-002: in-progress
    registry.records["SPEC-001.FR-002"] = RequirementRecord(
      uid="SPEC-001.FR-002",
      label="FR-002",
      title="In-progress requirement",
      coverage_entries=[
        {"artefact": "VT-002", "kind": "VT", "status": "in-progress"},
      ],
    )
    # FR-003: planned
    registry.records["SPEC-001.FR-003"] = RequirementRecord(
      uid="SPEC-001.FR-003",
      label="FR-003",
      title="Planned requirement",
      coverage_entries=[
        {"artefact": "VA-001", "kind": "VA", "status": "planned"},
      ],
    )
    # FR-004: mixed (verified + failed)
    registry.records["SPEC-001.FR-004"] = RequirementRecord(
      uid="SPEC-001.FR-004",
      label="FR-004",
      title="Mixed status requirement",
      coverage_entries=[
        {"artefact": "VT-003", "kind": "VT", "status": "verified"},
        {"artefact": "VH-001", "kind": "VH", "status": "failed"},
      ],
    )
    # NF-001: no coverage entries
    registry.records["SPEC-001.NF-001"] = RequirementRecord(
      uid="SPEC-001.NF-001",
      label="NF-001",
      title="No coverage requirement",
      coverage_entries=[],
    )
    return registry

  def test_single_status_verified(self) -> None:
    """Filter by single status 'verified' returns matching requirements."""
    registry = self._make_registry_with_entries()
    results = registry.find_by_verification_status(["verified"])
    uids = {r.uid for r in results}
    assert "SPEC-001.FR-001" in uids  # Has verified entry
    assert "SPEC-001.FR-004" in uids  # Has verified + failed
    assert "SPEC-001.FR-002" not in uids

  def test_single_status_failed(self) -> None:
    """Filter by 'failed' returns requirements with failed entries."""
    registry = self._make_registry_with_entries()
    results = registry.find_by_verification_status(["failed"])
    uids = {r.uid for r in results}
    assert "SPEC-001.FR-004" in uids
    assert len(uids) == 1

  def test_multi_status_or_logic(self) -> None:
    """Multi-value status uses OR logic: match if ANY entry matches ANY status."""
    registry = self._make_registry_with_entries()
    results = registry.find_by_verification_status(["planned", "in-progress"])
    uids = {r.uid for r in results}
    assert "SPEC-001.FR-002" in uids  # in-progress
    assert "SPEC-001.FR-003" in uids  # planned
    assert "SPEC-001.FR-001" not in uids

  def test_empty_list_returns_all(self) -> None:
    """Empty status list returns empty result (no filter match)."""
    registry = self._make_registry_with_entries()
    results = registry.find_by_verification_status([])
    assert results == []

  def test_nonexistent_status(self) -> None:
    """Non-existent status returns empty list."""
    registry = self._make_registry_with_entries()
    results = registry.find_by_verification_status(["nonexistent"])
    assert results == []

  def test_results_sorted_by_uid(self) -> None:
    """Results are sorted by uid."""
    registry = self._make_registry_with_entries()
    results = registry.find_by_verification_status(["verified"])
    uids = [r.uid for r in results]
    assert uids == sorted(uids)

  def test_no_coverage_entries_excluded(self) -> None:
    """Requirements with empty coverage_entries are never matched."""
    registry = self._make_registry_with_entries()
    # NF-001 has no coverage_entries — should never appear
    for status in ["verified", "in-progress", "planned", "failed", "blocked"]:
      results = registry.find_by_verification_status([status])
      uids = {r.uid for r in results}
      assert "SPEC-001.NF-001" not in uids


class TestFindByVerificationKind(unittest.TestCase):
  """Test RequirementsRegistry.find_by_verification_kind() method."""

  def setUp(self) -> None:
    self._cwd = Path.cwd()

  def tearDown(self) -> None:
    os.chdir(self._cwd)

  def _make_registry_with_entries(self) -> RequirementsRegistry:
    """Create a registry with records having diverse verification kinds."""
    tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.addCleanup(tmpdir.cleanup)
    root = Path(tmpdir.name)
    (root / ".git").mkdir()
    os.chdir(root)

    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    # FR-001: VT only
    registry.records["SPEC-001.FR-001"] = RequirementRecord(
      uid="SPEC-001.FR-001",
      label="FR-001",
      title="VT-only requirement",
      coverage_entries=[
        {"artefact": "VT-001", "kind": "VT", "status": "verified"},
      ],
    )
    # FR-002: VA only
    registry.records["SPEC-001.FR-002"] = RequirementRecord(
      uid="SPEC-001.FR-002",
      label="FR-002",
      title="VA-only requirement",
      coverage_entries=[
        {"artefact": "VA-001", "kind": "VA", "status": "verified"},
      ],
    )
    # FR-003: VH only
    registry.records["SPEC-001.FR-003"] = RequirementRecord(
      uid="SPEC-001.FR-003",
      label="FR-003",
      title="VH-only requirement",
      coverage_entries=[
        {"artefact": "VH-001", "kind": "VH", "status": "planned"},
      ],
    )
    # FR-004: mixed VT + VA
    registry.records["SPEC-001.FR-004"] = RequirementRecord(
      uid="SPEC-001.FR-004",
      label="FR-004",
      title="Mixed VT+VA requirement",
      coverage_entries=[
        {"artefact": "VT-002", "kind": "VT", "status": "in-progress"},
        {"artefact": "VA-002", "kind": "VA", "status": "verified"},
      ],
    )
    # NF-001: no coverage entries
    registry.records["SPEC-001.NF-001"] = RequirementRecord(
      uid="SPEC-001.NF-001",
      label="NF-001",
      title="No coverage requirement",
      coverage_entries=[],
    )
    return registry

  def test_single_kind_vt(self) -> None:
    """Filter by VT returns requirements with VT entries."""
    registry = self._make_registry_with_entries()
    results = registry.find_by_verification_kind(["VT"])
    uids = {r.uid for r in results}
    assert "SPEC-001.FR-001" in uids
    assert "SPEC-001.FR-004" in uids
    assert "SPEC-001.FR-002" not in uids  # VA only
    assert "SPEC-001.FR-003" not in uids  # VH only

  def test_single_kind_va(self) -> None:
    """Filter by VA returns requirements with VA entries."""
    registry = self._make_registry_with_entries()
    results = registry.find_by_verification_kind(["VA"])
    uids = {r.uid for r in results}
    assert "SPEC-001.FR-002" in uids
    assert "SPEC-001.FR-004" in uids
    assert "SPEC-001.FR-001" not in uids

  def test_single_kind_vh(self) -> None:
    """Filter by VH returns requirements with VH entries."""
    registry = self._make_registry_with_entries()
    results = registry.find_by_verification_kind(["VH"])
    uids = {r.uid for r in results}
    assert uids == {"SPEC-001.FR-003"}

  def test_multi_kind_or_logic(self) -> None:
    """Multi-value kind uses OR logic."""
    registry = self._make_registry_with_entries()
    results = registry.find_by_verification_kind(["VA", "VH"])
    uids = {r.uid for r in results}
    assert "SPEC-001.FR-002" in uids  # VA
    assert "SPEC-001.FR-003" in uids  # VH
    assert "SPEC-001.FR-004" in uids  # VA+VT (matches VA)
    assert "SPEC-001.FR-001" not in uids  # VT only

  def test_all_kinds(self) -> None:
    """Filtering by all three kinds returns all requirements with coverage."""
    registry = self._make_registry_with_entries()
    results = registry.find_by_verification_kind(["VT", "VA", "VH"])
    uids = {r.uid for r in results}
    assert "SPEC-001.NF-001" not in uids  # No entries
    assert len(uids) == 4

  def test_empty_list_returns_empty(self) -> None:
    """Empty kind list returns empty result."""
    registry = self._make_registry_with_entries()
    results = registry.find_by_verification_kind([])
    assert results == []

  def test_nonexistent_kind(self) -> None:
    """Non-existent kind returns empty list."""
    registry = self._make_registry_with_entries()
    results = registry.find_by_verification_kind(["XX"])
    assert results == []

  def test_results_sorted_by_uid(self) -> None:
    """Results are sorted by uid."""
    registry = self._make_registry_with_entries()
    results = registry.find_by_verification_kind(["VT"])
    uids = [r.uid for r in results]
    assert uids == sorted(uids)

  def test_no_coverage_entries_excluded(self) -> None:
    """Requirements with empty coverage_entries never matched."""
    registry = self._make_registry_with_entries()
    for kind in ["VT", "VA", "VH"]:
      results = registry.find_by_verification_kind([kind])
      uids = {r.uid for r in results}
      assert "SPEC-001.NF-001" not in uids


class TestRequirementsRegistryStandardSurface(unittest.TestCase):
  """Tests for ADR-009 standard registry surface: find, collect, iter, filter."""

  def setUp(self) -> None:
    self._cwd = Path.cwd()

  def tearDown(self) -> None:
    os.chdir(self._cwd)

  def _make_registry(self) -> tuple[RequirementsRegistry, Path]:
    tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.addCleanup(tmpdir.cleanup)
    root = Path(tmpdir.name)
    (root / ".git").mkdir()
    os.chdir(root)
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    registry.records["SPEC-001.FR-001"] = RequirementRecord(
      uid="SPEC-001.FR-001",
      label="FR-001",
      title="First requirement",
      specs=["SPEC-001"],
      kind="functional",
      status=STATUS_ACTIVE,
      tags=["core"],
    )
    registry.records["SPEC-001.NF-001"] = RequirementRecord(
      uid="SPEC-001.NF-001",
      label="NF-001",
      title="Non-functional requirement",
      specs=["SPEC-001"],
      kind="non-functional",
      status=STATUS_PENDING,
      tags=["performance"],
    )
    registry.records["SPEC-002.FR-001"] = RequirementRecord(
      uid="SPEC-002.FR-001",
      label="FR-001",
      title="Second spec requirement",
      specs=["SPEC-002"],
      kind="functional",
      status=STATUS_ACTIVE,
    )
    return registry, root

  # -- constructor ----------------------------------------------------------

  def test_constructor_with_root_keyword(self) -> None:
    tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.addCleanup(tmpdir.cleanup)
    root = Path(tmpdir.name)
    (root / ".git").mkdir()
    os.chdir(root)
    registry = RequirementsRegistry(root=root)
    assert registry.registry_path == get_registry_dir(root) / "requirements.yaml"

  def test_constructor_positional_still_works(self) -> None:
    tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.addCleanup(tmpdir.cleanup)
    root = Path(tmpdir.name)
    (root / ".git").mkdir()
    os.chdir(root)
    explicit_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(explicit_path)
    assert registry.registry_path == explicit_path

  # -- find() ---------------------------------------------------------------

  def test_find_returns_record(self) -> None:
    registry, _ = self._make_registry()
    record = registry.find("SPEC-001.FR-001")
    assert record is not None
    assert record.uid == "SPEC-001.FR-001"

  def test_find_returns_none_for_missing(self) -> None:
    registry, _ = self._make_registry()
    assert registry.find("SPEC-999.FR-999") is None

  # -- collect() ------------------------------------------------------------

  def test_collect_returns_dict(self) -> None:
    registry, _ = self._make_registry()
    result = registry.collect()
    assert isinstance(result, dict)
    assert len(result) == 3
    assert "SPEC-001.FR-001" in result

  def test_collect_returns_copy(self) -> None:
    registry, _ = self._make_registry()
    a = registry.collect()
    b = registry.collect()
    assert a is not b

  # -- iter() ---------------------------------------------------------------

  def test_iter_yields_all(self) -> None:
    registry, _ = self._make_registry()
    uids = {r.uid for r in registry.iter()}
    assert len(uids) == 3

  def test_iter_filters_by_status(self) -> None:
    registry, _ = self._make_registry()
    uids = {r.uid for r in registry.iter(status=STATUS_ACTIVE)}
    assert uids == {"SPEC-001.FR-001", "SPEC-002.FR-001"}

  # -- filter() -------------------------------------------------------------

  def test_filter_by_status(self) -> None:
    registry, _ = self._make_registry()
    result = registry.filter(status=STATUS_PENDING)
    assert len(result) == 1
    assert result[0].uid == "SPEC-001.NF-001"

  def test_filter_by_spec(self) -> None:
    registry, _ = self._make_registry()
    result = registry.filter(spec="SPEC-002")
    assert len(result) == 1
    assert result[0].uid == "SPEC-002.FR-001"

  def test_filter_by_kind(self) -> None:
    registry, _ = self._make_registry()
    result = registry.filter(kind="non-functional")
    assert len(result) == 1
    assert result[0].uid == "SPEC-001.NF-001"

  def test_filter_by_tag(self) -> None:
    registry, _ = self._make_registry()
    result = registry.filter(tag="core")
    assert len(result) == 1
    assert result[0].uid == "SPEC-001.FR-001"

  def test_filter_and_logic(self) -> None:
    registry, _ = self._make_registry()
    result = registry.filter(status=STATUS_ACTIVE, kind="functional")
    assert len(result) == 2

  def test_filter_no_params_returns_all(self) -> None:
    registry, _ = self._make_registry()
    assert len(registry.filter()) == 3

  def test_filter_no_matches_returns_empty(self) -> None:
    registry, _ = self._make_registry()
    assert registry.filter(tag="nonexistent") == []


class TestRequirementHeadingRegex(unittest.TestCase):
  """VT-REGEX-076-001: _REQUIREMENT_HEADING regex matches dotted backlog format."""

  def test_matches_fr_dotted(self) -> None:
    m = _REQUIREMENT_HEADING.match("### FR-016.001: User can filter by source")
    assert m is not None
    assert m.group(1).upper() == "FR"
    assert m.group(2) == "016"
    assert m.group(3) == "001"
    assert m.group(4).strip() == "User can filter by source"

  def test_matches_nf_dotted(self) -> None:
    m = _REQUIREMENT_HEADING.match("### NF-013.001: Performance under load")
    assert m is not None
    assert m.group(1).upper() == "NF"
    assert m.group(2) == "013"
    assert m.group(3) == "001"

  def test_rejects_non_dotted(self) -> None:
    assert _REQUIREMENT_HEADING.match("### FR-001: Title") is None

  def test_rejects_bullet_format(self) -> None:
    assert _REQUIREMENT_HEADING.match("- **FR-016.001**: Title") is None

  def test_matches_h2(self) -> None:
    m = _REQUIREMENT_HEADING.match("## FR-016.002: Another requirement")
    assert m is not None

  def test_matches_dash_separator(self) -> None:
    m = _REQUIREMENT_HEADING.match("### FR-016.001 - Dash separated title")
    assert m is not None
    assert m.group(4).strip() == "Dash separated title"


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
    registry._upsert_record(
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
    registry._upsert_record(
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


class TestCoverageReplacementSemantics(unittest.TestCase):
  """VT-081-001: Coverage evidence is rebuilt fresh each sync."""

  def _make_repo(self) -> Path:
    root = Path(tempfile.mkdtemp())
    (root / ".git").mkdir()
    return root

  def _write_spec(self, root: Path, spec_id: str, body: str) -> Path:
    """Write a spec file and return the tech specs root directory."""
    spec_dir = root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR / spec_id.lower()
    spec_dir.mkdir(parents=True, exist_ok=True)
    spec_file = spec_dir / f"{spec_id}.md"
    dump_markdown_file(
      spec_file,
      {"id": spec_id, "status": "draft", "kind": "spec"},
      body,
    )
    return root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR

  def test_coverage_evidence_replaced_not_accumulated(self) -> None:
    """Removing an artefact from a coverage block removes it from evidence."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    body_v1 = textwrap.dedent("""\
      ## Requirements
      - **FR-001**: First requirement

      ```yaml supekku:verification.coverage@v1
      schema: supekku.verification.coverage
      version: 1
      subject: SPEC-800
      entries:
        - artefact: VT-801
          kind: VT
          requirement: SPEC-800.FR-001
          status: verified
        - artefact: VT-802
          kind: VT
          requirement: SPEC-800.FR-001
          status: verified
      ```
    """)
    specs_root = self._write_spec(root, "SPEC-800", body_v1)

    registry.sync_from_specs(spec_dirs=[specs_root])
    fr001 = registry.records["SPEC-800.FR-001"]
    assert fr001.coverage_evidence == ["VT-801", "VT-802"]

    # Now remove VT-802 from coverage block
    body_v2 = textwrap.dedent("""\
      ## Requirements
      - **FR-001**: First requirement

      ```yaml supekku:verification.coverage@v1
      schema: supekku.verification.coverage
      version: 1
      subject: SPEC-800
      entries:
        - artefact: VT-801
          kind: VT
          requirement: SPEC-800.FR-001
          status: verified
      ```
    """)
    spec_file = specs_root / "spec-800" / "SPEC-800.md"
    dump_markdown_file(
      spec_file,
      {"id": "SPEC-800", "status": "draft", "kind": "spec"},
      body_v2,
    )

    registry.sync_from_specs(spec_dirs=[specs_root])
    fr001 = registry.records["SPEC-800.FR-001"]
    # VT-802 should be gone — replacement, not accumulation
    assert fr001.coverage_evidence == ["VT-801"]

  def test_sync_idempotency(self) -> None:
    """Running sync twice produces identical registry (NF-002)."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"

    body = textwrap.dedent("""\
      ## Requirements
      - **FR-001**: First requirement
      - **NF-001**: Non-functional requirement

      ```yaml supekku:verification.coverage@v1
      schema: supekku.verification.coverage
      version: 1
      subject: SPEC-810
      entries:
        - artefact: VT-811
          kind: VT
          requirement: SPEC-810.FR-001
          status: verified
      ```
    """)
    specs_root = self._write_spec(root, "SPEC-810", body)

    # First sync
    registry1 = RequirementsRegistry(registry_path)
    registry1.sync_from_specs(spec_dirs=[specs_root])
    registry1.save()
    content1 = registry_path.read_text(encoding="utf-8")

    # Second sync
    registry2 = RequirementsRegistry(registry_path)
    registry2.sync_from_specs(spec_dirs=[specs_root])
    registry2.save()
    content2 = registry_path.read_text(encoding="utf-8")

    assert content1 == content2

  def test_removed_coverage_block_clears_evidence(self) -> None:
    """Removing entire coverage block clears evidence for affected requirements."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    body_with_coverage = textwrap.dedent("""\
      ## Requirements
      - **FR-001**: Covered requirement

      ```yaml supekku:verification.coverage@v1
      schema: supekku.verification.coverage
      version: 1
      subject: SPEC-820
      entries:
        - artefact: VT-821
          kind: VT
          requirement: SPEC-820.FR-001
          status: verified
      ```
    """)
    specs_root = self._write_spec(root, "SPEC-820", body_with_coverage)
    registry.sync_from_specs(spec_dirs=[specs_root])
    assert registry.records["SPEC-820.FR-001"].coverage_evidence == ["VT-821"]
    assert registry.records["SPEC-820.FR-001"].status == STATUS_ACTIVE

    # Remove entire coverage block
    body_without_coverage = textwrap.dedent("""\
      ## Requirements
      - **FR-001**: Covered requirement
    """)
    spec_file = specs_root / "spec-820" / "SPEC-820.md"
    dump_markdown_file(
      spec_file,
      {"id": "SPEC-820", "status": "draft", "kind": "spec"},
      body_without_coverage,
    )

    registry.sync_from_specs(spec_dirs=[specs_root])
    fr001 = registry.records["SPEC-820.FR-001"]
    assert fr001.coverage_evidence == []
    assert fr001.coverage_entries == []
    # Status preserved — losing evidence doesn't downgrade (ADR-008 §3)
    assert fr001.status == STATUS_ACTIVE


class TestTerminalStatusGuard(unittest.TestCase):
  """VT-081-002: Terminal statuses not overwritten by coverage derivation."""

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

  def test_deprecated_status_constants(self) -> None:
    """deprecated and superseded are valid requirement statuses."""
    assert STATUS_DEPRECATED == "deprecated"
    assert STATUS_SUPERSEDED == "superseded"
    assert STATUS_DEPRECATED in TERMINAL_STATUSES
    assert STATUS_SUPERSEDED in TERMINAL_STATUSES

  def test_deprecated_not_overwritten_by_coverage(self) -> None:
    """A deprecated requirement keeps its status despite verified coverage."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    body = textwrap.dedent("""\
      ## Requirements
      - **FR-001**: Deprecated requirement

      ```yaml supekku:verification.coverage@v1
      schema: supekku.verification.coverage
      version: 1
      subject: SPEC-830
      entries:
        - artefact: VT-831
          kind: VT
          requirement: SPEC-830.FR-001
          status: verified
      ```
    """)
    specs_root = self._write_spec(root, "SPEC-830", body)

    registry.sync_from_specs(spec_dirs=[specs_root])
    assert registry.records["SPEC-830.FR-001"].status == STATUS_ACTIVE

    # Manually set to deprecated (normative lifecycle claim)
    registry.records["SPEC-830.FR-001"].status = STATUS_DEPRECATED

    # Re-sync — coverage says verified, but deprecated is terminal
    registry.sync_from_specs(spec_dirs=[specs_root])
    assert registry.records["SPEC-830.FR-001"].status == STATUS_DEPRECATED

  def test_superseded_not_overwritten_by_coverage(self) -> None:
    """A superseded requirement keeps its status despite coverage."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    body = textwrap.dedent("""\
      ## Requirements
      - **FR-001**: Superseded requirement

      ```yaml supekku:verification.coverage@v1
      schema: supekku.verification.coverage
      version: 1
      subject: SPEC-840
      entries:
        - artefact: VT-841
          kind: VT
          requirement: SPEC-840.FR-001
          status: in-progress
      ```
    """)
    specs_root = self._write_spec(root, "SPEC-840", body)

    registry.sync_from_specs(spec_dirs=[specs_root])
    registry.records["SPEC-840.FR-001"].status = STATUS_SUPERSEDED
    registry.sync_from_specs(spec_dirs=[specs_root])
    assert registry.records["SPEC-840.FR-001"].status == STATUS_SUPERSEDED


class TestInlineRequirementTags(unittest.TestCase):
  """VT-081-003: Inline tag extraction from [tag1, tag2] syntax."""

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

  def test_tags_extracted_from_inline_syntax(self) -> None:
    """Tags in [brackets] after category are parsed."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    body = textwrap.dedent("""\
      ## Requirements
      - **FR-001**(api)[security, auth]: Validate tokens
      - **FR-002**[performance]: Fast response
      - **NF-001**(infra)[reliability, ha]: High availability
      - **FR-003**: No tags here
    """)
    specs_root = self._write_spec(root, "SPEC-850", body)

    registry.sync_from_specs(spec_dirs=[specs_root])

    fr001 = registry.records["SPEC-850.FR-001"]
    assert fr001.tags == ["auth", "security"]
    assert fr001.category == "api"

    fr002 = registry.records["SPEC-850.FR-002"]
    assert fr002.tags == ["performance"]
    assert fr002.category is None

    nf001 = registry.records["SPEC-850.NF-001"]
    assert nf001.tags == ["ha", "reliability"]
    assert nf001.category == "infra"

    fr003 = registry.records["SPEC-850.FR-003"]
    assert fr003.tags == []

  def test_tags_populated_in_registry_after_save_load(self) -> None:
    """Tags survive save/load round-trip."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    body = textwrap.dedent("""\
      ## Requirements
      - **FR-001**[alpha, beta]: Tagged requirement
    """)
    specs_root = self._write_spec(root, "SPEC-860", body)

    registry.sync_from_specs(spec_dirs=[specs_root])
    registry.save()

    # Reload
    registry2 = RequirementsRegistry(registry_path)
    fr001 = registry2.records["SPEC-860.FR-001"]
    assert fr001.tags == ["alpha", "beta"]

  def test_filter_by_tag(self) -> None:
    """filter(tag=...) returns only tagged requirements."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    body = textwrap.dedent("""\
      ## Requirements
      - **FR-001**[security]: Secure endpoint
      - **FR-002**[performance]: Fast endpoint
      - **FR-003**[security, performance]: Both
    """)
    specs_root = self._write_spec(root, "SPEC-870", body)

    registry.sync_from_specs(spec_dirs=[specs_root])

    security = registry.filter(tag="security")
    assert {r.uid for r in security} == {
      "SPEC-870.FR-001",
      "SPEC-870.FR-003",
    }

    perf = registry.filter(tag="performance")
    assert {r.uid for r in perf} == {
      "SPEC-870.FR-002",
      "SPEC-870.FR-003",
    }

    none = registry.filter(tag="nonexistent")
    assert none == []

  def test_tags_merged_on_multi_spec_sync(self) -> None:
    """Tags from multiple specs are unioned during merge."""
    record1 = RequirementRecord(
      uid="SPEC-001.FR-001",
      label="FR-001",
      title="Shared requirement",
      tags=["alpha", "beta"],
    )
    record2 = RequirementRecord(
      uid="SPEC-001.FR-001",
      label="FR-001",
      title="Shared requirement",
      tags=["beta", "gamma"],
    )
    merged = record1.merge(record2)
    assert merged.tags == ["alpha", "beta", "gamma"]


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


if __name__ == "__main__":
  unittest.main()
