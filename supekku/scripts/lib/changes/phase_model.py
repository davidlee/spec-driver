"""Pydantic model for canonical phase frontmatter.

Defines the structured fields that phase frontmatter must/may carry.
This is the single source of truth for phase metadata validation —
replaces the previous triple-entry across phase.overview blocks,
phase.tracking blocks, and markdown body sections.

See DR-106 §3a for field analysis and placement rationale.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class PhaseSheet(BaseModel):
  """Canonical phase frontmatter fields beyond base artifact metadata.

  These fields represent the planning contract for a phase. Execution
  progress (whether criteria are met) is tracked in markdown body
  checkboxes, not in structured data.

  Fields:
    plan: Owning plan ID (e.g., "IP-106"). Written once by create_phase.
    delta: Owning delta ID (e.g., "DE-106"). Written once by create_phase.
    objective: Qualitative goal for the phase. Written during planning.
    entrance_criteria: Conditions that must be met before starting.
    exit_criteria: Conditions that must be met to complete.
  """

  model_config = ConfigDict(extra="ignore")

  plan: str | None = None
  delta: str | None = None
  objective: str | None = None
  entrance_criteria: list[str] | None = None
  exit_criteria: list[str] | None = None

  def has_canonical_fields(self) -> bool:
    """Return True if this phase has the canonical frontmatter fields.

    Used for compatibility: if plan and delta are present, this is a
    new-format phase and frontmatter is authoritative. If absent, fall
    back to phase.overview block extraction.
    """
    return self.plan is not None and self.delta is not None

  def to_phase_entry(self) -> dict[str, object]:
    """Convert to the dict shape expected by artifact loading.

    Returns a dict compatible with the phase entries that artifacts.py
    builds from phase.overview blocks, so downstream consumers (show
    delta, list_changes) work unchanged.
    """
    entry: dict[str, object] = {}
    if self.plan is not None:
      entry["plan"] = self.plan
    if self.delta is not None:
      entry["delta"] = self.delta
    if self.objective is not None:
      entry["objective"] = self.objective
    if self.entrance_criteria is not None:
      entry["entrance_criteria"] = self.entrance_criteria
    if self.exit_criteria is not None:
      entry["exit_criteria"] = self.exit_criteria
    return entry


__all__ = ["PhaseSheet"]
