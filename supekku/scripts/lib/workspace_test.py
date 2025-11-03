"""Tests for workspace module."""

from __future__ import annotations

import os
import unittest
from typing import TYPE_CHECKING

import yaml

from supekku.scripts.lib.core.paths import get_registry_dir
from supekku.scripts.lib.core.spec_utils import dump_markdown_file
from supekku.scripts.lib.decisions.registry import DecisionRegistry
from supekku.scripts.lib.test_base import RepoTestCase
from supekku.scripts.lib.workspace import Workspace

if TYPE_CHECKING:
  from pathlib import Path


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
      spec_path,
      frontmatter,
      "# Spec\n- FR-200: Sample requirement\n",
    )

  def test_workspace_loads_specs_and_syncs_requirements(self) -> None:
    """Test that workspace loads specs and syncs requirements correctly."""
    root = self._create_repo()
    self._write_spec(root)

    ws = Workspace(root)
    spec = ws.specs.get("SPEC-200")
    assert spec is not None

    ws.sync_requirements()
    registry = ws.requirements
    assert "SPEC-200.FR-200" in registry.records

  def test_sync_change_registries(self) -> None:
    """Test syncing change registries collects delta, revision, audit."""
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
    output = get_registry_dir(root) / "deltas.yaml"
    assert output.exists()

  def test_workspace_decisions_property(self) -> None:
    """Test that workspace.decisions property returns DecisionRegistry."""
    root = self._create_repo()
    ws = Workspace(root)

    # Access decisions property
    decisions = ws.decisions
    assert decisions is not None
    # Verify it's the correct type
    assert isinstance(decisions, DecisionRegistry)
    # Verify it's cached (same instance on multiple access)
    assert decisions is ws.decisions

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
    assert "ADR-001" in decisions_dict
    decision = decisions_dict["ADR-001"]
    assert decision.title == "Test Decision"
    assert decision.status == "accepted"

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
    registry_dir = get_registry_dir(root)
    registry_dir.mkdir(parents=True)

    ws = Workspace(root)
    ws.sync_decisions()

    # Verify YAML registry was created
    yaml_path = registry_dir / "decisions.yaml"
    assert yaml_path.exists()

    # Verify content of YAML
    with yaml_path.open("r", encoding="utf-8") as f:
      data = yaml.safe_load(f)
    assert "decisions" in data
    assert "ADR-001" in data["decisions"]
    assert "ADR-002" in data["decisions"]

    # Verify symlinks were created
    accepted_dir = decisions_dir / "accepted"
    draft_dir = decisions_dir / "draft"
    assert accepted_dir.exists()
    assert draft_dir.exists()

    # Verify symlink files
    accepted_link = accepted_dir / "ADR-001-accepted.md"
    draft_link = draft_dir / "ADR-002-draft.md"
    assert accepted_link.exists()
    assert accepted_link.is_symlink()
    assert draft_link.exists()
    assert draft_link.is_symlink()

    # Verify symlinks point to correct files
    assert accepted_link.resolve() == adr1.resolve()
    assert draft_link.resolve() == adr2.resolve()

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
    assert not old_link.exists()

    # Verify new symlink was created
    new_link = accepted_dir / "ADR-001-new.md"
    assert new_link.exists()
    assert new_link.is_symlink()


  def test_workspace_sync_all_registries(self) -> None:
    """Test that sync_all_registries syncs all registries in correct order."""
    root = self._create_repo()
    self._write_spec(root)

    # Create ADR at root of decisions directory
    decisions_dir = root / "specify" / "decisions"
    decisions_dir.mkdir(parents=True)
    adr_path = decisions_dir / "ADR-099-test.md"
    adr_path.write_text(
      """---
id: ADR-099
title: Test Decision
status: accepted
---
# Test""",
      encoding="utf-8",
    )

    # Create delta
    delta_dir = root / "change" / "deltas" / "DE-099-test"
    delta_dir.mkdir(parents=True)
    delta_path = delta_dir / "DE-099.md"
    delta_path.write_text(
      """---
id: DE-099
slug: test
name: Test Delta
status: draft
kind: delta
applies_to:
  specs: []
  requirements: []
---
# Test""",
      encoding="utf-8",
    )

    # Create registry directory
    registry_dir = get_registry_dir(root)
    registry_dir.mkdir(parents=True)

    ws = Workspace(root)

    # Sync all registries
    ws.sync_all_registries()

    # Verify specs were loaded
    assert len(ws.specs.all_specs()) > 0
    assert ws.specs.get("SPEC-200") is not None

    # Verify decisions were synced (registry created)
    yaml_path = registry_dir / "decisions.yaml"
    assert yaml_path.exists()

    # Verify change registries were synced
    delta_registry = ws.delta_registry.collect()
    assert "DE-099" in delta_registry

    # Verify requirements were synced from specs
    req_uid = "SPEC-200.FR-200"
    assert req_uid in ws.requirements.records


if __name__ == "__main__":
  unittest.main()
