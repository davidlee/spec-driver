# supekku.scripts.lib.memory.selection_test

Tests for memory selection — scope matching, specificity, and path normalization.

## Functions

- `_record() -> MemoryRecord`: Build a MemoryRecord with defaults for testing.

## Classes

### TestIsSurfaceable

Status filtering and thread recency rules.

**Inherits from:** unittest.TestCase

#### Methods

- `test_active_is_surfaceable(self) -> None`
- `test_deprecated_excluded(self) -> None`
- `test_draft_excluded_by_default(self) -> None`
- `test_draft_included_when_opted_in(self) -> None`
- `test_obsolete_excluded(self) -> None`
- `test_skip_status_filter_includes_deprecated(self) -> None`
- `test_skip_status_filter_includes_draft(self) -> None`
- `test_skip_status_filter_still_checks_threads(self) -> None`: Thread recency check applies even with skip_status_filter.
- `test_superseded_excluded(self) -> None`
- `test_thread_excluded_when_no_verified_date(self) -> None`
- `test_thread_excluded_when_not_scope_matched(self) -> None`
- `test_thread_excluded_when_scope_matches_but_stale(self) -> None`
- `test_thread_excluded_without_context(self) -> None`
- `test_thread_included_with_matching_scope_and_recent(self) -> None`

### TestMatchesScopeCommands

Scope matching via scope.commands using token-prefix.

**Inherits from:** unittest.TestCase

#### Methods

- `test_exact_command_match(self) -> None`
- `test_multiple_scope_commands(self) -> None`
- `test_no_match_different_command(self) -> None`
- `test_no_match_without_context_command(self) -> None`
- `test_no_substring_false_positive(self) -> None`: 'test' should NOT match 'pytest'.
- `test_no_substring_false_positive_build(self) -> None`: 'build' should NOT match 'rebuild'.
- `test_single_token_match(self) -> None`
- `test_two_token_prefix_match(self) -> None`

### TestMatchesScopeComposition

OR logic across match dimensions.

**Inherits from:** unittest.TestCase

#### Methods

- `test_command_match_suffices(self) -> None`
- `test_no_scope_no_tags_no_match(self) -> None`: Records with no scope and no tags never match via context.
- `test_path_match_suffices(self) -> None`
- `test_tag_match_suffices(self) -> None`

### TestMatchesScopeGlobs

Scope matching via scope.globs with proper ** support.

**Inherits from:** unittest.TestCase

#### Methods

- `test_doublestar_glob(self) -> None`
- `test_doublestar_universal(self) -> None`: scope.globs: ['**'] matches everything.
- `test_glob_does_not_match_without_context_paths(self) -> None`
- `test_no_glob_match(self) -> None`
- `test_star_glob(self) -> None`

### TestMatchesScopePathExact

Scope matching via scope.paths (exact and prefix).

**Inherits from:** unittest.TestCase

#### Methods

- `test_exact_match(self) -> None`
- `test_multiple_context_paths(self) -> None`
- `test_multiple_scope_paths(self) -> None`
- `test_no_match(self) -> None`
- `test_prefix_match_trailing_slash(self) -> None`: scope.paths entry with trailing / matches files under that dir.
- `test_prefix_no_match_partial_dirname(self) -> None`: 'src/auth/' should NOT match 'src/authorization/x.ts'.

### TestMatchesScopeTags

Scope matching via tag intersection.

**Inherits from:** unittest.TestCase

#### Methods

- `test_empty_context_tags_no_match(self) -> None`: Empty context.tags should not match even if record has tags.
- `test_empty_record_tags_no_match(self) -> None`
- `test_no_tag_match(self) -> None`
- `test_tag_match(self) -> None`

### TestNormalizePath

Path normalization to repo-relative POSIX form.

**Inherits from:** unittest.TestCase

#### Methods

- `test_already_relative(self) -> None`
- `test_dot_only(self) -> None`
- `test_empty_string(self) -> None`
- `test_no_double_slashes(self) -> None`
- `test_preserves_trailing_slash(self) -> None`
- `test_resolves_parent_refs(self) -> None`
- `test_strips_leading_dot_slash(self) -> None`
- `test_strips_leading_slash_relative_to_repo(self) -> None`

### TestScopeSpecificity

Specificity scoring: paths=3 > globs=2 > commands=1 > tags=0.

**Inherits from:** unittest.TestCase

#### Methods

- `test_command_specificity(self) -> None`
- `test_glob_specificity(self) -> None`
- `test_max_across_dimensions(self) -> None`: When multiple dimensions match, take the highest.
- `test_no_context_specificity_zero(self) -> None`
- `test_no_match_specificity_zero(self) -> None`
- `test_path_exact_specificity(self) -> None`
- `test_path_prefix_specificity(self) -> None`
- `test_tag_only_specificity(self) -> None`

### TestSelect

End-to-end selection pipeline.

**Inherits from:** unittest.TestCase

#### Methods

- `test_context_filters_by_scope(self) -> None`: With context, only scope-matched records returned.
- `test_determinism_multiple_runs(self) -> None`: Same input set produces identical output every run.
- `test_empty_input(self) -> None`
- `test_include_draft(self) -> None` - high second
- `test_limit(self) -> None`
- `test_no_context_returns_non_excluded(self) -> None`: Without context, all non-excluded records returned.
- `test_ordering_is_deterministic(self) -> None`: Records sorted by severity > weight > specificity > verified. - tags only, no --match-tag
- `_make_records(self) -> list[MemoryRecord]`

### TestSortKey

Deterministic sort key per JAMMS §5.4.

**Inherits from:** unittest.TestCase

#### Methods

- `test_deterministic_across_runs(self) -> None`: Same input set always produces same sort order.
- `test_id_tiebreak(self) -> None`: Lexicographic ID as final tie-breaker.
- `test_missing_severity_defaults_to_none(self) -> None`
- `test_missing_weight_defaults_to_zero(self) -> None`
- `test_severity_ordering(self) -> None`: critical < high < medium < low < none in sort order.
- `test_specificity_tiebreak(self) -> None`: Higher specificity sorts first within same severity/weight.
- `test_unknown_severity_treated_as_none(self) -> None`
- `test_verified_recency_tiebreak(self) -> None`: More recently verified sorts first; null last. - paths=3 > commands=1
- `test_weight_tiebreak_descending(self) -> None`: Higher weight sorts first within same severity.
