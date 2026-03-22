# supekku.scripts.lib.formatters.card_formatters

Card display formatters.

Pure formatting functions with no business logic.
Formatters take Card objects and return formatted strings for display.

## Functions

- `_calculate_card_column_widths(terminal_width) -> dict[Tuple[int, int]]`: Calculate optimal column widths for card table.

Args:
  terminal_width: Available terminal width

Returns:
  Dictionary mapping column index to max width
- `_card_list_to_tsv(cards) -> str`: Format cards as TSV with header row.
- `_format_card_as_row(card) -> list[str]`: Convert card to table row format.

Args:
  card: Card instance

Returns:
  List of column values [id, lane, title, created]
- `format_card_details(card) -> str`: Format card as human-readable detail view.

Args:
  card: Card instance to format

Returns:
  Formatted string with card details
- `format_card_list_json(cards) -> str`: Format cards as JSON array.

Args:
  cards: Sequence of Card instances

Returns:
  JSON string
- `format_card_list_table(cards, format_type, truncate) -> str`: Format cards as table, JSON, or TSV.

Args:
  cards: Sequence of Card instances
  format_type: Output format (table|json|tsv)
  truncate: If True, truncate long fields.

Returns:
  Formatted output string
