# supekku.scripts.lib.specs.index

Specification index management for creating symlink-based indices.

## Constants

- `__all__`

## Classes

### SpecIndexBuilder

Builds and manages specification indices using symlinks.

#### Methods

- `rebuild(self) -> None`: Rebuild the specification index by creating symlinks.
- `__init__(self, base_dir) -> None`
- @staticmethod `_clean_flat_view_dir(view_dir) -> None`: Remove all symlinks and empty subdirectories in a flat view.
- @staticmethod `_create_flat_view_link(view_dir, bucket, spec_name) -> None`: Create a symlink: view_dir/bucket/spec_name → ../../spec_name.
- @staticmethod `_ensure_alias(link, target) -> None`: Create or replace a directory alias symlink.
- `_read_frontmatter(self, path) -> dict`: Extract YAML frontmatter from a markdown file.

### SpecIndexEntry

Data class representing a specification index entry.
