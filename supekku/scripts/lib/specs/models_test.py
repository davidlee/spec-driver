"""Tests for Spec model taxonomy properties (VT-030-001)."""

from __future__ import annotations

import os

from supekku.scripts.lib.core.paths import SPECS_DIR, TECH_SPECS_SUBDIR
from supekku.scripts.lib.core.spec_utils import dump_markdown_file
from supekku.scripts.lib.specs.registry import SpecRegistry
from supekku.scripts.lib.test_base import RepoTestCase


class SpecTaxonomyTest(RepoTestCase):
  """VT-030-001: Spec model exposes category and c4_level from frontmatter."""

  def _make_repo_with_specs(self):
    root = self._make_repo()
    tech_dir = root / SPECS_DIR / TECH_SPECS_SUBDIR

    # Unit spec with taxonomy fields
    unit_dir = tech_dir / "SPEC-001"
    unit_dir.mkdir(parents=True)
    dump_markdown_file(
      unit_dir / "SPEC-001.md",
      {
        "id": "SPEC-001",
        "slug": "unit-example",
        "name": "Unit Example",
        "kind": "spec",
        "status": "draft",
        "created": "2026-01-01",
        "updated": "2026-01-01",
        "category": "unit",
        "c4_level": "code",
      },
      "# SPEC-001\n",
    )

    # Assembly spec with taxonomy fields
    asm_dir = tech_dir / "SPEC-002"
    asm_dir.mkdir(parents=True)
    dump_markdown_file(
      asm_dir / "SPEC-002.md",
      {
        "id": "SPEC-002",
        "slug": "assembly-example",
        "name": "Assembly Example",
        "kind": "spec",
        "status": "draft",
        "created": "2026-01-01",
        "updated": "2026-01-01",
        "category": "assembly",
        "c4_level": "component",
      },
      "# SPEC-002\n",
    )

    # Spec without taxonomy fields (unknown)
    bare_dir = tech_dir / "SPEC-003"
    bare_dir.mkdir(parents=True)
    dump_markdown_file(
      bare_dir / "SPEC-003.md",
      {
        "id": "SPEC-003",
        "slug": "bare-example",
        "name": "Bare Example",
        "kind": "spec",
        "status": "draft",
        "created": "2026-01-01",
        "updated": "2026-01-01",
      },
      "# SPEC-003\n",
    )

    os.chdir(root)
    return root

  def test_category_property(self):
    root = self._make_repo_with_specs()
    registry = SpecRegistry(root)

    assert registry.get("SPEC-001").category == "unit"
    assert registry.get("SPEC-002").category == "assembly"

  def test_c4_level_property(self):
    root = self._make_repo_with_specs()
    registry = SpecRegistry(root)

    assert registry.get("SPEC-001").c4_level == "code"
    assert registry.get("SPEC-002").c4_level == "component"

  def test_missing_taxonomy_returns_empty_string(self):
    root = self._make_repo_with_specs()
    registry = SpecRegistry(root)
    bare = registry.get("SPEC-003")

    assert bare.category == ""
    assert bare.c4_level == ""

  def test_to_dict_includes_taxonomy_when_present(self):
    root = self._make_repo_with_specs()
    registry = SpecRegistry(root)

    unit_dict = registry.get("SPEC-001").to_dict(root)
    assert unit_dict["category"] == "unit"
    assert unit_dict["c4_level"] == "code"

    asm_dict = registry.get("SPEC-002").to_dict(root)
    assert asm_dict["category"] == "assembly"
    assert asm_dict["c4_level"] == "component"

  def test_to_dict_omits_taxonomy_when_absent(self):
    root = self._make_repo_with_specs()
    registry = SpecRegistry(root)

    bare_dict = registry.get("SPEC-003").to_dict(root)
    assert "category" not in bare_dict
    assert "c4_level" not in bare_dict
