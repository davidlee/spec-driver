"""Legacy file operations re-exported from spec_driver.core.file_ops."""

from spec_driver.core.file_ops import (
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
