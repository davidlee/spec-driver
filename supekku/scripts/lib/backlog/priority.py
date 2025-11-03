"""Priority ordering and head-tail partitioning for backlog items.

This module implements the priority ordering logic for backlog items,
including the head-tail partition algorithm used for smart merging of
filtered item reordering.
"""

from typing import TypeVar

from .models import BacklogItem

T = TypeVar('T')


def build_partitions(
  all_items: list[T],
  filtered_items: set[T]
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
  prefix: list[T],
  partitions: list[tuple[T, list[T]]],
  new_filtered_order: list[T]
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
  items: list[BacklogItem],
  ordering: list[str]
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
    'p1': 0,
    'p2': 1,
    'p3': 2,
    '': 3,  # No severity
  }

  def sort_key(item: BacklogItem) -> tuple[int, int, str]:
    """Generate sort key: (registry_position, severity_rank, id)."""
    reg_pos = registry_index.get(item.id, 999999)  # Large number for unregistered
    sev_rank = severity_rank.get(item.severity.lower() if item.severity else '', 3)
    return (reg_pos, sev_rank, item.id)

  return sorted(items, key=sort_key)
