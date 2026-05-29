"""Tests for change_artifacts module."""

from __future__ import annotations

from typing import TYPE_CHECKING

import yaml

from supekku.scripts.lib.blocks.delta import DeltaRelationshipsBlock
from supekku.scripts.lib.blocks.revision import (
  REVISION_BLOCK_MARKER,
  RevisionChangeBlock,
  render_revision_change_block,
)
from supekku.scripts.lib.changes.artifacts import (
  _derive_applies_to,
  _derive_revision_applies_to,
  _derive_revision_link_relations,
  load_change_artifact,
)
from supekku.scripts.lib.core.spec_utils import dump_markdown_file_update

if TYPE_CHECKING:
  from pathlib import Path


def _block(data: dict) -> DeltaRelationshipsBlock:
  return DeltaRelationshipsBlock(raw_yaml="", data=data)


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
  dump_markdown_file_update(path, frontmatter, body)
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
  # DE-138 / DEC-138-11: applies_to unions specs.primary ∪ specs.collaborators.
  assert artifact.applies_to == {
    "specs": ["SPEC-002", "SPEC-147"],
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
  dump_markdown_file_update(
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
  dump_markdown_file_update(
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
  dump_markdown_file_update(
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


def test_phase_loaded_from_frontmatter_when_canonical_fields_present(
  tmp_path: Path,
) -> None:
  """DR-106: Phase data read from frontmatter when plan+delta present."""
  delta_dir = tmp_path / "DE-040"
  delta_dir.mkdir()
  dump_markdown_file_update(
    delta_dir / "DE-040.md",
    {
      "id": "DE-040",
      "slug": "fm-phase",
      "name": "Delta – FM Phase",
      "created": "2024-01-01",
      "updated": "2024-01-01",
      "status": "draft",
      "kind": "delta",
      "relations": [],
      "applies_to": {},
    },
    "# DE-040\n",
  )

  plan_body = (
    "```yaml supekku:plan.overview@v1\n"
    "schema: supekku.plan.overview\n"
    "version: 1\n"
    "plan: IP-040\n"
    "delta: DE-040\n"
    "phases:\n  - id: IP-040.PHASE-01\n"
    "```\n\n# IP-040\n"
  )
  dump_markdown_file_update(
    delta_dir / "IP-040.md",
    {
      "id": "IP-040",
      "slug": "plan",
      "name": "Plan",
      "created": "2024-01-01",
      "updated": "2024-01-01",
      "status": "draft",
      "kind": "plan",
    },
    plan_body,
  )

  phases_dir = delta_dir / "phases"
  phases_dir.mkdir()
  # New-format phase: canonical fields in frontmatter, no phase.overview block
  dump_markdown_file_update(
    phases_dir / "phase-01.md",
    {
      "id": "IP-040.PHASE-01",
      "slug": "phase-01",
      "name": "Phase 01",
      "created": "2024-01-01",
      "updated": "2024-01-01",
      "status": "in-progress",
      "kind": "phase",
      "plan": "IP-040",
      "delta": "DE-040",
      "objective": "Test frontmatter-first loading",
      "entrance_criteria": ["DR approved"],
      "exit_criteria": ["Tests pass"],
    },
    "# Phase 01\n\nNo overview block here.\n",
  )

  artifact = load_change_artifact(delta_dir / "DE-040.md")
  assert artifact
  assert artifact.plan is not None
  phases = artifact.plan["phases"]
  assert len(phases) == 1
  phase = phases[0]
  assert phase["phase"] == "IP-040.PHASE-01"
  assert phase["plan"] == "IP-040"
  assert phase["delta"] == "DE-040"
  assert phase["objective"] == "Test frontmatter-first loading"
  assert phase["status"] == "in-progress"
  assert phase["entrance_criteria"] == ["DR approved"]
  assert phase["exit_criteria"] == ["Tests pass"]


def test_phase_falls_back_to_block_when_no_canonical_frontmatter(
  tmp_path: Path,
) -> None:
  """DR-106: Legacy phases without plan/delta in frontmatter use block fallback."""
  delta_dir = tmp_path / "DE-041"
  delta_dir.mkdir()
  dump_markdown_file_update(
    delta_dir / "DE-041.md",
    {
      "id": "DE-041",
      "slug": "legacy-phase",
      "name": "Delta – Legacy Phase",
      "created": "2024-01-01",
      "updated": "2024-01-01",
      "status": "draft",
      "kind": "delta",
      "relations": [],
      "applies_to": {},
    },
    "# DE-041\n",
  )

  plan_body = (
    "```yaml supekku:plan.overview@v1\n"
    "schema: supekku.plan.overview\n"
    "version: 1\n"
    "plan: IP-041\n"
    "delta: DE-041\n"
    "phases:\n  - id: IP-041.PHASE-01\n"
    "```\n\n# IP-041\n"
  )
  dump_markdown_file_update(
    delta_dir / "IP-041.md",
    {
      "id": "IP-041",
      "slug": "plan",
      "name": "Plan",
      "created": "2024-01-01",
      "updated": "2024-01-01",
      "status": "draft",
      "kind": "plan",
    },
    plan_body,
  )

  phases_dir = delta_dir / "phases"
  phases_dir.mkdir()
  # Legacy-format phase: no plan/delta in frontmatter, has phase.overview block
  phase_body = (
    "```yaml supekku:phase.overview@v1\n"
    "schema: supekku.phase.overview\n"
    "version: 1\n"
    "phase: IP-041.PHASE-01\n"
    "plan: IP-041\n"
    "delta: DE-041\n"
    "objective: >-\n  Legacy block objective.\n"
    "entrance_criteria: []\n"
    "exit_criteria: []\n"
    "verification:\n  tests: []\n  evidence: []\n"
    "tasks: []\n"
    "risks: []\n"
    "```\n\n# Phase 01\n"
  )
  dump_markdown_file_update(
    phases_dir / "phase-01.md",
    {
      "id": "IP-041.PHASE-01",
      "slug": "phase-01",
      "name": "Phase 01",
      "created": "2024-01-01",
      "updated": "2024-01-01",
      "status": "draft",
      "kind": "phase",
    },
    phase_body,
  )

  artifact = load_change_artifact(delta_dir / "DE-041.md")
  assert artifact
  assert artifact.plan is not None
  phases = artifact.plan["phases"]
  assert len(phases) == 1
  phase = phases[0]
  assert phase["phase"] == "IP-041.PHASE-01"
  assert phase["plan"] == "IP-041"
  assert phase["objective"] == "Legacy block objective."


def test_ext_id_and_ext_url_loaded_from_frontmatter(tmp_path: Path) -> None:
  """VT-067-001: ext_id and ext_url are loaded from frontmatter."""
  path = tmp_path / "DE-030.md"
  dump_markdown_file_update(
    path,
    {
      "id": "DE-030",
      "slug": "ext-ref",
      "name": "Delta – External Ref",
      "created": "2024-01-01",
      "updated": "2024-01-01",
      "status": "draft",
      "kind": "delta",
      "ext_id": "GH-567",
      "ext_url": "https://github.com/org/repo/issues/567",
    },
    "# DE-030\n",
  )
  artifact = load_change_artifact(path)
  assert artifact
  assert artifact.ext_id == "GH-567"
  assert artifact.ext_url == "https://github.com/org/repo/issues/567"


def test_ext_fields_default_to_empty_string(tmp_path: Path) -> None:
  """VT-067-001: ext_id and ext_url default to empty string when absent."""
  path = _write_delta(tmp_path, "# DE-010\n")
  artifact = load_change_artifact(path)
  assert artifact
  assert artifact.ext_id == ""
  assert artifact.ext_url == ""


def test_to_dict_includes_ext_fields_when_present(tmp_path: Path) -> None:
  """VT-067-001: to_dict includes ext_id/ext_url when populated."""
  path = tmp_path / "DE-031.md"
  dump_markdown_file_update(
    path,
    {
      "id": "DE-031",
      "slug": "ext-dict",
      "name": "Delta – Dict",
      "created": "2024-01-01",
      "updated": "2024-01-01",
      "status": "draft",
      "kind": "delta",
      "ext_id": "LIN-42",
      "ext_url": "https://linear.app/team/LIN-42",
    },
    "# DE-031\n",
  )
  artifact = load_change_artifact(path)
  assert artifact
  data = artifact.to_dict(tmp_path)
  assert data["ext_id"] == "LIN-42"
  assert data["ext_url"] == "https://linear.app/team/LIN-42"


def test_to_dict_omits_ext_fields_when_absent(tmp_path: Path) -> None:
  """VT-067-001: to_dict omits ext_id/ext_url when empty."""
  path = _write_delta(tmp_path, "# DE-010\n")
  artifact = load_change_artifact(path)
  assert artifact
  data = artifact.to_dict(tmp_path)
  assert "ext_id" not in data
  assert "ext_url" not in data


# -- VT-DE138-DERIVE-001 — _derive_applies_to matrix (DR-138 §6.1, DEC-138-10) --


def test_derive_applies_to_block_sole_source_when_block_present() -> None:
  """Block present → block is sole source (FM silently shadowed even when populated)."""
  block = _block(
    {
      "specs": {"primary": ["SPEC-100"]},
      "requirements": {"implements": ["SPEC-100.FR-001"]},
    }
  )
  fm = {"applies_to": {"specs": ["FM-ONLY-SPEC"], "requirements": ["FM-ONLY-REQ"]}}
  result = _derive_applies_to(block, fm)
  assert result == {"specs": ["SPEC-100"], "requirements": ["SPEC-100.FR-001"]}


def test_derive_applies_to_falls_back_to_fm_when_block_absent() -> None:
  """Block absent → FM-fallback (transition-window for unmigrated artefacts)."""
  fm = {"applies_to": {"specs": ["SPEC-200"], "requirements": ["SPEC-200.FR-001"]}}
  result = _derive_applies_to(None, fm)
  assert result == {"specs": ["SPEC-200"], "requirements": ["SPEC-200.FR-001"]}


def test_derive_applies_to_returns_empty_when_both_absent() -> None:
  """Both block and FM absent → empty dict."""
  assert not _derive_applies_to(None, {})


def test_derive_applies_to_empty_block_falls_through_to_fm() -> None:
  """Block with no specs/reqs → FM-fallback (block payload treated as absent)."""
  block = _block({})
  fm = {"applies_to": {"specs": ["SPEC-300"]}}
  result = _derive_applies_to(block, fm)
  assert result == {"specs": ["SPEC-300"]}


def test_derive_applies_to_fm_non_dict_returns_empty() -> None:
  """FM applies_to that is not a dict → empty (guards against bad payloads)."""
  assert not _derive_applies_to(None, {"applies_to": "not-a-dict"})


# -- VT-DE138-COLLAB-001 — union primary + collaborators (DR-138 §6.1, DEC-138-11) --


def test_derive_applies_to_unions_primary_and_collaborators() -> None:
  """Block with primary + collaborators → applies_to.specs is the sorted union."""
  block = _block(
    {
      "specs": {
        "primary": ["SPEC-100"],
        "collaborators": ["SPEC-200", "SPEC-300"],
      },
    }
  )
  result = _derive_applies_to(block, {})
  assert result == {
    "specs": ["SPEC-100", "SPEC-200", "SPEC-300"],
    "requirements": [],
  }


def test_derive_applies_to_collaborator_only_spec_appears() -> None:
  """Collaborator-only spec (no primary) still surfaces in applies_to."""
  block = _block({"specs": {"primary": [], "collaborators": ["SPEC-COL"]}})
  result = _derive_applies_to(block, {})
  assert result == {"specs": ["SPEC-COL"], "requirements": []}


def test_derive_applies_to_unions_all_requirement_relations() -> None:
  """All of requirements.{implements,updates,verifies} union into applies_to.requirements."""  # noqa: E501
  block = _block(
    {
      "requirements": {
        "implements": ["SPEC-100.FR-001"],
        "updates": ["SPEC-100.FR-002"],
        "verifies": ["SPEC-100.NFR-PERF"],
      }
    }
  )
  result = _derive_applies_to(block, {})
  assert result == {
    "specs": [],
    "requirements": [
      "SPEC-100.FR-001",
      "SPEC-100.FR-002",
      "SPEC-100.NFR-PERF",
    ],
  }


# -- VT-DE138-RELLINK-001 — revision_links projection (DR-138 §6.1, F-138-16) --


def test_derive_revision_link_relations_projects_introduces() -> None:
  block = _block({"revision_links": {"introduces": ["RE-100", "RE-101"]}})
  rels = _derive_revision_link_relations(block)
  assert {"type": "introduces", "target": "RE-100"} in rels
  assert {"type": "introduces", "target": "RE-101"} in rels


def test_derive_revision_link_relations_projects_supersedes() -> None:
  block = _block({"revision_links": {"supersedes": ["RE-200"]}})
  rels = _derive_revision_link_relations(block)
  assert rels == [{"type": "supersedes", "target": "RE-200"}]


def test_derive_revision_link_relations_empty_when_block_absent() -> None:
  assert not _derive_revision_link_relations(None)


def test_derive_revision_link_relations_empty_when_no_revision_links() -> None:
  block = _block({})
  assert not _derive_revision_link_relations(block)


def test_derive_revision_link_relations_preserves_both_kinds() -> None:
  """ADR-002 backlinks observed — projection comes from authored block content only."""
  block = _block(
    {
      "revision_links": {
        "introduces": ["RE-100"],
        "supersedes": ["RE-090"],
      }
    }
  )
  rels = _derive_revision_link_relations(block)
  assert {(r["type"], r["target"]) for r in rels} == {
    ("introduces", "RE-100"),
    ("supersedes", "RE-090"),
  }


# -- VT-142-DERIVE-001 — _derive_revision_applies_to (DR-142 §6, DEC-142-05) --
# Narrow (DEC-CONSULT-02, user-approved): specs ← block.specs[].spec_id,
# requirements ← block.requirements[].requirement_id; sorted+deduped union over
# all blocks. Block-first (FM shadowed); FM-fallback only when no block. The
# source/destination split the list columns need (P03) is recomputed there, not
# folded into derived scope. RevisionChangeBlock is parse-on-demand.


def _rev_block(data: dict) -> RevisionChangeBlock:
  return RevisionChangeBlock(
    marker=REVISION_BLOCK_MARKER,
    language="yaml",
    info=REVISION_BLOCK_MARKER,
    yaml_content=yaml.safe_dump(data),
    content_start=0,
    content_end=0,
  )


def test_derive_revision_applies_to_block_sole_source() -> None:
  """Block present → block is sole source (FM scope keys shadowed)."""
  block = _rev_block(
    {
      "specs": [{"spec_id": "PROD-004", "action": "updated"}],
      "requirements": [{"requirement_id": "PROD-004.FR-007", "action": "modify"}],
    }
  )
  fm = {"applies_to": {"specs": ["FM-ONLY"], "requirements": ["FM-ONLY.FR-1"]}}
  result = _derive_revision_applies_to([block], fm)
  assert result == {"specs": ["PROD-004"], "requirements": ["PROD-004.FR-007"]}


def test_derive_revision_applies_to_sorted_and_deduped() -> None:
  """Duplicate + out-of-order ids collapse to a sorted unique set."""
  block = _rev_block(
    {
      "specs": [
        {"spec_id": "SPEC-200"},
        {"spec_id": "PROD-004"},
        {"spec_id": "PROD-004"},
      ],
      "requirements": [
        {"requirement_id": "PROD-004.FR-007"},
        {"requirement_id": "PROD-004.FR-007"},
      ],
    }
  )
  result = _derive_revision_applies_to([block], {})
  assert result == {
    "specs": ["PROD-004", "SPEC-200"],
    "requirements": ["PROD-004.FR-007"],
  }


def test_derive_revision_applies_to_unions_multiple_blocks() -> None:
  """Multiple blocks → union (extract_revision_blocks returns a list)."""
  block_a = _rev_block({"specs": [{"spec_id": "PROD-004"}]})
  block_b = _rev_block(
    {
      "specs": [{"spec_id": "SPEC-122"}],
      "requirements": [{"requirement_id": "SPEC-122.FR-003"}],
    }
  )
  result = _derive_revision_applies_to([block_a, block_b], {})
  assert result == {
    "specs": ["PROD-004", "SPEC-122"],
    "requirements": ["SPEC-122.FR-003"],
  }


def test_derive_revision_applies_to_falls_back_to_fm_when_no_block() -> None:
  """No block → FM-fallback (transition window for unmigrated revisions)."""
  fm = {"applies_to": {"specs": ["PROD-004"], "requirements": ["PROD-004.FR-007"]}}
  result = _derive_revision_applies_to([], fm)
  assert result == {"specs": ["PROD-004"], "requirements": ["PROD-004.FR-007"]}


def test_derive_revision_applies_to_empty_blocks_fall_through_to_fm() -> None:
  """Blocks with no specs/reqs → treated as absent → FM-fallback."""
  block = _rev_block({"specs": [], "requirements": []})
  fm = {"applies_to": {"specs": ["PROD-004"]}}
  assert _derive_revision_applies_to([block], fm) == {"specs": ["PROD-004"]}


def test_derive_revision_applies_to_returns_empty_when_both_absent() -> None:
  """No blocks + no FM applies_to → empty derived scope."""
  assert not _derive_revision_applies_to([], {})


def test_derive_revision_applies_to_fm_non_dict_returns_empty() -> None:
  """Non-dict FM applies_to → empty (guards against bad payloads)."""
  assert not _derive_revision_applies_to([], {"applies_to": "not-a-dict"})


def test_load_revision_derives_applies_to_from_block(tmp_path: Path) -> None:
  """Integration: kind=='revision' hook derives applies_to from the block,
  shadowing legacy hand-rolled FM scope keys (VT-142-DERIVE-001 integration leg)."""
  body = "# RE-050\n\n" + render_revision_change_block(
    "RE-050",
    specs=[{"spec_id": "PROD-004", "action": "updated"}],
    requirements=[
      {"requirement_id": "PROD-004.FR-007", "action": "modify"},
    ],
  )
  path = tmp_path / "RE-050.md"
  frontmatter = {
    "id": "RE-050",
    "slug": "example-revision",
    "name": "Revision – Example",
    "created": "2026-01-01",
    "updated": "2026-01-01",
    "status": "draft",
    "kind": "revision",
    "relations": [],
    # Legacy hand-rolled scope keys — must be shadowed by the derived block.
    "source_specs": ["FM-ONLY"],
    "destination_specs": ["FM-ONLY"],
    "requirements": ["FM-ONLY.FR-1"],
  }
  dump_markdown_file_update(path, frontmatter, body)
  artifact = load_change_artifact(path)
  assert artifact
  assert artifact.applies_to == {
    "specs": ["PROD-004"],
    "requirements": ["PROD-004.FR-007"],
  }
