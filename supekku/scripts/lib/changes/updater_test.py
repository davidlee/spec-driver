"""Tests for revision_updater module."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from supekku.scripts.lib.requirements.lifecycle import STATUS_ACTIVE, STATUS_PENDING

from .updater import (
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


def test_update_requirement_lifecycle_status_updates_status() -> None:
  """Test successful status update."""
  with TemporaryDirectory() as tmpdir:
    revision_file = Path(tmpdir) / "RE-001.md"
    revision_file.write_text(SAMPLE_REVISION_MD, encoding="utf-8")

    # Update status
    changed = update_requirement_lifecycle_status(
      revision_file,
      "SPEC-150.FR-001",
      STATUS_ACTIVE,
      block_index=0,
      requirement_index=0,
    )

    assert changed is True

    # Verify file was updated
    content = revision_file.read_text(encoding="utf-8")
    assert "status: active" in content
    assert "status: pending" not in content


def test_update_requirement_lifecycle_status_returns_false_when_no_change() -> None:
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


def test_update_requirement_lifecycle_status_validates_status() -> None:
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


def test_update_requirement_lifecycle_status_validates_requirement_id() -> None:
  """Test that mismatched requirement ID raises error."""
  with TemporaryDirectory() as tmpdir:
    revision_file = Path(tmpdir) / "RE-001.md"
    revision_file.write_text(SAMPLE_REVISION_MD, encoding="utf-8")

    # Try wrong requirement ID
    with pytest.raises(RevisionUpdateError, match="Requirement ID mismatch"):
      update_requirement_lifecycle_status(
        revision_file,
        "SPEC-999.FR-999",  # Wrong ID
        STATUS_ACTIVE,
        block_index=0,
        requirement_index=0,
      )


def test_update_requirement_lifecycle_status_validates_block_index() -> None:
  """Test that out-of-range block index raises error."""
  with TemporaryDirectory() as tmpdir:
    revision_file = Path(tmpdir) / "RE-001.md"
    revision_file.write_text(SAMPLE_REVISION_MD, encoding="utf-8")

    # Try invalid block index
    with pytest.raises(RevisionUpdateError, match="Block index .* out of range"):
      update_requirement_lifecycle_status(
        revision_file,
        "SPEC-150.FR-001",
        STATUS_ACTIVE,
        block_index=999,  # Out of range
        requirement_index=0,
      )


def test_update_requirement_lifecycle_status_validates_requirement_index() -> None:
  """Test that out-of-range requirement index raises error."""
  with TemporaryDirectory() as tmpdir:
    revision_file = Path(tmpdir) / "RE-001.md"
    revision_file.write_text(SAMPLE_REVISION_MD, encoding="utf-8")

    # Try invalid requirement index
    with pytest.raises(
      RevisionUpdateError,
      match="Requirement index .* out of range",
    ):
      update_requirement_lifecycle_status(
        revision_file,
        "SPEC-150.FR-001",
        STATUS_ACTIVE,
        block_index=0,
        requirement_index=999,  # Out of range
      )


def test_update_requirement_lifecycle_status_creates_lifecycle_if_missing() -> None:
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
      STATUS_ACTIVE,
      block_index=0,
      requirement_index=0,
    )

    assert changed is True

    # Verify lifecycle was added
    content = revision_file.read_text(encoding="utf-8")
    assert "lifecycle:" in content
    assert "status: active" in content


# --- Diff-based validation tests (DEC-046-01) ---

# Revision with pre-existing validation issues: PROD-* in spec_id (expects SPEC-*)
# and introduced_by doesn't match RE pattern.
REVISION_WITH_PREEXISTING_ERRORS = """---
id: RE-010
name: Test Revision With Pre-existing Issues
status: completed
kind: revision
---

# RE-010

```yaml supekku:revision.change@v1
schema: supekku.revision.change
version: 1
metadata:
  revision: RE-010
specs:
  - spec_id: PROD-008
    action: updated
requirements:
  - requirement_id: PROD-008.FR-001
    kind: functional
    action: introduce
    destination:
      spec: PROD-008
      requirement_id: PROD-008.FR-001
    lifecycle:
      status: pending
      introduced_by: DE-007
```
"""


def test_update_succeeds_with_preexisting_validation_errors() -> None:
  """Targeted update should succeed when block has pre-existing errors."""
  with TemporaryDirectory() as tmpdir:
    revision_file = Path(tmpdir) / "RE-010.md"
    revision_file.write_text(REVISION_WITH_PREEXISTING_ERRORS, encoding="utf-8")

    # This would previously fail because the entire block fails validation
    # (PROD-008 in spec_id, DE-007 in introduced_by).
    # With diff-based validation, it should succeed because the update
    # (pending → active) doesn't introduce NEW errors.
    changed = update_requirement_lifecycle_status(
      revision_file,
      "PROD-008.FR-001",
      STATUS_ACTIVE,
      block_index=0,
      requirement_index=0,
    )

    assert changed is True
    content = revision_file.read_text(encoding="utf-8")
    assert "status: active" in content


def test_update_rejects_genuinely_invalid_new_status() -> None:
  """Update that introduces new validation errors should still be rejected."""
  with TemporaryDirectory() as tmpdir:
    revision_file = Path(tmpdir) / "RE-001.md"
    revision_file.write_text(SAMPLE_REVISION_MD, encoding="utf-8")

    # Invalid status is caught by the explicit check before validation
    with pytest.raises(ValueError, match="Invalid status"):
      update_requirement_lifecycle_status(
        revision_file,
        "SPEC-150.FR-001",
        "bogus_status",
        block_index=0,
        requirement_index=0,
      )
