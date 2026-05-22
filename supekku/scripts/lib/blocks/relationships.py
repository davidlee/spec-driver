"""Utilities for parsing structured spec YAML blocks.

Covers spec.relationships, spec.capabilities, spec.concerns,
spec.hypotheses, and spec.decisions block types.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import yaml

from .yaml_utils import format_yaml_list, make_block_pattern

if TYPE_CHECKING:
  from pathlib import Path

SPEC_RELATIONSHIPS_MARKER = "supekku:spec.relationships@v1"
RELATIONSHIPS_SCHEMA = "supekku.spec.relationships"
RELATIONSHIPS_VERSION = 1

CAPABILITIES_MARKER = "supekku:spec.capabilities@v1"
CAPABILITIES_SCHEMA = "supekku.spec.capabilities"
CAPABILITIES_VERSION = 1

CONCERNS_MARKER = "supekku:spec.concerns@v1"
CONCERNS_SCHEMA = "supekku.spec.concerns"
CONCERNS_VERSION = 1

HYPOTHESES_MARKER = "supekku:spec.hypotheses@v1"
HYPOTHESES_SCHEMA = "supekku.spec.hypotheses"
HYPOTHESES_VERSION = 1

DECISIONS_MARKER = "supekku:spec.decisions@v1"
DECISIONS_SCHEMA = "supekku.spec.decisions"
DECISIONS_VERSION = 1


@dataclass(frozen=True)
class RelationshipsBlock:
  """Parsed YAML block containing specification relationships."""

  raw_yaml: str
  data: dict[str, Any]


@dataclass(frozen=True)
class SpecConcernsBlock:
  """Parsed YAML block containing spec concerns."""

  raw_yaml: str
  data: dict[str, Any]


@dataclass(frozen=True)
class SpecHypothesesBlock:
  """Parsed YAML block containing spec hypotheses."""

  raw_yaml: str
  data: dict[str, Any]


@dataclass(frozen=True)
class SpecDecisionsBlock:
  """Parsed YAML block containing spec decisions."""

  raw_yaml: str
  data: dict[str, Any]


_RELATIONSHIPS_PATTERN = make_block_pattern(SPEC_RELATIONSHIPS_MARKER)
_CONCERNS_PATTERN = make_block_pattern(CONCERNS_MARKER)
_HYPOTHESES_PATTERN = make_block_pattern(HYPOTHESES_MARKER)
_DECISIONS_PATTERN = make_block_pattern(DECISIONS_MARKER)


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
    f"```yaml {SPEC_RELATIONSHIPS_MARKER}",
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


def extract_spec_concerns(text: str) -> SpecConcernsBlock | None:
  """Extract spec concerns block from markdown text."""
  match = _CONCERNS_PATTERN.search(text)
  if not match:
    return None
  raw = match.group(1)
  try:
    data = yaml.safe_load(raw) or {}
  except yaml.YAMLError as exc:
    msg = f"invalid spec concerns YAML: {exc}"
    raise ValueError(msg) from exc
  if not isinstance(data, dict):
    msg = "spec concerns block must parse to mapping"
    raise ValueError(msg)
  return SpecConcernsBlock(raw_yaml=raw, data=data)


def extract_spec_hypotheses(text: str) -> SpecHypothesesBlock | None:
  """Extract spec hypotheses block from markdown text."""
  match = _HYPOTHESES_PATTERN.search(text)
  if not match:
    return None
  raw = match.group(1)
  try:
    data = yaml.safe_load(raw) or {}
  except yaml.YAMLError as exc:
    msg = f"invalid spec hypotheses YAML: {exc}"
    raise ValueError(msg) from exc
  if not isinstance(data, dict):
    msg = "spec hypotheses block must parse to mapping"
    raise ValueError(msg)
  return SpecHypothesesBlock(raw_yaml=raw, data=data)


def extract_spec_decisions(text: str) -> SpecDecisionsBlock | None:
  """Extract spec decisions block from markdown text."""
  match = _DECISIONS_PATTERN.search(text)
  if not match:
    return None
  raw = match.group(1)
  try:
    data = yaml.safe_load(raw) or {}
  except yaml.YAMLError as exc:
    msg = f"invalid spec decisions YAML: {exc}"
    raise ValueError(msg) from exc
  if not isinstance(data, dict):
    msg = "spec decisions block must parse to mapping"
    raise ValueError(msg)
  return SpecDecisionsBlock(raw_yaml=raw, data=data)


def _render_spec_block(
  marker: str, schema: str, version: int, list_key: str, items: list[Any]
) -> str:
  """Shared renderer for simple spec list-of-objects blocks."""
  head = f"```yaml {marker}\nschema: {schema}\nversion: {version}\n"
  if not items:
    return head + f"{list_key}: []\n```"
  body = yaml.safe_dump(
    {list_key: items}, sort_keys=False, allow_unicode=True, default_flow_style=False
  ).rstrip()
  return head + body + "\n```"


def render_spec_concerns_block(
  spec_id: str, *, concerns: list[dict[str, str]] | None = None
) -> str:
  """Render a spec concerns YAML block."""
  lines = [f"```yaml {CONCERNS_MARKER}", f"schema: {CONCERNS_SCHEMA}"]
  lines.append(f"version: {CONCERNS_VERSION}")
  lines.append(f"spec: {spec_id}")
  items = concerns or []
  if not items:
    lines.append("concerns: []")
  else:
    lines.append("concerns:")
    for c in items:
      lines.append(f"  - name: {c['name']}")
      lines.append("    description: |")
      for line in c["description"].strip().splitlines():
        lines.append(f"      {line}")
  lines.append("```")
  return "\n".join(lines)


def render_spec_hypotheses_block(
  spec_id: str, *, hypotheses: list[dict[str, str]] | None = None
) -> str:
  """Render a spec hypotheses YAML block."""
  items = [{k: v for k, v in h.items() if v is not None} for h in (hypotheses or [])]
  head = (
    f"```yaml {HYPOTHESES_MARKER}\n"
    f"schema: {HYPOTHESES_SCHEMA}\n"
    f"version: {HYPOTHESES_VERSION}\n"
    f"spec: {spec_id}\n"
  )
  if not items:
    return head + "hypotheses: []\n```"
  body = yaml.safe_dump(
    {"hypotheses": items}, sort_keys=False, allow_unicode=True, default_flow_style=False
  ).rstrip()
  return head + body + "\n```"


def render_spec_decisions_block(
  spec_id: str, *, decisions: list[dict[str, str]] | None = None
) -> str:
  """Render a spec decisions YAML block."""
  items = [{k: v for k, v in d.items() if v is not None} for d in (decisions or [])]
  head = (
    f"```yaml {DECISIONS_MARKER}\n"
    f"schema: {DECISIONS_SCHEMA}\n"
    f"version: {DECISIONS_VERSION}\n"
    f"spec: {spec_id}\n"
  )
  if not items:
    return head + "decisions: []\n```"
  body = yaml.safe_dump(
    {"decisions": items}, sort_keys=False, allow_unicode=True, default_flow_style=False
  ).rstrip()
  return head + body + "\n```"


__all__ = [
  "CAPABILITIES_MARKER",
  "CAPABILITIES_SCHEMA",
  "CAPABILITIES_VERSION",
  "CONCERNS_MARKER",
  "CONCERNS_SCHEMA",
  "CONCERNS_VERSION",
  "DECISIONS_MARKER",
  "DECISIONS_SCHEMA",
  "DECISIONS_VERSION",
  "HYPOTHESES_MARKER",
  "HYPOTHESES_SCHEMA",
  "HYPOTHESES_VERSION",
  "SPEC_RELATIONSHIPS_MARKER",
  "RELATIONSHIPS_SCHEMA",
  "RELATIONSHIPS_VERSION",
  "RelationshipsBlock",
  "SpecConcernsBlock",
  "SpecDecisionsBlock",
  "SpecHypothesesBlock",
  "extract_relationships",
  "extract_spec_concerns",
  "extract_spec_decisions",
  "extract_spec_hypotheses",
  "load_relationships_from_file",
  "render_spec_capabilities_block",
  "render_spec_concerns_block",
  "render_spec_decisions_block",
  "render_spec_hypotheses_block",
  "render_spec_relationships_block",
]


# Register schemas
from .schema_registry import BlockSchema, register_block_schema  # noqa: E402
from .spec_metadata import (  # noqa: E402
  SPEC_CAPABILITIES_METADATA,
  SPEC_CONCERNS_METADATA,
  SPEC_DECISIONS_METADATA,
  SPEC_HYPOTHESES_METADATA,
  SPEC_RELATIONSHIPS_METADATA,
)

register_block_schema(
  "spec.relationships",
  BlockSchema(
    name="spec.relationships",
    marker=SPEC_RELATIONSHIPS_MARKER,
    version=RELATIONSHIPS_VERSION,
    renderer=render_spec_relationships_block,
    description="Defines spec relationships to requirements and other specs",
    metadata=SPEC_RELATIONSHIPS_METADATA,
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
    metadata=SPEC_CAPABILITIES_METADATA,
  ),
)

register_block_schema(
  "spec.concerns",
  BlockSchema(
    name="spec.concerns",
    marker=CONCERNS_MARKER,
    version=CONCERNS_VERSION,
    renderer=render_spec_concerns_block,
    description="Spec concerns — enduring problem spaces or quality dimensions",
    metadata=SPEC_CONCERNS_METADATA,
  ),
)

register_block_schema(
  "spec.hypotheses",
  BlockSchema(
    name="spec.hypotheses",
    marker=HYPOTHESES_MARKER,
    version=HYPOTHESES_VERSION,
    renderer=render_spec_hypotheses_block,
    description="Spec hypotheses tracking belief evolution",
    metadata=SPEC_HYPOTHESES_METADATA,
  ),
)

register_block_schema(
  "spec.decisions",
  BlockSchema(
    name="spec.decisions",
    marker=DECISIONS_MARKER,
    version=DECISIONS_VERSION,
    renderer=render_spec_decisions_block,
    description="Key architectural or design decisions",
    metadata=SPEC_DECISIONS_METADATA,
  ),
)
