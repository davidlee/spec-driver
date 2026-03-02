"""Integration tests for memory CLI commands (create, list, show, find)."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import yaml
from typer.testing import CliRunner

from supekku.cli.create import app as create_app
from supekku.cli.find import app as find_app
from supekku.cli.list import app as list_app
from supekku.cli.show import app as show_app


def _write_memory_file(
  directory: Path,
  mem_id: str,
  name: str = "Test Memory",
  *,
  memory_type: str = "fact",
  status: str = "active",
  tags: list[str] | None = None,
  scope: dict | None = None,
  priority: dict | None = None,
  verified: str | None = None,
) -> Path:
  """Write a minimal valid memory file for testing."""
  fm: dict = {
    "id": mem_id,
    "name": name,
    "kind": "memory",
    "status": status,
    "memory_type": memory_type,
    "created": "2026-01-15",
    "updated": "2026-02-01",
    "tags": tags or [],
    "summary": "",
  }
  if scope:
    fm["scope"] = scope
  if priority:
    fm["priority"] = priority
  if verified:
    fm["verified"] = verified
  slug = name.lower().replace(" ", "_")
  path = directory / f"{mem_id}-{slug}.md"
  content = f"---\n{yaml.safe_dump(fm, sort_keys=False)}---\n\n# {name}\n"
  path.write_text(content, encoding="utf-8")
  return path


class CreateMemoryCommandTest(unittest.TestCase):
  """Test cases for create memory CLI command."""

  def setUp(self) -> None:
    self.runner = CliRunner()
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()

  def tearDown(self) -> None:
    self.tmpdir.cleanup()

  def test_create_memory(self) -> None:
    """Create memory writes file and prints ID."""
    result = self.runner.invoke(
      create_app,
      ["memory", "Test Fact", "--type", "fact", "--root", str(self.root)],
    )

    assert result.exit_code == 0, f"Failed: {result.stderr}"
    assert "Created memory: MEM-001" in result.stdout

    mem_dir = self.root / "memory"
    assert mem_dir.exists()
    files = list(mem_dir.glob("MEM-001-*.md"))
    assert len(files) == 1

    content = files[0].read_text(encoding="utf-8")
    assert "id: MEM-001" in content
    assert "memory_type: fact" in content
    assert "kind: memory" in content

  def test_create_memory_with_options(self) -> None:
    """Create memory respects --status, --tag, --summary."""
    result = self.runner.invoke(
      create_app,
      [
        "memory", "Arch Pattern",
        "--type", "pattern",
        "--status", "draft",
        "--tag", "arch",
        "--tag", "python",
        "--summary", "Key pattern",
        "--root", str(self.root),
      ],
    )

    assert result.exit_code == 0, f"Failed: {result.stderr}"
    assert "MEM-001" in result.stdout

    files = list((self.root / "memory").glob("MEM-001-*.md"))
    content = files[0].read_text(encoding="utf-8")
    assert "status: draft" in content
    assert "memory_type: pattern" in content
    assert "summary: Key pattern" in content

  def test_create_memory_increments_id(self) -> None:
    """Second create gets MEM-002."""
    mem_dir = self.root / "memory"
    mem_dir.mkdir(parents=True)
    _write_memory_file(mem_dir, "MEM-001")

    result = self.runner.invoke(
      create_app,
      ["memory", "Second", "--type", "concept", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "MEM-002" in result.stdout

  def test_create_memory_requires_type(self) -> None:
    """Missing --type should error."""
    result = self.runner.invoke(
      create_app,
      ["memory", "No Type", "--root", str(self.root)],
    )

    assert result.exit_code != 0


class ListMemoriesCommandTest(unittest.TestCase):
  """Test cases for list memories CLI command."""

  def setUp(self) -> None:
    self.runner = CliRunner()
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()
    self.mem_dir = self.root / "memory"
    self.mem_dir.mkdir()

  def tearDown(self) -> None:
    self.tmpdir.cleanup()

  def test_list_memories_empty(self) -> None:
    """Empty directory exits cleanly."""
    result = self.runner.invoke(
      list_app, ["memories", "--root", str(self.root)],
    )
    assert result.exit_code == 0

  def test_list_memories_table(self) -> None:
    """Table output includes record IDs and names."""
    _write_memory_file(self.mem_dir, "MEM-001", "First")
    _write_memory_file(self.mem_dir, "MEM-002", "Second")

    result = self.runner.invoke(
      list_app, ["memories", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "MEM-001" in result.stdout
    assert "MEM-002" in result.stdout

  def test_list_memories_json(self) -> None:
    """JSON output parses correctly."""
    _write_memory_file(self.mem_dir, "MEM-001", "JSON Test")

    result = self.runner.invoke(
      list_app, ["memories", "--json", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    assert len(parsed["items"]) == 1
    assert parsed["items"][0]["id"] == "MEM-001"

  def test_list_memories_filter_status(self) -> None:
    """--status filters records."""
    _write_memory_file(self.mem_dir, "MEM-001", "Active", status="active")
    _write_memory_file(self.mem_dir, "MEM-002", "Draft", status="draft")

    result = self.runner.invoke(
      list_app,
      ["memories", "--status", "draft", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "MEM-002" in result.stdout
    assert "MEM-001" not in result.stdout

  def test_list_memories_filter_type(self) -> None:
    """--type filters records."""
    _write_memory_file(
      self.mem_dir, "MEM-001", "Fact", memory_type="fact",
    )
    _write_memory_file(
      self.mem_dir, "MEM-002", "Pattern", memory_type="pattern",
    )

    result = self.runner.invoke(
      list_app,
      ["memories", "--type", "pattern", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "MEM-002" in result.stdout
    assert "MEM-001" not in result.stdout

  def test_list_memories_tsv(self) -> None:
    """TSV output contains tabs."""
    _write_memory_file(self.mem_dir, "MEM-001")

    result = self.runner.invoke(
      list_app,
      ["memories", "--format", "tsv", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "\t" in result.stdout
    assert "MEM-001" in result.stdout

  def test_list_memory_singular_alias(self) -> None:
    """Singular 'memory' alias works."""
    _write_memory_file(self.mem_dir, "MEM-001")

    result = self.runner.invoke(
      list_app, ["memory", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "MEM-001" in result.stdout


class ShowMemoryCommandTest(unittest.TestCase):
  """Test cases for show memory CLI command."""

  def setUp(self) -> None:
    self.runner = CliRunner()
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()
    self.mem_dir = self.root / "memory"
    self.mem_dir.mkdir()

  def tearDown(self) -> None:
    self.tmpdir.cleanup()

  def test_show_memory_details(self) -> None:
    """Show memory displays record details."""
    _write_memory_file(self.mem_dir, "MEM-001", "Test Memory")

    result = self.runner.invoke(
      show_app, ["memory", "MEM-001", "--root", str(self.root)],
    )

    assert result.exit_code == 0, f"Failed: {result.stderr}"
    assert "MEM-001" in result.stdout
    assert "Test Memory" in result.stdout

  def test_show_memory_json(self) -> None:
    """Show memory --json outputs valid JSON."""
    _write_memory_file(self.mem_dir, "MEM-001", "JSON Record")

    result = self.runner.invoke(
      show_app,
      ["memory", "MEM-001", "--json", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    assert parsed["id"] == "MEM-001"

  def test_show_memory_path(self) -> None:
    """Show memory --path outputs file path."""
    path = _write_memory_file(self.mem_dir, "MEM-001")

    result = self.runner.invoke(
      show_app,
      ["memory", "MEM-001", "--path", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert str(path) in result.stdout

  def test_show_memory_raw(self) -> None:
    """Show memory --raw outputs raw file content."""
    _write_memory_file(self.mem_dir, "MEM-001", "Raw Test")

    result = self.runner.invoke(
      show_app,
      ["memory", "MEM-001", "--raw", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "# Raw Test" in result.stdout
    assert "id: MEM-001" in result.stdout

  def test_show_memory_not_found(self) -> None:
    """Show memory with bad ID errors."""
    result = self.runner.invoke(
      show_app,
      ["memory", "MEM-999", "--root", str(self.root)],
    )

    assert result.exit_code == 1
    assert "not found" in result.stderr.lower()

  def test_show_memory_numeric_shorthand(self) -> None:
    """Show memory '1' normalizes to MEM-001."""
    _write_memory_file(self.mem_dir, "MEM-001")

    result = self.runner.invoke(
      show_app, ["memory", "1", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "MEM-001" in result.stdout

  def test_show_memory_mutually_exclusive(self) -> None:
    """--json and --path are mutually exclusive."""
    _write_memory_file(self.mem_dir, "MEM-001")

    result = self.runner.invoke(
      show_app,
      ["memory", "MEM-001", "--json", "--path", "--root", str(self.root)],
    )

    assert result.exit_code == 1
    assert "mutually exclusive" in result.stderr.lower()


class FindMemoryCommandTest(unittest.TestCase):
  """Test cases for find memory CLI command."""

  def setUp(self) -> None:
    self.runner = CliRunner()
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()
    self.mem_dir = self.root / "memory"
    self.mem_dir.mkdir()

  def tearDown(self) -> None:
    self.tmpdir.cleanup()

  def test_find_memory_wildcard(self) -> None:
    """Find memory with MEM-* pattern."""
    _write_memory_file(self.mem_dir, "MEM-001", "First")
    _write_memory_file(self.mem_dir, "MEM-002", "Second")

    result = self.runner.invoke(
      find_app, ["memory", "MEM-*", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "MEM-001" in result.stdout
    assert "MEM-002" in result.stdout

  def test_find_memory_exact(self) -> None:
    """Find memory with exact ID."""
    _write_memory_file(self.mem_dir, "MEM-001")

    result = self.runner.invoke(
      find_app, ["memory", "MEM-001", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "MEM-001" in result.stdout

  def test_find_memory_numeric_shorthand(self) -> None:
    """Find memory with numeric shorthand."""
    _write_memory_file(self.mem_dir, "MEM-001")

    result = self.runner.invoke(
      find_app, ["memory", "1", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "MEM-001" in result.stdout

  def test_find_memory_no_match(self) -> None:
    """Find memory with no match exits cleanly."""
    result = self.runner.invoke(
      find_app, ["memory", "MEM-999", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert result.stdout.strip() == ""


class ListMemoriesSelectionTest(unittest.TestCase):
  """Integration tests for list memories selection/filtering options."""

  def setUp(self) -> None:
    self.runner = CliRunner()
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()
    self.mem_dir = self.root / "memory"
    self.mem_dir.mkdir()

  def tearDown(self) -> None:
    self.tmpdir.cleanup()

  # -- --path scope matching --

  def test_path_filters_by_scope(self) -> None:
    """--path returns only records whose scope.paths match."""
    _write_memory_file(
      self.mem_dir, "MEM-001", "Auth Pattern",
      scope={"paths": ["src/auth/"]},
    )
    _write_memory_file(
      self.mem_dir, "MEM-002", "DB Pattern",
      scope={"paths": ["src/db/models.py"]},
    )

    result = self.runner.invoke(
      list_app,
      ["memories", "--path", "src/auth/login.py",
       "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "MEM-001" in result.stdout
    assert "MEM-002" not in result.stdout

  def test_path_no_match_empty_output(self) -> None:
    """--path with no matching records exits cleanly."""
    _write_memory_file(
      self.mem_dir, "MEM-001", "Auth",
      scope={"paths": ["src/auth/"]},
    )

    result = self.runner.invoke(
      list_app,
      ["memories", "--path", "src/unrelated/foo.py",
       "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "MEM-001" not in result.stdout

  def test_path_repeatable(self) -> None:
    """Multiple --path flags are OR'd."""
    _write_memory_file(
      self.mem_dir, "MEM-001", "Auth",
      scope={"paths": ["src/auth/"]},
    )
    _write_memory_file(
      self.mem_dir, "MEM-002", "DB",
      scope={"paths": ["src/db/"]},
    )
    _write_memory_file(
      self.mem_dir, "MEM-003", "CLI",
      scope={"paths": ["src/cli/"]},
    )

    result = self.runner.invoke(
      list_app,
      ["memories",
       "--path", "src/auth/login.py",
       "--path", "src/db/conn.py",
       "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "MEM-001" in result.stdout
    assert "MEM-002" in result.stdout
    assert "MEM-003" not in result.stdout

  # -- --command scope matching --

  def test_command_filters_by_scope(self) -> None:
    """--command filters by token-prefix match on scope.commands."""
    _write_memory_file(
      self.mem_dir, "MEM-001", "Test Tips",
      scope={"commands": ["test"]},
    )
    _write_memory_file(
      self.mem_dir, "MEM-002", "Lint Tips",
      scope={"commands": ["lint"]},
    )

    result = self.runner.invoke(
      list_app,
      ["memories", "--command", "test auth --verbose",
       "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "MEM-001" in result.stdout
    assert "MEM-002" not in result.stdout

  # -- --match-tag scope matching --

  def test_match_tag_filters_by_tag_intersection(self) -> None:
    """--match-tag filters records whose tags overlap."""
    _write_memory_file(
      self.mem_dir, "MEM-001", "Auth",
      tags=["auth", "security"],
    )
    _write_memory_file(
      self.mem_dir, "MEM-002", "DB",
      tags=["database"],
    )

    result = self.runner.invoke(
      list_app,
      ["memories", "--match-tag", "auth",
       "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "MEM-001" in result.stdout
    assert "MEM-002" not in result.stdout

  def test_match_tag_repeatable(self) -> None:
    """Multiple --match-tag flags are OR'd."""
    _write_memory_file(
      self.mem_dir, "MEM-001", "Auth",
      tags=["auth"],
    )
    _write_memory_file(
      self.mem_dir, "MEM-002", "DB",
      tags=["database"],
    )
    _write_memory_file(
      self.mem_dir, "MEM-003", "CLI",
      tags=["cli"],
    )

    result = self.runner.invoke(
      list_app,
      ["memories",
       "--match-tag", "auth",
       "--match-tag", "database",
       "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "MEM-001" in result.stdout
    assert "MEM-002" in result.stdout
    assert "MEM-003" not in result.stdout

  # -- --include-draft --

  def test_draft_excluded_by_default(self) -> None:
    """Draft records are excluded without --include-draft."""
    _write_memory_file(
      self.mem_dir, "MEM-001", "Active", status="active",
    )
    _write_memory_file(
      self.mem_dir, "MEM-002", "Draft", status="draft",
    )

    result = self.runner.invoke(
      list_app,
      ["memories", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "MEM-001" in result.stdout
    assert "MEM-002" not in result.stdout

  def test_include_draft_shows_drafts(self) -> None:
    """--include-draft surfaces draft records."""
    _write_memory_file(
      self.mem_dir, "MEM-001", "Active", status="active",
    )
    _write_memory_file(
      self.mem_dir, "MEM-002", "Draft", status="draft",
    )

    result = self.runner.invoke(
      list_app,
      ["memories", "--include-draft", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "MEM-001" in result.stdout
    assert "MEM-002" in result.stdout

  # -- --limit --

  def test_limit_caps_output(self) -> None:
    """--limit restricts the number of results."""
    for i in range(1, 6):
      _write_memory_file(
        self.mem_dir, f"MEM-{i:03d}", f"Mem {i}",
      )

    result = self.runner.invoke(
      list_app,
      ["memories", "--limit", "2", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    # Count non-empty, non-header lines containing MEM-
    mem_lines = [
      ln for ln in result.stdout.splitlines() if "MEM-" in ln
    ]
    assert len(mem_lines) == 2

  # -- deprecated excluded by default --

  def test_deprecated_excluded_by_default(self) -> None:
    """Deprecated records are excluded without explicit --status."""
    _write_memory_file(
      self.mem_dir, "MEM-001", "Active", status="active",
    )
    _write_memory_file(
      self.mem_dir, "MEM-002", "Old", status="deprecated",
    )

    result = self.runner.invoke(
      list_app,
      ["memories", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "MEM-001" in result.stdout
    assert "MEM-002" not in result.stdout

  def test_explicit_status_bypasses_exclusion(self) -> None:
    """--status deprecated shows deprecated records (skip_status_filter)."""
    _write_memory_file(
      self.mem_dir, "MEM-001", "Active", status="active",
    )
    _write_memory_file(
      self.mem_dir, "MEM-002", "Old", status="deprecated",
    )

    result = self.runner.invoke(
      list_app,
      ["memories", "--status", "deprecated",
       "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "MEM-002" in result.stdout
    assert "MEM-001" not in result.stdout

  # -- deterministic ordering --

  def test_ordering_by_severity(self) -> None:
    """Records ordered by severity (critical before low)."""
    _write_memory_file(
      self.mem_dir, "MEM-001", "Low Sev",
      priority={"severity": "low", "weight": 0},
    )
    _write_memory_file(
      self.mem_dir, "MEM-002", "Critical Sev",
      priority={"severity": "critical", "weight": 0},
    )

    result = self.runner.invoke(
      list_app,
      ["memories", "--format", "tsv", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    lines = [ln for ln in result.stdout.splitlines() if "MEM-" in ln]
    assert len(lines) == 2
    assert lines[0].startswith("MEM-002"), (
      f"Critical should come first, got: {lines}"
    )
    assert lines[1].startswith("MEM-001")

  # -- combined scope + metadata filter --

  def test_path_combined_with_type_filter(self) -> None:
    """--path and --type both apply (AND between metadata and scope)."""
    _write_memory_file(
      self.mem_dir, "MEM-001", "Auth Fact",
      memory_type="fact",
      scope={"paths": ["src/auth/"]},
    )
    _write_memory_file(
      self.mem_dir, "MEM-002", "Auth Pattern",
      memory_type="pattern",
      scope={"paths": ["src/auth/"]},
    )

    result = self.runner.invoke(
      list_app,
      ["memories",
       "--type", "fact",
       "--path", "src/auth/login.py",
       "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "MEM-001" in result.stdout
    assert "MEM-002" not in result.stdout


if __name__ == "__main__":
  unittest.main()
