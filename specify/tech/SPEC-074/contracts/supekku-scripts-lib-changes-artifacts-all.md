# supekku.scripts.lib.changes.artifacts

Change artifact management and processing utilities.

## Constants

- `__all__`

## Functions

- `load_change_artifact(path) -> <BinOp>`: Load and parse a change artifact from markdown file.

Args:
  path: Path to artifact markdown file.

Returns:
  Parsed ChangeArtifact or None if ID is missing.

Raises:
  ValueError: If status is invalid.

## Classes

### ChangeArtifact

Represents a change artifact with metadata and relationships.

#### Methods

- `to_dict(self, repo_root) -> dict[Tuple[str, Any]]`: Convert artifact to dictionary for registry serialization.

Args:
  repo_root: Repository root for computing relative paths.

Returns:
  Dictionary representation of the artifact.
