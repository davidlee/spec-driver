"""Tests for spec_sync core models.
"""

import unittest
from pathlib import Path

from .models import DocVariant, SourceDescriptor, SourceUnit, SyncOutcome


class TestSourceUnit(unittest.TestCase):
    """Test SourceUnit model."""

    def test_source_unit_creation(self):
        """Test SourceUnit can be created with required fields."""
        unit = SourceUnit(language="go", identifier="internal/foo", root=Path("/repo"))

        self.assertEqual(unit.language, "go")
        self.assertEqual(unit.identifier, "internal/foo")
        self.assertEqual(unit.root, Path("/repo"))

    def test_source_unit_immutable(self):
        """Test SourceUnit is immutable (frozen dataclass)."""
        unit = SourceUnit("go", "internal/foo", Path("/repo"))

        with self.assertRaises(AttributeError):
            unit.language = "python"  # type: ignore

    def test_source_unit_equality(self):
        """Test SourceUnit equality comparison."""
        unit1 = SourceUnit("go", "internal/foo", Path("/repo"))
        unit2 = SourceUnit("go", "internal/foo", Path("/repo"))
        unit3 = SourceUnit("python", "internal/foo", Path("/repo"))

        self.assertEqual(unit1, unit2)
        self.assertNotEqual(unit1, unit3)


class TestDocVariant(unittest.TestCase):
    """Test DocVariant model."""

    def test_doc_variant_creation(self):
        """Test DocVariant can be created with required fields."""
        variant = DocVariant(
            name="public",
            path=Path("contracts/go/foo-public.md"),
            hash="abc123",
            status="created",
        )

        self.assertEqual(variant.name, "public")
        self.assertEqual(variant.path, Path("contracts/go/foo-public.md"))
        self.assertEqual(variant.hash, "abc123")
        self.assertEqual(variant.status, "created")

    def test_doc_variant_immutable(self):
        """Test DocVariant is immutable (frozen dataclass)."""
        variant = DocVariant("public", Path("test.md"), "hash", "created")

        with self.assertRaises(AttributeError):
            variant.name = "private"  # type: ignore

    def test_doc_variant_status_types(self):
        """Test DocVariant accepts valid status values."""
        for status in ["created", "changed", "unchanged"]:
            variant = DocVariant("public", Path("test.md"), "hash", status)
            self.assertEqual(variant.status, status)


class TestSourceDescriptor(unittest.TestCase):
    """Test SourceDescriptor model."""

    def test_source_descriptor_creation(self):
        """Test SourceDescriptor can be created with required fields."""
        variant = DocVariant("public", Path("test.md"), "hash", "created")
        descriptor = SourceDescriptor(
            slug_parts=["internal", "foo"],
            default_frontmatter={"packages": ["internal/foo"]},
            variants=[variant],
        )

        self.assertEqual(descriptor.slug_parts, ["internal", "foo"])
        self.assertEqual(descriptor.default_frontmatter["packages"], ["internal/foo"])
        self.assertEqual(len(descriptor.variants), 1)
        self.assertEqual(descriptor.variants[0], variant)


class TestSyncOutcome(unittest.TestCase):
    """Test SyncOutcome model."""

    def test_sync_outcome_defaults(self):
        """Test SyncOutcome has sensible defaults."""
        outcome = SyncOutcome()

        self.assertEqual(outcome.processed_units, [])
        self.assertEqual(outcome.created_specs, {})
        self.assertEqual(outcome.skipped_units, [])
        self.assertEqual(outcome.warnings, [])
        self.assertEqual(outcome.errors, [])

    def test_sync_outcome_with_data(self):
        """Test SyncOutcome can store operation results."""
        unit = SourceUnit("go", "internal/foo", Path("/repo"))
        outcome = SyncOutcome(
            processed_units=[unit],
            created_specs={"go:internal/foo": "SPEC-001"},
            skipped_units=["invalid/package"],
            warnings=["gomarkdoc not found"],
            errors=["syntax error in file.go"],
        )

        self.assertEqual(len(outcome.processed_units), 1)
        self.assertEqual(outcome.processed_units[0], unit)
        self.assertEqual(outcome.created_specs["go:internal/foo"], "SPEC-001")
        self.assertIn("invalid/package", outcome.skipped_units)
        self.assertIn("gomarkdoc not found", outcome.warnings)
        self.assertIn("syntax error in file.go", outcome.errors)


if __name__ == "__main__":
    unittest.main()
