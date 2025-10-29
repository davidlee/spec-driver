"""Tests for change_registry module."""

from __future__ import annotations

import os
import unittest
from pathlib import Path

from supekku.scripts.lib.test_base import RepoTestCase

from supekku.scripts.lib.change_registry import ChangeRegistry
from supekku.scripts.lib.spec_utils import dump_markdown_file
from supekku.scripts.lib.relations import add_relation


class ChangeRegistryTest(RepoTestCase):
    """Test cases for ChangeRegistry functionality."""

    def _create_repo(self) -> Path:
        root = super()._make_repo()
        os.chdir(root)
        return root

    def _write_change(
        self,
        root: Path,
        kind: str,
        artifact_id: str,
        relations: list[tuple[str, str]] | None = None,
    ) -> None:
        bundle_dir = root / "change" / kind / f"{artifact_id}-sample"
        bundle_dir.mkdir(parents=True, exist_ok=True)
        path = bundle_dir / f"{artifact_id}.md"
        frontmatter = {
            "id": artifact_id,
            "slug": artifact_id.lower(),
            "name": artifact_id,
            "created": "2024-06-01",
            "updated": "2024-06-02",
            "status": "draft",
            "kind": kind[:-1] if kind.endswith("s") else kind,
            "relations": [],
            "applies_to": {"requirements": ["SPEC-010.FR-001"]},
        }
        dump_markdown_file(path, frontmatter, f"# {artifact_id}\n")
        if relations:
            for relation_type, target in relations:
                add_relation(path, relation_type=relation_type, target=target)

    def test_collect_and_sync_delta_registry(self) -> None:
        root = self._create_repo()
        self._write_change(
            root, "deltas", "DE-101", [("implements", "SPEC-010.FR-001")]
        )

        registry = ChangeRegistry(root=root, kind="delta")
        artifacts = registry.collect()
        self.assertIn("DE-101", artifacts)
        artifact = artifacts["DE-101"]
        self.assertEqual(artifact.relations[0]["target"], "SPEC-010.FR-001")

        registry.sync()
        output = (root / "supekku" / "registry" / "deltas.yaml").read_text()
        self.assertIn("DE-101", output)
        self.assertIn("SPEC-010.FR-001", output)


if __name__ == "__main__":
    unittest.main()
