# supekku.cli.backfill_test

Tests for backfill CLI command.

Note: These are basic tests for the backfill command. Full integration
testing will be performed manually in Task 1.6 due to complexity of
mocking SpecRegistry and template infrastructure.

## Constants

- `runner`

## Functions

- `test_backfill_help()`: Help text should be available.
- `test_backfill_spec_not_found(tmp_path, monkeypatch)`: Backfilling non-existent spec should error.
