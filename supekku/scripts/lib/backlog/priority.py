"""Priority ordering and head-tail partitioning for backlog items.

This module implements the priority ordering logic for backlog items,
including the head-tail partition algorithm used for smart merging of
filtered item reordering.
"""

from __future__ import annotations

import re
from typing import TypeVar

from .models import BacklogItem

T = TypeVar("T")


def build_partitions(
  all_items: list[T], filtered_items: set[T]
) -> tuple[list[T], list[tuple[T, list[T]]]]:
  """Partition items into (shown, [unshown_followers]) pairs.

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
  """
  prefix: list[T] = []
  partitions: list[tuple[T, list[T]]] = []
  current_tail: list[T] = []
  seen_first_shown = False

  for item in all_items:
    if item in filtered_items:
      if not seen_first_shown:
        # First shown item - current_tail is actually the prefix
        prefix = current_tail.copy()
        current_tail = []
        seen_first_shown = True
      else:
        # Subsequent shown item - attach current_tail to previous partition
        if partitions:
          last_head, _ = partitions[-1]
          partitions[-1] = (last_head, current_tail)
        current_tail = []
      # Add this shown item with empty tail (will be filled next iteration)
      partitions.append((item, []))
    else:
      current_tail.append(item)

  # Attach any remaining tail to the last partition
  if current_tail and partitions:
    last_head, _ = partitions[-1]
    partitions[-1] = (last_head, current_tail)
  elif current_tail and not seen_first_shown:
    # No shown items at all - everything is prefix
    prefix = current_tail

  return prefix, partitions


def merge_ordering(
  prefix: list[T], partitions: list[tuple[T, list[T]]], new_filtered_order: list[T]
) -> list[T]:
  """Reorder partitions based on new filtered order, then flatten.

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
  """
  # Create lookup for partitions by head
  partition_map = {head: (head, tail) for head, tail in partitions}

  # Start with prefix
  result = prefix.copy()

  # Reorder based on new_filtered_order
  for head in new_filtered_order:
    if head in partition_map:
      head_item, tail_items = partition_map[head]
      result.append(head_item)
      result.extend(tail_items)

  return result


def sort_by_priority(
  items: list[BacklogItem], ordering: list[str]
) -> list[BacklogItem]:
  """Sort backlog items by priority with fallback to severity and ID.

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
  """
  # Build registry index map (ID -> position)
  registry_index = {item_id: idx for idx, item_id in enumerate(ordering)}

  # Severity ranking (lower = higher priority)
  severity_rank = {
    "p1": 0,
    "p2": 1,
    "p3": 2,
    "": 3,  # No severity
  }

  def sort_key(item: BacklogItem) -> tuple[int, int, str]:
    """Generate sort key: (registry_position, severity_rank, id)."""
    reg_pos = registry_index.get(item.id, 999999)  # Large number for unregistered
    sev_rank = severity_rank.get(item.severity.lower() if item.severity else "", 3)
    return (reg_pos, sev_rank, item.id)

  return sorted(items, key=sort_key)


def generate_markdown_list(items: list[BacklogItem]) -> str:
  """Generate markdown checklist from backlog items.

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
  """
  lines = []
  for item in items:
    # Build item line
    severity_str = f" ({item.severity})" if item.severity else ""

    # Truncate long titles to keep list readable
    title = item.title
    max_title_len = 80
    if len(title) > max_title_len:
      title = title[: max_title_len - 3] + "..."

    line = f"- [ ] {item.id}{severity_str}: {title}"
    lines.append(line)

  return "\n".join(lines)


def parse_markdown_list(markdown: str) -> list[str]:
  """Parse markdown checklist and extract item IDs in order.

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
    >>> markdown = "- [ ] ISSUE-003: Fix\\n- [ ] IMPR-002: Add"
    >>> parse_markdown_list(markdown)
    ["ISSUE-003", "IMPR-002"]
  """
  # Pattern matches backlog IDs: KIND-NUMBER (e.g., ISSUE-003, IMPR-002)
  id_pattern = re.compile(r"([A-Z]+-\d+)")

  ids: list[str] = []
  seen: set[str] = set()

  for line in markdown.split("\n"):
    # Skip blank lines and comments
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
      continue

    # Extract first ID match from line
    match = id_pattern.search(line)
    if match:
      item_id = match.group(1)
      # Keep first occurrence only (ignore duplicates)
      if item_id not in seen:
        ids.append(item_id)
        seen.add(item_id)

  if not ids:
    msg = "No valid backlog item IDs found in markdown"
    raise ValueError(msg)

  return ids


def edit_backlog_ordering(
  all_items: list[BacklogItem],
  filtered_items: list[BacklogItem],
  current_ordering: list[str],
) -> list[str]:
  """Interactive editor flow for reordering backlog items.

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
  """
  # Import here to avoid circular dependency
  from supekku.scripts.lib.core.editor import invoke_editor  # noqa: PLC0415, I001

  # Sort items by current ordering
  all_sorted = sort_by_priority(all_items, current_ordering)
  filtered_sorted = sort_by_priority(filtered_items, current_ordering)

  # Generate markdown list from filtered items
  markdown_content = generate_markdown_list(filtered_sorted)

  # Instructions for user
  instructions = (
    "Reorder backlog items by moving lines up/down. Save and exit to apply changes."
  )

  # Invoke editor
  edited_content = invoke_editor(markdown_content, instructions)

  # If user cancelled (None or empty), return None to indicate cancellation
  if not edited_content:
    return None

  # Parse edited markdown to get new order
  new_filtered_ids = parse_markdown_list(edited_content)

  # Build filtered item objects for new order (preserve object references)
  filtered_map = {item.id: item for item in filtered_items}
  new_filtered_items = [
    filtered_map[item_id] for item_id in new_filtered_ids if item_id in filtered_map
  ]

  # Detect deleted items: items that were shown but aren't in the edited list
  original_filtered_ids = {item.id for item in filtered_sorted}
  kept_filtered_ids = set(new_filtered_ids)
  deleted_ids = original_filtered_ids - kept_filtered_ids

  # Create set of IDs that should be treated as "unshown" during partitioning
  # This includes both originally hidden items AND deleted items
  filtered_id_set = {item.id for item in filtered_sorted if item.id not in deleted_ids}

  # Build partitions using ID-based checking
  prefix: list[BacklogItem] = []
  partitions: list[tuple[BacklogItem, list[BacklogItem]]] = []
  current_tail: list[BacklogItem] = []
  seen_first_shown = False

  for item in all_sorted:
    if item.id in filtered_id_set:
      if not seen_first_shown:
        prefix = current_tail.copy()
        current_tail = []
        seen_first_shown = True
      else:
        if partitions:
          last_head, _ = partitions[-1]
          partitions[-1] = (last_head, current_tail)
        current_tail = []
      partitions.append((item, []))
    else:
      current_tail.append(item)

  # Attach any remaining tail
  if current_tail and partitions:
    last_head, _ = partitions[-1]
    partitions[-1] = (last_head, current_tail)
  elif current_tail and not seen_first_shown:
    prefix = current_tail

  # Merge using new order - use ID-based lookup instead of object keys
  partition_map = {head.id: (head, tail) for head, tail in partitions}

  # Start with prefix
  result = prefix.copy()

  # Reorder based on new_filtered_order
  for head in new_filtered_items:
    if head.id in partition_map:
      head_item, tail_items = partition_map[head.id]
      result.append(head_item)
      result.extend(tail_items)

  # Return IDs only
  return [item.id for item in result]
