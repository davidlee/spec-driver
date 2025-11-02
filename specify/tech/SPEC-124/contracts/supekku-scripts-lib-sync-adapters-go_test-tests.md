# supekku.scripts.lib.sync.adapters.go_test

Tests for Go language adapter.

## Classes

### TestGoAdapter

Test GoAdapter functionality.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test fixtures.
- `test_describe_go_package(self) -> None`: Test describe method generates correct metadata for Go packages.
- `test_describe_rejects_non_go_unit(self) -> None`: Test describe method rejects non-Go source units.
- @patch(supekku.scripts.lib.sync.adapters.go.is_go_available) `test_discover_targets_raises_when_go_not_available(self, mock_is_go) -> None`: Test discover_targets raises error when Go toolchain is not available.
- @patch(pathlib.Path.exists) @patch(pathlib.Path.mkdir) @patch(subprocess.run) @patch(supekku.scripts.lib.sync.adapters.go.is_go_available) @patch(supekku.scripts.lib.sync.adapters.go.which) `test_generate_check_mode(self, _mock_mkdir, mock_exists, mock_subprocess, mock_which, mock_is_go) -> None`: Test generate method in check mode.
- @patch(pathlib.Path.exists) @patch(pathlib.Path.mkdir) @patch(pathlib.Path.read_text) @patch(subprocess.run) @patch(supekku.scripts.lib.sync.adapters.go.is_go_available) @patch(supekku.scripts.lib.sync.adapters.go.which) `test_generate_creates_variants(self, _mock_mkdir, mock_exists, mock_read_text, mock_subprocess, mock_which, mock_is_go) -> None`: Test generate method creates documentation variants.
- @patch(supekku.scripts.lib.sync.adapters.go.is_go_available) `test_generate_raises_when_go_not_available(self, mock_is_go) -> None`: Test generate raises error when Go toolchain is not available.
- @patch(supekku.scripts.lib.sync.adapters.go.is_go_available) @patch(supekku.scripts.lib.sync.adapters.go.which) `test_generate_raises_when_gomarkdoc_not_available(self, mock_which, mock_is_go) -> None`: Test generate raises error when gomarkdoc is not available.
- `test_generate_rejects_non_go_unit(self) -> None`: Test generate method rejects non-Go source units.
- `test_is_go_available(self) -> None`: Test is_go_available correctly detects Go presence.
- `test_is_gomarkdoc_available(self) -> None`: Test is_gomarkdoc_available correctly detects gomarkdoc presence.
- `test_language_identifier(self) -> None`: Test that GoAdapter has correct language identifier.
- `test_supports_identifier_invalid_identifiers(self) -> None`: Test supports_identifier returns False for non-Go identifiers.
- `test_supports_identifier_valid_go_packages(self) -> None`: Test supports_identifier returns True for valid Go package paths.
