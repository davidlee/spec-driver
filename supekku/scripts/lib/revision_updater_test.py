"""Tests for revision_updater module."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from .lifecycle import STATUS_LIVE, STATUS_PENDING
from .revision_updater import (
    RevisionUpdateError,
    update_requirement_lifecycle_status,
)


SAMPLE_REVISION_MD = """---
id: RE-001
name: Test Revision
status: completed
kind: revision
---

# RE-001 - Test Revision

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
```
"""


def test_update_requirement_lifecycle_status_updates_status():
    """Test successful status update."""
    with TemporaryDirectory() as tmpdir:
        revision_file = Path(tmpdir) / "RE-001.md"
        revision_file.write_text(SAMPLE_REVISION_MD, encoding="utf-8")

        # Update status
        changed = update_requirement_lifecycle_status(
            revision_file,
            "SPEC-150.FR-001",
            STATUS_LIVE,
            block_index=0,
            requirement_index=0,
        )

        assert changed is True

        # Verify file was updated
        content = revision_file.read_text(encoding="utf-8")
        assert "status: live" in content
        assert "status: pending" not in content


def test_update_requirement_lifecycle_status_returns_false_when_no_change():
    """Test that function returns False when status already matches."""
    with TemporaryDirectory() as tmpdir:
        revision_file = Path(tmpdir) / "RE-001.md"
        revision_file.write_text(SAMPLE_REVISION_MD, encoding="utf-8")

        # Update to pending (already pending)
        changed = update_requirement_lifecycle_status(
            revision_file,
            "SPEC-150.FR-001",
            STATUS_PENDING,
            block_index=0,
            requirement_index=0,
        )

        assert changed is False


def test_update_requirement_lifecycle_status_validates_status():
    """Test that invalid status values are rejected."""
    with TemporaryDirectory() as tmpdir:
        revision_file = Path(tmpdir) / "RE-001.md"
        revision_file.write_text(SAMPLE_REVISION_MD, encoding="utf-8")

        # Try invalid status
        with pytest.raises(ValueError, match="Invalid status"):
            update_requirement_lifecycle_status(
                revision_file,
                "SPEC-150.FR-001",
                "invalid_status",
                block_index=0,
                requirement_index=0,
            )


def test_update_requirement_lifecycle_status_validates_requirement_id():
    """Test that mismatched requirement ID raises error."""
    with TemporaryDirectory() as tmpdir:
        revision_file = Path(tmpdir) / "RE-001.md"
        revision_file.write_text(SAMPLE_REVISION_MD, encoding="utf-8")

        # Try wrong requirement ID
        with pytest.raises(RevisionUpdateError, match="Requirement ID mismatch"):
            update_requirement_lifecycle_status(
                revision_file,
                "SPEC-999.FR-999",  # Wrong ID
                STATUS_LIVE,
                block_index=0,
                requirement_index=0,
            )


def test_update_requirement_lifecycle_status_validates_block_index():
    """Test that out-of-range block index raises error."""
    with TemporaryDirectory() as tmpdir:
        revision_file = Path(tmpdir) / "RE-001.md"
        revision_file.write_text(SAMPLE_REVISION_MD, encoding="utf-8")

        # Try invalid block index
        with pytest.raises(RevisionUpdateError, match="Block index .* out of range"):
            update_requirement_lifecycle_status(
                revision_file,
                "SPEC-150.FR-001",
                STATUS_LIVE,
                block_index=999,  # Out of range
                requirement_index=0,
            )


def test_update_requirement_lifecycle_status_validates_requirement_index():
    """Test that out-of-range requirement index raises error."""
    with TemporaryDirectory() as tmpdir:
        revision_file = Path(tmpdir) / "RE-001.md"
        revision_file.write_text(SAMPLE_REVISION_MD, encoding="utf-8")

        # Try invalid requirement index
        with pytest.raises(
            RevisionUpdateError, match="Requirement index .* out of range"
        ):
            update_requirement_lifecycle_status(
                revision_file,
                "SPEC-150.FR-001",
                STATUS_LIVE,
                block_index=0,
                requirement_index=999,  # Out of range
            )


def test_update_requirement_lifecycle_status_creates_lifecycle_if_missing():
    """Test that lifecycle section is created if it doesn't exist."""
    revision_without_lifecycle = """---
id: RE-002
---

# RE-002

```yaml supekku:revision.change@v1
schema: supekku.revision.change
version: 1
metadata:
  revision: RE-002
specs:
  - spec_id: SPEC-150
    action: updated
requirements:
  - requirement_id: SPEC-150.FR-002
    kind: functional
    action: introduce
    destination:
      spec: SPEC-150
      requirement_id: SPEC-150.FR-002
```
"""

    with TemporaryDirectory() as tmpdir:
        revision_file = Path(tmpdir) / "RE-002.md"
        revision_file.write_text(revision_without_lifecycle, encoding="utf-8")

        # Update status (will create lifecycle section)
        changed = update_requirement_lifecycle_status(
            revision_file,
            "SPEC-150.FR-002",
            STATUS_LIVE,
            block_index=0,
            requirement_index=0,
        )

        assert changed is True

        # Verify lifecycle was added
        content = revision_file.read_text(encoding="utf-8")
        assert "lifecycle:" in content
        assert "status: live" in content
