"""Tests for revision_blocks module."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .revision_blocks import (
  REVISION_BLOCK_MARKER,
  RevisionBlockValidator,
  extract_revision_blocks,
)

if TYPE_CHECKING:
  from pathlib import Path

SAMPLE_VALID_YAML = """schema: supekku.revision.change
version: 1
metadata:
  revision: RE-123
specs:
  - spec_id: SPEC-150
    action: updated
requirements:
  - requirement_id: SPEC-150.FR-009
    kind: functional
    action: move
    origin:
      - kind: requirement
        ref: SPEC-002.FR-009
    destination:
      spec: SPEC-150
      requirement_id: SPEC-150.FR-009
      additional_specs:
        - SPEC-002
"""


def _wrap_block(inner: str) -> str:
  return f"intro\n```yaml {REVISION_BLOCK_MARKER}\n{inner}```\n<!-- id: block -->\n"


def test_extract_revision_block_identifies_marker() -> None:
  """Test extracting revision block identifies marker and structure."""
  content = _wrap_block(SAMPLE_VALID_YAML)
  blocks = extract_revision_blocks(content)
  assert len(blocks) == 1
  block = blocks[0]
  assert block.marker == REVISION_BLOCK_MARKER
  assert block.language == "yaml"
  assert block.content_start < block.content_end
  assert block.yaml_content.startswith("schema:")


def test_validator_accepts_minimal_valid_payload() -> None:
  """Test validator accepts minimal valid revision block."""
  validator = RevisionBlockValidator()
  content = _wrap_block(SAMPLE_VALID_YAML)
  block = extract_revision_blocks(content)[0]
  data = block.parse()
  messages = validator.validate(data)
  assert not messages


def test_validator_flags_missing_destination_for_move() -> None:
  """Test validator flags move action missing destination."""
  validator = RevisionBlockValidator()
  invalid_yaml = """schema: supekku.revision.change
version: 1
metadata:
  revision: RE-321
specs: []
requirements:
  - requirement_id: SPEC-001.FR-001
    kind: functional
    action: move
    origin:
      - kind: requirement
        ref: SPEC-001.FR-001
"""
  block = extract_revision_blocks(_wrap_block(invalid_yaml))[0]
  data = block.parse()
  messages = validator.validate(data)
  assert any("destination" in msg.render_path() for msg in messages)


def test_validator_flags_invalid_additional_specs() -> None:
  """Test validator flags invalid additional_specs."""
  validator = RevisionBlockValidator()
  invalid = """schema: supekku.revision.change
version: 1
metadata:
  revision: RE-777
specs: []
requirements:
  - requirement_id: SPEC-001.FR-001
    kind: functional
    action: introduce
    destination:
      spec: SPEC-001
      additional_specs:
        - SPEC-FOO
        - SPEC-002
"""
  block = extract_revision_blocks(_wrap_block(invalid))[0]
  data = block.parse()
  messages = validator.validate(data)
  assert any("additional_specs" in msg.render_path() for msg in messages)


def test_formatting_rewrites_inline_mappings(tmp_path: Path) -> None:
  """Test formatting rewrites inline YAML mappings to block style."""
  inline_yaml = """schema: supekku.revision.change
version: 1
metadata: {revision: RE-321}
specs: []
requirements: []
"""
  original = _wrap_block(inline_yaml)
  path = tmp_path / "sample.md"
  path.write_text(original)

  block = extract_revision_blocks(original)[0]
  data = block.parse()
  formatted = block.formatted_yaml(data)
  assert "metadata:\n  revision:" in formatted
  updated = block.replace_content(original, formatted)
  path.write_text(updated)
  after = path.read_text()
  assert "metadata:\n  revision: RE-321" in after
  assert after.endswith("<!-- id: block -->\n")
