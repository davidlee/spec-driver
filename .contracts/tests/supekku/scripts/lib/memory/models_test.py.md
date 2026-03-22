# supekku.scripts.lib.memory.models_test

Tests for MemoryRecord model.

## Classes

### TestMemoryRecord

Test MemoryRecord dataclass construction and serialization.

**Inherits from:** unittest.TestCase

#### Methods

- `test_from_frontmatter_bad_date_ignored(self) -> None`: Unparseable dates coerce to None.
- `test_from_frontmatter_full(self) -> None`: All optional fields are parsed correctly.
- `test_from_frontmatter_minimal(self) -> None`: Direct construction from frontmatter dict.
- `test_from_frontmatter_with_dates(self) -> None`: Date strings and date objects are coerced correctly.
- `test_from_frontmatter_with_links(self) -> None`: Links object is parsed correctly.
- `test_full_construction(self) -> None`: Construct with all fields populated.
- `test_links_defaults_empty(self) -> None`: links field defaults to empty dict.
- `test_minimal_construction(self) -> None`: Construct with only required fields.
- `test_optional_fields_default(self) -> None`: Optional fields have sensible defaults.
- `test_to_dict_empty_path(self) -> None`: to_dict handles empty path.
- `test_to_dict_full(self) -> None`: to_dict includes all populated fields.
- `test_to_dict_minimal(self) -> None`: to_dict with minimal record omits empty optional fields.
- `test_to_dict_omits_empty_links(self) -> None`: to_dict omits links when empty.
- `test_to_dict_path_relativization(self) -> None`: to_dict relativizes path against root.
- `test_to_dict_with_links(self) -> None`: to_dict includes links when non-empty.

### TestMemoryRecordVerifiedSha

Tests for verified_sha field on MemoryRecord.

**Inherits from:** unittest.TestCase

#### Methods

- `test_from_frontmatter_with_verified_sha(self) -> None`
- `test_from_frontmatter_without_verified_sha(self) -> None`
- `test_to_dict_includes_verified_sha_when_present(self) -> None`
- `test_to_dict_omits_verified_sha_when_none(self) -> None`
