# supekku.scripts.lib.spec_sync.adapters.base

Abstract base class for language adapters.

## Classes

### LanguageAdapter

Abstract interface for language-specific source discovery and documentation.

Each language adapter is responsible for:
1. Discovering source units (packages, modules, files) for its language
2. Describing how source units should be processed (slug, frontmatter, variants)
3. Generating documentation variants with check mode support
4. Determining whether it supports a given identifier format

**Inherits from:** ABC

#### Methods

- @abstractmethod `describe(self, unit) -> SourceDescriptor`: Describe how a source unit should be processed.

Args:
    unit: Source unit to describe

Returns:
    SourceDescriptor with slug parts, frontmatter defaults, and variants
- @abstractmethod `discover_targets(self, repo_root, requested) -> list[SourceUnit]`: Discover source units for this language.

Args:
    repo_root: Root directory of the repository
    requested: Optional list of specific identifiers to process

Returns:
    List of SourceUnit objects representing discoverable targets
- @abstractmethod `generate(self, unit) -> list[DocVariant]`: Generate documentation variants for a source unit.

Args:
    unit: Source unit to generate documentation for
    spec_dir: Specification directory to write documentation to
    check: If True, only check if docs would change (don't write files)

Returns:
    List of DocVariant objects with generation results
- @abstractmethod `supports_identifier(self, identifier) -> bool`: Check if this adapter can handle the given identifier format.

Args:
    identifier: Source identifier to check

Returns:
    True if this adapter can process the identifier
- `validate_source_exists(self, unit) -> dict[Tuple[str, <BinOp>]]`: Validate that source file exists and is git-tracked.

Args:
    unit: Source unit to validate

Returns:
    Dictionary with validation results:
      - exists: Whether source file exists on disk
      - git_tracked: Whether file is tracked by git (None if can't determine)
      - status: "valid", "missing", or "untracked"
      - message: Human-readable status message
