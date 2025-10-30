"""Reusable file operations for workspace management."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class FileChanges:
  """Represents the categorization of files in a sync operation."""

  new_files: list[Path]
  existing_files: list[Path]
  unchanged_files: list[Path]

  @property
  def has_changes(self) -> bool:
    """Returns True if there are any new or existing files to process."""
    return bool(self.new_files or self.existing_files)

  @property
  def total_changes(self) -> int:
    """Returns the total number of files that would be changed."""
    return len(self.new_files) + len(self.existing_files)


def scan_directory_changes(
  source_dir: Path, dest_dir: Path, pattern: str = "*"
) -> FileChanges:
  """Scan for differences between source and destination directories.

  Args:
    source_dir: Directory containing source files to copy
    dest_dir: Destination directory to check for existing files
    pattern: Glob pattern to filter files (default: "*" for all files)

  Returns:
    FileChanges object with categorized file lists (paths relative to source_dir)
  """
  if not source_dir.exists():
    return FileChanges(new_files=[], existing_files=[], unchanged_files=[])

  source_files = list(source_dir.glob(pattern))

  # Filter to files only
  source_files = [f for f in source_files if f.is_file()]

  new_files = []
  existing_files = []
  unchanged_files = []

  for source_file in source_files:
    rel_path = source_file.relative_to(source_dir)
    dest_file = dest_dir / rel_path

    if dest_file.exists():
      # Check if content differs
      if source_file.read_bytes() == dest_file.read_bytes():
        unchanged_files.append(rel_path)
      else:
        existing_files.append(rel_path)
    else:
      new_files.append(rel_path)

  return FileChanges(
    new_files=sorted(new_files),
    existing_files=sorted(existing_files),
    unchanged_files=sorted(unchanged_files),
  )


def format_change_summary(changes: FileChanges) -> str:
  """Format a change summary for display to the user.

  Args:
    changes: FileChanges object to summarize

  Returns:
    Human-readable summary string like "3 new, 5 updates" or "3 new" or "5 updates"
  """
  parts = []

  if changes.new_files:
    parts.append(f"{len(changes.new_files)} new")

  if changes.existing_files:
    parts.append(f"{len(changes.existing_files)} updates")

  if not parts:
    return "no changes"

  return ", ".join(parts)


def format_detailed_changes(
  changes: FileChanges, dest_dir: Path | None = None, indent: str = "  "
) -> str:
  """Format a detailed list of changes for display.

  Args:
    changes: FileChanges object to format
    dest_dir: Optional destination directory to show paths relative to cwd
    indent: String to use for indentation (default: "  ")

  Returns:
    Multi-line string with detailed file lists
  """
  lines = []

  if changes.new_files:
    lines.append(f"{indent}New files:")
    for file in changes.new_files:
      if dest_dir:
        full_path = dest_dir / file
        try:
          rel_path = full_path.relative_to(Path.cwd())
          # Prepend ./ for clarity
          display_path = f"./{rel_path}"
        except ValueError:
          # If not relative to cwd, use full path
          display_path = str(full_path)
      else:
        display_path = str(file)
      lines.append(f"{indent}  + {display_path}")

  if changes.existing_files:
    if lines:
      lines.append("")
    lines.append(f"{indent}Files to update:")
    for file in changes.existing_files:
      if dest_dir:
        full_path = dest_dir / file
        try:
          rel_path = full_path.relative_to(Path.cwd())
          # Prepend ./ for clarity
          display_path = f"./{rel_path}"
        except ValueError:
          # If not relative to cwd, use full path
          display_path = str(full_path)
      else:
        display_path = str(file)
      lines.append(f"{indent}  ~ {display_path}")

  return "\n".join(lines)
