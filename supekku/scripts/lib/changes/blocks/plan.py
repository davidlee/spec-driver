"""Utilities for parsing structured plan and phase overview YAML blocks."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import yaml

if TYPE_CHECKING:
  from pathlib import Path

PLAN_MARKER = "supekku:plan.overview@v1"
PHASE_MARKER = "supekku:phase.overview@v1"


@dataclass(frozen=True)
class PlanOverviewBlock:
  """Parsed YAML block containing plan overview information."""

  raw_yaml: str
  data: dict[str, Any]


@dataclass(frozen=True)
class PhaseOverviewBlock:
  """Parsed YAML block containing phase overview information."""

  raw_yaml: str
  data: dict[str, Any]


_PLAN_PATTERN = re.compile(
  r"```(?:yaml|yml)\s+" + re.escape(PLAN_MARKER) + r"\n(.*?)```",
  re.DOTALL,
)
_PHASE_PATTERN = re.compile(
  r"```(?:yaml|yml)\s+" + re.escape(PHASE_MARKER) + r"\n(.*?)```",
  re.DOTALL,
)


def _format_yaml_error(
  error: yaml.YAMLError,
  yaml_content: str,
  source_path: Path | None,
  block_type: str,
) -> str:
  """Format a YAML error with helpful context about the file and offending content."""
  lines = yaml_content.splitlines()

  # Extract line number from error if available
  error_line = None
  if hasattr(error, "problem_mark") and error.problem_mark:
    error_line = error.problem_mark.line

  # Build error message
  parts = [f"YAML parsing error in {block_type} block"]
  if source_path:
    parts.append(f"File: {source_path}")

  parts.append(f"Error: {error}")

  # Show context around the error
  if error_line is not None and lines:
    start = max(0, error_line - 2)
    end = min(len(lines), error_line + 3)
    parts.append("\nYAML content around error:")
    for i in range(start, end):
      marker = " → " if i == error_line else "   "
      parts.append(f"{marker}{i + 1:3d} | {lines[i]}")

  return "\n".join(parts)


def extract_plan_overview(
  text: str,
  source_path: Path | None = None,
) -> PlanOverviewBlock | None:
  """Extract and parse plan overview YAML block from markdown text."""
  match = _PLAN_PATTERN.search(text)
  if not match:
    return None
  raw = match.group(1)
  try:
    data = yaml.safe_load(raw) or {}
  except yaml.YAMLError as e:
    context = _format_yaml_error(e, raw, source_path, "plan overview")
    raise ValueError(context) from e
  if not isinstance(data, dict):
    msg = "plan overview block must parse to mapping"
    raise ValueError(msg)
  return PlanOverviewBlock(raw_yaml=raw, data=data)


def extract_phase_overview(
  text: str,
  source_path: Path | None = None,
) -> PhaseOverviewBlock | None:
  """Extract and parse phase overview YAML block from markdown text."""
  match = _PHASE_PATTERN.search(text)
  if not match:
    return None
  raw = match.group(1)
  try:
    data = yaml.safe_load(raw) or {}
  except yaml.YAMLError as e:
    context = _format_yaml_error(e, raw, source_path, "phase overview")
    raise ValueError(context) from e
  if not isinstance(data, dict):
    msg = "phase overview block must parse to mapping"
    raise ValueError(msg)
  return PhaseOverviewBlock(raw_yaml=raw, data=data)


def load_plan_overview(path: Path) -> PlanOverviewBlock | None:
  """Load and parse plan overview from a markdown file."""
  return extract_plan_overview(path.read_text(encoding="utf-8"), source_path=path)


def load_phase_overview(path: Path) -> PhaseOverviewBlock | None:
  """Load and parse phase overview from a markdown file."""
  return extract_phase_overview(path.read_text(encoding="utf-8"), source_path=path)


__all__ = [
  "PHASE_MARKER",
  "PLAN_MARKER",
  "PhaseOverviewBlock",
  "PlanOverviewBlock",
  "extract_phase_overview",
  "extract_plan_overview",
  "load_phase_overview",
  "load_plan_overview",
]
