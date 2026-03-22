"""Diagnostic check runner — orchestrates check categories."""

from __future__ import annotations

from .checks import CHECK_REGISTRY
from .models import CategorySummary, DiagnosticWorkspace, worst_status

# Exit codes mapped from worst overall status
EXIT_CODES: dict[str, int] = {"pass": 0, "warn": 1, "fail": 2}


def run_checks(
  ws: DiagnosticWorkspace, *, categories: list[str] | None = None
) -> list[CategorySummary]:
  """Run diagnostic checks and return category summaries.

  Args:
    ws: Workspace to diagnose.
    categories: Optional list of category names to run. None runs all.

  Returns:
    List of CategorySummary, one per category run.

  Raises:
    ValueError: If a requested category is not in the registry.
  """
  registry = CHECK_REGISTRY
  if categories is not None:
    unknown = set(categories) - set(registry)
    if unknown:
      msg = f"Unknown check categories: {', '.join(sorted(unknown))}"
      raise ValueError(msg)
    registry = {k: v for k, v in registry.items() if k in categories}

  summaries: list[CategorySummary] = []
  for category_name, check_fn in registry.items():
    results = check_fn(ws)
    summaries.append(CategorySummary(category=category_name, results=tuple(results)))
  return summaries


def overall_exit_code(summaries: list[CategorySummary]) -> int:
  """Compute exit code from worst status across all summaries."""
  statuses = [s.status for s in summaries]
  return EXIT_CODES[worst_status(statuses)]


__all__ = ["EXIT_CODES", "overall_exit_code", "run_checks"]
