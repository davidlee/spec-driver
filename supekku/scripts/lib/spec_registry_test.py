"""Tests for spec_registry module."""

from __future__ import annotations

import os
import unittest
from typing import TYPE_CHECKING

from supekku.scripts.lib.spec_models import Spec
from supekku.scripts.lib.spec_registry import SpecRegistry
from supekku.scripts.lib.spec_utils import dump_markdown_file
from supekku.scripts.lib.test_base import RepoTestCase

if TYPE_CHECKING:
  from pathlib import Path


class SpecRegistryTest(RepoTestCase):
  """Test cases for spec_registry functionality."""

  def _make_repo(self) -> Path:
    root = super()._make_repo()

    tech_dir = root / "specify" / "tech" / "SPEC-001-sample"
    tech_dir.mkdir(parents=True)
    tech_spec = tech_dir / "SPEC-001.md"
    tech_frontmatter = {
      "id": "SPEC-001",
      "slug": "sample-tech",
      "name": "Sample Tech Spec",
      "created": "2024-06-01",
      "updated": "2024-06-01",
      "status": "draft",
      "kind": "spec",
      "packages": ["internal/sample"],
    }
    dump_markdown_file(tech_spec, tech_frontmatter, "# Sample Tech\n")

    product_dir = root / "specify" / "product"
    product_dir.mkdir(parents=True, exist_ok=True)
    product_spec = product_dir / "PROD-001.md"
    product_frontmatter = {
      "id": "PROD-001",
      "slug": "sample-product",
      "name": "Sample Product Spec",
      "created": "2024-06-01",
      "updated": "2024-06-01",
      "status": "draft",
      "kind": "prod",
    }
    dump_markdown_file(product_spec, product_frontmatter, "# Sample Product\n")

    os.chdir(root)
    return root

  def test_registry_loads_specs(self) -> None:
    root = self._make_repo()
    registry = SpecRegistry(root)

    spec = registry.get("SPEC-001")
    assert isinstance(spec, Spec)
    assert spec.slug == "sample-tech"
    assert spec.packages == ["internal/sample"]

    prod = registry.get("PROD-001")
    assert prod is not None
    assert prod.kind == "prod"

  def test_find_by_package(self) -> None:
    root = self._make_repo()
    registry = SpecRegistry(root)

    matches = registry.find_by_package("internal/sample")
    assert [spec.id for spec in matches] == ["SPEC-001"]

  def test_reload_refreshes_registry(self) -> None:
    root = self._make_repo()
    registry = SpecRegistry(root)

    new_dir = root / "specify" / "tech" / "SPEC-002-extra"
    new_dir.mkdir(parents=True)
    new_spec = new_dir / "SPEC-002.md"
    frontmatter = {
      "id": "SPEC-002",
      "slug": "extra",
      "name": "Extra Spec",
      "created": "2024-06-02",
      "updated": "2024-06-02",
      "status": "draft",
      "kind": "spec",
    }
    dump_markdown_file(new_spec, frontmatter, "# Extra\n")

    registry.reload()
    assert registry.get("SPEC-002") is not None


if __name__ == "__main__":
  unittest.main()
