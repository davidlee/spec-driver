# supekku.scripts.lib.sync.adapters.zig

Zig language adapter for specification synchronization.

## Functions

- `is_zig_available() -> bool`: Check if zig compiler is available in PATH.

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
- `generate(self, unit) -> list[DocVariant]`: Generate documentation for a Zig package/module.

Uses `zig build-exe --emit=docs` or autodoc when available.

Args:
    unit: Zig source unit
    spec_dir: Specification directory to write documentation to
    check: If True, only check if docs would change

Returns:
    List of DocVariant objects with generation results
- `supports_identifier(self, identifier) -> bool`: Check if identifier looks like a Zig path.

Args:
    identifier: Identifier to check

Returns:
    True if identifier appears to be a Zig source path

### ZigToolchainNotAvailableError

Raised when Zig toolchain is required but not available.

**Inherits from:** RuntimeError
