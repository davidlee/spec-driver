# supekku.scripts.lib.sync.adapters.python

Python language adapter for specification synchronization.

## Classes

### PythonAdapter

Language adapter for Python modules using AST documentation workflow.

Uses the existing deterministic AST documentation system to generate
specification variants for Python source files.

**Inherits from:** LanguageAdapter

#### Methods

- `describe(self, unit) -> SourceDescriptor`: Describe how a Python module should be processed.

Args:
    unit: Python module source unit

Returns:
    SourceDescriptor with Python-specific metadata
- `discover_targets(self, repo_root, requested) -> list[SourceUnit]`: Discover Python modules for documentation.

Args:
    repo_root: Root directory of the repository
    requested: Optional list of specific module paths to process

Returns:
    List of SourceUnit objects for Python modules
- `generate(self, unit) -> list[DocVariant]`: Generate documentation for a Python module using AST analysis.

Args:
    unit: Python module source unit
    spec_dir: Specification directory to write documentation to
    check: If True, only check if docs would change

Returns:
    List of DocVariant objects with generation results
- `supports_identifier(self, identifier) -> bool`: Check if identifier looks like a Python module or file path.

Args:
    identifier: Identifier to check

Returns:
    True if identifier appears to be a Python module path
- `_should_skip_file(self, file_path) -> bool`: Check if a Python file should be skipped during discovery.

Args:
    file_path: Path to the Python file

Returns:
    True if the file should be skipped
