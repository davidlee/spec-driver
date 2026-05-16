"""Utilities for extracting structured revision blocks."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any

import yaml

from .revision_metadata import (
  REVISION_BLOCK_SCHEMA_ID,
  REVISION_BLOCK_VERSION,
  REVISION_CHANGE_METADATA,
)
from .schema_registry import BlockSchema, register_block_schema

if TYPE_CHECKING:
  from pathlib import Path

REVISION_BLOCK_MARKER = "supekku:revision.change@v1"


@dataclass
class RevisionChangeBlock:
  """Represents a parsed revision change block from markdown."""

  marker: str
  language: str
  info: str
  yaml_content: str
  content_start: int
  content_end: int
  source_path: Path | None = None

  def parse(self) -> dict[str, Any]:
    """Parse YAML content from revision block.

    Returns:
      Parsed YAML data as dictionary.

    Raises:
      ValueError: If YAML is invalid or doesn't parse to a mapping.
    """
    try:
      loaded = yaml.safe_load(self.yaml_content)
    except yaml.YAMLError as exc:  # pragma: no cover - repr includes location
      msg = f"invalid YAML: {exc}"
      raise ValueError(msg) from exc
    if loaded is None:
      return {}
    if not isinstance(loaded, dict):
      msg = "revision block must parse to a mapping"
      raise ValueError(msg)
    return loaded

  def formatted_yaml(self, data: dict[str, Any] | None = None) -> str:
    """Format data as canonical YAML.

    Args:
      data: Optional data to format. If None, parses from yaml_content.

    Returns:
      Formatted YAML string with trailing newline.
    """
    payload = data if data is not None else self.parse()
    dumped = yaml.safe_dump(
      payload,
      sort_keys=False,
      indent=2,
      default_flow_style=False,
    )
    if not dumped.endswith("\n"):
      dumped += "\n"
    return dumped

  def replace_content(self, original: str, new_yaml: str) -> str:
    """Replace block content in original string.

    Args:
      original: Original file content.
      new_yaml: New YAML content to insert.

    Returns:
      Updated content with replacement applied.
    """
    return original[: self.content_start] + new_yaml + original[self.content_end :]


def extract_revision_blocks(
  markdown: str,
  *,
  source: Path | None = None,
) -> list[RevisionChangeBlock]:
  """Extract revision change blocks from markdown content.

  Args:
    markdown: Markdown content to parse.
    source: Optional source file path for error reporting.

  Returns:
    List of parsed RevisionChangeBlock objects.
  """
  lines = markdown.splitlines(keepends=True)
  blocks: list[RevisionChangeBlock] = []
  offset = 0
  idx = 0
  while idx < len(lines):
    line = lines[idx]
    line_start = offset
    offset += len(line)
    match = re.match(r"^(`{3,})(.*)$", line.rstrip("\r\n"))
    if not match:
      idx += 1
      continue
    fence = match.group(1)
    info = match.group(2).strip()
    if not info:
      idx += 1
      continue
    info_parts = info.split()
    language = info_parts[0]
    marker = next(
      (part for part in info_parts[1:] if part.startswith("supekku:")),
      "",
    )
    if language not in {"yaml", "yml"} or marker != REVISION_BLOCK_MARKER:
      idx += 1
      continue
    closing_idx = idx + 1
    while closing_idx < len(lines):
      candidate = lines[closing_idx]
      candidate_stripped = candidate.rstrip("\r\n")
      if (
        candidate_stripped.startswith(fence)
        and candidate_stripped[len(fence) :].strip() == ""
      ):
        break
      closing_idx += 1
    if closing_idx >= len(lines):
      idx += 1
      continue
    content_start = line_start + len(line)
    yaml_content = "".join(lines[idx + 1 : closing_idx])
    content_end = content_start + len(yaml_content)
    block = RevisionChangeBlock(
      marker=marker,
      language=language,
      info=info,
      yaml_content=yaml_content,
      content_start=content_start,
      content_end=content_end,
      source_path=source,
    )
    blocks.append(block)
    # move idx to closing fence line
    while idx < closing_idx:
      idx += 1
      offset += len(lines[idx])
    idx += 1
  return blocks


def load_revision_blocks(path: Path) -> list[RevisionChangeBlock]:
  """Load and extract revision change blocks from a file.

  Args:
    path: Path to markdown file.

  Returns:
    List of parsed RevisionChangeBlock objects.
  """
  content = path.read_text(encoding="utf-8")
  return extract_revision_blocks(content, source=path)


def render_revision_change_block(
  revision_id: str,
  *,
  specs: list[dict[str, Any]] | None = None,
  requirements: list[dict[str, Any]] | None = None,
  prepared_by: str | None = None,
  generated_at: str | None = None,
) -> str:
  """Render a revision change YAML block with given values.

  This is the canonical source for the block structure. Templates and
  creation code should use this instead of hardcoding the structure.

  Note: This generates a minimal but valid revision block. For complex revisions,
  consider building the dict structure and using yaml.safe_dump directly.

  Args:
    revision_id: The revision ID (e.g., "RE-001").
    specs: List of spec change dicts with:
      - spec_id: str
      - action: str ("created", "updated", "retired")
      - summary: str (optional)
      - requirement_flow: dict (optional)
      - section_changes: list (optional)
    requirements: List of requirement change dicts with:
      - requirement_id: str
      - kind: str ("functional", "non-functional")
      - action: str ("introduce", "modify", "move", "retire")
      - summary: str (optional)
      - destination: dict (optional)
      - origin: list (optional)
      - lifecycle: dict (optional)
    prepared_by: Optional preparer identifier.
    generated_at: Optional generation timestamp.

  Returns:
    Formatted YAML code block as string.
  """
  # Build metadata
  metadata: dict[str, Any] = {"revision": revision_id}
  if prepared_by:
    metadata["prepared_by"] = prepared_by
  if generated_at:
    metadata["generated_at"] = generated_at
  elif not prepared_by:  # Only add default timestamp if neither field provided
    metadata["generated_at"] = datetime.now().isoformat() + "Z"

  # Build the block data structure
  data: dict[str, Any] = {
    "schema": REVISION_BLOCK_SCHEMA_ID,
    "version": REVISION_BLOCK_VERSION,
    "metadata": metadata,
    "specs": specs or [],
    "requirements": requirements or [],
  }

  # Render as YAML
  yaml_content = yaml.safe_dump(
    data,
    sort_keys=False,
    indent=2,
    default_flow_style=False,
  )

  lines = [
    f"```yaml {REVISION_BLOCK_MARKER}",
    yaml_content.rstrip("\n"),
    "```",
  ]
  return "\n".join(lines)


__all__ = [
  "REVISION_BLOCK_MARKER",
  "REVISION_BLOCK_SCHEMA_ID",
  "REVISION_BLOCK_VERSION",
  "RevisionChangeBlock",
  "extract_revision_blocks",
  "load_revision_blocks",
  "render_revision_change_block",
]


register_block_schema(
  "revision.change",
  BlockSchema(
    name="revision.change",
    marker=REVISION_BLOCK_MARKER,
    version=REVISION_BLOCK_VERSION,
    renderer=render_revision_change_block,
    description="Documents changes to specs and requirements in a revision",
    metadata=REVISION_CHANGE_METADATA,
  ),
)
