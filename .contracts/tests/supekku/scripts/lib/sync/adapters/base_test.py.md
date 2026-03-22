# supekku.scripts.lib.sync.adapters.base_test

Tests for base language adapter.

## Classes

### ConcreteAdapter

Concrete implementation for testing abstract base class.

**Inherits from:** LanguageAdapter

#### Methods

- `describe(self, unit)`: Stub implementation.
- `discover_targets(self, repo_root, requested)`: Stub implementation.
- `generate(self, unit)`: Stub implementation.
- `supports_identifier(self, identifier)`: Stub implementation.

### TestLanguageAdapterCreateDocVariant

Test LanguageAdapter doc variant creation.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test fixtures.
- `test_create_doc_variant_basic(self) -> None`: Test creating a basic doc variant.
- `test_create_doc_variant_different_language(self) -> None`: Test creating doc variant for different language.
- `test_create_doc_variant_single_slug_part(self) -> None`: Test creating doc variant with single slug part.

### TestLanguageAdapterGitTracking

Test LanguageAdapter git tracking functionality.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test fixtures.
- `tearDown(self) -> None`: Clean up test fixtures.
- `test_get_git_tracked_files_caches_results(self) -> None`: Test that git tracked files are cached.
- `test_get_git_tracked_files_empty_lines(self) -> None`: Test that empty lines in git output are ignored.
- `test_get_git_tracked_files_git_error(self) -> None`: Test handling git command errors.
- `test_get_git_tracked_files_no_git(self) -> None`: Test when git is not available.
- `test_get_git_tracked_files_success(self) -> None`: Test getting git tracked files successfully.
- `test_get_git_tracked_files_timeout(self) -> None`: Test handling git command timeout.

### TestLanguageAdapterShouldSkipPath

Test LanguageAdapter path skipping functionality.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test fixtures.
- `tearDown(self) -> None`: Clean up test fixtures.
- `test_should_skip_change_directory(self) -> None`: Test that paths in change/ are skipped.
- `test_should_skip_no_git_does_not_skip(self) -> None`: Test that files are not skipped when git is unavailable.
- `test_should_skip_non_git_tracked(self) -> None`: Test that non-git-tracked files are skipped.
- `test_should_skip_specify_directory(self) -> None`: Test that paths in specify/ are skipped.
- `test_should_skip_symlink(self) -> None`: Test that symlinks are skipped.

### TestLanguageAdapterValidateUnitLanguage

Test LanguageAdapter unit language validation.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test fixtures.
- `test_validate_unit_language_matching(self) -> None`: Test validation passes for matching language.
- `test_validate_unit_language_mismatched(self) -> None`: Test validation fails for mismatched language.

### TestLanguageAdapterValidation

Test LanguageAdapter validation methods.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test fixtures.
- `tearDown(self) -> None`: Clean up test fixtures.
- `test_get_source_path_default_implementation(self) -> None`: Test default _get_source_path implementation.
- `test_get_source_path_nested(self) -> None`: Test _get_source_path with nested identifier.
- `test_validate_source_exists_cannot_determine_path(self) -> None`: Test validation when source path cannot be determined.
- `test_validate_source_exists_file_exists_git_tracked(self) -> None`: Test validation when file exists and is git-tracked.
- `test_validate_source_exists_file_exists_not_tracked(self) -> None`: Test validation when file exists but not git-tracked.
- `test_validate_source_exists_file_missing(self) -> None`: Test validation when source file doesn't exist.
- `test_validate_source_exists_nested_path(self) -> None`: Test validation with nested directory structure.
- `test_validate_source_exists_no_git_available(self) -> None`: Test validation when git is not available.
