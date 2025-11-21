"""TypeScript/JavaScript language adapter using AST-based documentation.

This adapter uses ts-morph (via ts-doc-extract npm package) to generate
deterministic, token-efficient documentation from TypeScript and JavaScript source.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from shutil import which
from typing import TYPE_CHECKING, ClassVar

from rich.console import Console

from supekku.scripts.lib.core import (
  PackageManagerInfo,
  get_install_instructions,
  get_package_manager_info,
  is_npm_package_available,
)
from supekku.scripts.lib.sync.models import (
  DocVariant,
  SourceDescriptor,
  SourceUnit,
)

from .base import LanguageAdapter

if TYPE_CHECKING:
  from collections.abc import Sequence


class TypeScriptExtractionError(RuntimeError):
  """Raised when ts-doc-extract fails to extract AST."""


class NodeRuntimeNotAvailableError(RuntimeError):
  """Raised when Node.js runtime is required but not available."""


class TypeScriptAdapter(LanguageAdapter):
  """AST-based TypeScript/JavaScript adapter using ts-morph.

  Mirrors the Python adapter architecture:
  1. Discover logical modules (not just packages)
  2. Extract AST via ts-doc-extract (Node.js subprocess)
  3. Generate token-efficient markdown from AST JSON

  Supports: .ts, .tsx, .js, .jsx files
  Package managers: npm, pnpm, bun
  """

  language: ClassVar[str] = "typescript"

  def __init__(self, repo_root: Path) -> None:
    """Initialize TypeScriptAdapter with caching for npm_utils calls."""
    super().__init__(repo_root)
    self._pm_info: PackageManagerInfo | None = None
    self._ts_doc_extract_available: bool | None = None

  @staticmethod
  def is_node_available() -> bool:
    """Check if Node.js is available in PATH."""
    return which("node") is not None

  def discover_targets(
    self,
    repo_root: Path,
    requested: Sequence[str] | None = None,
  ) -> list[SourceUnit]:
    """Discover TypeScript/JavaScript modules.

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

    """
    if requested:
      return self._discover_requested(repo_root, requested)

    source_units = []

    # Find all TypeScript/JavaScript packages
    for package_root in self._find_typescript_packages(repo_root):
      # Find logical modules within this package
      for module_path in self._find_logical_modules(package_root):
        identifier = str(module_path.relative_to(repo_root))

        source_units.append(
          SourceUnit(
            language=self.language,
            identifier=identifier,
            root=repo_root,
          ),
        )

    return sorted(source_units, key=lambda u: u.identifier)

  def _discover_requested(
    self,
    repo_root: Path,
    requested: Sequence[str],
  ) -> list[SourceUnit]:
    """Discover specific requested modules."""
    source_units = []

    for identifier in requested:
      if not self.supports_identifier(identifier):
        continue

      # Convert identifier to path
      module_path = repo_root / identifier

      if module_path.exists():
        source_units.append(
          SourceUnit(
            language=self.language,
            identifier=identifier,
            root=repo_root,
          ),
        )

    return source_units

  def _find_typescript_packages(self, repo_root: Path) -> list[Path]:
    """Find all package.json directories containing TypeScript/JavaScript.

    Args:
        repo_root: Repository root

    Returns:
        List of package directories

    """
    packages = []

    for package_json in repo_root.glob("**/package.json"):
      package_dir = package_json.parent

      # Skip specific directories (not using _should_skip_path for directories)
      # because git only tracks files, not directories
      path_str = str(package_dir)
      skip_dirs = {
        "node_modules",
        ".next",
        "dist",
        "build",
        "out",
        ".git",
        "specify",
        "change",
      }

      if any(
        f"/{skip}/" in path_str or path_str.endswith(f"/{skip}") for skip in skip_dirs
      ):
        continue

      # Check if package contains TypeScript or JavaScript
      has_ts = (
        (package_dir / "tsconfig.json").exists()
        or any(package_dir.glob("**/*.ts"))
        or any(package_dir.glob("**/*.tsx"))
        or any(package_dir.glob("**/*.js"))
        or any(package_dir.glob("**/*.jsx"))
      )

      if has_ts:
        packages.append(package_dir)

    return packages

  def _find_logical_modules(self, package_root: Path) -> list[Path]:
    """Find logical modules within a package.

    A logical module is:
    1. A directory with index.ts/index.tsx/index.js/index.jsx
    2. A standalone significant .ts/.tsx/.js/.jsx file
    3. A top-level src/ subdirectory with multiple files

    Args:
        package_root: Package directory containing package.json

    Returns:
        List of module paths (files or directories)

    """
    modules = []
    src_dir = package_root / "src"

    if not src_dir.exists():
      # No src/ directory - look for top-level TS/JS files
      for pattern in ["*.ts", "*.tsx", "*.js", "*.jsx"]:
        for file in package_root.glob(pattern):
          if not self._should_skip_file(file):
            modules.append(file)
      return modules

    # Find directories with index files
    indexed_dirs = set()
    for pattern in ["**/index.ts", "**/index.tsx", "**/index.js", "**/index.jsx"]:
      for index_file in src_dir.glob(pattern):
        module_dir = index_file.parent
        if not self._should_skip_path(module_dir):
          modules.append(module_dir)
          indexed_dirs.add(module_dir)

    # Find significant standalone files (not in indexed directories)
    for pattern in ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx"]:
      for file in src_dir.glob(pattern):
        if self._should_skip_file(file):
          continue

        # Skip if file is in an indexed directory
        if any(file.is_relative_to(d) for d in indexed_dirs):
          continue

        # Skip index files themselves
        if file.stem == "index":
          continue

        # Check if this is a "significant" file
        # Heuristic: files in top 2 levels of src/ or in important directories
        try:
          rel_path = file.relative_to(src_dir)
          depth = len(rel_path.parents) - 1
          important_dirs = {"lib", "utils", "db", "api", "services", "components"}

          is_significant = (
            depth <= 1  # Top 2 levels
            or any(part in important_dirs for part in rel_path.parts)
          )

          if is_significant:
            modules.append(file)
        except ValueError:
          continue

    return modules

  def _should_skip_file(self, file_path: Path) -> bool:
    """Check if a TypeScript/JavaScript file should be skipped.

    Args:
        file_path: File path to check

    Returns:
        True if file should be skipped

    """
    # Use base adapter checks
    if self._should_skip_path(file_path):
      return True

    # Skip test files
    filename_lower = file_path.name.lower()
    # pylint: disable=too-many-boolean-expressions
    if (
      ".test." in filename_lower
      or ".spec." in filename_lower
      or filename_lower.startswith("test_")
      or filename_lower.endswith("_test.ts")
      or filename_lower.endswith("_test.js")
      or filename_lower.endswith("_test.tsx")
      or filename_lower.endswith("_test.jsx")
    ):
      return True

    # Skip build/dist directories
    skip_dirs = {"dist", "build", ".next", "out", "node_modules"}
    return any(part in skip_dirs for part in file_path.parts)

  def _ensure_ts_doc_extract_available(self, package_root: Path | None = None) -> bool:
    """Check if ts-doc-extract is available (local or global), with caching.

    Checks for ts-doc-extract in node_modules/.bin (if package_root provided)
    and in global PATH. Caches result per adapter instance to avoid repeated
    subprocess calls.

    Args:
        package_root: Package root to check for local installation (optional)

    Returns:
        True if ts-doc-extract is available, False otherwise

    """
    if self._ts_doc_extract_available is not None:
      return self._ts_doc_extract_available

    self._ts_doc_extract_available = is_npm_package_available(
      "ts-doc-extract", package_root
    )
    return self._ts_doc_extract_available

  def _get_npx_command(self, package_root: Path) -> list[str]:
    """Get the appropriate npx command based on package manager.

    Uses npm_utils to detect package manager and build command with --yes flags
    to prevent interactive install prompts. Caches PackageManagerInfo per adapter
    instance to avoid repeated subprocess calls.

    Args:
        package_root: Package root directory

    Returns:
        Command to run npx equivalent (pnpm dlx, bunx, or npx) with --yes flags

    """
    if self._pm_info is None:
      self._pm_info = get_package_manager_info(package_root)

    return self._pm_info.build_npx_command("ts-doc-extract")

  def _find_package_root(self, file_path: Path) -> Path:
    """Find nearest package.json directory.

    Args:
        file_path: Starting file or directory path

    Returns:
        Directory containing package.json

    Raises:
        TypeScriptExtractionError: If no package.json found

    """
    current = file_path if file_path.is_dir() else file_path.parent

    while current != current.parent:
      if (current / "package.json").exists():
        return current
      current = current.parent

    msg = f"No package.json found for: {file_path}"
    raise TypeScriptExtractionError(msg)

  def _extract_ast(self, file_path: Path, variant: str = "public") -> dict:
    """Extract AST data from TypeScript/JavaScript file via ts-doc-extract.

    Args:
        file_path: Path to .ts/.tsx/.js/.jsx file or directory with index file
        variant: 'public' or 'internal'

    Returns:
        Parsed JSON from ts-doc-extract

    Raises:
        TypeScriptExtractionError: If extraction fails

    """
    # Determine actual file to extract
    if file_path.is_dir():
      # Look for index file
      for name in ["index.ts", "index.tsx", "index.js", "index.jsx"]:
        index_file = file_path / name
        if index_file.exists():
          file_path = index_file
          break
      else:
        msg = f"No index file found in directory: {file_path}"
        raise TypeScriptExtractionError(msg)

    # Get package root and npx command
    try:
      package_root = self._find_package_root(file_path)
    except TypeScriptExtractionError:
      # If no package.json, use parent directory
      package_root = file_path.parent

    npx_cmd = self._get_npx_command(package_root)

    # Build command
    cmd = [
      *npx_cmd,
      "ts-doc-extract",
      str(file_path),
      f"--variant={variant}",
    ]

    try:
      result = subprocess.run(
        cmd,
        cwd=package_root,
        capture_output=True,
        text=True,
        timeout=30,
        check=True,
      )

      return json.loads(result.stdout)

    except subprocess.CalledProcessError as e:
      msg = f"ts-doc-extract failed: {e.stderr}"
      raise TypeScriptExtractionError(msg) from e
    except json.JSONDecodeError as e:
      msg = f"Invalid JSON from ts-doc-extract: {e}"
      raise TypeScriptExtractionError(msg) from e
    except subprocess.TimeoutExpired as e:
      msg = f"ts-doc-extract timed out after 30s: {file_path}"
      raise TypeScriptExtractionError(msg) from e

  def describe(self, unit: SourceUnit) -> SourceDescriptor:
    """Describe how a TypeScript/JavaScript module should be processed.

    Args:
        unit: TypeScript/JavaScript module source unit

    Returns:
        SourceDescriptor with TypeScript-specific metadata

    """
    self._validate_unit_language(unit)

    # Generate slug from module path
    module_path = Path(unit.identifier)

    # Remove extension if it's a file
    if module_path.suffix in {".ts", ".tsx", ".js", ".jsx"}:
      module_path = module_path.with_suffix("")

    slug_parts = list(module_path.parts)

    # Generate module name for frontmatter (dotted notation)
    module_name = ".".join(slug_parts)

    default_frontmatter = {
      "sources": [
        {
          "language": "typescript",
          "identifier": unit.identifier,
          "module": module_name,
          "variants": [
            {"name": "api", "path": "contracts/api.md"},
            {"name": "internal", "path": "contracts/internal.md"},
          ],
        },
      ],
    }

    variants = [
      DocVariant(
        name="api",
        path=Path("contracts/api.md"),
        hash="",
        status="unchanged",
      ),
      DocVariant(
        name="internal",
        path=Path("contracts/internal.md"),
        hash="",
        status="unchanged",
      ),
    ]

    return SourceDescriptor(
      slug_parts=slug_parts,
      default_frontmatter=default_frontmatter,
      variants=variants,
    )

  def generate(
    self,
    unit: SourceUnit,
    *,
    spec_dir: Path,
    check: bool = False,
  ) -> list[DocVariant]:
    """Generate documentation for a TypeScript/JavaScript module.

    Args:
        unit: TypeScript/JavaScript module source unit
        spec_dir: Specification directory to write documentation to
        check: If True, only check if docs would change

    Returns:
        List of DocVariant objects with generation results

    Raises:
        NodeRuntimeNotAvailableError: If Node.js is not available

    """
    self._validate_unit_language(unit)

    # Check if Node.js is available
    if not self.is_node_available():
      raise NodeRuntimeNotAvailableError(
        "Node.js runtime not found in PATH. Please install Node.js from "
        "https://nodejs.org/ or ensure it is in your PATH."
      )

    # Convert unit to absolute path
    module_path = self.repo_root / unit.identifier

    # Find package root for this module to check ts-doc-extract availability
    try:
      package_root = self._find_package_root(module_path)
    except ValueError:
      # No package.json found, use None for global-only check
      package_root = None

    # Check if ts-doc-extract is available (pre-flight validation per DEC-019-002)
    if not self._ensure_ts_doc_extract_available(package_root):
      # Get package manager info for install instructions
      pm_info = get_package_manager_info(package_root) if package_root else None
      instructions = get_install_instructions("ts-doc-extract", pm_info)

      console = Console(stderr=True)
      console.print(
        f"[yellow]Warning:[/yellow] ts-doc-extract not found. "
        f"Skipping TypeScript contract generation.\n\n{instructions}",
        style="dim",
      )

      # Skip gracefully - return empty list (per DEC-019-004)
      return []

    if not module_path.exists():
      # Return error variants
      return [
        DocVariant(
          name="api",
          path=Path("contracts/api.md"),
          hash="",
          status="unchanged",
        ),
        DocVariant(
          name="internal",
          path=Path("contracts/internal.md"),
          hash="",
          status="unchanged",
        ),
      ]

    # Map variant names
    variant_mapping = {
      "api": "public",  # Our 'api' maps to ts-doc-extract's 'public'
      "internal": "internal",
    }

    output_root = spec_dir / "contracts"
    doc_variants = []

    for our_variant, ts_variant in variant_mapping.items():
      try:
        # Extract AST
        ast_data = self._extract_ast(module_path, ts_variant)

        # Generate markdown
        markdown = self._generate_markdown(ast_data, our_variant)

        # Calculate output path
        output_file = output_root / f"{our_variant}.md"

        # Calculate hash
        content_hash = hashlib.sha256(markdown.encode("utf-8")).hexdigest()

        # Write file (unless check mode)
        if check:
          # Check if file exists and content matches
          if output_file.exists():
            with open(output_file, encoding="utf-8") as f:
              existing = f.read()
            existing_hash = hashlib.sha256(existing.encode("utf-8")).hexdigest()
            status = "unchanged" if existing_hash == content_hash else "error"
          else:
            status = "error"  # Missing file in check mode
        else:
          # Write mode
          status = "unchanged"
          if output_file.exists():
            with open(output_file, encoding="utf-8") as f:
              existing = f.read()
            existing_hash = hashlib.sha256(existing.encode("utf-8")).hexdigest()
            if existing_hash != content_hash:
              status = "changed"
          else:
            status = "created"

          # Write file
          output_file.parent.mkdir(parents=True, exist_ok=True)
          with open(output_file, "w", encoding="utf-8") as f:
            f.write(markdown)

        doc_variants.append(
          DocVariant(
            name=our_variant,
            path=output_file.relative_to(spec_dir),
            hash=content_hash,
            status=status,
          ),
        )

      except TypeScriptExtractionError:
        # Return error variant
        doc_variants.append(
          DocVariant(
            name=our_variant,
            path=Path(f"contracts/{our_variant}.md"),
            hash="",
            status="unchanged",
          ),
        )

    # If both variants exist and are identical, remove internal.md
    if (
      not check
      and len(doc_variants) == 2
      and doc_variants[0].hash
      and doc_variants[0].hash == doc_variants[1].hash
    ):
      internal_file = output_root / "internal.md"
      if internal_file.exists():
        internal_file.unlink()
      # Remove internal variant from list
      doc_variants = [v for v in doc_variants if v.name != "internal"]

    return doc_variants

  def _generate_markdown(self, ast_data: dict, _variant: str) -> str:
    """Generate token-efficient markdown from AST data.

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

    """
    lines = []

    # Module header
    lines.append(f"# {ast_data['module']}")
    lines.append("")

    exports = ast_data.get("exports", [])

    # Group by kind
    types = [e for e in exports if e["kind"] in ("type", "interface")]
    constants = [e for e in exports if e["kind"] == "const"]
    functions = [e for e in exports if e["kind"] == "function"]
    classes = [e for e in exports if e["kind"] == "class"]
    enums = [e for e in exports if e["kind"] == "enum"]

    # Types & Interfaces
    if types:
      lines.append("## Types")
      lines.append("")
      for t in types:
        lines.append(f"### {t['name']}")
        lines.append("")
        lines.append("```typescript")
        lines.append(t["signature"])
        lines.append("```")

        # JSDoc description
        if t.get("jsDoc", {}).get("description"):
          lines.append("")
          lines.append(t["jsDoc"]["description"])

        # Non-JSDoc comments
        non_jsdoc = [c for c in t.get("leadingComments", []) if c["type"] != "jsdoc"]
        if non_jsdoc:
          lines.append("")
          for comment in non_jsdoc:
            # Clean comment text (remove // or /* */)
            text = comment["text"].strip()
            if text.startswith("//"):
              text = text[2:].strip()
            elif text.startswith("/*") and text.endswith("*/"):
              text = text[2:-2].strip()
            lines.append(f"*{text}*")

        lines.append("")

    # Constants
    if constants:
      lines.append("## Constants")
      lines.append("")
      for const in constants:
        sig = const["signature"]
        jsdoc = const.get("jsDoc") or {}
        doc = jsdoc.get("description", "")
        comment = ""
        if const.get("leadingComments"):
          text = const["leadingComments"][0]["text"].strip()
          if text.startswith("//"):
            comment = text[2:].strip()
          elif text.startswith("/*") and text.endswith("*/"):
            comment = text[2:-2].strip()

        if doc:
          lines.append(f"- `{sig}` - {doc}")
        elif comment:
          lines.append(f"- `{sig}` - {comment}")
        else:
          lines.append(f"- `{sig}`")
      lines.append("")

    # Functions
    if functions:
      lines.append("## Functions")
      lines.append("")
      for func in functions:
        lines.append(f"### {func['name']}")
        lines.append("")

        # Build signature
        params = ", ".join(
          f"{p['name']}: {p.get('type', 'any')}" for p in func.get("parameters", [])
        )
        ret = func.get("returnType", "void")
        sig = f"{func['name']}({params}): {ret}"

        lines.append("```typescript")
        if func.get("isAsync"):
          lines.append(f"async {sig}")
        else:
          lines.append(sig)
        lines.append("```")

        # JSDoc
        if func.get("jsDoc"):
          jsdoc = func["jsDoc"]
          if jsdoc.get("description"):
            lines.append("")
            lines.append(jsdoc["description"])

          # Parameters
          param_tags = [t for t in jsdoc.get("tags", []) if t["name"] == "param"]
          if param_tags:
            lines.append("")
            lines.append("**Parameters:**")
            for tag in param_tags:
              lines.append(f"- {tag['text']}")

          # Returns
          returns_tags = [t for t in jsdoc.get("tags", []) if t["name"] == "returns"]
          if returns_tags:
            lines.append("")
            lines.append(f"**Returns:** {returns_tags[0]['text']}")

        lines.append("")

    # Classes
    # pylint: disable=too-many-nested-blocks
    if classes:
      lines.append("## Classes")
      lines.append("")

      for cls in classes:
        lines.append(f"### {cls['name']}")
        lines.append("")

        # Base class / interfaces
        if cls.get("baseClass"):
          lines.append(f"**Extends:** `{cls['baseClass']}`")
          lines.append("")
        if cls.get("interfaces"):
          lines.append(
            f"**Implements:** {', '.join(f'`{i}`' for i in cls['interfaces'])}"
          )
          lines.append("")

        # JSDoc
        if cls.get("jsDoc", {}).get("description"):
          lines.append(cls["jsDoc"]["description"])
          lines.append("")

        # Members
        if cls.get("members"):
          # Properties
          props = [m for m in cls["members"] if m["kind"] == "property"]
          if props:
            lines.append("**Properties:**")
            for prop in props:
              vis = f"{prop['visibility']} " if prop["visibility"] != "public" else ""
              static = "static " if prop.get("isStatic") else ""
              lines.append(f"- {vis}{static}`{prop['signature']}`")
            lines.append("")

          # Methods
          methods = [m for m in cls["members"] if m["kind"] == "method"]
          if methods:
            lines.append("**Methods:**")
            for method in methods:
              vis = (
                f"{method['visibility']} " if method["visibility"] != "public" else ""
              )
              static = "static " if method.get("isStatic") else ""
              async_kw = "async " if method.get("isAsync") else ""

              # Description from JSDoc
              desc = method.get("jsDoc", {}).get("description", "")

              if desc:
                lines.append(
                  f"- {vis}{static}{async_kw}`{method['signature']}` - {desc}"
                )
              else:
                lines.append(f"- {vis}{static}{async_kw}`{method['signature']}`")
            lines.append("")

        lines.append("")

    # Enums
    if enums:
      lines.append("## Enums")
      lines.append("")
      for enum in enums:
        lines.append(f"### {enum['name']}")
        lines.append("")
        for val in enum.get("enumValues", []):
          lines.append(f"- `{val['name']}` = `{val['value']}`")
        lines.append("")

    return "\n".join(lines)

  def supports_identifier(self, identifier: str) -> bool:
    """Check if identifier looks like a TypeScript/JavaScript module.

    Args:
        identifier: Identifier to check

    Returns:
        True if identifier appears to be a TypeScript/JavaScript path

    """
    if not identifier:
      return False

    # Basic sanity checks
    if " " in identifier or "\n" in identifier or "\t" in identifier:
      return False

    # TypeScript/JavaScript files
    if any(
      identifier.endswith(ext)
      for ext in [".ts", ".tsx", ".js", ".jsx", ".mts", ".mjs", ".cjs"]
    ):
      return True

    # Exclude non-TS/JS extensions
    non_ts_extensions = [".py", ".go", ".java", ".cpp", ".c", ".h"]
    if any(identifier.endswith(ext) for ext in non_ts_extensions):
      return False

    # Common TS/JS directory patterns
    ts_patterns = [
      "src/",
      "lib/",
      "components/",
      "pages/",
      "app/",
    ]

    if any(identifier.startswith(pattern) for pattern in ts_patterns):
      return True

    # Simple paths that could be TS/JS
    return all(c.isalnum() or c in "/-_." for c in identifier)
