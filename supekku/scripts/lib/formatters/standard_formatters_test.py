"""Tests for standard_formatters module."""

from __future__ import annotations

import json
import unittest
from datetime import date

from supekku.scripts.lib.formatters.standard_formatters import (
  format_standard_details,
  format_standard_list_json,
  format_standard_list_table,
)
from supekku.scripts.lib.standards.registry import StandardRecord


class TestFormatStandardDetails(unittest.TestCase):
  """Tests for format_standard_details function."""

  def test_format_minimal_standard(self) -> None:
    """Test formatting with minimal required fields."""
    standard = StandardRecord(
      id="STD-001",
      title="Test Standard",
      status="draft",
    )

    result = format_standard_details(standard)

    assert "ID: STD-001" in result
    assert "Title: Test Standard" in result
    assert "Status: draft" in result
    # Should not include empty optional fields
    assert "Owners:" not in result
    assert "Supersedes:" not in result

  def test_format_full_standard(self) -> None:
    """Test formatting with all fields populated."""
    standard = StandardRecord(
      id="STD-002",
      title="Comprehensive Standard",
      status="required",
      created=date(2024, 1, 1),
      updated=date(2024, 1, 3),
      reviewed=date(2024, 1, 4),
      owners=["team-alpha"],
      supersedes=["STD-001"],
      superseded_by=["STD-003"],
      policies=["POL-001"],
      specs=["SPEC-100"],
      requirements=["SPEC-100.FR-001"],
      deltas=["DE-001"],
      related_policies=["POL-004"],
      related_standards=["STD-005"],
      tags=["coding", "quality"],
    )

    result = format_standard_details(standard)

    # Basic fields
    assert "ID: STD-002" in result
    assert "Title: Comprehensive Standard" in result
    assert "Status: required" in result

    # Timestamps
    assert "Created: 2024-01-01" in result
    assert "Updated: 2024-01-03" in result
    assert "Reviewed: 2024-01-04" in result

    # People
    assert "Owners: team-alpha" in result

    # Relationships
    assert "Supersedes: STD-001" in result
    assert "Superseded by: STD-003" in result

    # References
    assert "Related specs: SPEC-100" in result
    assert "Requirements: SPEC-100.FR-001" in result
    assert "Deltas: DE-001" in result
    assert "Policies: POL-001" in result

    # Related items
    assert "Related policies: POL-004" in result
    assert "Related standards: STD-005" in result

    # Tags
    assert "Tags: coding, quality" in result

  def test_format_default_status_standard(self) -> None:
    """Test formatting with 'default' status (unique to standards)."""
    standard = StandardRecord(
      id="STD-003",
      title="Default Standard",
      status="default",
      summary="Recommended unless justified otherwise",
    )

    result = format_standard_details(standard)

    assert "ID: STD-003" in result
    assert "Status: default" in result

  def test_format_with_backlinks(self) -> None:
    """Test formatting with backlinks."""
    standard = StandardRecord(
      id="STD-004",
      title="Standard with Backlinks",
      status="required",
    )
    # Manually set backlinks (normally populated by registry)
    standard.backlinks = {
      "referenced_by": ["ADR-004", "STD-005"],
      "guided_by": ["POL-200"],
    }

    result = format_standard_details(standard)

    assert "Backlinks:" in result
    assert "referenced_by: ADR-004, STD-005" in result
    assert "guided_by: POL-200" in result

  def test_format_with_multiple_owners(self) -> None:
    """Test formatting with multiple owners."""
    standard = StandardRecord(
      id="STD-005",
      title="Multi-owner Standard",
      status="required",
      owners=["team-alpha", "team-beta"],
    )

    result = format_standard_details(standard)

    assert "Owners: team-alpha, team-beta" in result

  def test_format_preserves_order(self) -> None:
    """Test that output maintains logical field ordering."""
    standard = StandardRecord(
      id="STD-006",
      title="Ordered Fields",
      status="draft",
      created=date(2024, 1, 1),
      tags=["test"],
    )

    result = format_standard_details(standard)
    lines = result.split("\n")

    # Basic fields should come first
    assert lines[0] == "ID: STD-006"
    assert lines[1] == "Title: Ordered Fields"
    assert lines[2] == "Status: draft"
    # Timestamp should follow
    assert lines[3] == "Created: 2024-01-01"
    # Tags should be near the end
    assert "Tags: test" in lines

  def test_format_empty_lists_omitted(self) -> None:
    """Test that empty list fields are not displayed."""
    standard = StandardRecord(
      id="STD-007",
      title="Minimal Standard",
      status="required",
      owners=[],  # Empty list should be omitted
      tags=[],  # Empty list should be omitted
    )

    result = format_standard_details(standard)

    assert "Owners:" not in result
    assert "Tags:" not in result
    assert "Policies:" not in result


class TestFormatStandardListJson(unittest.TestCase):
  """Tests for format_standard_list_json function."""

  def test_format_single_standard(self) -> None:
    """Test JSON formatting with single standard."""
    standard = StandardRecord(
      id="STD-001",
      title="Test Standard",
      status="required",
      updated=date(2024, 1, 15),
      summary="Test summary",
      path="/path/to/standard",
    )

    result = format_standard_list_json([standard])
    data = json.loads(result)

    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == "STD-001"
    assert data["items"][0]["title"] == "Test Standard"
    assert data["items"][0]["status"] == "required"
    assert data["items"][0]["updated"] == "2024-01-15"
    assert data["items"][0]["summary"] == "Test summary"
    assert data["items"][0]["path"] == "/path/to/standard"

  def test_format_multiple_standards(self) -> None:
    """Test JSON formatting with multiple standards."""
    standards = [
      StandardRecord(
        id="STD-001",
        title="First Standard",
        status="required",
        updated=date(2024, 1, 1),
      ),
      StandardRecord(
        id="STD-002",
        title="Second Standard",
        status="default",
        updated=date(2024, 1, 2),
      ),
    ]

    result = format_standard_list_json(standards)
    data = json.loads(result)

    assert len(data["items"]) == 2
    assert data["items"][0]["id"] == "STD-001"
    assert data["items"][1]["id"] == "STD-002"
    assert data["items"][1]["status"] == "default"

  def test_format_standard_without_updated_date(self) -> None:
    """Test JSON formatting with standard missing updated date."""
    standard = StandardRecord(
      id="STD-001",
      title="Test Standard",
      status="required",
      updated=None,
    )

    result = format_standard_list_json([standard])
    data = json.loads(result)

    assert data["items"][0]["updated"] is None


class TestFormatStandardListTable(unittest.TestCase):
  """Tests for format_standard_list_table function."""

  def test_format_table_basic(self) -> None:
    """Test table formatting with basic standards."""
    standards = [
      StandardRecord(
        id="STD-001",
        title="First Standard",
        status="required",
        updated=date(2024, 1, 1),
      ),
      StandardRecord(
        id="STD-002",
        title="Second Standard",
        status="default",
        updated=date(2024, 1, 2),
      ),
    ]

    result = format_standard_list_table(standards, format_type="table")

    assert "STD-001" in result
    assert "STD-002" in result
    assert "First Standard" in result
    assert "Second Standard" in result

  def test_format_tsv(self) -> None:
    """Test TSV formatting."""
    standards = [
      StandardRecord(
        id="STD-001",
        title="First Standard",
        status="required",
        updated=date(2024, 1, 1),
      ),
    ]

    result = format_standard_list_table(standards, format_type="tsv")

    # TSV should contain tab-separated values
    assert "\t" in result
    assert "STD-001" in result
    assert "required" in result
    assert "First Standard" in result

  def test_format_json_via_table_function(self) -> None:
    """Test JSON formatting through format_standard_list_table."""
    standards = [
      StandardRecord(
        id="STD-001",
        title="Test Standard",
        status="default",
        updated=date(2024, 1, 1),
      ),
    ]

    result = format_standard_list_table(standards, format_type="json")
    data = json.loads(result)

    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == "STD-001"
    assert data["items"][0]["status"] == "default"

  def test_format_title_prefix_removal(self) -> None:
    """Test that STD-XXX: prefix is removed from titles in table view."""
    standard = StandardRecord(
      id="STD-001",
      title="STD-001: Standard Title",
      status="required",
      updated=date(2024, 1, 1),
    )

    result = format_standard_list_table([standard], format_type="table")

    # Title should appear without prefix in table
    assert "Standard Title" in result

  def test_format_missing_updated_date(self) -> None:
    """Test formatting with missing updated date shows em dash."""
    standard = StandardRecord(
      id="STD-001",
      title="Test Standard",
      status="required",
      updated=None,
    )

    result = format_standard_list_table([standard], format_type="table")

    # Em dash should appear for missing date
    assert "—" in result or "N/A" in result


if __name__ == "__main__":
  unittest.main()
