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
- `to_dict(self) -> dict`: Convert card to dictionary for JSON serialization.
