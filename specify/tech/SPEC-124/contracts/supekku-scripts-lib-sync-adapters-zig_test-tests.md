# supekku.scripts.lib.sync.adapters.zig_test

Tests for Zig language adapter.

## Classes

### TestZigAdapter

Test ZigAdapter functionality.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test fixtures.
- `test_describe_rejects_non_zig_unit(self) -> None`: Test describe method rejects non-Zig source units.
- `test_describe_zig_package(self) -> None`: Test describe method generates correct metadata for Zig packages.
- @patch(pathlib.Path.exists) @patch(pathlib.Path.is_file) @patch(pathlib.Path.mkdir) @patch(subprocess.run) @patch(supekku.scripts.lib.sync.adapters.zig.is_zigmarkdoc_available) `test_generate_check_mode(self, _mock_mkdir, mock_is_file, mock_exists, mock_subprocess, mock_is_zigmarkdoc) -> None`: Test generate method in check mode.
- @patch(pathlib.Path.exists) @patch(pathlib.Path.is_file) @patch(pathlib.Path.mkdir) @patch(subprocess.run) @patch(supekku.scripts.lib.sync.adapters.zig.is_zigmarkdoc_available) `test_generate_check_mode_detects_changes(self, _mock_mkdir, mock_is_file, mock_exists, mock_subprocess, mock_is_zigmarkdoc) -> None`: Test generate method in check mode detects changes.
- @patch(pathlib.Path.exists) @patch(pathlib.Path.is_file) @patch(pathlib.Path.mkdir) @patch(pathlib.Path.read_text) @patch(subprocess.run) @patch(supekku.scripts.lib.sync.adapters.zig.is_zigmarkdoc_available) `test_generate_creates_variants(self, _mock_mkdir, mock_is_file, mock_exists, mock_read_text, mock_subprocess, mock_is_zigmarkdoc) -> None`: Test generate method creates documentation variants.
- @patch(pathlib.Path.exists) @patch(supekku.scripts.lib.sync.adapters.zig.is_zigmarkdoc_available) `test_generate_raises_when_source_not_exists(self, mock_exists, mock_is_zigmarkdoc) -> None`: Test generate raises FileNotFoundError when source path doesn't exist.
- @patch(supekku.scripts.lib.sync.adapters.zig.is_zigmarkdoc_available) `test_generate_raises_when_zigmarkdoc_not_available(self, mock_is_zigmarkdoc) -> None`: Test generate raises error when zigmarkdoc is not available.
- `test_generate_rejects_non_zig_unit(self) -> None`: Test generate method rejects non-Zig source units.
- @patch(pathlib.Path.exists) @patch(pathlib.Path.is_file) @patch(pathlib.Path.mkdir) @patch(pathlib.Path.read_text) @patch(subprocess.run) @patch(supekku.scripts.lib.sync.adapters.zig.is_zigmarkdoc_available) `test_generate_with_include_private_flag(self, _mock_mkdir, mock_is_file, mock_exists, mock_read_text, mock_subprocess, mock_is_zigmarkdoc) -> None`: Test generate calls zigmarkdoc with --include-private.
- `test_is_zigmarkdoc_available(self) -> None`: Test is_zigmarkdoc_available correctly detects zigmarkdoc presence.
- `test_language_identifier(self) -> None`: Test that ZigAdapter has correct language identifier.
- `test_supports_identifier_invalid_identifiers(self) -> None`: Test supports_identifier returns False for non-Zig identifiers.
- `test_supports_identifier_valid_zig_paths(self) -> None`: Test supports_identifier returns True for valid Zig paths.
