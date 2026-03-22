# supekku.scripts.lib.backlog.priority

Priority ordering and head-tail partitioning for backlog items.

This module implements the priority ordering logic for backlog items,
including the head-tail partition algorithm used for smart merging of
filtered item reordering.

## Constants

- `T`

## Functions

- `build_partitions(all_items, filtered_items) -> tuple[Tuple[list[T], list[tuple[Tuple[T, list[T]]]]]]`: Partition items into (shown, [unshown_followers]) pairs.

The partition structure preserves the relationship between filtered (shown)
items and their unshown followers. This enables smart merging where
reordering shown items causes their tails to move atomically.

Args:
  all_items: Complete ordered list of items
  filtered_items: Set of items that are visible/shown after filtering

Returns:
  Tuple of (prefix, partitions) where:
    - prefix: Items before the first shown item
    - partitions: List of (head, [tail_items]) pairs
      - head: A shown item (or None for trailing unshown items)
      - tail_items: Unshown items that follow this head

Example:
  all_items = ['a', 'b', 'c', 'd', 'e']
  filtered_items = {'b', 'd'}
  => prefix=['a'], partitions=[('b', ['c']), ('d', ['e'])]
- `edit_backlog_ordering(all_items, filtered_items, current_ordering) -> list[str]`: Interactive editor flow for reordering backlog items.

Opens filtered items in user's editor for reordering, then merges the
edited order with unfiltered items using head-tail partitioning to
preserve relative positions of hidden items.

Items deleted from the editor are preserved in their original position
(treated as unshown items).

Args:
  all_items: Complete list of all backlog items
  filtered_items: Subset of items to show in editor
  current_ordering: Current registry ordering (all item IDs)

Returns:
  Complete new ordering (all item IDs) after merge, or None if cancelled

Raises:
  ValueError: If parsing fails or editor returns invalid data
  EditorError: If editor invocation fails

Example:
  >>> all_items = [item_a, item_b, item_c]
  >>> filtered = [item_a, item_c]  # User only sees a and c
  >>> ordering = ["A", "B", "C"]
  >>> # User reorders to: c, a
  >>> edit_backlog_ordering(all_items, filtered, ordering)
  ["C", "B", "A"]  # B stays in middle (hidden, follows original head)
- `generate_markdown_list(items) -> str`: Generate markdown checklist from backlog items.

Creates a markdown list suitable for interactive editing in a text editor.
Format: "- [ ] ID (severity): Title"

Args:
  items: List of backlog items to format

Returns:
  Markdown string with one item per line

Example:
  >>> items = [BacklogItem(id="ISSUE-003", title="Fix bug", severity="p1")]
  >>> generate_markdown_list(items)
  "- [ ] ISSUE-003 (p1): Fix bug"
- `merge_ordering(prefix, partitions, new_filtered_order) -> list[T]`: Reorder partitions based on new filtered order, then flatten.

Takes the partitioned structure and a new ordering of the filtered items,
then reconstructs the full ordered list with tails moving atomically
with their heads.

Args:
  prefix: Items before the first shown item
  partitions: List of (head, [tail_items]) pairs
  new_filtered_order: New desired order for shown items

Returns:
  Flattened ordered list with tails following their reordered heads

Example:
  prefix = ['a']
  partitions = [('b', ['c']), ('d', ['e'])]
  new_filtered_order = ['d', 'b']
  => ['a', 'd', 'e', 'b', 'c']
- `parse_markdown_list(markdown) -> list[str]`: Parse markdown checklist and extract item IDs in order.

Extracts backlog item IDs using regex pattern matching. Tolerates various
markdown formats and ignores comments, blank lines, and headers.

Supported formats:
  - [ ] ISSUE-003: Title
  - [ ] ISSUE-003 (p3): Title
  - [ ] ISSUE-003
  - ISSUE-003: Title  (without checkbox)

Args:
  markdown: Markdown content to parse

Returns:
  Ordered list of item IDs

Raises:
  ValueError: If no valid IDs found or parsing fails

Example:
  >>> markdown = "- [ ] ISSUE-003: Fix\n- [ ] IMPR-002: Add"
  >>> parse_markdown_list(markdown)
  ["ISSUE-003", "IMPR-002"]
- `sort_by_priority(items, ordering) -> list[BacklogItem]`: Sort backlog items by priority with fallback to severity and ID.

Priority order:
  1. Registry position (lower index = higher priority)
  2. Severity (p1 > p2 > p3 > none)
  3. ID (alphabetical)

Items not in the registry are treated as lowest priority.

Args:
  items: List of backlog items to sort
  ordering: Ordered list of item IDs from registry

Returns:
  Sorted list of backlog items
