"""Tests for spec_formatters module."""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import Mock

from supekku.scripts.lib.formatters.spec_formatters import (
  format_package_list,
  format_spec_list_item,
)


class TestFormatPackageList(unittest.TestCase):
  """Tests for format_package_list function."""

  def test_empty_list(self) -> None:
    """Test formatting empty package list."""
    result = format_package_list([])
    assert result == ""

  def test_single_package(self) -> None:
    """Test formatting single package."""
    result = format_package_list(["internal/api"])
    assert result == "internal/api"

  def test_multiple_packages(self) -> None:
    """Test formatting multiple packages."""
    result = format_package_list(["internal/api", "internal/models", "pkg/utils"])
    assert result == "internal/api,internal/models,pkg/utils"


class TestFormatSpecListItem(unittest.TestCase):
  """Tests for format_spec_list_item function."""

  def _create_mock_spec(
    self,
    spec_id: str = "SPEC-001",
    slug: str = "test-spec",
    packages: list[str] | None = None,
    path: Path | None = None,
  ) -> Mock:
    """Create a mock Spec object."""
    spec = Mock()
    spec.id = spec_id
    spec.slug = slug
    spec.packages = packages or []
    spec.path = path or Path("/tmp/specs/SPEC-001.md")
    return spec

  def test_basic_format(self) -> None:
    """Test basic format with id and slug."""
    spec = self._create_mock_spec()
    result = format_spec_list_item(spec)
    assert result == "SPEC-001\ttest-spec"

  def test_format_with_path(self) -> None:
    """Test format with path instead of slug."""
    spec = self._create_mock_spec(path=Path("/repo/specify/tech/SPEC-001.md"))
    root = Path("/repo")

    result = format_spec_list_item(spec, include_path=True, root=root)

    assert result == "SPEC-001\tspecify/tech/SPEC-001.md"

  def test_format_with_path_no_root_raises(self) -> None:
    """Test that include_path without root raises ValueError."""
    spec = self._create_mock_spec()

    with self.assertRaises(ValueError) as ctx:
      format_spec_list_item(spec, include_path=True)

    assert "root parameter required" in str(ctx.exception)

  def test_format_with_path_outside_root(self) -> None:
    """Test path formatting when spec path is outside root."""
    spec = self._create_mock_spec(path=Path("/other/location/SPEC-001.md"))
    root = Path("/repo")

    result = format_spec_list_item(spec, include_path=True, root=root)

    # Should use absolute path when relative_to fails
    assert result == "SPEC-001\t/other/location/SPEC-001.md"

  def test_format_with_packages(self) -> None:
    """Test format with package list."""
    spec = self._create_mock_spec(packages=["internal/api", "internal/models"])

    result = format_spec_list_item(spec, include_packages=True)

    assert result == "SPEC-001\ttest-spec\tinternal/api,internal/models"

  def test_format_with_empty_packages(self) -> None:
    """Test format with empty package list."""
    spec = self._create_mock_spec(packages=[])

    result = format_spec_list_item(spec, include_packages=True)

    assert result == "SPEC-001\ttest-spec\t"

  def test_format_with_path_and_packages(self) -> None:
    """Test format with both path and packages."""
    spec = self._create_mock_spec(
      path=Path("/repo/specify/tech/SPEC-001.md"),
      packages=["internal/api"],
    )
    root = Path("/repo")

    result = format_spec_list_item(
      spec,
      include_path=True,
      include_packages=True,
      root=root,
    )

    assert result == "SPEC-001\tspecify/tech/SPEC-001.md\tinternal/api"

  def test_product_spec(self) -> None:
    """Test formatting product spec."""
    spec = self._create_mock_spec(
      spec_id="PROD-042",
      slug="user-dashboard",
      path=Path("/repo/specify/product/PROD-042.md"),
    )
    root = Path("/repo")

    result = format_spec_list_item(spec, include_path=True, root=root)

    assert result == "PROD-042\tspecify/product/PROD-042.md"

  def test_all_options(self) -> None:
    """Test formatting with all options enabled."""
    spec = self._create_mock_spec(
      spec_id="SPEC-123",
      slug="complex-spec",
      path=Path("/repo/specify/tech/complex/SPEC-123.md"),
      packages=["pkg/core", "pkg/utils", "internal/lib"],
    )
    root = Path("/repo")

    result = format_spec_list_item(
      spec,
      include_path=True,
      include_packages=True,
      root=root,
    )

    expected = (
      "SPEC-123\tspecify/tech/complex/SPEC-123.md\tpkg/core,pkg/utils,internal/lib"
    )
    assert result == expected


if __name__ == "__main__":
  unittest.main()
