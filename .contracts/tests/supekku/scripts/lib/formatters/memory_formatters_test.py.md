# supekku.scripts.lib.formatters.memory_formatters_test

Tests for memory display formatters.

## Functions

- `_make_record() -> MemoryRecord`: Create a MemoryRecord with sensible defaults, overridable.
- `_make_staleness(memory_id, verified_sha, verified_date, scope_paths, commits_since, days_since, has_scope, confidence) -> tuple[Tuple[StalenessInfo, MemoryRecord]]`: Build a StalenessInfo + MemoryRecord pair for formatter tests.
- `_sample_nodes() -> list[LinkGraphNode]`

## Classes

### TestFormatLinkGraphJson

Tests for format_link_graph_json.

#### Methods

- `test_empty(self) -> None`
- `test_multi_node(self) -> None`
- `test_structure(self) -> None`

### TestFormatLinkGraphTable

Tests for format_link_graph_table.

#### Methods

- `test_empty(self) -> None`
- `test_includes_type(self) -> None`
- `test_multi_depth_indentation(self) -> None`
- `test_single_node(self) -> None`

### TestFormatLinkGraphTree

Tests for format_link_graph_tree.

#### Methods

- `test_empty(self) -> None`
- `test_empty_type_no_suffix(self) -> None`
- `test_multi_depth(self) -> None`
- `test_single_node(self) -> None`

### TestFormatMemoryDetails

Tests for format_memory_details.

#### Methods

- `test_empty_links_omitted(self) -> None`
- `test_empty_priority_omitted(self) -> None`
- `test_empty_provenance_omitted(self) -> None`
- `test_empty_relations_omitted(self) -> None`
- `test_empty_scope_omitted(self) -> None`
- `test_full_record(self) -> None`: All non-empty fields render in detail view.
- `test_includes_confidence(self) -> None`
- `test_includes_dates(self) -> None`
- `test_includes_link_label(self) -> None`
- `test_includes_missing_links(self) -> None`
- `test_includes_path(self) -> None`
- `test_includes_resolved_links(self) -> None`
- `test_includes_summary(self) -> None`
- `test_includes_tags(self) -> None`
- `test_minimal_record(self) -> None`
- `test_no_dates(self) -> None`
- `test_omits_empty_optional_fields(self) -> None`

### TestFormatMemoryListJson

Tests for format_memory_list_json.

#### Methods

- `test_date_serialization_iso(self) -> None`: JSON serializes dates as ISO-8601 strings, not raw date objects.
- `test_empty_list(self) -> None`
- `test_includes_optional_fields(self) -> None`
- `test_json_includes_links(self) -> None`: JSON output includes links when present.
- `test_json_omits_empty_links(self) -> None`: JSON output omits links when empty.
- `test_null_dates_in_json(self) -> None`: JSON serializes None dates as null.
- `test_structure(self) -> None`

### TestFormatMemoryListTable

Tests for format_memory_list_table.

#### Methods

- `test_empty_list(self) -> None`
- `test_json_format(self) -> None`
- `test_table_includes_type_column(self) -> None`
- `test_table_output(self) -> None`
- `test_truncate_table(self) -> None`: Table with truncate=True does not error and still renders.
- `test_tsv_column_content(self) -> None`: TSV columns contain expected values in order.
- `test_tsv_column_count(self) -> None`: TSV rows have exactly 6 columns: id, status, type, name, confidence, updated.
- `test_tsv_format(self) -> None`
- `test_tsv_no_confidence(self) -> None`: TSV renders empty string for missing confidence.

### TestFormatStalenessTable

Tests for format_staleness_table.

#### Methods

- `test_empty_input(self) -> None`
- `test_empty_tier_omitted(self) -> None`: Tiers with no entries are not shown.
- `test_scoped_attested_tier(self) -> None`: Scoped+attested memories appear in tier 1.
- `test_scoped_unattested_tier(self) -> None`: Scoped+unattested memories appear in tier 2. - commits_since
- `test_sort_within_attested_tier(self) -> None`: Attested tier sorts by commits_since descending.
- `test_tier_ordering(self) -> None`: Tiers appear in order: scoped+attested, scoped+unattested, unscoped.
- `test_unscoped_tier(self) -> None`: Unscoped memories appear in tier 3.
