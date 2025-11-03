"""Tests for requirement_formatters module."""

from __future__ import annotations

import json
import unittest

from supekku.scripts.lib.formatters.requirement_formatters import (
  format_requirement_details,
  format_requirement_list_json,
  format_requirement_list_table,
)
from supekku.scripts.lib.requirements.registry import RequirementRecord


class TestFormatRequirementListTable(unittest.TestCase):
  """Tests for format_requirement_list_table function."""

  def test_format_empty_list_table(self) -> None:
    """Test formatting empty requirement list as table."""
    result = format_requirement_list_table([], format_type="table")
    assert "Requirements" in result
    assert isinstance(result, str)

  def test_format_empty_list_json(self) -> None:
    """Test formatting empty requirement list as JSON."""
    result = format_requirement_list_table([], format_type="json")
    data = json.loads(result)
    assert data["items"] == []

  def test_format_empty_list_tsv(self) -> None:
    """Test formatting empty requirement list as TSV."""
    result = format_requirement_list_table([], format_type="tsv")
    assert result == ""

  def test_format_single_requirement_table(self) -> None:
    """Test formatting single requirement as table."""
    req = RequirementRecord(
      uid="SPEC-001.FR-001",
      label="FR-001",
      title="User authentication",
      status="active",
      primary_spec="SPEC-001",
      specs=["SPEC-001"],
    )
    result = format_requirement_list_table([req], format_type="table")
    assert "FR-001" in result
    assert "SPEC-001" in result

  def test_format_single_requirement_json(self) -> None:
    """Test formatting single requirement as JSON."""
    req = RequirementRecord(
      uid="SPEC-001.FR-001",
      label="FR-001",
      title="User authentication",
      status="active",
      kind="functional",
      primary_spec="SPEC-001",
      specs=["SPEC-001"],
    )
    result = format_requirement_list_table([req], format_type="json")
    data = json.loads(result)
    assert len(data["items"]) == 1
    assert data["items"][0]["uid"] == "SPEC-001.FR-001"
    assert data["items"][0]["label"] == "FR-001"
    assert data["items"][0]["title"] == "User authentication"
    assert data["items"][0]["status"] == "active"
    assert data["items"][0]["kind"] == "functional"

  def test_format_single_requirement_tsv(self) -> None:
    """Test formatting single requirement as TSV."""
    req = RequirementRecord(
      uid="SPEC-001.FR-001",
      label="FR-001",
      title="User authentication",
      status="active",
      primary_spec="SPEC-001",
      specs=["SPEC-001"],
    )
    result = format_requirement_list_table([req], format_type="tsv")
    lines = result.strip().split("\n")
    assert len(lines) == 1
    fields = lines[0].split("\t")
    assert fields[0] == "SPEC-001"  # spec
    assert fields[1] == "FR-001"  # label
    assert fields[2] == "User authentication"  # title
    assert fields[3] == "active"  # status

  def test_format_multiple_requirements(self) -> None:
    """Test formatting multiple requirements."""
    reqs = [
      RequirementRecord(
        uid="SPEC-001.FR-001",
        label="FR-001",
        title="User authentication",
        status="active",
        primary_spec="SPEC-001",
        specs=["SPEC-001"],
      ),
      RequirementRecord(
        uid="SPEC-001.NF-001",
        label="NF-001",
        title="Response time < 200ms",
        status="in-progress",
        kind="non-functional",
        primary_spec="SPEC-001",
        specs=["SPEC-001"],
      ),
    ]
    result = format_requirement_list_table(reqs, format_type="json")
    data = json.loads(result)
    assert len(data["items"]) == 2
    assert data["items"][0]["uid"] == "SPEC-001.FR-001"
    assert data["items"][1]["uid"] == "SPEC-001.NF-001"
    assert data["items"][1]["kind"] == "non-functional"

  def test_format_with_lifecycle_fields(self) -> None:
    """Test formatting requirement with lifecycle fields."""
    req = RequirementRecord(
      uid="SPEC-001.FR-002",
      label="FR-002",
      title="Password reset",
      status="active",
      primary_spec="SPEC-001",
      specs=["SPEC-001"],
      introduced="RE-001",
      implemented_by=["DE-001"],
      verified_by=["AUD-001"],
    )
    result = format_requirement_list_table([req], format_type="json")
    data = json.loads(result)
    assert data["items"][0]["introduced"] == "RE-001"
    assert data["items"][0]["implemented_by"] == ["DE-001"]
    assert data["items"][0]["verified_by"] == ["AUD-001"]

  def test_format_with_no_primary_spec(self) -> None:
    """Test formatting requirement without primary spec."""
    req = RequirementRecord(
      uid="SPEC-001.FR-003",
      label="FR-003",
      title="Email verification",
      status="pending",
      specs=["SPEC-001", "SPEC-002"],
    )
    result = format_requirement_list_table([req], format_type="tsv")
    lines = result.strip().split("\n")
    fields = lines[0].split("\t")
    # Should use first spec from specs list
    assert fields[0] == "SPEC-001"

  def test_format_with_no_specs(self) -> None:
    """Test formatting requirement with no specs."""
    req = RequirementRecord(
      uid="SPEC-001.FR-004",
      label="FR-004",
      title="Orphaned requirement",
      status="retired",
    )
    result = format_requirement_list_table([req], format_type="tsv")
    # TSV should have spec (empty), label, title, status
    # Note: split('\t') doesn't create trailing empty field for leading empty
    assert result == "\tFR-004\tOrphaned requirement\tretired"


class TestFormatRequirementListJson(unittest.TestCase):
  """Tests for format_requirement_list_json function."""

  def test_format_minimal_requirement(self) -> None:
    """Test formatting requirement with minimal fields."""
    req = RequirementRecord(
      uid="SPEC-001.FR-001",
      label="FR-001",
      title="Test requirement",
      status="pending",
    )
    result = format_requirement_list_json([req])
    data = json.loads(result)
    assert data["items"][0]["uid"] == "SPEC-001.FR-001"
    assert data["items"][0]["label"] == "FR-001"
    assert data["items"][0]["status"] == "pending"
    # Optional fields should not be included if empty
    assert "introduced" not in data["items"][0]
    assert "implemented_by" not in data["items"][0]
    assert "verified_by" not in data["items"][0]
    assert "path" not in data["items"][0]

  def test_format_requirement_with_path(self) -> None:
    """Test formatting requirement with path."""
    req = RequirementRecord(
      uid="SPEC-001.FR-001",
      label="FR-001",
      title="Test requirement",
      status="active",
      path="specify/tech/SPEC-001/SPEC-001.md",
    )
    result = format_requirement_list_json([req])
    data = json.loads(result)
    assert data["items"][0]["path"] == "specify/tech/SPEC-001/SPEC-001.md"


class TestFormatRequirementDetails(unittest.TestCase):
  """Tests for format_requirement_details function."""

  def test_format_minimal_requirement(self) -> None:
    """Test formatting requirement with minimal fields."""
    req = RequirementRecord(
      uid="SPEC-001.FR-001",
      label="FR-001",
      title="User authentication",
      status="pending",
    )
    result = format_requirement_details(req)
    assert "UID: SPEC-001.FR-001" in result
    assert "Label: FR-001" in result
    assert "Title: User authentication" in result
    assert "Status: pending" in result
    # Should not include empty optional fields
    assert "Introduced:" not in result
    assert "Implemented by:" not in result

  def test_format_full_requirement(self) -> None:
    """Test formatting requirement with all fields."""
    req = RequirementRecord(
      uid="SPEC-001.FR-001",
      label="FR-001",
      title="User authentication",
      status="active",
      kind="functional",
      primary_spec="SPEC-001",
      specs=["SPEC-001", "SPEC-002"],
      introduced="RE-001",
      implemented_by=["DE-001", "DE-002"],
      verified_by=["AUD-001"],
      path="specify/tech/SPEC-001/SPEC-001.md",
    )
    result = format_requirement_details(req)
    assert "UID: SPEC-001.FR-001" in result
    assert "Label: FR-001" in result
    assert "Title: User authentication" in result
    assert "Kind: functional" in result
    assert "Status: active" in result
    assert "Primary Spec: SPEC-001" in result
    assert "Specs: SPEC-001, SPEC-002" in result
    assert "Introduced: RE-001" in result
    assert "Implemented by: DE-001, DE-002" in result
    assert "Verified by: AUD-001" in result
    assert "Path: specify/tech/SPEC-001/SPEC-001.md" in result
