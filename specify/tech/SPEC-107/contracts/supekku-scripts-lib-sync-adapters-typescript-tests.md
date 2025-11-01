# supekku.scripts.lib.sync.adapters.typescript

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
- @staticmethod `_detect_package_manager(path) -> str`: Detect package manager from lockfile.

Walks up directory tree to find lockfile.
Priority: pnpm > bun > npm

Args:
    path: Starting path (file or directory)

Returns:
    Package manager name: 'pnpm', 'bun', or 'npm'
- `_discover_requested(self, repo_root, requested) -> list[SourceUnit]`: Discover specific requested modules.
- `_extract_ast(self, file_path, variant) -> dict`: Extract AST data from TypeScript/JavaScript file via ts-doc-extract.

Args:
    file_path: Path to .ts/.tsx/.js/.jsx file or directory with index file
    variant: 'public' or 'internal'

Returns:
    Parsed JSON from ts-doc-extract

Raises:
    TypeScriptExtractionError: If extraction fails
- `_find_logical_modules(self, package_root) -> list[Path]`: Find logical modules within a package.

A logical module is:
1. A directory with index.ts/index.tsx/index.js/index.jsx
2. A standalone significant .ts/.tsx/.js/.jsx file
3. A top-level src/ subdirectory with multiple files

Args:
    package_root: Package directory containing package.json

Returns:
    List of module paths (files or directories)
- `_find_package_root(self, file_path) -> Path`: Find nearest package.json directory.

Args:
    file_path: Starting file or directory path

Returns:
    Directory containing package.json

Raises:
    TypeScriptExtractionError: If no package.json found
- `_find_typescript_packages(self, repo_root) -> list[Path]`: Find all package.json directories containing TypeScript/JavaScript.

Args:
    repo_root: Repository root

Returns:
    List of package directories
- `_generate_markdown(self, ast_data, _variant) -> str`: Generate token-efficient markdown from AST data.

Format optimized for AI agents:
- Hierarchical structure
- Inline type signatures
- Comments preserved but condensed
- No redundancy

Args:
    ast_data: AST data from ts-doc-extract
    variant: 'api' or 'internal'

Returns:
    Generated markdown string
- `_get_npx_command(self, package_root) -> list[str]`: Get the appropriate npx command based on package manager.

Args:
    package_root: Package root directory

Returns:
    Command to run npx equivalent (pnpm dlx, bunx, or npx)
- `_should_skip_file(self, file_path) -> bool`: Check if a TypeScript/JavaScript file should be skipped.

Args:
    file_path: File path to check

Returns:
    True if file should be skipped

### TypeScriptExtractionError

Raised when ts-doc-extract fails to extract AST.

**Inherits from:** RuntimeError
