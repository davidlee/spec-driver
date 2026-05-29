"""Tests for revision change summary (DE-142 P03 — list revisions enrichment)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from supekku.scripts.lib.blocks.revision import render_revision_change_block
from supekku.scripts.lib.changes.artifacts import ChangeArtifact
from supekku.scripts.lib.changes.revision_check import (
  RevisionChangeSummary,
  revision_change_summary,
)
from supekku.scripts.lib.core.spec_utils import dump_markdown_file_update

if TYPE_CHECKING:
  from pathlib import Path

_EM_DASH = "–"


def _artifact(path: Path) -> ChangeArtifact:
  return ChangeArtifact(
    id="RE-099",
    kind="revision",
    status="draft",
    name="Spec Revision - Example",
    slug="re-099",
    path=path,
    updated="2026-01-01",
  )


def _write_revision(
  tmp_path: Path,
  *,
  specs: list[dict] | None = None,
  requirements: list[dict] | None = None,
  body: str | None = None,
) -> Path:
  if body is None:
    body = "# RE-099\n\n" + render_revision_change_block(
      "RE-099", specs=specs or [], requirements=requirements or []
    )
  path = tmp_path / "RE-099.md"
  dump_markdown_file_update(
    path,
    {
      "id": "RE-099",
      "slug": "re-099",
      "name": "Spec Revision - Example",
      "created": "2026-01-01",
      "updated": "2026-01-01",
      "status": "draft",
      "kind": "revision",
      "relations": [],
    },
    body,
  )
  return path


# -- VT-142-LIST-002 — breakdown from block --


def test_summary_breakdown_from_block(tmp_path: Path) -> None:
  path = _write_revision(
    tmp_path,
    specs=[{"spec_id": "PROD-004", "action": "updated"}],
    requirements=[
      {
        "requirement_id": "PROD-004.FR-007",
        "action": "move",
        "origin": [{"kind": "spec", "ref": "SPEC-100"}],
        "destination": {"spec": "PROD-004"},
      },
    ],
  )
  summary = revision_change_summary(_artifact(path))
  assert summary.sources == ["SPEC-100"]
  assert summary.destinations == ["PROD-004"]
  assert summary.requirements == ["PROD-004.FR-007"]


def test_summary_dedupes_and_sorts_across_requirements(tmp_path: Path) -> None:
  path = _write_revision(
    tmp_path,
    requirements=[
      {
        "requirement_id": "PROD-004.FR-007",
        "action": "move",
        "origin": [
          {"kind": "spec", "ref": "SPEC-200"},
          {"kind": "spec", "ref": "SPEC-100"},
        ],
        "destination": {"spec": "PROD-004"},
      },
      {
        "requirement_id": "PROD-004.FR-007",
        "action": "modify",
        "destination": {"spec": "PROD-004"},
      },
    ],
  )
  summary = revision_change_summary(_artifact(path))
  assert summary.sources == ["SPEC-100", "SPEC-200"]
  assert summary.destinations == ["PROD-004"]
  assert summary.requirements == ["PROD-004.FR-007"]


def test_summary_excludes_non_spec_origin(tmp_path: Path) -> None:
  path = _write_revision(
    tmp_path,
    requirements=[
      {
        "requirement_id": "SPEC-100.FR-001",
        "action": "move",
        "origin": [{"kind": "backlog", "ref": "ISSUE-1"}],
        "destination": {"spec": "SPEC-100"},
      },
    ],
  )
  summary = revision_change_summary(_artifact(path))
  assert not summary.sources
  assert summary.destinations == ["SPEC-100"]
  assert summary.requirements == ["SPEC-100.FR-001"]


# -- VT-142-LIST-003 — em-dash for empty --


def test_no_block_yields_empty_summary(tmp_path: Path) -> None:
  path = _write_revision(tmp_path, body="# RE-099\n\nNo block here.\n")
  summary = revision_change_summary(_artifact(path))
  assert (summary.sources, summary.destinations, summary.requirements) == ([], [], [])


def test_empty_summary_cells_are_em_dash() -> None:
  summary = RevisionChangeSummary(sources=[], destinations=[], requirements=[])
  assert summary.source_cell() == _EM_DASH
  assert summary.destination_cell() == _EM_DASH
  assert summary.requirements_cell() == _EM_DASH


def test_populated_cells_count_and_first() -> None:
  summary = RevisionChangeSummary(
    sources=["SPEC-100", "SPEC-200"],
    destinations=["PROD-004"],
    requirements=["PROD-004.FR-007", "PROD-004.FR-008"],
  )
  assert summary.source_cell() == "2 (SPEC-100)"
  assert summary.destination_cell() == "1 (PROD-004)"
  assert summary.requirements_cell() == "2"
