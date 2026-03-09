# supekku.scripts.lib.drift.registry_test

Tests for drift ledger registry (VT-065-registry).

## Functions

- `_write_ledger(drift_dir, filename, content) -> Path`: Write a ledger file and return its path.
- @pytest.fixture `drift_dir(tmp_path) -> Path`: Create a .spec-driver/drift/ directory with test ledgers.

## Classes

### TestDiscovery

Registry discovers ledger files in .spec-driver/drift/.

#### Methods

- `test_discovers_ledger_files(self, drift_dir, tmp_path)`
- `test_discovers_multiple_ledgers(self, drift_dir, tmp_path)`
- `test_empty_directory(self, drift_dir, tmp_path)`
- `test_ignores_non_ledger_files(self, drift_dir, tmp_path)`
- `test_nonexistent_directory(self, tmp_path)`

### TestFind

Registry find by ID.

#### Methods

- `test_find_existing(self, drift_dir, tmp_path)`
- `test_find_nonexistent(self, drift_dir, tmp_path)`

### TestIter

Registry iteration with optional status filter.

#### Methods

- `test_iter_all(self, drift_dir, tmp_path)`
- `test_iter_by_status(self, drift_dir, tmp_path)`

### TestMalformedLedgers

Registry handles malformed ledger files gracefully.

#### Methods

- `test_malformed_frontmatter_skipped(self, drift_dir, tmp_path)`
- `test_missing_id_skipped(self, drift_dir, tmp_path)`

### TestParsedContent

Registry correctly parses ledger content including entries.

#### Methods

- `test_body_preserved(self, drift_dir, tmp_path)`
- `test_delta_ref_extracted(self, drift_dir, tmp_path)`
- `test_entries_parsed(self, drift_dir, tmp_path)`
- `test_lazy_loading(self, drift_dir, tmp_path)`: Registry doesn't load until first access.
