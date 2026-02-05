"""Card model for kanban board management."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Card:
  """Card model representing a kanban card with T### ID."""

  id: str
  title: str
  lane: str | None
  path: Path
  created: str | None

  @classmethod
  def from_file(cls, card_path: Path) -> Card:
    """Parse card from markdown file.

    Args:
      card_path: Path to card markdown file

    Returns:
      Card instance with parsed metadata

    Raises:
      ValueError: If ID cannot be parsed from filename
    """
    # Parse ID from filename (T###-description.md)
    card_id = cls._parse_id_from_filename(card_path)

    # Parse lane from path
    lane = cls._detect_lane_from_path(card_path)

    # Parse content
    content = card_path.read_text()
    title = cls._parse_title_from_content(content, card_id)
    created = cls._parse_created_from_content(content)

    return cls(
      id=card_id,
      title=title,
      lane=lane,
      path=card_path,
      created=created,
    )

  @staticmethod
  def _parse_id_from_filename(card_path: Path) -> str:
    """Extract T### ID from filename."""
    match = re.match(r"^(T\d+)", card_path.stem)
    if not match:
      raise ValueError(f"Cannot parse card ID from filename: {card_path.name}")
    return match.group(1)

  @staticmethod
  def _detect_lane_from_path(card_path: Path) -> str | None:
    """Detect lane from path (kanban/doing/T123.md -> 'doing')."""
    parts = card_path.parts
    try:
      kanban_idx = parts.index("kanban")
      if kanban_idx + 1 < len(parts):
        return parts[kanban_idx + 1]
    except ValueError:
      pass
    return None

  @staticmethod
  def _parse_title_from_content(content: str, card_id: str) -> str:
    """Parse title from first H1 (# T###: Title)."""
    for line in content.split("\n"):
      if line.startswith("# "):
        # Extract title after "T###: "
        match = re.match(rf"^#\s+{re.escape(card_id)}:\s*(.+)$", line)
        if match:
          return match.group(1).strip()
        # Fallback: just remove the "# " prefix
        return line[2:].strip()
    return "Untitled"

  @staticmethod
  def _parse_created_from_content(content: str) -> str | None:
    """Parse Created: YYYY-MM-DD date from content."""
    for line in content.split("\n"):
      match = re.match(r"^Created:\s*(\d{4}-\d{2}-\d{2})\s*$", line)
      if match:
        return match.group(1)
    return None

  def to_dict(self) -> dict:
    """Convert card to dictionary for JSON serialization."""
    return {
      "id": self.id,
      "title": self.title,
      "lane": self.lane,
      "path": str(self.path),
      "created": self.created,
    }
