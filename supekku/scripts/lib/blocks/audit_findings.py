"""Block parser for supekku:audit.findings@v1 YAML blocks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import yaml

from supekku.scripts.lib.blocks.yaml_utils import make_block_pattern

AUDIT_FINDINGS_MARKER = "supekku:audit.findings@v1"
AUDIT_FINDINGS_SCHEMA = "supekku.audit.findings"
AUDIT_FINDINGS_VERSION = 1


@dataclass(frozen=True)
class AuditFindingsBlock:
  """Parsed YAML block containing audit findings."""

  raw_yaml: str
  data: dict[str, Any]


_AUDIT_FINDINGS_PATTERN = make_block_pattern(AUDIT_FINDINGS_MARKER)


def extract_audit_findings(text: str) -> AuditFindingsBlock | None:
  """Extract a single audit findings block from markdown content.

  Returns None if no block found. Raises ValueError on malformed YAML,
  multiple blocks, or audit field mismatch.
  """
  matches = list(_AUDIT_FINDINGS_PATTERN.finditer(text))
  if not matches:
    return None
  if len(matches) > 1:
    msg = "multiple audit.findings blocks found; exactly one is allowed"
    raise ValueError(msg)
  raw = matches[0].group(1)
  try:
    data = yaml.safe_load(raw) or {}
  except yaml.YAMLError as exc:
    msg = f"invalid audit findings YAML: {exc}"
    raise ValueError(msg) from exc
  if not isinstance(data, dict):
    msg = "audit findings block must parse to mapping"
    raise ValueError(msg)
  return AuditFindingsBlock(raw_yaml=raw, data=data)


def validate_audit_field(block: AuditFindingsBlock, audit_id: str) -> None:
  """Raise ValueError if block audit field does not match artifact id."""
  block_audit = block.data.get("audit", "")
  if block_audit != audit_id:
    msg = (
      f"audit findings block audit field '{block_audit}' "
      f"does not match artifact id '{audit_id}'"
    )
    raise ValueError(msg)


def load_audit_findings(
  body: str,
  fm: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
  """Canonical dual-path loader for audit findings (DEC-141-06).

  Block-first authority: extracts findings from body block when present.
  Falls back to frontmatter when no block exists and fm is provided.
  """
  block = extract_audit_findings(body)
  if block is not None:
    return block.data.get("findings", [])
  if fm is not None:
    return fm.get("findings", [])
  return []


def _yaml_str(value: str) -> str:
  """Quote a string value for YAML if it contains special characters."""
  if not value:
    return '""'
  needs_quoting = any(c in value for c in ":{}[],'\"&*?|>!%@`#")
  if needs_quoting or value != value.strip():
    dumped = yaml.dump(value, default_flow_style=True).rstrip()
    if dumped.endswith("\n..."):
      dumped = dumped[:-4]
    return dumped.rstrip("\n")
  return value


def _render_disposition(disposition: dict[str, Any], indent: int) -> list[str]:
  """Render disposition sub-object as indented YAML lines."""
  prefix = " " * indent
  lines = [f"{prefix}disposition:"]
  inner = " " * (indent + 2)

  for key in ("status", "kind", "rationale"):
    if key in disposition:
      lines.append(f"{inner}{key}: {_yaml_str(str(disposition[key]))}")

  for list_key in ("refs", "drift_refs"):
    if list_key in disposition and disposition[list_key]:
      lines.append(f"{inner}{list_key}:")
      for ref_entry in disposition[list_key]:
        first = True
        for k, v in ref_entry.items():
          if first:
            lines.append(f"{inner}  - {k}: {_yaml_str(str(v))}")
            first = False
          else:
            lines.append(f"{inner}    {k}: {_yaml_str(str(v))}")

  if "closure_override" in disposition and disposition["closure_override"]:
    co = disposition["closure_override"]
    lines.append(f"{inner}closure_override:")
    deep = " " * (indent + 4)
    if "effect" in co:
      lines.append(f"{deep}effect: {co['effect']}")
    if "rationale" in co:
      lines.append(f"{deep}rationale: {_yaml_str(str(co['rationale']))}")

  return lines


def render_audit_findings_block(
  audit_id: str,
  findings: list[dict[str, Any]],
) -> str:
  """Render audit findings as a code-fenced supekku:audit.findings@v1 block."""
  lines = [
    f"```yaml {AUDIT_FINDINGS_MARKER}",
    f"schema: {AUDIT_FINDINGS_SCHEMA}",
    f"version: {AUDIT_FINDINGS_VERSION}",
    f"audit: {audit_id}",
    "findings:",
  ]

  if not findings:
    lines[-1] = "findings: []"
  else:
    for finding in findings:
      lines.append(f"  - id: {finding['id']}")
      lines.append(f"    description: {_yaml_str(str(finding['description']))}")
      lines.append(f"    outcome: {finding['outcome']}")

      for opt_key in ("linked_issue", "linked_delta"):
        val = finding.get(opt_key, "")
        if val:
          lines.append(f"    {opt_key}: {_yaml_str(str(val))}")

      if "disposition" in finding and finding["disposition"]:
        lines.extend(_render_disposition(finding["disposition"], indent=4))

  lines.append("```")
  return "\n".join(lines)


__all__ = [
  "AUDIT_FINDINGS_MARKER",
  "AUDIT_FINDINGS_SCHEMA",
  "AUDIT_FINDINGS_VERSION",
  "AuditFindingsBlock",
  "extract_audit_findings",
  "load_audit_findings",
  "render_audit_findings_block",
  "validate_audit_field",
]


from .schema_registry import BlockSchema, register_block_schema  # noqa: E402

register_block_schema(
  "audit.findings",
  BlockSchema(
    name="audit.findings",
    marker=AUDIT_FINDINGS_MARKER,
    version=AUDIT_FINDINGS_VERSION,
    renderer=render_audit_findings_block,
    description="Structured audit findings within audit artifacts",
    metadata=None,
  ),
)
