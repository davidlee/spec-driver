"""Tests for change_artifacts module."""

from __future__ import annotations

from typing import TYPE_CHECKING

from supekku.scripts.lib.changes.artifacts import load_change_artifact
from supekku.scripts.lib.core.spec_utils import dump_markdown_file

if TYPE_CHECKING:
  from pathlib import Path


def _write_delta(tmp_path: Path, body: str) -> Path:
  path = tmp_path / "DE-010.md"
  frontmatter = {
    "id": "DE-010",
    "slug": "example",
    "name": "Delta – Example",
    "created": "2024-01-01",
    "updated": "2024-01-01",
    "status": "draft",
    "kind": "delta",
    "relations": [],
    "applies_to": {},
  }
  dump_markdown_file(path, frontmatter, body)
  return path


def test_loads_frontmatter_when_no_structured_block(tmp_path: Path) -> None:
  """Test loading change artifact with only frontmatter and no structured block."""
  path = _write_delta(tmp_path, "# DE-010\n")
  artifact = load_change_artifact(path)
  assert artifact
  assert artifact.id == "DE-010"
  assert not artifact.applies_to
  assert not artifact.relations


def test_structured_delta_updates_applies_and_relations(tmp_path: Path) -> None:
  """Test that structured delta blocks update applies_to and relations metadata."""
  body = """```yaml supekku:delta.relationships@v1
schema: supekku.delta.relationships
version: 1
delta: DE-010
revision_links:
  introduces:
    - RE-123
  supersedes: []
specs:
  primary:
    - SPEC-147
  collaborators:
    - SPEC-002
requirements:
  implements:
    - SPEC-147.FR-001
  updates:
    - SPEC-147.FR-005
  verifies: []
phases:
  - id: IP-010.PHASE-01
    goal: deliver core capability
    status: pending
```

# DE-010
"""
  path = _write_delta(tmp_path, body)
  artifact = load_change_artifact(path)
  assert artifact
  assert artifact.applies_to == {
    "specs": ["SPEC-147"],
    "requirements": ["SPEC-147.FR-001", "SPEC-147.FR-005"],
  }
  assert {r["type"] for r in artifact.relations} == {"introduces"}
  introduces = [r for r in artifact.relations if r["type"] == "introduces"]
  assert introduces
  assert introduces[0]["target"] == "RE-123"


def test_plan_and_phase_overview_included(tmp_path: Path) -> None:
  """Test that plan and phase overviews are included in change artifact."""
  delta_dir = tmp_path / "DE-020"
  delta_dir.mkdir()
  delta_body = (
    "```yaml supekku:delta.relationships@v1\n"
    "schema: supekku.delta.relationships\n"
    "version: 1\n"
    "delta: DE-020\n"
    "revision_links:\n  introduces: []\n  supersedes: []\n"
    "specs:\n  primary:\n    - SPEC-500\n  collaborators: []\n"
    "requirements:\n  implements:\n    - SPEC-500.FR-001\n"
    "  updates: []\n  verifies: []\n"
    "phases: []\n"
    "```\n\n# DE-020\n"
  )
  dump_markdown_file(
    delta_dir / "DE-020.md",
    {
      "id": "DE-020",
      "slug": "example",
      "name": "Delta – Example",
      "created": "2024-01-01",
      "updated": "2024-01-01",
      "status": "draft",
      "kind": "delta",
      "relations": [],
      "applies_to": {},
    },
    delta_body,
  )

  plan_body = (
    "```yaml supekku:plan.overview@v1\n"
    "schema: supekku.plan.overview\n"
    "version: 1\n"
    "plan: IP-020\n"
    "delta: DE-020\n"
    "revision_links:\n  aligns_with: []\n"
    "specs:\n  primary:\n    - SPEC-500\n  collaborators: []\n"
    "requirements:\n  targets:\n    - SPEC-500.FR-001\n"
    "  dependencies: []\n"
    "phases:\n  - id: IP-020.PHASE-01\n    name: Phase 01\n"
    "    objective: >-\n      Initial delivery.\n"
    "    entrance_criteria: []\n    exit_criteria: []\n"
    "```\n"
    "\n# IP-020 – Example Plan\n"
  )
  dump_markdown_file(
    delta_dir / "IP-020.md",
    {
      "id": "IP-020",
      "slug": "example-plan",
      "name": "Implementation Plan – Example",
      "created": "2024-01-01",
      "updated": "2024-01-01",
      "status": "draft",
      "kind": "plan",
    },
    plan_body,
  )

  phases_dir = delta_dir / "phases"
  phases_dir.mkdir()
  phase_body = (
    "```yaml supekku:phase.overview@v1\n"
    "schema: supekku.phase.overview\n"
    "version: 1\n"
    "phase: IP-020.PHASE-01\n"
    "plan: IP-020\n"
    "delta: DE-020\n"
    "objective: >-\n  Deliver MVP.\n"
    "entrance_criteria: []\n"
    "exit_criteria: []\n"
    "verification:\n  tests: []\n  evidence: []\n"
    "tasks: []\n"
    "risks: []\n"
    "```\n\n# Phase 01\n"
  )
  dump_markdown_file(
    phases_dir / "phase-01.md",
    {
      "id": "IP-020.PHASE-01",
      "slug": "phase-01",
      "name": "Phase 01",
      "created": "2024-01-01",
      "updated": "2024-01-01",
      "status": "draft",
      "kind": "phase",
    },
    phase_body,
  )

  artifact = load_change_artifact(delta_dir / "DE-020.md")
  assert artifact
  assert artifact.plan is not None
  assert artifact.plan["id"] == "IP-020"
  assert len(artifact.plan["phases"]) == 1
  assert artifact.plan["phases"][0].get("phase") == "IP-020.PHASE-01"
