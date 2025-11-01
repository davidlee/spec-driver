# supekku.scripts.lib.sync.engine

Multi-language specification synchronization engine.

## Classes

### SpecSyncEngine

Engine for synchronizing technical specifications across multiple languages.

Orchestrates language adapters to discover source units, generate documentation,
and maintain registry mappings for Go, Python, and other supported languages.

#### Methods

- `add_adapter(self, language, adapter) -> None`: Add or replace adapter for a language.

Args:
    language: Language identifier
    adapter: Language adapter to add
- `get_adapter(self, language) -> <BinOp>`: Get adapter for a specific language.

Args:
    language: Language identifier

Returns:
    Language adapter or None if not supported
- `get_supported_languages(self) -> list[str]`: Get list of supported languages.

Returns:
    List of language identifiers
- `supports_identifier(self, identifier) -> <BinOp>`: Determine which language (if any) supports the given identifier.

Args:
    identifier: Source identifier to check

Returns:
    Language name if supported, None otherwise
- `synchronize(self) -> SyncOutcome`: Synchronize specifications across multiple languages.

Args:
    languages: Optional list of languages to process. If None,
        processes all.
    targets: Optional list of specific targets to process
        (format: "lang:identifier")
    check: If True, only check if docs would change (don't write
        files)

Returns:
    SyncOutcome with results of the synchronization operation
- `__init__(self, repo_root, tech_dir, adapters) -> None`: Initialize the multi-language spec sync engine.

Args:
    repo_root: Root directory of the repository
    tech_dir: Directory containing technical specifications
    adapters: Optional mapping of language -> adapter. If not provided,
             default adapters for Go and Python will be used.
- `_add_auto_detected_target(self, target, active_languages, language_targets) -> None`: Add target by auto-detecting language from identifier patterns.
- `_add_explicit_target(self, target, active_languages, language_targets) -> None`: Add target with explicit language prefix.
- `_add_target_to_language_map(self, target, active_languages, language_targets) -> None`: Add a target to the appropriate language in the target map.
- `_determine_active_languages(self, languages) -> list[str]`: Determine which languages to process.
- `_parse_targets(self, targets, active_languages) -> dict[Tuple[str, list[str]]]`: Parse targets into language-specific lists.
- `_process_language(self, language, lang_targets, check, outcome) -> None`: Process all source units for a single language.
- `_process_source_unit(self, unit, adapter, check, outcome) -> None`: Process a single source unit.
