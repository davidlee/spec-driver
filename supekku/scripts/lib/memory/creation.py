"""Shared logic for creating memory artifacts."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import yaml

from supekku.scripts.lib.core import slugify
from supekku.scripts.lib.memory.registry import MemoryRegistry


@dataclass
class MemoryCreationOptions:
  """Options for creating a new memory artifact."""

  name: str
  memory_type: str
  status: str = "active"
  tags: list[str] = field(default_factory=list)
  summary: str = ""


@dataclass
class MemoryCreationResult:
  """Result of creating a new memory artifact."""

  memory_id: str
  path: Path
  filename: str


class MemoryAlreadyExistsError(Exception):
  """Raised when attempting to create a memory file that already exists."""


def generate_next_memory_id(registry: MemoryRegistry) -> str:
  """Generate the next available memory ID.

  Args:
    registry: Memory registry to scan for existing IDs.

  Returns:
    Next available memory ID (e.g., "MEM-003").
  """
  memories = registry.collect()
  max_id = 0
  for memory_id in memories:
    match = re.match(r"MEM-(\d+)", memory_id)
    if match:
      max_id = max(max_id, int(match.group(1)))

  next_id = max_id + 1
  return f"MEM-{next_id:03d}"


def build_memory_frontmatter(
  memory_id: str,
  options: MemoryCreationOptions,
) -> dict:
  """Build frontmatter dictionary for a memory artifact.

  Args:
    memory_id: Memory identifier (e.g., "MEM-001").
    options: Creation options (name, memory_type, status, tags, summary).

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
    "tags": options.tags,
    "summary": options.summary,
  }


def create_memory(
  registry: MemoryRegistry,
  options: MemoryCreationOptions,
) -> MemoryCreationResult:
  """Create a new memory artifact with the next available ID.

  Args:
    registry: Memory registry for finding next ID.
    options: Memory creation options.

  Returns:
    MemoryCreationResult with ID, path, and filename.

  Raises:
    MemoryAlreadyExistsError: If memory file already exists at computed path.
  """
  memory_id = generate_next_memory_id(registry)

  title_slug = slugify(options.name)
  filename = f"{memory_id}-{title_slug}.md"
  memory_path = registry.directory / filename

  if memory_path.exists():
    msg = f"Memory file already exists: {memory_path}"
    raise MemoryAlreadyExistsError(msg)

  frontmatter = build_memory_frontmatter(memory_id, options)

  body = f"# {options.name}\n\n## Summary\n\n## Context\n"

  frontmatter_yaml = yaml.safe_dump(frontmatter, sort_keys=False)
  full_content = f"---\n{frontmatter_yaml}---\n\n{body}"

  memory_path.parent.mkdir(parents=True, exist_ok=True)
  memory_path.write_text(full_content, encoding="utf-8")

  return MemoryCreationResult(
    memory_id=memory_id,
    path=memory_path,
    filename=filename,
  )
