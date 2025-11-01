# supekku.scripts.lib.file_ops

Reusable file operations for workspace management.

## Functions

- `format_change_summary(changes) -> str`: Format a change summary for display to the user.

Args:
  changes: FileChanges object to summarize

Returns:
  Human-readable summary string like "3 new, 5 updates" or "3 new" or "5 updates"
- `format_detailed_changes(changes, dest_dir, indent) -> str`: Format a detailed list of changes for display.

Args:
  changes: FileChanges object to format
  dest_dir: Optional destination directory to show paths relative to cwd
  indent: String to use for indentation (default: "  ")

Returns:
  Multi-line string with detailed file lists
- `scan_directory_changes(source_dir, dest_dir, pattern) -> FileChanges`: Scan for differences between source and destination directories.

Args:
  source_dir: Directory containing source files to copy
  dest_dir: Destination directory to check for existing files
  pattern: Glob pattern to filter files (default: "*" for all files)

Returns:
  FileChanges object with categorized file lists (paths relative to source_dir)

## Classes

### FileChanges

Represents the categorization of files in a sync operation.

#### Methods

- @property `has_changes(self) -> bool`: Returns True if there are any new or existing files to process.
- @property `total_changes(self) -> int`: Returns the total number of files that would be changed.
