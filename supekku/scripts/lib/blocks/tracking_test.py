"""Tests for phase tracking block extraction and parsing (VT-PHASE-007).

Validator-equivalence coverage now lives in ``tracking_metadata_test.py``
(see DE-118 IP-118-P03 C2 retirement). This file retains extraction and
integration-shape tests that exercise the parser only.
"""

from __future__ import annotations

import pytest

from .plan import (
  TRACKING_MARKER,
  TRACKING_SCHEMA,
  TRACKING_VERSION,
  PhaseTrackingBlock,
  extract_phase_tracking,
)

# Sample valid tracking block YAML
SAMPLE_VALID_TRACKING = """schema: supekku.phase.tracking
version: 1
phase: IP-004.PHASE-05
entrance_criteria:
  - item: "Phases 01, 02, 04 complete"
    completed: true
  - item: "User approval for design"
    completed: true
exit_criteria:
  - item: "Schema defined"
    completed: false
  - item: "Parser implemented"
    completed: false
tasks:
  - id: "5.1"
    description: "Define schema"
    status: pending
  - id: "5.2"
    description: "Implement parser"
    status: in_progress
  - id: "5.3"
    description: "Write tests"
    status: completed
"""


def _wrap_block(inner: str) -> str:
  """Wrap YAML content in markdown code fence with tracking marker."""
  return f"# Phase Document\n\n```yaml {TRACKING_MARKER}\n{inner}```\n\n## Content\n"


# Extraction tests


def test_extract_phase_tracking_finds_valid_block() -> None:
  """Test extracting tracking block from markdown."""
  content = _wrap_block(SAMPLE_VALID_TRACKING)
  block = extract_phase_tracking(content)
  assert block is not None
  assert isinstance(block, PhaseTrackingBlock)
  assert block.data["schema"] == TRACKING_SCHEMA
  assert block.data["version"] == TRACKING_VERSION
  assert block.data["phase"] == "IP-004.PHASE-05"


def test_extract_phase_tracking_returns_none_when_missing() -> None:
  """Test that missing tracking block returns None (backward compat)."""
  content = "# Phase\n\nSome content without tracking block.\n"
  block = extract_phase_tracking(content)
  assert block is None


def test_extract_phase_tracking_parses_criteria() -> None:
  """Test tracking block correctly parses entrance/exit criteria."""
  content = _wrap_block(SAMPLE_VALID_TRACKING)
  block = extract_phase_tracking(content)
  assert block is not None

  entrance = block.data["entrance_criteria"]
  assert len(entrance) == 2
  assert entrance[0]["item"] == "Phases 01, 02, 04 complete"
  assert entrance[0]["completed"] is True
  assert entrance[1]["completed"] is True

  exit_crit = block.data["exit_criteria"]
  assert len(exit_crit) == 2
  assert exit_crit[0]["item"] == "Schema defined"
  assert exit_crit[0]["completed"] is False


def test_extract_phase_tracking_parses_tasks() -> None:
  """Test tracking block correctly parses tasks array."""
  content = _wrap_block(SAMPLE_VALID_TRACKING)
  block = extract_phase_tracking(content)
  assert block is not None

  tasks = block.data["tasks"]
  assert len(tasks) == 3
  assert tasks[0]["id"] == "5.1"
  assert tasks[0]["description"] == "Define schema"
  assert tasks[0]["status"] == "pending"
  assert tasks[1]["status"] == "in_progress"
  assert tasks[2]["status"] == "completed"


def test_extract_phase_tracking_handles_malformed_yaml() -> None:
  """Test that malformed YAML raises ValueError with context."""
  invalid_yaml = "schema: supekku.phase.tracking\nversion: 1\nphase: [invalid"
  content = _wrap_block(invalid_yaml)

  with pytest.raises(ValueError, match="phase tracking"):
    extract_phase_tracking(content)


# Completion calculation tests (integration shape)


def test_task_completion_calculation() -> None:
  """Test calculating task completion from tracking data."""
  content = _wrap_block(SAMPLE_VALID_TRACKING)
  block = extract_phase_tracking(content)
  assert block is not None

  tasks = block.data.get("tasks", [])
  completed = sum(1 for t in tasks if t.get("status") == "completed")
  total = len(tasks)

  assert total == 3
  assert completed == 1
  assert completed / total == pytest.approx(0.333, abs=0.01)


def test_criteria_completion_calculation() -> None:
  """Test calculating criteria completion from tracking data."""
  content = _wrap_block(SAMPLE_VALID_TRACKING)
  block = extract_phase_tracking(content)
  assert block is not None

  entrance = block.data.get("entrance_criteria", [])
  entrance_completed = sum(1 for c in entrance if c.get("completed"))
  assert len(entrance) == 2
  assert entrance_completed == 2

  exit_crit = block.data.get("exit_criteria", [])
  exit_completed = sum(1 for c in exit_crit if c.get("completed"))
  assert len(exit_crit) == 2
  assert exit_completed == 0


# File path tracking — extraction-only coverage


def test_extract_phase_tracking_parses_phase_files() -> None:
  """Phase-level files dict is parsed into the data payload."""
  with_files = f"""schema: {TRACKING_SCHEMA}
version: {TRACKING_VERSION}
phase: IP-004.PHASE-05
files:
  references:
    - "supekku/scripts/lib/blocks/plan.py"
    - "specify/product/PROD-006/PROD-006.md"
  context:
    - "change/deltas/DE-002*/phases/phase-01.md"
"""
  content = _wrap_block(with_files)
  block = extract_phase_tracking(content)
  assert block is not None

  files = block.data.get("files")
  assert files is not None
  assert len(files["references"]) == 2
  assert len(files["context"]) == 1


def test_extract_phase_tracking_parses_task_files() -> None:
  """Task-level files dict is parsed into the data payload."""
  with_task_files = f"""schema: {TRACKING_SCHEMA}
version: {TRACKING_VERSION}
phase: IP-004.PHASE-05
tasks:
  - id: "5.1"
    description: "Define schema"
    status: completed
    files:
      added:
        - "supekku/scripts/lib/blocks/tracking_test.py"
      modified:
        - "supekku/scripts/lib/blocks/plan.py"
        - "supekku/templates/phase.md"
      removed: []
      tests:
        - "supekku/scripts/lib/blocks/tracking_test.py"
"""
  content = _wrap_block(with_task_files)
  block = extract_phase_tracking(content)
  assert block is not None

  tasks = block.data.get("tasks", [])
  assert len(tasks) == 1
  task_files = tasks[0].get("files")
  assert task_files is not None
  assert len(task_files["added"]) == 1
  assert len(task_files["modified"]) == 2
  assert len(task_files["removed"]) == 0
  assert len(task_files["tests"]) == 1
