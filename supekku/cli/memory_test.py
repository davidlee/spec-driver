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
  path = directory / f"{mem_id}.md"
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
      [
        "memory",
        "mem.fact.test",
        "--name",
        "Test Fact",
        "--type",
        "fact",
        "--root",
        str(self.root),
      ],
    )

    assert result.exit_code == 0, f"Failed: {result.stderr}"
    assert "Created memory: mem.fact.test" in result.stdout

    mem_dir = self.root / "memory"
    assert mem_dir.exists()
    path = mem_dir / "mem.fact.test.md"
    assert path.exists()

    content = path.read_text(encoding="utf-8")
    assert "id: mem.fact.test" in content
    assert "memory_type: fact" in content
    assert "kind: memory" in content

  def test_create_memory_with_options(self) -> None:
    """Create memory respects --status, --tag, --summary."""
    result = self.runner.invoke(
      create_app,
      [
        "memory",
        "mem.pattern.arch.registry",
        "--name",
        "Arch Pattern",
        "--type",
        "pattern",
        "--status",
        "draft",
        "--tag",
        "arch",
        "--tag",
        "python",
        "--summary",
        "Key pattern",
        "--root",
        str(self.root),
      ],
    )

    assert result.exit_code == 0, f"Failed: {result.stderr}"
    assert "mem.pattern.arch.registry" in result.stdout

    path = self.root / "memory" / "mem.pattern.arch.registry.md"
    content = path.read_text(encoding="utf-8")
    assert "status: draft" in content
    assert "memory_type: pattern" in content
    assert "summary: Key pattern" in content

  def test_create_memory_rejects_duplicate(self) -> None:
    """Creating a memory with an existing ID fails."""
    mem_dir = self.root / "memory"
    mem_dir.mkdir(parents=True)
    _write_memory_file(mem_dir, "mem.fact.alpha")

    result = self.runner.invoke(
      create_app,
      [
        "memory",
        "mem.fact.alpha",
        "--name",
        "Duplicate",
        "--type",
        "fact",
        "--root",
        str(self.root),
      ],
    )

    assert result.exit_code != 0

  def test_create_memory_requires_type(self) -> None:
    """Missing --type should error."""
    result = self.runner.invoke(
      create_app,
      [
        "memory",
        "mem.fact.test",
        "--name",
        "No Type",
        "--root",
        str(self.root),
      ],
    )

    assert result.exit_code != 0

  def test_create_memory_shorthand_id(self) -> None:
    """Shorthand ID (without mem. prefix) is normalized."""
    result = self.runner.invoke(
      create_app,
      [
        "memory",
        "fact.shorthand",
        "--name",
        "Shorthand",
        "--type",
        "fact",
        "--root",
        str(self.root),
      ],
    )

    assert result.exit_code == 0
    assert "mem.fact.shorthand" in result.stdout


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
      list_app,
      ["memories", "--root", str(self.root)],
    )
    assert result.exit_code == 0

  def test_list_memories_table(self) -> None:
    """Table output includes record IDs and names."""
    _write_memory_file(self.mem_dir, "mem.fact.alpha", "First")
    _write_memory_file(self.mem_dir, "mem.fact.beta", "Second")

    result = self.runner.invoke(
      list_app,
      ["memories", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "mem.fact.alpha" in result.stdout
    assert "mem.fact.beta" in result.stdout

  def test_list_memories_json(self) -> None:
    """JSON output parses correctly."""
    _write_memory_file(self.mem_dir, "mem.fact.alpha", "JSON Test")

    result = self.runner.invoke(
      list_app,
      ["memories", "--json", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    assert len(parsed["items"]) == 1
    assert parsed["items"][0]["id"] == "mem.fact.alpha"

  def test_list_memories_filter_status(self) -> None:
    """--status filters records."""
    _write_memory_file(self.mem_dir, "mem.fact.alpha", "Active", status="active")
    _write_memory_file(self.mem_dir, "mem.fact.beta", "Draft", status="draft")

    result = self.runner.invoke(
      list_app,
      ["memories", "--status", "draft", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "mem.fact.beta" in result.stdout
    assert "mem.fact.alpha" not in result.stdout

  def test_list_memories_filter_type(self) -> None:
    """--type filters records."""
    _write_memory_file(
      self.mem_dir,
      "mem.fact.alpha",
      "Fact",
      memory_type="fact",
    )
    _write_memory_file(
      self.mem_dir,
      "mem.fact.beta",
      "Pattern",
      memory_type="pattern",
    )

    result = self.runner.invoke(
      list_app,
      ["memories", "--type", "pattern", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "mem.fact.beta" in result.stdout
    assert "mem.fact.alpha" not in result.stdout

  def test_list_memories_tsv(self) -> None:
    """TSV output contains tabs."""
    _write_memory_file(self.mem_dir, "mem.fact.alpha")

    result = self.runner.invoke(
      list_app,
      ["memories", "--format", "tsv", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "\t" in result.stdout
    assert "mem.fact.alpha" in result.stdout

  def test_list_memory_singular_alias(self) -> None:
    """Singular 'memory' alias works."""
    _write_memory_file(self.mem_dir, "mem.fact.alpha")

    result = self.runner.invoke(
      list_app,
      ["memory", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "mem.fact.alpha" in result.stdout


class ListMemoriesLinksToTest(unittest.TestCase):
  """Integration tests for list memories --links-to."""

  def setUp(self) -> None:
    self.runner = CliRunner()
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()
    self.mem_dir = self.root / "memory"
    self.mem_dir.mkdir()

  def tearDown(self) -> None:
    self.tmpdir.cleanup()

  def _write_memory_with_body(
    self,
    mem_id: str,
    name: str,
    body: str,
    *,
    status: str = "active",
  ) -> Path:
    """Write a memory file with custom body content."""
    fm = {
      "id": mem_id,
      "name": name,
      "kind": "memory",
      "status": status,
      "memory_type": "fact",
      "created": "2026-01-15",
      "updated": "2026-02-01",
      "tags": [],
      "summary": "",
    }
    path = self.mem_dir / f"{mem_id}.md"
    content = f"---\n{yaml.safe_dump(fm, sort_keys=False)}---\n\n{body}\n"
    path.write_text(content, encoding="utf-8")
    return path

  def test_links_to_returns_backlinkers(self) -> None:
    """--links-to shows memories that link to the target."""
    self._write_memory_with_body(
      "mem.fact.hub", "Hub", "The hub memory."
    )
    self._write_memory_with_body(
      "mem.fact.alpha", "Alpha", "See [[mem.fact.hub]] for details."
    )
    self._write_memory_with_body(
      "mem.fact.beta", "Beta", "Unrelated content."
    )

    result = self.runner.invoke(
      list_app,
      ["memories", "--links-to", "mem.fact.hub", "--root", str(self.root)],
    )

    assert result.exit_code == 0, f"Failed: {result.output}"
    assert "mem.fact.alpha" in result.stdout
    assert "mem.fact.beta" not in result.stdout

  def test_links_to_no_backlinks(self) -> None:
    """--links-to with no backlinks exits cleanly."""
    self._write_memory_with_body(
      "mem.fact.lonely", "Lonely", "Nobody links to me."
    )

    result = self.runner.invoke(
      list_app,
      ["memories", "--links-to", "mem.fact.lonely", "--root", str(self.root)],
    )

    assert result.exit_code == 0

  def test_links_to_multiple_backlinkers(self) -> None:
    """--links-to returns all memories that link to the target."""
    self._write_memory_with_body(
      "mem.fact.hub", "Hub", "Central node."
    )
    self._write_memory_with_body(
      "mem.fact.a", "A", "See [[mem.fact.hub]]."
    )
    self._write_memory_with_body(
      "mem.fact.b", "B", "Also see [[mem.fact.hub]]."
    )
    self._write_memory_with_body(
      "mem.fact.c", "C", "And [[mem.fact.hub]] too."
    )

    result = self.runner.invoke(
      list_app,
      ["memories", "--links-to", "mem.fact.hub", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "mem.fact.a" in result.stdout
    assert "mem.fact.b" in result.stdout
    assert "mem.fact.c" in result.stdout
    assert "mem.fact.hub" not in result.stdout

  def test_links_to_with_shorthand(self) -> None:
    """--links-to accepts shorthand IDs (without mem. prefix)."""
    self._write_memory_with_body(
      "mem.fact.hub", "Hub", "Central."
    )
    self._write_memory_with_body(
      "mem.fact.linker", "Linker", "See [[mem.fact.hub]]."
    )

    result = self.runner.invoke(
      list_app,
      ["memories", "--links-to", "fact.hub", "--root", str(self.root)],
    )

    assert result.exit_code == 0, f"Failed: {result.output}"
    assert "mem.fact.linker" in result.stdout

  def test_links_to_json_output(self) -> None:
    """--links-to works with --json output."""
    self._write_memory_with_body(
      "mem.fact.hub", "Hub", "Central."
    )
    self._write_memory_with_body(
      "mem.fact.alpha", "Alpha", "See [[mem.fact.hub]]."
    )

    result = self.runner.invoke(
      list_app,
      ["memories", "--links-to", "mem.fact.hub", "--json", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    ids = [item["id"] for item in parsed["items"]]
    assert "mem.fact.alpha" in ids


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
    _write_memory_file(self.mem_dir, "mem.fact.alpha", "Test Memory")

    result = self.runner.invoke(
      show_app,
      ["memory", "mem.fact.alpha", "--root", str(self.root)],
    )

    assert result.exit_code == 0, f"Failed: {result.stderr}"
    assert "mem.fact.alpha" in result.stdout
    assert "Test Memory" in result.stdout

  def test_show_memory_json(self) -> None:
    """Show memory --json outputs valid JSON."""
    _write_memory_file(self.mem_dir, "mem.fact.alpha", "JSON Record")

    result = self.runner.invoke(
      show_app,
      ["memory", "mem.fact.alpha", "--json", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    assert parsed["id"] == "mem.fact.alpha"

  def test_show_memory_path(self) -> None:
    """Show memory --path outputs file path."""
    path = _write_memory_file(self.mem_dir, "mem.fact.alpha")

    result = self.runner.invoke(
      show_app,
      ["memory", "mem.fact.alpha", "--path", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert str(path) in result.stdout

  def test_show_memory_raw(self) -> None:
    """Show memory --raw outputs raw file content."""
    _write_memory_file(self.mem_dir, "mem.fact.alpha", "Raw Test")

    result = self.runner.invoke(
      show_app,
      ["memory", "mem.fact.alpha", "--raw", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "# Raw Test" in result.stdout
    assert "id: mem.fact.alpha" in result.stdout

  def test_show_memory_not_found(self) -> None:
    """Show memory with bad ID errors."""
    result = self.runner.invoke(
      show_app,
      ["memory", "mem.fact.nonexistent", "--root", str(self.root)],
    )

    assert result.exit_code == 1
    assert "not found" in result.stderr.lower()

  def test_show_memory_shorthand(self) -> None:
    """Show memory 'fact.alpha' normalizes to mem.fact.alpha."""
    _write_memory_file(self.mem_dir, "mem.fact.alpha")

    result = self.runner.invoke(
      show_app,
      ["memory", "fact.alpha", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "mem.fact.alpha" in result.stdout

  def test_show_memory_mutually_exclusive(self) -> None:
    """--json and --path are mutually exclusive."""
    _write_memory_file(self.mem_dir, "mem.fact.alpha")

    result = self.runner.invoke(
      show_app,
      ["memory", "mem.fact.alpha", "--json", "--path", "--root", str(self.root)],
    )

    assert result.exit_code == 1
    assert "mutually exclusive" in result.stderr.lower()


class ShowMemoryLinksDepthTest(unittest.TestCase):
  """Integration tests for show memory --links-depth."""

  def setUp(self) -> None:
    self.runner = CliRunner()
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()
    self.mem_dir = self.root / "memory"
    self.mem_dir.mkdir()

  def tearDown(self) -> None:
    self.tmpdir.cleanup()

  def _write_memory_with_body(
    self,
    mem_id: str,
    name: str,
    body: str,
    *,
    memory_type: str = "fact",
  ) -> Path:
    """Write a memory file with custom body content."""
    fm = {
      "id": mem_id,
      "name": name,
      "kind": "memory",
      "status": "active",
      "memory_type": memory_type,
      "created": "2026-01-15",
      "updated": "2026-02-01",
      "tags": [],
      "summary": "",
    }
    path = self.mem_dir / f"{mem_id}.md"
    content = f"---\n{yaml.safe_dump(fm, sort_keys=False)}---\n\n{body}\n"
    path.write_text(content, encoding="utf-8")
    return path

  def test_links_depth_shows_graph_table(self) -> None:
    """--links-depth 1 shows outgoing links as table."""
    self._write_memory_with_body(
      "mem.fact.root", "Root", "See [[mem.fact.child]]."
    )
    self._write_memory_with_body(
      "mem.fact.child", "Child", "Leaf node."
    )

    result = self.runner.invoke(
      show_app,
      [
        "memory", "mem.fact.root",
        "--links-depth", "1",
        "--root", str(self.root),
      ],
    )

    assert result.exit_code == 0, f"Failed: {result.output}"
    assert "mem.fact.root" in result.stdout
    assert "mem.fact.child" in result.stdout

  def test_links_depth_tree_format(self) -> None:
    """--links-depth with --tree shows indented tree."""
    self._write_memory_with_body(
      "mem.fact.root", "Root", "See [[mem.fact.child]]."
    )
    self._write_memory_with_body(
      "mem.fact.child", "Child", "Leaf node.", memory_type="pattern"
    )

    result = self.runner.invoke(
      show_app,
      [
        "memory", "mem.fact.root",
        "--links-depth", "1",
        "--tree",
        "--root", str(self.root),
      ],
    )

    assert result.exit_code == 0, f"Failed: {result.output}"
    # Tree format: indented child
    assert "mem.fact.root" in result.stdout
    assert "  mem.fact.child" in result.stdout

  def test_links_depth_json_format(self) -> None:
    """--links-depth with --json outputs structured JSON."""
    self._write_memory_with_body(
      "mem.fact.root", "Root", "See [[mem.fact.child]]."
    )
    self._write_memory_with_body(
      "mem.fact.child", "Child", "Leaf."
    )

    result = self.runner.invoke(
      show_app,
      [
        "memory", "mem.fact.root",
        "--links-depth", "1",
        "--json",
        "--root", str(self.root),
      ],
    )

    assert result.exit_code == 0, f"Failed: {result.output}"
    parsed = json.loads(result.stdout)
    assert isinstance(parsed, list)
    ids = [n["id"] for n in parsed]
    assert "mem.fact.root" in ids
    assert "mem.fact.child" in ids

  def test_links_depth_zero(self) -> None:
    """--links-depth 0 shows only root node."""
    self._write_memory_with_body(
      "mem.fact.root", "Root", "See [[mem.fact.child]]."
    )
    self._write_memory_with_body(
      "mem.fact.child", "Child", "Leaf."
    )

    result = self.runner.invoke(
      show_app,
      [
        "memory", "mem.fact.root",
        "--links-depth", "0",
        "--root", str(self.root),
      ],
    )

    assert result.exit_code == 0
    assert "mem.fact.root" in result.stdout
    assert "mem.fact.child" not in result.stdout

  def test_links_depth_not_found(self) -> None:
    """--links-depth on nonexistent memory errors."""
    result = self.runner.invoke(
      show_app,
      [
        "memory", "mem.fact.missing",
        "--links-depth", "1",
        "--root", str(self.root),
      ],
    )

    assert result.exit_code == 1


class ShowMemoryBodyOnlyTest(unittest.TestCase):
  """Integration tests for show memory --body-only."""

  def setUp(self) -> None:
    self.runner = CliRunner()
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()
    self.mem_dir = self.root / "memory"
    self.mem_dir.mkdir()

  def tearDown(self) -> None:
    self.tmpdir.cleanup()

  def test_body_only_strips_frontmatter(self) -> None:
    """--body-only outputs body without frontmatter."""
    _write_memory_file(self.mem_dir, "mem.fact.alpha", "Body Test")

    result = self.runner.invoke(
      show_app,
      ["memory", "mem.fact.alpha", "--body-only", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "---" not in result.stdout
    assert "id:" not in result.stdout
    assert "# Body Test" in result.stdout

  def test_body_only_short_flag(self) -> None:
    """-b is shorthand for --body-only."""
    _write_memory_file(self.mem_dir, "mem.fact.alpha", "Short Flag")

    result = self.runner.invoke(
      show_app,
      ["memory", "mem.fact.alpha", "-b", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "# Short Flag" in result.stdout
    assert "---" not in result.stdout

  def test_body_only_mutually_exclusive_with_json(self) -> None:
    """--body-only and --json are mutually exclusive."""
    _write_memory_file(self.mem_dir, "mem.fact.alpha")

    result = self.runner.invoke(
      show_app,
      ["memory", "mem.fact.alpha", "--body-only", "--json", "--root", str(self.root)],
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
    """Find memory with mem.* pattern."""
    _write_memory_file(self.mem_dir, "mem.fact.alpha", "First")
    _write_memory_file(self.mem_dir, "mem.fact.beta", "Second")

    result = self.runner.invoke(
      find_app,
      ["memory", "mem.fact.*", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "mem.fact.alpha" in result.stdout
    assert "mem.fact.beta" in result.stdout

  def test_find_memory_exact(self) -> None:
    """Find memory with exact ID."""
    _write_memory_file(self.mem_dir, "mem.fact.alpha")

    result = self.runner.invoke(
      find_app,
      ["memory", "mem.fact.alpha", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "mem.fact.alpha" in result.stdout

  def test_find_memory_shorthand(self) -> None:
    """Find memory with shorthand (omitted mem. prefix)."""
    _write_memory_file(self.mem_dir, "mem.fact.alpha")

    result = self.runner.invoke(
      find_app,
      ["memory", "fact.alpha", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "mem.fact.alpha" in result.stdout

  def test_find_memory_no_match(self) -> None:
    """Find memory with no match exits cleanly."""
    result = self.runner.invoke(
      find_app,
      ["memory", "mem.fact.nonexistent", "--root", str(self.root)],
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
      self.mem_dir,
      "mem.fact.alpha",
      "Auth Pattern",
      scope={"paths": ["src/auth/"]},
    )
    _write_memory_file(
      self.mem_dir,
      "mem.fact.beta",
      "DB Pattern",
      scope={"paths": ["src/db/models.py"]},
    )

    result = self.runner.invoke(
      list_app,
      ["memories", "--path", "src/auth/login.py", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "mem.fact.alpha" in result.stdout
    assert "mem.fact.beta" not in result.stdout

  def test_path_no_match_empty_output(self) -> None:
    """--path with no matching records exits cleanly."""
    _write_memory_file(
      self.mem_dir,
      "mem.fact.alpha",
      "Auth",
      scope={"paths": ["src/auth/"]},
    )

    result = self.runner.invoke(
      list_app,
      ["memories", "--path", "src/unrelated/foo.py", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "mem.fact.alpha" not in result.stdout

  def test_path_repeatable(self) -> None:
    """Multiple --path flags are OR'd."""
    _write_memory_file(
      self.mem_dir,
      "mem.fact.alpha",
      "Auth",
      scope={"paths": ["src/auth/"]},
    )
    _write_memory_file(
      self.mem_dir,
      "mem.fact.beta",
      "DB",
      scope={"paths": ["src/db/"]},
    )
    _write_memory_file(
      self.mem_dir,
      "mem.fact.gamma",
      "CLI",
      scope={"paths": ["src/cli/"]},
    )

    result = self.runner.invoke(
      list_app,
      [
        "memories",
        "--path",
        "src/auth/login.py",
        "--path",
        "src/db/conn.py",
        "--root",
        str(self.root),
      ],
    )

    assert result.exit_code == 0
    assert "mem.fact.alpha" in result.stdout
    assert "mem.fact.beta" in result.stdout
    assert "mem.fact.gamma" not in result.stdout

  # -- --command scope matching --

  def test_command_filters_by_scope(self) -> None:
    """--command filters by token-prefix match on scope.commands."""
    _write_memory_file(
      self.mem_dir,
      "mem.fact.alpha",
      "Test Tips",
      scope={"commands": ["test"]},
    )
    _write_memory_file(
      self.mem_dir,
      "mem.fact.beta",
      "Lint Tips",
      scope={"commands": ["lint"]},
    )

    result = self.runner.invoke(
      list_app,
      ["memories", "--command", "test auth --verbose", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "mem.fact.alpha" in result.stdout
    assert "mem.fact.beta" not in result.stdout

  # -- --match-tag scope matching --

  def test_match_tag_filters_by_tag_intersection(self) -> None:
    """--match-tag filters records whose tags overlap."""
    _write_memory_file(
      self.mem_dir,
      "mem.fact.alpha",
      "Auth",
      tags=["auth", "security"],
    )
    _write_memory_file(
      self.mem_dir,
      "mem.fact.beta",
      "DB",
      tags=["database"],
    )

    result = self.runner.invoke(
      list_app,
      ["memories", "--match-tag", "auth", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "mem.fact.alpha" in result.stdout
    assert "mem.fact.beta" not in result.stdout

  def test_match_tag_repeatable(self) -> None:
    """Multiple --match-tag flags are OR'd."""
    _write_memory_file(
      self.mem_dir,
      "mem.fact.alpha",
      "Auth",
      tags=["auth"],
    )
    _write_memory_file(
      self.mem_dir,
      "mem.fact.beta",
      "DB",
      tags=["database"],
    )
    _write_memory_file(
      self.mem_dir,
      "mem.fact.gamma",
      "CLI",
      tags=["cli"],
    )

    result = self.runner.invoke(
      list_app,
      [
        "memories",
        "--match-tag",
        "auth",
        "--match-tag",
        "database",
        "--root",
        str(self.root),
      ],
    )

    assert result.exit_code == 0
    assert "mem.fact.alpha" in result.stdout
    assert "mem.fact.beta" in result.stdout
    assert "mem.fact.gamma" not in result.stdout

  # -- --include-draft --

  def test_draft_excluded_by_default(self) -> None:
    """Draft records are excluded without --include-draft."""
    _write_memory_file(
      self.mem_dir,
      "mem.fact.alpha",
      "Active",
      status="active",
    )
    _write_memory_file(
      self.mem_dir,
      "mem.fact.beta",
      "Draft",
      status="draft",
    )

    result = self.runner.invoke(
      list_app,
      ["memories", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "mem.fact.alpha" in result.stdout
    assert "mem.fact.beta" not in result.stdout

  def test_include_draft_shows_drafts(self) -> None:
    """--include-draft surfaces draft records."""
    _write_memory_file(
      self.mem_dir,
      "mem.fact.alpha",
      "Active",
      status="active",
    )
    _write_memory_file(
      self.mem_dir,
      "mem.fact.beta",
      "Draft",
      status="draft",
    )

    result = self.runner.invoke(
      list_app,
      ["memories", "--include-draft", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "mem.fact.alpha" in result.stdout
    assert "mem.fact.beta" in result.stdout

  # -- --limit --

  def test_limit_caps_output(self) -> None:
    """--limit restricts the number of results."""
    names = ["alpha", "beta", "gamma", "delta", "epsilon"]
    for name in names:
      _write_memory_file(
        self.mem_dir,
        f"mem.fact.{name}",
        f"Mem {name}",
      )

    result = self.runner.invoke(
      list_app,
      ["memories", "--limit", "2", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    # Count non-empty, non-header lines containing mem.
    mem_lines = [ln for ln in result.stdout.splitlines() if "mem." in ln]
    assert len(mem_lines) == 2

  # -- deprecated excluded by default --

  def test_deprecated_excluded_by_default(self) -> None:
    """Deprecated records are excluded without explicit --status."""
    _write_memory_file(
      self.mem_dir,
      "mem.fact.alpha",
      "Active",
      status="active",
    )
    _write_memory_file(
      self.mem_dir,
      "mem.fact.beta",
      "Old",
      status="deprecated",
    )

    result = self.runner.invoke(
      list_app,
      ["memories", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "mem.fact.alpha" in result.stdout
    assert "mem.fact.beta" not in result.stdout

  def test_explicit_status_bypasses_exclusion(self) -> None:
    """--status deprecated shows deprecated records (skip_status_filter)."""
    _write_memory_file(
      self.mem_dir,
      "mem.fact.alpha",
      "Active",
      status="active",
    )
    _write_memory_file(
      self.mem_dir,
      "mem.fact.beta",
      "Old",
      status="deprecated",
    )

    result = self.runner.invoke(
      list_app,
      ["memories", "--status", "deprecated", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    assert "mem.fact.beta" in result.stdout
    assert "mem.fact.alpha" not in result.stdout

  # -- deterministic ordering --

  def test_ordering_by_severity(self) -> None:
    """Records ordered by severity (critical before low)."""
    _write_memory_file(
      self.mem_dir,
      "mem.fact.alpha",
      "Low Sev",
      priority={"severity": "low", "weight": 0},
    )
    _write_memory_file(
      self.mem_dir,
      "mem.fact.beta",
      "Critical Sev",
      priority={"severity": "critical", "weight": 0},
    )

    result = self.runner.invoke(
      list_app,
      ["memories", "--format", "tsv", "--root", str(self.root)],
    )

    assert result.exit_code == 0
    lines = [ln for ln in result.stdout.splitlines() if "mem." in ln]
    assert len(lines) == 2
    assert lines[0].startswith("mem.fact.beta"), (
      f"Critical should come first, got: {lines}"
    )
    assert lines[1].startswith("mem.fact.alpha")

  # -- combined scope + metadata filter --

  def test_path_combined_with_type_filter(self) -> None:
    """--path and --type both apply (AND between metadata and scope)."""
    _write_memory_file(
      self.mem_dir,
      "mem.fact.alpha",
      "Auth Fact",
      memory_type="fact",
      scope={"paths": ["src/auth/"]},
    )
    _write_memory_file(
      self.mem_dir,
      "mem.fact.beta",
      "Auth Pattern",
      memory_type="pattern",
      scope={"paths": ["src/auth/"]},
    )

    result = self.runner.invoke(
      list_app,
      [
        "memories",
        "--type",
        "fact",
        "--path",
        "src/auth/login.py",
        "--root",
        str(self.root),
      ],
    )

    assert result.exit_code == 0
    assert "mem.fact.alpha" in result.stdout
    assert "mem.fact.beta" not in result.stdout


if __name__ == "__main__":
  unittest.main()
