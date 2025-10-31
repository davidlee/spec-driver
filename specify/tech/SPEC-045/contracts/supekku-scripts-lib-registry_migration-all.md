# supekku.scripts.lib.registry_migration

Registry migration from v1 (flat) to v2 (language-aware) format.

## Constants

- `__all__`

## Classes

### LanguageDetector

Detects language from source identifiers using SpecSyncEngine adapters.

#### Methods

- `detect_language(self, identifier) -> str`: Detect language from identifier using adapter support checks.

Uses refined logic for disambiguation when multiple adapters match.

Args:
    identifier: Source identifier (package path, file path, etc.)

Returns:
    Language name ("go", "python", etc.)
- `__init__(self) -> None`: Initialize with language adapters for detection.

### RegistryV2

v2 registry model - language-aware structure.

Format: {
    "version": 2,
    "languages": {
        "go": {"package/path": "SPEC-XXX"},
        "python": {"module.py": "SPEC-YYY"}
    },
    "metadata": {"created": "2025-01-15", ...}
}

#### Methods

- `add_source_unit(self, language, identifier, spec_id) -> None`: Add a source unit mapping to the registry.
- @classmethod `create_empty(cls) -> RegistryV2`: Create empty v2 registry with metadata.
- @classmethod `from_dict(cls, data) -> RegistryV2`: Create v2 registry from dictionary.
- @classmethod `from_file(cls, path) -> RegistryV2`: Load v2 registry from JSON file.
- `get_all_source_units(self) -> dict[Tuple[tuple[Tuple[str, str]], str]]`: Get all source units as (language, identifier) -> spec_id mapping.
- `get_spec_id(self, language, identifier) -> <BinOp>`: Get spec ID for a specific language and identifier.
- `get_spec_id_compat(self, identifier) -> <BinOp>`: Get spec ID with backwards compatibility.

Searches all languages, with Go as default/fallback for ambiguous cases.
- `remove_source_unit(self, language, identifier) -> bool`: Remove a source unit mapping from the registry.

Args:
    language: Language of the source unit
    identifier: Source identifier

Returns:
    True if the entry was removed, False if it didn't exist
- `remove_spec(self, spec_id) -> int`: Remove all source units that map to a specific spec ID.

Args:
    spec_id: Spec ID to remove (e.g., "SPEC-001")

Returns:
    Number of source units removed
- `save_to_file(self, path) -> None`: Save v2 registry to JSON file.
- `to_dict(self) -> dict[Tuple[str, Any]]`: Convert to dictionary for serialization.
