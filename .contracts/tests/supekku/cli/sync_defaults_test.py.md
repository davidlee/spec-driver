# supekku.cli.sync_defaults_test

Integration tests for sync defaults: contracts-first, opt-in spec creation.

VT-SYNC-DEFAULTS-001 through 005, verifying DE-028 preference resolution,
backward compat heuristic, and flag passthrough.

## Constants

- `_SPEC_DRIVER_DIR`
- `_SYNC_REQS_SUCCESS`
- `_SYNC_SPECS_SUCCESS`
- `_WORKFLOW_TOML`

## Functions

- `_read_toml_autocreate(root) -> bool`: Read spec_autocreate from workflow.toml.

## Classes

### SyncDefaultsTest

VT-SYNC-DEFAULTS: preference resolution and backward compat.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- @patch(supekku.cli.sync._sync_requirements) @patch(supekku.cli.sync._sync_specs) @patch(supekku.cli.sync.find_repo_root) `test_vt001_fresh_dir_defaults_to_contracts_only(self, mock_root, mock_sync_specs, mock_sync_reqs) -> None`: VT-001: fresh repo, bare sync → specs + contracts (default on).
- @patch(supekku.cli.sync._sync_requirements) @patch(supekku.cli.sync._sync_specs) @patch(supekku.cli.sync.find_repo_root) `test_vt002_specs_flag_persists_and_inherited(self, mock_root, mock_sync_specs, mock_sync_reqs) -> None`: VT-SYNC-DEFAULTS-002: --specs persists; subsequent sync inherits.
- @patch(supekku.cli.sync._sync_requirements) @patch(supekku.cli.sync._sync_specs) @patch(supekku.cli.sync.find_repo_root) `test_vt003_no_contracts_flag_skips_contract_generation(self, mock_root, mock_sync_specs, mock_sync_reqs) -> None`: VT-SYNC-DEFAULTS-003: --specs --no-contracts → specs yes, contracts no.
- @patch(supekku.cli.sync._sync_requirements) @patch(supekku.cli.sync._sync_specs) @patch(supekku.cli.sync.find_repo_root) `test_vt004_existing_registry_triggers_backward_compat(self, mock_root, mock_sync_specs, mock_sync_reqs) -> None`: VT-SYNC-DEFAULTS-004: populated registry → spec creation active (default on).
- @patch(supekku.cli.sync._sync_requirements) @patch(supekku.cli.sync._sync_specs) @patch(supekku.cli.sync.find_repo_root) `test_vt005_hint_message_when_specs_off(self, mock_root, mock_sync_specs, mock_sync_reqs) -> None`: VT-005: no specs-off hint when default is on.
- `_invoke(self, args)`
- `_write_registry(self, languages) -> None` - -- helpers --
