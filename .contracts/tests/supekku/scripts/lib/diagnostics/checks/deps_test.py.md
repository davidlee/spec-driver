# supekku.scripts.lib.diagnostics.checks.deps_test

Tests for dependency checks.

## Constants

- `_ALL_DEP_NAMES`

## Classes

### TestCheckDeps

Tests for check_deps function.

**Inherits from:** unittest.TestCase

#### Methods

- `test_all_available(self) -> None`: All deps present produces all-pass results.
- `test_all_results_have_deps_category(self) -> None`: Every result should be in the deps category.
- `test_covers_all_expected_deps(self) -> None`: Check that all expected dependency names are covered.
- `test_git_missing_but_jj_present(self) -> None`: jj as git alternative should pass.
- `test_go_missing_warns(self) -> None`: Missing go should warn.
- `test_gomarkdoc_missing_warns_with_install(self) -> None`: Missing gomarkdoc should warn with install command.
- `test_no_vcs_warns(self) -> None`: Missing both git and jj should warn.
- `test_python_version_pass(self) -> None`: Current python should always pass.
- `test_ts_doc_extract_missing_warns(self) -> None`: Missing ts-doc-extract should warn.
- `test_zig_missing_warns(self) -> None`: Missing zig should warn.
- `test_zigmarkdoc_missing_warns(self) -> None`: Missing zigmarkdoc should warn with install link.
- `_run_with_all_available(self) -> list`

### \_FakeWorkspace
