"""Tests for spec_utils module."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from supekku.scripts.lib.frontmatter_schema import FrontmatterValidationError
from supekku.scripts.lib.spec_utils import (
    append_unique,
    dump_markdown_file,
    ensure_list_entry,
    load_markdown_file,
    load_validated_markdown_file,
    validate_frontmatter,
)


class SpecUtilsTestCase(unittest.TestCase):
    """Test cases for spec_utils module functionality."""

    def test_load_markdown_file_parses_frontmatter_and_body(self) -> None:
        content = textwrap.dedent(
            """
            ---
            id: SPEC-001
            name: Example Spec
            kind: spec
            ---

            Body line
            ---
            Extra body line
            """
        ).lstrip("\n")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "spec.md"
            path.write_text(content, encoding="utf-8")

            frontmatter, body = load_markdown_file(path)

        self.assertEqual(
            frontmatter,
            {
                "id": "SPEC-001",
                "name": "Example Spec",
                "kind": "spec",
            },
        )
        self.assertEqual(body, "Body line\n---\nExtra body line\n")

    def test_dump_markdown_file_round_trip(self) -> None:
        frontmatter = {"id": "SPEC-010", "name": "Round Trip", "kind": "spec"}
        body = "Round trip body\n"

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "spec.md"
            dump_markdown_file(path, frontmatter, body)

            reloaded_frontmatter, reloaded_body = load_markdown_file(path)

        self.assertEqual(reloaded_frontmatter, frontmatter)
        self.assertEqual(reloaded_body, body)

    def test_ensure_list_entry_returns_existing_list(self) -> None:
        data = {"owners": ["alice"]}
        result = ensure_list_entry(data, "owners")
        self.assertIs(result, data["owners"])

        result.append("bob")
        self.assertEqual(data["owners"], ["alice", "bob"])

    def test_ensure_list_entry_raises_for_non_list(self) -> None:
        data = {"owners": "alice"}
        with self.assertRaises(TypeError):
            ensure_list_entry(data, "owners")

    def test_append_unique_appends_when_missing(self) -> None:
        values = ["alice"]
        modified = append_unique(values, "bob")
        self.assertTrue(modified)
        self.assertEqual(values, ["alice", "bob"])

    def test_append_unique_skips_existing_item(self) -> None:
        values = ["alice", "bob"]
        modified = append_unique(values, "alice")
        self.assertFalse(modified)
        self.assertEqual(values, ["alice", "bob"])

    def test_validate_frontmatter_success(self) -> None:
        frontmatter = {
            "id": "SPEC-200",
            "name": "Validated Spec",
            "slug": "validated-spec",
            "kind": "spec",
            "status": "draft",
            "created": "2024-06-01",
            "updated": "2024-07-01",
            "owners": ["alice"],
            "relations": [
                {
                    "type": "implements",
                    "target": "FR-100",
                    "annotation": "covers primary requirement",
                }
            ],
        }

        result = validate_frontmatter(frontmatter)

        self.assertEqual(result.id, "SPEC-200")
        self.assertEqual(result.created.isoformat(), "2024-06-01")
        self.assertEqual(len(result.relations), 1)
        relation = result.relations[0]
        self.assertEqual(relation.type, "implements")
        self.assertEqual(relation.target, "FR-100")
        self.assertEqual(
            result.data["relations"][0]["annotation"], "covers primary requirement"
        )
        self.assertIsNot(result.data, frontmatter)
        self.assertEqual(frontmatter["owners"], ["alice"])

    def test_validate_frontmatter_missing_required_field(self) -> None:
        frontmatter = {
            "name": "Missing Id",
            "slug": "missing-id",
            "kind": "spec",
            "status": "draft",
            "created": "2024-06-01",
            "updated": "2024-07-01",
        }

        with self.assertRaises(FrontmatterValidationError):
            validate_frontmatter(frontmatter)

    def test_validate_frontmatter_invalid_relations(self) -> None:
        frontmatter = {
            "id": "SPEC-201",
            "name": "Bad Relations",
            "slug": "bad-relations",
            "kind": "spec",
            "status": "draft",
            "created": "2024-06-01",
            "updated": "2024-07-01",
            "relations": ["not-a-mapping"],
        }

        with self.assertRaises(FrontmatterValidationError):
            validate_frontmatter(frontmatter)

    def test_load_validated_markdown_file_round_trip(self) -> None:
        frontmatter = {
            "id": "SPEC-202",
            "name": "Load Validated",
            "slug": "load-validated",
            "kind": "spec",
            "status": "draft",
            "created": "2024-06-01",
            "updated": "2024-07-01",
        }
        body = "Some content\n"

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "spec.md"
            dump_markdown_file(path, frontmatter, body)

            result, loaded_body = load_validated_markdown_file(path)

        self.assertEqual(result.slug, "load-validated")
        self.assertEqual(loaded_body, body)


if __name__ == "__main__":
    unittest.main()
