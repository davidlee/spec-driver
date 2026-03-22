"""Tests for requirement coverage tracking."""

from __future__ import annotations

import io
import os
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

from supekku.scripts.lib.core.paths import (
  SPEC_DRIVER_DIR,
  TECH_SPECS_SUBDIR,
  get_registry_dir,
)
from supekku.scripts.lib.core.spec_utils import dump_markdown_file
from supekku.scripts.lib.requirements.lifecycle import STATUS_ACTIVE
from supekku.scripts.lib.requirements.registry import (
  RequirementRecord,
  RequirementsRegistry,
)
from supekku.scripts.lib.specs.registry import SpecRegistry


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


if __name__ == "__main__":
  unittest.main()
