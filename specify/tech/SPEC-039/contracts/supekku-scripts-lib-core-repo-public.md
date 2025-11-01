# supekku.scripts.lib.core.repo

Repository discovery utilities.

## Functions

- `find_repo_root(start) -> Path`: Find repository root from starting path.

Args:
  start: Path to start searching from. Defaults to current directory.

Returns:
  Repository root path.

Raises:
  RuntimeError: If repository root cannot be found.
