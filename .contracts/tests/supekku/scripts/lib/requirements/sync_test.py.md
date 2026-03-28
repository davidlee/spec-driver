# supekku.scripts.lib.requirements.sync_test

Tests for requirement synchronization.

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
- `_write_spec(self, root, spec_id, body) -> Path`

### TestBacklogRequirementSync

VT-SYNC-076-002: Backlog items synced to requirements registry.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_sync_backlog_records_in_seen_set(self) -> None`: Backlog-sourced records are added to seen and not purged by cleanup.
- `test_sync_discovers_backlog_requirements(self) -> None`: Backlog items with heading-format requirements appear in registry.
- `_make_backlog_item(self, item_id, kind, body) -> Path`: Create a minimal backlog item file and return its path.

### TestBreakoutFrontmatterSync

DE-095: Sync reads tags/ext_id/ext_url from breakout requirement files.

**Inherits from:** unittest.TestCase

#### Methods

- `test_breakout_ext_id_and_ext_url(self) -> None`: ext_id/ext_url from breakout frontmatter populate the record.
- `test_breakout_tags_merged_with_inline(self) -> None`: Frontmatter tags from breakout file merge with inline tags.
- `test_breakout_tags_only(self) -> None`: Breakout with tags but no ext fields.
- `test_breakout_via_spec_registry(self) -> None`: Breakout enrichment works through spec_registry path too.
- `test_breakout_without_metadata_no_effect(self) -> None`: Breakout file without tags/ext_id/ext_url leaves record unchanged.
- `_make_repo(self) -> Path`
- `_write_breakout(self, root, spec_id, req_id, frontmatter) -> None`
- `_write_spec(self, root, spec_id, body) -> Path`

### TestPlaceholderRecordSourceType

DE-129 Phase 2: _create_placeholder_record stamps source_type='revision'.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_placeholder_has_revision_source_type(self) -> None`: Revision-created placeholder records have source_type='revision'.

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

### TestStaleRequirementPruning

DE-129 Phase 2: Post-relation stale requirement pruning.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_backlog_sourced_requirement_not_pruned(self) -> None`: Backlog-sourced requirements are not pruned (primary_spec is backlog ID).
- `test_deleted_requirement_is_pruned(self) -> None`: Requirement removed from spec body is pruned from registry.
- `test_pruning_idempotent(self) -> None`: Re-running sync after pruning produces no further changes (NF-002).
- `test_pruning_via_spec_dirs_path(self) -> None`: Pruning works through the spec_dirs fallback extraction path.
- `test_revision_introduced_requirement_not_pruned(self) -> None`: Requirements with `introduced` set are preserved even when absent from body.
- `test_revision_moved_requirement_not_pruned_from_old_spec(self) -> None`: Requirement moved by revision block is not pruned from old spec.

This is the critical test for ext. review F1: pruning runs after
revision blocks have updated primary_spec, so the moved requirement
no longer belongs to the source spec's pruning scope.
- `_make_repo(self, body) -> Path`
- `_write_spec(self, root, spec_id, body) -> Path`

### TestSyncStatsFields

DE-129 Phase 2: SyncStats has pruned and warnings fields.

**Inherits from:** unittest.TestCase

#### Methods

- `test_defaults_to_zero(self) -> None`
- `test_fields_are_mutable(self) -> None`

### TestSyncSummaryLine

DE-129 Phase 2: Sync summary line with log-level discipline.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_clean_sync_emits_info(self) -> None`: When no warnings/pruning, summary is at info level.
- `test_sync_with_pruning_emits_warning(self) -> None`: When pruning occurs, summary is at warning level.
- `test_sync_with_warnings_emits_warning(self) -> None`: When warnings exist, summary is at warning level.

### TestUpsertRecordProvenance

VT-UPSERT-076-003: _upsert_record stamps source provenance.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_upsert_stamps_source_kind_on_create(self) -> None`
- `test_upsert_stamps_source_kind_on_merge(self) -> None`

### TestWarningCounting

DE-129 Phase 2: SyncStats.warnings incremented by parser diagnostics.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_collision_increments_warnings(self) -> None`: Duplicate requirement ID increments stats.warnings.
- `test_frontmatter_definitions_increments_warnings(self) -> None`: Frontmatter requirement definitions increment stats.warnings.
