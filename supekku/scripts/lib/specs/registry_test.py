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


class TestSpecRegistryReverseQueries(RepoTestCase):
  """Test reverse relationship query methods for SpecRegistry."""

  def _make_repo(self) -> Path:
    root = super()._make_repo()
    os.chdir(root)
    return root

  def _write_spec_with_adrs(self, root: Path, spec_id: str, adr_ids: list[str]) -> None:
    """Write a spec that references specific ADRs."""
    kind = "tech" if spec_id.startswith("SPEC-") else "product"
    spec_dir = root / "specify" / kind / f"{spec_id.lower()}-sample"
    spec_dir.mkdir(parents=True, exist_ok=True)
    spec_path = spec_dir / f"{spec_id}.md"

    # Create frontmatter with informed_by field
    frontmatter = {
      "id": spec_id,
      "slug": spec_id.lower(),
      "name": f"Spec {spec_id}",
      "created": "2024-06-01",
      "updated": "2024-06-01",
      "status": "draft",
      "kind": "spec" if kind == "tech" else "prod",
      "informed_by": adr_ids,
    }
    dump_markdown_file(spec_path, frontmatter, f"# {spec_id}\n")

  def test_find_by_informed_by_single_adr(self) -> None:
    """Test finding specs informed by a specific ADR."""
    root = self._make_repo()
    self._write_spec_with_adrs(root, "SPEC-001", ["ADR-001"])
    self._write_spec_with_adrs(root, "SPEC-002", ["ADR-002"])

    registry = SpecRegistry(root)

    specs = registry.find_by_informed_by("ADR-001")

    assert isinstance(specs, list)
    assert len(specs) == 1
    assert specs[0].id == "SPEC-001"

  def test_find_by_informed_by_multiple_specs_same_adr(self) -> None:
    """Test finding multiple specs informed by same ADR."""
    root = self._make_repo()
    self._write_spec_with_adrs(root, "SPEC-001", ["ADR-010"])
    self._write_spec_with_adrs(root, "SPEC-002", ["ADR-010", "ADR-011"])
    self._write_spec_with_adrs(root, "PROD-001", ["ADR-010"])

    registry = SpecRegistry(root)

    specs = registry.find_by_informed_by("ADR-010")

    assert isinstance(specs, list)
    assert len(specs) == 3
    spec_ids = {s.id for s in specs}
    assert "SPEC-001" in spec_ids
    assert "SPEC-002" in spec_ids
    assert "PROD-001" in spec_ids

  def test_find_by_informed_by_nonexistent_adr(self) -> None:
    """Test finding specs for non-existent ADR returns empty list."""
    root = self._make_repo()
    self._write_spec_with_adrs(root, "SPEC-001", ["ADR-001"])

    registry = SpecRegistry(root)

    specs = registry.find_by_informed_by("ADR-999")

    assert isinstance(specs, list)
    assert len(specs) == 0

  def test_find_by_informed_by_none(self) -> None:
    """Test find_by_informed_by with None returns empty list."""
    root = self._make_repo()

    registry = SpecRegistry(root)

    specs = registry.find_by_informed_by(None)

    assert isinstance(specs, list)
    assert len(specs) == 0

  def test_find_by_informed_by_empty_string(self) -> None:
    """Test find_by_informed_by with empty string returns empty list."""
    root = self._make_repo()

    registry = SpecRegistry(root)

    specs = registry.find_by_informed_by("")

    assert isinstance(specs, list)
    assert len(specs) == 0

  def test_find_by_informed_by_returns_spec_objects(self) -> None:
    """Test that find_by_informed_by returns proper Spec objects."""
    root = self._make_repo()
    self._write_spec_with_adrs(root, "SPEC-001", ["ADR-001"])

    registry = SpecRegistry(root)

    specs = registry.find_by_informed_by("ADR-001")

    assert len(specs) == 1
    spec = specs[0]

    # Verify it's a Spec with expected attributes
    assert isinstance(spec, Spec)
    assert spec.id == "SPEC-001"
    assert hasattr(spec, "slug")
    assert hasattr(spec, "kind")
    assert "ADR-001" in spec.informed_by

  def test_find_by_informed_by_case_sensitive(self) -> None:
    """Test that ADR ID matching is case-sensitive."""
    root = self._make_repo()
    self._write_spec_with_adrs(root, "SPEC-001", ["ADR-001"])

    registry = SpecRegistry(root)

    # Correct case
    specs_upper = registry.find_by_informed_by("ADR-001")
    # Wrong case
    specs_lower = registry.find_by_informed_by("adr-001")

    assert len(specs_upper) == 1
    assert len(specs_lower) == 0

  def test_find_by_informed_by_spec_without_informed_by_field(self) -> None:
    """Test that specs without informed_by field are not returned."""
    root = self._make_repo()

    # Create spec WITHOUT informed_by field
    spec_dir = root / "specify" / "tech" / "spec-003-sample"
    spec_dir.mkdir(parents=True, exist_ok=True)
    spec_path = spec_dir / "SPEC-003.md"
    frontmatter = {
      "id": "SPEC-003",
      "slug": "spec-003",
      "name": "Spec 003",
      "created": "2024-06-01",
      "updated": "2024-06-01",
      "status": "draft",
      "kind": "spec",
    }
    dump_markdown_file(spec_path, frontmatter, "# SPEC-003\n")

    registry = SpecRegistry(root)

    specs = registry.find_by_informed_by("ADR-001")

    assert isinstance(specs, list)
    assert len(specs) == 0

  def test_find_by_informed_by_works_with_prod_specs(self) -> None:
    """Test finding PROD specs by ADR."""
    root = self._make_repo()
    self._write_spec_with_adrs(root, "PROD-005", ["ADR-020"])

    registry = SpecRegistry(root)

    specs = registry.find_by_informed_by("ADR-020")

    assert isinstance(specs, list)
    assert len(specs) == 1
    assert specs[0].id == "PROD-005"
    assert specs[0].kind == "prod"


if __name__ == "__main__":
  unittest.main()
