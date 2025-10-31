# supekku.scripts.lib.spec_index

Specification index management for creating symlink-based indices.

## Constants

- `__all__`

## Classes

### SpecIndexBuilder

Builds and manages specification indices using symlinks.

#### Methods

- `rebuild(self) -> None`: Rebuild the specification index by creating symlinks.
- `__init__(self, base_dir) -> None`
- `_read_frontmatter(self, path) -> dict`: Extract YAML frontmatter from a markdown file.

### SpecIndexEntry

Data class representing a specification index entry.
