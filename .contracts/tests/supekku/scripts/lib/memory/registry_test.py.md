# supekku.scripts.lib.memory.registry_test

Tests for MemoryRegistry.

## Constants

- `ARCHIVED_MEM`
- `FULL_MEM`
- `MINIMAL_MEM` - ── Fixture content ─────────────────────────────────────────────
- `PATTERN_MEM`

## Functions

- `_setup_repo(tmpdir, files) -> Path`: Set up a test repo with .git marker and optional memory files.

Args:
tmpdir: Temporary directory path.
files: Mapping of filename to content for memory/ directory.

Returns:
Root path of the test repo.

## Classes

### TestMemoryRegistry

Test MemoryRegistry discovery, parsing, and filtering.

**Inherits from:** unittest.TestCase

#### Methods

- `test_collect_bodies_empty_directory(self) -> None`: collect_bodies returns empty dict when no memories exist.
- `test_collect_bodies_returns_body_text(self) -> None`: collect_bodies returns {id: body_text} for all memories.
- `test_collect_bodies_strips_frontmatter(self) -> None`: collect_bodies does not include frontmatter delimiters or content.
- `test_collect_discovers_mem_files(self) -> None`: collect finds mem.\*.md files and parses them.
- `test_collect_empty_directory(self) -> None`: collect returns empty dict when no memory directory exists.
- `test_collect_empty_directory_exists(self) -> None`: collect returns empty dict when memory dir has no mem.\* files.
- `test_collect_falls_back_to_filename_stem(self) -> None`: When frontmatter has no id, filename stem is used.
- `test_collect_ignores_non_mem_files(self) -> None`: collect skips files that don't match mem.\*.md pattern.
- `test_collect_parses_full_correctly(self) -> None`: collect parses full memory file with all fields.
- `test_collect_parses_minimal_correctly(self) -> None`: collect parses minimal memory file fields.
- `test_collect_skips_malformed_files(self) -> None`: collect skips files with missing/broken frontmatter.
- `test_collect_uses_frontmatter_id_over_filename(self) -> None`: Frontmatter id takes precedence over filename stem.
- `test_custom_directory(self) -> None`: Registry accepts a custom memory directory path.
- `test_filter_by_memory_type(self) -> None`: filter by memory_type returns matching records.
- `test_filter_by_status(self) -> None`: filter by status returns matching records.
- `test_filter_by_tag(self) -> None`: filter by tag returns records containing that tag.
- `test_filter_combined(self) -> None`: filter with multiple criteria ANDs them together.
- `test_filter_no_criteria(self) -> None`: filter with no criteria returns all records.
- `test_find_existing(self) -> None`: find returns the record for a known ID.
- `test_find_missing(self) -> None`: find returns None for unknown ID.
- `test_init_default_directory(self) -> None`: Registry defaults to memory/ under repo root.
- `test_iter_all(self) -> None`: iter without filters yields all records.
- `test_iter_by_status(self) -> None`: iter with status filter yields only matching records.
- `test_to_dict_integration(self) -> None`: Records produced by collect serialize correctly via to_dict.
