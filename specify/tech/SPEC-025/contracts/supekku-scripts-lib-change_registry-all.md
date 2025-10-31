# supekku.scripts.lib.change_registry

Registry management for tracking and organizing change artifacts.

## Constants

- `_KIND_TO_DIR`
- `_KIND_TO_PREFIX`
- `__all__`

## Classes

### ChangeRegistry

Registry for managing change artifacts of specific types.

#### Methods

- `collect(self) -> dict[Tuple[str, ChangeArtifact]]`
- `sync(self) -> None`
- `__init__(self) -> None`
