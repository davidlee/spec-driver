# supekku.scripts.lib.core.paths

Central path configuration for spec-driver directories.

This module provides a single source of truth for all spec-driver workspace paths,
making it easy to change directory names or structure without hunting through code.

## Constants

- `SPEC_DRIVER_DIR` - Changed from "supekku" to ".spec-driver" for cleaner repo root

## Functions

- `get_about_dir(repo_root) -> Path`: Get the about directory for documentation.

Args:
  repo_root: Repository root path. If None, will auto-discover.

Returns:
  Path to the about directory (e.g., repo_root/supekku/about)
- `get_registry_dir(repo_root) -> Path`: Get the registry directory for YAML registry files.

Args:
  repo_root: Repository root path. If None, will auto-discover.

Returns:
  Path to the registry directory (e.g., repo_root/supekku/registry)
- `get_spec_driver_root(repo_root) -> Path`: Get the spec-driver configuration directory.

Args:
  repo_root: Repository root path. If None, will auto-discover.

Returns:
  Path to the spec-driver directory (e.g., repo_root/supekku)
- `get_templates_dir(repo_root) -> Path`: Get the templates directory for spec templates.

Args:
  repo_root: Repository root path. If None, will auto-discover.

Returns:
  Path to the templates directory (e.g., repo_root/supekku/templates)
