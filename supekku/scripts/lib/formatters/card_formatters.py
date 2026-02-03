"""Card display formatters.

Pure formatting functions with no business logic.
Formatters take Card objects and return formatted strings for display.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from supekku.scripts.lib.formatters.table_utils import (
  add_row_with_truncation,
  create_table,
  format_as_json,
  format_as_tsv,
  get_terminal_width,
  render_table,
)

if TYPE_CHECKING:
  from collections.abc import Sequence

  from supekku.scripts.lib.cards import Card


def format_card_details(card: Card) -> str:
  """Format card as human-readable detail view.

  Args:
    card: Card instance to format

  Returns:
    Formatted string with card details
  """
  lines = [
    f"ID: {card.id}",
    f"Title: {card.title}",
    f"Lane: {card.lane or 'unknown'}",
    f"Path: {card.path}",
  ]

  if card.created:
    lines.append(f"Created: {card.created}")

  return "\n".join(lines)


def _format_card_as_row(card: Card) -> list[str]:
  """Convert card to table row format.

  Args:
    card: Card instance

  Returns:
    List of column values [id, lane, title, created]
  """
  return [
    card.id,
    card.lane or "unknown",
    card.title,
    card.created or "N/A",
  ]


def _format_cards_as_tsv_rows(cards: Sequence[Card]) -> list[list[str]]:
  """Convert cards to TSV row format.

  Args:
    cards: Sequence of Card instances

  Returns:
    List of rows, each row is a list of column values
  """
  return [_format_card_as_row(card) for card in cards]


def _calculate_card_column_widths(terminal_width: int) -> dict[int, int]:
  """Calculate optimal column widths for card table.

  Args:
    terminal_width: Available terminal width

  Returns:
    Dictionary mapping column index to max width
  """
  # Column widths: ID (8), Lane (10), Created (12), rest for Title
  # Reserve space for borders/padding (~10 chars total)
  reserved = 10
  id_width = 8
  lane_width = 10
  created_width = 12
  title_width = max(
    terminal_width - id_width - lane_width - created_width - reserved,
    30,  # minimum title width
  )

  return {
    0: id_width,  # ID
    1: lane_width,  # Lane
    2: title_width,  # Title
    3: created_width,  # Created
  }


def _format_as_table(cards: Sequence[Card]) -> str:
  """Format cards as aligned table.

  Args:
    cards: Sequence of Card instances

  Returns:
    Formatted table string
  """
  if not cards:
    return "No cards found."

  headers = ["ID", "Lane", "Title", "Created"]
  table = create_table(headers)

  terminal_width = get_terminal_width()
  column_widths = _calculate_card_column_widths(terminal_width)

  for card in cards:
    row = _format_card_as_row(card)
    add_row_with_truncation(table, row, column_widths)

  return render_table(table)


def format_card_list_table(
  cards: Sequence[Card],
  format_type: str = "table",
) -> str:
  """Format cards as table or TSV.

  Args:
    cards: Sequence of Card instances
    format_type: Output format ("table" or "tsv")

  Returns:
    Formatted output string
  """
  if format_type == "tsv":
    headers = ["ID", "Lane", "Title", "Created"]
    rows = [headers] + _format_cards_as_tsv_rows(cards)
    return format_as_tsv(rows)

  return _format_as_table(cards)


def format_card_list_json(cards: Sequence[Card]) -> str:
  """Format cards as JSON array.

  Args:
    cards: Sequence of Card instances

  Returns:
    JSON string
  """
  card_dicts = [
    {
      "id": card.id,
      "title": card.title,
      "lane": card.lane,
      "path": str(card.path),
      "created": card.created,
    }
    for card in cards
  ]
  return format_as_json(card_dicts)
