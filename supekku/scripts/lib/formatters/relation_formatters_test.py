"""Tests for relation_formatters — VT-085-005 and VT-090-P5."""

from supekku.scripts.lib.relations.query import ReferenceHit

from .relation_formatters import format_refs_count, format_refs_tsv, format_related_section


class TestFormatRefsCount:
  """VT-085-005: format_refs_count rendering."""

  def test_empty_list(self) -> None:
    assert format_refs_count([]) == ""

  def test_single_ref(self) -> None:
    refs = [ReferenceHit(target="PROD-010", source="relation", detail="implements")]
    assert format_refs_count(refs) == "1 ref"

  def test_multiple_refs(self) -> None:
    refs = [
      ReferenceHit(target="PROD-010", source="relation", detail="implements"),
      ReferenceHit(target="IMPR-006", source="context_input", detail="issue"),
      ReferenceHit(target="SPEC-100", source="applies_to", detail="spec"),
    ]
    assert format_refs_count(refs) == "3 refs"

  def test_two_refs_plural(self) -> None:
    refs = [
      ReferenceHit(target="A", source="relation", detail="x"),
      ReferenceHit(target="B", source="relation", detail="y"),
    ]
    assert format_refs_count(refs) == "2 refs"


class TestFormatRefsTsv:
  """VT-085-005: format_refs_tsv rendering."""

  def test_empty_list(self) -> None:
    assert format_refs_tsv([]) == ""

  def test_single_ref(self) -> None:
    refs = [ReferenceHit(target="PROD-010", source="relation", detail="implements")]
    assert format_refs_tsv(refs) == "relation.implements:PROD-010"

  def test_multiple_refs(self) -> None:
    refs = [
      ReferenceHit(target="PROD-010", source="relation", detail="implements"),
      ReferenceHit(target="IMPR-006", source="context_input", detail="issue"),
    ]
    expected = "relation.implements:PROD-010,context_input.issue:IMPR-006"
    assert format_refs_tsv(refs) == expected

  def test_empty_detail(self) -> None:
    refs = [ReferenceHit(target="X", source="relation", detail="")]
    assert format_refs_tsv(refs) == "relation:X"

  def test_informed_by_source(self) -> None:
    refs = [ReferenceHit(target="ADR-001", source="informed_by", detail="adr")]
    assert format_refs_tsv(refs) == "informed_by.adr:ADR-001"

  def test_applies_to_source(self) -> None:
    refs = [ReferenceHit(target="REQ-001", source="applies_to", detail="requirement")]
    assert format_refs_tsv(refs) == "applies_to.requirement:REQ-001"


class TestFormatRelatedSection:
  """VT-090-P5-4/P5-5: format_related_section rendering."""

  def test_empty_dict_returns_empty_list(self) -> None:
    """VT-090-P5-5: No references → no section."""
    assert format_related_section({}) == []

  def test_single_kind(self) -> None:
    refs = {"delta": [("DE-009", "CLI JSON fixes"), ("DE-011", "Enhanced filtering")]}
    result = format_related_section(refs)
    assert "Referenced by:" in result
    assert "  Deltas (2):" in result
    assert "    DE-009  CLI JSON fixes" in result
    assert "    DE-011  Enhanced filtering" in result

  def test_multiple_kinds_sorted(self) -> None:
    refs = {
      "revision": [("RE-024", "Delta completion")],
      "audit": [("AUD-004", "Conformance")],
      "delta": [("DE-009", "Fixes")],
    }
    result = format_related_section(refs)
    # Kinds should be sorted alphabetically
    kind_lines = [line for line in result if "(" in line and "):" in line]
    assert len(kind_lines) == 3
    assert "Audits" in kind_lines[0]
    assert "Deltas" in kind_lines[1]
    assert "Revisions" in kind_lines[2]

  def test_kind_label_replaces_underscore(self) -> None:
    refs = {"drift_ledger": [("DL-001", "Spec drift")]}
    result = format_related_section(refs)
    assert "  Drift Ledgers (1):" in result

  def test_starts_with_blank_line(self) -> None:
    refs = {"delta": [("DE-001", "Test")]}
    result = format_related_section(refs)
    assert result[0] == ""
    assert result[1] == "Referenced by:"
