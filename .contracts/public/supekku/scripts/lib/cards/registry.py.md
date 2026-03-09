# supekku.scripts.lib.cards.registry

Card registry for discovery, ID allocation, and card management.

## Constants

- `VALID_LANES`

## Classes

### CardRegistry

Registry for managing kanban cards.

#### Methods

- `all_cards(self) -> list[Card]`: Discover all cards in kanban directory.

Returns:
  List of all Card instances found - ------------------------------------------------------------------
- `cards_by_lane(self, lane) -> list[Card]`: Get all cards in a specific lane.

Args:
  lane: Lane name (backlog, doing, done)

Returns:
  List of cards in the specified lane
- `collect(self) -> dict[Tuple[str, Card]]`: Return all cards as a dictionary keyed by ID.

Returns:
  Dictionary mapping card ID to Card.
- `create_card(self, description, lane) -> Card`: Create a new card from template.

Args:
  description: Card description for the title
  lane: Target lane (backlog/doing/done), default backlog

Returns:
  Created Card instance

Raises:
  ValueError: If lane is invalid
- `filter(self) -> list[Card]`: Filter cards by lane.

Args:
  lane: Filter by lane (backlog/doing/done).

Returns:
  List of matching Cards.
- `find(self, card_id) -> <BinOp>`: Find a card by its ID.

Returns:
  Card or None if not found. - -- ADR-009 standard surface --------------------------------------------
- `iter(self) -> Iterator[Card]`: Iterate over cards, optionally filtered by lane.

Args:
  lane: If provided, yield only cards in this lane.

Yields:
  Card instances.
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
