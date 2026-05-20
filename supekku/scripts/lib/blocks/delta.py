"""Utilities for parsing structured delta YAML blocks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import yaml

from .yaml_utils import format_yaml_list, make_block_pattern

if TYPE_CHECKING:
  from pathlib import Path

DELTA_RELATIONSHIPS_MARKER = "supekku:delta.relationships@v1"
RELATIONSHIPS_SCHEMA = "supekku.delta.relationships"
RELATIONSHIPS_VERSION = 1

DELTA_CONTEXT_INPUTS_MARKER = "supekku:delta.context_inputs@v1"
CONTEXT_INPUTS_SCHEMA = "supekku.delta.context_inputs"
CONTEXT_INPUTS_VERSION = 1

DELTA_RISK_REGISTER_MARKER = "supekku:delta.risk_register@v1"
RISK_REGISTER_SCHEMA = "supekku.delta.risk_register"
RISK_REGISTER_VERSION = 1


@dataclass(frozen=True)
class DeltaRelationshipsBlock:
  """Parsed YAML block containing delta relationships."""

  raw_yaml: str
  data: dict[str, Any]


@dataclass(frozen=True)
class DeltaContextInputsBlock:
  """Parsed YAML block containing delta context inputs."""

  raw_yaml: str
  data: dict[str, Any]


@dataclass(frozen=True)
class DeltaRiskRegisterBlock:
  """Parsed YAML block containing delta risk register."""

  raw_yaml: str
  data: dict[str, Any]


_BLOCK_PATTERN = make_block_pattern(DELTA_RELATIONSHIPS_MARKER)
_CONTEXT_INPUTS_PATTERN = make_block_pattern(DELTA_CONTEXT_INPUTS_MARKER)
_RISK_REGISTER_PATTERN = make_block_pattern(DELTA_RISK_REGISTER_MARKER)


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


def extract_delta_context_inputs(text: str) -> DeltaContextInputsBlock | None:
  """Extract delta context_inputs block from markdown text."""
  match = _CONTEXT_INPUTS_PATTERN.search(text)
  if not match:
    return None
  raw = match.group(1)
  try:
    data = yaml.safe_load(raw) or {}
  except yaml.YAMLError as exc:
    msg = f"invalid delta context_inputs YAML: {exc}"
    raise ValueError(msg) from exc
  if not isinstance(data, dict):
    msg = "delta context_inputs block must parse to mapping"
    raise ValueError(msg)
  return DeltaContextInputsBlock(raw_yaml=raw, data=data)


def extract_delta_risk_register(text: str) -> DeltaRiskRegisterBlock | None:
  """Extract delta risk_register block from markdown text."""
  match = _RISK_REGISTER_PATTERN.search(text)
  if not match:
    return None
  raw = match.group(1)
  try:
    data = yaml.safe_load(raw) or {}
  except yaml.YAMLError as exc:
    msg = f"invalid delta risk_register YAML: {exc}"
    raise ValueError(msg) from exc
  if not isinstance(data, dict):
    msg = "delta risk_register block must parse to mapping"
    raise ValueError(msg)
  return DeltaRiskRegisterBlock(raw_yaml=raw, data=data)


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
    f"```yaml {DELTA_RELATIONSHIPS_MARKER}",
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


_CTX_ENTRY_KEY_ORDER = ("type", "id", "summary")
_RISK_ENTRY_KEY_ORDER = (
  "id",
  "title",
  "likelihood",
  "impact",
  "exposure",
  "mitigation",
  "status",
)


def _normalise_entry(entry: dict[str, Any], order: tuple[str, ...]) -> dict[str, Any]:
  """Return entry with declared keys in canonical order; keys with ``None`` omitted."""
  out: dict[str, Any] = {}
  for key in order:
    if key in entry and entry[key] is not None:
      out[key] = entry[key]
  for key, value in entry.items():
    if key in order:
      continue
    if value is None:
      continue
    out[key] = value
  return out


def _render_block(
  marker: str, schema: str, version: int, list_key: str, items: list[Any]
) -> str:
  head = f"```yaml {marker}\nschema: {schema}\nversion: {version}\n"
  if not items:
    return head + f"{list_key}: []\n```"
  body = yaml.safe_dump(
    {list_key: items}, sort_keys=False, allow_unicode=True, default_flow_style=False
  ).rstrip()
  return head + body + "\n```"


def render_delta_context_inputs_block(
  *, entries: list[dict[str, Any]] | None = None
) -> str:
  """Render a delta context_inputs YAML block.

  Empty ``entries`` renders ``entries: []`` (empty-block canonical form).
  Populated entries are normalised to canonical key order (``type``, ``id``,
  ``summary``); ``None`` summaries are omitted (schema is non-nullable str —
  emitters MUST omit the key, never emit ``summary: null``; F-138-31).
  """
  items = [_normalise_entry(e, _CTX_ENTRY_KEY_ORDER) for e in (entries or [])]
  return _render_block(
    DELTA_CONTEXT_INPUTS_MARKER,
    CONTEXT_INPUTS_SCHEMA,
    CONTEXT_INPUTS_VERSION,
    "entries",
    items,
  )


def render_delta_risk_register_block(
  *, risks: list[dict[str, Any]] | None = None
) -> str:
  """Render a delta risk_register YAML block.

  Empty ``risks`` renders ``risks: []`` (empty-block canonical form).
  Populated entries are normalised to canonical key order; ``None`` values
  are omitted.
  """
  items = [_normalise_entry(r, _RISK_ENTRY_KEY_ORDER) for r in (risks or [])]
  return _render_block(
    DELTA_RISK_REGISTER_MARKER,
    RISK_REGISTER_SCHEMA,
    RISK_REGISTER_VERSION,
    "risks",
    items,
  )


__all__ = [
  "CONTEXT_INPUTS_SCHEMA",
  "CONTEXT_INPUTS_VERSION",
  "DELTA_CONTEXT_INPUTS_MARKER",
  "DELTA_RELATIONSHIPS_MARKER",
  "DELTA_RISK_REGISTER_MARKER",
  "DeltaContextInputsBlock",
  "DeltaRelationshipsBlock",
  "DeltaRiskRegisterBlock",
  "RISK_REGISTER_SCHEMA",
  "RISK_REGISTER_VERSION",
  "extract_delta_context_inputs",
  "extract_delta_relationships",
  "extract_delta_risk_register",
  "load_delta_relationships",
  "render_delta_context_inputs_block",
  "render_delta_relationships_block",
  "render_delta_risk_register_block",
]


# Register schemas
from .delta_metadata import (  # noqa: E402
  DELTA_CONTEXT_INPUTS_METADATA,
  DELTA_RELATIONSHIPS_METADATA,
  DELTA_RISK_REGISTER_METADATA,
)
from .schema_registry import BlockSchema, register_block_schema  # noqa: E402

register_block_schema(
  "delta.relationships",
  BlockSchema(
    name="delta.relationships",
    marker=DELTA_RELATIONSHIPS_MARKER,
    version=RELATIONSHIPS_VERSION,
    renderer=render_delta_relationships_block,
    description=(
      "Tracks delta relationships to specs, requirements, phases, and revisions"
    ),
    metadata=DELTA_RELATIONSHIPS_METADATA,
  ),
)

register_block_schema(
  "delta.context_inputs",
  BlockSchema(
    name="delta.context_inputs",
    marker=DELTA_CONTEXT_INPUTS_MARKER,
    version=CONTEXT_INPUTS_VERSION,
    renderer=render_delta_context_inputs_block,
    description="Context inputs (research, decisions, refs) consumed by this delta",
    metadata=DELTA_CONTEXT_INPUTS_METADATA,
  ),
)

register_block_schema(
  "delta.risk_register",
  BlockSchema(
    name="delta.risk_register",
    marker=DELTA_RISK_REGISTER_MARKER,
    version=RISK_REGISTER_VERSION,
    renderer=render_delta_risk_register_block,
    description="Delta risk register entries",
    metadata=DELTA_RISK_REGISTER_METADATA,
  ),
)
