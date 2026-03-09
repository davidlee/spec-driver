# supekku.scripts.lib.requirements.registry_test

Tests for requirements module.

## Classes

### RequirementsRegistryTest

Test cases for RequirementsRegistry functionality.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_category_merge_precedence(self) -> None`: VT-017-002: Test category merge with body precedence.
- `test_category_parsing_frontmatter(self) -> None`: VT-017-001: Test category extraction from frontmatter.
- `test_category_parsing_inline_syntax(self) -> None`: VT-017-001: Test category extraction from inline syntax.
- `test_category_serialization_round_trip(self) -> None`: VT-017-002: Test category survives serialization round-trip.
- `test_compute_status_from_coverage(self) -> None`: Unit test for status computation from coverage entries.
- `test_compute_status_from_coverage_ignores_unknown_statuses(self) -> None`: VT-043-002: Unknown statuses are filtered out of derivation.
- `test_coverage_drift_detection(self) -> None`: Registry emits warnings for coverage conflicts. - Planned
- `test_coverage_evidence_field_serialization(self) -> None`: VT-910: RequirementRecord with coverage_evidence serializes correctly.
- `test_coverage_evidence_merge(self) -> None`: VT-910: RequirementRecord.merge() combines coverage_evidence correctly.
- `test_coverage_sync_populates_coverage_evidence(self) -> None`: VT-911: Coverage sync populates coverage_evidence, not verified_by.
- `test_delta_relationships_block_marks_implemented_by(self) -> None`: Test that delta relationship blocks mark requirements as implemented.
- `test_move_requirement_updates_primary_spec(self) -> None`: Test that moving a requirement updates its primary spec and UID.
- `test_qualified_requirement_format(self) -> None`: Test extraction of requirements with fully-qualified IDs (SPEC-XXX.FR-001).
- `test_relationship_block_adds_collaborators(self) -> None`: Test that spec relationship blocks add collaborator specs to requirements.
- `test_revision_block_moves_requirement_and_sets_collaborators(self) -> None`: Test that revision blocks can move requirements and set collaborator specs.
- `test_search_filters(self) -> None`: Test that search can filter requirements by text query.
- `test_sync_collects_change_relations(self) -> None`: Test syncing collects relations from delta, revision, audit artifacts.
- `test_sync_creates_entries(self) -> None`: Test that syncing from specs creates registry entries for requirements.
- `test_sync_preserves_status(self) -> None`: Test that re-syncing preserves manually set requirement statuses.
- `test_sync_processes_coverage_blocks(self) -> None`: VT-902: Registry sync updates lifecycle from coverage blocks.
- `_create_change_bundle(self, root, bundle, file_id, kind) -> Path`
- `_make_repo(self) -> Path`
- `_write_revision_with_block(self, root, revision_id, block_yaml) -> Path`
- `_write_spec(self, root, spec_id, body) -> None`

### TestBacklogRequirementSync

VT-SYNC-076-002: Backlog items synced to requirements registry.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_sync_backlog_records_in_seen_set(self) -> None`: Backlog-sourced records are added to seen and not purged by cleanup.
- `test_sync_discovers_backlog_requirements(self) -> None`: Backlog items with heading-format requirements appear in registry.
- `_make_backlog_item(self, item_id, kind, body) -> Path`: Create a minimal backlog item file and return its path.

### TestCoverageReplacementSemantics

VT-081-001: Coverage evidence is rebuilt fresh each sync.

**Inherits from:** unittest.TestCase

#### Methods

- `test_coverage_evidence_replaced_not_accumulated(self) -> None`: Removing an artefact from a coverage block removes it from evidence.
- `test_removed_coverage_block_clears_evidence(self) -> None`: Removing entire coverage block clears evidence for affected requirements.
- `test_sync_idempotency(self) -> None`: Running sync twice produces identical registry (NF-002).
- `_make_repo(self) -> Path`
- `_write_spec(self, root, spec_id, body) -> Path`: Write a spec file and return the tech specs root directory.

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

### TestInlineRequirementTags

VT-081-003: Inline tag extraction from [tag1, tag2] syntax.

**Inherits from:** unittest.TestCase

#### Methods

- `test_filter_by_tag(self) -> None`: filter(tag=...) returns only tagged requirements.
- `test_tags_extracted_from_inline_syntax(self) -> None`: Tags in [brackets] after category are parsed.
- `test_tags_merged_on_multi_spec_sync(self) -> None`: Tags from multiple specs are unioned during merge.
- `test_tags_populated_in_registry_after_save_load(self) -> None`: Tags survive save/load round-trip.
- `_make_repo(self) -> Path`
- `_write_spec(self, root, spec_id, body) -> Path`

### TestRequirementCoverageEntries

Test that coverage_entries field is populated during registry sync.

After _apply_coverage_blocks(), each RequirementRecord should have a
coverage_entries field containing the structured verification data
(artefact, kind, status) from coverage blocks.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_coverage_entries_contain_correct_data(self) -> None`: Coverage entries preserve artefact ID, kind, and status from blocks.
- `test_coverage_entries_empty_for_no_coverage(self) -> None`: Requirements without coverage blocks have empty coverage_entries. - From spec + plan
- `test_coverage_entries_multiple_statuses(self) -> None`: Requirements with entries from multiple sources aggregate all entries.
- `test_coverage_entries_populated_after_sync(self) -> None`: Syncing with coverage blocks populates coverage_entries on records.
- `test_coverage_entries_serialization(self) -> None`: coverage_entries survives to_dict/from_dict round-trip.
- `test_unknown_coverage_status_excluded_from_derivation(self) -> None`: VT-043-001: Entries with unknown statuses must not influence derived status.
- `_make_repo(self) -> Path`

### TestRequirementHeadingRegex

VT-REGEX-076-001: _REQUIREMENT_HEADING regex matches dotted backlog format.

**Inherits from:** unittest.TestCase

#### Methods

- `test_matches_dash_separator(self) -> None`
- `test_matches_fr_dotted(self) -> None`
- `test_matches_h2(self) -> None`
- `test_matches_nf_dotted(self) -> None`
- `test_rejects_bullet_format(self) -> None`
- `test_rejects_non_dotted(self) -> None`

### TestRequirementRecordToDict

Tests for RequirementRecord.to_dict() serialization.

**Inherits from:** unittest.TestCase

#### Methods

- `test_to_dict_ext_id_only(self) -> None`: ext_id without ext_url — only ext_id appears.
- `test_to_dict_includes_ext_id_ext_url_when_set(self) -> None`: Populated ext_id/ext_url should appear in serialized dict.
- `test_to_dict_omits_ext_id_ext_url_when_empty(self) -> None`: Empty ext_id/ext_url should not appear in serialized dict.

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

### TestSourceKindFields

VT-UPSERT-076-003 / VT-COMPAT-076-005: source fields.

**Inherits from:** unittest.TestCase

#### Methods

- `test_defaults_to_empty(self) -> None`
- `test_from_dict_defaults_missing(self) -> None`
- `test_from_dict_reads_present(self) -> None`
- `test_merge_incoming_wins(self) -> None`
- `test_merge_preserves_existing_when_incoming_empty(self) -> None`
- `test_roundtrip_serialization(self) -> None`
- `test_to_dict_includes_when_set(self) -> None`
- `test_to_dict_omits_when_empty(self) -> None`

### TestTerminalStatusGuard

VT-081-002: Terminal statuses not overwritten by coverage derivation.

**Inherits from:** unittest.TestCase

#### Methods

- `test_deprecated_not_overwritten_by_coverage(self) -> None`: A deprecated requirement keeps its status despite verified coverage.
- `test_deprecated_status_constants(self) -> None`: deprecated and superseded are valid requirement statuses.
- `test_superseded_not_overwritten_by_coverage(self) -> None`: A superseded requirement keeps its status despite coverage.
- `_make_repo(self) -> Path`
- `_write_spec(self, root, spec_id, body) -> Path`

### TestUpsertRecordProvenance

VT-UPSERT-076-003: _upsert_record stamps source provenance.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_upsert_stamps_source_kind_on_create(self) -> None`
- `test_upsert_stamps_source_kind_on_merge(self) -> None`
