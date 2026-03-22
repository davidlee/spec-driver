"""Core infrastructure layer for spec-driver.

Foundational pure functions, I/O, Git wrappers.
"""

from .file_ops import (
  FileChanges,
  copy_with_write_permission,
  copytree_with_write_permission,
  format_change_summary,
  format_detailed_changes,
  scan_directory_changes,
)

__all__ = [
  "FileChanges",
  "copy_with_write_permission",
  "copytree_with_write_permission",
  "format_change_summary",
  "format_detailed_changes",
  "scan_directory_changes",
]
