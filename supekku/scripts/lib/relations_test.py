"""Tests for relations module."""

from __future__ import annotations

import os
import unittest
from pathlib import Path

from supekku.scripts.lib.relations import add_relation, list_relations, remove_relation
from supekku.scripts.lib.spec_utils import dump_markdown_file
from supekku.scripts.lib.test_base import RepoTestCase


class RelationsTest(RepoTestCase):
    """Test cases for relations management functionality."""

    def _make_spec(self) -> Path:
        root = super()._make_repo()
        spec_path = root / "SPEC-001.md"
        frontmatter = {
            "id": "SPEC-001",
            "slug": "example",
            "name": "Example Spec",
            "created": "2024-06-01",
            "updated": "2024-06-01",
            "status": "draft",
            "kind": "spec",
        }
        dump_markdown_file(spec_path, frontmatter, "# Example\n")
        os.chdir(root)
        return spec_path

    def test_list_relations_empty(self) -> None:
        spec_path = self._make_spec()
        relations = list_relations(spec_path)
        self.assertEqual(relations, [])

    def test_add_relation(self) -> None:
        spec_path = self._make_spec()
        added = add_relation(
            spec_path,
            relation_type="implements",
            target="FR-001",
            annotation="test",
        )
        self.assertTrue(added)
        relations = list_relations(spec_path)
        self.assertEqual(len(relations), 1)
        relation = relations[0]
        self.assertEqual(relation.type, "implements")
        self.assertEqual(relation.target, "FR-001")
        self.assertEqual(relation.attributes.get("annotation"), "test")

    def test_add_relation_avoids_duplicates(self) -> None:
        spec_path = self._make_spec()
        add_relation(spec_path, relation_type="implements", target="FR-001")
        added = add_relation(spec_path, relation_type="implements", target="FR-001")
        self.assertFalse(added)
        relations = list_relations(spec_path)
        self.assertEqual(len(relations), 1)

    def test_remove_relation(self) -> None:
        spec_path = self._make_spec()
        add_relation(spec_path, relation_type="implements", target="FR-001")
        removed = remove_relation(
            spec_path, relation_type="implements", target="FR-001",
        )
        self.assertTrue(removed)
        self.assertEqual(list_relations(spec_path), [])

    def test_remove_missing_relation_returns_false(self) -> None:
        spec_path = self._make_spec()
        removed = remove_relation(
            spec_path, relation_type="implements", target="FR-999",
        )
        self.assertFalse(removed)


if __name__ == "__main__":
    unittest.main()
