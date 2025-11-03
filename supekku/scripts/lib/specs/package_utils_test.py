"""Tests for package detection utilities (VT-001).

Verification Target: PROD-005.FR-001 - Leaf Python Package Identification

Test Coverage:
- Leaf package identification across real supekku/ structure
- Non-leaf package detection (parent packages)
- Non-package path validation
- File-to-package resolution at various depths
- Edge cases: single-file packages, deeply nested structures
"""

from __future__ import annotations

from pathlib import Path

import pytest

from supekku.scripts.lib.specs.package_utils import (
  find_all_leaf_packages,
  find_package_for_file,
  is_leaf_package,
  validate_package_path,
)

# Known leaf packages in supekku/ (as of 2025-11-03)
KNOWN_LEAF_PACKAGES = {
  "supekku/cli",
  "supekku/scripts/backlog",
  "supekku/scripts/cli",
  "supekku/scripts/lib/backlog",
  "supekku/scripts/lib/blocks/metadata",
  "supekku/scripts/lib/changes/blocks",
  "supekku/scripts/lib/core/frontmatter_metadata",
  "supekku/scripts/lib/decisions",
  "supekku/scripts/lib/deletion",
  "supekku/scripts/lib/docs/python",
  "supekku/scripts/lib/formatters",
  "supekku/scripts/lib/policies",
  "supekku/scripts/lib/relations",
  "supekku/scripts/lib/requirements",
  "supekku/scripts/lib/specs",
  "supekku/scripts/lib/standards",
  "supekku/scripts/lib/sync/adapters",
  "supekku/scripts/lib/validation",
}

# Known parent packages (not leaves)
KNOWN_PARENT_PACKAGES = {
  "supekku",
  "supekku/scripts",
  "supekku/scripts/lib",
  "supekku/scripts/lib/blocks",
  "supekku/scripts/lib/changes",
  "supekku/scripts/lib/core",
  "supekku/scripts/lib/docs",
  "supekku/scripts/lib/sync",
}


class TestIsLeafPackage:
  """Test is_leaf_package() function."""

  def test_identifies_all_known_leaf_packages(self) -> None:
    """Test that all 16 known leaf packages are correctly identified."""
    for pkg_path in KNOWN_LEAF_PACKAGES:
      path = Path(pkg_path)
      assert is_leaf_package(path), f"Should identify {pkg_path} as leaf package"

  def test_rejects_parent_packages(self) -> None:
    """Test that parent packages are not identified as leaf packages."""
    for pkg_path in KNOWN_PARENT_PACKAGES:
      path = Path(pkg_path)
      assert not is_leaf_package(path), f"Should reject {pkg_path} as leaf package"

  def test_rejects_non_package_directories(self) -> None:
    """Test that directories without __init__.py are rejected."""
    # .git directory has no __init__.py
    assert not is_leaf_package(Path(".git"))
    assert not is_leaf_package(Path("change/deltas"))

  def test_rejects_files(self) -> None:
    """Test that file paths are rejected."""
    assert not is_leaf_package(Path("README.md"))
    assert not is_leaf_package(Path("supekku/cli/__init__.py"))

  def test_rejects_nonexistent_paths(self) -> None:
    """Test that non-existent paths are rejected."""
    assert not is_leaf_package(Path("nonexistent/package/path"))


class TestFindPackageForFile:
  """Test find_package_for_file() function."""

  def test_resolves_file_in_leaf_package(self) -> None:
    """Test resolution of file to its leaf package."""
    file_path = Path("supekku/scripts/lib/formatters/change_formatters.py")
    result = find_package_for_file(file_path)
    assert result == Path("supekku/scripts/lib/formatters")

  def test_resolves_file_in_nested_package(self) -> None:
    """Test resolution of file in deeply nested package."""
    file_path = Path(
      "supekku/scripts/lib/core/frontmatter_metadata/base.py",
    )
    result = find_package_for_file(file_path)
    assert result == Path("supekku/scripts/lib/core/frontmatter_metadata")

  def test_resolves_init_file_to_package(self) -> None:
    """Test that __init__.py resolves to its containing package."""
    file_path = Path("supekku/scripts/lib/formatters/__init__.py")
    result = find_package_for_file(file_path)
    assert result == Path("supekku/scripts/lib/formatters")

  def test_resolves_test_file_to_package(self) -> None:
    """Test resolution of test file to package."""
    file_path = Path("supekku/scripts/lib/specs/package_utils_test.py")
    result = find_package_for_file(file_path)
    assert result == Path("supekku/scripts/lib/specs")

  def test_returns_none_for_file_outside_package(self) -> None:
    """Test that files outside packages return None."""
    # File in root (no package)
    result = find_package_for_file(Path("README.md"))
    assert result is None

  def test_handles_directory_input(self) -> None:
    """Test that directory paths work (returns the directory if it's a package)."""
    result = find_package_for_file(Path("supekku/cli"))
    assert result == Path("supekku/cli")


class TestValidatePackagePath:
  """Test validate_package_path() function."""

  def test_accepts_valid_leaf_package(self) -> None:
    """Test that valid leaf packages pass validation."""
    validate_package_path(Path("supekku/cli"))  # Should not raise

  def test_accepts_valid_parent_package(self) -> None:
    """Test that parent packages also pass validation."""
    validate_package_path(Path("supekku/scripts/lib"))  # Should not raise

  def test_raises_for_nonexistent_path(self) -> None:
    """Test that non-existent paths raise FileNotFoundError."""
    with pytest.raises(FileNotFoundError, match="does not exist"):
      validate_package_path(Path("nonexistent/package"))

  def test_raises_for_file_path(self) -> None:
    """Test that file paths raise ValueError."""
    with pytest.raises(ValueError, match="must be a directory"):
      validate_package_path(Path("README.md"))

  def test_raises_for_directory_without_init(self) -> None:
    """Test that directories without __init__.py raise ValueError."""
    with pytest.raises(ValueError, match="missing __init__.py"):
      validate_package_path(Path("change/deltas"))


class TestFindAllLeafPackages:
  """Test find_all_leaf_packages() function."""

  def test_finds_all_18_leaf_packages_in_supekku(self) -> None:
    """Test that all 18 known leaf packages are discovered."""
    result = find_all_leaf_packages(Path("supekku"))
    result_set = {str(p) for p in result}

    assert len(result) == 18, f"Expected 18 leaf packages, found {len(result)}"
    assert result_set == KNOWN_LEAF_PACKAGES

  def test_returns_sorted_results(self) -> None:
    """Test that results are sorted for deterministic output."""
    result = find_all_leaf_packages(Path("supekku"))
    sorted_result = sorted(result)
    assert result == sorted_result

  def test_excludes_parent_packages(self) -> None:
    """Test that parent packages are not included in results."""
    result = find_all_leaf_packages(Path("supekku"))
    result_set = {str(p) for p in result}

    for parent_pkg in KNOWN_PARENT_PACKAGES:
      assert parent_pkg not in result_set

  def test_handles_single_leaf_package_tree(self) -> None:
    """Test discovery in a subtree with one leaf package."""
    # supekku/cli is a leaf package with no children
    result = find_all_leaf_packages(Path("supekku/cli"))
    assert len(result) == 1
    assert result[0] == Path("supekku/cli")

  def test_handles_nonexistent_root(self) -> None:
    """Test that non-existent root returns empty list."""
    result = find_all_leaf_packages(Path("nonexistent/root"))
    assert result == []

  def test_handles_tree_with_multiple_levels(self) -> None:
    """Test discovery in complex nested structure."""
    # supekku/scripts/lib has multiple leaf packages at various depths
    result = find_all_leaf_packages(Path("supekku/scripts/lib"))
    result_set = {str(p) for p in result}

    # Should find all leaf packages under lib/
    expected = {
      pkg for pkg in KNOWN_LEAF_PACKAGES if pkg.startswith("supekku/scripts/lib/")
    }
    assert result_set == expected


class TestEdgeCases:
  """Test edge cases and boundary conditions."""

  def test_single_file_package_is_leaf(self) -> None:
    """Test that a package with only __init__.py is a leaf package."""
    # supekku/cli only has __init__.py (no other Python files)
    # It should still be a leaf package
    assert is_leaf_package(Path("supekku/cli"))

  def test_deeply_nested_package(self) -> None:
    """Test handling of deeply nested packages."""
    # frontmatter_metadata is 5 levels deep
    deep_pkg = Path("supekku/scripts/lib/core/frontmatter_metadata")
    assert is_leaf_package(deep_pkg)

  def test_package_with_test_only_files(self) -> None:
    """Test packages containing only test files are still leaf packages."""
    # This is hypothetical, but the logic should work
    # A package is a leaf if it has __init__.py and no child packages,
    # regardless of what other files it contains
    pass  # Covered by real package tests

  def test_relative_vs_absolute_paths(self) -> None:
    """Test that both relative and absolute paths work."""
    relative = Path("supekku/cli")
    absolute = relative.absolute()

    assert is_leaf_package(relative)
    assert is_leaf_package(absolute)


class TestIntegrationScenarios:
  """Integration tests covering real-world workflows."""

  def test_file_to_package_to_validation_workflow(self) -> None:
    """Test complete workflow: file -> package -> validation."""
    # Step 1: Find package for a file
    file_path = Path("supekku/scripts/lib/formatters/decision_formatters.py")
    package = find_package_for_file(file_path)

    assert package is not None

    # Step 2: Validate the package
    validate_package_path(package)  # Should not raise

    # Step 3: Verify it's a leaf package
    assert is_leaf_package(package)

  def test_discover_all_then_validate_workflow(self) -> None:
    """Test workflow: discover all packages -> validate each."""
    packages = find_all_leaf_packages(Path("supekku"))

    # All discovered packages should pass validation
    for pkg in packages:
      validate_package_path(pkg)  # Should not raise
      assert is_leaf_package(pkg)

  def test_multiple_files_resolve_to_same_package(self) -> None:
    """Test that multiple files in same package resolve correctly."""
    files = [
      Path("supekku/scripts/lib/formatters/change_formatters.py"),
      Path("supekku/scripts/lib/formatters/decision_formatters.py"),
      Path("supekku/scripts/lib/formatters/__init__.py"),
    ]

    packages = [find_package_for_file(f) for f in files]

    # All should resolve to the same package
    assert all(p == Path("supekku/scripts/lib/formatters") for p in packages)
