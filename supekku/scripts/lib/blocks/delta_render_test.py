"""Tests for delta relationship block rendering."""

from __future__ import annotations

from supekku.scripts.lib.blocks.delta import render_delta_relationships_block


def test_render_delta_relationships_block_minimal() -> None:
  """Test rendering delta relationships block with minimal data."""
  result = render_delta_relationships_block("DE-001")

  assert "```yaml supekku:delta.relationships@v1" in result
  assert "schema: supekku.delta.relationships" in result
  assert "version: 1" in result
  assert "delta: DE-001" in result
  assert "specs:" in result
  assert "requirements:" in result
  assert "phases: []" in result


def test_render_delta_relationships_block_with_specs() -> None:
  """Test rendering delta relationships block with specs."""
  result = render_delta_relationships_block(
    "DE-001",
    primary_specs=["SPEC-100", "SPEC-200"],
    collaborator_specs=["SPEC-300"],
  )

  assert "primary:" in result
  assert "- SPEC-100" in result
  assert "- SPEC-200" in result
  assert "collaborators:" in result
  assert "- SPEC-300" in result


def test_render_delta_relationships_block_with_requirements() -> None:
  """Test rendering delta relationships block with requirements."""
  result = render_delta_relationships_block(
    "DE-001",
    implements_requirements=["SPEC-100.FR-001"],
    updates_requirements=["SPEC-200.FR-002"],
    verifies_requirements=["SPEC-300.FR-003"],
  )

  assert "implements:" in result
  assert "- SPEC-100.FR-001" in result
  assert "updates:" in result
  assert "- SPEC-200.FR-002" in result
  assert "verifies:" in result
  assert "- SPEC-300.FR-003" in result


def test_render_delta_relationships_block_sorts_lists() -> None:
  """Test that rendering function sorts list items."""
  result = render_delta_relationships_block(
    "DE-001",
    primary_specs=["SPEC-300", "SPEC-100", "SPEC-200"],
  )

  # Find the position of each spec
  spec_100_pos = result.index("SPEC-100")
  spec_200_pos = result.index("SPEC-200")
  spec_300_pos = result.index("SPEC-300")

  # Verify sorted order
  assert spec_100_pos < spec_200_pos < spec_300_pos
