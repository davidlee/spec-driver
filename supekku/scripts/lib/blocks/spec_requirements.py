"""Block parser for supekku:spec.requirements@v1 YAML blocks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import yaml

from supekku.scripts.lib.blocks.yaml_utils import make_block_pattern

if TYPE_CHECKING:
  from pathlib import Path

REQUIREMENTS_MARKER = "supekku:spec.requirements@v1"
REQUIREMENTS_SCHEMA = "supekku.spec.requirements"
REQUIREMENTS_VERSION = 1


@dataclass(frozen=True)
class SpecRequirementsBlock:
  """Parsed YAML block containing spec requirements."""

  raw_yaml: str
  data: dict[str, Any]


_REQUIREMENTS_PATTERN = make_block_pattern(REQUIREMENTS_MARKER)


def extract_spec_requirements(text: str) -> SpecRequirementsBlock | None:
  """Extract a single spec requirements block from markdown content.

  Returns None if no block found. Raises ValueError on malformed YAML
  or if multiple blocks are present (DEC-140-15).
  """
  matches = list(_REQUIREMENTS_PATTERN.finditer(text))
  if not matches:
    return None
  if len(matches) > 1:
    msg = "multiple spec.requirements blocks found; exactly one is allowed"
    raise ValueError(msg)
  raw = matches[0].group(1)
  try:
    data = yaml.safe_load(raw) or {}
  except yaml.YAMLError as exc:
    msg = f"invalid spec requirements YAML: {exc}"
    raise ValueError(msg) from exc
  if not isinstance(data, dict):
    msg = "spec requirements block must parse to mapping"
    raise ValueError(msg)
  return SpecRequirementsBlock(raw_yaml=raw, data=data)


def load_spec_requirements(path: Path) -> SpecRequirementsBlock | None:
  """Load and extract a spec requirements block from file."""
  text = path.read_text(encoding="utf-8")
  return extract_spec_requirements(text)


def render_spec_requirements_block(
  spec_id: str,
  *,
  requirements: list[dict[str, Any]] | None = None,
) -> str:
  """Render a spec requirements YAML block.

  Args:
    spec_id: Owning spec/product ID (e.g. "PROD-004").
    requirements: List of requirement entry dicts. Each entry may have:
      id, title, lifecycle, kind, category, description,
      acceptance_criteria, tags.
  """
  lines = [
    f"```yaml {REQUIREMENTS_MARKER}",
    f"schema: {REQUIREMENTS_SCHEMA}",
    f"version: {REQUIREMENTS_VERSION}",
    f"spec: {spec_id}",
    "requirements:",
  ]

  if not requirements:
    lines[-1] = "requirements: []"
  else:
    for entry in requirements:
      lines.append(f"  - id: {entry['id']}")
      lines.append(f"    title: {entry['title']}")
      lines.append(f"    lifecycle: {entry.get('lifecycle', 'pending')}")
      lines.append(f"    kind: {entry['kind']}")
      if "category" in entry and entry["category"]:
        lines.append(f"    category: {entry['category']}")
      desc = entry.get("description", "")
      if desc:
        lines.append("    description: |")
        for desc_line in desc.rstrip().splitlines():
          lines.append(f"      {desc_line}")
      else:
        lines.append('    description: ""')
      criteria = entry.get("acceptance_criteria", [])
      if criteria:
        lines.append("    acceptance_criteria:")
        for criterion in criteria:
          lines.append(f"      - {criterion}")
      else:
        lines.append("    acceptance_criteria: []")
      tags = entry.get("tags", [])
      if tags:
        tag_str = ", ".join(tags)
        lines.append(f"    tags: [{tag_str}]")

  lines.append("```")
  return "\n".join(lines)


__all__ = [
  "REQUIREMENTS_MARKER",
  "REQUIREMENTS_SCHEMA",
  "REQUIREMENTS_VERSION",
  "SpecRequirementsBlock",
  "extract_spec_requirements",
  "load_spec_requirements",
  "render_spec_requirements_block",
]


from .schema_registry import BlockSchema, register_block_schema  # noqa: E402
from .spec_requirements_metadata import SPEC_REQUIREMENTS_METADATA  # noqa: E402

register_block_schema(
  "spec.requirements",
  BlockSchema(
    name="spec.requirements",
    marker=REQUIREMENTS_MARKER,
    version=REQUIREMENTS_VERSION,
    renderer=render_spec_requirements_block,
    description="Structured requirements within spec/product artifacts",
    metadata=SPEC_REQUIREMENTS_METADATA,
  ),
)
