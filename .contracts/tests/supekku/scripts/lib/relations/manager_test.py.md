# supekku.scripts.lib.relations.manager_test

Tests for relations module.

## Classes

### RelationsTest

Test cases for relations management functionality.

**Inherits from:** RepoTestCase

#### Methods

- `test_add_relation(self) -> None`: Test adding a relation with attributes to a spec.
- `test_add_relation_avoids_duplicates(self) -> None`: Test that adding duplicate relations is prevented.
- `test_list_relations_empty(self) -> None`: Test listing relations returns empty list when no relations exist.
- `test_remove_missing_relation_returns_false(self) -> None`: Test that attempting to remove a non-existent relation returns False.
- `test_remove_relation(self) -> None`: Test removing an existing relation from a spec.
- `_make_spec(self) -> Path`
