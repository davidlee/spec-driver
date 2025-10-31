# supekku.scripts.lib.spec_sync.adapters.typescript

TypeScript/JavaScript language adapter using AST-based documentation.

This adapter uses ts-morph (via ts-doc-extract npm package) to generate
deterministic, token-efficient documentation from TypeScript and JavaScript source.

## Classes

### NodeRuntimeNotAvailableError

Raised when Node.js runtime is required but not available.

**Inherits from:** RuntimeError

### TypeScriptAdapter

AST-based TypeScript/JavaScript adapter using ts-morph.

Mirrors the Python adapter architecture:
1. Discover logical modules (not just packages)
2. Extract AST via ts-doc-extract (Node.js subprocess)
3. Generate token-efficient markdown from AST JSON

Supports: .ts, .tsx, .js, .jsx files
Package managers: npm, pnpm, bun

**Inherits from:** LanguageAdapter

#### Methods

- `describe(self, unit) -> SourceDescriptor`: Describe how a TypeScript/JavaScript module should be processed.

Args:
    unit: TypeScript/JavaScript module source unit

Returns:
    SourceDescriptor with TypeScript-specific metadata
- `discover_targets(self, repo_root, requested) -> list[SourceUnit]`: Discover TypeScript/JavaScript modules.

Strategy:
1. Find all TypeScript/JavaScript packages (package.json with TS/JS)
2. Within each package, find logical modules:
   - Directories with index.ts/index.js
   - Standalone significant .ts/.js files
   - Top-level src/ subdirectories

Args:
    repo_root: Repository root directory
    requested: Optional list of specific modules to process

Returns:
    List of SourceUnit objects for each logical module
- `generate(self, unit) -> list[DocVariant]`: Generate documentation for a TypeScript/JavaScript module.

Args:
    unit: TypeScript/JavaScript module source unit
    spec_dir: Specification directory to write documentation to
    check: If True, only check if docs would change

Returns:
    List of DocVariant objects with generation results

Raises:
    NodeRuntimeNotAvailableError: If Node.js is not available
- @staticmethod `is_bun_available() -> bool`: Check if bun is available in PATH.
- @staticmethod `is_node_available() -> bool`: Check if Node.js is available in PATH.
- @staticmethod `is_pnpm_available() -> bool`: Check if pnpm is available in PATH.
- `supports_identifier(self, identifier) -> bool`: Check if identifier looks like a TypeScript/JavaScript module.

Args:
    identifier: Identifier to check

Returns:
    True if identifier appears to be a TypeScript/JavaScript path

### TypeScriptExtractionError

Raised when ts-doc-extract fails to extract AST.

**Inherits from:** RuntimeError
