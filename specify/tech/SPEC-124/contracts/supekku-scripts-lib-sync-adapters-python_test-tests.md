# supekku.scripts.lib.sync.adapters.python_test

Tests for Python language adapter.

## Classes

### TestPythonAdapter

Test PythonAdapter functionality.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test fixtures.
- `test_describe_python_module(self) -> None`: Test describe method generates correct metadata for Python modules.
- `test_describe_python_package_init(self) -> None`: Test describe method handles __init__.py files correctly.
- `test_describe_rejects_non_python_unit(self) -> None`: Test describe method rejects non-Python source units.
- @patch(pathlib.Path.exists) @patch(supekku.scripts.lib.sync.adapters.python.find_all_leaf_packages) `test_discover_targets_auto_discovery(self, mock_find_packages, mock_exists) -> None`: Test discover_targets auto-discovers Python packages.
- @patch(pathlib.Path.exists) `test_discover_targets_requested_modules(self, mock_exists) -> None`: Test discover_targets processes requested modules.
- @patch(pathlib.Path.exists) @patch(supekku.scripts.lib.docs.python.generate_docs) `test_generate_check_mode(self, mock_generate_docs, mock_exists) -> None`: Test generate method in check mode.
- @patch(pathlib.Path.exists) @patch(supekku.scripts.lib.docs.python.generate_docs) `test_generate_creates_variants(self, mock_generate_docs, mock_exists) -> None`: Test generate method creates documentation variants.
- @patch(pathlib.Path.exists) @patch(supekku.scripts.lib.docs.python.generate_docs) `test_generate_handles_exceptions(self, mock_generate_docs, mock_exists) -> None`: Test generate method handles exceptions gracefully.
- @patch(pathlib.Path.exists) `test_generate_missing_file(self, mock_exists) -> None`: Test generate method handles missing files gracefully.
- `test_generate_rejects_non_python_unit(self) -> None`: Test generate method rejects non-Python source units.
- `test_language_identifier(self) -> None`: Test that PythonAdapter has correct language identifier.
- `test_should_not_skip_regular_files(self) -> None`: Test _should_skip_file allows regular Python files.
- `test_should_skip_file_patterns(self) -> None`: Test _should_skip_file identifies files to skip.
- `test_should_skip_init_files(self) -> None`: Test __init__.py files are skipped.
- `test_supports_identifier_invalid_identifiers(self) -> None`: Test supports_identifier returns False for non-Python identifiers.
- `test_supports_identifier_valid_python_modules(self) -> None`: Test supports_identifier returns True for valid Python identifiers.
