# supekku.scripts.lib.specs.registry

Registry for managing and accessing specification files.

## Classes

### SpecRegistry

Discovery service for SPEC/PROD artefacts.

#### Methods

- `all_specs(self) -> list[Spec]`: Return all loaded specs.
- `collect(self) -> dict[Tuple[str, Spec]]`: Return all specs as a dictionary keyed by ID.

Returns:
Copy of the internal spec dictionary.

- `filter(self) -> list[Spec]`: Filter specs by multiple criteria (AND logic).

Args:
status: Filter by status field.
category: Filter by category (unit/assembly).
kind: Filter by kind (spec/prod).
tag: Filter by tag membership.

Returns:
List of matching Specs.

- `find(self, spec_id) -> <BinOp>`: Find a spec by its ID.

Returns:
Spec or None if not found.

- `find_by_informed_by(self, adr_id) -> list[Spec]`: Find specs informed by a specific ADR.

Args:
adr_id: The ADR ID to search for (e.g., "ADR-001").
Returns empty list if None or empty string.

Returns:
List of Spec objects informed by the given ADR.
Returns empty list if adr_id is None, empty, or no matches found.

- `find_by_package(self, package) -> list[Spec]`: Find all specs that reference the given package.
- `get(self, spec_id) -> <BinOp>`: Find a spec by ID. Deprecated — use find() instead.
- `iter(self) -> Iterator[Spec]`: Iterate over specs, optionally filtered by status.

Args:
status: If provided, yield only specs with this status.

Yields:
Spec instances.

- `reload(self) -> None`: Reload all specs from the filesystem.
