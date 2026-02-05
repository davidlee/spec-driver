# supekku.scripts.lib.cards.models

Card model for kanban board management.

## Classes

### Card

Card model representing a kanban card with T### ID.

#### Methods

- @classmethod `from_file(cls, card_path) -> Card`: Parse card from markdown file.

Args:
  card_path: Path to card markdown file

Returns:
  Card instance with parsed metadata

Raises:
  ValueError: If ID cannot be parsed from filename
- @staticmethod `_detect_lane_from_path(card_path) -> <BinOp>`: Detect lane from path (kanban/doing/T123.md -> 'doing').
- @staticmethod `_parse_created_from_content(content) -> <BinOp>`: Parse Created: YYYY-MM-DD date from content.
- @staticmethod `_parse_id_from_filename(card_path) -> str`: Extract T### ID from filename.
- @staticmethod `_parse_title_from_content(content, card_id) -> str`: Parse title from first H1 (# T###: Title).
