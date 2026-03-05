"""Tests for discover_plans() plan discovery function."""

from __future__ import annotations

import os
import unittest
from typing import TYPE_CHECKING

from supekku.scripts.lib.changes.registry import discover_plans
from supekku.scripts.lib.core.paths import CHANGES_DIR, DELTAS_SUBDIR
from supekku.scripts.lib.core.spec_utils import dump_markdown_file
from supekku.scripts.lib.test_base import RepoTestCase

if TYPE_CHECKING:
  from pathlib import Path


def _plan_overview_block(
  plan_id: str,
  delta_id: str,
  phases: list[dict[str, str]] | None = None,
) -> str:
  """Render a plan overview YAML block for test fixtures."""
  lines = [
    "```yaml supekku:plan.overview@v1",
    "schema: supekku.plan.overview",
    "version: 1",
    f"plan: {plan_id}",
    f"delta: {delta_id}",
  ]
  if phases:
    lines.append("phases:")
    for phase in phases:
      lines.append(f"  - id: {phase['id']}")
      lines.append(f"    name: {phase['name']}")
      lines.append(f"    status: {phase['status']}")
  lines.append("```")
  return "\n".join(lines)


def _write_plan(
  root: Path,
  delta_id: str,
  plan_id: str,
  *,
  status: str = "draft",
  name: str | None = None,
  phases: list[dict[str, str]] | None = None,
) -> Path:
  """Write a plan file inside a delta directory."""
  delta_dir = root / CHANGES_DIR / DELTAS_SUBDIR / f"{delta_id}-sample"
  delta_dir.mkdir(parents=True, exist_ok=True)
  path = delta_dir / f"{plan_id}.md"
  frontmatter = {
    "id": plan_id,
    "slug": f"{delta_id.lower()}_test",
    "name": name or f"Implementation Plan - {plan_id}",
    "created": "2026-03-01",
    "updated": "2026-03-02",
    "status": status,
    "kind": "plan",
  }
  body = _plan_overview_block(plan_id, delta_id, phases)
  dump_markdown_file(path, frontmatter, body)
  return path


class TestDiscoverPlans(RepoTestCase):
  """Tests for discover_plans()."""

  def _create_repo(self) -> Path:
    root = super()._make_repo()
    os.chdir(root)
    return root

  def test_empty_repo_returns_empty_list(self) -> None:
    root = self._create_repo()
    result = discover_plans(root)
    assert result == []

  def test_no_deltas_dir_returns_empty_list(self) -> None:
    root = self._create_repo()
    (root / CHANGES_DIR).mkdir(parents=True)
    result = discover_plans(root)
    assert result == []

  def test_discovers_single_plan(self) -> None:
    root = self._create_repo()
    _write_plan(root, "DE-100", "IP-100")

    result = discover_plans(root)

    assert len(result) == 1
    plan = result[0]
    assert plan.id == "IP-100"
    assert plan.status == "draft"
    assert plan.name == "Implementation Plan - IP-100"
    assert plan.delta_id == "DE-100"

  def test_discovers_multiple_plans(self) -> None:
    root = self._create_repo()
    _write_plan(root, "DE-100", "IP-100")
    _write_plan(root, "DE-101", "IP-101", status="complete")

    result = discover_plans(root)

    assert len(result) == 2
    ids = {p.id for p in result}
    assert ids == {"IP-100", "IP-101"}

  def test_returns_sorted_by_id(self) -> None:
    root = self._create_repo()
    _write_plan(root, "DE-102", "IP-102")
    _write_plan(root, "DE-100", "IP-100")
    _write_plan(root, "DE-101", "IP-101")

    result = discover_plans(root)

    assert [p.id for p in result] == ["IP-100", "IP-101", "IP-102"]

  def test_plan_summary_fields(self) -> None:
    root = self._create_repo()
    phases = [
      {"id": "IP-100.PHASE-01", "name": "Phase 1", "status": "complete"},
      {"id": "IP-100.PHASE-02", "name": "Phase 2", "status": "pending"},
    ]
    path = _write_plan(
      root,
      "DE-100",
      "IP-100",
      name="My Plan",
      status="in-progress",
      phases=phases,
    )

    result = discover_plans(root)

    assert len(result) == 1
    plan = result[0]
    assert plan.id == "IP-100"
    assert plan.status == "in-progress"
    assert plan.name == "My Plan"
    assert plan.slug == "de-100_test"
    assert plan.path == path
    assert plan.updated == "2026-03-02"
    assert plan.delta_id == "DE-100"
    assert len(plan.phases) == 2
    assert plan.phases[0]["id"] == "IP-100.PHASE-01"
    assert plan.phases[1]["status"] == "pending"

  def test_plan_without_overview_block(self) -> None:
    """Plans without a plan.overview block get empty delta_id and phases."""
    root = self._create_repo()
    delta_dir = root / CHANGES_DIR / DELTAS_SUBDIR / "DE-100-sample"
    delta_dir.mkdir(parents=True, exist_ok=True)
    path = delta_dir / "IP-100.md"
    frontmatter = {
      "id": "IP-100",
      "slug": "test",
      "name": "Bare Plan",
      "created": "2026-03-01",
      "updated": "2026-03-01",
      "status": "draft",
      "kind": "plan",
    }
    dump_markdown_file(path, frontmatter, "# No overview block\n")

    result = discover_plans(root)

    assert len(result) == 1
    assert result[0].delta_id == ""
    assert result[0].phases == []

  def test_skips_non_plan_files(self) -> None:
    """Only IP-*.md files are discovered, not DE-*.md or DR-*.md."""
    root = self._create_repo()
    delta_dir = root / CHANGES_DIR / DELTAS_SUBDIR / "DE-100-sample"
    delta_dir.mkdir(parents=True, exist_ok=True)
    frontmatter = {
      "id": "DE-100",
      "slug": "x",
      "name": "Delta",
      "created": "2026-03-01",
      "updated": "2026-03-01",
      "status": "draft",
      "kind": "delta",
    }
    dump_markdown_file(delta_dir / "DE-100.md", frontmatter, "# Delta\n")
    _write_plan(root, "DE-100", "IP-100")

    result = discover_plans(root)

    assert len(result) == 1
    assert result[0].id == "IP-100"

  def test_skips_malformed_frontmatter(self) -> None:
    """Plans with unparseable frontmatter are silently skipped."""
    root = self._create_repo()
    delta_dir = root / CHANGES_DIR / DELTAS_SUBDIR / "DE-100-sample"
    delta_dir.mkdir(parents=True, exist_ok=True)
    (delta_dir / "IP-100.md").write_text("not valid frontmatter\n")
    _write_plan(root, "DE-101", "IP-101")

    result = discover_plans(root)

    assert len(result) == 1
    assert result[0].id == "IP-101"

  def test_plan_summary_is_frozen(self) -> None:
    root = self._create_repo()
    _write_plan(root, "DE-100", "IP-100")

    result = discover_plans(root)
    plan = result[0]

    with self.assertRaises(AttributeError):
      plan.id = "IP-999"  # type: ignore[misc]


if __name__ == "__main__":
  unittest.main()
