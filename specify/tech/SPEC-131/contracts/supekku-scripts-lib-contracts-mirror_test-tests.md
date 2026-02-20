# supekku.scripts.lib.contracts.mirror_test

Tests for contract mirror tree builder.

## Classes

### TestContractMirrorTreeBuilder

Test ContractMirrorTreeBuilder end-to-end.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up temp repo with tech directory.
- `tearDown(self) -> None`: Clean up temp directory.
- `test_alias_not_created_for_empty_view(self) -> None`: Test aliases are not created when target view is empty.
- `test_conflict_resolution(self) -> None`: Test conflicting mirror paths resolved by lowest SPEC ID.
- `test_missing_registry(self) -> None`: Test rebuild with missing registry produces warning.
- `test_python_deduplicates_same_spec(self) -> None`: Two identifiers mapping to the same SPEC don't produce duplicates.
- `test_rebuild_cleans_stale(self) -> None`: Test rebuild removes stale entries from previous build.
- `test_rebuild_creates_aliases(self) -> None`: Test alias symlinks are created for existing views.
- `test_rebuild_creates_mirror_dir(self) -> None`: Test rebuild creates .contracts/ directory.
- `test_rebuild_go_contracts(self) -> None`: Test Go contracts produce correct package-based mirror paths.
- `test_rebuild_is_idempotent(self) -> None`: Test consecutive rebuilds produce identical results.
- `test_rebuild_python_contracts(self) -> None`: Test Python contracts produce correct mirror symlinks.
- `test_rebuild_python_multiple_modules(self) -> None`: Test multiple Python modules in same SPEC.
- `test_rebuild_removes_all_stale_views(self) -> None`: Test rebuild removes entire stale view directories.
- `test_rebuild_ts_contracts(self) -> None`: Test TypeScript contracts produce correct mirror symlinks.
- `test_rebuild_zig_contracts(self) -> None`: Test Zig contracts produce correct mirror symlinks.
- `test_rebuild_zig_root_package(self) -> None`: Test Zig root package maps to __root__/ directory.
- `test_symlinks_use_relative_paths(self) -> None`: Test symlink targets are relative, not absolute.
- `test_write_confinement(self) -> None`: Test rebuild writes only within .contracts/ (VT-CONTRACT-MIRROR-003).
- `_create_contract_file(self, spec_id, filename, content) -> None`
- `_create_python_contract(self, spec_id, filename, module_name) -> None`
- `_create_registry(self, languages) -> None`

### TestExtractPythonVariant

Test variant extraction from Python contract filenames.

**Inherits from:** unittest.TestCase

#### Methods

- `test_all_variant(self) -> None`: Test extracting 'all' variant.
- `test_empty_stem(self) -> None`: Test bare .md returns None.
- `test_no_hyphen(self) -> None`: Test filename without hyphen returns None.
- `test_public_variant(self) -> None`: Test extracting 'public' variant.
- `test_realistic_filename(self) -> None`: Test real-world contract filename.
- `test_test_module_filename(self) -> None`: Test real-world test module contract filename.
- `test_tests_variant(self) -> None`: Test extracting 'tests' variant from test module.
- `test_unknown_variant(self) -> None`: Test unknown variant returns None.

### TestGoMirrorEntries

Test Go contract mirror entry production.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up temp contracts directory.
- `tearDown(self) -> None`: Clean up temp directory.
- `test_package_based(self) -> None`: Test Go package identifier preserves contract filename in path.

### TestPythonMirrorEntries

Test Python contract mirror entry production.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up temp contracts directory.
- `tearDown(self) -> None`: Clean up temp directory.
- `test_multiple_modules(self) -> None`: Test multiple module contracts in same SPEC.
- `test_multiple_variants(self) -> None`: Test same module with multiple variants.
- `test_nonexistent_dir(self) -> None`: Test nonexistent contracts directory returns empty.
- `test_produces_entry(self) -> None`: Test single contract produces correct entry.
- `test_skips_non_variant_files(self) -> None`: Test files without known variant suffix are skipped.
- `test_warns_on_unreadable_header(self) -> None`: Test warning when contract has no parseable header.
- `_create_contract(self, filename, header) -> None`

### TestPythonModuleToPath

Test dotted module name to file path conversion.

**Inherits from:** unittest.TestCase

#### Methods

- `test_deep_module(self) -> None`: Test deeply nested module path.
- `test_simple_module(self) -> None`: Test two-segment dotted name.
- `test_single_segment(self) -> None`: Test single-segment module name.

### TestReadPythonModuleName

Test reading module name from contract header.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up temp directory.
- `tearDown(self) -> None`: Clean up temp directory.
- `test_reads_module_name(self) -> None`: Test reading simple dotted module name from header.
- `test_reads_with_description(self) -> None`: Test reading header followed by description text.
- `test_returns_none_for_empty_file(self) -> None`: Test empty file returns None.
- `test_returns_none_for_missing_file(self) -> None`: Test nonexistent file returns None.
- `test_returns_none_for_no_header(self) -> None`: Test file without markdown header returns None.

### TestTsMirrorEntries

Test TypeScript contract mirror entry production.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up temp contracts directory.
- `tearDown(self) -> None`: Clean up temp directory.
- `test_file_based(self) -> None`: Test TS file identifier produces entries for both views.
- `test_missing_variant(self) -> None`: Test only existing contract files produce entries.

### TestZigMirrorEntries

Test Zig contract mirror entry production.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up temp contracts directory.
- `tearDown(self) -> None`: Clean up temp directory.
- `test_file_based_identifier(self) -> None`: Test Zig file identifier produces entries for both views.
- `test_missing_variant(self) -> None`: Test only existing contract files produce entries.
- `test_no_contracts(self) -> None`: Test empty contracts directory returns empty.
- `test_root_package(self) -> None`: Test root package '.' maps to __root__/ directory.
