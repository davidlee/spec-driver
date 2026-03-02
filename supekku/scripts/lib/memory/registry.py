"""MemoryRegistry — discovery, parsing, and querying of memory artifacts."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

from supekku.scripts.lib.core.repo import find_repo_root
from supekku.scripts.lib.core.spec_utils import load_markdown_file

from .models import MemoryRecord

if TYPE_CHECKING:
  from collections.abc import Iterator


class MemoryRegistry:
  """Registry for discovering and querying memory artifact files.

  Follows the same collect/find/iter/filter pattern as DecisionRegistry.
  Memory files are expected to be named MEM-*.md in the memory directory.
  """

  def __init__(
    self,
    *,
    root: Path | None = None,
    directory: Path | None = None,
  ) -> None:
    self.root = find_repo_root(root)
    self.directory = directory or (self.root / "memory")

  def collect(self) -> dict[str, MemoryRecord]:
    """Discover and parse all MEM-*.md files into MemoryRecords.

    Returns:
      Dictionary mapping memory ID to MemoryRecord.
    """
    records: dict[str, MemoryRecord] = {}
    if not self.directory.exists():
      return records

    for mem_file in self.directory.glob("MEM-*.md"):
      try:
        record = self._parse_memory_file(mem_file)
        if record:
          records[record.id] = record
      except (ValueError, KeyError, FileNotFoundError):
        continue

    return records

  def _parse_memory_file(self, path: Path) -> MemoryRecord | None:
    """Parse a single memory file into a MemoryRecord.

    Args:
      path: Path to the MEM-*.md file.

    Returns:
      MemoryRecord or None if the file can't be parsed.
    """
    frontmatter, _ = load_markdown_file(path)
    if not frontmatter:
      return None

    # Validate ID is present (from frontmatter or filename)
    filename_match = re.match(r"MEM-(\d+)", path.name)
    if not filename_match:
      return None

    file_id = f"MEM-{filename_match.group(1)}"
    if not frontmatter.get("id"):
      frontmatter["id"] = file_id

    return MemoryRecord.from_frontmatter(path, frontmatter)

  def find(self, memory_id: str) -> MemoryRecord | None:
    """Find a specific memory record by ID.

    Args:
      memory_id: The memory ID (e.g. "MEM-001").

    Returns:
      MemoryRecord or None if not found.
    """
    return self.collect().get(memory_id)

  def iter(self, *, status: str | None = None) -> Iterator[MemoryRecord]:
    """Iterate over memory records, optionally filtered by status.

    Args:
      status: If provided, yield only records with this status.

    Yields:
      MemoryRecord instances.
    """
    for record in self.collect().values():
      if status is None or record.status == status:
        yield record

  def filter(
    self,
    *,
    memory_type: str | None = None,
    status: str | None = None,
    tag: str | None = None,
  ) -> list[MemoryRecord]:
    """Filter memory records by multiple criteria (AND logic).

    Args:
      memory_type: Filter by memory_type field.
      status: Filter by status field.
      tag: Filter by tag membership.

    Returns:
      List of matching MemoryRecords.
    """
    results = []
    for record in self.iter():
      if memory_type and record.memory_type != memory_type:
        continue
      if status and record.status != status:
        continue
      if tag and tag not in record.tags:
        continue
      results.append(record)
    return results
