"""Weighted fuzzy scorer for cross-artifact search.

Pure functions — no TUI state, no side effects.

Design reference: DR-087 DEC-087-02.
"""

from __future__ import annotations

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

# Bonus for substring (contiguous) matches vs scattered subsequence.
_SUBSTRING_BONUS = 2.0
# Bonus for matching at the start of the text.
_PREFIX_BONUS = 1.5


def _field_weight(field_name: str) -> float:
  """Return the scoring weight for a searchable field."""
  return _FIELD_WEIGHTS.get(field_name, WEIGHT_ATTRIBUTE)


def _fuzzy_score(query: str, text: str) -> float:
  """Score *query* against *text* using linear subsequence matching.

  Returns 0.0 if *query* is not a subsequence of *text*.
  Otherwise returns a score based on match compactness, contiguity,
  and position.  O(n) per candidate — no combinatorial explosion.
  """
  q_lower = query.lower()
  t_lower = text.lower()

  # Fast path: contiguous substring match.
  sub_pos = t_lower.find(q_lower)
  if sub_pos >= 0:
    score = len(q_lower) * _SUBSTRING_BONUS
    if sub_pos == 0:
      score *= _PREFIX_BONUS
    return score

  # Subsequence match: greedy left-to-right scan.
  positions: list[int] = []
  start = 0
  for ch in q_lower:
    idx = t_lower.find(ch, start)
    if idx < 0:
      return 0.0
    positions.append(idx)
    start = idx + 1

  # Score: query length penalised by how spread out the match is.
  span = positions[-1] - positions[0] + 1
  compactness = len(q_lower) / span
  return len(q_lower) * compactness


def score_entry(entry: SearchEntry, query: str) -> float:
  """Score a single :class:`SearchEntry` against *query*.

  Returns ``max(weight * fuzzy_score)`` across all searchable fields
  and relation targets.  Returns 0.0 when nothing matches.
  """
  if not query:
    return 0.0

  best = 0.0

  # Score searchable fields with per-field weights.
  for field_name, text in entry.searchable_fields.items():
    if not text:
      continue
    raw = _fuzzy_score(query, text)
    if raw > 0:
      weighted = _field_weight(field_name) * raw
      best = max(best, weighted)

  # Score each relation target individually (DEC-087-02).
  for target in entry.relation_targets:
    raw = _fuzzy_score(query, target)
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

  scored = [(entry, score_entry(entry, query)) for entry in index]
  hits = [(e, s) for e, s in scored if s > 0]
  hits.sort(key=lambda pair: pair[1], reverse=True)
  return [e for e, _s in hits[:limit]]
