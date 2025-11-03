"""Tests for decision_formatters module."""

from __future__ import annotations

import unittest
from datetime import date

from supekku.scripts.lib.decisions.registry import DecisionRecord
from supekku.scripts.lib.formatters.decision_formatters import format_decision_details


class TestFormatDecisionDetails(unittest.TestCase):
  """Tests for format_decision_details function."""

  def test_format_minimal_decision(self) -> None:
    """Test formatting with minimal required fields."""
    decision = DecisionRecord(
      id="ADR-001",
      title="Test Decision",
      status="draft",
    )

    result = format_decision_details(decision)

    assert "ID: ADR-001" in result
    assert "Title: Test Decision" in result
    assert "Status: draft" in result
    # Should not include empty optional fields
    assert "Authors:" not in result
    assert "Owners:" not in result
    assert "Supersedes:" not in result

  def test_format_full_decision(self) -> None:
    """Test formatting with all fields populated."""
    decision = DecisionRecord(
      id="ADR-002",
      title="Comprehensive Decision",
      status="accepted",
      created=date(2024, 1, 1),
      decided=date(2024, 1, 2),
      updated=date(2024, 1, 3),
      reviewed=date(2024, 1, 4),
      authors=[{"name": "Jane Doe", "contact": "jane@example.com"}],
      owners=["team-alpha"],
      supersedes=["ADR-001"],
      superseded_by=["ADR-003"],
      policies=["POL-001", "POL-002"],
      standards=["STD-001"],
      specs=["SPEC-100"],
      requirements=["SPEC-100.FR-001"],
      deltas=["DELTA-001"],
      revisions=["REV-001"],
      audits=["AUDIT-001"],
      related_decisions=["ADR-004"],
      related_policies=["POL-001"],
      tags=["api", "security"],
    )

    result = format_decision_details(decision)

    # Basic fields
    assert "ID: ADR-002" in result
    assert "Title: Comprehensive Decision" in result
    assert "Status: accepted" in result

    # Timestamps
    assert "Created: 2024-01-01" in result
    assert "Decided: 2024-01-02" in result
    assert "Updated: 2024-01-03" in result
    assert "Reviewed: 2024-01-04" in result

    # People
    assert "Authors: {'name': 'Jane Doe', 'contact': 'jane@example.com'}" in result
    assert "Owners: team-alpha" in result

    # Relationships
    assert "Supersedes: ADR-001" in result
    assert "Superseded by: ADR-003" in result

    # Cross-references
    assert "Policies: POL-001, POL-002" in result
    assert "Standards: STD-001" in result

    # References
    assert "Related specs: SPEC-100" in result
    assert "Requirements: SPEC-100.FR-001" in result
    assert "Deltas: DELTA-001" in result
    assert "Revisions: REV-001" in result
    assert "Audits: AUDIT-001" in result

    # Related items
    assert "Related decisions: ADR-004" in result
    assert "Related policies: POL-001" in result

    # Tags
    assert "Tags: api, security" in result

  def test_format_with_backlinks(self) -> None:
    """Test formatting with backlinks."""
    decision = DecisionRecord(
      id="ADR-003",
      title="Decision with Backlinks",
      status="accepted",
    )
    # Manually set backlinks (normally populated by registry)
    decision.backlinks = {
      "referenced_by": ["ADR-004", "ADR-005"],
      "implements": ["SPEC-200"],
    }

    result = format_decision_details(decision)

    assert "Backlinks:" in result
    assert "referenced_by: ADR-004, ADR-005" in result
    assert "implements: SPEC-200" in result

  def test_format_with_multiple_authors(self) -> None:
    """Test formatting with multiple authors."""
    decision = DecisionRecord(
      id="ADR-004",
      title="Multi-author Decision",
      status="accepted",
      authors=[
        {"name": "Alice", "contact": "alice@example.com"},
        {"name": "Bob", "contact": "bob@example.com"},
      ],
    )

    result = format_decision_details(decision)

    assert "Authors:" in result
    assert "Alice" in result
    assert "Bob" in result

  def test_format_preserves_order(self) -> None:
    """Test that output maintains logical field ordering."""
    decision = DecisionRecord(
      id="ADR-005",
      title="Ordered Fields",
      status="draft",
      created=date(2024, 1, 1),
      tags=["test"],
    )

    result = format_decision_details(decision)
    lines = result.split("\n")

    # Basic fields should come first
    assert lines[0] == "ID: ADR-005"
    assert lines[1] == "Title: Ordered Fields"
    assert lines[2] == "Status: draft"
    # Timestamp should follow
    assert lines[3] == "Created: 2024-01-01"
    # Tags should be near the end
    assert "Tags: test" in lines

  def test_format_with_policies_and_standards(self) -> None:
    """Test formatting decisions with policy and standard cross-references."""
    decision = DecisionRecord(
      id="ADR-006",
      title="Decision with Cross-References",
      status="accepted",
      policies=["POL-001", "POL-002"],
      standards=["STD-001", "STD-002", "STD-003"],
    )

    result = format_decision_details(decision)

    assert "Policies: POL-001, POL-002" in result
    assert "Standards: STD-001, STD-002, STD-003" in result

  def test_format_without_policies_or_standards(self) -> None:
    """Test that policies and standards are omitted when empty."""
    decision = DecisionRecord(
      id="ADR-007",
      title="Decision without Cross-References",
      status="draft",
    )

    result = format_decision_details(decision)

    assert "Policies:" not in result
    assert "Standards:" not in result


if __name__ == "__main__":
  unittest.main()
