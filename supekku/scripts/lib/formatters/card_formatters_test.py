"""Tests for card formatters.

VT-021-006: list cards output formats (table/json/tsv)
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from supekku.scripts.lib.cards import Card
from supekku.scripts.lib.formatters.card_formatters import (
  format_card_details,
  format_card_list_json,
  format_card_list_table,
)


class TestCardFormatters(unittest.TestCase):
  """VT-021-006: Output format consistency."""

  def test_format_card_details(self) -> None:
    """Format card as human-readable detail view."""
    card = Card(
      id="T123",
      title="Fix the bug",
      lane="doing",
      path=Path("/kanban/doing/T123-fix.md"),
      created="2026-02-03",
    )

    output = format_card_details(card)

    self.assertIn("ID: T123", output)
    self.assertIn("Title: Fix the bug", output)
    self.assertIn("Lane: doing", output)
    self.assertIn("Created: 2026-02-03", output)

  def test_format_card_details_without_lane(self) -> None:
    """Handle card without lane."""
    card = Card(
      id="T456",
      title="Task",
      lane=None,
      path=Path("/other/T456-task.md"),
      created="2026-02-03",
    )

    output = format_card_details(card)

    self.assertIn("Lane: unknown", output)

  def test_format_card_details_without_created(self) -> None:
    """Handle card without created date."""
    card = Card(
      id="T789",
      title="Old card",
      lane="backlog",
      path=Path("/kanban/backlog/T789-old.md"),
      created=None,
    )

    output = format_card_details(card)

    self.assertNotIn("Created:", output)

  def test_format_card_list_table_aligned(self) -> None:
    """Format cards as aligned table."""
    cards = [
      Card("T001", "First task", "backlog", Path("/k/b/T001.md"), "2026-02-01"),
      Card("T002", "Second task", "doing", Path("/k/d/T002.md"), "2026-02-02"),
      Card("T003", "Third task", "done", Path("/k/d/T003.md"), "2026-02-03"),
    ]

    output = format_card_list_table(cards, format_type="table")

    # Should have headers
    self.assertIn("ID", output)
    self.assertIn("Lane", output)
    self.assertIn("Title", output)
    self.assertIn("Created", output)

    # Should have card data
    self.assertIn("T001", output)
    self.assertIn("First task", output)
    self.assertIn("backlog", output)
    self.assertIn("T002", output)
    self.assertIn("doing", output)
    self.assertIn("T003", output)
    self.assertIn("done", output)

  def test_format_card_list_tsv(self) -> None:
    """Format cards as tab-separated values."""
    cards = [
      Card("T001", "Task one", "backlog", Path("/k/b/T001.md"), "2026-02-01"),
      Card("T002", "Task two", "doing", Path("/k/d/T002.md"), "2026-02-02"),
    ]

    output = format_card_list_table(cards, format_type="tsv")

    # Should have tab-separated values
    lines = output.split("\n")
    self.assertGreater(len(lines), 2)  # Header + at least 2 cards

    # Check header
    self.assertIn("\t", lines[0])
    self.assertIn("ID", lines[0])

    # Check data rows
    self.assertIn("T001\t", lines[1])
    self.assertIn("T002\t", lines[2])

  def test_format_card_list_json_valid(self) -> None:
    """Format cards as valid JSON array."""
    cards = [
      Card("T001", "Task one", "backlog", Path("/k/b/T001.md"), "2026-02-01"),
      Card("T002", "Task two", None, Path("/other/T002.md"), None),
    ]

    output = format_card_list_json(cards)

    # Should be valid JSON with standard structure
    parsed = json.loads(output)
    self.assertIn("items", parsed)
    items = parsed["items"]
    self.assertIsInstance(items, list)
    self.assertEqual(len(items), 2)

    # Check first card
    self.assertEqual(items[0]["id"], "T001")
    self.assertEqual(items[0]["title"], "Task one")
    self.assertEqual(items[0]["lane"], "backlog")
    self.assertEqual(items[0]["created"], "2026-02-01")

    # Check second card (with None values)
    self.assertEqual(items[1]["id"], "T002")
    self.assertIsNone(items[1]["lane"])
    self.assertIsNone(items[1]["created"])

  def test_format_empty_card_list(self) -> None:
    """Handle empty card list gracefully."""
    output = format_card_list_table([], format_type="table")
    self.assertEqual(output, "No cards found.")

    output_json = format_card_list_json([])
    parsed = json.loads(output_json)
    self.assertEqual(parsed["items"], [])
