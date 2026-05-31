"""Helpers for summarizing pylint json2 output."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

SEVERITY_ORDER = {
  "fatal": 0,
  "error": 1,
  "warning": 2,
  "refactor": 3,
  "convention": 4,
  "info": 5,
}


def load_pylint_json(raw: str) -> dict[str, Any]:
  """Parse pylint json2 output.

  Args:
    raw: Raw json2 string emitted by pylint.

  Returns:
    Parsed pylint report.

  Raises:
    ValueError: If the payload is not valid pylint json2 output.
  """
  try:
    data = json.loads(raw)
  except json.JSONDecodeError as exc:
    msg = f"invalid pylint json: {exc}"
    raise ValueError(msg) from exc
  if not isinstance(data, dict):
    msg = "pylint json must be a mapping"
    raise ValueError(msg)
  if "messages" not in data or "statistics" not in data:
    msg = "pylint json missing required keys"
    raise ValueError(msg)
  return data


def summarize_pylint_report(report: dict[str, Any]) -> dict[str, Any]:
  """Summarize pylint json2 output into compact counters.

  Args:
    report: Parsed pylint json2 payload.

  Returns:
    Summary dictionary with score, message counts, and top items.
  """
  messages = report.get("messages", [])
  if not isinstance(messages, list):
    messages = []

  symbol_counts = Counter()
  path_counts = Counter()
  type_counts = Counter()

  normalized_messages: list[dict[str, Any]] = []
  for item in messages:
    if not isinstance(item, dict):
      continue
    normalized_messages.append(item)
    symbol_counts[str(item.get("symbol", "unknown"))] += 1
    path_counts[str(item.get("path", "unknown"))] += 1
    type_counts[str(item.get("type", "unknown"))] += 1

  statistics = report.get("statistics", {})
  if not isinstance(statistics, dict):
    statistics = {}
  score = statistics.get("score", 0.0)
  try:
    numeric_score = float(score)
  except (TypeError, ValueError):
    numeric_score = 0.0

  return {
    "score": numeric_score,
    "message_count": len(normalized_messages),
    "symbol_counts": symbol_counts,
    "path_counts": path_counts,
    "type_counts": type_counts,
    "messages": sorted(
      normalized_messages,
      key=lambda item: (
        SEVERITY_ORDER.get(str(item.get("type", "info")), 99),
        str(item.get("path", "")),
        int(item.get("line", 0) or 0),
        str(item.get("symbol", "")),
      ),
    ),
  }


def render_pylint_summary(
  summary: dict[str, Any],
  *,
  targets: list[str],
  json_path: Path | None,
  top_n: int = 10,
) -> str:
  """Render a compact human-readable pylint summary.

  Args:
    summary: Result from summarize_pylint_report.
    targets: Lint targets used for the run.
    json_path: Optional file where full json output was written.
    top_n: Maximum number of rows per section.

  Returns:
    Multi-line summary text.
  """
  lines = [
    f"Targets: {', '.join(targets)}",
    f"Score: {summary['score']:.2f}/10",
    f"Messages: {summary['message_count']}",
  ]
  if json_path is not None:
    lines.append(f"Full JSON: {json_path}")

  symbol_counts: Counter[str] = summary["symbol_counts"]
  if symbol_counts:
    lines.append("")
    lines.append("Top message symbols:")
    for symbol, count in symbol_counts.most_common(top_n):
      lines.append(f"  {count:>4}  {symbol}")

  path_counts: Counter[str] = summary["path_counts"]
  if path_counts:
    lines.append("")
    lines.append("Files with most messages:")
    for path, count in path_counts.most_common(top_n):
      lines.append(f"  {count:>4}  {path}")

  messages: list[dict[str, Any]] = summary["messages"]
  if messages:
    lines.append("")
    lines.append("First messages by severity:")
    for item in messages[:top_n]:
      path = str(item.get("path", "unknown"))
      line = item.get("line", 0)
      symbol = str(item.get("symbol", "unknown"))
      message = str(item.get("message", "")).strip()
      lines.append(f"  {path}:{line}  {symbol}  {message}")

  return "\n".join(lines)


__all__ = [
  "load_pylint_json",
  "render_pylint_summary",
  "summarize_pylint_report",
]
