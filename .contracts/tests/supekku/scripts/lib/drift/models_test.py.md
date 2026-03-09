# supekku.scripts.lib.drift.models_test

Tests for drift ledger models and lifecycle vocabulary (VT-065-models).

## Classes

### TestClaim

Claim typed substructure.

#### Methods

- `test_frozen(self)`
- `test_required_fields(self)`
- `test_with_label(self)`

### TestDiscoveredBy

DiscoveredBy typed substructure.

#### Methods

- `test_frozen(self)`
- `test_required_fields(self)`
- `test_with_ref(self)`

### TestDriftEntry

DriftEntry model construction and defaults.

#### Methods

- `test_entries_are_mutable(self)`: Entries are mutable — status can be updated in-place.
- `test_extra_field_preserved(self)`
- `test_full_entry(self)`
- `test_minimal_entry(self)`

### TestDriftLedger

DriftLedger model construction and defaults.

#### Methods

- `test_body_preserved(self)`
- `test_ledger_with_entries(self)`
- `test_minimal_ledger(self)`

### TestLifecycleConstants

Lifecycle vocabulary completeness.

#### Methods

- `test_assessments(self)`
- `test_entry_statuses(self)`
- `test_entry_types(self)`
- `test_ledger_statuses(self)`
- `test_resolution_paths_includes_backlog(self)`: backlog was added per pilot usage — see DR-065.
- `test_severities(self)`

### TestSource

Source typed substructure.

#### Methods

- `test_frozen(self)`
- `test_required_fields(self)`
- `test_with_note(self)`

### TestStatusValidation

Permissive validation with warnings (DEC-057-08 pattern).

#### Methods

- `test_invalid_entry_status_warns(self, caplog)`
- `test_invalid_ledger_status_warns(self, caplog)`
- `test_valid_entry_status(self)`
- `test_valid_ledger_status(self)`
