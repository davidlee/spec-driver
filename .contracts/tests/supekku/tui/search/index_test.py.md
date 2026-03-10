# supekku.tui.search.index_test

Tests for search index builder (VT-087-002).

## Functions

- `_make_entry() -> ArtifactEntry`

## Classes

### TestBuildSearchIndex

Test build_search_index end-to-end.

#### Methods

- `test_empty_when_no_factories(self)`
- `test_produces_entries_for_working_registries(self)`
- `test_skips_failing_records(self)`: If adapt_record fails for one record, others still indexed.
- `test_skips_failing_registries(self)`

### TestExtractRelationTargets

Test _extract_relation_targets.

#### Methods

- `test_empty_relations(self)`
- `test_no_relations(self)`
- `test_record_without_relations_attr(self)`
- `test_with_relations(self)`

### TestExtractSearchableFields

Test _extract_searchable_fields.

#### Methods

- `test_core_fields(self)`
- `test_empty_string_attrs_omitted(self)`
- `test_empty_tags_list(self)`
- `test_missing_attrs_omitted(self)`
- `test_record_without_optional_attrs(self)`: Records that lack certain attrs entirely (e.g. no .slug).
- `test_scalar_frontmatter_attrs(self)`
- `test_tags_none(self)`
- `test_tags_produce_per_tag_entries(self)`
- `test_whitespace_tags_stripped(self)`

### _BadRecord

### _FakeRecord

Minimal record for testing field extraction.
