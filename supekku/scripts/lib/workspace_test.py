"""Tests for workspace module."""

from __future__ import annotations

import os
import unittest
from pathlib import Path

from supekku.scripts.lib.spec_utils import dump_markdown_file
from supekku.scripts.lib.test_base import RepoTestCase
from supekku.scripts.lib.workspace import Workspace


class WorkspaceTest(RepoTestCase):
    """Test cases for workspace functionality."""

    def _create_repo(self) -> Path:
        root = super()._make_repo()
        os.chdir(root)
        return root

    def _write_spec(self, root: Path) -> None:
        spec_dir = root / "specify" / "tech" / "SPEC-200-sample"
        spec_dir.mkdir(parents=True)
        spec_path = spec_dir / "SPEC-200.md"
        frontmatter = {
            "id": "SPEC-200",
            "slug": "sample",
            "name": "Sample Spec",
            "created": "2024-06-01",
            "updated": "2024-06-01",
            "status": "draft",
            "kind": "spec",
        }
        dump_markdown_file(
            spec_path, frontmatter, "# Spec\n- FR-200: Sample requirement\n",
        )

    def test_workspace_loads_specs_and_syncs_requirements(self) -> None:
        root = self._create_repo()
        self._write_spec(root)

        ws = Workspace(root)
        spec = ws.specs.get("SPEC-200")
        self.assertIsNotNone(spec)

        ws.sync_requirements()
        registry = ws.requirements
        self.assertIn("SPEC-200.FR-200", registry.records)

    def test_sync_change_registries(self) -> None:
        root = self._create_repo()
        change_dir = root / "change" / "deltas" / "DE-200-sample"
        change_dir.mkdir(parents=True)
        delta_path = change_dir / "DE-200.md"
        frontmatter = {
            "id": "DE-200",
            "slug": "delta",
            "name": "Delta",
            "created": "2024-06-01",
            "updated": "2024-06-01",
            "status": "draft",
            "kind": "delta",
            "relations": [],
        }
        dump_markdown_file(delta_path, frontmatter, "# Delta\n")

        ws = Workspace(root)
        ws.sync_change_registries(kinds=["delta"])
        output = root / "supekku" / "registry" / "deltas.yaml"
        self.assertTrue(output.exists())

    def test_workspace_decisions_property(self) -> None:
        """Test that workspace.decisions property returns DecisionRegistry."""
        root = self._create_repo()
        ws = Workspace(root)

        # Access decisions property
        decisions = ws.decisions
        self.assertIsNotNone(decisions)
        # Verify it's the correct type
        from supekku.scripts.lib.decision_registry import DecisionRegistry

        self.assertIsInstance(decisions, DecisionRegistry)
        # Verify it's cached (same instance on multiple access)
        self.assertIs(decisions, ws.decisions)

    def test_workspace_decisions_collect_and_access(self) -> None:
        """Test accessing ADRs through workspace.decisions."""
        root = self._create_repo()

        # Create ADR directory and file
        decisions_dir = root / "specify" / "decisions"
        decisions_dir.mkdir(parents=True)
        adr_file = decisions_dir / "ADR-001-test-decision.md"
        adr_content = """---
id: ADR-001
title: "Test Decision"
status: accepted
created: 2024-01-01
authors:
  - name: "Test Author"
    contact: "test@example.com"
---

# ADR-001: Test Decision

## Context
Test context.

## Decision
We decided to test.
"""
        adr_file.write_text(adr_content, encoding="utf-8")

        ws = Workspace(root)
        decisions_dict = ws.decisions.collect()

        # Verify ADR was collected
        self.assertIn("ADR-001", decisions_dict)
        decision = decisions_dict["ADR-001"]
        self.assertEqual(decision.title, "Test Decision")
        self.assertEqual(decision.status, "accepted")

    def test_workspace_sync_decisions(self) -> None:
        """Test workspace.sync_decisions creates registry and symlinks."""
        root = self._create_repo()

        # Create ADR directory and files
        decisions_dir = root / "specify" / "decisions"
        decisions_dir.mkdir(parents=True)

        # Create ADRs with different statuses
        adr1 = decisions_dir / "ADR-001-accepted.md"
        adr1.write_text(
            """---
id: ADR-001
title: "Accepted Decision"
status: accepted
---
# Test""",
            encoding="utf-8",
        )

        adr2 = decisions_dir / "ADR-002-draft.md"
        adr2.write_text(
            """---
id: ADR-002
title: "Draft Decision"
status: draft
---
# Test""",
            encoding="utf-8",
        )

        # Create registry directory
        registry_dir = root / "supekku" / "registry"
        registry_dir.mkdir(parents=True)

        ws = Workspace(root)
        ws.sync_decisions()

        # Verify YAML registry was created
        yaml_path = registry_dir / "decisions.yaml"
        self.assertTrue(yaml_path.exists())

        # Verify content of YAML
        import yaml

        with yaml_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        self.assertIn("decisions", data)
        self.assertIn("ADR-001", data["decisions"])
        self.assertIn("ADR-002", data["decisions"])

        # Verify symlinks were created
        accepted_dir = decisions_dir / "accepted"
        draft_dir = decisions_dir / "draft"
        self.assertTrue(accepted_dir.exists())
        self.assertTrue(draft_dir.exists())

        # Verify symlink files
        accepted_link = accepted_dir / "ADR-001-accepted.md"
        draft_link = draft_dir / "ADR-002-draft.md"
        self.assertTrue(accepted_link.exists() and accepted_link.is_symlink())
        self.assertTrue(draft_link.exists() and draft_link.is_symlink())

        # Verify symlinks point to correct files
        self.assertEqual(accepted_link.resolve(), adr1.resolve())
        self.assertEqual(draft_link.resolve(), adr2.resolve())

    def test_workspace_decisions_integration_with_existing_data(self) -> None:
        """Test decisions integration when data already exists."""
        root = self._create_repo()

        # Pre-create directories and existing symlinks
        decisions_dir = root / "specify" / "decisions"
        decisions_dir.mkdir(parents=True)
        accepted_dir = decisions_dir / "accepted"
        accepted_dir.mkdir(parents=True)

        # Create an old/stale symlink
        old_link = accepted_dir / "old-decision.md"
        old_link.symlink_to("../nonexistent.md")

        # Create actual ADR
        adr = decisions_dir / "ADR-001-new.md"
        adr.write_text(
            """---
id: ADR-001
title: "New Decision"
status: accepted
---
# Test""",
            encoding="utf-8",
        )

        ws = Workspace(root)
        ws.sync_decisions()

        # Verify old symlink was removed
        self.assertFalse(old_link.exists())

        # Verify new symlink was created
        new_link = accepted_dir / "ADR-001-new.md"
        self.assertTrue(new_link.exists() and new_link.is_symlink())


if __name__ == "__main__":
    unittest.main()
