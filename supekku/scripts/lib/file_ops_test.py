"""Tests for file_ops module."""

import os
from pathlib import Path

from supekku.scripts.lib.file_ops import (
  FileChanges,
  format_change_summary,
  format_detailed_changes,
  scan_directory_changes,
)


def test_file_changes_has_changes():
  """Test FileChanges.has_changes property."""
  # No changes
  changes = FileChanges(new_files=[], existing_files=[], unchanged_files=[])
  assert not changes.has_changes

  # Only new files
  changes = FileChanges(
    new_files=[Path("a.txt")], existing_files=[], unchanged_files=[]
  )
  assert changes.has_changes

  # Only existing files
  changes = FileChanges(
    new_files=[], existing_files=[Path("b.txt")], unchanged_files=[]
  )
  assert changes.has_changes

  # Both new and existing
  changes = FileChanges(
    new_files=[Path("a.txt")],
    existing_files=[Path("b.txt")],
    unchanged_files=[],
  )
  assert changes.has_changes

  # Only unchanged files
  changes = FileChanges(
    new_files=[], existing_files=[], unchanged_files=[Path("c.txt")]
  )
  assert not changes.has_changes


def test_file_changes_total_changes():
  """Test FileChanges.total_changes property."""
  changes = FileChanges(
    new_files=[Path("a.txt"), Path("b.txt")],
    existing_files=[Path("c.txt")],
    unchanged_files=[Path("d.txt")],
  )
  assert changes.total_changes == 3


def test_scan_directory_changes_nonexistent_source(tmp_path):
  """Test scan_directory_changes with nonexistent source directory."""
  source = tmp_path / "nonexistent"
  dest = tmp_path / "dest"
  dest.mkdir()

  changes = scan_directory_changes(source, dest)

  assert not changes.new_files
  assert not changes.existing_files
  assert not changes.unchanged_files


def test_scan_directory_changes_all_new(tmp_path):
  """Test scan_directory_changes with all new files."""
  source = tmp_path / "source"
  dest = tmp_path / "dest"
  source.mkdir()
  dest.mkdir()

  (source / "file1.txt").write_text("content1")
  (source / "file2.txt").write_text("content2")

  changes = scan_directory_changes(source, dest, "*.txt")

  assert len(changes.new_files) == 2
  assert Path("file1.txt") in changes.new_files
  assert Path("file2.txt") in changes.new_files
  assert not changes.existing_files
  assert not changes.unchanged_files


def test_scan_directory_changes_all_existing_modified(tmp_path):
  """Test scan_directory_changes with all existing files that differ."""
  source = tmp_path / "source"
  dest = tmp_path / "dest"
  source.mkdir()
  dest.mkdir()

  (source / "file1.txt").write_text("new content1")
  (source / "file2.txt").write_text("new content2")
  (dest / "file1.txt").write_text("old content1")
  (dest / "file2.txt").write_text("old content2")

  changes = scan_directory_changes(source, dest, "*.txt")

  assert not changes.new_files
  assert len(changes.existing_files) == 2
  assert Path("file1.txt") in changes.existing_files
  assert Path("file2.txt") in changes.existing_files
  assert not changes.unchanged_files


def test_scan_directory_changes_all_existing_unchanged(tmp_path):
  """Test scan_directory_changes with all existing files that are identical."""
  source = tmp_path / "source"
  dest = tmp_path / "dest"
  source.mkdir()
  dest.mkdir()

  (source / "file1.txt").write_text("same content1")
  (source / "file2.txt").write_text("same content2")
  (dest / "file1.txt").write_text("same content1")
  (dest / "file2.txt").write_text("same content2")

  changes = scan_directory_changes(source, dest, "*.txt")

  assert not changes.new_files
  assert not changes.existing_files
  assert len(changes.unchanged_files) == 2
  assert Path("file1.txt") in changes.unchanged_files
  assert Path("file2.txt") in changes.unchanged_files


def test_scan_directory_changes_mixed(tmp_path):
  """Test scan_directory_changes with mixed new, existing, and unchanged files."""
  source = tmp_path / "source"
  dest = tmp_path / "dest"
  source.mkdir()
  dest.mkdir()

  # New file
  (source / "new.txt").write_text("new content")

  # Existing modified file
  (source / "modified.txt").write_text("new version")
  (dest / "modified.txt").write_text("old version")

  # Unchanged file
  (source / "unchanged.txt").write_text("same content")
  (dest / "unchanged.txt").write_text("same content")

  changes = scan_directory_changes(source, dest, "*.txt")

  assert len(changes.new_files) == 1
  assert Path("new.txt") in changes.new_files

  assert len(changes.existing_files) == 1
  assert Path("modified.txt") in changes.existing_files

  assert len(changes.unchanged_files) == 1
  assert Path("unchanged.txt") in changes.unchanged_files


def test_scan_directory_changes_pattern_filter(tmp_path):
  """Test scan_directory_changes with glob pattern filtering."""
  source = tmp_path / "source"
  dest = tmp_path / "dest"
  source.mkdir()
  dest.mkdir()

  (source / "file1.txt").write_text("content1")
  (source / "file2.md").write_text("content2")
  (source / "file3.txt").write_text("content3")

  changes = scan_directory_changes(source, dest, "*.txt")

  assert len(changes.new_files) == 2
  assert Path("file1.txt") in changes.new_files
  assert Path("file3.txt") in changes.new_files
  assert Path("file2.md") not in changes.new_files


def test_scan_directory_changes_skips_directories(tmp_path):
  """Test that scan_directory_changes only processes files, not directories."""
  source = tmp_path / "source"
  dest = tmp_path / "dest"
  source.mkdir()
  dest.mkdir()

  (source / "file.txt").write_text("content")
  (source / "subdir").mkdir()

  changes = scan_directory_changes(source, dest)

  assert len(changes.new_files) == 1
  assert Path("file.txt") in changes.new_files


def test_format_change_summary_no_changes():
  """Test format_change_summary with no changes."""
  changes = FileChanges(new_files=[], existing_files=[], unchanged_files=[])
  assert format_change_summary(changes) == "no changes"


def test_format_change_summary_only_new():
  """Test format_change_summary with only new files."""
  changes = FileChanges(
    new_files=[Path("a.txt"), Path("b.txt"), Path("c.txt")],
    existing_files=[],
    unchanged_files=[],
  )
  assert format_change_summary(changes) == "3 new"


def test_format_change_summary_only_updates():
  """Test format_change_summary with only updates."""
  changes = FileChanges(
    new_files=[],
    existing_files=[Path("a.txt"), Path("b.txt")],
    unchanged_files=[],
  )
  assert format_change_summary(changes) == "2 updates"


def test_format_change_summary_both():
  """Test format_change_summary with both new and updated files."""
  changes = FileChanges(
    new_files=[Path("a.txt"), Path("b.txt")],
    existing_files=[Path("c.txt"), Path("d.txt"), Path("e.txt")],
    unchanged_files=[],
  )
  assert format_change_summary(changes) == "2 new, 3 updates"


def test_format_detailed_changes_no_changes():
  """Test format_detailed_changes with no changes."""
  changes = FileChanges(new_files=[], existing_files=[], unchanged_files=[])
  assert format_detailed_changes(changes) == ""


def test_format_detailed_changes_only_new():
  """Test format_detailed_changes with only new files."""
  changes = FileChanges(
    new_files=[Path("a.txt"), Path("b.txt")], existing_files=[], unchanged_files=[]
  )
  result = format_detailed_changes(changes)
  assert "New files:" in result
  assert "+ a.txt" in result
  assert "+ b.txt" in result


def test_format_detailed_changes_only_updates():
  """Test format_detailed_changes with only updates."""
  changes = FileChanges(
    new_files=[], existing_files=[Path("a.txt"), Path("b.txt")], unchanged_files=[]
  )
  result = format_detailed_changes(changes)
  assert "Files to update:" in result
  assert "~ a.txt" in result
  assert "~ b.txt" in result


def test_format_detailed_changes_both():
  """Test format_detailed_changes with both new and updated files."""
  changes = FileChanges(
    new_files=[Path("new.txt")],
    existing_files=[Path("existing.txt")],
    unchanged_files=[],
  )
  result = format_detailed_changes(changes)
  assert "New files:" in result
  assert "+ new.txt" in result
  assert "Files to update:" in result
  assert "~ existing.txt" in result


def test_format_detailed_changes_custom_indent():
  """Test format_detailed_changes with custom indentation."""
  changes = FileChanges(
    new_files=[Path("a.txt")], existing_files=[], unchanged_files=[]
  )
  result = format_detailed_changes(changes, indent="    ")
  assert result.startswith("    New files:")
  assert "    + a.txt" in result


def test_format_detailed_changes_with_dest_dir(tmp_path):
  """Test format_detailed_changes shows relative paths when dest_dir provided."""
  # Create a destination within tmp_path (which becomes our cwd for the test)
  original_cwd = Path.cwd()
  try:
    # Change to tmp_path to test relative path generation
    os.chdir(tmp_path)

    dest = tmp_path / "destination"
    changes = FileChanges(
      new_files=[Path("new.txt"), Path("subdir/another.txt")],
      existing_files=[Path("existing.txt")],
      unchanged_files=[],
    )
    result = format_detailed_changes(changes, dest)

    # Should show relative paths with ./
    assert "+ ./destination/new.txt" in result
    assert "+ ./destination/subdir/another.txt" in result
    assert "~ ./destination/existing.txt" in result

    # Should not show bare filenames
    assert "+ new.txt" not in result
    assert "~ existing.txt" not in result
  finally:
    os.chdir(original_cwd)
