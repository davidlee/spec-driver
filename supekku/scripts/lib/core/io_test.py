"""Tests for core I/O utilities."""

from __future__ import annotations

import tempfile
from pathlib import Path

from supekku.scripts.lib.core.io import atomic_write


class TestAtomicWrite:
  """Tests for atomic_write."""

  def test_writes_content(self):
    with tempfile.TemporaryDirectory() as tmpdir:
      dest = Path(tmpdir) / "out.yaml"
      result = atomic_write(dest, "hello: world\n")
      assert result == dest
      assert dest.read_text() == "hello: world\n"

  def test_returns_path(self):
    with tempfile.TemporaryDirectory() as tmpdir:
      dest = Path(tmpdir) / "result.txt"
      returned = atomic_write(dest, "data")
      assert returned == dest

  def test_creates_parent_directory(self):
    with tempfile.TemporaryDirectory() as tmpdir:
      dest = Path(tmpdir) / "nested" / "deep" / "file.txt"
      atomic_write(dest, "content")
      assert dest.exists()
      assert dest.read_text() == "content"

  def test_overwrites_existing_file(self):
    with tempfile.TemporaryDirectory() as tmpdir:
      dest = Path(tmpdir) / "file.txt"
      dest.write_text("old content")
      atomic_write(dest, "new content")
      assert dest.read_text() == "new content"

  def test_no_temp_file_left_on_success(self):
    with tempfile.TemporaryDirectory() as tmpdir:
      dest = Path(tmpdir) / "out.txt"
      atomic_write(dest, "data")
      files = list(Path(tmpdir).iterdir())
      assert files == [dest]

  def test_utf8_encoding(self):
    with tempfile.TemporaryDirectory() as tmpdir:
      dest = Path(tmpdir) / "unicode.txt"
      content = "héllo wörld — 日本語\n"
      atomic_write(dest, content)
      assert dest.read_text(encoding="utf-8") == content
