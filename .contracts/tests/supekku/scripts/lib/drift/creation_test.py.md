# supekku.scripts.lib.drift.creation_test

Tests for drift ledger creation.

## Classes

### TestCreateDriftLedger

Tests for create_drift_ledger.

**Inherits from:** unittest.TestCase

#### Methods

- `test_creates_directory_if_missing(self) -> None`: Creates .spec-driver/drift/ if it doesn't exist.
- `test_creates_ledger_file(self) -> None`: Creates a ledger file with correct frontmatter.
- `test_delta_ref_included(self) -> None`: Includes delta_ref in frontmatter when provided.
- `test_empty_delta_ref(self) -> None`: Empty delta_ref produces empty string in frontmatter.
- `test_empty_name_raises(self) -> None`: Raises ValueError for empty name.
- `test_increments_id(self) -> None`: Allocates sequential IDs.
- `test_slug_in_filename(self) -> None`: Name is slugified in the filename.
