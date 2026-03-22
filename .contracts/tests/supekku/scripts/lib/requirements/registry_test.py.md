# supekku.scripts.lib.requirements.registry_test

Tests for RequirementsRegistry public API and query surface.

## Classes

### TestFindByVerificationKind

Test RequirementsRegistry.find_by_verification_kind() method.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_all_kinds(self) -> None`: Filtering by all three kinds returns all requirements with coverage. - VT only
- `test_empty_list_returns_empty(self) -> None`: Empty kind list returns empty result.
- `test_multi_kind_or_logic(self) -> None`: Multi-value kind uses OR logic.
- `test_no_coverage_entries_excluded(self) -> None`: Requirements with empty coverage_entries never matched.
- `test_nonexistent_kind(self) -> None`: Non-existent kind returns empty list.
- `test_results_sorted_by_uid(self) -> None`: Results are sorted by uid.
- `test_single_kind_va(self) -> None`: Filter by VA returns requirements with VA entries. - VH only
- `test_single_kind_vh(self) -> None`: Filter by VH returns requirements with VH entries.
- `test_single_kind_vt(self) -> None`: Filter by VT returns requirements with VT entries.
- `_make_registry_with_entries(self) -> RequirementsRegistry`: Create a registry with records having diverse verification kinds.

### TestFindByVerificationStatus

Test RequirementsRegistry.find_by_verification_status() method.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_empty_list_returns_all(self) -> None`: Empty status list returns empty result (no filter match).
- `test_multi_status_or_logic(self) -> None`: Multi-value status uses OR logic: match if ANY entry matches ANY status.
- `test_no_coverage_entries_excluded(self) -> None`: Requirements with empty coverage_entries are never matched.
- `test_nonexistent_status(self) -> None`: Non-existent status returns empty list.
- `test_results_sorted_by_uid(self) -> None`: Results are sorted by uid.
- `test_single_status_failed(self) -> None`: Filter by 'failed' returns requirements with failed entries.
- `test_single_status_verified(self) -> None`: Filter by single status 'verified' returns matching requirements.
- `_make_registry_with_entries(self) -> RequirementsRegistry`: Create a registry with records having diverse coverage_entries.

### TestRequirementsRegistryReverseQueries

Test reverse relationship query methods for RequirementsRegistry.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_find_by_verified_by_case_sensitive(self) -> None`: Test that artifact ID matching is case-sensitive.
- `test_find_by_verified_by_empty_string(self) -> None`: Test find_by_verified_by with empty string returns empty list.
- `test_find_by_verified_by_exact_match(self) -> None`: Test finding requirements verified by specific artifact (exact match).
- `test_find_by_verified_by_glob_pattern(self) -> None`: Test finding requirements with glob pattern matching.
- `test_find_by_verified_by_glob_wildcard_positions(self) -> None`: Test glob patterns with wildcards in different positions.
- `test_find_by_verified_by_none(self) -> None`: Test find_by_verified_by with None returns empty list.
- `test_find_by_verified_by_nonexistent_artifact(self) -> None`: Test finding requirements for non-existent artifact returns empty list.
- `test_find_by_verified_by_returns_requirement_records(self) -> None`: Test that find_by_verified_by returns proper RequirementRecord objects.
- `test_find_by_verified_by_searches_both_fields(self) -> None`: Test that find_by_verified_by searches both verified_by and coverage_evidence.
- `test_find_by_verified_by_va_pattern(self) -> None`: Test finding requirements with VA (agent validation) artifacts.
- `test_find_by_verified_by_vt_prefix_pattern(self) -> None`: Test finding requirements with VT-PROD prefix.
- `_create_registry_with_verification(self, root) -> RequirementsRegistry`: Create requirements registry and manually add verification metadata.
- `_make_repo(self) -> Path`
- `_write_spec_with_requirements(self, root, spec_id, requirements) -> None`: Write a spec file with specific requirements.

### TestRequirementsRegistryStandardSurface

Tests for ADR-009 standard registry surface: find, collect, iter, filter.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_collect_returns_copy(self) -> None`
- `test_collect_returns_dict(self) -> None` - -- collect() ------------------------------------------------------------
- `test_constructor_positional_still_works(self) -> None`
- `test_constructor_with_root_keyword(self) -> None` - -- constructor ----------------------------------------------------------
- `test_filter_and_logic(self) -> None`
- `test_filter_by_kind(self) -> None`
- `test_filter_by_spec(self) -> None`
- `test_filter_by_status(self) -> None` - -- filter() -------------------------------------------------------------
- `test_filter_by_tag(self) -> None`
- `test_filter_no_matches_returns_empty(self) -> None`
- `test_filter_no_params_returns_all(self) -> None`
- `test_find_returns_none_for_missing(self) -> None`
- `test_find_returns_record(self) -> None` - -- find() ---------------------------------------------------------------
- `test_iter_filters_by_status(self) -> None`
- `test_iter_yields_all(self) -> None` - -- iter() ---------------------------------------------------------------
- `_make_registry(self) -> tuple[Tuple[RequirementsRegistry, Path]]`

### TestTerminalStatusGuard

VT-081-002: Terminal statuses not overwritten by coverage derivation.

**Inherits from:** unittest.TestCase

#### Methods

- `test_deprecated_not_overwritten_by_coverage(self) -> None`: A deprecated requirement keeps its status despite verified coverage.
- `test_deprecated_status_constants(self) -> None`: deprecated and superseded are valid requirement statuses.
- `test_superseded_not_overwritten_by_coverage(self) -> None`: A superseded requirement keeps its status despite coverage.
- `_make_repo(self) -> Path`
- `_write_spec(self, root, spec_id, body) -> Path`
