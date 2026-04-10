"""Card registry for discovery, ID allocation, and card management."""

from __future__ import annotations

import re
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

from supekku.scripts.lib.core import slugify
from supekku.scripts.lib.core.ids import next_sequential_id
from supekku.scripts.lib.core.templates import get_package_templates_dir

from .models import Card

VALID_LANES = {"backlog", "doing", "done"}


class CardRegistry:
  """Registry for managing kanban cards."""

  def __init__(self, root: Path) -> None:
    """Initialize card registry.

    Args:
      root: Repository root path
    """
    self.root = Path(root)
    self.kanban_dir = self.root / "kanban"

  # -- ADR-009 standard surface --------------------------------------------

  def find(self, card_id: str) -> Card | None:
    """Find a card by its ID.

    Returns:
      Card or None if not found.
    """
    for card in self.all_cards():
      if card.id == card_id:
        return card
    return None

  def collect(self) -> dict[str, Card]:
    """Return all cards as a dictionary keyed by ID.

    Returns:
      Dictionary mapping card ID to Card.
    """
    return {card.id: card for card in self.all_cards()}

  def iter(self, *, lane: str | None = None) -> Iterator[Card]:
    """Iterate over cards, optionally filtered by lane.

    Args:
      lane: If provided, yield only cards in this lane.

    Yields:
      Card instances.
    """
    for card in self.all_cards():
      if lane is None or card.lane == lane:
        yield card

  def filter(self, *, lane: str | None = None) -> list[Card]:
    """Filter cards by lane.

    Args:
      lane: Filter by lane (backlog/doing/done).

    Returns:
      List of matching Cards.
    """
    return list(self.iter(lane=lane))

  # ------------------------------------------------------------------

  def all_cards(self) -> list[Card]:
    """Discover all cards in kanban directory.

    Returns:
      List of all Card instances found
    """
    cards = []
    if not self.kanban_dir.exists():
      return cards

    for card_path in self.kanban_dir.rglob("T*.md"):
      if card_path.name.startswith("T") and re.match(r"^T\d+", card_path.stem):
        try:
          card = Card.from_file(card_path)
          cards.append(card)
        except ValueError:
          # Skip files that don't parse as cards
          continue

    return sorted(cards, key=lambda c: c.id)

  def cards_by_lane(self, lane: str) -> list[Card]:
    """Get all cards in a specific lane.

    Args:
      lane: Lane name (backlog, doing, done)

    Returns:
      List of cards in the specified lane
    """
    return [c for c in self.all_cards() if c.lane == lane]

  def next_id(self) -> str:
    """Allocate next available card ID.

    Scans all lanes for existing T### IDs and returns max + 1.

    Returns:
      Next card ID (e.g., "T001", "T042")
    """
    return next_sequential_id([c.id for c in self.all_cards()], "T", separator="")

  def create_card(self, description: str, lane: str = "backlog") -> Card:
    """Create a new card from template.

    Args:
      description: Card description for the title
      lane: Target lane (backlog/doing/done), default backlog

    Returns:
      Created Card instance

    Raises:
      ValueError: If lane is invalid
    """
    if lane not in VALID_LANES:
      raise ValueError(
        f"Invalid lane: {lane}. Must be one of: {', '.join(sorted(VALID_LANES))}"
      )

    # Ensure template exists
    template_path = self.kanban_dir / "template.md"
    if not template_path.exists():
      self._create_default_template()

    # Allocate ID
    card_id = self.next_id()

    # Read template
    template_content = template_path.read_text()

    # Rewrite H1 and Created date
    card_content = self._rewrite_template(template_content, card_id, description)

    # Create card file
    slug = slugify(description)[:40]
    card_filename = f"{card_id}-{slug}.md"
    lane_dir = self.kanban_dir / lane
    lane_dir.mkdir(parents=True, exist_ok=True)
    card_path = lane_dir / card_filename

    card_path.write_text(card_content)

    return Card.from_file(card_path)

  def resolve_card(self, card_id: str, anywhere: bool = False) -> Card:
    """Resolve card ID to Card instance.

    Args:
      card_id: Card ID (e.g., "T123")
      anywhere: Search entire repo instead of just kanban/

    Returns:
      Resolved Card instance

    Raises:
      FileNotFoundError: If card not found
      ValueError: If multiple cards match (ambiguous)
    """
    search_root = self.root if anywhere else self.kanban_dir

    if not search_root.exists():
      raise FileNotFoundError(f"Card {card_id} not found (search root doesn't exist)")

    # Find all matching cards
    pattern = f"{card_id}-*.md"
    matches = list(search_root.rglob(pattern))

    if not matches:
      raise FileNotFoundError(
        f"Card {card_id} not found in {'repo' if anywhere else 'kanban/'}"
      )

    if len(matches) > 1:
      candidates = "\n".join(f"  - {m}" for m in matches)
      raise ValueError(
        f"Ambiguous card ID {card_id}. Multiple candidates found:\n{candidates}"
      )

    return Card.from_file(matches[0])

  def resolve_path(self, card_id: str, anywhere: bool = False) -> str:
    """Resolve card ID to path string (for -q flag).

    Args:
      card_id: Card ID (e.g., "T123")
      anywhere: Search entire repo instead of just kanban/

    Returns:
      Path string to card file
    """
    card = self.resolve_card(card_id, anywhere)
    return str(card.path)

  def _create_default_template(self) -> None:
    """Create default kanban/template.md if missing."""
    template_path = self.kanban_dir / "template.md"
    template_path.parent.mkdir(parents=True, exist_ok=True)
    package_template = get_package_templates_dir() / "kanban" / "template.md"
    template_path.write_text(package_template.read_text(encoding="utf-8"))

  @staticmethod
  def _rewrite_template(template: str, card_id: str, description: str) -> str:
    """Rewrite template with card ID and description.

    Only rewrites first H1 and Created date, preserves all other content.

    Args:
      template: Template content
      card_id: Card ID (e.g., "T001")
      description: Card description

    Returns:
      Rewritten card content
    """
    lines = template.split("\n")
    result = []
    h1_rewritten = False
    created_rewritten = False

    today = datetime.now().strftime("%Y-%m-%d")

    for line in lines:
      # Rewrite first H1
      if not h1_rewritten and line.startswith("# "):
        result.append(f"# {card_id}: {description}")
        h1_rewritten = True
        continue

      # Rewrite Created line
      if not created_rewritten and line.startswith("Created:"):
        result.append(f"Created: {today}")
        created_rewritten = True
        continue

      # Preserve all other lines
      result.append(line)

    return "\n".join(result)
