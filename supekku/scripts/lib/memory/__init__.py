"""Memory domain — models, registry, selection, and ID utilities."""

from __future__ import annotations

from supekku.scripts.lib.memory.ids import (
  extract_type_from_id,
  filename_from_id,
  normalize_memory_id,
  validate_memory_id,
)
from supekku.scripts.lib.memory.models import MemoryRecord
from supekku.scripts.lib.memory.registry import MemoryRegistry
from supekku.scripts.lib.memory.selection import (
  MatchContext,
  is_surfaceable,
  matches_scope,
  normalize_path,
  scope_specificity,
  select,
  sort_key,
)

__all__: list[str] = [
  "MatchContext",
  "MemoryRecord",
  "MemoryRegistry",
  "extract_type_from_id",
  "filename_from_id",
  "is_surfaceable",
  "matches_scope",
  "normalize_memory_id",
  "normalize_path",
  "scope_specificity",
  "select",
  "sort_key",
  "validate_memory_id",
]
