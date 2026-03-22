# supekku.cli.test_version_warning

Tests for version-staleness CLI warning.

## Classes

### TestWarnIfVersionStale

Tests for _warn_if_version_stale.

**Inherits from:** unittest.TestCase

#### Methods

- @patch(_VERSION_FN, return_value=2.0.0) `test_install_command_suppresses_warning(self, _mock) -> None`: No warning when running the install command itself.
- @patch(_VERSION_FN, return_value=1.0.0) `test_matching_version_no_warning(self, _mock) -> None`: No warning when versions match.
- @patch(_VERSION_FN, return_value=1.0.0) `test_missing_version_stamp_warns(self, _mock) -> None`: Warning when version key is absent from config.
- @patch(_VERSION_FN, return_value=2.0.0) `test_stale_version_warns(self, _mock) -> None`: Warning when installed version differs from running version.
