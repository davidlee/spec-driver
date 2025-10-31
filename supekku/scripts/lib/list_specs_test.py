"""Tests for list_specs module."""

from __future__ import annotations

import io
import os
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from supekku.scripts.lib.spec_index import SpecIndexBuilder
from supekku.scripts.lib.core.spec_utils import dump_markdown_file
from supekku.scripts.list_specs import main as list_specs_main


@pytest.fixture
def temp_repo(tmp_path: Path) -> Path:
  """Create a temporary git repository for testing."""
  root = tmp_path
  (root / ".git").mkdir()
  return root


def _write_spec(
  root: Path,
  spec_id: str,
  slug: str,
  packages: list[str],
  name: str,
) -> Path:
  directory = root / "specify" / "tech" / f"{spec_id.lower()}-bundle"
  directory.mkdir(parents=True, exist_ok=True)
  path = directory / f"{spec_id}.md"
  frontmatter = {
    "id": spec_id,
    "slug": slug,
    "name": name,
    "created": "2024-01-01",
    "updated": "2024-01-01",
    "status": "draft",
    "kind": "spec",
    "packages": packages,
  }
  dump_markdown_file(path, frontmatter, f"# {spec_id}\n")
  return path


def _run(args: list[str], *, root: Path) -> list[str]:
  buf = io.StringIO()
  with redirect_stdout(buf):
    list_specs_main(["--root", str(root), *args])
  return [line for line in buf.getvalue().splitlines() if line.strip()]


def test_package_filter(temp_repo: Path) -> None:
  """Test filtering specs by package name substring."""
  _write_spec(temp_repo, "SPEC-100", "spec-100", ["internal/foo"], "Foo")
  _write_spec(temp_repo, "SPEC-200", "spec-200", ["internal/bar"], "Bar")

  lines = _run(["--package", "foo"], root=temp_repo)
  assert lines == ["SPEC-100\tspec-100"]


def test_for_path_filters_using_cwd(temp_repo: Path) -> None:
  """Test that --for-path finds specs matching the current working directory."""
  spec_path = _write_spec(
    temp_repo,
    "SPEC-300",
    "spec-300",
    ["internal/shared/pkg"],
    "Pkg",
  )
  working_dir = temp_repo / "internal" / "shared" / "pkg"
  working_dir.mkdir(parents=True, exist_ok=True)

  SpecIndexBuilder(temp_repo / "specify" / "tech").rebuild()

  original_cwd = Path.cwd()
  try:
    os.chdir(working_dir)
    lines = _run(["--for-path", ".", "--paths"], root=temp_repo)
  finally:
    os.chdir(original_cwd)

  assert lines == [f"SPEC-300\t{spec_path.relative_to(temp_repo).as_posix()}"]


def test_packages_flag_includes_package_list(temp_repo: Path) -> None:
  """Test that --packages flag includes package list in output."""
  _write_spec(
    temp_repo,
    "SPEC-400",
    "spec-400",
    ["internal/example", "cmd/example"],
    "Example",
  )

  lines = _run(["--packages"], root=temp_repo)
  assert lines == ["SPEC-400\tspec-400\tinternal/example,cmd/example"]


def test_package_path_filter_uses_symlink_index(temp_repo: Path) -> None:
  """Test filtering by exact package path using symlink index."""
  _write_spec(temp_repo, "SPEC-500", "spec-500", ["internal/app/foo"], "Foo")

  # Rebuild index manually
  SpecIndexBuilder(temp_repo / "specify" / "tech").rebuild()

  lines = _run(["--package-path", "internal/app/foo"], root=temp_repo)
  assert lines == ["SPEC-500\tspec-500"]
