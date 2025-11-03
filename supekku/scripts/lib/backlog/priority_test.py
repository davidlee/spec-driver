"""Tests for backlog priority ordering and partitioning.

VT-015-001: Head-tail partition algorithm tests
VT-015-003: Priority ordering sort function tests
VT-015-004: Editor utility and markdown functions tests
"""

import unittest
from pathlib import Path

from .models import BacklogItem
from .priority import (
  build_partitions,
  generate_markdown_list,
  merge_ordering,
  parse_markdown_list,
  sort_by_priority,
)


class HeadTailPartitionTest(unittest.TestCase):
  """VT-015-001: Tests for head-tail partition algorithm."""

  def test_build_partitions_simple_case(self):
    """Test basic partitioning with interspersed shown/unshown items."""
    all_items = ['a', 'b', 'c', 'd', 'e']
    filtered = {'b', 'd'}
    prefix, partitions = build_partitions(all_items, filtered)

    self.assertEqual(['a'], prefix)
    self.assertEqual([('b', ['c']), ('d', ['e'])], partitions)

  def test_build_partitions_no_prefix(self):
    """Test partitioning when first item is shown."""
    all_items = ['a', 'b', 'c', 'd']
    filtered = {'a', 'c'}
    prefix, partitions = build_partitions(all_items, filtered)

    self.assertEqual([], prefix)
    self.assertEqual([('a', ['b']), ('c', ['d'])], partitions)

  def test_build_partitions_all_filtered(self):
    """Test partitioning when all items are shown."""
    all_items = ['a', 'b', 'c']
    filtered = {'a', 'b', 'c'}
    prefix, partitions = build_partitions(all_items, filtered)

    self.assertEqual([], prefix)
    self.assertEqual([('a', []), ('b', []), ('c', [])], partitions)

  def test_build_partitions_none_filtered(self):
    """Test partitioning when no items are shown (all go to prefix)."""
    all_items = ['a', 'b', 'c']
    filtered = set()
    prefix, partitions = build_partitions(all_items, filtered)

    self.assertEqual(['a', 'b', 'c'], prefix)
    self.assertEqual([], partitions)

  def test_build_partitions_trailing_unshown(self):
    """Test handling of trailing unshown items."""
    all_items = ['a', 'b', 'c', 'd', 'e', 'f']
    filtered = {'b', 'd'}
    prefix, partitions = build_partitions(all_items, filtered)

    self.assertEqual(['a'], prefix)
    # Last partition includes all trailing items
    self.assertEqual([('b', ['c']), ('d', ['e', 'f'])], partitions)

  def test_build_partitions_consecutive_shown(self):
    """Test partitioning with consecutive shown items (empty tails)."""
    all_items = ['a', 'b', 'c', 'd', 'e']
    filtered = {'b', 'c', 'd'}
    prefix, partitions = build_partitions(all_items, filtered)

    self.assertEqual(['a'], prefix)
    self.assertEqual([('b', []), ('c', []), ('d', ['e'])], partitions)

  def test_merge_ordering_reorders_heads(self):
    """Test that merge_ordering correctly reorders heads with tails."""
    prefix = ['a']
    partitions = [('b', ['c']), ('d', ['e', 'f'])]
    new_order = ['d', 'b']

    result = merge_ordering(prefix, partitions, new_order)
    self.assertEqual(['a', 'd', 'e', 'f', 'b', 'c'], result)

  def test_merge_ordering_preserves_prefix(self):
    """Test that prefix items stay at the beginning."""
    prefix = ['x', 'y']
    partitions = [('a', ['b']), ('c', ['d'])]
    new_order = ['c', 'a']

    result = merge_ordering(prefix, partitions, new_order)
    self.assertEqual(['x', 'y', 'c', 'd', 'a', 'b'], result)

  def test_merge_ordering_empty_prefix(self):
    """Test merge with no prefix items."""
    prefix = []
    partitions = [('a', ['b', 'c']), ('d', [])]
    new_order = ['d', 'a']

    result = merge_ordering(prefix, partitions, new_order)
    self.assertEqual(['d', 'a', 'b', 'c'], result)

  def test_merge_ordering_single_item(self):
    """Test merge with a single shown item."""
    prefix = ['x']
    partitions = [('a', ['b', 'c'])]
    new_order = ['a']

    result = merge_ordering(prefix, partitions, new_order)
    self.assertEqual(['x', 'a', 'b', 'c'], result)

  def test_roundtrip_partition_and_merge(self):
    """Test that partition + merge preserves original order when filter unchanged."""
    all_items = ['a', 'b', 'c', 'd', 'e', 'f']
    filtered = {'b', 'd', 'e'}

    prefix, partitions = build_partitions(all_items, filtered)
    # Use original filtered order
    original_filtered_order = [item for item in all_items if item in filtered]
    result = merge_ordering(prefix, partitions, original_filtered_order)

    self.assertEqual(all_items, result)


class PrioritySortTest(unittest.TestCase):
  """VT-015-003: Tests for priority sort function."""

  def setUp(self):
    """Create test backlog items."""
    self.items = [
      BacklogItem(
        id='ISSUE-001', kind='issue', status='open', title='A',
        path='', severity='p2'
      ),
      BacklogItem(
        id='ISSUE-002', kind='issue', status='open', title='B',
        path='', severity='p1'
      ),
      BacklogItem(
        id='ISSUE-003', kind='issue', status='open', title='C',
        path='', severity='p3'
      ),
      BacklogItem(
        id='IMPR-001', kind='improvement', status='open', title='D',
        path='', severity=''
      ),
      BacklogItem(
        id='IMPR-002', kind='improvement', status='open', title='E',
        path='', severity='p1'
      ),
    ]

  def test_sort_by_priority_registry_order_trumps_severity(self):
    """Test that registry position takes precedence over severity."""
    ordering = ['ISSUE-003', 'ISSUE-002', 'ISSUE-001']  # p3, p1, p2
    sorted_items = sort_by_priority(self.items, ordering)

    # Should follow registry order despite severity, then unregistered by severity/ID
    # IMPR-002 (p1) comes before IMPR-001 (no severity)
    self.assertEqual(['ISSUE-003', 'ISSUE-002', 'ISSUE-001', 'IMPR-002', 'IMPR-001'],
                     [item.id for item in sorted_items])

  def test_sort_by_priority_severity_fallback(self):
    """Test severity ordering for items not in registry."""
    ordering = []  # Empty registry
    sorted_items = sort_by_priority(self.items, ordering)

    # Should sort by severity: p1, p1, p2, p3, none
    self.assertEqual('p1', sorted_items[0].severity)
    self.assertEqual('p1', sorted_items[1].severity)
    self.assertEqual('p2', sorted_items[2].severity)
    self.assertEqual('p3', sorted_items[3].severity)
    self.assertEqual('', sorted_items[4].severity)

  def test_sort_by_priority_id_fallback(self):
    """Test ID alphabetical ordering as final fallback."""
    # Items with same severity
    items = [
      BacklogItem(
        id='ISSUE-003', kind='issue', status='open',
        title='C', path='', severity='p2'
      ),
      BacklogItem(
        id='ISSUE-001', kind='issue', status='open',
        title='A', path='', severity='p2'
      ),
      BacklogItem(
        id='ISSUE-002', kind='issue', status='open',
        title='B', path='', severity='p2'
      ),
    ]
    ordering = []
    sorted_items = sort_by_priority(items, ordering)

    self.assertEqual(['ISSUE-001', 'ISSUE-002', 'ISSUE-003'],
                     [item.id for item in sorted_items])

  def test_sort_by_priority_partial_registry(self):
    """Test mixed scenario: some items in registry, some not."""
    ordering = ['IMPR-002', 'ISSUE-001']  # Only 2 items in registry
    sorted_items = sort_by_priority(self.items, ordering)

    ids = [item.id for item in sorted_items]
    # Registry items first
    self.assertEqual('IMPR-002', ids[0])
    self.assertEqual('ISSUE-001', ids[1])
    # Then unregistered sorted by severity/ID
    self.assertEqual('ISSUE-002', ids[2])  # p1
    self.assertEqual('ISSUE-003', ids[3])  # p3
    self.assertEqual('IMPR-001', ids[4])  # no severity

  def test_sort_by_priority_empty_items(self):
    """Test sorting empty list."""
    sorted_items = sort_by_priority([], ['ISSUE-001'])
    self.assertEqual([], sorted_items)

  def test_sort_by_priority_empty_registry(self):
    """Test sorting with empty registry falls back to severity/ID."""
    sorted_items = sort_by_priority(self.items, [])

    # Should be ordered by severity (p1 items first, then p2, p3, none)
    # Just verify p1 items come before p2, p2 before p3, etc.
    severity_order = {'p1': 0, 'p2': 1, 'p3': 2, '': 3}
    severity_ranks = [severity_order.get(item.severity, 3) for item in sorted_items]

    # Verify non-decreasing severity ranks
    for i in range(len(severity_ranks) - 1):
      self.assertLessEqual(
        severity_ranks[i], severity_ranks[i + 1],
        f"Severity rank at {i} ({severity_ranks[i]}) "
        f"> rank at {i+1} ({severity_ranks[i+1]})"
      )

  def test_sort_by_priority_case_insensitive_severity(self):
    """Test that severity comparison handles case variations."""
    items = [
      BacklogItem(
        id='A', kind='issue', status='open', title='', path='', severity='P2'
      ),
      BacklogItem(
        id='B', kind='issue', status='open', title='', path='', severity='p1'
      ),
      BacklogItem(
        id='C', kind='issue', status='open', title='', path='', severity='P3'
      ),
    ]
    sorted_items = sort_by_priority(items, [])

    self.assertEqual(['B', 'A', 'C'], [item.id for item in sorted_items])


class TestGenerateMarkdownList(unittest.TestCase):
  """Test generate_markdown_list function."""

  def test_basic_list_generation(self) -> None:
    """Test generating markdown list from backlog items."""

    items = [
      BacklogItem(id='ISSUE-001', kind='issue', status='open', title='Fix bug', path=Path()),  # noqa: E501
      BacklogItem(id='IMPR-002', kind='improvement', status='idea', title='Add feature', path=Path()),  # noqa: E501
    ]

    result = generate_markdown_list(items)

    expected = "- [ ] ISSUE-001: Fix bug\n- [ ] IMPR-002: Add feature"
    self.assertEqual(expected, result)

  def test_with_severity(self) -> None:
    """Test markdown generation includes severity."""

    items = [
      BacklogItem(id='ISSUE-001', kind='issue', status='open', title='Bug', path=Path(), severity='p1'),  # noqa: E501
      BacklogItem(id='ISSUE-002', kind='issue', status='open', title='Minor', path=Path(), severity='p3'),  # noqa: E501
    ]

    result = generate_markdown_list(items)

    assert "ISSUE-001 (p1):" in result
    assert "ISSUE-002 (p3):" in result

  def test_long_title_truncation(self) -> None:
    """Test that long titles are truncated."""

    long_title = "A" * 100
    items = [BacklogItem(id='ISSUE-001', kind='issue', status='open', title=long_title, path=Path())]  # noqa: E501

    result = generate_markdown_list(items)

    assert len(result.split(': ', 1)[1]) <= 83  # 80 chars + "..."
    assert result.endswith("...")

  def test_empty_list(self) -> None:
    """Test generating markdown from empty list."""

    result = generate_markdown_list([])

    self.assertEqual("", result)


class TestParseMarkdownList(unittest.TestCase):
  """Test parse_markdown_list function."""

  def test_basic_parsing(self) -> None:
    """Test parsing markdown list with checkboxes."""

    markdown = """- [ ] ISSUE-003: Fix bug
- [ ] IMPR-002: Add feature
- [ ] ISSUE-005: Another fix"""

    result = parse_markdown_list(markdown)

    self.assertEqual(['ISSUE-003', 'IMPR-002', 'ISSUE-005'], result)

  def test_with_severity(self) -> None:
    """Test parsing handles severity in parentheses."""

    markdown = "- [ ] ISSUE-003 (p1): Critical bug\n- [ ] IMPR-002 (p2): Enhancement"

    result = parse_markdown_list(markdown)

    self.assertEqual(['ISSUE-003', 'IMPR-002'], result)

  def test_without_checkbox(self) -> None:
    """Test parsing items without checkbox syntax."""

    markdown = "ISSUE-003: Fix bug\nIMPR-002: Add feature"

    result = parse_markdown_list(markdown)

    self.assertEqual(['ISSUE-003', 'IMPR-002'], result)

  def test_ignores_blank_lines(self) -> None:
    """Test that blank lines are ignored."""

    markdown = """ISSUE-003: Fix

IMPR-002: Add

"""

    result = parse_markdown_list(markdown)

    self.assertEqual(['ISSUE-003', 'IMPR-002'], result)

  def test_ignores_comments(self) -> None:
    """Test that comment lines are ignored."""

    markdown = """# This is a header
ISSUE-003: Fix
# Another comment
IMPR-002: Add"""

    result = parse_markdown_list(markdown)

    self.assertEqual(['ISSUE-003', 'IMPR-002'], result)

  def test_duplicate_ids_kept_first(self) -> None:
    """Test that duplicate IDs keep only first occurrence."""

    markdown = """ISSUE-003: First
ISSUE-003: Duplicate
IMPR-002: Second"""

    result = parse_markdown_list(markdown)

    self.assertEqual(['ISSUE-003', 'IMPR-002'], result)

  def test_empty_markdown_raises(self) -> None:
    """Test that empty markdown raises ValueError."""

    with self.assertRaises(ValueError) as cm:
      parse_markdown_list("")

    self.assertIn("No valid backlog item IDs", str(cm.exception))

  def test_no_ids_raises(self) -> None:
    """Test that markdown with no IDs raises ValueError."""

    markdown = "Some text without any IDs\nJust random content"

    with self.assertRaises(ValueError) as cm:
      parse_markdown_list(markdown)

    self.assertIn("No valid backlog item IDs", str(cm.exception))

  def test_mixed_formats(self) -> None:
    """Test parsing various markdown formats together."""

    markdown = """# Priority Order
- [ ] ISSUE-003: Fix critical bug
IMPR-002 (p2): Enhancement
- ISSUE-005: Another issue
"""

    result = parse_markdown_list(markdown)

    self.assertEqual(['ISSUE-003', 'IMPR-002', 'ISSUE-005'], result)


if __name__ == '__main__':
  unittest.main()
