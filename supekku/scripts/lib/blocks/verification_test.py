"""Tests for verification coverage block module."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .verification import (
  COVERAGE_MARKER,
  VerificationCoverageValidator,
  extract_coverage_blocks,
  load_coverage_blocks,
)

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
    f"# Test Document\n\n```yaml {COVERAGE_MARKER}\n"
    f"{inner}```\n\n## More content\n"
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


def test_validator_accepts_minimal_valid_payload() -> None:
  """Test validator accepts minimal valid coverage block."""
  validator = VerificationCoverageValidator()
  content = _wrap_block(SAMPLE_VALID_YAML)
  block = extract_coverage_blocks(content)[0]
  errors = validator.validate(block)
  assert not errors


def test_validator_accepts_optional_phase() -> None:
  """Test validator accepts entries with optional phase field."""
  validator = VerificationCoverageValidator()
  yaml_without_phase = """schema: supekku.verification.coverage
version: 1
subject: SPEC-123
entries:
  - artefact: VT-210
    kind: VT
    requirement: SPEC-123.FR-001
    status: verified
"""
  block = extract_coverage_blocks(_wrap_block(yaml_without_phase))[0]
  errors = validator.validate(block)
  assert not errors


def test_validator_accepts_optional_notes() -> None:
  """Test validator accepts entries with optional notes field."""
  validator = VerificationCoverageValidator()
  yaml_with_notes = """schema: supekku.verification.coverage
version: 1
subject: SPEC-123
entries:
  - artefact: VT-210
    kind: VT
    requirement: SPEC-123.FR-001
    status: verified
    notes: Test passed successfully
"""
  block = extract_coverage_blocks(_wrap_block(yaml_with_notes))[0]
  errors = validator.validate(block)
  assert not errors


def test_validator_flags_missing_schema() -> None:
  """Test validator flags missing schema field."""
  validator = VerificationCoverageValidator()
  invalid_yaml = """version: 1
subject: SPEC-123
entries:
  - artefact: VT-210
    kind: VT
    requirement: SPEC-123.FR-001
    status: verified
"""
  block = extract_coverage_blocks(_wrap_block(invalid_yaml))[0]
  errors = validator.validate(block)
  assert any("schema" in err for err in errors)


def test_validator_flags_wrong_version() -> None:
  """Test validator flags incorrect version."""
  validator = VerificationCoverageValidator()
  invalid_yaml = """schema: supekku.verification.coverage
version: 99
subject: SPEC-123
entries:
  - artefact: VT-210
    kind: VT
    requirement: SPEC-123.FR-001
    status: verified
"""
  block = extract_coverage_blocks(_wrap_block(invalid_yaml))[0]
  errors = validator.validate(block)
  assert any("version" in err for err in errors)


def test_validator_flags_missing_subject() -> None:
  """Test validator flags missing subject field."""
  validator = VerificationCoverageValidator()
  invalid_yaml = """schema: supekku.verification.coverage
version: 1
entries:
  - artefact: VT-210
    kind: VT
    requirement: SPEC-123.FR-001
    status: verified
"""
  block = extract_coverage_blocks(_wrap_block(invalid_yaml))[0]
  errors = validator.validate(block)
  assert any("subject" in err for err in errors)


def test_validator_flags_invalid_subject_pattern() -> None:
  """Test validator flags subject with invalid pattern."""
  validator = VerificationCoverageValidator()
  invalid_yaml = """schema: supekku.verification.coverage
version: 1
subject: INVALID-123
entries:
  - artefact: VT-210
    kind: VT
    requirement: SPEC-123.FR-001
    status: verified
"""
  block = extract_coverage_blocks(_wrap_block(invalid_yaml))[0]
  errors = validator.validate(block)
  assert any("pattern" in err and "INVALID-123" in err for err in errors)


def test_validator_accepts_all_subject_prefixes() -> None:
  """Test validator accepts SPEC, PROD, IP, and AUD subject prefixes."""
  validator = VerificationCoverageValidator()
  for prefix in ["SPEC", "PROD", "IP", "AUD"]:
    yaml_block = f"""schema: supekku.verification.coverage
version: 1
subject: {prefix}-123
entries:
  - artefact: VT-210
    kind: VT
    requirement: SPEC-123.FR-001
    status: verified
"""
    block = extract_coverage_blocks(_wrap_block(yaml_block))[0]
    errors = validator.validate(block)
    assert not errors, f"Failed for prefix {prefix}: {errors}"


def test_validator_flags_missing_entries() -> None:
  """Test validator flags missing entries field."""
  validator = VerificationCoverageValidator()
  invalid_yaml = """schema: supekku.verification.coverage
version: 1
subject: SPEC-123
"""
  block = extract_coverage_blocks(_wrap_block(invalid_yaml))[0]
  errors = validator.validate(block)
  assert any("entries" in err for err in errors)


def test_validator_flags_entries_not_list() -> None:
  """Test validator flags entries as non-list."""
  validator = VerificationCoverageValidator()
  invalid_yaml = """schema: supekku.verification.coverage
version: 1
subject: SPEC-123
entries: not-a-list
"""
  block = extract_coverage_blocks(_wrap_block(invalid_yaml))[0]
  errors = validator.validate(block)
  assert any("list" in err for err in errors)


def test_validator_flags_entry_not_object() -> None:
  """Test validator flags entry as non-object."""
  validator = VerificationCoverageValidator()
  invalid_yaml = """schema: supekku.verification.coverage
version: 1
subject: SPEC-123
entries:
  - not-an-object
"""
  block = extract_coverage_blocks(_wrap_block(invalid_yaml))[0]
  errors = validator.validate(block)
  assert any("object" in err for err in errors)


def test_validator_flags_missing_artefact() -> None:
  """Test validator flags missing artefact field."""
  validator = VerificationCoverageValidator()
  invalid_yaml = """schema: supekku.verification.coverage
version: 1
subject: SPEC-123
entries:
  - kind: VT
    requirement: SPEC-123.FR-001
    status: verified
"""
  block = extract_coverage_blocks(_wrap_block(invalid_yaml))[0]
  errors = validator.validate(block)
  assert any("artefact" in err for err in errors)


def test_validator_flags_invalid_artefact_pattern() -> None:
  """Test validator flags artefact with invalid pattern."""
  validator = VerificationCoverageValidator()
  invalid_yaml = """schema: supekku.verification.coverage
version: 1
subject: SPEC-123
entries:
  - artefact: INVALID-210
    kind: VT
    requirement: SPEC-123.FR-001
    status: verified
"""
  block = extract_coverage_blocks(_wrap_block(invalid_yaml))[0]
  errors = validator.validate(block)
  assert any("V[TAH]-###" in err for err in errors)


def test_validator_accepts_all_verification_kinds() -> None:
  """Test validator accepts VT, VA, and VH artifact kinds."""
  validator = VerificationCoverageValidator()
  for kind, prefix in [("VT", "VT"), ("VA", "VA"), ("VH", "VH")]:
    yaml_block = f"""schema: supekku.verification.coverage
version: 1
subject: SPEC-123
entries:
  - artefact: {prefix}-210
    kind: {kind}
    requirement: SPEC-123.FR-001
    status: verified
"""
    block = extract_coverage_blocks(_wrap_block(yaml_block))[0]
    errors = validator.validate(block)
    assert not errors, f"Failed for kind {kind}: {errors}"


def test_validator_flags_invalid_kind() -> None:
  """Test validator flags invalid kind value."""
  validator = VerificationCoverageValidator()
  invalid_yaml = """schema: supekku.verification.coverage
version: 1
subject: SPEC-123
entries:
  - artefact: VT-210
    kind: INVALID
    requirement: SPEC-123.FR-001
    status: verified
"""
  block = extract_coverage_blocks(_wrap_block(invalid_yaml))[0]
  errors = validator.validate(block)
  assert any("kind" in err and "INVALID" in err for err in errors)


def test_validator_flags_missing_requirement() -> None:
  """Test validator flags missing requirement field."""
  validator = VerificationCoverageValidator()
  invalid_yaml = """schema: supekku.verification.coverage
version: 1
subject: SPEC-123
entries:
  - artefact: VT-210
    kind: VT
    status: verified
"""
  block = extract_coverage_blocks(_wrap_block(invalid_yaml))[0]
  errors = validator.validate(block)
  assert any("requirement" in err for err in errors)


def test_validator_flags_invalid_requirement_pattern() -> None:
  """Test validator flags requirement with invalid pattern."""
  validator = VerificationCoverageValidator()
  invalid_yaml = """schema: supekku.verification.coverage
version: 1
subject: SPEC-123
entries:
  - artefact: VT-210
    kind: VT
    requirement: INVALID
    status: verified
"""
  block = extract_coverage_blocks(_wrap_block(invalid_yaml))[0]
  errors = validator.validate(block)
  assert any("requirement" in err and "INVALID" in err for err in errors)


def test_validator_accepts_fr_and_nfr_requirements() -> None:
  """Test validator accepts both FR and NFR requirement types."""
  validator = VerificationCoverageValidator()
  for req_type in ["FR", "NFR"]:
    yaml_block = f"""schema: supekku.verification.coverage
version: 1
subject: SPEC-123
entries:
  - artefact: VT-210
    kind: VT
    requirement: SPEC-123.{req_type}-001
    status: verified
"""
    block = extract_coverage_blocks(_wrap_block(yaml_block))[0]
    errors = validator.validate(block)
    assert not errors, f"Failed for requirement type {req_type}: {errors}"


def test_validator_flags_invalid_phase_pattern() -> None:
  """Test validator flags phase with invalid pattern."""
  validator = VerificationCoverageValidator()
  invalid_yaml = """schema: supekku.verification.coverage
version: 1
subject: SPEC-123
entries:
  - artefact: VT-210
    kind: VT
    requirement: SPEC-123.FR-001
    phase: INVALID-PHASE
    status: verified
"""
  block = extract_coverage_blocks(_wrap_block(invalid_yaml))[0]
  errors = validator.validate(block)
  assert any("phase" in err and "INVALID-PHASE" in err for err in errors)


def test_validator_flags_missing_status() -> None:
  """Test validator flags missing status field."""
  validator = VerificationCoverageValidator()
  invalid_yaml = """schema: supekku.verification.coverage
version: 1
subject: SPEC-123
entries:
  - artefact: VT-210
    kind: VT
    requirement: SPEC-123.FR-001
"""
  block = extract_coverage_blocks(_wrap_block(invalid_yaml))[0]
  errors = validator.validate(block)
  assert any("status" in err for err in errors)


def test_validator_flags_invalid_status() -> None:
  """Test validator flags invalid status value."""
  validator = VerificationCoverageValidator()
  invalid_yaml = """schema: supekku.verification.coverage
version: 1
subject: SPEC-123
entries:
  - artefact: VT-210
    kind: VT
    requirement: SPEC-123.FR-001
    status: invalid-status
"""
  block = extract_coverage_blocks(_wrap_block(invalid_yaml))[0]
  errors = validator.validate(block)
  assert any("status" in err and "invalid-status" in err for err in errors)


def test_validator_accepts_all_valid_statuses() -> None:
  """Test validator accepts all valid status values."""
  validator = VerificationCoverageValidator()
  for status in ["planned", "in-progress", "verified", "failed", "blocked"]:
    yaml_block = f"""schema: supekku.verification.coverage
version: 1
subject: SPEC-123
entries:
  - artefact: VT-210
    kind: VT
    requirement: SPEC-123.FR-001
    status: {status}
"""
    block = extract_coverage_blocks(_wrap_block(yaml_block))[0]
    errors = validator.validate(block)
    assert not errors, f"Failed for status {status}: {errors}"


def test_validator_with_subject_id_match() -> None:
  """Test validator accepts matching subject_id parameter."""
  validator = VerificationCoverageValidator()
  block = extract_coverage_blocks(_wrap_block(SAMPLE_VALID_YAML))[0]
  errors = validator.validate(block, subject_id="SPEC-123")
  assert not errors


def test_validator_with_subject_id_mismatch() -> None:
  """Test validator flags mismatching subject_id parameter."""
  validator = VerificationCoverageValidator()
  block = extract_coverage_blocks(_wrap_block(SAMPLE_VALID_YAML))[0]
  errors = validator.validate(block, subject_id="SPEC-999")
  assert any("does not match expected" in err for err in errors)


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
  assert blocks == []


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
