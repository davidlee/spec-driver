"""Tests for resolve CLI commands."""

from __future__ import annotations

from pathlib import Path

from supekku.cli.resolve import (
  _build_artifact_index,
  _resolve_memory_links,
)
from supekku.scripts.lib.core.spec_utils import (
  dump_markdown_file,
  load_markdown_file,
)


def _init_repo(tmp_path: Path) -> Path:
  """Initialize minimal repo structure for testing.

  Creates .spec-driver dir so find_repo_root succeeds,
  and memory/ for mem files. Returns memory dir.
  """
  (tmp_path / ".spec-driver").mkdir(exist_ok=True)
  mem_dir = tmp_path / "memory"
  mem_dir.mkdir(exist_ok=True)
  return mem_dir


def _write_memory(
  mem_dir: Path,
  mem_id: str,
  name: str,
  body: str,
  memory_type: str = "fact",
) -> None:
  """Write a minimal memory file to disk."""
  dump_markdown_file(
    mem_dir / f"{mem_id}.md",
    {
      "id": mem_id,
      "name": name,
      "kind": "memory",
      "status": "active",
      "memory_type": memory_type,
    },
    body,
  )


# ── _build_artifact_index ────────────────────────────────────


class TestBuildArtifactIndex:
  """Tests for _build_artifact_index."""

  def test_includes_memory_records(self, tmp_path: Path) -> None:
    """Index includes memory records from registry."""
    mem_dir = _init_repo(tmp_path)
    _write_memory(mem_dir, "mem.fact.auth", "Auth", "Auth info\n")

    index = _build_artifact_index(tmp_path)
    assert "mem.fact.auth" in index
    path, kind = index["mem.fact.auth"]
    assert kind == "memory"
    assert "mem.fact.auth.md" in path

  def test_empty_repo(self, tmp_path: Path) -> None:
    """Index is empty for a repo with no artifacts."""
    _init_repo(tmp_path)
    index = _build_artifact_index(tmp_path)
    assert index == {}


# ── _resolve_memory_links ────────────────────────────────────


class TestResolveMemoryLinks:
  """Tests for _resolve_memory_links."""

  def test_no_op_empty_directory(self, tmp_path: Path) -> None:
    """No-op when memory directory is empty."""
    _init_repo(tmp_path)
    stats = _resolve_memory_links(tmp_path, dry_run=False)
    assert stats["processed"] == 0
    assert stats["resolved"] == 0
    assert stats["missing"] == 0

  def test_no_op_missing_directory(self, tmp_path: Path) -> None:
    """No-op when memory directory doesn't exist."""
    stats = _resolve_memory_links(tmp_path, dry_run=False)
    assert stats["processed"] == 0

  def test_resolves_and_writes_frontmatter(
    self,
    tmp_path: Path,
  ) -> None:
    """Resolution writes full links to frontmatter in full mode."""
    mem_dir = _init_repo(tmp_path)

    _write_memory(mem_dir, "mem.fact.auth", "Auth", "No links.\n")
    _write_memory(
      mem_dir,
      "mem.pattern.cli.skinny",
      "Skinny CLI",
      "See [[mem.fact.auth]]\n",
      memory_type="pattern",
    )

    stats = _resolve_memory_links(
      tmp_path,
      dry_run=False,
      link_mode="full",
    )
    assert stats["processed"] == 2
    assert stats["resolved"] >= 1

    fm, _ = load_markdown_file(
      mem_dir / "mem.pattern.cli.skinny.md",
    )
    assert "links" in fm
    assert len(fm["links"]["out"]) == 1
    assert fm["links"]["out"][0]["id"] == "mem.fact.auth"

  def test_default_mode_omits_out(
    self,
    tmp_path: Path,
  ) -> None:
    """Default mode (missing) omits resolved links from frontmatter."""
    mem_dir = _init_repo(tmp_path)

    _write_memory(mem_dir, "mem.fact.auth", "Auth", "No links.\n")
    _write_memory(
      mem_dir,
      "mem.pattern.cli.skinny",
      "Skinny CLI",
      "See [[mem.fact.auth]]\n",
      memory_type="pattern",
    )

    stats = _resolve_memory_links(tmp_path, dry_run=False)
    assert stats["processed"] == 2
    assert stats["resolved"] >= 1

    fm, _ = load_markdown_file(
      mem_dir / "mem.pattern.cli.skinny.md",
    )
    # Default mode=missing: no links.out persisted, no links key
    # since there are no missing links either
    assert "links" not in fm

  def test_dry_run_skips_writes(self, tmp_path: Path) -> None:
    """Dry-run does not modify files."""
    mem_dir = _init_repo(tmp_path)
    _write_memory(
      mem_dir,
      "mem.fact.auth",
      "Auth",
      "See [[mem.fact.auth]]\n",
    )

    stats = _resolve_memory_links(tmp_path, dry_run=True)
    assert stats["processed"] >= 1

    fm, _ = load_markdown_file(mem_dir / "mem.fact.auth.md")
    assert "links" not in fm

  def test_missing_targets_tracked(self, tmp_path: Path) -> None:
    """Missing targets counted in stats."""
    mem_dir = _init_repo(tmp_path)
    _write_memory(
      mem_dir,
      "mem.fact.test",
      "Test",
      "Ref: [[ADR-999]]\n",
    )

    stats = _resolve_memory_links(tmp_path, dry_run=False)
    assert stats["missing"] >= 1

  def test_clears_stale_links(self, tmp_path: Path) -> None:
    """Links removed when body no longer contains them."""
    mem_dir = _init_repo(tmp_path)

    dump_markdown_file(
      mem_dir / "mem.fact.test.md",
      {
        "id": "mem.fact.test",
        "name": "Test",
        "kind": "memory",
        "status": "active",
        "memory_type": "fact",
        "links": {
          "out": [
            {"id": "ADR-001", "path": "a.md", "kind": "adr"},
          ],
        },
      },
      "No links anymore.\n",
    )

    _resolve_memory_links(tmp_path, dry_run=False)

    fm, _ = load_markdown_file(mem_dir / "mem.fact.test.md")
    assert "links" not in fm
