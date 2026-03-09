# supekku.scripts.lib.docs.python.analyzer

AST-based Python module analyzer.

## Classes

### DeterministicPythonModuleAnalyzer

Analyzes Python module AST to extract documentation information.

#### Methods

- `analyze(self) -> dict`: Analyze the Python file and extract documentation info with caching.
- `__init__(self, file_path, base_path, cache) -> None`
- `_analyze_assignment(self, node) -> list[dict]`: Analyze variable assignments.
- `_analyze_class(self, node) -> dict`: Analyze a class definition.
- `_analyze_function(self, node) -> dict`: Analyze a function definition.
- `_analyze_import(self, node) -> dict`: Analyze import statements.
- `_get_module_level_comments(self, tree) -> list[str]`: Get comments that appear before the first significant statement.
- `_get_name(self, node) -> str`: Get the name of an AST node with improved handling.
