"""Utilities for parsing structured plan and phase overview YAML blocks."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import yaml

from .yaml_utils import format_yaml_list

if TYPE_CHECKING:
  from pathlib import Path

PLAN_MARKER = "supekku:plan.overview@v1"
PLAN_SCHEMA = "supekku.plan.overview"
PLAN_VERSION = 1

PHASE_MARKER = "supekku:phase.overview@v1"
PHASE_SCHEMA = "supekku.phase.overview"
PHASE_VERSION = 1


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


class PlanOverviewValidator:
  """Validator for plan overview blocks."""

  def validate(self, block: PlanOverviewBlock) -> list[str]:
    """Validate plan overview block against schema.

    Args:
      block: Parsed plan overview block to validate.

    Returns:
      List of error messages (empty if valid).
    """
    errors: list[str] = []
    data = block.data

    # Validate schema and version
    if data.get("schema") != PLAN_SCHEMA:
      errors.append(f"plan overview block must declare schema {PLAN_SCHEMA}")
    if data.get("version") != PLAN_VERSION:
      errors.append(f"plan overview block must declare version {PLAN_VERSION}")

    # Validate plan ID (required)
    if not data.get("plan"):
      errors.append("plan overview block missing plan id")
    elif not isinstance(data.get("plan"), str):
      errors.append("plan id must be a string")

    # Validate delta ID (required)
    if not data.get("delta"):
      errors.append("plan overview block missing delta id")
    elif not isinstance(data.get("delta"), str):
      errors.append("delta id must be a string")

    # Validate revision_links (optional object with arrays)
    revision_links = data.get("revision_links")
    if revision_links is not None:
      if not isinstance(revision_links, dict):
        errors.append("revision_links must be an object")
      else:
        aligns_with = revision_links.get("aligns_with")
        if aligns_with is not None:
          if not isinstance(aligns_with, list):
            errors.append("revision_links.aligns_with must be an array")
          elif not all(isinstance(item, str) for item in aligns_with):
            errors.append("revision_links.aligns_with items must be strings")

    # Validate specs (optional object with arrays)
    specs = data.get("specs")
    if specs is not None:
      if not isinstance(specs, dict):
        errors.append("specs must be an object")
      else:
        for field_name in ["primary", "collaborators"]:
          field = specs.get(field_name)
          if field is not None:
            if not isinstance(field, list):
              errors.append(f"specs.{field_name} must be an array")
            elif not all(isinstance(item, str) for item in field):
              errors.append(f"specs.{field_name} items must be strings")

    # Validate requirements (optional object with arrays)
    requirements = data.get("requirements")
    if requirements is not None:
      if not isinstance(requirements, dict):
        errors.append("requirements must be an object")
      else:
        for field_name in ["targets", "dependencies"]:
          field = requirements.get(field_name)
          if field is not None:
            if not isinstance(field, list):
              errors.append(f"requirements.{field_name} must be an array")
            elif not all(isinstance(item, str) for item in field):
              errors.append(f"requirements.{field_name} items must be strings")

    # Validate phases (required array of objects)
    phases = data.get("phases")
    if not phases:
      errors.append("plan overview block missing phases")
    elif not isinstance(phases, list):
      errors.append("phases must be an array")
    elif len(phases) == 0:
      errors.append("phases array must not be empty")
    else:
      for idx, phase in enumerate(phases):
        if not isinstance(phase, dict):
          errors.append(f"phases[{idx}] must be an object")
          continue

        # Each phase must have an id
        if not phase.get("id"):
          errors.append(f"phases[{idx}] missing id")
        elif not isinstance(phase.get("id"), str):
          errors.append(f"phases[{idx}] id must be a string")

        # name is optional but must be string
        if "name" in phase and not isinstance(phase.get("name"), str):
          errors.append(f"phases[{idx}] name must be a string")

        # objective is optional but must be string
        if "objective" in phase and not isinstance(phase.get("objective"), str):
          errors.append(f"phases[{idx}] objective must be a string")

        # entrance_criteria and exit_criteria are optional arrays of strings
        for criteria_field in ["entrance_criteria", "exit_criteria"]:
          criteria = phase.get(criteria_field)
          if criteria is not None:
            if not isinstance(criteria, list):
              errors.append(f"phases[{idx}] {criteria_field} must be an array")
            elif not all(isinstance(item, str) for item in criteria):
              errors.append(f"phases[{idx}] {criteria_field} items must be strings")

    return errors


class PhaseOverviewValidator:
  """Validator for phase overview blocks."""

  def validate(self, block: PhaseOverviewBlock) -> list[str]:
    """Validate phase overview block against schema.

    Args:
      block: Parsed phase overview block to validate.

    Returns:
      List of error messages (empty if valid).
    """
    errors: list[str] = []
    data = block.data

    # Validate schema and version
    if data.get("schema") != PHASE_SCHEMA:
      errors.append(f"phase overview block must declare schema {PHASE_SCHEMA}")
    if data.get("version") != PHASE_VERSION:
      errors.append(f"phase overview block must declare version {PHASE_VERSION}")

    # Validate phase ID (required)
    if not data.get("phase"):
      errors.append("phase overview block missing phase id")
    elif not isinstance(data.get("phase"), str):
      errors.append("phase id must be a string")

    # Validate plan ID (required)
    if not data.get("plan"):
      errors.append("phase overview block missing plan id")
    elif not isinstance(data.get("plan"), str):
      errors.append("plan id must be a string")

    # Validate delta ID (required)
    if not data.get("delta"):
      errors.append("phase overview block missing delta id")
    elif not isinstance(data.get("delta"), str):
      errors.append("delta id must be a string")

    # Validate objective (optional but must be string)
    if "objective" in data and not isinstance(data.get("objective"), str):
      errors.append("objective must be a string")

    # Validate entrance_criteria and exit_criteria (optional arrays)
    for field_name in ["entrance_criteria", "exit_criteria", "tasks", "risks"]:
      field = data.get(field_name)
      if field is not None:
        if not isinstance(field, list):
          errors.append(f"{field_name} must be an array")
        elif not all(isinstance(item, str) for item in field):
          errors.append(f"{field_name} items must be strings")

    # Validate verification (optional object with arrays)
    verification = data.get("verification")
    if verification is not None:
      if not isinstance(verification, dict):
        errors.append("verification must be an object")
      else:
        for field_name in ["tests", "evidence"]:
          field = verification.get(field_name)
          if field is not None:
            if not isinstance(field, list):
              errors.append(f"verification.{field_name} must be an array")
            elif not all(isinstance(item, str) for item in field):
              errors.append(f"verification.{field_name} items must be strings")

    return errors


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


def render_plan_overview_block(
  plan_id: str,
  delta_id: str,
  *,
  primary_specs: list[str] | None = None,
  collaborator_specs: list[str] | None = None,
  target_requirements: list[str] | None = None,
  dependency_requirements: list[str] | None = None,
  first_phase_id: str | None = None,
  first_phase_name: str = "Phase 01 - Initial delivery",
  first_phase_objective: str = "Deliver the foundational work for this delta.",
  aligns_with_revisions: list[str] | None = None,
) -> str:
  """Render a plan overview YAML block with given values.

  This is the canonical source for the block structure. Templates and
  creation code should use this instead of hardcoding the structure.

  Args:
    plan_id: The plan ID.
    delta_id: The delta ID this plan implements.
    primary_specs: List of primary spec IDs.
    collaborator_specs: List of collaborator spec IDs.
    target_requirements: List of requirement IDs this targets.
    dependency_requirements: List of requirement IDs this depends on.
    first_phase_id: ID for the first phase (auto-generated if None).
    first_phase_name: Name for the first phase.
    first_phase_objective: Objective for the first phase.
    aligns_with_revisions: List of revision IDs this aligns with.

  Returns:
    Formatted YAML code block as string.
  """
  phase_id = first_phase_id or f"{plan_id}-P01"

  lines = [
    f"```yaml {PLAN_MARKER}",
    "schema: supekku.plan.overview",
    "version: 1",
    f"plan: {plan_id}",
    f"delta: {delta_id}",
    "revision_links:",
    format_yaml_list("aligns_with", aligns_with_revisions, level=1),
    "specs:",
    format_yaml_list("primary", primary_specs, level=1),
    format_yaml_list("collaborators", collaborator_specs, level=1),
    "requirements:",
    format_yaml_list("targets", target_requirements, level=1),
    format_yaml_list("dependencies", dependency_requirements, level=1),
    "phases:",
    f"  - id: {phase_id}",
    f"    name: {first_phase_name}",
    "    objective: >-",
    f"      {first_phase_objective}",
    "    entrance_criteria: []",
    "    exit_criteria: []",
    "```",
  ]
  return "\n".join(lines)


def render_phase_overview_block(
  phase_id: str,
  plan_id: str,
  delta_id: str,
  *,
  objective: str = "Describe the outcome for this phase.",
  entrance_criteria: list[str] | None = None,
  exit_criteria: list[str] | None = None,
  verification_tests: list[str] | None = None,
  verification_evidence: list[str] | None = None,
  tasks: list[str] | None = None,
  risks: list[str] | None = None,
) -> str:
  """Render a phase overview YAML block with given values.

  This is the canonical source for the block structure. Templates and
  creation code should use this instead of hardcoding the structure.

  Args:
    phase_id: The phase ID.
    plan_id: The plan ID this phase belongs to.
    delta_id: The delta ID this phase implements.
    objective: The phase objective.
    entrance_criteria: List of entrance criteria.
    exit_criteria: List of exit criteria.
    verification_tests: List of test IDs for verification.
    verification_evidence: List of evidence items for verification.
    tasks: List of task descriptions.
    risks: List of risk descriptions.

  Returns:
    Formatted YAML code block as string.
  """
  lines = [
    f"```yaml {PHASE_MARKER}",
    "schema: supekku.phase.overview",
    "version: 1",
    f"phase: {phase_id}",
    f"plan: {plan_id}",
    f"delta: {delta_id}",
    "objective: >-",
    f"  {objective}",
    format_yaml_list("entrance_criteria", entrance_criteria, level=0),
    format_yaml_list("exit_criteria", exit_criteria, level=0),
    "verification:",
    format_yaml_list("tests", verification_tests, level=1),
    format_yaml_list("evidence", verification_evidence, level=1),
    format_yaml_list("tasks", tasks, level=0),
    format_yaml_list("risks", risks, level=0),
    "```",
  ]
  return "\n".join(lines)


__all__ = [
  "PHASE_MARKER",
  "PHASE_SCHEMA",
  "PHASE_VERSION",
  "PLAN_MARKER",
  "PLAN_SCHEMA",
  "PLAN_VERSION",
  "PhaseOverviewBlock",
  "PhaseOverviewValidator",
  "PlanOverviewBlock",
  "PlanOverviewValidator",
  "extract_phase_overview",
  "extract_plan_overview",
  "load_phase_overview",
  "load_plan_overview",
  "render_phase_overview_block",
  "render_plan_overview_block",
]


# Register schemas
from .schema_registry import BlockSchema, register_block_schema  # noqa: E402

register_block_schema(
  "plan.overview",
  BlockSchema(
    name="plan.overview",
    marker=PLAN_MARKER,
    version=1,
    renderer=render_plan_overview_block,
    description="Defines implementation plan with phases, specs, and requirements",
  ),
)

register_block_schema(
  "phase.overview",
  BlockSchema(
    name="phase.overview",
    marker=PHASE_MARKER,
    version=1,
    renderer=render_phase_overview_block,
    description="Defines a phase within a plan with objectives, criteria, and tasks",
  ),
)
