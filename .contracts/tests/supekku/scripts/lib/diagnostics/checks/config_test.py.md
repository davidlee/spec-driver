# supekku.scripts.lib.diagnostics.checks.config_test

Tests for configuration checks.

## Constants

- `_VERSION_MODULE`

## Functions

- `_make_full_workspace(tmp) -> _FakeWorkspace`: Create a workspace with all config files present.

## Classes

### TestCheckConfig

Tests for check_config function.

**Inherits from:** unittest.TestCase

#### Methods

- @patch(\_VERSION_MODULE, return_value=1.0.0) `test_all_results_have_config_category(self, _mock_ver) -> None`: Every result should be in the config category.
- `test_empty_allowlist_warns(self) -> None`: Empty skills allowlist should warn.
- @patch(\_VERSION_MODULE, return_value=1.0.0) `test_full_config_all_pass(self, _mock_ver) -> None`: Complete configuration should produce no warns or fails.
- `test_invalid_workflow_toml_fails(self) -> None`: Invalid TOML should fail.
- `test_missing_claude_md_warns(self) -> None`: Missing CLAUDE.md should warn.
- `test_missing_target_dir_warns(self) -> None`: Missing agent target dir should warn.
- `test_missing_workflow_toml_warns(self) -> None`: Missing workflow.toml should warn.
- `test_skills_count_in_message(self) -> None`: Allowlist check should report count.

### TestVersionStaleness

Tests for version-staleness diagnostic check.

**Inherits from:** unittest.TestCase

#### Methods

- @patch(\_VERSION_MODULE, return_value=1.0.0) `test_matching_version_passes(self, _mock_ver) -> None`: Matching version should pass.
- @patch(\_VERSION_MODULE, return_value=1.0.0) `test_missing_version_stamp_warns(self, _mock_ver) -> None`: Missing version key should warn.
- @patch(\_VERSION_MODULE, return_value=1.0.0) `test_missing_workflow_toml_warns(self, _mock_ver) -> None`: Missing workflow.toml should warn for version check too.
- @patch(\_VERSION_MODULE, return_value=2.0.0) `test_stale_version_warns(self, _mock_ver) -> None`: Outdated version should warn with install suggestion.

### \_FakeWorkspace
