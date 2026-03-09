"""Cross-artifact fuzzy search with weighted scoring.

Pure-function search module — no TUI imports.  Reusable by any consumer
that needs weighted fuzzy search across artifact registries.

Design reference: DR-087.
"""

from supekku.tui.search.index import SearchEntry, build_search_index
from supekku.tui.search.scorer import score_entry, search

__all__ = [
  "SearchEntry",
  "build_search_index",
  "score_entry",
  "search",
]
