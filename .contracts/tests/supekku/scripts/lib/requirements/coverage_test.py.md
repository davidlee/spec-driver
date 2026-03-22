# supekku.scripts.lib.requirements.coverage_test

Tests for requirement coverage tracking.

## Classes

### TestCoverageReplacementSemantics

VT-081-001: Coverage evidence is rebuilt fresh each sync.

**Inherits from:** unittest.TestCase

#### Methods

- `test_coverage_evidence_replaced_not_accumulated(self) -> None`: Removing an artefact from a coverage block removes it from evidence.
- `test_removed_coverage_block_clears_evidence(self) -> None`: Removing entire coverage block clears evidence for affected requirements.
- `test_sync_idempotency(self) -> None`: Running sync twice produces identical registry (NF-002).
- `_make_repo(self) -> Path`
- `_write_spec(self, root, spec_id, body) -> Path`: Write a spec file and return the tech specs root directory.

### TestRequirementCoverageEntries

Test that coverage_entries field is populated during registry sync.

After \_apply_coverage_blocks(), each RequirementRecord should have a
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
