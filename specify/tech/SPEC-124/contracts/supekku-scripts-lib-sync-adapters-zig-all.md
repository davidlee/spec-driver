# supekku.scripts.lib.sync.adapters.zig

Zig language adapter for specification synchronization.

## Functions

- `is_zig_available() -> bool`: Check if zig compiler is available in PATH.
- `is_zigmarkdoc_available() -> bool`: Check if zigmarkdoc is available in PATH.

## Classes

### ZigAdapter

Language adapter for Zig modules and packages.

Discovers Zig source files and packages, generates documentation using
autodoc when available.

**Inherits from:** LanguageAdapter

#### Methods

- `describe(self, unit) -> SourceDescriptor`: Describe how a Zig package/module should be processed.

Args:
    unit: Zig source unit

Returns:
    SourceDescriptor with Zig-specific metadata
- `discover_targets(self, repo_root, requested) -> list[SourceUnit]`: Discover Zig packages and modules.

Args:
    repo_root: Root directory of the repository
    requested: Optional list of specific paths to process

Returns:
    List of SourceUnit objects for Zig packages/modules
- `generate(self, unit) -> list[DocVariant]`: Generate documentation for a Zig package/module using zigmarkdoc.

Args:
    unit: Zig source unit
    spec_dir: Specification directory to write documentation to
    check: If True, only check if docs would change

Returns:
    List of DocVariant objects with generation results

Raises:
    ZigmarkdocNotAvailableError: If zigmarkdoc is not available
    FileNotFoundError: If source path does not exist
- `supports_identifier(self, identifier) -> bool`: Check if identifier looks like a Zig path.

Args:
    identifier: Identifier to check

Returns:
    True if identifier appears to be a Zig source path
- `_find_zig_files(self, root) -> list[Path]`: Find Zig source files.

Returns individual .zig files (Zig is per-file, not per-directory).
- `_is_zig_package(self, path) -> bool`: Check if directory is a Zig package.

A Zig package is identified by:
- build.zig in the directory
- src/ subdirectory with .zig files
- build.zig.zon (Zig package manifest)

### ZigToolchainNotAvailableError

Raised when Zig toolchain is required but not available.

**Inherits from:** RuntimeError

### ZigmarkdocNotAvailableError

Raised when zigmarkdoc is required but not available.

**Inherits from:** RuntimeError
