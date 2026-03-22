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

### TestUpsertRecordProvenance

VT-UPSERT-076-003: \_upsert_record stamps source provenance.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_upsert_stamps_source_kind_on_create(self) -> None`
- `test_upsert_stamps_source_kind_on_merge(self) -> None`
