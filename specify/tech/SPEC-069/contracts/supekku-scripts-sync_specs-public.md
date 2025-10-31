# supekku.scripts.sync_specs

Multi-language specification synchronization.

Synchronizes technical specifications with source code across multiple languages,
generating interface documentation and maintaining registry mappings.

Supports Go (via gomarkdoc) and Python (via AST analysis) with extensible
adapter architecture for additional languages.

## Constants

- `REGISTRY_PATH`
- `ROOT`
- `TECH_DIR`

## Functions

- `main() -> None`: Main entry point for multi-language spec synchronization.
- `parse_language_targets(targets) -> dict[Tuple[str, list[str]]]`: Parse language-prefixed targets into language-specific lists.

Args:
    targets: List of targets, optionally prefixed with language
             (e.g., "go:internal/foo", "python:module.py")

Returns:
    Dictionary mapping language to list of identifiers

## Classes

### MultiLanguageSpecManager

Manages spec creation and registry updates for multiple languages.

#### Methods

- `process_source_unit(self, source_unit, adapter, check_mode, dry_run) -> dict`: Process a single source unit.

Create spec, update registry, generate docs.
- `rebuild_indices(self) -> None`: Rebuild symlink indices.
- `save_registry(self) -> None`: Save the registry to disk.
