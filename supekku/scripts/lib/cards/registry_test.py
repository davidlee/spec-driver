"""Tests for card registry and models.

VT-021-001: ID parsing + lane detection + ambiguity rules
VT-021-002: next-ID allocation scans all lanes
VT-021-003: create card copies template and rewrites only H1/Created
VT-021-004: show card -q path-only behaviour and errors
"""

from __future__ import annotations

import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from textwrap import dedent

from supekku.scripts.lib.cards import Card, CardRegistry


class TestCardModel(unittest.TestCase):
  """VT-021-001: ID parsing and lane detection."""

  def setUp(self) -> None:
    """Create temporary directory for tests."""
    self._cwd = Path.cwd()
    self._tmpdir = tempfile.TemporaryDirectory()
    self.tmp_path = Path(self._tmpdir.name)

  def tearDown(self) -> None:
    """Clean up temporary directory."""
    os.chdir(self._cwd)
    self._tmpdir.cleanup()

  def test_parse_id_from_filename(self) -> None:
    """Parse card ID from filename T123-description.md."""
    card_path = self.tmp_path / "kanban" / "backlog" / "T123-fix-bug.md"
    card_path.parent.mkdir(parents=True)
    card_path.write_text("# T123: Fix bug\n\nCreated: 2026-02-03\n")

    card = Card.from_file(card_path)

    self.assertEqual(card.id, "T123")
    self.assertEqual(card.path, card_path)

  def test_detect_lane_from_path(self) -> None:
    """Detect lane from path kanban/doing/T123.md -> 'doing'."""
    card_path = self.tmp_path / "kanban" / "doing" / "T456-task.md"
    card_path.parent.mkdir(parents=True)
    card_path.write_text("# T456: Task\n\nCreated: 2026-02-03\n")

    card = Card.from_file(card_path)

    self.assertEqual(card.lane, "doing")

  def test_handle_missing_lane(self) -> None:
    """Handle missing lane (no kanban/ in path) -> None."""
    card_path = self.tmp_path / "other" / "T789-card.md"
    card_path.parent.mkdir(parents=True)
    card_path.write_text("# T789: Card\n\nCreated: 2026-02-03\n")

    card = Card.from_file(card_path)

    self.assertIsNone(card.lane)

  def test_parse_title_from_h1(self) -> None:
    """Parse title from first H1."""
    card_path = self.tmp_path / "kanban" / "backlog" / "T100-title-test.md"
    card_path.parent.mkdir(parents=True)
    card_path.write_text("# T100: This is the title\n\nCreated: 2026-02-03\n")

    card = Card.from_file(card_path)

    self.assertEqual(card.title, "This is the title")

  def test_parse_created_date(self) -> None:
    """Parse Created date from card content."""
    card_path = self.tmp_path / "kanban" / "backlog" / "T200-date-test.md"
    card_path.parent.mkdir(parents=True)
    card_path.write_text("# T200: Date test\n\nCreated: 2026-02-03\n")

    card = Card.from_file(card_path)

    self.assertEqual(card.created, "2026-02-03")

  def test_handle_missing_created_date(self) -> None:
    """Handle missing Created date gracefully."""
    card_path = self.tmp_path / "kanban" / "backlog" / "T300-no-date.md"
    card_path.parent.mkdir(parents=True)
    card_path.write_text("# T300: No date\n\n## Content\n")

    card = Card.from_file(card_path)

    self.assertIsNone(card.created)


class TestCardDiscovery(unittest.TestCase):
  """VT-021-001: Discovery across lanes and ambiguity detection."""

  def setUp(self) -> None:
    """Create temporary directory for tests."""
    self._cwd = Path.cwd()
    self._tmpdir = tempfile.TemporaryDirectory()
    self.tmp_path = Path(self._tmpdir.name)

  def tearDown(self) -> None:
    """Clean up temporary directory."""
    os.chdir(self._cwd)
    self._tmpdir.cleanup()

  def test_discover_cards_across_lanes(self) -> None:
    """Discover cards across all lanes (backlog/doing/done)."""
    backlog = self.tmp_path / "kanban" / "backlog" / "T001-backlog-card.md"
    doing = self.tmp_path / "kanban" / "doing" / "T002-doing-card.md"
    done = self.tmp_path / "kanban" / "done" / "T003-done-card.md"

    for card_path in [backlog, doing, done]:
      card_path.parent.mkdir(parents=True, exist_ok=True)
      card_id = card_path.stem.split("-")[0]
      card_path.write_text(f"# {card_id}: Card\n\nCreated: 2026-02-03\n")

    registry = CardRegistry(self.tmp_path)
    cards = registry.all_cards()

    self.assertEqual(len(cards), 3)
    self.assertEqual({c.id for c in cards}, {"T001", "T002", "T003"})

  def test_handle_empty_kanban(self) -> None:
    """Return empty list when no cards found."""
    kanban_dir = self.tmp_path / "kanban"
    kanban_dir.mkdir()

    registry = CardRegistry(self.tmp_path)
    cards = registry.all_cards()

    self.assertEqual(cards, [])

  def test_filter_by_lane(self) -> None:
    """Filter cards by lane."""
    backlog = self.tmp_path / "kanban" / "backlog" / "T001-card.md"
    doing = self.tmp_path / "kanban" / "doing" / "T002-card.md"

    for card_path in [backlog, doing]:
      card_path.parent.mkdir(parents=True, exist_ok=True)
      card_id = card_path.stem.split("-")[0]
      card_path.write_text(f"# {card_id}: Card\n\nCreated: 2026-02-03\n")

    registry = CardRegistry(self.tmp_path)
    doing_cards = registry.cards_by_lane("doing")

    self.assertEqual(len(doing_cards), 1)
    self.assertEqual(doing_cards[0].id, "T002")


class TestNextIdAllocation(unittest.TestCase):
  """VT-021-002: Next-ID allocation scans all lanes."""

  def setUp(self) -> None:
    """Create temporary directory for tests."""
    self._cwd = Path.cwd()
    self._tmpdir = tempfile.TemporaryDirectory()
    self.tmp_path = Path(self._tmpdir.name)

  def tearDown(self) -> None:
    """Clean up temporary directory."""
    os.chdir(self._cwd)
    self._tmpdir.cleanup()

  def test_empty_kanban_returns_t001(self) -> None:
    """Empty kanban -> T001."""
    kanban_dir = self.tmp_path / "kanban"
    kanban_dir.mkdir()

    registry = CardRegistry(self.tmp_path)
    next_id = registry.next_id()

    self.assertEqual(next_id, "T001")

  def test_existing_cards_returns_max_plus_one(self) -> None:
    """Existing T001, T002 -> T003."""
    for card_num in [1, 2]:
      card_path = self.tmp_path / "kanban" / "backlog" / f"T{card_num:03d}-card.md"
      card_path.parent.mkdir(parents=True, exist_ok=True)
      card_path.write_text(f"# T{card_num:03d}: Card\n\nCreated: 2026-02-03\n")

    registry = CardRegistry(self.tmp_path)
    next_id = registry.next_id()

    self.assertEqual(next_id, "T003")

  def test_gaps_in_sequence(self) -> None:
    """Gaps in sequence (T001, T005) -> T006."""
    for card_num in [1, 5]:
      card_path = self.tmp_path / "kanban" / "backlog" / f"T{card_num:03d}-card.md"
      card_path.parent.mkdir(parents=True, exist_ok=True)
      card_path.write_text(f"# T{card_num:03d}: Card\n\nCreated: 2026-02-03\n")

    registry = CardRegistry(self.tmp_path)
    next_id = registry.next_id()

    self.assertEqual(next_id, "T006")

  def test_scans_all_lanes(self) -> None:
    """Scan all lanes, not just backlog."""
    backlog = self.tmp_path / "kanban" / "backlog" / "T001-card.md"
    doing = self.tmp_path / "kanban" / "doing" / "T005-card.md"
    done = self.tmp_path / "kanban" / "done" / "T003-card.md"

    for card_path in [backlog, doing, done]:
      card_path.parent.mkdir(parents=True, exist_ok=True)
      card_id = card_path.stem.split("-")[0]
      card_path.write_text(f"# {card_id}: Card\n\nCreated: 2026-02-03\n")

    registry = CardRegistry(self.tmp_path)
    next_id = registry.next_id()

    self.assertEqual(next_id, "T006")  # Max is T005


class TestCardCreation(unittest.TestCase):
  """VT-021-003: Card creation with template preservation."""

  def setUp(self) -> None:
    """Create temporary directory for tests."""
    self._cwd = Path.cwd()
    self._tmpdir = tempfile.TemporaryDirectory()
    self.tmp_path = Path(self._tmpdir.name)

  def tearDown(self) -> None:
    """Clean up temporary directory."""
    os.chdir(self._cwd)
    self._tmpdir.cleanup()

  def test_create_card_with_description(self) -> None:
    """Create card rewrites first H1 to # T###: description."""
    template = self.tmp_path / "kanban" / "template.md"
    template.parent.mkdir(parents=True)
    template.write_text(
      dedent("""
      # T000: Placeholder

      Created:

      ## Description

      Template content here.

      ## Notes
    """).strip()
    )

    registry = CardRegistry(self.tmp_path)
    card = registry.create_card("Fix the bug", lane="backlog")

    self.assertEqual(card.id, "T001")
    self.assertEqual(card.title, "Fix the bug")
    content = card.path.read_text()
    self.assertIn("# T001: Fix the bug", content)
    self.assertIn("Template content here.", content)

  def test_inserts_created_date(self) -> None:
    """Inserts/updates Created: YYYY-MM-DD line."""
    template = self.tmp_path / "kanban" / "template.md"
    template.parent.mkdir(parents=True)
    template.write_text("# T000: Placeholder\n\nCreated:\n\n## Content\n")

    registry = CardRegistry(self.tmp_path)
    card = registry.create_card("Test task")

    content = card.path.read_text()
    today = datetime.now().strftime("%Y-%m-%d")
    self.assertIn(f"Created: {today}", content)

  def test_preserves_template_content(self) -> None:
    """Preserves all other template content verbatim."""
    template = self.tmp_path / "kanban" / "template.md"
    template.parent.mkdir(parents=True)
    template_content = dedent("""
      # T000: Placeholder

      Created:

      ## Description

      This is important template content.
      It should not be modified.

      ## Notes

      - Keep this
      - And this
    """).strip()
    template.write_text(template_content)

    registry = CardRegistry(self.tmp_path)
    card = registry.create_card("New card")

    content = card.path.read_text()
    self.assertIn("This is important template content.", content)
    self.assertIn("It should not be modified.", content)
    self.assertIn("- Keep this", content)
    self.assertIn("- And this", content)

  def test_auto_creates_template_if_missing(self) -> None:
    """Auto-creates kanban/template.md if missing."""
    kanban_dir = self.tmp_path / "kanban"
    kanban_dir.mkdir()

    registry = CardRegistry(self.tmp_path)
    card = registry.create_card("First card")

    template = self.tmp_path / "kanban" / "template.md"
    self.assertTrue(template.exists())
    self.assertTrue(card.path.exists())

  def test_respects_lane_flag(self) -> None:
    """Respects --lane flag (backlog/doing/done, default backlog)."""
    template = self.tmp_path / "kanban" / "template.md"
    template.parent.mkdir(parents=True)
    template.write_text("# T000: Placeholder\n\nCreated:\n")

    registry = CardRegistry(self.tmp_path)

    backlog_card = registry.create_card("Backlog task", lane="backlog")
    doing_card = registry.create_card("Doing task", lane="doing")
    done_card = registry.create_card("Done task", lane="done")

    self.assertIn("backlog", str(backlog_card.path))
    self.assertIn("doing", str(doing_card.path))
    self.assertIn("done", str(done_card.path))

  def test_default_lane_is_backlog(self) -> None:
    """Default lane is backlog when not specified."""
    template = self.tmp_path / "kanban" / "template.md"
    template.parent.mkdir(parents=True)
    template.write_text("# T000: Placeholder\n\nCreated:\n")

    registry = CardRegistry(self.tmp_path)
    card = registry.create_card("Default lane test")

    self.assertIn("backlog", str(card.path))

  def test_validates_lane_exists(self) -> None:
    """Validates lane exists or errors clearly."""
    template = self.tmp_path / "kanban" / "template.md"
    template.parent.mkdir(parents=True)
    template.write_text("# T000: Placeholder\n\nCreated:\n")

    registry = CardRegistry(self.tmp_path)

    with self.assertRaisesRegex(ValueError, "Invalid lane"):
      registry.create_card("Test", lane="invalid")


class TestCardResolution(unittest.TestCase):
  """VT-021-004: Card resolution and ambiguity handling."""

  def setUp(self) -> None:
    """Create temporary directory for tests."""
    self._cwd = Path.cwd()
    self._tmpdir = tempfile.TemporaryDirectory()
    self.tmp_path = Path(self._tmpdir.name)

  def tearDown(self) -> None:
    """Clean up temporary directory."""
    os.chdir(self._cwd)
    self._tmpdir.cleanup()

  def test_unambiguous_match_returns_card(self) -> None:
    """Unambiguous match returns single Card."""
    card_path = self.tmp_path / "kanban" / "backlog" / "T123-unique.md"
    card_path.parent.mkdir(parents=True)
    card_path.write_text("# T123: Unique\n\nCreated: 2026-02-03\n")

    registry = CardRegistry(self.tmp_path)
    card = registry.resolve_card("T123")

    self.assertEqual(card.id, "T123")
    self.assertEqual(card.path, card_path)

  def test_no_match_raises_error(self) -> None:
    """No match raises error with clear message."""
    kanban_dir = self.tmp_path / "kanban"
    kanban_dir.mkdir()

    registry = CardRegistry(self.tmp_path)

    with self.assertRaisesRegex(FileNotFoundError, "Card T999 not found"):
      registry.resolve_card("T999")

  def test_multiple_matches_raises_ambiguity_error(self) -> None:
    """Multiple matches raise error listing candidates."""
    card1 = self.tmp_path / "kanban" / "backlog" / "T123-first.md"
    card2 = self.tmp_path / "kanban" / "doing" / "T123-second.md"

    for card_path in [card1, card2]:
      card_path.parent.mkdir(parents=True, exist_ok=True)
      card_path.write_text("# T123: Card\n\nCreated: 2026-02-03\n")

    registry = CardRegistry(self.tmp_path)

    with self.assertRaisesRegex(ValueError, "Ambiguous.*T123.*candidates"):
      registry.resolve_card("T123")

  def test_anywhere_flag_expands_search(self) -> None:
    """--anywhere flag expands search beyond kanban/."""
    card_path = self.tmp_path / "other" / "location" / "T456-elsewhere.md"
    card_path.parent.mkdir(parents=True)
    card_path.write_text("# T456: Elsewhere\n\nCreated: 2026-02-03\n")

    registry = CardRegistry(self.tmp_path)
    card = registry.resolve_card("T456", anywhere=True)

    self.assertEqual(card.id, "T456")
    self.assertEqual(card.path, card_path)

  def test_resolve_path_only(self) -> None:
    """resolve_path returns only path string for -q flag."""
    card_path = self.tmp_path / "kanban" / "backlog" / "T789-path-test.md"
    card_path.parent.mkdir(parents=True)
    card_path.write_text("# T789: Path test\n\nCreated: 2026-02-03\n")

    registry = CardRegistry(self.tmp_path)
    path = registry.resolve_path("T789")

    self.assertEqual(path, str(card_path))
