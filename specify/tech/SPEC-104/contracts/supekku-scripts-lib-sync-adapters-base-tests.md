# supekku.scripts.lib.sync.adapters.base

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
- `__init__(self, repo_root) -> None`: Initialize adapter with repository root. - Language identifier (e.g., "go", "python", "typescript")
- `_create_doc_variant(self, name, slug_parts, language_subdir) -> DocVariant`: Create a DocVariant with standard placeholder values.

Args:
    name: Variant name (e.g., "public", "api", "tests")
    slug_parts: Parts to join for the filename
    language_subdir: Language subdirectory (e.g., "go", "python")

Returns:
    DocVariant with placeholder hash and status
- `_get_git_tracked_files(self) -> set[Path]`: Get set of git-tracked files (cached).

Returns:
    Set of absolute paths to git-tracked files
- `_get_source_path(self, unit) -> <BinOp>`: Get filesystem path for a source unit.

Default implementation assumes identifier is relative path from repo root.
Subclasses should override for language-specific path resolution.

Args:
    unit: Source unit

Returns:
    Path to source file, or None if cannot be determined
- `_should_skip_path(self, path) -> bool`: Check if a path should be skipped (shared across all adapters).

Args:
    path: Path to check

Returns:
    True if the path should be skipped
- `_validate_unit_language(self, unit) -> None`: Validate that the unit language matches this adapter.

Args:
    unit: Source unit to validate

Raises:
    ValueError: If unit language doesn't match adapter language
