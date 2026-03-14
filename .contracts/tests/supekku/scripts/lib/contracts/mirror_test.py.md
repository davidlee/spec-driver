# supekku.scripts.lib.contracts.mirror_test

Tests for contract mirror tree builder.

## Classes

### TestContractMirrorTreeBuilder

Test ContractMirrorTreeBuilder: compat symlinks SPEC-*/contracts/ → .contracts/.

Canonical contract files live in .contracts/<view>/<path>.
rebuild() creates compat symlinks from SPEC-*/contracts/ pointing back
into .contracts/ so that spec-relative tooling still works.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up temp repo with tech directory.
- `tearDown(self) -> None`: Clean up temp directory.
- `test_alias_not_created_for_empty_view(self) -> None`: Aliases are not created when target view directory doesn't exist.
- `test_aliases_created_in_contracts_root(self) -> None`: View aliases (api → public) created in .contracts/. - -- aliases --
- `test_canonical_files_not_modified(self) -> None`: Rebuild must not modify canonical .contracts/ files.
- `test_drift_warning_python_spec(self) -> None`: Drift warning fires for Python specs with contracts but no canonical.
- `test_drift_warning_when_spec_has_contracts_but_no_canonical(self) -> None`: VT-CONTRACTS-DRIFT-001: warn on contracts/ with no canonical. - -- drift warnings (VT-CONTRACTS-DRIFT-001) --
- `test_empty_registry(self) -> None`: Test rebuild with empty registry is a no-op.
- `test_go_compat_symlinks(self) -> None`: Go: compat symlinks mirror package-based paths.
- `test_missing_registry(self) -> None`: Test rebuild with missing registry produces warning. - -- basic wiring --
- `test_no_drift_warning_for_empty_contracts_dir(self) -> None`: Empty contracts/ dir does NOT trigger drift warning (no false positives).
- `test_no_drift_warning_when_canonical_entries_exist(self) -> None`: No drift warning when canonical entries exist for the spec's unit.
- `test_no_drift_warning_when_contracts_dir_missing(self) -> None`: No drift warning when SPEC has no contracts/ directory at all.
- `test_python_compat_symlinks(self) -> None`: Python: compat symlinks for distributed contract files.
- `test_rebuild_is_idempotent(self) -> None`: Consecutive rebuilds produce identical results.
- `test_replaces_non_symlink_with_warning(self) -> None`: Replacing a real file in SPEC-*/contracts/ emits a warning.
- `test_symlinks_use_relative_paths(self) -> None`: Compat symlink targets are relative, not absolute. - -- properties --
- `test_ts_compat_symlinks(self) -> None`: TypeScript: compat symlinks for file-based identifiers.
- `test_zig_compat_symlinks(self) -> None`: Zig: compat symlinks in SPEC-*/contracts/ → .contracts/. - -- per-language compat symlinks --
- `test_zig_root_package(self) -> None`: Zig root package '.' maps to __root__/ directory.
- `_compat_link(self, spec_id, view, rel_path) -> Path`: Return expected compat symlink path in SPEC-*/contracts/.
- `_create_canonical(self, view, rel_path) -> Path`: Create a canonical contract file in .contracts/<view>/<rel_path>.
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
- `test_root_package(self) -> None`: Test Go root package '.' maps to __root__/ directory.

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

### TestPythonStagingDir

Test Python staging directory computation.

**Inherits from:** unittest.TestCase

#### Methods

- `test_dotted_identifier(self) -> None`: Test dotted module names are slugified.
- `test_package_identifier(self) -> None`: Test Python package identifier slugified correctly.

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

### TestResolveGoVariantOutputs

Test Go pre-generation path resolution.

**Inherits from:** unittest.TestCase

#### Methods

- `test_root_package(self) -> None`: Test root package '.' maps to __root__/ directory.
- `test_simple_package(self) -> None`: Test single-segment Go package.
- `test_standard_package(self) -> None`: Test Go package produces dir/filename canonical paths.

### TestResolveTsVariantOutputs

Test TypeScript pre-generation path resolution.

**Inherits from:** unittest.TestCase

#### Methods

- `test_file_identifier(self) -> None`: Test TS file produces {identifier}.md leaf with adapter variant names.

### TestResolveZigVariantOutputs

Test Zig pre-generation path resolution.

**Inherits from:** unittest.TestCase

#### Methods

- `test_file_identifier(self) -> None`: Test Zig file produces {identifier}.md leaf.
- `test_root_package(self) -> None`: Test root '.' maps to __root__/ with original filenames.

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
