# supekku.scripts.lib.sync.adapters.typescript_test

Tests for TypeScript/JavaScript language adapter.

## Module Notes

- pylint: disable=protected-access

## Classes

### TestTypeScriptAdapter

Test TypeScriptAdapter functionality.

*pylint: disable=too-many-public-methods*

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test fixtures.
- `test_deduplicates_identical_variants(self) -> None`: Test that internal.md is removed when identical to api.md.
- `test_describe_typescript_module_directory(self) -> None`: Test describe method for TypeScript directory module.
- `test_describe_typescript_module_file(self) -> None`: Test describe method for TypeScript file.
- `test_detect_package_manager_bun(self) -> None`: Test package manager detection finds bun.
- `test_detect_package_manager_defaults_to_npm(self) -> None`: Test package manager detection defaults to npm when no lockfile found.
- `test_detect_package_manager_npm(self) -> None`: Test package manager detection finds npm.
- `test_detect_package_manager_pnpm(self) -> None`: Test package manager detection finds pnpm.
- `test_extract_ast_directory_no_index_raises_error(self) -> None`: Test AST extraction from directory without index file raises error.
- `test_extract_ast_directory_with_index(self) -> None`: Test AST extraction from directory finds index.ts.
- `test_extract_ast_invalid_json(self) -> None`: Test AST extraction handles invalid JSON output.
- `test_extract_ast_subprocess_error(self) -> None`: Test AST extraction handles subprocess errors.
- `test_extract_ast_success(self) -> None`: Test successful AST extraction.
- `test_find_package_root_raises_when_not_found(self) -> None`: Test _find_package_root raises error when no package.json found.
- `test_find_package_root_success(self) -> None`: Test finding package.json in parent directory.
- `test_generate_markdown_simple(self) -> None`: Test markdown generation from AST data.
- `test_generate_markdown_with_class(self) -> None`: Test markdown generation with class.
- `test_generate_requires_node_runtime(self) -> None`: Test generate raises error when Node.js not available.
- `test_generate_validates_unit_language(self) -> None`: Test generate validates unit language.
- `test_get_npx_command_bun(self) -> None`: Test npx command generation for bun.
- `test_get_npx_command_fallback_to_npx(self) -> None`: Test npx command falls back to npx when package manager not available.
- `test_get_npx_command_npm(self) -> None`: Test npx command generation for npm.
- `test_get_npx_command_pnpm(self) -> None`: Test npx command generation for pnpm.
- `test_is_bun_available(self) -> None`: Test bun availability detection.
- `test_is_node_available(self) -> None`: Test Node.js availability detection.
- `test_is_pnpm_available(self) -> None`: Test pnpm availability detection.
- `test_language_identifier(self) -> None`: Test that TypeScriptAdapter has correct language identifier.
- `test_should_skip_file_build_dirs(self) -> None`: Test that files in build directories are skipped.
- `test_should_skip_file_test_files(self) -> None`: Test that test files are skipped.
- `test_supports_identifier_invalid_identifiers(self) -> None`: Test supports_identifier returns False for non-TS/JS identifiers.
- `test_supports_identifier_valid_typescript(self) -> None`: Test supports_identifier returns True for valid TS/JS identifiers.
