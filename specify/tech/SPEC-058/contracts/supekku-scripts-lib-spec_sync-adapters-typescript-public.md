# supekku.scripts.lib.spec_sync.adapters.typescript

TypeScript language adapter for specification synchronization (STUB).

This is a placeholder implementation for future TypeScript support.
Currently returns not implemented errors for all operations.

## Classes

### TypeScriptAdapter

Language adapter for TypeScript modules (STUB IMPLEMENTATION).

This is a placeholder implementation that provides the interface
for TypeScript support but does not yet implement documentation
generation. Future implementation should integrate with TypeDoc
or a custom AST-based documentation generator.

TODO: Implement actual TypeScript documentation generation
TODO: Evaluate TypeDoc vs custom AST solution
TODO: Define variant mapping (public/internal/tests)
TODO: Implement source discovery patterns

**Inherits from:** LanguageAdapter

#### Methods

- `describe(self, unit) -> SourceDescriptor`: Describe how a TypeScript source unit should be processed.

Args:
    unit: Source unit to describe

Returns:
    SourceDescriptor with placeholder metadata

Raises:
    ValueError: If unit is not a TypeScript unit
- `discover_targets(self, repo_root, requested) -> list[SourceUnit]`: Discover TypeScript modules for documentation.

Args:
    repo_root: Root directory of the repository
    requested: Optional list of specific module paths to process

Returns:
    List of SourceUnit objects for TypeScript modules
- `generate(self, unit) -> list[DocVariant]`: Generate documentation variants for a TypeScript source unit (NOOP).

This is a placeholder implementation that skips actual documentation
generation. It returns placeholder variants marked as 'skipped' until
the AST-based doc generator is implemented.

Args:
    unit: Source unit to generate documentation for
    spec_dir: Specification directory to write documentation to
    check: If True, only check if docs would change

Returns:
    List of DocVariant objects with 'skipped' status

Raises:
    ValueError: If unit is not a TypeScript unit
- `supports_identifier(self, identifier) -> bool`: Check if this adapter can handle TypeScript identifiers.

Args:
    identifier: Source identifier to check

Returns:
    True if identifier looks like a TypeScript file path
