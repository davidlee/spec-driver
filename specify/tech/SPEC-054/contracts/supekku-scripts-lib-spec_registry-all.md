# supekku.scripts.lib.spec_registry

Registry for managing and accessing specification files.

## Constants

- `__all__`

## Classes

### SpecRegistry

Discovery service for SPEC/PROD artefacts.

#### Methods

- `all_specs(self) -> list[Spec]`: Return all loaded specs.
- `find_by_package(self, package) -> list[Spec]`: Find all specs that reference the given package.
- `get(self, spec_id) -> <BinOp>`: Get a spec by its ID.
- `reload(self) -> None`: Reload all specs from the filesystem.
- `__init__(self, root) -> None`
- `_iter_prefixed_files(self, directory, prefix) -> Iterator[Path]`: Iterate over files with the given prefix in a directory.
- `_load_directory(self, directory) -> None` - ------------------------------------------------------------------
- `_register_spec(self, path, expected_kind) -> None`
