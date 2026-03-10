# supekku.tui.search.scorer

Weighted fuzzy scorer for cross-artifact search.

Pure functions — no TUI state, no side effects.

Design reference: DR-087 DEC-087-02.

## Constants

- `WEIGHT_ATTRIBUTE`
- `WEIGHT_OWN_ID` - DR-087 DEC-087-02.
- `WEIGHT_RELATION_TARGET`
- `WEIGHT_TITLE` - DR-087 DEC-087-02.

## Functions

- `score_entry(entry, query) -> float`: Score a single :class:`SearchEntry` against *query*.

Returns ``max(weight * fuzzy_score)`` across all searchable fields
and relation targets.  Returns 0.0 when nothing matches.
- `search(query, index) -> list[SearchEntry]`: Score, filter, sort, and truncate search results.

Returns up to *limit* entries with score > 0, sorted by descending score.
