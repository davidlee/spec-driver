"""Tests for verification coverage block extraction and loading.

Validation of `verification.coverage` blocks is covered by
``verification_metadata_test.py`` (driven by ``MetadataValidator`` against
``VERIFICATION_COVERAGE_METADATA``). The hand-rolled
``VerificationCoverageValidator`` class was retired by DE-118 IP-118-P03 C1.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .verification import COVERAGE_MARKER, extract_coverage_blocks, load_coverage_blocks

if TYPE_CHECKING:
  from pathlib import Path

SAMPLE_VALID_YAML = """schema: supekku.verification.coverage
version: 1
subject: SPEC-123
entries:
  - artefact: VT-210
    kind: VT
    requirement: SPEC-123.FR-001
    phase: IP-456.PHASE-02
    status: verified
    notes: All test cases passing
  - artefact: VA-211
    kind: VA
    requirement: SPEC-123.NFR-002
    status: in-progress
"""


def _wrap_block(inner: str) -> str:
  return (
    f"# Test Document\n\n```yaml {COVERAGE_MARKER}\n{inner}```\n\n## More content\n"
  )


def test_extract_coverage_blocks_identifies_marker() -> None:
  """Test extracting coverage block identifies marker and structure."""
  content = _wrap_block(SAMPLE_VALID_YAML)
  blocks = extract_coverage_blocks(content)
  assert len(blocks) == 1
  block = blocks[0]
  assert block.raw_yaml.startswith("schema:")
  assert block.data["schema"] == "supekku.verification.coverage"
  assert block.data["version"] == 1


def test_extract_multiple_coverage_blocks() -> None:
  """Test extracting multiple coverage blocks from same document."""
  block1 = """schema: supekku.verification.coverage
version: 1
subject: SPEC-100
entries:
  - artefact: VT-100
    kind: VT
    requirement: SPEC-100.FR-001
    status: planned
"""
  block2 = """schema: supekku.verification.coverage
version: 1
subject: SPEC-200
entries:
  - artefact: VH-200
    kind: VH
    requirement: SPEC-200.FR-001
    status: verified
"""
  content = _wrap_block(block1) + "\n\n" + _wrap_block(block2)
  blocks = extract_coverage_blocks(content)
  assert len(blocks) == 2
  assert blocks[0].data["subject"] == "SPEC-100"
  assert blocks[1].data["subject"] == "SPEC-200"


def test_load_coverage_blocks_from_file(tmp_path: Path) -> None:
  """Test loading coverage blocks from file."""
  content = _wrap_block(SAMPLE_VALID_YAML)
  path = tmp_path / "test.md"
  path.write_text(content)

  blocks = load_coverage_blocks(path)
  assert len(blocks) == 1
  assert blocks[0].data["subject"] == "SPEC-123"
  assert len(blocks[0].data["entries"]) == 2


def test_extract_returns_empty_list_when_no_blocks() -> None:
  """Test extraction returns empty list when no coverage blocks found."""
  content = "# Document\n\nNo coverage blocks here.\n"
  blocks = extract_coverage_blocks(content)
  assert not blocks


def test_extract_raises_on_invalid_yaml() -> None:
  """Test extraction raises ValueError on invalid YAML."""
  invalid_content = f"```yaml {COVERAGE_MARKER}\ninvalid: yaml: :\n```"
  with pytest.raises(ValueError, match="invalid coverage YAML"):
    extract_coverage_blocks(invalid_content)


def test_extract_raises_on_non_mapping_yaml() -> None:
  """Test extraction raises ValueError on non-mapping YAML."""
  invalid_content = f"```yaml {COVERAGE_MARKER}\n- list\n- not\n- mapping\n```"
  with pytest.raises(ValueError, match="must parse to mapping"):
    extract_coverage_blocks(invalid_content)
