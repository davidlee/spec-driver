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
- `_extract_declaration(self, line) -> <BinOp>`: Extract declaration name from a pub line.

Args:
    line: Line starting with 'pub '

Returns:
    Declaration signature or None
- `_find_zig_modules(self, root) -> list[Path]`: Find Zig modules (directories with .zig files).

Returns directories containing .zig files that are likely modules.
- `_generate_zig_docs(self, source_path) -> str`: Generate markdown documentation for Zig source.

Parses Zig files and extracts doc comments and public declarations.

Args:
    source_path: Path to Zig source file or directory

Returns:
    Markdown documentation string
- `_is_zig_package(self, path) -> bool`: Check if directory is a Zig package.

A Zig package is identified by:
- build.zig in the directory
- src/ subdirectory with .zig files
- build.zig.zon (Zig package manifest)
- `_parse_zig_file(self, zig_file) -> list[str]`: Parse a Zig file and extract documentation.

Args:
    zig_file: Path to .zig file

Returns:
    List of documentation lines

### ZigToolchainNotAvailableError

Raised when Zig toolchain is required but not available.

**Inherits from:** RuntimeError
