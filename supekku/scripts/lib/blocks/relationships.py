"""Utilities for parsing structured spec YAML blocks."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import yaml

from .yaml_utils import format_yaml_list

if TYPE_CHECKING:
  from pathlib import Path

RELATIONSHIPS_MARKER = "supekku:spec.relationships@v1"
RELATIONSHIPS_SCHEMA = "supekku.spec.relationships"
RELATIONSHIPS_VERSION = 1

CAPABILITIES_MARKER = "supekku:spec.capabilities@v1"
CAPABILITIES_SCHEMA = "supekku.spec.capabilities"
CAPABILITIES_VERSION = 1


@dataclass(frozen=True)
class RelationshipsBlock:
  """Parsed YAML block containing specification relationships."""

  raw_yaml: str
  data: dict[str, Any]


class RelationshipsBlockValidator:
  """Validator for specification relationships blocks."""

  def validate(
    self,
    block: RelationshipsBlock,
    *,
    spec_id: str | None = None,
  ) -> list[str]:
    """Validate relationships block against schema.

    Args:
      block: Parsed relationships block to validate.
      spec_id: Optional expected spec ID to match against.

    Returns:
      List of error messages (empty if valid).
    """
    errors: list[str] = []
    data = block.data
    if data.get("schema") != RELATIONSHIPS_SCHEMA:
      errors.append(
        "relationships block must declare schema supekku.spec.relationships",
      )
    if data.get("version") != RELATIONSHIPS_VERSION:
      errors.append("relationships block must declare version 1")

    spec_value = str(data.get("spec", ""))
    if not spec_value:
      errors.append("relationships block missing spec id")
    elif spec_id and spec_value != spec_id:
      errors.append(
        f"relationships block spec {spec_value} does not match expected {spec_id}",
      )

    requirements = data.get("requirements")
    if not isinstance(requirements, dict):
      errors.append("relationships requirements must be a mapping")
    else:
      for key in ("primary", "collaborators"):
        value = requirements.get(key)
        if value is None:
          continue
        if not isinstance(value, list):
          errors.append(f"requirements.{key} must be a list")
          continue
        for item in value:
          if not isinstance(item, str):
            errors.append(f"requirements.{key} entries must be strings")

    interactions = data.get("interactions")
    if interactions is not None:
      if not isinstance(interactions, list):
        errors.append("interactions must be a list")
      else:
        for entry in interactions:
          if not isinstance(entry, dict):
            errors.append("interaction entries must be objects")
            continue
          if "type" not in entry:
            errors.append("interaction missing type")
          if "spec" not in entry:
            errors.append("interaction missing spec")
    return errors


_RELATIONSHIPS_PATTERN = re.compile(
  r"```(?:yaml|yml)\s+" + re.escape(RELATIONSHIPS_MARKER) + r"\n(.*?)```",
  re.DOTALL,
)


def extract_relationships(block: str) -> RelationshipsBlock | None:
  """Extract and parse relationships block from markdown content.

  Args:
    block: Markdown content containing relationships block.

  Returns:
    Parsed RelationshipsBlock or None if not found.

  Raises:
    ValueError: If YAML is invalid or doesn't parse to a mapping.
  """
  match = _RELATIONSHIPS_PATTERN.search(block)
  if not match:
    return None
  raw = match.group(1)
  try:
    data = yaml.safe_load(raw) or {}
  except yaml.YAMLError as exc:  # pragma: no cover
    msg = f"invalid relationships YAML: {exc}"
    raise ValueError(msg) from exc
  if not isinstance(data, dict):
    msg = "relationships block must parse to mapping"
    raise ValueError(msg)
  return RelationshipsBlock(raw_yaml=raw, data=data)


def load_relationships_from_file(path: Path) -> RelationshipsBlock | None:
  """Load and extract relationships block from file.

  Args:
    path: Path to markdown file.

  Returns:
    Parsed RelationshipsBlock or None if not found.
  """
  text = path.read_text(encoding="utf-8")
  return extract_relationships(text)


def render_spec_relationships_block(
  spec_id: str,
  *,
  primary_requirements: list[str] | None = None,
  collaborator_requirements: list[str] | None = None,
  interactions: list[dict[str, str]] | None = None,
) -> str:
  """Render a spec relationships YAML block with given values.

  This is the canonical source for the block structure. Templates and
  creation code should use this instead of hardcoding the structure.

  Args:
    spec_id: The specification ID.
    primary_requirements: List of primary requirement codes
      (e.g., ["FR-001", "FR-002"]).
    collaborator_requirements: List of collaborator requirement codes.
    interactions: List of interaction dicts with 'type' and 'spec' keys.

  Returns:
    Formatted YAML code block as string.
  """
  lines = [
    f"```yaml {RELATIONSHIPS_MARKER}",
    f"schema: {RELATIONSHIPS_SCHEMA}",
    f"version: {RELATIONSHIPS_VERSION}",
    f"spec: {spec_id}",
    "requirements:",
    format_yaml_list("primary", primary_requirements, level=1),
    format_yaml_list("collaborators", collaborator_requirements, level=1),
  ]

  # Add interactions
  if not interactions:
    lines.append("interactions: []")
  else:
    lines.append("interactions:")
    for interaction in interactions:
      lines.append(f"  - type: {interaction['type']}")
      lines.append(f"    spec: {interaction['spec']}")
      if "notes" in interaction:
        lines.append(f"    notes: {interaction['notes']}")

  lines.append("```")
  return "\n".join(lines)


def render_spec_capabilities_block(
  spec_id: str,
  *,
  capabilities: list[dict[str, Any]] | None = None,
) -> str:
  """Render a spec capabilities YAML block with given values.

  This is the canonical source for the block structure. Templates and
  creation code should use this instead of hardcoding the structure.

  Args:
    spec_id: The specification ID.
    capabilities: List of capability dicts with:
      - id: str (kebab-case identifier)
      - name: str (human-readable name)
      - responsibilities: list[str] | None
      - requirements: list[str] | None
      - summary: str
      - success_criteria: list[str] | None

  Returns:
    Formatted YAML code block as string.
  """
  lines = [
    f"```yaml {CAPABILITIES_MARKER}",
    f"schema: {CAPABILITIES_SCHEMA}",
    f"version: {CAPABILITIES_VERSION}",
    f"spec: {spec_id}",
  ]

  # Add capabilities
  if not capabilities:
    lines.append("capabilities: []")
  else:
    lines.append("capabilities:")
    for cap in capabilities:
      lines.append(f"  - id: {cap['id']}")
      lines.append(f"    name: {cap['name']}")

      # Responsibilities
      responsibilities = cap.get("responsibilities", [])
      if not responsibilities:
        lines.append("    responsibilities: []")
      else:
        lines.append("    responsibilities:")
        for resp in responsibilities:
          lines.append(f"      - {resp}")

      # Requirements
      requirements = cap.get("requirements", [])
      if not requirements:
        lines.append("    requirements: []")
      else:
        lines.append("    requirements:")
        for req in requirements:
          lines.append(f"      - {req}")

      # Summary (use folded scalar >- for multi-line)
      summary = cap.get("summary", "")
      if summary:
        lines.append("    summary: >-")
        for summary_line in summary.strip().splitlines():
          lines.append(f"      {summary_line}")

      # Success criteria
      success_criteria = cap.get("success_criteria", [])
      if not success_criteria:
        lines.append("    success_criteria: []")
      else:
        lines.append("    success_criteria:")
        for criterion in success_criteria:
          lines.append(f"      - {criterion}")

  lines.append("```")
  return "\n".join(lines)


__all__ = [
  "CAPABILITIES_MARKER",
  "CAPABILITIES_SCHEMA",
  "CAPABILITIES_VERSION",
  "RELATIONSHIPS_MARKER",
  "RELATIONSHIPS_SCHEMA",
  "RELATIONSHIPS_VERSION",
  "RelationshipsBlock",
  "RelationshipsBlockValidator",
  "extract_relationships",
  "load_relationships_from_file",
  "render_spec_capabilities_block",
  "render_spec_relationships_block",
]


# Register schemas
from .schema_registry import BlockSchema, register_block_schema  # noqa: E402

register_block_schema(
  "spec.relationships",
  BlockSchema(
    name="spec.relationships",
    marker=RELATIONSHIPS_MARKER,
    version=RELATIONSHIPS_VERSION,
    renderer=render_spec_relationships_block,
    description="Defines spec relationships to requirements and other specs",
  ),
)

register_block_schema(
  "spec.capabilities",
  BlockSchema(
    name="spec.capabilities",
    marker=CAPABILITIES_MARKER,
    version=CAPABILITIES_VERSION,
    renderer=render_spec_capabilities_block,
    description="Defines spec capabilities with responsibilities and success criteria",
  ),
)
