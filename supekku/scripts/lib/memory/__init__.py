"""Memory domain — models, registry, selection, ID utilities, and links."""

from __future__ import annotations

from supekku.scripts.lib.memory.ids import (
  extract_type_from_id,
  filename_from_id,
  normalize_memory_id,
  validate_memory_id,
)
from supekku.scripts.lib.memory.links import (
  LinkGraphNode,
  LinkResolutionResult,
  MissingLink,
  ParsedLink,
  ResolvedLink,
  compute_backlinks,
  expand_link_graph,
  links_to_frontmatter,
  parse_links,
  resolve_all_links,
  resolve_parsed_link,
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
  "LinkGraphNode",
  "LinkResolutionResult",
  "MatchContext",
  "MemoryRecord",
  "MemoryRegistry",
  "MissingLink",
  "ParsedLink",
  "ResolvedLink",
  "extract_type_from_id",
  "filename_from_id",
  "is_surfaceable",
  "compute_backlinks",
  "expand_link_graph",
  "links_to_frontmatter",
  "matches_scope",
  "normalize_memory_id",
  "normalize_path",
  "parse_links",
  "resolve_all_links",
  "resolve_parsed_link",
  "scope_specificity",
  "select",
  "sort_key",
  "validate_memory_id",
]
