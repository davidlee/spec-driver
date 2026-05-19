"""Tests for spec_driver.migrations._helpers (frozen-forever bytes helpers)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

from spec_driver.migrations._helpers import (
  atomic_write,
  replace_in_frontmatter_block,
  split_frontmatter,
)


class TestSplitFrontmatter:
  def test_canonical_frontmatter(self) -> None:
    text = "---\nid: DE-001\nkind: delta\n---\nbody text\n"
    yaml_block, body = split_frontmatter(text)
    assert yaml_block == "id: DE-001\nkind: delta\n"
    assert body == "body text\n"

  def test_no_frontmatter_returns_empty_yaml(self) -> None:
    text = "no frontmatter here\nsecond line\n"
    yaml_block, body = split_frontmatter(text)
    assert yaml_block == ""
    assert body == text

  def test_empty_string(self) -> None:
    assert split_frontmatter("") == ("", "")

  def test_open_delimiter_only(self) -> None:
    text = "---\nid: DE-001\n(missing close)"
    yaml_block, body = split_frontmatter(text)
    assert yaml_block == ""
    assert body == text

  def test_trailing_no_newline(self) -> None:
    text = "---\nid: DE-001\n---"
    yaml_block, body = split_frontmatter(text)
    assert yaml_block == "id: DE-001\n"
    assert body == ""


class TestAtomicWrite:
  def test_writes_new_file(self, tmp_path: Path) -> None:
    target = tmp_path / "out.md"
    atomic_write(target, "hello\n")
    assert target.read_text(encoding="utf-8") == "hello\n"

  def test_overwrites_existing(self, tmp_path: Path) -> None:
    target = tmp_path / "out.md"
    target.write_text("old\n", encoding="utf-8")
    atomic_write(target, "new\n")
    assert target.read_text(encoding="utf-8") == "new\n"

  @pytest.mark.skipif(sys.platform == "win32", reason="POSIX mode bits only")
  def test_preserves_mode_on_overwrite(self, tmp_path: Path) -> None:
    target = tmp_path / "out.md"
    target.write_text("old\n", encoding="utf-8")
    target.chmod(0o640)
    atomic_write(target, "new\n")
    assert (target.stat().st_mode & 0o777) == 0o640

  def test_creates_parent_directories(self, tmp_path: Path) -> None:
    target = tmp_path / "nested" / "dir" / "out.md"
    atomic_write(target, "x")
    assert target.read_text(encoding="utf-8") == "x"

  def test_failure_cleans_tempfile(
    self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    target = tmp_path / "out.md"

    def _boom(*_args: object, **_kw: object) -> None:
      raise RuntimeError("boom")

    monkeypatch.setattr(os, "replace", _boom)
    with pytest.raises(RuntimeError):
      atomic_write(target, "x")

    leftovers = [p for p in tmp_path.iterdir() if p.name.startswith(".out.md")]
    assert leftovers == []


class TestReplaceInFrontmatterBlock:
  def test_rewrites_scalar(self) -> None:
    fm = "id: DE-001\nstatus: draft\nkind: delta\n"
    out = replace_in_frontmatter_block(fm, "status", "completed")
    assert out == "id: DE-001\nstatus: completed\nkind: delta\n"

  def test_preserves_trailing_comment(self) -> None:
    fm = "id: DE-001\nstatus: draft  # legacy hint\nkind: delta\n"
    out = replace_in_frontmatter_block(fm, "status", "completed")
    assert out == "id: DE-001\nstatus: completed  # legacy hint\nkind: delta\n"

  def test_preserves_quoted_value(self) -> None:
    fm = 'id: "DE-001"\nstatus: draft\n'
    out = replace_in_frontmatter_block(fm, "status", "completed")
    assert out == 'id: "DE-001"\nstatus: completed\n'

  def test_missing_key_raises(self) -> None:
    fm = "id: DE-001\nkind: delta\n"
    with pytest.raises(KeyError):
      replace_in_frontmatter_block(fm, "status", "completed")

  def test_indented_child_key_not_matched(self) -> None:
    fm = "id: DE-001\nrelations:\n  status: in-flight\nstatus: draft\n"
    out = replace_in_frontmatter_block(fm, "status", "completed")
    assert "  status: in-flight" in out
    assert "\nstatus: completed\n" in out
