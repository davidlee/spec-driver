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
