"""Card display formatters.

Pure formatting functions with no business logic.
Formatters take Card objects and return formatted strings for display.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from supekku.scripts.lib.formatters.table_utils import (
  format_as_json,
  format_as_tsv,
  format_list_table,
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


def _card_list_to_tsv(cards: Sequence[Card]) -> str:
  """Format cards as TSV with header row."""
  headers = ["ID", "Lane", "Title", "Created"]
  rows = [headers] + [_format_card_as_row(card) for card in cards]
  return format_as_tsv(rows)


def format_card_list_table(
  cards: Sequence[Card],
  format_type: str = "table",
  truncate: bool = False,
) -> str:
  """Format cards as table, JSON, or TSV.

  Args:
    cards: Sequence of Card instances
    format_type: Output format (table|json|tsv)
    truncate: If True, truncate long fields.

  Returns:
    Formatted output string
  """
  if format_type == "tsv":
    return _card_list_to_tsv(cards)

  return format_list_table(
    cards,
    columns=["ID", "Lane", "Title", "Created"],
    title="Cards",
    prepare_row=_format_card_as_row,
    prepare_tsv_row=_format_card_as_row,
    to_json=format_card_list_json,
    format_type=format_type,
    truncate=truncate,
    column_widths=_calculate_card_column_widths,
  )


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
