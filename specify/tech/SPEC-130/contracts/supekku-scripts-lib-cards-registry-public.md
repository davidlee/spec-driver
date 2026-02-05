# supekku.scripts.lib.cards.registry

Card registry for discovery, ID allocation, and card management.

## Constants

- `DEFAULT_TEMPLATE`
- `VALID_LANES`

## Classes

### CardRegistry

Registry for managing kanban cards.

#### Methods

- `all_cards(self) -> list[Card]`: Discover all cards in kanban directory.

Returns:
  List of all Card instances found
- `cards_by_lane(self, lane) -> list[Card]`: Get all cards in a specific lane.

Args:
  lane: Lane name (backlog, doing, done)

Returns:
  List of cards in the specified lane
- `create_card(self, description, lane) -> Card`: Create a new card from template.

Args:
  description: Card description for the title
  lane: Target lane (backlog/doing/done), default backlog

Returns:
  Created Card instance

Raises:
  ValueError: If lane is invalid
- `next_id(self) -> str`: Allocate next available card ID.

Scans all lanes for existing T### IDs and returns max + 1.

Returns:
  Next card ID (e.g., "T001", "T042")
- `resolve_card(self, card_id, anywhere) -> Card`: Resolve card ID to Card instance.

Args:
  card_id: Card ID (e.g., "T123")
  anywhere: Search entire repo instead of just kanban/

Returns:
  Resolved Card instance

Raises:
  FileNotFoundError: If card not found
  ValueError: If multiple cards match (ambiguous)
- `resolve_path(self, card_id, anywhere) -> str`: Resolve card ID to path string (for -q flag).

Args:
  card_id: Card ID (e.g., "T123")
  anywhere: Search entire repo instead of just kanban/

Returns:
  Path string to card file
