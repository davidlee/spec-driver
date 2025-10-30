"""AST-based Python module analyzer."""

import ast
from pathlib import Path

from .cache import ParseCache
from .comments import CommentExtractor
from .path_utils import PathNormalizer


class DeterministicPythonModuleAnalyzer:
  def __init__(
    self,
    file_path: Path,
    base_path: Path | None = None,
    cache: ParseCache | None = None,
  ) -> None:
    self.file_path = file_path
    self.base_path = base_path
    self.cache = cache
    self.module_name = PathNormalizer.get_module_name(file_path, base_path)

    with open(self.file_path, encoding="utf-8") as f:
      self.source_code = f.read()

    self.comment_extractor = CommentExtractor(self.source_code)

  def analyze(self) -> dict:
    """Analyze the Python file and extract documentation info with caching."""
    # Try cache first
    if self.cache:
      cached_result = self.cache.get(self.file_path)
      if cached_result is not None:
        return cached_result

    # Perform analysis
    try:
      tree = ast.parse(self.source_code)
    except SyntaxError as e:
      return {"error": f"Syntax error in {self.file_path}: {e}"}
      # Don't cache error results

    analysis = {
      "module_name": self.module_name,
      "file_path": PathNormalizer.normalize_path_for_id(
        self.file_path,
        self.base_path,
      ),
      "docstring": ast.get_docstring(tree),
      "classes": [],
      "functions": [],
      "constants": [],
      "imports": [],
      "module_comments": self._get_module_level_comments(tree),
    }

    # Collect all elements
    for node in ast.walk(tree):
      if isinstance(node, ast.ClassDef):
        analysis["classes"].append(self._analyze_class(node))
      elif (
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.col_offset == 0
      ):
        analysis["functions"].append(self._analyze_function(node))
      elif isinstance(node, ast.Assign) and node.col_offset == 0:
        analysis["constants"].extend(self._analyze_assignment(node))
      elif isinstance(node, (ast.Import, ast.ImportFrom)):
        analysis["imports"].append(self._analyze_import(node))

    # DETERMINISTIC SORTING: Sort all elements by name for consistent output
    analysis["classes"].sort(key=lambda x: x["name"])
    analysis["functions"].sort(key=lambda x: x["name"])
    analysis["constants"].sort(key=lambda x: x["name"])
    analysis["imports"].sort(
      key=lambda x: (x.get("module", ""), str(x.get("names", []))),
    )

    # Sort methods within each class
    for class_info in analysis["classes"]:
      class_info["methods"].sort(key=lambda x: (x["is_private"], x["name"]))

    # Cache successful analysis
    if self.cache:
      self.cache.put(self.file_path, analysis)

    return analysis

  def _get_module_level_comments(self, tree: ast.AST) -> list[str]:
    """Get comments that appear before the first significant statement."""
    comments = []
    first_stmt_line = None

    # Find the first significant statement
    for node in ast.walk(tree):
      if isinstance(
        node,
        (
          ast.ClassDef,
          ast.FunctionDef,
          ast.AsyncFunctionDef,
          ast.Import,
          ast.ImportFrom,
          ast.Assign,
        ),
      ) and (first_stmt_line is None or node.lineno < first_stmt_line):
        first_stmt_line = node.lineno

    # Collect comments before first statement
    for line_num, comment in sorted(self.comment_extractor.comments.items()):
      if first_stmt_line is None or line_num < first_stmt_line:
        comments.append(comment)

    return comments

  def _analyze_class(self, node: ast.ClassDef) -> dict:
    """Analyze a class definition."""
    methods = []
    for item in node.body:
      if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
        methods.append(self._analyze_function(item))

    comment = self.comment_extractor.get_comment_for_line(node.lineno)

    return {
      "name": node.name,
      "docstring": ast.get_docstring(node),
      "comment": comment,
      "bases": sorted([self._get_name(base) for base in node.bases]),  # Sorted
      "decorators": sorted(
        [self._get_name(dec) for dec in node.decorator_list],
      ),  # Sorted
      "methods": methods,  # Will be sorted later
      "is_private": node.name.startswith("_"),
      "line_number": node.lineno,
    }

  def _analyze_function(self, node: ast.FunctionDef) -> dict:
    """Analyze a function definition."""
    args_info = []
    for arg in node.args.args:
      arg_info = {"name": arg.arg}
      if arg.annotation:
        arg_info["type"] = self._get_name(arg.annotation)
      args_info.append(arg_info)

    return_type = None
    if node.returns:
      return_type = self._get_name(node.returns)

    comment = self.comment_extractor.get_comment_for_line(node.lineno)

    return {
      "name": node.name,
      "docstring": ast.get_docstring(node),
      "comment": comment,
      "args": [arg.arg for arg in node.args.args],
      "args_detailed": args_info,
      "return_type": return_type,
      "decorators": sorted(
        [self._get_name(dec) for dec in node.decorator_list],
      ),  # Sorted
      "is_private": node.name.startswith("_"),
      "is_async": isinstance(node, ast.AsyncFunctionDef),
      "is_property": any(
        "property" in self._get_name(dec) for dec in node.decorator_list
      ),
      "is_classmethod": any(
        "classmethod" in self._get_name(dec) for dec in node.decorator_list
      ),
      "is_staticmethod": any(
        "staticmethod" in self._get_name(dec) for dec in node.decorator_list
      ),
      "line_number": node.lineno,
    }

  def _analyze_assignment(self, node: ast.Assign) -> list[dict]:
    """Analyze variable assignments."""
    variables = []
    comment = self.comment_extractor.get_comment_for_line(node.lineno)

    for target in node.targets:
      if isinstance(target, ast.Name):
        # Handle type annotations
        type_annotation = None
        if isinstance(node, ast.AnnAssign) and node.annotation:
          type_annotation = self._get_name(node.annotation)

        variables.append(
          {
            "name": target.id,
            "type": type_annotation,
            "comment": comment,
            "is_private": target.id.startswith("_"),
            "line_number": node.lineno,
          },
        )

    return variables

  def _analyze_import(self, node) -> dict:
    """Analyze import statements."""
    if isinstance(node, ast.Import):
      return {
        "type": "import",
        "names": sorted([alias.name for alias in node.names]),  # Sorted
        "line_number": node.lineno,
      }
    if isinstance(node, ast.ImportFrom):
      return {
        "type": "from_import",
        "module": node.module,
        "names": sorted([alias.name for alias in node.names]),  # Sorted
        "line_number": node.lineno,
      }
    return None

  def _get_name(self, node) -> str:
    """Get the name of an AST node with improved handling."""
    if isinstance(node, ast.Name):
      return node.id
    if isinstance(node, ast.Attribute):
      return f"{self._get_name(node.value)}.{node.attr}"
    if isinstance(node, ast.Constant):
      return str(node.value)
    if isinstance(node, ast.Subscript):
      return f"{self._get_name(node.value)}[{self._get_name(node.slice)}]"
    if isinstance(node, ast.Tuple):
      # Handle tuple type annotations like Tuple[str, int]
      elts = [self._get_name(elt) for elt in node.elts]
      return f"Tuple[{', '.join(elts)}]"
    if isinstance(node, ast.List):
      # Handle list type annotations
      elts = [self._get_name(elt) for elt in node.elts]
      return f"List[{', '.join(elts)}]"
    if isinstance(node, ast.Call):
      # Handle complex decorator calls like @property, @staticmethod, etc.
      func_name = self._get_name(node.func)
      if node.args or node.keywords:
        # For decorators with arguments, include them
        args = [self._get_name(arg) for arg in node.args]
        kwargs = [f"{kw.arg}={self._get_name(kw.value)}" for kw in node.keywords]
        all_args = args + kwargs
        return f"{func_name}({', '.join(all_args)})"
      return func_name
    if hasattr(node, "__class__"):
      # For any other AST node, use the class name instead of object reference
      return f"<{node.__class__.__name__}>"
    return "Unknown"
