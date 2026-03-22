"""Tests for Spec model taxonomy properties (VT-030-001)."""

from __future__ import annotations

import os

from supekku.scripts.lib.core.paths import SPEC_DRIVER_DIR, TECH_SPECS_SUBDIR
from supekku.scripts.lib.core.spec_utils import dump_markdown_file
from supekku.scripts.lib.specs.registry import SpecRegistry
from supekku.scripts.lib.test_base import RepoTestCase


class SpecTaxonomyTest(RepoTestCase):
  """VT-030-001: Spec model exposes category and c4_level from frontmatter."""

  def _make_repo_with_specs(self):
    root = self._make_repo()
    tech_dir = root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR

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

    spec1 = registry.get("SPEC-001")
    spec2 = registry.get("SPEC-002")
    assert spec1 is not None
    assert spec2 is not None
    assert spec1.category == "unit"
    assert spec2.category == "assembly"

  def test_c4_level_property(self):
    root = self._make_repo_with_specs()
    registry = SpecRegistry(root)

    spec1 = registry.get("SPEC-001")
    spec2 = registry.get("SPEC-002")
    assert spec1 is not None
    assert spec2 is not None
    assert spec1.c4_level == "code"
    assert spec2.c4_level == "component"

  def test_missing_taxonomy_returns_empty_string(self):
    root = self._make_repo_with_specs()
    registry = SpecRegistry(root)
    bare = registry.get("SPEC-003")
    assert bare is not None

    assert bare.category == ""
    assert bare.c4_level == ""

  def test_to_dict_includes_taxonomy_when_present(self):
    root = self._make_repo_with_specs()
    registry = SpecRegistry(root)

    spec1 = registry.get("SPEC-001")
    spec2 = registry.get("SPEC-002")
    assert spec1 is not None
    assert spec2 is not None
    unit_dict = spec1.to_dict(root)
    assert unit_dict["category"] == "unit"
    assert unit_dict["c4_level"] == "code"

    asm_dict = spec2.to_dict(root)
    assert asm_dict["category"] == "assembly"
    assert asm_dict["c4_level"] == "component"

  def test_to_dict_omits_taxonomy_when_absent(self):
    root = self._make_repo_with_specs()
    registry = SpecRegistry(root)

    spec3 = registry.get("SPEC-003")
    assert spec3 is not None
    bare_dict = spec3.to_dict(root)
    assert "category" not in bare_dict
    assert "c4_level" not in bare_dict


class SpecExternalRefTest(RepoTestCase):
  """VT-067-001: Spec model exposes ext_id and ext_url from frontmatter."""

  def _make_repo_with_external_spec(self):
    root = self._make_repo()
    tech_dir = root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR

    ext_dir = tech_dir / "SPEC-010"
    ext_dir.mkdir(parents=True)
    dump_markdown_file(
      ext_dir / "SPEC-010.md",
      {
        "id": "SPEC-010",
        "slug": "external-ref",
        "name": "External Ref",
        "kind": "spec",
        "status": "draft",
        "created": "2026-01-01",
        "updated": "2026-01-01",
        "ext_id": "JIRA-1234",
        "ext_url": "https://jira.example.com/browse/JIRA-1234",
      },
      "# SPEC-010\n",
    )

    bare_dir = tech_dir / "SPEC-011"
    bare_dir.mkdir(parents=True)
    dump_markdown_file(
      bare_dir / "SPEC-011.md",
      {
        "id": "SPEC-011",
        "slug": "no-external",
        "name": "No External",
        "kind": "spec",
        "status": "draft",
        "created": "2026-01-01",
        "updated": "2026-01-01",
      },
      "# SPEC-011\n",
    )

    os.chdir(root)
    return root

  def test_ext_id_property(self):
    root = self._make_repo_with_external_spec()
    registry = SpecRegistry(root)
    spec = registry.get("SPEC-010")
    assert spec is not None
    assert spec.ext_id == "JIRA-1234"

  def test_ext_url_property(self):
    root = self._make_repo_with_external_spec()
    registry = SpecRegistry(root)
    spec = registry.get("SPEC-010")
    assert spec is not None
    assert spec.ext_url == "https://jira.example.com/browse/JIRA-1234"

  def test_missing_ext_fields_return_empty_string(self):
    root = self._make_repo_with_external_spec()
    registry = SpecRegistry(root)
    bare = registry.get("SPEC-011")
    assert bare is not None
    assert bare.ext_id == ""
    assert bare.ext_url == ""

  def test_to_dict_includes_ext_fields_when_present(self):
    root = self._make_repo_with_external_spec()
    registry = SpecRegistry(root)
    spec = registry.get("SPEC-010")
    assert spec is not None
    data = spec.to_dict(root)
    assert data["ext_id"] == "JIRA-1234"
    assert data["ext_url"] == "https://jira.example.com/browse/JIRA-1234"

  def test_to_dict_omits_ext_fields_when_absent(self):
    root = self._make_repo_with_external_spec()
    registry = SpecRegistry(root)
    spec = registry.get("SPEC-011")
    assert spec is not None
    data = spec.to_dict(root)
    assert "ext_id" not in data
    assert "ext_url" not in data


class SpecRelationsTest(RepoTestCase):
  """VT-085-006: Spec model exposes .relations property from frontmatter."""

  def _make_repo_with_relations_spec(self):
    root = self._make_repo()
    tech_dir = root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR

    # Spec with relations
    rel_dir = tech_dir / "SPEC-020"
    rel_dir.mkdir(parents=True)
    dump_markdown_file(
      rel_dir / "SPEC-020.md",
      {
        "id": "SPEC-020",
        "slug": "with-relations",
        "name": "With Relations",
        "kind": "spec",
        "status": "draft",
        "created": "2026-01-01",
        "updated": "2026-01-01",
        "relations": [
          {"type": "implements", "target": "PROD-010"},
          {"type": "depends_on", "target": "SPEC-100", "annotation": "core dep"},
        ],
      },
      "# SPEC-020\n",
    )

    # Spec without relations
    bare_dir = tech_dir / "SPEC-021"
    bare_dir.mkdir(parents=True)
    dump_markdown_file(
      bare_dir / "SPEC-021.md",
      {
        "id": "SPEC-021",
        "slug": "no-relations",
        "name": "No Relations",
        "kind": "spec",
        "status": "draft",
        "created": "2026-01-01",
        "updated": "2026-01-01",
      },
      "# SPEC-021\n",
    )

    os.chdir(root)
    return root

  def test_relations_present(self):
    root = self._make_repo_with_relations_spec()
    registry = SpecRegistry(root)
    spec = registry.find("SPEC-020")
    assert spec is not None
    rels = spec.relations
    assert len(rels) == 2
    assert rels[0]["type"] == "implements"
    assert rels[0]["target"] == "PROD-010"
    assert rels[1]["type"] == "depends_on"
    assert rels[1]["target"] == "SPEC-100"

  def test_relations_absent_returns_empty(self):
    root = self._make_repo_with_relations_spec()
    registry = SpecRegistry(root)
    spec = registry.find("SPEC-021")
    assert spec is not None
    assert spec.relations == []

  def test_relations_are_dicts(self):
    root = self._make_repo_with_relations_spec()
    registry = SpecRegistry(root)
    spec = registry.find("SPEC-020")
    assert spec is not None
    for rel in spec.relations:
      assert isinstance(rel, dict)
      assert "type" in rel
      assert "target" in rel

  def test_to_dict_includes_relations_when_present(self):
    root = self._make_repo_with_relations_spec()
    registry = SpecRegistry(root)
    spec020 = registry.find("SPEC-020")
    assert spec020 is not None
    data = spec020.to_dict(root)
    assert "relations" in data
    assert len(data["relations"]) == 2
    assert data["relations"][0] == {"type": "implements", "target": "PROD-010"}
    assert data["relations"][1]["type"] == "depends_on"
    assert data["relations"][1]["target"] == "SPEC-100"

  def test_to_dict_omits_relations_when_absent(self):
    root = self._make_repo_with_relations_spec()
    registry = SpecRegistry(root)
    spec021 = registry.find("SPEC-021")
    assert spec021 is not None
    data = spec021.to_dict(root)
    assert "relations" not in data
