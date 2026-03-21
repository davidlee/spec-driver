"""Tests for bridge block extraction and rendering (DR-102 §7)."""

from __future__ import annotations

import unittest

from supekku.scripts.lib.workflow.bridge import (
  extract_notes_bridge,
  extract_phase_bridge,
  render_notes_bridge,
  render_phase_bridge,
)


class ExtractPhaseBridgeTest(unittest.TestCase):
  """Test phase-bridge extraction from markdown."""

  def test_extracts_valid_block(self) -> None:
    text = """# Phase 05

## Workflow

```yaml supekku:workflow.phase-bridge@v1
schema: supekku.workflow.phase-bridge
version: 1
phase: IP-090.PHASE-05
status: complete
handoff_ready: true
review_required: true
```

## Notes
"""
    data = extract_phase_bridge(text)
    assert data is not None
    assert data["phase"] == "IP-090.PHASE-05"
    assert data["handoff_ready"] is True
    assert data["review_required"] is True

  def test_returns_none_when_absent(self) -> None:
    text = "# Phase 05\n\nNo bridge here.\n"
    assert extract_phase_bridge(text) is None

  def test_returns_none_on_invalid_yaml(self) -> None:
    text = """```yaml supekku:workflow.phase-bridge@v1
invalid: [yaml: {broken
```"""
    assert extract_phase_bridge(text) is None

  def test_minimal_block(self) -> None:
    text = """```yaml supekku:workflow.phase-bridge@v1
schema: supekku.workflow.phase-bridge
version: 1
phase: IP-100.PHASE-01
status: in_progress
handoff_ready: false
```"""
    data = extract_phase_bridge(text)
    assert data is not None
    assert data["handoff_ready"] is False


class ExtractNotesBridgeTest(unittest.TestCase):
  """Test notes-bridge extraction from markdown."""

  def test_extracts_valid_block(self) -> None:
    text = """# Notes

## New Agent Instructions

```yaml supekku:workflow.notes-bridge@v1
schema: supekku.workflow.notes-bridge
version: 1
artifact: DE-090
workflow_state: workflow/state.yaml
current_handoff: workflow/handoff.current.yaml
```

More content.
"""
    data = extract_notes_bridge(text)
    assert data is not None
    assert data["artifact"] == "DE-090"
    assert data["workflow_state"] == "workflow/state.yaml"

  def test_returns_none_when_absent(self) -> None:
    assert extract_notes_bridge("# Notes\n") is None


class RenderNotesBridgeTest(unittest.TestCase):
  """Test notes-bridge rendering."""

  def test_minimal_render(self) -> None:
    block = render_notes_bridge(artifact_id="DE-100")
    assert "supekku:workflow.notes-bridge@v1" in block
    assert "artifact: DE-100" in block
    assert "workflow_state: workflow/state.yaml" in block

  def test_with_optionals(self) -> None:
    block = render_notes_bridge(
      artifact_id="DE-100",
      current_handoff="workflow/handoff.current.yaml",
      review_index="workflow/review-index.yaml",
    )
    assert "current_handoff" in block
    assert "review_index" in block

  def test_roundtrip(self) -> None:
    """Rendered block can be extracted back."""
    block = render_notes_bridge(
      artifact_id="DE-100",
      current_handoff="workflow/handoff.current.yaml",
    )
    data = extract_notes_bridge(block)
    assert data is not None
    assert data["artifact"] == "DE-100"
    assert data["current_handoff"] == "workflow/handoff.current.yaml"


class RenderPhaseBridgeTest(unittest.TestCase):
  """Test phase-bridge rendering."""

  def test_minimal_render(self) -> None:
    block = render_phase_bridge(phase_id="IP-100.PHASE-01")
    assert "supekku:workflow.phase-bridge@v1" in block
    assert "phase: IP-100.PHASE-01" in block
    assert "handoff_ready: true" in block

  def test_with_review_required(self) -> None:
    block = render_phase_bridge(
      phase_id="IP-100.PHASE-01",
      review_required=True,
    )
    assert "review_required: true" in block

  def test_roundtrip(self) -> None:
    block = render_phase_bridge(
      phase_id="IP-100.PHASE-02",
      status="complete",
      handoff_ready=True,
      review_required=True,
    )
    data = extract_phase_bridge(block)
    assert data is not None
    assert data["phase"] == "IP-100.PHASE-02"
    assert data["handoff_ready"] is True
    assert data["review_required"] is True

  def test_handoff_not_ready(self) -> None:
    block = render_phase_bridge(
      phase_id="IP-100.PHASE-01",
      handoff_ready=False,
    )
    data = extract_phase_bridge(block)
    assert data is not None
    assert data["handoff_ready"] is False


if __name__ == "__main__":
  unittest.main()
