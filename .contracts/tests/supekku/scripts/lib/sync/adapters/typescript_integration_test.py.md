# supekku.scripts.lib.sync.adapters.typescript_integration_test

Integration tests for TypeScript adapter dependency handling (VT-019-003).

Tests sync-level behavior when ts-doc-extract is missing,
verifying graceful degradation through the full generate() path.

## Classes

### TestTypescriptSyncWithMissingDependency

VT-019-003: Integration test for sync with missing ts-doc-extract.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_generate_returns_empty_when_ts_doc_extract_missing(self) -> None`: Sync skips TS units gracefully when ts-doc-extract is not installed.
- `test_subsequent_units_skip_without_recheck(self) -> None`: Availability check is cached — second unit skips without re-checking.
- `test_warning_includes_install_instructions(self) -> None`: Warning message includes actionable install instructions.
