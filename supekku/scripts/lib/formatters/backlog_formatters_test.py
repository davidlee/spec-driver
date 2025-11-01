"""Tests for backlog_formatters module."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from supekku.scripts.lib.backlog.models import BacklogItem
from supekku.scripts.lib.formatters.backlog_formatters import (
  format_backlog_details,
  format_backlog_list_json,
  format_backlog_list_table,
)


class TestFormatBacklogListTable(unittest.TestCase):
  """Tests for format_backlog_list_table function."""

  def test_format_empty_list_table(self) -> None:
    """Test formatting empty backlog list as table."""
    result = format_backlog_list_table([], format_type="table")
    assert "Backlog Items" in result
    assert isinstance(result, str)

  def test_format_empty_list_json(self) -> None:
    """Test formatting empty backlog list as JSON."""
    result = format_backlog_list_table([], format_type="json")
    data = json.loads(result)
    assert data["items"] == []

  def test_format_empty_list_tsv(self) -> None:
    """Test formatting empty backlog list as TSV."""
    result = format_backlog_list_table([], format_type="tsv")
    assert result == ""

  def test_format_single_issue_table(self) -> None:
    """Test formatting single issue as table."""
    item = BacklogItem(
      id="ISSUE-001",
      kind="issue",
      status="open",
      title="Login button not working",
      path=Path("backlog/issues/ISSUE-001-login-bug/ISSUE-001.md"),
      severity="p1",
    )
    result = format_backlog_list_table([item], format_type="table")
    assert "ISSUE-001" in result
    assert "issue" in result

  def test_format_single_issue_json(self) -> None:
    """Test formatting single issue as JSON."""
    item = BacklogItem(
      id="ISSUE-001",
      kind="issue",
      status="open",
      title="Login button not working",
      path=Path("backlog/issues/ISSUE-001-login-bug/ISSUE-001.md"),
      severity="p1",
      categories=["ui", "auth"],
      impact="user",
    )
    result = format_backlog_list_table([item], format_type="json")
    data = json.loads(result)
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == "ISSUE-001"
    assert data["items"][0]["kind"] == "issue"
    assert data["items"][0]["status"] == "open"
    assert data["items"][0]["title"] == "Login button not working"
    assert data["items"][0]["severity"] == "p1"
    assert data["items"][0]["categories"] == ["ui", "auth"]
    assert data["items"][0]["impact"] == "user"

  def test_format_single_issue_tsv(self) -> None:
    """Test formatting single issue as TSV."""
    item = BacklogItem(
      id="ISSUE-001",
      kind="issue",
      status="open",
      title="Login button not working",
      path=Path("backlog/issues/ISSUE-001-login-bug/ISSUE-001.md"),
      severity="p1",
    )
    result = format_backlog_list_table([item], format_type="tsv")
    lines = result.strip().split("\n")
    assert len(lines) == 1
    fields = lines[0].split("\t")
    assert fields[0] == "ISSUE-001"
    assert fields[1] == "issue"
    assert fields[2] == "open"
    assert fields[3] == "Login button not working"
    assert fields[4] == "p1"

  def test_format_multiple_backlog_items(self) -> None:
    """Test formatting multiple backlog items of different kinds."""
    items = [
      BacklogItem(
        id="ISSUE-001",
        kind="issue",
        status="open",
        title="Login bug",
        path=Path("backlog/issues/ISSUE-001/ISSUE-001.md"),
        severity="p1",
      ),
      BacklogItem(
        id="PROB-001",
        kind="problem",
        status="captured",
        title="Users can't reset password",
        path=Path("backlog/problems/PROB-001/PROB-001.md"),
      ),
      BacklogItem(
        id="IMPR-001",
        kind="improvement",
        status="idea",
        title="Add dark mode",
        path=Path("backlog/improvements/IMPR-001/IMPR-001.md"),
      ),
      BacklogItem(
        id="RISK-001",
        kind="risk",
        status="suspected",
        title="Data breach risk",
        path=Path("backlog/risks/RISK-001/RISK-001.md"),
        severity="p2",
        likelihood=0.3,
      ),
    ]
    result = format_backlog_list_table(items, format_type="json")
    data = json.loads(result)
    assert len(data["items"]) == 4
    assert data["items"][0]["id"] == "ISSUE-001"
    assert data["items"][1]["id"] == "PROB-001"
    assert data["items"][2]["id"] == "IMPR-001"
    assert data["items"][3]["id"] == "RISK-001"
    assert data["items"][3]["likelihood"] == 0.3

  def test_format_with_timestamps(self) -> None:
    """Test formatting backlog item with timestamps."""
    item = BacklogItem(
      id="ISSUE-002",
      kind="issue",
      status="resolved",
      title="Memory leak",
      path=Path("backlog/issues/ISSUE-002/ISSUE-002.md"),
      severity="p2",
      created="2025-01-01",
      updated="2025-01-15",
    )
    result = format_backlog_list_table([item], format_type="json")
    data = json.loads(result)
    assert data["items"][0]["created"] == "2025-01-01"
    assert data["items"][0]["updated"] == "2025-01-15"

  def test_format_problem_without_severity(self) -> None:
    """Test formatting problem item without severity field."""
    item = BacklogItem(
      id="PROB-002",
      kind="problem",
      status="analyzed",
      title="Performance degradation",
      path=Path("backlog/problems/PROB-002/PROB-002.md"),
    )
    result = format_backlog_list_table([item], format_type="tsv")
    # TSV should have id, kind, status, title, and empty severity
    # Note: split('\t') doesn't create trailing empty field
    assert result == "PROB-002\tproblem\tanalyzed\tPerformance degradation\t"


class TestFormatBacklogListJson(unittest.TestCase):
  """Tests for format_backlog_list_json function."""

  def test_format_minimal_backlog_item(self) -> None:
    """Test formatting backlog item with minimal fields."""
    item = BacklogItem(
      id="IMPR-001",
      kind="improvement",
      status="idea",
      title="Add feature X",
      path=Path("backlog/improvements/IMPR-001/IMPR-001.md"),
    )
    result = format_backlog_list_json([item])
    data = json.loads(result)
    assert data["items"][0]["id"] == "IMPR-001"
    assert data["items"][0]["kind"] == "improvement"
    assert data["items"][0]["status"] == "idea"
    assert data["items"][0]["title"] == "Add feature X"
    # Optional fields should not be included if not present
    assert "severity" not in data["items"][0]
    assert "categories" not in data["items"][0]

  def test_format_backlog_item_with_all_fields(self) -> None:
    """Test formatting backlog item with all possible fields."""
    item = BacklogItem(
      id="RISK-002",
      kind="risk",
      status="confirmed",
      title="Security vulnerability",
      path=Path("backlog/risks/RISK-002/RISK-002.md"),
      severity="p1",
      categories=["security", "api"],
      impact="system",
      likelihood=0.8,
      created="2025-01-01",
      updated="2025-01-10",
    )
    result = format_backlog_list_json([item])
    data = json.loads(result)
    assert data["items"][0]["severity"] == "p1"
    assert data["items"][0]["categories"] == ["security", "api"]
    assert data["items"][0]["impact"] == "system"
    assert data["items"][0]["likelihood"] == 0.8
    assert data["items"][0]["created"] == "2025-01-01"
    assert data["items"][0]["updated"] == "2025-01-10"


class TestFormatBacklogDetails(unittest.TestCase):
  """Tests for format_backlog_details function."""

  def test_format_minimal_backlog_item(self) -> None:
    """Test formatting backlog item with minimal fields."""
    item = BacklogItem(
      id="IMPR-001",
      kind="improvement",
      status="idea",
      title="Add feature X",
      path=Path("backlog/improvements/IMPR-001/IMPR-001.md"),
    )
    result = format_backlog_details(item)
    assert "ID: IMPR-001" in result
    assert "Kind: improvement" in result
    assert "Status: idea" in result
    assert "Title: Add feature X" in result
    # Should not include missing optional fields
    assert "Severity:" not in result
    assert "Categories:" not in result

  def test_format_full_issue(self) -> None:
    """Test formatting issue with all fields."""
    item = BacklogItem(
      id="ISSUE-003",
      kind="issue",
      status="in-progress",
      title="Database connection timeout",
      path=Path("backlog/issues/ISSUE-003/ISSUE-003.md"),
      severity="p2",
      categories=["backend", "database"],
      impact="user",
      created="2025-01-05",
      updated="2025-01-20",
    )
    result = format_backlog_details(item)
    assert "ID: ISSUE-003" in result
    assert "Kind: issue" in result
    assert "Status: in-progress" in result
    assert "Title: Database connection timeout" in result
    assert "Severity: p2" in result
    assert "Categories: backend, database" in result
    assert "Impact: user" in result
    assert "Created: 2025-01-05" in result
    assert "Updated: 2025-01-20" in result

  def test_format_risk_with_likelihood(self) -> None:
    """Test formatting risk with likelihood field."""
    item = BacklogItem(
      id="RISK-003",
      kind="risk",
      status="mitigated",
      title="Third-party API failure",
      path=Path("backlog/risks/RISK-003/RISK-003.md"),
      severity="p3",
      likelihood=0.2,
    )
    result = format_backlog_details(item)
    assert "Likelihood: 0.2" in result
