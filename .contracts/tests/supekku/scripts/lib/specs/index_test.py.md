# supekku.scripts.lib.specs.index_test

Tests for specification index management.

## Classes

### TestSpecIndexBuilder

Test SpecIndexBuilder functionality.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test fixtures.
- `tearDown(self) -> None`: Clean up test fixtures.
- `test_alias_symlinks_cleaned_on_rebuild(self) -> None`: Alias symlinks are idempotent across rebuilds.
- `test_alias_symlinks_resolve_to_specs(self) -> None`: Alias symlinks resolve through to actual spec directories.
- `test_initialization(self) -> None`: Test SpecIndexBuilder initialization.
- `test_read_frontmatter_incomplete_delimiters(self) -> None`: Test \_read_frontmatter with incomplete frontmatter delimiters.
- `test_read_frontmatter_no_frontmatter(self) -> None`: Test \_read_frontmatter with file without frontmatter.
- `test_read_frontmatter_valid_yaml(self) -> None`: Test \_read_frontmatter with valid YAML.
- `test_rebuild_cleans_existing_symlinks(self) -> None`: Test rebuild cleans up existing symlinks before creating new ones.
- `test_rebuild_cleans_taxonomy_views(self) -> None`: VT-030-004: taxonomy views are cleaned on rebuild.
- `test_rebuild_creates_alias_symlinks(self) -> None`: Phase 3: convenience alias directory symlinks for ergonomic navigation.
- `test_rebuild_creates_by_c4_level_views(self) -> None`: VT-030-004: by-c4-level views built deterministically.
- `test_rebuild_creates_by_category_views(self) -> None`: VT-030-004: by-category views built deterministically.
- `test_rebuild_creates_directories(self) -> None`: Test that rebuild creates necessary directories.
- `test_rebuild_creates_nested_directory_structure(self) -> None`: Test rebuild creates nested directories for complex identifiers.
- `test_rebuild_handles_empty_frontmatter(self) -> None`: Test rebuild handles specs with empty frontmatter.
- `test_rebuild_handles_malformed_frontmatter(self) -> None`: Test rebuild handles specs with malformed frontmatter.
- `test_rebuild_handles_missing_spec_files(self) -> None`: Test rebuild gracefully handles missing spec files.
- `test_rebuild_skips_sources_without_language_or_identifier(self) -> None`: Test rebuild skips sources missing language or identifier.
- `test_rebuild_with_language_symlinks_go(self) -> None`: Test rebuild creates by-language symlinks for Go sources.
- `test_rebuild_with_language_symlinks_python(self) -> None`: Test rebuild creates by-language symlinks for Python sources.
- `test_rebuild_with_mixed_language_sources(self) -> None`: Test rebuild handles specs with multiple language sources.
- `test_rebuild_with_package_symlinks(self) -> None`: Test rebuild creates package-based symlinks.
- `test_rebuild_with_slug_symlinks(self) -> None`: Test rebuild creates slug-based symlinks.
- `_create_spec_with_frontmatter(self, spec_id, frontmatter) -> Path`: Create a spec directory and file with given frontmatter.

### TestSpecIndexEntry

Test SpecIndexEntry data class.

**Inherits from:** unittest.TestCase

#### Methods

- `test_creation(self) -> None`: Test creating a SpecIndexEntry.
- `test_creation_with_tests_path(self) -> None`: Test creating a SpecIndexEntry with tests path.
