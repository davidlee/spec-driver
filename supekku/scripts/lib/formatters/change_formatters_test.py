"""Tests for change_formatters module."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from supekku.scripts.lib.changes.artifacts import ChangeArtifact
from supekku.scripts.lib.core.paths import AUDITS_SUBDIR, DELTAS_SUBDIR, SPEC_DRIVER_DIR
from supekku.scripts.lib.formatters.change_formatters import (
  _format_delta_reverse_lookups,
  format_audit_details,
  format_change_list_item,
  format_change_list_json,
  format_change_list_table,
  format_change_with_context,
  format_delta_details,
  format_phase_summary,
  format_plan_details,
  format_plan_list_table,
  format_revision_details,
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


class TestFormatRevisionDetails(unittest.TestCase):
  """Tests for format_revision_details function."""

  def test_minimal_revision(self) -> None:
    """Test formatting revision with minimal fields."""
    artifact = ChangeArtifact(
      id="RE-001",
      kind="revision",
      status="draft",
      name="Test Revision",
      slug="test-revision",
      path=Path("/repo/change/revisions/RE-001/RE-001.md"),
      updated=None,
    )
    root = Path("/repo")

    result = format_revision_details(artifact, root=root)

    assert "Revision: RE-001" in result
    assert "Name: Test Revision" in result
    assert "Status: draft" in result
    assert "Kind: revision" in result
    assert "File: change/revisions/RE-001/RE-001.md" in result

  def test_revision_with_applies_to(self) -> None:
    """Test formatting revision with applies_to specs and requirements."""
    artifact = ChangeArtifact(
      id="RE-002",
      kind="revision",
      status="completed",
      name="API Schema Changes",
      slug="api-schema-changes",
      path=Path("/repo/change/revisions/RE-002/RE-002.md"),
      updated="2024-10-20",
      applies_to={
        "specs": ["SPEC-009", "SPEC-010"],
        "requirements": ["SPEC-009.FR-001", "SPEC-010.FR-001"],
      },
    )

    result = format_revision_details(artifact)

    assert "Affects:" in result
    assert "Specs: SPEC-009, SPEC-010" in result
    assert "Requirements:" in result
    assert "SPEC-009.FR-001" in result
    assert "SPEC-010.FR-001" in result

  def test_revision_with_relations(self) -> None:
    """Test formatting revision with relations."""
    artifact = ChangeArtifact(
      id="RE-003",
      kind="revision",
      status="draft",
      name="Related Revision",
      slug="related",
      path=Path("/repo/test.md"),
      updated=None,
      relations=[
        {"type": "documents", "target": "DE-003"},
        {"type": "affects", "target": "SPEC-009"},
      ],
    )

    result = format_revision_details(artifact)

    assert "Relations:" in result
    assert "documents: DE-003" in result
    assert "affects: SPEC-009" in result

  def test_complete_revision(self) -> None:
    """Test formatting revision with all fields populated."""
    artifact = ChangeArtifact(
      id="RE-099",
      kind="revision",
      status="completed",
      name="Complete Revision",
      slug="complete-rev",
      path=Path("/repo/change/revisions/RE-099/RE-099.md"),
      updated="2024-11-01",
      applies_to={
        "specs": ["SPEC-100", "SPEC-101"],
        "requirements": ["SPEC-100.FR-001", "SPEC-101.NF-001"],
      },
      relations=[
        {"type": "documents", "target": "DE-100"},
        {"type": "affects", "target": "SPEC-100"},
      ],
    )
    root = Path("/repo")

    result = format_revision_details(artifact, root=root)

    # Verify all sections
    assert "Revision: RE-099" in result
    assert "Complete Revision" in result
    assert "completed" in result
    assert "Affects:" in result
    assert "SPEC-100" in result
    assert "Relations:" in result
    assert "File: change/revisions/RE-099/RE-099.md" in result


class TestFormatDeltaDetails(unittest.TestCase):
  """Tests for format_delta_details function."""

  def test_minimal_delta(self) -> None:
    """Test formatting delta with minimal fields."""
    artifact = ChangeArtifact(
      id="DE-001",
      kind="delta",
      status="draft",
      name="Test Delta",
      slug="test-delta",
      path=Path("/repo/change/deltas/DE-001/DE-001.md"),
      updated=None,
    )
    root = Path("/repo")

    result = format_delta_details(artifact, root=root)

    assert "Delta: DE-001" in result
    assert "Name: Test Delta" in result
    assert "Status: draft" in result
    assert "Kind: delta" in result
    assert "File: change/deltas/DE-001/DE-001.md" in result

  def test_delta_with_applies_to(self) -> None:
    """Test formatting delta with applies_to specs and requirements."""
    artifact = ChangeArtifact(
      id="DE-003",
      kind="delta",
      status="completed",
      name="Feature Implementation",
      slug="feature-impl",
      path=Path("/repo/change/deltas/DE-003/DE-003.md"),
      updated="2024-10-15",
      applies_to={
        "specs": ["SPEC-150"],
        "requirements": ["SPEC-150.FR-001", "SPEC-150.FR-002"],
      },
    )

    result = format_delta_details(artifact)

    assert "Applies To:" in result
    assert "Specs: SPEC-150" in result
    assert "Requirements:" in result
    assert "SPEC-150.FR-001" in result
    assert "SPEC-150.FR-002" in result

  def test_delta_with_plan(self) -> None:
    """Test formatting delta with plan phases."""
    artifact = ChangeArtifact(
      id="DE-003",
      kind="delta",
      status="draft",
      name="Multi-phase Delta",
      slug="multi-phase",
      path=Path("/repo/test.md"),
      updated=None,
      plan={
        "id": "IP-003",
        "phases": [
          {"phase": 0, "objective": "Foundation & Prerequisites"},
          {"phase": 1, "objective": "Core Implementation"},
          {"phase": 2, "objective": "Testing & Validation"},
        ],
      },
    )

    result = format_delta_details(artifact)

    assert "Plan: IP-003 (3 phases)" in result
    # Table format - just check objectives are present
    assert "Foundation & Prerequisites" in result
    assert "Core Implementation" in result
    assert "Testing & Validation" in result

  def test_delta_with_relations(self) -> None:
    """Test formatting delta with relations."""
    artifact = ChangeArtifact(
      id="DE-005",
      kind="delta",
      status="draft",
      name="Related Delta",
      slug="related",
      path=Path("/repo/test.md"),
      updated=None,
      relations=[
        {"type": "implements", "target": "SPEC-150"},
        {"type": "documented_by", "target": "RE-003"},
      ],
    )

    result = format_delta_details(artifact)

    assert "Relations:" in result
    assert "implements: SPEC-150" in result
    assert "documented_by: RE-003" in result

  def test_delta_without_root(self) -> None:
    """Test formatting delta without root shows absolute path."""
    artifact = ChangeArtifact(
      id="DE-001",
      kind="delta",
      status="draft",
      name="Test",
      slug="test",
      path=Path("/repo/change/deltas/DE-001/DE-001.md"),
      updated=None,
    )

    result = format_delta_details(artifact)

    assert "File: /repo/change/deltas/DE-001/DE-001.md" in result

  def test_complete_delta(self) -> None:
    """Test formatting delta with all fields populated."""
    artifact = ChangeArtifact(
      id="DE-099",
      kind="delta",
      status="completed",
      name="Complete Implementation",
      slug="complete-impl",
      path=Path("/repo/change/deltas/DE-099/DE-099.md"),
      updated="2024-11-01",
      applies_to={
        "specs": ["SPEC-100", "SPEC-101"],
        "requirements": ["SPEC-100.FR-001", "SPEC-100.FR-002", "SPEC-101.NF-001"],
      },
      plan={
        "id": "IP-099",
        "phases": [
          {"phase": 0, "objective": "Setup"},
          {"phase": 1, "objective": "Implementation"},
        ],
      },
      relations=[
        {"type": "implements", "target": "SPEC-100"},
        {"type": "documented_by", "target": "RE-010"},
      ],
    )
    root = Path("/repo")

    result = format_delta_details(artifact, root=root)

    # Verify all sections
    assert "Delta: DE-099" in result
    assert "Complete Implementation" in result
    assert "completed" in result
    assert "Applies To:" in result
    assert "SPEC-100" in result
    assert "Plan: IP-099 (2 phases)" in result
    assert "Relations:" in result
    assert "File: change/deltas/DE-099/DE-099.md" in result


class TestFormatDeltaPhasesVTPHASE003(unittest.TestCase):
  """VT-PHASE-003: Tests for phase display in delta formatter.

  Verifies PROD-006.FR-003: Enhanced delta display shows phases.
  """

  def test_delta_with_zero_phases(self) -> None:
    """Test delta with plan but no phases shows plan ID."""
    artifact = ChangeArtifact(
      id="DE-010",
      kind="delta",
      status="draft",
      name="No Phases Delta",
      slug="no-phases",
      path=Path("/repo/change/deltas/DE-010/DE-010.md"),
      updated=None,
      plan={"id": "IP-010", "phases": []},
    )

    result = format_delta_details(artifact)

    # Plan should not be shown if no phases
    assert "Plan: IP-010" not in result

  def test_delta_with_three_phases(self) -> None:
    """Test delta with 3 phases shows all with proper formatting."""
    artifact = ChangeArtifact(
      id="DE-011",
      kind="delta",
      status="draft",
      name="Three Phase Delta",
      slug="three-phase",
      path=Path("/repo/change/deltas/DE-011/DE-011.md"),
      updated=None,
      plan={
        "id": "IP-011",
        "phases": [
          {"id": "IP-011.PHASE-01", "name": "Phase 01", "objective": "First phase"},
          {"id": "IP-011.PHASE-02", "name": "Phase 02", "objective": "Second phase"},
          {"id": "IP-011.PHASE-03", "name": "Phase 03", "objective": "Third phase"},
        ],
      },
    )

    result = format_delta_details(artifact)

    assert "Plan: IP-011 (3 phases)" in result
    assert "PHASE-01" in result
    assert "PHASE-02" in result
    assert "PHASE-03" in result

  def test_delta_phase_objective_truncation(self) -> None:
    """Test that long objectives are wrapped in table display."""
    long_objective = "A" * 120  # 120 character objective
    artifact = ChangeArtifact(
      id="DE-012",
      kind="delta",
      status="draft",
      name="Long Objective Delta",
      slug="long-obj",
      path=Path("/repo/change/deltas/DE-012/DE-012.md"),
      updated=None,
      plan={
        "id": "IP-012",
        "phases": [
          {"id": "IP-012.PHASE-01", "objective": long_objective},
        ],
      },
    )

    result = format_delta_details(artifact)

    # Long objectives should be wrapped in Rich table (no ellipsis)
    assert "Plan: IP-012 (1 phases)" in result
    # Should contain the full objective (wrapped across lines)
    assert "AAAA" in result  # Part of the long objective
    # Should not contain full 120 character string
    assert "A" * 120 not in result

  def test_delta_phase_id_and_name_formatted(self) -> None:
    """Test phase ID and name are formatted correctly in output."""
    artifact = ChangeArtifact(
      id="DE-013",
      kind="delta",
      status="draft",
      name="Format Test Delta",
      slug="format-test",
      path=Path("/repo/change/deltas/DE-013/DE-013.md"),
      updated=None,
      plan={
        "id": "IP-013",
        "phases": [
          {
            "id": "IP-013.PHASE-01",
            "name": "Phase 01 - Setup",
            "objective": "Initial setup and configuration",
          },
        ],
      },
    )

    result = format_delta_details(artifact)

    # Verify phase ID appears in short format (prefix stripped)
    assert "PHASE-01" in result
    # Verify objective appears
    assert "Initial setup and configuration" in result


class FormatAuditDetailsTest(unittest.TestCase):
  """Tests for format_audit_details (VT-format-audit)."""

  def _make_audit(self, **overrides: object) -> ChangeArtifact:
    defaults: dict[str, object] = {
      "id": "AUD-001",
      "kind": "audit",
      "status": "draft",
      "name": "Audit - test audit",
      "slug": "test-audit",
      "path": Path("change/audits/AUD-001.md"),
      "updated": "2026-03-04",
      "applies_to": {},
      "relations": [],
    }
    defaults.update(overrides)
    return ChangeArtifact(**defaults)  # type: ignore[invalid-argument-type]

  def test_basic_fields(self) -> None:
    result = format_audit_details(self._make_audit())
    assert "Audit: AUD-001" in result
    assert "Name: Audit - test audit" in result
    assert "Status: draft" in result
    assert "Kind: audit" in result

  def test_with_root_shows_relative_path(self) -> None:
    root = Path("/repo")
    audit = self._make_audit(path=root / SPEC_DRIVER_DIR / AUDITS_SUBDIR / "AUD-001.md")
    result = format_audit_details(audit, root=root)
    assert ".spec-driver/audits/AUD-001.md" in result

  def test_with_relations(self) -> None:
    audit = self._make_audit(
      relations=[{"type": "audits", "target": "DE-041"}],
    )
    result = format_audit_details(audit)
    assert "audits: DE-041" in result

  def test_with_applies_to(self) -> None:
    audit = self._make_audit(
      applies_to={"specs": ["SPEC-009"], "requirements": []},
    )
    result = format_audit_details(audit)
    assert "SPEC-009" in result


class FormatPlanDetailsTest(unittest.TestCase):
  """Tests for format_plan_details (VT-format-plan)."""

  def test_basic_fields(self) -> None:
    data = {"id": "IP-041", "name": "Test Plan", "status": "draft", "kind": "plan"}
    result = format_plan_details(data)
    assert "Plan: IP-041" in result
    assert "Name: Test Plan" in result
    assert "Status: draft" in result

  def test_with_path_and_root(self) -> None:
    root = Path("/repo")
    path = root / SPEC_DRIVER_DIR / DELTAS_SUBDIR / "DE-041" / "IP-041.md"
    data = {"id": "IP-041", "name": "P", "status": "draft"}
    result = format_plan_details(data, root=root, path=path)
    assert ".spec-driver/deltas/DE-041/IP-041.md" in result

  def test_missing_fields_use_defaults(self) -> None:
    result = format_plan_details({})
    assert "Plan: unknown" in result
    assert "Status: " in result


class FormatPlanListTableTest(unittest.TestCase):
  """Tests for format_plan_list_table (VT-format-plan-list)."""

  @staticmethod
  def _plan(
    plan_id: str = "IP-041",
    name: str = "Test Plan",
    status: str = "draft",
    delta: str = "DE-041",
  ) -> dict:
    return {"id": plan_id, "name": name, "status": status, "delta_ref": delta}

  def test_table_contains_columns_and_data(self) -> None:
    plans = [self._plan(), self._plan("IP-042", "Other Plan", "complete", "DE-042")]
    result = format_plan_list_table(plans)
    assert "ID" in result
    assert "Status" in result
    assert "IP-041" in result
    assert "IP-042" in result

  def test_table_shows_delta_ref(self) -> None:
    result = format_plan_list_table([self._plan()])
    assert "DE-041" in result

  def test_table_strips_name_prefix(self) -> None:
    plan = self._plan(name="Implementation Plan - CLI completeness")
    result = format_plan_list_table([plan])
    assert "Implementation Plan - " not in result
    assert "CLI completeness" in result

  def test_json_format(self) -> None:
    plans = [self._plan()]
    result = format_plan_list_table(plans, format_type="json")
    parsed = json.loads(result)
    assert len(parsed["items"]) == 1
    assert parsed["items"][0]["id"] == "IP-041"
    assert parsed["items"][0]["status"] == "draft"

  def test_tsv_format(self) -> None:
    plans = [self._plan(), self._plan("IP-042", "Other", "complete", "DE-042")]
    result = format_plan_list_table(plans, format_type="tsv")
    lines = result.split("\n")
    assert len(lines) == 2
    assert "IP-041" in lines[0]
    assert "DE-042" in lines[1]

  def test_empty_plans(self) -> None:
    result = format_plan_list_table([])
    assert "ID" in result  # table headers still rendered

  def test_empty_plans_json(self) -> None:
    result = format_plan_list_table([], format_type="json")
    parsed = json.loads(result)
    assert parsed["items"] == []

  def test_missing_fields_use_defaults(self) -> None:
    result = format_plan_list_table([{"id": "IP-099"}])
    assert "IP-099" in result

  def test_truncate_parameter_accepted(self) -> None:
    plans = [self._plan(name="A" * 200)]
    result = format_plan_list_table(plans, truncate=True)
    assert "..." in result


class TestChangeExternalFields(unittest.TestCase):
  """Tests for ext_id/ext_url support in change formatters (VT-067-002)."""

  def _make_delta(self, **overrides: object) -> ChangeArtifact:
    defaults: dict[str, object] = {
      "id": "DE-050",
      "kind": "delta",
      "status": "draft",
      "name": "External Delta",
      "slug": "external-delta",
      "path": Path("/repo/change/deltas/DE-050/DE-050.md"),
      "updated": None,
    }
    defaults.update(overrides)
    return ChangeArtifact(**defaults)  # type: ignore[invalid-argument-type]

  def test_delta_details_with_ext_id_only(self) -> None:
    """Test delta detail shows ext_id without url."""
    artifact = self._make_delta(ext_id="JIRA-100")
    result = format_delta_details(artifact)
    assert "External: JIRA-100" in result
    assert "(" not in result.split("External:")[1].split("\n")[0]

  def test_delta_details_with_ext_id_and_url(self) -> None:
    """Test delta detail shows ext_id with url."""
    artifact = self._make_delta(
      ext_id="JIRA-100",
      ext_url="https://jira.example.com/JIRA-100",
    )
    result = format_delta_details(artifact)
    assert "External: JIRA-100 (https://jira.example.com/JIRA-100)" in result

  def test_delta_details_without_ext_id_omits_line(self) -> None:
    """Test delta detail omits External line when no ext_id."""
    artifact = self._make_delta()
    result = format_delta_details(artifact)
    assert "External:" not in result

  def test_revision_details_with_ext_id(self) -> None:
    """Test revision detail shows ext_id."""
    artifact = self._make_delta(
      id="RE-010",
      kind="revision",
      name="External Revision",
      ext_id="GH-77",
      ext_url="https://github.com/org/repo/issues/77",
    )
    result = format_revision_details(artifact)
    assert "External: GH-77 (https://github.com/org/repo/issues/77)" in result

  def test_json_includes_ext_fields(self) -> None:
    """Test JSON output includes ext_id and ext_url when present."""
    artifact = self._make_delta(
      ext_id="GH-42",
      ext_url="https://github.com/org/repo/issues/42",
    )
    result = format_change_list_json([artifact])
    data = json.loads(result)
    assert data["items"][0]["ext_id"] == "GH-42"
    assert data["items"][0]["ext_url"] == "https://github.com/org/repo/issues/42"

  def test_json_omits_ext_fields_when_empty(self) -> None:
    """Test JSON output omits ext_id/ext_url when empty."""
    artifact = self._make_delta()
    result = format_change_list_json([artifact])
    data = json.loads(result)
    assert "ext_id" not in data["items"][0]
    assert "ext_url" not in data["items"][0]

  def test_tsv_show_external_inserts_ext_id(self) -> None:
    """Test TSV includes ext_id after ID when show_external=True."""
    artifact = self._make_delta(ext_id="LIN-33")
    result = format_change_list_table(
      [artifact],
      format_type="tsv",
      show_external=True,
    )
    fields = result.strip().split("\t")
    assert fields[0] == "DE-050"
    assert fields[1] == "LIN-33"
    assert fields[2] == "draft"

  def test_tsv_no_external_omits_ext_id(self) -> None:
    """Test TSV omits ext_id when show_external=False."""
    artifact = self._make_delta(ext_id="LIN-33")
    result = format_change_list_table(
      [artifact],
      format_type="tsv",
      show_external=False,
    )
    fields = result.strip().split("\t")
    assert fields[0] == "DE-050"
    assert fields[1] == "draft"

  def test_table_show_external_includes_column(self) -> None:
    """Test table includes ExtID column when show_external=True."""
    artifact = self._make_delta(ext_id="LIN-33")
    result = format_change_list_table(
      [artifact],
      format_type="table",
      show_external=True,
    )
    assert "ExtID" in result
    assert "LIN-33" in result


class TestFormatDeltaReverseLookups(unittest.TestCase):
  """Tests for _format_delta_reverse_lookups (VT-090-P2-3)."""

  def test_no_lookups(self) -> None:
    result = _format_delta_reverse_lookups([], [])
    assert result == []

  def test_single_audit(self) -> None:
    result = _format_delta_reverse_lookups(
      [("AUD-003", "DE-081 conformance")],
      [],
    )
    text = "\n".join(result)
    assert "Audit: AUD-003 — DE-081 conformance" in text

  def test_single_revision(self) -> None:
    result = _format_delta_reverse_lookups(
      [],
      [("RE-037", "Delta DE-081 completion")],
    )
    text = "\n".join(result)
    assert "Revision: RE-037 — Delta DE-081 completion" in text

  def test_mixed(self) -> None:
    result = _format_delta_reverse_lookups(
      [("AUD-003", "Conformance audit")],
      [("RE-037", "Completion revision")],
    )
    text = "\n".join(result)
    assert "Audit: AUD-003" in text
    assert "Revision: RE-037" in text

  def test_in_format_delta_details(self) -> None:
    """Reverse lookups appear in full delta details output."""
    artifact = ChangeArtifact(
      id="DE-081",
      name="Test Delta",
      slug="test-delta",
      kind="delta",
      status="completed",
      updated="2026-03-01",
      path=Path("/repo/.spec-driver/deltas/DE-081/DE-081.md"),
    )

    result = format_delta_details(
      artifact,
      linked_audits=[("AUD-003", "Conformance audit")],
      linked_revisions=[("RE-037", "Completion")],
    )
    assert "Audit: AUD-003 — Conformance audit" in result
    assert "Revision: RE-037 — Completion" in result


if __name__ == "__main__":
  unittest.main()
