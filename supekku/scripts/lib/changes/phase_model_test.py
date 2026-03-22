"""Tests for PhaseSheet Pydantic model."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import frontmatter

from supekku.scripts.lib.changes.phase_model import PhaseSheet


class TestPhaseSheetModel:
  """Core model validation tests."""

  def test_full_new_format(self) -> None:
    """New-format phase with all canonical fields."""
    sheet = PhaseSheet(
      plan="IP-106",
      delta="DE-106",
      objective="Wire frontmatter-first phase loading",
      entrance_criteria=["DR-106 approved", "Tests passing"],
      exit_criteria=["show delta works", "Legacy compat"],
    )
    assert sheet.has_canonical_fields()
    assert sheet.plan == "IP-106"
    assert sheet.delta == "DE-106"
    assert sheet.objective == "Wire frontmatter-first phase loading"
    assert sheet.entrance_criteria == ["DR-106 approved", "Tests passing"]
    assert sheet.exit_criteria == ["show delta works", "Legacy compat"]

  def test_minimal_new_format(self) -> None:
    """New-format phase with only required canonical fields."""
    sheet = PhaseSheet(plan="IP-106", delta="DE-106")
    assert sheet.has_canonical_fields()
    assert sheet.objective is None
    assert sheet.entrance_criteria is None
    assert sheet.exit_criteria is None

  def test_legacy_format_no_canonical_fields(self) -> None:
    """Legacy phase with no plan/delta in frontmatter."""
    sheet = PhaseSheet()
    assert not sheet.has_canonical_fields()

  def test_extra_fields_ignored(self) -> None:
    """Extra frontmatter fields are silently ignored."""
    sheet = PhaseSheet(
      plan="IP-106",
      delta="DE-106",
      id="IP-106.PHASE-01",  # type: ignore[call-arg]
      status="draft",  # type: ignore[call-arg]
      kind="phase",  # type: ignore[call-arg]
      slug="some-slug",  # type: ignore[call-arg]
    )
    assert sheet.has_canonical_fields()
    assert sheet.plan == "IP-106"

  def test_to_phase_entry_full(self) -> None:
    """to_phase_entry includes all present fields."""
    sheet = PhaseSheet(
      plan="IP-106",
      delta="DE-106",
      objective="Test objective",
      entrance_criteria=["criterion-1"],
      exit_criteria=["criterion-2"],
    )
    entry = sheet.to_phase_entry()
    assert entry == {
      "plan": "IP-106",
      "delta": "DE-106",
      "objective": "Test objective",
      "entrance_criteria": ["criterion-1"],
      "exit_criteria": ["criterion-2"],
    }

  def test_to_phase_entry_minimal(self) -> None:
    """to_phase_entry omits None fields."""
    sheet = PhaseSheet(plan="IP-106", delta="DE-106")
    entry = sheet.to_phase_entry()
    assert entry == {"plan": "IP-106", "delta": "DE-106"}
    assert "objective" not in entry
    assert "entrance_criteria" not in entry

  def test_to_phase_entry_empty(self) -> None:
    """to_phase_entry returns empty dict for legacy phases."""
    sheet = PhaseSheet()
    entry = sheet.to_phase_entry()
    assert entry == {}


class TestPhaseSheetCorpus:
  """Test model against real phase files in the workspace."""

  @staticmethod
  def _find_phase_files() -> list[Path]:
    """Find all phase files in .spec-driver/deltas/."""
    root = Path(".spec-driver/deltas")
    if not root.exists():
      return []
    return sorted(root.glob("*/phases/phase-*.md"))

  def test_all_existing_phases_parse(self) -> None:
    """Every existing phase file's frontmatter parses through PhaseSheet.

    Legacy phases (no plan/delta in frontmatter) should parse with
    has_canonical_fields() == False. This proves backward compatibility.
    """
    phase_files = self._find_phase_files()
    assert phase_files, "Expected at least one phase file in .spec-driver/deltas/"

    for phase_file in phase_files:
      fm = frontmatter.load(str(phase_file))
      # Should never raise — extra='ignore' handles unknown fields
      sheet = PhaseSheet(**fm.metadata)  # type: ignore[invalid-argument-type]
      # Just verify it parsed without error; canonical fields may or may not exist
      assert isinstance(sheet, PhaseSheet), f"Failed to parse {phase_file}"

  def test_date_handling(self) -> None:
    """PyYAML auto-parses dates; Pydantic extra='ignore' handles them."""
    # Simulate what python-frontmatter gives us: dates as date objects
    sheet = PhaseSheet(
      plan="IP-106",
      delta="DE-106",
      created=date(2026, 3, 21),  # type: ignore[call-arg]
      updated=date(2026, 3, 21),  # type: ignore[call-arg]
    )
    assert sheet.has_canonical_fields()
