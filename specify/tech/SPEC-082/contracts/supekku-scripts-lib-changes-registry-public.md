# supekku.scripts.lib.changes.registry

Registry management for tracking and organizing change artifacts.

## Classes

### ChangeRegistry

Registry for managing change artifacts of specific types.

#### Methods

- `collect(self) -> dict[Tuple[str, ChangeArtifact]]`: Collect all change artifacts from directory.

Returns:
  Dictionary mapping artifact IDs to ChangeArtifact objects.
- `sync(self) -> None`: Synchronize registry file with artifacts found in directory.
