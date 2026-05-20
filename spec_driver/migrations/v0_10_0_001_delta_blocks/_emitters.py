"""Frozen-local render emitters for the v0_10_0_001_delta_blocks step.

These produce byte-identical output to the supekku-side ``render_*`` helpers in
``supekku/scripts/lib/blocks/delta.py``. The migration package cannot import
those helpers (``Migrations isolation`` import-linter contract forbids any
``supekku.*`` import inside ``spec_driver.migrations``); duplication is the
accepted exception per DEC-138-12. Drift between the two implementations is
bounded by the byte-equality VT in ``migration_test.py``.

Per DR-137 DEC-137-26 these emitters are forward-only: defects are fixed by a
new ordinal step (``v0_10_0_002_*``), never by editing the v0_10_0_001 emitter.
"""

from __future__ import annotations

from typing import Any

import yaml

DELTA_RELATIONSHIPS_MARKER = "supekku:delta.relationships@v1"
RELATIONSHIPS_SCHEMA = "supekku.delta.relationships"
RELATIONSHIPS_VERSION = 1

DELTA_CONTEXT_INPUTS_MARKER = "supekku:delta.context_inputs@v1"
CONTEXT_INPUTS_SCHEMA = "supekku.delta.context_inputs"
CONTEXT_INPUTS_VERSION = 1

DELTA_RISK_REGISTER_MARKER = "supekku:delta.risk_register@v1"
RISK_REGISTER_SCHEMA = "supekku.delta.risk_register"
RISK_REGISTER_VERSION = 1

_CTX_ENTRY_KEY_ORDER: tuple[str, ...] = ("type", "id", "summary")
_RISK_ENTRY_KEY_ORDER: tuple[str, ...] = (
  "id",
  "title",
  "likelihood",
  "impact",
  "exposure",
  "mitigation",
  "status",
)


def _format_yaml_list(key: str, values: list[str] | None, level: int = 0) -> str:
  """Mirror of ``supekku.scripts.lib.blocks.yaml_utils.format_yaml_list``."""
  indent = "  " * level
  items = [str(v) for v in (values or []) if v]
  if not items:
    return f"{indent}{key}: []"
  child_indent = "  " * (level + 1)
  lines = [f"{indent}{key}:"]
  lines.extend(f"{child_indent}- {item}" for item in sorted(items))
  return "\n".join(lines)


def _normalise_entry(entry: dict[str, Any], order: tuple[str, ...]) -> dict[str, Any]:
  """Return entry with declared keys in canonical order; ``None`` values omitted.

  Mirror of supekku-side ``_normalise_entry`` in ``blocks/delta.py``.
  """
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
    {list_key: items},
    sort_keys=False,
    allow_unicode=True,
    default_flow_style=False,
  ).rstrip()
  return head + body + "\n```"


def render_relationships_block(
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
  """Render a delta relationships block — byte-equivalent to supekku helper."""
  lines = [
    f"```yaml {DELTA_RELATIONSHIPS_MARKER}",
    f"schema: {RELATIONSHIPS_SCHEMA}",
    f"version: {RELATIONSHIPS_VERSION}",
    f"delta: {delta_id}",
    "revision_links:",
    _format_yaml_list("introduces", introduces_revisions, level=1),
    _format_yaml_list("supersedes", supersedes_revisions, level=1),
    "specs:",
    _format_yaml_list("primary", primary_specs, level=1),
    _format_yaml_list("collaborators", collaborator_specs, level=1),
    "requirements:",
    _format_yaml_list("implements", implements_requirements, level=1),
    _format_yaml_list("updates", updates_requirements, level=1),
    _format_yaml_list("verifies", verifies_requirements, level=1),
    _format_yaml_list("phases", phases, level=0),
    "```",
  ]
  return "\n".join(lines)


def render_context_inputs_block(*, entries: list[dict[str, Any]] | None = None) -> str:
  """Render a delta context_inputs block — byte-equivalent to supekku helper."""
  items = [_normalise_entry(e, _CTX_ENTRY_KEY_ORDER) for e in (entries or [])]
  return _render_block(
    DELTA_CONTEXT_INPUTS_MARKER,
    CONTEXT_INPUTS_SCHEMA,
    CONTEXT_INPUTS_VERSION,
    "entries",
    items,
  )


def render_risk_register_block(*, risks: list[dict[str, Any]] | None = None) -> str:
  """Render a delta risk_register block — byte-equivalent to supekku helper."""
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
  "RELATIONSHIPS_SCHEMA",
  "RELATIONSHIPS_VERSION",
  "RISK_REGISTER_SCHEMA",
  "RISK_REGISTER_VERSION",
  "render_context_inputs_block",
  "render_relationships_block",
  "render_risk_register_block",
]
