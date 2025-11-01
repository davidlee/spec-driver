"""Utilities for parsing structured delta YAML blocks."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import yaml

from .yaml_utils import format_yaml_list

if TYPE_CHECKING:
  from pathlib import Path

RELATIONSHIPS_MARKER = "supekku:delta.relationships@v1"
RELATIONSHIPS_SCHEMA = "supekku.delta.relationships"
RELATIONSHIPS_VERSION = 1


@dataclass(frozen=True)
class DeltaRelationshipsBlock:
  """Parsed YAML block containing delta relationships."""

  raw_yaml: str
  data: dict[str, Any]


class DeltaRelationshipsValidator:
  """Validator for delta relationships blocks."""

  def validate(
    self,
    block: DeltaRelationshipsBlock,
    *,
    delta_id: str | None = None,
  ) -> list[str]:
    """Validate delta relationships block structure and content."""
    errors: list[str] = []
    data = block.data
    if data.get("schema") != RELATIONSHIPS_SCHEMA:
      errors.append(
        "delta relationships block must declare schema supekku.delta.relationships",
      )
    if data.get("version") != RELATIONSHIPS_VERSION:
      errors.append("delta relationships block must declare version 1")

    delta_value = str(data.get("delta", ""))
    if not delta_value:
      errors.append("delta relationships block missing delta id")
    elif delta_id and delta_value != delta_id:
      errors.append(
        f"delta relationships block id {delta_value} does not match "
        f"expected {delta_id}",
      )

    specs = data.get("specs")
    if specs is not None and not isinstance(specs, dict):
      errors.append("delta relationships specs must be a mapping")
    requirements = data.get("requirements")
    if requirements is not None and not isinstance(requirements, dict):
      errors.append("delta relationships requirements must be a mapping")

    for section, _expected_type in ((specs, list), (requirements, list)):
      if not isinstance(section, dict):
        continue
      for key, value in section.items():
        if value is None:
          continue
        if not isinstance(value, list):
          errors.append(f"{section}.{key} must be a list")
          continue
        for item in value:
          if not isinstance(item, str):
            errors.append(f"{section}.{key} entries must be strings")

    phases = data.get("phases")
    if phases is not None:
      if not isinstance(phases, list):
        errors.append("delta relationships phases must be a list")
      else:
        for entry in phases:
          if not isinstance(entry, dict):
            errors.append("phases entries must be objects")
            continue
          if "id" not in entry:
            errors.append("phase entry missing id")
    return errors


_BLOCK_PATTERN = re.compile(
  r"```(?:yaml|yml)\s+" + re.escape(RELATIONSHIPS_MARKER) + r"\n(.*?)```",
  re.DOTALL,
)


def extract_delta_relationships(text: str) -> DeltaRelationshipsBlock | None:
  """Extract delta relationships block from markdown text."""
  match = _BLOCK_PATTERN.search(text)
  if not match:
    return None
  raw = match.group(1)
  try:
    data = yaml.safe_load(raw) or {}
  except yaml.YAMLError as exc:  # pragma: no cover
    msg = f"invalid delta relationships YAML: {exc}"
    raise ValueError(msg) from exc
  if not isinstance(data, dict):
    msg = "delta relationships block must parse to mapping"
    raise ValueError(msg)
  return DeltaRelationshipsBlock(raw_yaml=raw, data=data)


def load_delta_relationships(path: Path) -> DeltaRelationshipsBlock | None:
  """Load and extract delta relationships block from file."""
  text = path.read_text(encoding="utf-8")
  return extract_delta_relationships(text)


def render_delta_relationships_block(
  delta_id: str,
  *,
  primary_specs: list[str] | None = None,
  collaborator_specs: list[str] | None = None,
  implements_requirements: list[str] | None = None,
  updates_requirements: list[str] | None = None,
  verifies_requirements: list[str] | None = None,
  phases: list[str] | None = None,
  introduces_revisions: list[str] | None = None,
  supersedes_revisions: list[str] | None = None,
) -> str:
  """Render a delta relationships YAML block with given values.

  This is the canonical source for the block structure. Templates and
  creation code should use this instead of hardcoding the structure.

  Args:
    delta_id: The delta ID.
    primary_specs: List of primary spec IDs.
    collaborator_specs: List of collaborator spec IDs.
    implements_requirements: List of requirement IDs this implements.
    updates_requirements: List of requirement IDs this updates.
    verifies_requirements: List of requirement IDs this verifies.
    phases: List of phase IDs.
    introduces_revisions: List of revision IDs this introduces.
    supersedes_revisions: List of revision IDs this supersedes.

  Returns:
    Formatted YAML code block as string.
  """
  lines = [
    f"```yaml {RELATIONSHIPS_MARKER}",
    f"schema: {RELATIONSHIPS_SCHEMA}",
    f"version: {RELATIONSHIPS_VERSION}",
    f"delta: {delta_id}",
    "revision_links:",
    format_yaml_list("introduces", introduces_revisions, level=1),
    format_yaml_list("supersedes", supersedes_revisions, level=1),
    "specs:",
    format_yaml_list("primary", primary_specs, level=1),
    format_yaml_list("collaborators", collaborator_specs, level=1),
    "requirements:",
    format_yaml_list("implements", implements_requirements, level=1),
    format_yaml_list("updates", updates_requirements, level=1),
    format_yaml_list("verifies", verifies_requirements, level=1),
    format_yaml_list("phases", phases, level=0),
    "```",
  ]
  return "\n".join(lines)


__all__ = [
  "RELATIONSHIPS_MARKER",
  "DeltaRelationshipsBlock",
  "DeltaRelationshipsValidator",
  "extract_delta_relationships",
  "load_delta_relationships",
  "render_delta_relationships_block",
]
