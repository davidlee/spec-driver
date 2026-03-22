"""Tests for spec_sync core models."""

import unittest
from pathlib import Path

import pytest
from pydantic import ValidationError

from .models import DocVariant, SourceDescriptor, SourceUnit, SyncOutcome


class TestSourceUnit(unittest.TestCase):
  """Test SourceUnit model."""

  def test_source_unit_creation(self) -> None:
    """Test SourceUnit can be created with required fields."""
    unit = SourceUnit(language="go", identifier="internal/foo", root=Path("/repo"))

    assert unit.language == "go"
    assert unit.identifier == "internal/foo"
    assert unit.root == Path("/repo")

  def test_source_unit_immutable(self) -> None:
    """Test SourceUnit is immutable (frozen model)."""
    unit = SourceUnit(language="go", identifier="internal/foo", root=Path("/repo"))

    with pytest.raises(ValidationError):
      unit.language = "python"  # type: ignore

  def test_source_unit_equality(self) -> None:
    """Test SourceUnit equality comparison."""
    unit1 = SourceUnit(language="go", identifier="internal/foo", root=Path("/repo"))
    unit2 = SourceUnit(language="go", identifier="internal/foo", root=Path("/repo"))
    unit3 = SourceUnit(language="python", identifier="internal/foo", root=Path("/repo"))

    assert unit1 == unit2
    assert unit1 != unit3


class TestDocVariant(unittest.TestCase):
  """Test DocVariant model."""

  def test_doc_variant_creation(self) -> None:
    """Test DocVariant can be created with required fields."""
    variant = DocVariant(
      name="public",
      path=Path("contracts/go/foo-public.md"),
      hash="abc123",
      status="created",
    )

    assert variant.name == "public"
    assert variant.path == Path("contracts/go/foo-public.md")
    assert variant.hash == "abc123"
    assert variant.status == "created"

  def test_doc_variant_immutable(self) -> None:
    """Test DocVariant is immutable (frozen model)."""
    variant = DocVariant(
      name="public",
      path=Path("test.md"),
      hash="hash",
      status="created",
    )

    with pytest.raises(ValidationError):
      variant.name = "private"  # type: ignore

  def test_doc_variant_status_types(self) -> None:
    """Test DocVariant accepts valid status values."""
    for status in ["created", "changed", "unchanged"]:
      variant = DocVariant(
        name="public",
        path=Path("test.md"),
        hash="hash",
        status=status,
      )
      assert variant.status == status


class TestSourceDescriptor(unittest.TestCase):
  """Test SourceDescriptor model."""

  def test_source_descriptor_creation(self) -> None:
    """Test SourceDescriptor can be created with required fields."""
    variant = DocVariant(
      name="public",
      path=Path("test.md"),
      hash="hash",
      status="created",
    )
    descriptor = SourceDescriptor(
      slug_parts=["internal", "foo"],
      default_frontmatter={"packages": ["internal/foo"]},
      variants=[variant],
    )

    assert descriptor.slug_parts == ["internal", "foo"]
    assert descriptor.default_frontmatter["packages"] == ["internal/foo"]
    assert len(descriptor.variants) == 1
    assert descriptor.variants[0] == variant


class TestSyncOutcome(unittest.TestCase):
  """Test SyncOutcome model."""

  def test_sync_outcome_defaults(self) -> None:
    """Test SyncOutcome has sensible defaults."""
    outcome = SyncOutcome()

    assert not outcome.processed_units
    assert not outcome.created_specs
    assert not outcome.skipped_units
    assert not outcome.warnings
    assert not outcome.errors

  def test_sync_outcome_with_data(self) -> None:
    """Test SyncOutcome can store operation results."""
    unit = SourceUnit(language="go", identifier="internal/foo", root=Path("/repo"))
    outcome = SyncOutcome(
      processed_units=[unit],
      created_specs={"go:internal/foo": "SPEC-001"},
      skipped_units=["invalid/package"],
      warnings=["gomarkdoc not found"],
      errors=["syntax error in file.go"],
    )

    assert len(outcome.processed_units) == 1
    assert outcome.processed_units[0] == unit
    assert outcome.created_specs["go:internal/foo"] == "SPEC-001"
    assert "invalid/package" in outcome.skipped_units
    assert "gomarkdoc not found" in outcome.warnings
    assert "syntax error in file.go" in outcome.errors


if __name__ == "__main__":
  unittest.main()
