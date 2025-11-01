# supekku.scripts.lib.relations.manager

Utilities for managing relationships between specifications and changes.

## Constants

- `RelationDict`

## Functions

- `add_relation(path) -> bool`: Add a relation to markdown file frontmatter.

Args:
  path: Path to markdown file.
  relation_type: Type of relation (e.g., "implements", "supersedes").
  target: Target identifier.
  **attributes: Additional relation attributes.

Returns:
  True if relation was added, False if it already existed.

Raises:
  ValueError: If relation_type or target are empty.
  TypeError: If frontmatter relations are malformed.
- `list_relations(path) -> list[Relation]`: List relations from markdown file frontmatter.

Args:
  path: Path to markdown file.

Returns:
  List of parsed Relation objects.
- `remove_relation(path) -> bool`: Remove a relation from markdown file frontmatter.

Args:
  path: Path to markdown file.
  relation_type: Type of relation to remove.
  target: Target identifier.

Returns:
  True if relation was removed, False if it wasn't found.

Raises:
  ValueError: If relation_type or target are empty.
  TypeError: If frontmatter relations are malformed.
