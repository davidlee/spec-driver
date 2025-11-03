# supekku.scripts.lib.specs.registry

Registry for managing and accessing specification files.

## Constants

- `__all__`

## Classes

### SpecRegistry

Discovery service for SPEC/PROD artefacts.

#### Methods

- `all_specs(self) -> list[Spec]`: Return all loaded specs.
- `find_by_informed_by(self, adr_id) -> list[Spec]`: Find specs informed by a specific ADR.

Args:
  adr_id: The ADR ID to search for (e.g., "ADR-001").
          Returns empty list if None or empty string.

Returns:
  List of Spec objects informed by the given ADR.
  Returns empty list if adr_id is None, empty, or no matches found.
- `find_by_package(self, package) -> list[Spec]`: Find all specs that reference the given package.
- `get(self, spec_id) -> <BinOp>`: Get a spec by its ID.
- `reload(self) -> None`: Reload all specs from the filesystem.
- `__init__(self, root) -> None`
- `_iter_prefixed_files(self, directory, prefix) -> Iterator[Path]`: Iterate over files with the given prefix in a directory.
- `_load_directory(self, directory) -> None` - ------------------------------------------------------------------
- `_register_spec(self, path, expected_kind) -> None`
