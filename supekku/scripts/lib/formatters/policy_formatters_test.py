"""Tests for policy_formatters module."""

from __future__ import annotations

import json
import unittest
from datetime import date

from supekku.scripts.lib.formatters.policy_formatters import (
  format_policy_details,
  format_policy_list_json,
  format_policy_list_table,
)
from supekku.scripts.lib.policies.registry import PolicyRecord


class TestFormatPolicyDetails(unittest.TestCase):
  """Tests for format_policy_details function."""

  def test_format_minimal_policy(self) -> None:
    """Test formatting with minimal required fields."""
    policy = PolicyRecord(
      id="POL-001",
      title="Test Policy",
      status="draft",
    )

    result = format_policy_details(policy)

    assert "ID: POL-001" in result
    assert "Title: Test Policy" in result
    assert "Status: draft" in result
    # Should not include empty optional fields
    assert "Owners:" not in result
    assert "Supersedes:" not in result

  def test_format_full_policy(self) -> None:
    """Test formatting with all fields populated."""
    policy = PolicyRecord(
      id="POL-002",
      title="Comprehensive Policy",
      status="active",
      created=date(2024, 1, 1),
      updated=date(2024, 1, 3),
      reviewed=date(2024, 1, 4),
      owners=["team-alpha"],
      supersedes=["POL-001"],
      superseded_by=["POL-003"],
      standards=["STD-001"],
      specs=["SPEC-100"],
      requirements=["SPEC-100.FR-001"],
      deltas=["DE-001"],
      related_policies=["POL-004"],
      related_standards=["STD-002"],
      tags=["security", "compliance"],
    )

    result = format_policy_details(policy)

    # Basic fields
    assert "ID: POL-002" in result
    assert "Title: Comprehensive Policy" in result
    assert "Status: active" in result

    # Timestamps
    assert "Created: 2024-01-01" in result
    assert "Updated: 2024-01-03" in result
    assert "Reviewed: 2024-01-04" in result

    # People
    assert "Owners: team-alpha" in result

    # Relationships
    assert "Supersedes: POL-001" in result
    assert "Superseded by: POL-003" in result

    # References
    assert "Related specs: SPEC-100" in result
    assert "Requirements: SPEC-100.FR-001" in result
    assert "Deltas: DE-001" in result
    assert "Standards: STD-001" in result

    # Related items
    assert "Related policies: POL-004" in result
    assert "Related standards: STD-002" in result

    # Tags
    assert "Tags: security, compliance" in result

  def test_format_with_backlinks(self) -> None:
    """Test formatting with backlinks."""
    policy = PolicyRecord(
      id="POL-003",
      title="Policy with Backlinks",
      status="active",
    )
    # Manually set backlinks (normally populated by registry)
    policy.backlinks = {
      "referenced_by": ["ADR-004", "POL-005"],
      "enforces": ["STD-200"],
    }

    result = format_policy_details(policy)

    assert "Backlinks:" in result
    assert "referenced_by: ADR-004, POL-005" in result
    assert "enforces: STD-200" in result

  def test_format_with_multiple_owners(self) -> None:
    """Test formatting with multiple owners."""
    policy = PolicyRecord(
      id="POL-004",
      title="Multi-owner Policy",
      status="active",
      owners=["team-alpha", "team-beta"],
    )

    result = format_policy_details(policy)

    assert "Owners: team-alpha, team-beta" in result

  def test_format_preserves_order(self) -> None:
    """Test that output maintains logical field ordering."""
    policy = PolicyRecord(
      id="POL-005",
      title="Ordered Fields",
      status="draft",
      created=date(2024, 1, 1),
      tags=["test"],
    )

    result = format_policy_details(policy)
    lines = result.split("\n")

    # Basic fields should come first
    assert lines[0] == "ID: POL-005"
    assert lines[1] == "Title: Ordered Fields"
    assert lines[2] == "Status: draft"
    # Timestamp should follow
    assert lines[3] == "Created: 2024-01-01"
    # Tags should be near the end
    assert "Tags: test" in lines

  def test_format_empty_lists_omitted(self) -> None:
    """Test that empty list fields are not displayed."""
    policy = PolicyRecord(
      id="POL-006",
      title="Minimal Policy",
      status="active",
      owners=[],  # Empty list should be omitted
      tags=[],  # Empty list should be omitted
    )

    result = format_policy_details(policy)

    assert "Owners:" not in result
    assert "Tags:" not in result
    assert "Standards:" not in result


class TestFormatPolicyListJson(unittest.TestCase):
  """Tests for format_policy_list_json function."""

  def test_format_single_policy(self) -> None:
    """Test JSON formatting with single policy."""
    policy = PolicyRecord(
      id="POL-001",
      title="Test Policy",
      status="active",
      updated=date(2024, 1, 15),
      summary="Test summary",
      path="/path/to/policy",
    )

    result = format_policy_list_json([policy])
    data = json.loads(result)

    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == "POL-001"
    assert data["items"][0]["title"] == "Test Policy"
    assert data["items"][0]["status"] == "active"
    assert data["items"][0]["updated"] == "2024-01-15"
    assert data["items"][0]["summary"] == "Test summary"
    assert data["items"][0]["path"] == "/path/to/policy"

  def test_format_multiple_policies(self) -> None:
    """Test JSON formatting with multiple policies."""
    policies = [
      PolicyRecord(
        id="POL-001",
        title="First Policy",
        status="active",
        updated=date(2024, 1, 1),
      ),
      PolicyRecord(
        id="POL-002",
        title="Second Policy",
        status="draft",
        updated=date(2024, 1, 2),
      ),
    ]

    result = format_policy_list_json(policies)
    data = json.loads(result)

    assert len(data["items"]) == 2
    assert data["items"][0]["id"] == "POL-001"
    assert data["items"][1]["id"] == "POL-002"

  def test_format_policy_without_updated_date(self) -> None:
    """Test JSON formatting with policy missing updated date."""
    policy = PolicyRecord(
      id="POL-001",
      title="Test Policy",
      status="active",
      updated=None,
    )

    result = format_policy_list_json([policy])
    data = json.loads(result)

    assert data["items"][0]["updated"] is None


class TestFormatPolicyListTable(unittest.TestCase):
  """Tests for format_policy_list_table function."""

  def test_format_table_basic(self) -> None:
    """Test table formatting with basic policies."""
    policies = [
      PolicyRecord(
        id="POL-001",
        title="First Policy",
        status="active",
        updated=date(2024, 1, 1),
      ),
      PolicyRecord(
        id="POL-002",
        title="Second Policy",
        status="draft",
        updated=date(2024, 1, 2),
      ),
    ]

    result = format_policy_list_table(policies, format_type="table")

    assert "POL-001" in result
    assert "POL-002" in result
    assert "First Policy" in result
    assert "Second Policy" in result

  def test_format_tsv(self) -> None:
    """Test TSV formatting."""
    policies = [
      PolicyRecord(
        id="POL-001",
        title="First Policy",
        status="active",
        updated=date(2024, 1, 1),
      ),
    ]

    result = format_policy_list_table(policies, format_type="tsv")

    # TSV should contain tab-separated values
    assert "\t" in result
    assert "POL-001" in result
    assert "active" in result
    assert "First Policy" in result

  def test_format_json_via_table_function(self) -> None:
    """Test JSON formatting through format_policy_list_table."""
    policies = [
      PolicyRecord(
        id="POL-001",
        title="Test Policy",
        status="active",
        updated=date(2024, 1, 1),
      ),
    ]

    result = format_policy_list_table(policies, format_type="json")
    data = json.loads(result)

    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == "POL-001"

  def test_format_title_prefix_removal(self) -> None:
    """Test that POL-XXX: prefix is removed from titles in table view."""
    policy = PolicyRecord(
      id="POL-001",
      title="POL-001: Policy Title",
      status="active",
      updated=date(2024, 1, 1),
    )

    result = format_policy_list_table([policy], format_type="table")

    # Title should appear without prefix in table
    assert "Policy Title" in result

  def test_format_missing_updated_date(self) -> None:
    """Test formatting with missing updated date shows em dash."""
    policy = PolicyRecord(
      id="POL-001",
      title="Test Policy",
      status="active",
      updated=None,
    )

    result = format_policy_list_table([policy], format_type="table")

    # Em dash should appear for missing date
    assert "—" in result or "N/A" in result


if __name__ == "__main__":
  unittest.main()
