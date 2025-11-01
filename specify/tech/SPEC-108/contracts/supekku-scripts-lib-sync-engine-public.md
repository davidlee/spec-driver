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
