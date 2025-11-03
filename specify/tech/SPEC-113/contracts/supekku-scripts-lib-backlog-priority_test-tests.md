# supekku.scripts.lib.backlog.priority_test

Tests for backlog priority ordering and partitioning.

VT-015-001: Head-tail partition algorithm tests
VT-015-003: Priority ordering sort function tests
VT-015-004: Editor utility and markdown functions tests

## Classes

### HeadTailPartitionTest

VT-015-001: Tests for head-tail partition algorithm.

**Inherits from:** unittest.TestCase

#### Methods

- `test_build_partitions_all_filtered(self)`: Test partitioning when all items are shown.
- `test_build_partitions_consecutive_shown(self)`: Test partitioning with consecutive shown items (empty tails).
- `test_build_partitions_no_prefix(self)`: Test partitioning when first item is shown.
- `test_build_partitions_none_filtered(self)`: Test partitioning when no items are shown (all go to prefix).
- `test_build_partitions_simple_case(self)`: Test basic partitioning with interspersed shown/unshown items.
- `test_build_partitions_trailing_unshown(self)`: Test handling of trailing unshown items.
- `test_merge_ordering_empty_prefix(self)`: Test merge with no prefix items.
- `test_merge_ordering_preserves_prefix(self)`: Test that prefix items stay at the beginning.
- `test_merge_ordering_reorders_heads(self)`: Test that merge_ordering correctly reorders heads with tails.
- `test_merge_ordering_single_item(self)`: Test merge with a single shown item.
- `test_roundtrip_partition_and_merge(self)`: Test that partition + merge preserves original order when filter unchanged.

### PrioritySortTest

VT-015-003: Tests for priority sort function.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self)`: Create test backlog items.
- `test_sort_by_priority_case_insensitive_severity(self)`: Test that severity comparison handles case variations.
- `test_sort_by_priority_empty_items(self)`: Test sorting empty list. - no severity
- `test_sort_by_priority_empty_registry(self)`: Test sorting with empty registry falls back to severity/ID.
- `test_sort_by_priority_id_fallback(self)`: Test ID alphabetical ordering as final fallback.
- `test_sort_by_priority_partial_registry(self)`: Test mixed scenario: some items in registry, some not.
- `test_sort_by_priority_registry_order_trumps_severity(self)`: Test that registry position takes precedence over severity.
- `test_sort_by_priority_severity_fallback(self)`: Test severity ordering for items not in registry.

### TestGenerateMarkdownList

Test generate_markdown_list function.

**Inherits from:** unittest.TestCase

#### Methods

- `test_basic_list_generation(self) -> None`: Test generating markdown list from backlog items.
- `test_empty_list(self) -> None`: Test generating markdown from empty list.
- `test_long_title_truncation(self) -> None`: Test that long titles are truncated.
- `test_with_severity(self) -> None`: Test markdown generation includes severity.

### TestParseMarkdownList

Test parse_markdown_list function.

**Inherits from:** unittest.TestCase

#### Methods

- `test_basic_parsing(self) -> None`: Test parsing markdown list with checkboxes.
- `test_duplicate_ids_kept_first(self) -> None`: Test that duplicate IDs keep only first occurrence.
- `test_empty_markdown_raises(self) -> None`: Test that empty markdown raises ValueError.
- `test_ignores_blank_lines(self) -> None`: Test that blank lines are ignored.
- `test_ignores_comments(self) -> None`: Test that comment lines are ignored.
- `test_mixed_formats(self) -> None`: Test parsing various markdown formats together.
- `test_no_ids_raises(self) -> None`: Test that markdown with no IDs raises ValueError.
- `test_with_severity(self) -> None`: Test parsing handles severity in parentheses.
- `test_without_checkbox(self) -> None`: Test parsing items without checkbox syntax.
