"""Shared logic for creating memory artifacts.

Memory IDs are user-supplied semantic dot-separated identifiers
(e.g., mem.pattern.cli.skinny). See ids.py for validation rules.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import yaml

from supekku.scripts.lib.core.events import record_artifact
from supekku.scripts.lib.memory.ids import (
  extract_type_from_id,
  filename_from_id,
  normalize_memory_id,
)
from supekku.scripts.lib.memory.registry import MemoryRegistry


@dataclass
class MemoryCreationOptions:
  """Options for creating a new memory artifact."""

  memory_id: str
  name: str
  memory_type: str
  status: str = "active"
  confidence: str = "medium"
  tags: list[str] = field(default_factory=list)
  summary: str = ""


@dataclass
class MemoryCreationResult:
  """Result of creating a new memory artifact."""

  memory_id: str
  path: Path
  filename: str
  warnings: list[str] = field(default_factory=list)


class MemoryAlreadyExistsError(Exception):
  """Raised when attempting to create a memory that already exists."""


def build_memory_frontmatter(
  memory_id: str,
  options: MemoryCreationOptions,
) -> dict:
  """Build frontmatter dictionary for a memory artifact.

  Args:
    memory_id: Canonical memory ID (e.g., 'mem.pattern.cli.skinny').
    options: Creation options.

  Returns:
    Dictionary containing memory frontmatter.
  """
  today = date.today().isoformat()
  return {
    "id": memory_id,
    "name": options.name,
    "kind": "memory",
    "status": options.status,
    "memory_type": options.memory_type,
    "created": today,
    "updated": today,
    "verified": today,
    "confidence": options.confidence or "medium",
    "tags": options.tags,
    "summary": options.summary,
  }


def create_memory(
  registry: MemoryRegistry,
  options: MemoryCreationOptions,
) -> MemoryCreationResult:
  """Create a new memory artifact with user-supplied semantic ID.

  Args:
    registry: Memory registry for uniqueness check.
    options: Memory creation options (must include memory_id).

  Returns:
    MemoryCreationResult with ID, path, filename, and any warnings.

  Raises:
    ValueError: If the memory ID is malformed.
    MemoryAlreadyExistsError: If a memory with this ID already exists.
  """
  canonical_id = normalize_memory_id(options.memory_id)
  record_artifact(canonical_id)
  result_warnings: list[str] = []

  # Warn if ID type segment disagrees with memory_type
  id_type = extract_type_from_id(canonical_id)
  if id_type and id_type != options.memory_type:
    msg = (
      f"ID type segment '{id_type}' differs from memory_type '{options.memory_type}'"
    )
    result_warnings.append(msg)
    warnings.warn(msg, UserWarning, stacklevel=2)

  # Check uniqueness against registry
  existing = registry.collect()
  if canonical_id in existing:
    msg = f"Memory already exists: {canonical_id}"
    raise MemoryAlreadyExistsError(msg)

  filename = filename_from_id(canonical_id)
  memory_path = registry.directory / filename

  if memory_path.exists():
    msg = f"Memory file already exists: {memory_path}"
    raise MemoryAlreadyExistsError(msg)

  frontmatter = build_memory_frontmatter(canonical_id, options)
  body = f"# {options.name}\n\n## Summary\n\n## Context\n"
  frontmatter_yaml = yaml.safe_dump(frontmatter, sort_keys=False)
  full_content = f"---\n{frontmatter_yaml}---\n\n{body}"

  memory_path.parent.mkdir(parents=True, exist_ok=True)
  memory_path.write_text(full_content, encoding="utf-8")

  return MemoryCreationResult(
    memory_id=canonical_id,
    path=memory_path,
    filename=filename,
    warnings=result_warnings,
  )
