"""Tests for plan and phase block rendering."""

from __future__ import annotations

from supekku.scripts.lib.blocks.plan import (
  render_phase_overview_block,
  render_plan_overview_block,
)


def test_render_plan_overview_block_minimal() -> None:
  """Test rendering plan overview block with minimal data."""
  result = render_plan_overview_block("IP-001", "DE-001")

  assert "```yaml supekku:plan.overview@v1" in result
  assert "schema: supekku.plan.overview" in result
  assert "version: 1" in result
  assert "plan: IP-001" in result
  assert "delta: DE-001" in result
  assert "specs:" in result
  assert "requirements:" in result
  assert "phases:" in result


def test_render_plan_overview_block_with_specs_and_requirements() -> None:
  """Test rendering plan overview block with specs and requirements."""
  result = render_plan_overview_block(
    "IP-001",
    "DE-001",
    primary_specs=["SPEC-100", "SPEC-200"],
    target_requirements=["SPEC-100.FR-001"],
  )

  assert "primary:" in result
  assert "- SPEC-100" in result
  assert "- SPEC-200" in result
  assert "targets:" in result
  assert "- SPEC-100.FR-001" in result


def test_render_plan_overview_block_with_custom_phase() -> None:
  """Test rendering plan overview block with custom first phase."""
  result = render_plan_overview_block(
    "IP-001",
    "DE-001",
    first_phase_id="IP-001.PHASE-CUSTOM",
    first_phase_name="Custom Phase",
    first_phase_objective="Custom objective",
  )

  assert "id: IP-001.PHASE-CUSTOM" in result
  assert "name: Custom Phase" in result
  assert "Custom objective" in result


def test_render_phase_overview_block_minimal() -> None:
  """Test rendering phase overview block with minimal data."""
  result = render_phase_overview_block("IP-001.PHASE-01", "IP-001", "DE-001")

  assert "```yaml supekku:phase.overview@v1" in result
  assert "schema: supekku.phase.overview" in result
  assert "version: 1" in result
  assert "phase: IP-001.PHASE-01" in result
  assert "plan: IP-001" in result
  assert "delta: DE-001" in result
  assert "objective:" in result
  assert "verification:" in result


def test_render_phase_overview_block_with_custom_data() -> None:
  """Test rendering phase overview block with custom data."""
  result = render_phase_overview_block(
    "IP-001.PHASE-01",
    "IP-001",
    "DE-001",
    objective="Complete implementation",
    entrance_criteria=["Design approved"],
    exit_criteria=["Tests passing"],
    verification_tests=["VT-001"],
    verification_evidence=["Test report"],
    tasks=["Task 1", "Task 2"],
    risks=["Risk 1"],
  )

  assert "Complete implementation" in result
  assert "entrance_criteria:" in result
  assert "- Design approved" in result
  assert "exit_criteria:" in result
  assert "- Tests passing" in result
  assert "tests:" in result
  assert "- VT-001" in result
  assert "evidence:" in result
  assert "- Test report" in result
  assert "tasks:" in result
  assert "- Task 1" in result
  assert "risks:" in result
  assert "- Risk 1" in result
