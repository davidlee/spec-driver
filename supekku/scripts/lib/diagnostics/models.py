"""Core data model for workspace health diagnostics."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

Status = Literal["pass", "warn", "fail"]

_SEVERITY_ORDER: dict[Status, int] = {"pass": 0, "warn": 1, "fail": 2}


def worst_status(statuses: list[Status]) -> Status:
  """Return the most severe status from a list.

  Returns "pass" for an empty list.
  """
  if not statuses:
    return "pass"
  return max(statuses, key=lambda s: _SEVERITY_ORDER[s])


class DiagnosticResult(BaseModel, frozen=True):
  """Single diagnostic finding within a category."""

  category: str
  name: str
  status: Status
  message: str
  suggestion: str | None = None


class CategorySummary(BaseModel, frozen=True):
  """Aggregated results for one check category."""

  category: str
  results: tuple[DiagnosticResult, ...]

  @property
  def status(self) -> Status:
    """Worst status across all results in this category."""
    return worst_status([r.status for r in self.results])


__all__ = ["CategorySummary", "DiagnosticResult", "Status", "worst_status"]
