"""Tests for compact CLI command."""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import yaml
from typer.testing import CliRunner

from supekku.cli.main import app

runner = CliRunner()

# Minimal delta frontmatter with empty defaults (compactable)
BLOATED_DELTA = {
  "id": "DE-900",
  "name": "Test Delta",
  "slug": "test-delta",
  "kind": "delta",
  "status": "draft",
  "created": "2026-03-03",
  "updated": "2026-03-03",
  "relations": [],
  "applies_to": {"specs": [], "requirements": []},
  "owners": [],
  "tags": [],
}

# Already minimal — nothing to compact
MINIMAL_DELTA = {
  "id": "DE-901",
  "name": "Minimal Delta",
  "slug": "minimal-delta",
  "kind": "delta",
  "status": "draft",
  "created": "2026-03-03",
  "updated": "2026-03-03",
}


def _write_delta(root: Path, frontmatter: dict, body: str = "# Test\n") -> Path:
  """Write a delta file in the expected directory structure."""
  delta_id = frontmatter["id"]
  slug = frontmatter.get("slug", "test")
  delta_dir = root / "change" / "deltas" / f"{delta_id}-{slug}"
  delta_dir.mkdir(parents=True, exist_ok=True)
  delta_file = delta_dir / f"{delta_id}.md"
  fm_yaml = yaml.safe_dump(frontmatter, sort_keys=False)
  delta_file.write_text(f"---\n{fm_yaml}---\n\n{body}", encoding="utf-8")
  return delta_file


def _root_flag(root: Path) -> list[str]:
  return ["--root", str(root)]


class TestCompactDelta(unittest.TestCase):
  """Tests for `spec-driver compact delta`."""

  def setUp(self) -> None:
    self._tmpdir = TemporaryDirectory()
    self.root = Path(self._tmpdir.name)
    (self.root / ".spec-driver").mkdir()

  def tearDown(self) -> None:
    self._tmpdir.cleanup()

  def test_dry_run_shows_changes(self) -> None:
    _write_delta(self.root, BLOATED_DELTA)
    result = runner.invoke(
      app,
      ["compact", "delta", "--dry-run", *_root_flag(self.root)],
    )
    self.assertEqual(result.exit_code, 0, result.output)
    self.assertIn("DE-900", result.output)
    self.assertIn("dry run", result.output.lower())

  def test_dry_run_does_not_modify_files(self) -> None:
    delta_file = _write_delta(self.root, BLOATED_DELTA)
    original = delta_file.read_text()
    runner.invoke(
      app,
      ["compact", "delta", "--dry-run", *_root_flag(self.root)],
    )
    self.assertEqual(delta_file.read_text(), original)

  def test_compact_removes_empty_defaults(self) -> None:
    delta_file = _write_delta(self.root, BLOATED_DELTA)
    result = runner.invoke(
      app,
      ["compact", "delta", *_root_flag(self.root)],
    )
    self.assertEqual(result.exit_code, 0, result.output)
    self.assertIn("DE-900", result.output)

    text = delta_file.read_text()
    data = yaml.safe_load(text.split("---")[1])
    self.assertNotIn("relations", data)
    self.assertNotIn("applies_to", data)
    self.assertNotIn("owners", data)
    self.assertNotIn("tags", data)
    self.assertEqual(data["id"], "DE-900")
    self.assertEqual(data["kind"], "delta")

  def test_compact_preserves_body(self) -> None:
    body = "# Delta Description\n\nSome content here.\n"
    delta_file = _write_delta(self.root, BLOATED_DELTA, body=body)
    runner.invoke(
      app,
      ["compact", "delta", *_root_flag(self.root)],
    )
    text = delta_file.read_text()
    self.assertIn("Some content here.", text)

  def test_no_changes_needed(self) -> None:
    _write_delta(self.root, MINIMAL_DELTA)
    result = runner.invoke(
      app,
      ["compact", "delta", *_root_flag(self.root)],
    )
    self.assertEqual(result.exit_code, 0, result.output)
    self.assertIn("No deltas needed compaction", result.output)

  def test_specific_delta_id(self) -> None:
    _write_delta(self.root, BLOATED_DELTA)
    _write_delta(self.root, MINIMAL_DELTA)
    result = runner.invoke(
      app,
      ["compact", "delta", "DE-900", *_root_flag(self.root)],
    )
    self.assertEqual(result.exit_code, 0, result.output)
    self.assertIn("DE-900", result.output)
    self.assertNotIn("DE-901", result.output)

  def test_unknown_delta_id_fails(self) -> None:
    _write_delta(self.root, BLOATED_DELTA)
    result = runner.invoke(
      app,
      ["compact", "delta", "DE-999", *_root_flag(self.root)],
    )
    self.assertNotEqual(result.exit_code, 0)
    self.assertIn("not found", result.output.lower())


if __name__ == "__main__":
  unittest.main()
