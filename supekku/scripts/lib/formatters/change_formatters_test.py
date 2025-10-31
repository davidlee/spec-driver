"""Tests for change_formatters module."""

from __future__ import annotations

import unittest
from pathlib import Path

from supekku.scripts.lib.changes.artifacts import ChangeArtifact
from supekku.scripts.lib.formatters.change_formatters import (
  format_change_list_item,
  format_change_with_context,
  format_phase_summary,
)


class TestFormatChangeListItem(unittest.TestCase):
  """Tests for format_change_list_item function."""

  def test_format_basic_delta(self) -> None:
    """Test formatting a basic delta artifact."""
    artifact = ChangeArtifact(
      id="DE-001",
      kind="delta",
      status="draft",
      name="Test Delta",
      slug="test-delta",
      path=Path("/tmp/test.md"),
      updated=None,
    )

    result = format_change_list_item(artifact)

    assert result == "DE-001\tdelta\tdraft\tTest Delta"

  def test_format_revision_artifact(self) -> None:
    """Test formatting a revision artifact."""
    artifact = ChangeArtifact(
      id="RE-042",
      kind="revision",
      status="completed",
      name="Update API Schema",
      slug="update-api-schema",
      path=Path("/tmp/revision.md"),
      updated="2024-01-15",
    )

    result = format_change_list_item(artifact)

    assert result == "RE-042\trevision\tcompleted\tUpdate API Schema"


class TestFormatPhaseSummary(unittest.TestCase):
  """Tests for format_phase_summary function."""

  def test_phase_with_objective(self) -> None:
    """Test formatting phase with objective."""
    phase = {
      "phase": "P1",
      "objective": "Implement authentication layer",
    }

    result = format_phase_summary(phase)

    assert result == "P1: Implement authentication layer"

  def test_phase_without_objective(self) -> None:
    """Test formatting phase without objective."""
    phase = {
      "phase": "P2",
    }

    result = format_phase_summary(phase)

    assert result == "P2"

  def test_phase_with_long_objective(self) -> None:
    """Test formatting phase with objective exceeding max length."""
    phase = {
      "phase": "P3",
      "objective": (
        "This is a very long objective that exceeds the maximum allowed "
        "length and should be truncated appropriately with ellipsis"
      ),
    }

    result = format_phase_summary(phase, max_objective_len=60)

    assert len(result) <= 64  # "P3: " + 57 chars + "..."
    assert result.startswith("P3: This is a very long objective")
    assert result.endswith("...")

  def test_phase_with_multiline_objective(self) -> None:
    """Test that only first line of objective is used."""
    phase = {
      "phase": "P4",
      "objective": "First line objective\nSecond line\nThird line",
    }

    result = format_phase_summary(phase)

    assert result == "P4: First line objective"
    assert "Second line" not in result

  def test_phase_with_id_instead_of_phase(self) -> None:
    """Test phase using 'id' field instead of 'phase'."""
    phase = {
      "id": "PHASE-X",
      "objective": "Alternative identifier",
    }

    result = format_phase_summary(phase)

    assert result == "PHASE-X: Alternative identifier"

  def test_phase_with_empty_objective(self) -> None:
    """Test phase with empty string objective."""
    phase = {
      "phase": "P5",
      "objective": "   ",
    }

    result = format_phase_summary(phase)

    assert result == "P5"


class TestFormatChangeWithContext(unittest.TestCase):
  """Tests for format_change_with_context function."""

  def test_format_minimal_change(self) -> None:
    """Test formatting change with no additional context."""
    artifact = ChangeArtifact(
      id="DE-001",
      kind="delta",
      status="draft",
      name="Minimal Change",
      slug="minimal-change",
      path=Path("/tmp/test.md"),
      updated=None,
    )

    result = format_change_with_context(artifact)

    assert result == "DE-001\tdelta\tdraft\tMinimal Change"

  def test_format_with_specs(self) -> None:
    """Test formatting change with related specs."""
    artifact = ChangeArtifact(
      id="DE-002",
      kind="delta",
      status="draft",
      name="Change with Specs",
      slug="change-with-specs",
      path=Path("/tmp/test.md"),
      updated=None,
      applies_to={"specs": ["SPEC-100", "SPEC-101"]},
    )

    result = format_change_with_context(artifact)

    lines = result.split("\n")
    assert len(lines) == 2
    assert lines[0] == "DE-002\tdelta\tdraft\tChange with Specs"
    assert lines[1] == "  specs: SPEC-100, SPEC-101"

  def test_format_with_requirements(self) -> None:
    """Test formatting change with requirements."""
    artifact = ChangeArtifact(
      id="DE-003",
      kind="delta",
      status="draft",
      name="Change with Requirements",
      slug="change-with-reqs",
      path=Path("/tmp/test.md"),
      updated=None,
      applies_to={"requirements": ["SPEC-100.FR-001", "SPEC-100.FR-002"]},
    )

    result = format_change_with_context(artifact)

    lines = result.split("\n")
    assert lines[1] == "  requirements: SPEC-100.FR-001, SPEC-100.FR-002"

  def test_format_with_phases(self) -> None:
    """Test formatting change with plan phases."""
    artifact = ChangeArtifact(
      id="DE-004",
      kind="delta",
      status="draft",
      name="Change with Phases",
      slug="change-with-phases",
      path=Path("/tmp/test.md"),
      updated=None,
      plan={
        "phases": [
          {"phase": "P1", "objective": "Design phase"},
          {"phase": "P2", "objective": "Implementation phase"},
        ],
      },
    )

    result = format_change_with_context(artifact)

    lines = result.split("\n")
    assert len(lines) == 4
    assert lines[0] == "DE-004\tdelta\tdraft\tChange with Phases"
    assert lines[1] == "  phases:"
    assert lines[2] == "    P1: Design phase"
    assert lines[3] == "    P2: Implementation phase"

  def test_format_with_all_context(self) -> None:
    """Test formatting change with all context fields."""
    artifact = ChangeArtifact(
      id="DE-005",
      kind="delta",
      status="in-progress",
      name="Comprehensive Change",
      slug="comprehensive-change",
      path=Path("/tmp/test.md"),
      updated="2024-01-15",
      applies_to={
        "specs": ["SPEC-200"],
        "requirements": ["SPEC-200.FR-001"],
      },
      plan={
        "phases": [
          {"phase": "P1", "objective": "Analysis"},
        ],
      },
    )

    result = format_change_with_context(artifact)

    lines = result.split("\n")
    assert len(lines) == 5
    assert "DE-005" in lines[0]
    assert "  specs: SPEC-200" in lines
    assert "  requirements: SPEC-200.FR-001" in lines
    assert "  phases:" in lines
    assert "    P1: Analysis" in lines

  def test_format_empty_applies_to(self) -> None:
    """Test formatting when applies_to is empty dict."""
    artifact = ChangeArtifact(
      id="DE-006",
      kind="delta",
      status="draft",
      name="Empty Applies",
      slug="empty-applies",
      path=Path("/tmp/test.md"),
      updated=None,
      applies_to={},
    )

    result = format_change_with_context(artifact)

    # Should only have the basic line, no specs/requirements
    assert result == "DE-006\tdelta\tdraft\tEmpty Applies"

  def test_format_empty_phases_list(self) -> None:
    """Test formatting when phases list is empty."""
    artifact = ChangeArtifact(
      id="DE-007",
      kind="delta",
      status="draft",
      name="Empty Phases",
      slug="empty-phases",
      path=Path("/tmp/test.md"),
      updated=None,
      plan={"phases": []},
    )

    result = format_change_with_context(artifact)

    # Should not include "phases:" header
    assert result == "DE-007\tdelta\tdraft\tEmpty Phases"
    assert "phases:" not in result


if __name__ == "__main__":
  unittest.main()
