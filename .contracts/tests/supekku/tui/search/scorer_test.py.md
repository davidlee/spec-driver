# supekku.tui.search.scorer_test

Tests for search scorer (VT-087-001, VT-087-003).

## Functions

- `_se() -> SearchEntry`: Build a SearchEntry for testing.

## Classes

### TestFuzzyScore

Unit tests for the linear fuzzy scorer.

#### Methods

- `test_case_insensitive(self)`
- `test_contiguous_beats_scattered(self)`
- `test_empty_query_returns_zero(self)`
- `test_long_query_stays_fast(self)`: Regression: Matcher was exponential on long queries with scattered chars.
- `test_no_subsequence_returns_zero(self)`
- `test_prefix_match_beats_mid_match(self)`
- `test_substring_match_scores_high(self)`

### TestScoreEntry

VT-087-001: Scorer weight application and field priority.

#### Methods

- `test_attribute_match(self)`
- `test_empty_query_returns_zero(self)`
- `test_id_match_uses_own_id_weight(self)`
- `test_no_match_returns_zero(self)`
- `test_per_tag_scoring(self)`
- `test_relation_target_match(self)`
- `test_title_match_lower_than_id_match(self)`

### TestSearch

Test the search() convenience function.

#### Methods

- `test_empty_query_returns_empty(self)`
- `test_filters_zero_scores(self)`
- `test_limit_respected(self)`
- `test_no_matches_returns_empty(self)`
- `test_returns_sorted_by_score(self)`

### TestWeightOrdering

VT-087-003: Own-ID outranks relation-target for equivalent match quality.

#### Methods

- `test_own_id_beats_relation_target_for_same_query(self)`: Artifact with own ID 'DE-085' should outrank artifact that
references DE-085 via relation, when query is 'DE-085'.
- `test_perfect_relation_beats_weak_own_id(self)`: A perfect relation match (0.5 * high) should beat a weak
own-ID match (1.0 * low).
- `test_weight_constants_ordering(self)`: Verify the weight hierarchy is as documented.
