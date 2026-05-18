"""Utilities for parsing verification coverage YAML blocks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import yaml

from supekku.scripts.lib.blocks.yaml_utils import make_block_pattern

if TYPE_CHECKING:
  from pathlib import Path

COVERAGE_MARKER = "supekku:verification.coverage@v1"
COVERAGE_SCHEMA = "supekku.verification.coverage"
COVERAGE_VERSION = 1

# Valid verification artifact kinds
VALID_KINDS = {"VT", "VA", "VH"}

# OQ-137-02 sunset: derived re-export from per-kind metadata.
from supekku.scripts.lib.core.frontmatter_metadata.verification import (  # noqa: E402
  VERIFICATION_FRONTMATTER_METADATA,
)

VERIFICATION_STATUSES: frozenset[str] = frozenset(
  VERIFICATION_FRONTMATTER_METADATA.fields["status"].enum_values or []
)


@dataclass(frozen=True)
class VerificationCoverageBlock:
  """Parsed YAML block containing verification coverage entries."""

  raw_yaml: str
  data: dict[str, Any]


_COVERAGE_PATTERN = make_block_pattern(COVERAGE_MARKER)


def extract_coverage_blocks(text: str) -> list[VerificationCoverageBlock]:
  """Extract and parse all coverage blocks from markdown content.

  Args:
    text: Markdown content containing coverage blocks.

  Returns:
    List of parsed VerificationCoverageBlock instances.

  Raises:
    ValueError: If YAML is invalid or doesn't parse to a mapping.
  """
  blocks: list[VerificationCoverageBlock] = []
  for match in _COVERAGE_PATTERN.finditer(text):
    raw = match.group(1)
    try:
      data = yaml.safe_load(raw) or {}
    except yaml.YAMLError as exc:  # pragma: no cover
      msg = f"invalid coverage YAML: {exc}"
      raise ValueError(msg) from exc
    if not isinstance(data, dict):
      msg = "coverage block must parse to mapping"
      raise ValueError(msg)
    blocks.append(VerificationCoverageBlock(raw_yaml=raw, data=data))
  return blocks


def load_coverage_blocks(path: Path) -> list[VerificationCoverageBlock]:
  """Load and extract coverage blocks from file.

  Args:
    path: Path to markdown file.

  Returns:
    List of parsed VerificationCoverageBlock instances.
  """
  text = path.read_text(encoding="utf-8")
  return extract_coverage_blocks(text)


def render_verification_coverage_block(
  subject_id: str,
  *,
  entries: list[dict[str, Any]] | None = None,
) -> str:
  """Render a verification coverage YAML block with given values.

  This is the canonical source for the block structure. Templates and
  creation code should use this instead of hardcoding the structure.

  Args:
    subject_id: The subject ID (SPEC, PROD, IP, or AUD).
    entries: List of verification entries. Each entry is a dict with:
      - artefact: str (e.g., "VT-001")
      - kind: str (VT, VA, or VH)
      - requirement: str (e.g., "SPEC-100.FR-001")
      - status: str (planned, in-progress, verified, failed, blocked)
      - phase: str | None (optional, e.g., "IP-001.PHASE-01")
      - notes: str | None (optional)

  Returns:
    Formatted YAML code block as string.

  Example:
    >>> block = render_verification_coverage_block(
    ...   "SPEC-100",
    ...   entries=[{
    ...     "artefact": "VT-001",
    ...     "kind": "VT",
    ...     "requirement": "SPEC-100.FR-001",
    ...     "status": "planned",
    ...   }]
    ... )
  """
  lines = [
    f"```yaml {COVERAGE_MARKER}",
    f"schema: {COVERAGE_SCHEMA}",
    f"version: {COVERAGE_VERSION}",
    f"subject: {subject_id}",
    "entries:",
  ]

  # Add entries or empty array
  if not entries:
    lines[-1] = "entries: []"
  else:
    for entry in entries:
      lines.append(f"  - artefact: {entry['artefact']}")
      lines.append(f"    kind: {entry['kind']}")
      lines.append(f"    requirement: {entry['requirement']}")
      if "phase" in entry and entry["phase"]:
        lines.append(f"    phase: {entry['phase']}")
      lines.append(f"    status: {entry['status']}")
      if "notes" in entry and entry["notes"]:
        # Handle multi-line notes with >- folded scalar
        notes_text = entry["notes"].strip()
        if "\n" in notes_text:
          lines.append("    notes: >-")
          for note_line in notes_text.splitlines():
            lines.append(f"      {note_line}")
        else:
          lines.append(f"    notes: {notes_text}")

  lines.append("```")
  return "\n".join(lines)


__all__ = [
  "COVERAGE_MARKER",
  "COVERAGE_SCHEMA",
  "COVERAGE_VERSION",
  "VALID_KINDS",
  "VERIFICATION_STATUSES",
  "VerificationCoverageBlock",
  "extract_coverage_blocks",
  "load_coverage_blocks",
  "render_verification_coverage_block",
]


# Register schema
from .schema_registry import BlockSchema, register_block_schema  # noqa: E402
from .verification_metadata import VERIFICATION_COVERAGE_METADATA  # noqa: E402

register_block_schema(
  "verification.coverage",
  BlockSchema(
    name="verification.coverage",
    marker=COVERAGE_MARKER,
    version=COVERAGE_VERSION,
    renderer=render_verification_coverage_block,
    description=(
      "Tracks verification artifacts (tests, analyses, histories) for requirements"
    ),
    metadata=VERIFICATION_COVERAGE_METADATA,
  ),
)
