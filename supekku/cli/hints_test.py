"""Tests for schema hint output — VT-077-schema-hints."""

from __future__ import annotations

import unittest

from supekku.cli.hints import ARTIFACT_SCHEMA_MAP, format_schema_hints


class FormatSchemaHintsTest(unittest.TestCase):
  """Unit tests for format_schema_hints()."""

  def test_delta_hints_include_relationships(self) -> None:
    hints = format_schema_hints("delta")
    assert any("delta.relationships" in h for h in hints)

  def test_delta_hints_include_frontmatter(self) -> None:
    hints = format_schema_hints("delta")
    assert any("frontmatter.delta" in h for h in hints)

  def test_plan_hints(self) -> None:
    hints = format_schema_hints("plan")
    assert any("plan.overview" in h for h in hints)

  def test_phase_hints(self) -> None:
    hints = format_schema_hints("phase")
    assert any("phase.overview" in h for h in hints)
    assert any("phase.tracking" in h for h in hints)

  def test_revision_hints(self) -> None:
    hints = format_schema_hints("revision")
    assert any("revision.change" in h for h in hints)

  def test_audit_hints(self) -> None:
    hints = format_schema_hints("audit")
    assert any("verification.coverage" in h for h in hints)

  def test_spec_hints_include_block_schemas(self) -> None:
    hints = format_schema_hints("spec")
    assert any("spec.relationships" in h for h in hints)
    assert any("spec.capabilities" in h for h in hints)

  def test_prod_hints(self) -> None:
    hints = format_schema_hints("prod")
    assert any("frontmatter.prod" in h for h in hints)

  def test_policy_hints(self) -> None:
    hints = format_schema_hints("policy")
    assert any("frontmatter.policy" in h for h in hints)

  def test_standard_hints(self) -> None:
    hints = format_schema_hints("standard")
    assert any("frontmatter.standard" in h for h in hints)

  def test_memory_hints(self) -> None:
    hints = format_schema_hints("memory")
    assert any("frontmatter.memory" in h for h in hints)

  def test_unmapped_kind_returns_empty(self) -> None:
    assert format_schema_hints("unknown_artifact") == []

  def test_card_returns_empty(self) -> None:
    """Card has no meaningful schemas to hint."""
    assert format_schema_hints("card") == []

  def test_hints_are_runnable_commands(self) -> None:
    """Each hint should be a spec-driver schema show command."""
    for kind in ARTIFACT_SCHEMA_MAP:
      for hint in format_schema_hints(kind):
        assert "spec-driver schema show" in hint
        assert "-f yaml-example" in hint

  def test_all_mapped_kinds_produce_nonempty_hints(self) -> None:
    for kind in ARTIFACT_SCHEMA_MAP:
      hints = format_schema_hints(kind)
      assert len(hints) > 0, f"Expected hints for {kind}"


if __name__ == "__main__":
  unittest.main()
