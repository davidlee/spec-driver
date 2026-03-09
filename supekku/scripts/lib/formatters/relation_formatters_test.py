"""Tests for relation_formatters — VT-085-005."""

from supekku.scripts.lib.relations.query import ReferenceHit

from .relation_formatters import format_refs_count, format_refs_tsv


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
