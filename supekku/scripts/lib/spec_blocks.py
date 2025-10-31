"""Utilities for parsing structured spec YAML blocks."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import yaml

if TYPE_CHECKING:
  from pathlib import Path

RELATIONSHIPS_MARKER = "supekku:spec.relationships@v1"
RELATIONSHIPS_SCHEMA = "supekku.spec.relationships"
RELATIONSHIPS_VERSION = 1


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


__all__ = [
  "RELATIONSHIPS_MARKER",
  "RelationshipsBlock",
  "RelationshipsBlockValidator",
  "extract_relationships",
  "load_relationships_from_file",
]
