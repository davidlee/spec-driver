# supekku.scripts.lib.requirements.parser_lockstep_test

Lockstep: frozen migration regex must match runtime parser pattern.

Cross-cutting test ensuring DEC-138-12 frozen-local patterns in the
migration module stay in sync with the runtime parser. Lives outside
``spec_driver.migrations`` to satisfy the import-linter isolation
contract.

## Classes

### TestMigrationLockstep

#### Methods

- `test_frozen_regex_matches_runtime_flags(self)`
- `test_frozen_regex_matches_runtime_pattern(self)`
