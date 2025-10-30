"""Tests for revision_discovery module."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from .revision_discovery import RequirementSource, find_requirement_sources

SAMPLE_REVISION_MD = """---
id: RE-001
name: Test Revision
status: completed
kind: revision
---

# RE-001 - Test Revision

## Context

Test revision for unit tests.

```yaml supekku:revision.change@v1
schema: supekku.revision.change
version: 1
metadata:
  revision: RE-001
specs:
  - spec_id: SPEC-150
    action: updated
requirements:
  - requirement_id: SPEC-150.FR-001
    kind: functional
    action: introduce
    destination:
      spec: SPEC-150
      requirement_id: SPEC-150.FR-001
    lifecycle:
      status: pending
      introduced_by: RE-001
  - requirement_id: SPEC-150.FR-002
    kind: functional
    action: introduce
    destination:
      spec: SPEC-150
      requirement_id: SPEC-150.FR-002
    lifecycle:
      status: pending
      introduced_by: RE-001
```

## Summary

Test revision.
"""


def test_find_requirement_sources_locates_single_requirement() -> None:
  """Test finding a single requirement in a revision file."""
  with TemporaryDirectory() as tmpdir:
    # Create revision directory structure
    revision_dir = Path(tmpdir) / "revisions"
    bundle_dir = revision_dir / "RE-001-test"
    bundle_dir.mkdir(parents=True)

    # Write revision file
    revision_file = bundle_dir / "RE-001.md"
    revision_file.write_text(SAMPLE_REVISION_MD, encoding="utf-8")

    # Find requirement
    sources = find_requirement_sources(
      ["SPEC-150.FR-001"],
      [revision_dir],
    )

    assert len(sources) == 1
    assert "SPEC-150.FR-001" in sources

    source = sources["SPEC-150.FR-001"]
    assert isinstance(source, RequirementSource)
    assert source.requirement_id == "SPEC-150.FR-001"
    assert source.revision_id == "RE-001"
    assert source.revision_file == revision_file
    assert source.block_index == 0
    assert source.requirement_index == 0


def test_find_requirement_sources_locates_multiple_requirements() -> None:
  """Test finding multiple requirements in the same revision file."""
  with TemporaryDirectory() as tmpdir:
    revision_dir = Path(tmpdir) / "revisions"
    bundle_dir = revision_dir / "RE-001-test"
    bundle_dir.mkdir(parents=True)

    revision_file = bundle_dir / "RE-001.md"
    revision_file.write_text(SAMPLE_REVISION_MD, encoding="utf-8")

    # Find both requirements
    sources = find_requirement_sources(
      ["SPEC-150.FR-001", "SPEC-150.FR-002"],
      [revision_dir],
    )

    assert len(sources) == 2
    assert "SPEC-150.FR-001" in sources
    assert "SPEC-150.FR-002" in sources

    source1 = sources["SPEC-150.FR-001"]
    source2 = sources["SPEC-150.FR-002"]

    assert source1.requirement_index == 0
    assert source2.requirement_index == 1
    assert source1.revision_file == source2.revision_file


def test_find_requirement_sources_returns_empty_for_not_found() -> None:
  """Test that non-existent requirements return empty results."""
  with TemporaryDirectory() as tmpdir:
    revision_dir = Path(tmpdir) / "revisions"
    bundle_dir = revision_dir / "RE-001-test"
    bundle_dir.mkdir(parents=True)

    revision_file = bundle_dir / "RE-001.md"
    revision_file.write_text(SAMPLE_REVISION_MD, encoding="utf-8")

    # Search for non-existent requirement
    sources = find_requirement_sources(
      ["SPEC-999.FR-999"],
      [revision_dir],
    )

    assert len(sources) == 0


def test_find_requirement_sources_handles_empty_directory() -> None:
  """Test handling of empty revision directory."""
  with TemporaryDirectory() as tmpdir:
    revision_dir = Path(tmpdir) / "revisions"
    revision_dir.mkdir()

    sources = find_requirement_sources(
      ["SPEC-150.FR-001"],
      [revision_dir],
    )

    assert len(sources) == 0


def test_find_requirement_sources_handles_non_existent_directory() -> None:
  """Test handling of non-existent directory."""
  sources = find_requirement_sources(
    ["SPEC-150.FR-001"],
    [Path("/nonexistent/path")],
  )

  assert len(sources) == 0


def test_find_requirement_sources_skips_malformed_files() -> None:
  """Test that malformed revision files are skipped gracefully."""
  with TemporaryDirectory() as tmpdir:
    revision_dir = Path(tmpdir) / "revisions"
    bundle_dir = revision_dir / "RE-002-bad"
    bundle_dir.mkdir(parents=True)

    # Write malformed revision file
    bad_file = bundle_dir / "RE-002.md"
    bad_file.write_text(
      "This is not valid markdown with YAML blocks",
      encoding="utf-8",
    )

    sources = find_requirement_sources(
      ["SPEC-150.FR-001"],
      [revision_dir],
    )

    # Should not crash, just return empty
    assert len(sources) == 0
