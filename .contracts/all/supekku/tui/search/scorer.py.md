# supekku.tui.search.scorer

Weighted fuzzy scorer for cross-artifact search.

Pure functions — no TUI state, no side effects.

Design reference: DR-087 DEC-087-02.

## Constants

- `WEIGHT_ATTRIBUTE`
- `WEIGHT_OWN_ID` - DR-087 DEC-087-02.
- `WEIGHT_RELATION_TARGET`
- `WEIGHT_TITLE` - DR-087 DEC-087-02.
- `_DEFAULT_LIMIT`
- `_PREFIX_BONUS` - Bonus for matching at the start of the text.
- `_SUBSTRING_BONUS` - Bonus for substring (contiguous) matches vs scattered subsequence.

## Functions

- `_field_weight(field_name) -> float`: Return the scoring weight for a searchable field.
- `_fuzzy_score(query, text) -> float`: Score _query_ against _text_ using linear subsequence matching.

Returns 0.0 if _query_ is not a subsequence of _text_.
Otherwise returns a score based on match compactness, contiguity,
and position. O(n) per candidate — no combinatorial explosion.

- `score_entry(entry, query) -> float`: Score a single :class:`SearchEntry` against _query_.

Returns `max(weight * fuzzy_score)` across all searchable fields
and relation targets. Returns 0.0 when nothing matches.

- `search(query, index) -> list[SearchEntry]`: Score, filter, sort, and truncate search results.

Returns up to _limit_ entries with score > 0, sorted by descending score.
