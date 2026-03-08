"""Tests for spec_formatters module."""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from unittest.mock import Mock

from supekku.scripts.lib.formatters.spec_formatters import (
  format_package_list,
  format_spec_details,
  format_spec_list_item,
  format_spec_list_json,
  format_spec_list_table,
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


class TestFormatSpecDetails(unittest.TestCase):
  """Tests for format_spec_details function."""

  def _create_mock_spec(
    self,
    spec_id: str = "SPEC-001",
    name: str = "Test Specification",
    slug: str = "test-spec",
    *,
    kind: str = "spec",
    status: str = "draft",
    packages: list[str] | None = None,
    path: Path | None = None,
  ) -> Mock:
    """Create a mock Spec object with all fields."""
    spec = Mock()
    spec.id = spec_id
    spec.name = name
    spec.slug = slug
    spec.kind = kind
    spec.status = status
    spec.packages = packages or []
    spec.path = path or Path("/repo/specify/tech/SPEC-001/SPEC-001.md")
    return spec

  def test_minimal_spec(self) -> None:
    """Test formatting spec with minimal fields."""
    spec = self._create_mock_spec()

    result = format_spec_details(spec)

    assert "ID: SPEC-001" in result
    assert "Name: Test Specification" in result
    assert "Slug: test-spec" in result
    assert "Kind: spec" in result
    assert "Status: draft" in result

  def test_spec_with_packages(self) -> None:
    """Test formatting spec with packages."""
    spec = self._create_mock_spec(packages=["internal/api", "internal/models"])

    result = format_spec_details(spec)

    assert "Packages:" in result
    assert "internal/api" in result
    assert "internal/models" in result

  def test_spec_without_packages(self) -> None:
    """Test formatting spec with no packages."""
    spec = self._create_mock_spec(packages=[])

    result = format_spec_details(spec)

    # Should not show Packages section when empty
    assert "Packages:" not in result

  def test_spec_with_path(self) -> None:
    """Test formatting spec with file path."""
    spec = self._create_mock_spec(
      path=Path("/repo/specify/tech/SPEC-009/SPEC-009.md"),
    )
    root = Path("/repo")

    result = format_spec_details(spec, root=root)

    assert "File: specify/tech/SPEC-009/SPEC-009.md" in result

  def test_spec_without_root(self) -> None:
    """Test formatting spec without root shows absolute path."""
    spec = self._create_mock_spec(
      path=Path("/repo/specify/tech/SPEC-009/SPEC-009.md"),
    )

    result = format_spec_details(spec)

    assert "File: /repo/specify/tech/SPEC-009/SPEC-009.md" in result

  def test_product_spec(self) -> None:
    """Test formatting product spec."""
    spec = self._create_mock_spec(
      spec_id="PROD-042",
      name="User Dashboard",
      slug="user-dashboard",
      kind="prod",
      status="active",
    )

    result = format_spec_details(spec)

    assert "ID: PROD-042" in result
    assert "Name: User Dashboard" in result
    assert "Kind: prod" in result
    assert "Status: active" in result

  def test_complete_spec(self) -> None:
    """Test formatting spec with all fields populated."""
    spec = self._create_mock_spec(
      spec_id="SPEC-123",
      name="Complete Specification",
      slug="complete-spec",
      kind="spec",
      status="active",
      packages=["pkg/core", "pkg/utils", "internal/lib"],
      path=Path("/repo/specify/tech/SPEC-123/SPEC-123.md"),
    )
    root = Path("/repo")

    result = format_spec_details(spec, root=root)

    # Verify all sections present
    assert "ID: SPEC-123" in result
    assert "Name: Complete Specification" in result
    assert "Slug: complete-spec" in result
    assert "Kind: spec" in result
    assert "Status: active" in result
    assert "Packages:" in result
    assert "pkg/core" in result
    assert "File: specify/tech/SPEC-123/SPEC-123.md" in result

  def test_spec_with_taxonomy_fields(self) -> None:
    """Test formatting spec displays category and c4_level."""
    spec = self._create_mock_spec()
    spec.category = "assembly"
    spec.c4_level = "component"

    result = format_spec_details(spec)

    assert "Category: assembly" in result
    assert "C4 Level: component" in result

  def test_spec_with_category_only(self) -> None:
    """Test formatting spec with category but no c4_level."""
    spec = self._create_mock_spec()
    spec.category = "unit"
    spec.c4_level = ""

    result = format_spec_details(spec)

    assert "Category: unit" in result
    assert "C4 Level" not in result

  def test_spec_without_taxonomy(self) -> None:
    """Test formatting spec without taxonomy fields omits them."""
    spec = self._create_mock_spec()
    spec.category = ""
    spec.c4_level = ""

    result = format_spec_details(spec)

    assert "Category" not in result
    assert "C4 Level" not in result


class TestSpecExternalFields(unittest.TestCase):
  """Tests for ext_id/ext_url support in spec formatters (VT-067-002)."""

  def _create_mock_spec(
    self,
    spec_id: str = "SPEC-001",
    name: str = "Test Spec",
    slug: str = "test-spec",
    *,
    kind: str = "spec",
    status: str = "active",
    ext_id: str = "",
    ext_url: str = "",
    packages: list[str] | None = None,
    tags: list[str] | None = None,
  ) -> Mock:
    spec = Mock()
    spec.id = spec_id
    spec.name = name
    spec.slug = slug
    spec.kind = kind
    spec.status = status
    spec.ext_id = ext_id
    spec.ext_url = ext_url
    spec.packages = packages or []
    spec.tags = tags or []
    spec.category = ""
    spec.c4_level = ""
    spec.path = Path(f"/repo/specify/tech/{spec_id}/{spec_id}.md")
    return spec

  def test_details_with_ext_id_only(self) -> None:
    """Test detail formatter shows ext_id without url."""
    spec = self._create_mock_spec(ext_id="JIRA-123")
    result = format_spec_details(spec)
    assert "External: JIRA-123" in result
    assert "(" not in result.split("External:")[1].split("\n")[0]

  def test_details_with_ext_id_and_url(self) -> None:
    """Test detail formatter shows ext_id with url."""
    spec = self._create_mock_spec(
      ext_id="JIRA-123",
      ext_url="https://jira.example.com/JIRA-123",
    )
    result = format_spec_details(spec)
    assert "External: JIRA-123 (https://jira.example.com/JIRA-123)" in result

  def test_details_without_ext_id_omits_line(self) -> None:
    """Test detail formatter omits External line when no ext_id."""
    spec = self._create_mock_spec()
    result = format_spec_details(spec)
    assert "External:" not in result

  def test_json_includes_ext_fields(self) -> None:
    """Test JSON output includes ext_id and ext_url when present."""
    spec = self._create_mock_spec(
      ext_id="GH-42",
      ext_url="https://github.com/org/repo/issues/42",
    )
    result = format_spec_list_json([spec])
    data = json.loads(result)
    assert data["items"][0]["ext_id"] == "GH-42"
    assert data["items"][0]["ext_url"] == "https://github.com/org/repo/issues/42"

  def test_json_omits_ext_fields_when_empty(self) -> None:
    """Test JSON output omits ext_id/ext_url when empty."""
    spec = self._create_mock_spec()
    result = format_spec_list_json([spec])
    data = json.loads(result)
    assert "ext_id" not in data["items"][0]
    assert "ext_url" not in data["items"][0]

  def test_table_show_external_includes_column(self) -> None:
    """Test table output includes ExtID column when show_external=True."""
    spec = self._create_mock_spec(ext_id="LIN-99")
    result = format_spec_list_table([spec], format_type="table", show_external=True)
    assert "ExtID" in result
    assert "LIN-99" in result

  def test_table_no_external_omits_column(self) -> None:
    """Test table output omits ExtID column when show_external=False."""
    spec = self._create_mock_spec(ext_id="LIN-99")
    result = format_spec_list_table([spec], format_type="table", show_external=False)
    assert "ExtID" not in result

  def test_tsv_show_external_inserts_ext_id(self) -> None:
    """Test TSV output includes ext_id after ID when show_external=True."""
    spec = self._create_mock_spec(ext_id="LIN-99")
    result = format_spec_list_table([spec], format_type="tsv", show_external=True)
    fields = result.strip().split("\t")
    assert fields[0] == "SPEC-001"
    assert fields[1] == "LIN-99"

  def test_tsv_no_external_omits_ext_id(self) -> None:
    """Test TSV output omits ext_id when show_external=False."""
    spec = self._create_mock_spec(ext_id="LIN-99")
    result = format_spec_list_table([spec], format_type="tsv", show_external=False)
    fields = result.strip().split("\t")
    assert fields[0] == "SPEC-001"
    assert fields[1] == "Test Spec"


if __name__ == "__main__":
  unittest.main()
