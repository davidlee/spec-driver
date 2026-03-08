"""Pure formatting functions for workspace diagnostic output."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from supekku.scripts.lib.diagnostics.models import worst_status
from supekku.scripts.lib.diagnostics.runner import EXIT_CODES

if TYPE_CHECKING:
  from supekku.scripts.lib.diagnostics.models import CategorySummary

_STATUS_SYMBOLS: dict[str, str] = {
  "pass": "\u2713",  # ✓
  "warn": "\u26a0",  # ⚠
  "fail": "\u2717",  # ✗
}


def format_doctor_text(
  summaries: list[CategorySummary], *, verbose: bool = False
) -> str:
  """Format diagnostic summaries as human-readable text.

  Args:
    summaries: Category summaries from the runner.
    verbose: If True, include passing results. Default hides them.

  Returns:
    Formatted multi-line string.
  """
  lines: list[str] = ["spec-driver doctor", "=" * 18, ""]

  for summary in summaries:
    lines.append(summary.category)
    for result in summary.results:
      if result.status == "pass" and not verbose:
        continue
      symbol = _STATUS_SYMBOLS[result.status]
      lines.append(f"  {symbol} {result.name} \u2014 {result.message}")
      if result.suggestion:
        lines.append(f"    \u2192 {result.suggestion}")

    if all(r.status == "pass" for r in summary.results) and not verbose:
      lines.append("  all checks passed")
    lines.append("")

  counts = _count_statuses(summaries)
  lines.append(
    f"Summary: {counts['pass']} pass, "
    f"{counts['warn']} warn, {counts['fail']} fail"
  )
  return "\n".join(lines)


def format_doctor_json(summaries: list[CategorySummary]) -> str:
  """Format diagnostic summaries as JSON.

  Returns:
    JSON string with categories, results, and summary.
  """
  counts = _count_statuses(summaries)
  data = {
    "categories": [
      {
        "category": s.category,
        "status": s.status,
        "results": [
          {
            "name": r.name,
            "status": r.status,
            "message": r.message,
            "suggestion": r.suggestion,
          }
          for r in s.results
        ],
      }
      for s in summaries
    ],
    "summary": counts,
    "exit_code": EXIT_CODES[
      worst_status([s.status for s in summaries])
    ],
  }
  return json.dumps(data, indent=2)


def _count_statuses(
  summaries: list[CategorySummary],
) -> dict[str, int]:
  """Count total results by status across all categories."""
  counts = {"pass": 0, "warn": 0, "fail": 0}
  for summary in summaries:
    for result in summary.results:
      counts[result.status] += 1
  return counts


__all__ = ["format_doctor_json", "format_doctor_text"]
