# supekku.scripts.lib.memory.creation_test

Tests for memory creation logic.

## Functions

- `_write_memory_file(directory, mem_id, name, memory_type) -> None`: Write a minimal valid memory file.
- @pytest.fixture `memory_dir(tmp_path) -> Path`: Create a temporary memory directory with sample files.
- @pytest.fixture `registry(tmp_path, memory_dir) -> MemoryRegistry`: Create a MemoryRegistry rooted at tmp_path.

## Classes

### TestBuildMemoryFrontmatter

Tests for build_memory_frontmatter.

#### Methods

- `test_confidence_custom_value(self) -> None`
- `test_confidence_defaults_to_medium(self) -> None`
- `test_confidence_empty_string_defaults_to_medium(self) -> None`
- `test_dates_are_iso_strings(self) -> None`
- `test_does_not_stamp_verified_sha_at_creation(self) -> None`
- `test_minimal(self) -> None`
- `test_stamps_verified_date_at_creation(self) -> None`
- `test_with_all_options(self) -> None`

### TestCreateMemory

Tests for create_memory with semantic IDs.

#### Methods

- `test_creates_directory_if_missing(self, tmp_path) -> None`
- `test_creates_file(self, registry, memory_dir) -> None`
- `test_custom_status(self, registry) -> None`
- `test_file_has_body(self, registry) -> None`
- `test_file_has_valid_frontmatter(self, registry) -> None`
- `test_no_warning_when_types_match(self, registry) -> None`
- `test_normalizes_id_to_lowercase(self, registry) -> None`
- `test_raises_on_duplicate_id(self, registry, memory_dir) -> None`
- `test_raises_on_invalid_id(self, registry) -> None`
- `test_warns_on_type_mismatch(self, registry) -> None`
