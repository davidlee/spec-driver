"""Memory domain — models, registry, and selection for memory artifacts."""

from __future__ import annotations

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
  "is_surfaceable",
  "matches_scope",
  "normalize_path",
  "scope_specificity",
  "select",
  "sort_key",
]
