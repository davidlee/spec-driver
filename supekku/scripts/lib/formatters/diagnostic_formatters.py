"""Pure formatting functions for workspace diagnostic output."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from supekku.scripts.lib.diagnostics.models import worst_status
from supekku.scripts.lib.diagnostics.runner import EXIT_CODES

if TYPE_CHECKING:
  from supekku.scripts.lib.diagnostics.models import CategorySummary

_RESET = "\033[0m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_RED = "\033[31m"
_BOLD = "\033[1m"
_DIM = "\033[2m"

_PLAIN_SYMBOLS: dict[str, str] = {
  "pass": "\u2713",  # ✓
  "warn": "\u26a0",  # ⚠
  "fail": "\u2717",  # ✗
}

_COLOR_SYMBOLS: dict[str, str] = {
  "pass": f"{_GREEN}\u2713{_RESET}",
  "warn": f"{_YELLOW}\u26a0{_RESET}",
  "fail": f"{_RED}\u2717{_RESET}",
}

_STATUS_COLOURS: dict[str, str] = {
  "pass": _GREEN,
  "warn": _YELLOW,
  "fail": _RED,
}


def format_doctor_text(
  summaries: list[CategorySummary],
  *,
  verbose: bool = False,
  color: bool = True,
) -> str:
  """Format diagnostic summaries as human-readable text.

  Args:
    summaries: Category summaries from the runner.
    verbose: If True, include passing results. Default hides them.
    color: If True, use ANSI colour codes. Default True.

  Returns:
    Formatted multi-line string.
  """
  lines: list[str] = [
    f"{_BOLD}spec-driver doctor{_RESET}" if color else "spec-driver doctor",
    "=" * 18,
    "",
  ]

  for summary in summaries:
    lines.append(f"{_BOLD}{summary.category}{_RESET}" if color else summary.category)
    for result in summary.results:
      if result.status == "pass" and not verbose:
        continue
      symbol = _COLOR_SYMBOLS[result.status] if color else _PLAIN_SYMBOLS[result.status]
      colour = _STATUS_COLOURS[result.status] if color else ""
      reset = _RESET if color else ""
      lines.append(f"  {symbol} {colour}{result.name}{reset} \u2014 {result.message}")
      if result.suggestion:
        dim = _DIM if color else ""
        lines.append(f"    \u2192 {dim}{result.suggestion}{reset}")

    if all(r.status == "pass" for r in summary.results) and not verbose:
      dim = _DIM if color else ""
      reset = _RESET if color else ""
      lines.append(f"  {dim}all checks passed{reset}")
    lines.append("")

  counts = _count_statuses(summaries)
  lines.append(_format_summary_line(counts, color=color))
  return "\n".join(lines)


def _format_summary_line(counts: dict[str, int], *, color: bool = True) -> str:
  """Format the summary counts line with optional colour."""
  if not color:
    return (
      f"Summary: {counts['pass']} pass, {counts['warn']} warn, {counts['fail']} fail"
    )
  parts = [
    f"{_GREEN}{counts['pass']} pass{_RESET}",
    f"{_YELLOW}{counts['warn']} warn{_RESET}",
    f"{_RED}{counts['fail']} fail{_RESET}",
  ]
  return f"Summary: {', '.join(parts)}"


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
    "exit_code": EXIT_CODES[worst_status([s.status for s in summaries])],
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
