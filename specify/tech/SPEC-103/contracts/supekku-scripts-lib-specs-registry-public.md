# supekku.scripts.lib.specs.registry

Registry for managing and accessing specification files.

## Classes

### SpecRegistry

Discovery service for SPEC/PROD artefacts.

#### Methods

- `all_specs(self) -> list[Spec]`: Return all loaded specs.
- `find_by_package(self, package) -> list[Spec]`: Find all specs that reference the given package.
- `get(self, spec_id) -> <BinOp>`: Get a spec by its ID.
- `reload(self) -> None`: Reload all specs from the filesystem.
