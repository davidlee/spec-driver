"""Tests for spec_registry module."""

from __future__ import annotations

import os
import unittest
from typing import TYPE_CHECKING

from supekku.scripts.lib.core.spec_utils import dump_markdown_file
from supekku.scripts.lib.specs.models import Spec
from supekku.scripts.lib.specs.package_utils import find_package_for_file
from supekku.scripts.lib.specs.registry import SpecRegistry
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
    """Test that registry correctly loads both tech and product specs."""
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
    """Test finding specs by package name."""
    root = self._make_repo()
    registry = SpecRegistry(root)

    matches = registry.find_by_package("internal/sample")
    assert [spec.id for spec in matches] == ["SPEC-001"]

  def test_reload_refreshes_registry(self) -> None:
    """Test that reloading the registry picks up newly added specs."""
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

  def test_file_to_package_resolution(self) -> None:
    """VT-004: Test file-to-package resolution for spec queries.

    Verifies that files in a package resolve to the correct package-level
    spec, supporting --for-path queries at various depths.
    """
    root = self._make_repo()

    # Create leaf package structure (no child packages)
    # Files at various depths within the same package
    pkg_root = root / "internal" / "sample"
    pkg_root.mkdir(parents=True, exist_ok=True)
    (pkg_root / "__init__.py").write_text("# Package init\n")
    (pkg_root / "module.py").write_text("def foo(): pass\n")

    # Create subdirectories without __init__.py (not packages, just dirs)
    nested = pkg_root / "sub"
    nested.mkdir(exist_ok=True)
    (nested / "nested_module.py").write_text("def bar(): pass\n")

    deep = nested / "deep"
    deep.mkdir(exist_ok=True)
    (deep / "deep_module.py").write_text("def baz(): pass\n")

    # Initialize registry with package-level spec
    registry = SpecRegistry(root)

    # Test 1: Package root __init__.py resolves to package
    file1 = pkg_root / "__init__.py"
    package1 = find_package_for_file(file1)
    assert package1 is not None, f"Failed to find package for {file1}"
    rel_pkg1 = str(package1.relative_to(root))
    specs1 = registry.find_by_package(rel_pkg1)
    assert len(specs1) == 1, f"Expected 1 spec for package, got {len(specs1)}"
    assert specs1[0].id == "SPEC-001"

    # Test 2: Module in package root resolves to same package
    file2 = pkg_root / "module.py"
    package2 = find_package_for_file(file2)
    assert package2 is not None
    rel_pkg2 = str(package2.relative_to(root))
    specs2 = registry.find_by_package(rel_pkg2)
    assert len(specs2) == 1
    assert specs2[0].id == "SPEC-001"

    # Test 3: Nested module resolves to same package (leaf package)
    file3 = nested / "nested_module.py"
    package3 = find_package_for_file(file3)
    assert package3 is not None
    rel_pkg3 = str(package3.relative_to(root))
    specs3 = registry.find_by_package(rel_pkg3)
    assert len(specs3) == 1
    assert specs3[0].id == "SPEC-001"

    # Test 4: Deeply nested module resolves to same package
    file4 = deep / "deep_module.py"
    package4 = find_package_for_file(file4)
    assert package4 is not None
    rel_pkg4 = str(package4.relative_to(root))
    specs4 = registry.find_by_package(rel_pkg4)
    assert len(specs4) == 1
    assert specs4[0].id == "SPEC-001"

    # Test 5: All files in same package resolve to same spec
    packages = [rel_pkg1, rel_pkg2, rel_pkg3, rel_pkg4]
    assert len(set(packages)) == 1, "All files should resolve to same package"

    # Test 6: Non-existent file handling
    nonexistent = root / "does_not_exist.py"
    package_none = find_package_for_file(nonexistent)
    assert package_none is None, "Non-existent file should return None"


if __name__ == "__main__":
  unittest.main()
