# supekku.scripts.lib.formatters.card_formatters

Card display formatters.

Pure formatting functions with no business logic.
Formatters take Card objects and return formatted strings for display.

## Functions

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
- `format_card_list_table(cards, format_type) -> str`: Format cards as table or TSV.

Args:
  cards: Sequence of Card instances
  format_type: Output format ("table" or "tsv")

Returns:
  Formatted output string
