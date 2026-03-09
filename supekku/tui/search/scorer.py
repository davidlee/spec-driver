"""Weighted fuzzy scorer for cross-artifact search.

Pure functions — no TUI state, no side effects.

Design reference: DR-087 DEC-087-02.
"""

from __future__ import annotations

from textual.fuzzy import Matcher

from supekku.tui.search.index import (
  FIELD_ID,
  FIELD_TITLE,
  SearchEntry,
)

# Scoring weights (POL-002: named constants, not magic numbers).
# DR-087 DEC-087-02.
WEIGHT_OWN_ID = 1.0
WEIGHT_TITLE = 0.7
WEIGHT_RELATION_TARGET = 0.5
WEIGHT_ATTRIBUTE = 0.4

_FIELD_WEIGHTS: dict[str, float] = {
  FIELD_ID: WEIGHT_OWN_ID,
  FIELD_TITLE: WEIGHT_TITLE,
}

_DEFAULT_LIMIT = 50


def _field_weight(field_name: str) -> float:
  """Return the scoring weight for a searchable field."""
  return _FIELD_WEIGHTS.get(field_name, WEIGHT_ATTRIBUTE)


def score_entry(query: str, entry: SearchEntry) -> float:
  """Score a single :class:`SearchEntry` against *query*.

  Returns ``max(weight * fuzzy_score)`` across all searchable fields
  and relation targets.  Returns 0.0 when nothing matches.
  """
  if not query:
    return 0.0

  matcher = Matcher(query)
  best = 0.0

  # Score searchable fields with per-field weights.
  for field_name, text in entry.searchable_fields.items():
    if not text:
      continue
    raw = matcher.match(text)
    if raw > 0:
      weighted = _field_weight(field_name) * raw
      best = max(best, weighted)

  # Score each relation target individually (DEC-087-02).
  for target in entry.relation_targets:
    raw = matcher.match(target)
    if raw > 0:
      weighted = WEIGHT_RELATION_TARGET * raw
      best = max(best, weighted)

  return best


def search(
  query: str,
  index: list[SearchEntry],
  *,
  limit: int = _DEFAULT_LIMIT,
) -> list[SearchEntry]:
  """Score, filter, sort, and truncate search results.

  Returns up to *limit* entries with score > 0, sorted by descending score.
  """
  if not query:
    return []

  scored = [(entry, score_entry(query, entry)) for entry in index]
  hits = [(e, s) for e, s in scored if s > 0]
  hits.sort(key=lambda pair: pair[1], reverse=True)
  return [e for e, _s in hits[:limit]]
