"""Tests for TypeScript/JavaScript language adapter."""
# pylint: disable=protected-access

import json
import shutil
import unittest
from pathlib import Path
from subprocess import CalledProcessError
from unittest.mock import Mock, patch

import pytest

from supekku.scripts.lib.sync.models import SourceUnit

from .typescript import (
  NodeRuntimeNotAvailableError,
  TypeScriptAdapter,
  TypeScriptExtractionError,
)


class TestTypeScriptAdapter(unittest.TestCase):  # pylint: disable=too-many-public-methods
  """Test TypeScriptAdapter functionality."""

  def setUp(self) -> None:
    """Set up test fixtures."""
    self.repo_root = Path("/test/repo")
    self.adapter = TypeScriptAdapter(self.repo_root)

  def test_language_identifier(self) -> None:
    """Test that TypeScriptAdapter has correct language identifier."""
    assert TypeScriptAdapter.language == "typescript"
    assert self.adapter.language == "typescript"

  def test_is_node_available(self) -> None:
    """Test Node.js availability detection."""
    with patch("supekku.scripts.lib.sync.adapters.typescript.which") as mock_which:
      # Test Node.js available
      mock_which.return_value = "/usr/bin/node"
      assert TypeScriptAdapter.is_node_available()

      # Test Node.js not available
      mock_which.return_value = None
      assert not TypeScriptAdapter.is_node_available()

  def test_is_pnpm_available(self) -> None:
    """Test pnpm availability detection."""
    with patch("supekku.scripts.lib.sync.adapters.typescript.which") as mock_which:
      # Test pnpm available
      mock_which.return_value = "/usr/bin/pnpm"
      assert TypeScriptAdapter.is_pnpm_available()

      # Test pnpm not available
      mock_which.return_value = None
      assert not TypeScriptAdapter.is_pnpm_available()

  def test_is_bun_available(self) -> None:
    """Test bun availability detection."""
    with patch("supekku.scripts.lib.sync.adapters.typescript.which") as mock_which:
      # Test bun available
      mock_which.return_value = "/usr/bin/bun"
      assert TypeScriptAdapter.is_bun_available()

      # Test bun not available
      mock_which.return_value = None
      assert not TypeScriptAdapter.is_bun_available()

  def test_supports_identifier_valid_typescript(self) -> None:
    """Test supports_identifier returns True for valid TS/JS identifiers."""
    valid_identifiers = [
      "module.ts",
      "module.tsx",
      "module.js",
      "module.jsx",
      "module.mts",
      "module.mjs",
      "module.cjs",
      "src/components/Button.tsx",
      "src/lib/utils.ts",
      "src/db/client.js",
      "lib/helper.js",
      "components/Header.tsx",
      "app/page.tsx",
      "pages/index.js",
    ]

    for identifier in valid_identifiers:
      with self.subTest(identifier=identifier):
        msg = f"Should support TypeScript identifier: {identifier}"
        assert self.adapter.supports_identifier(identifier), msg

  def test_supports_identifier_invalid_identifiers(self) -> None:
    """Test supports_identifier returns False for non-TS/JS identifiers."""
    invalid_identifiers = [
      "",  # empty
      "module.py",  # Python file
      "file.go",  # Go file
      "script.java",  # Java file
      "file with spaces.ts",  # spaces
      "module\twith\ttabs.ts",  # tabs
      "module\nwith\nnewlines.ts",  # newlines
    ]

    for identifier in invalid_identifiers:
      with self.subTest(identifier=identifier):
        msg = f"Should not support identifier: {identifier}"
        assert not self.adapter.supports_identifier(identifier), msg

  def test_detect_package_manager_pnpm(self) -> None:
    """Test package manager detection finds pnpm."""
    test_dir = Path("/test/project/src")

    # Create a mock that returns True only for pnpm-lock.yaml
    with patch("pathlib.Path.exists", lambda self: "pnpm-lock.yaml" in str(self)):
      pm = TypeScriptAdapter._detect_package_manager(test_dir)
      assert pm == "pnpm"

  def test_detect_package_manager_bun(self) -> None:
    """Test package manager detection finds bun."""
    test_dir = Path("/test/project/src")

    # Create a mock that returns True only for bun.lockb
    with patch("pathlib.Path.exists", lambda self: "bun.lockb" in str(self)):
      pm = TypeScriptAdapter._detect_package_manager(test_dir)
      assert pm == "bun"

  def test_detect_package_manager_npm(self) -> None:
    """Test package manager detection finds npm."""
    test_dir = Path("/test/project/src")

    # Create a mock that returns True only for package-lock.json
    with patch("pathlib.Path.exists", lambda self: "package-lock.json" in str(self)):
      pm = TypeScriptAdapter._detect_package_manager(test_dir)
      assert pm == "npm"

  def test_detect_package_manager_defaults_to_npm(self) -> None:
    """Test package manager detection defaults to npm when no lockfile found."""
    test_dir = Path("/test/project/src")

    with patch.object(Path, "exists", return_value=False):
      pm = TypeScriptAdapter._detect_package_manager(test_dir)
      assert pm == "npm"

  def test_get_npx_command_pnpm(self) -> None:
    """Test npx command generation for pnpm."""
    package_root = Path("/test/project")

    with (
      patch.object(TypeScriptAdapter, "_detect_package_manager", return_value="pnpm"),
      patch.object(TypeScriptAdapter, "is_pnpm_available", return_value=True),
    ):
      cmd = self.adapter._get_npx_command(package_root)
      assert cmd == ["pnpm", "dlx"]

  def test_get_npx_command_bun(self) -> None:
    """Test npx command generation for bun."""
    package_root = Path("/test/project")

    with (
      patch.object(TypeScriptAdapter, "_detect_package_manager", return_value="bun"),
      patch.object(TypeScriptAdapter, "is_bun_available", return_value=True),
    ):
      cmd = self.adapter._get_npx_command(package_root)
      assert cmd == ["bunx"]

  def test_get_npx_command_npm(self) -> None:
    """Test npx command generation for npm."""
    package_root = Path("/test/project")

    with patch.object(TypeScriptAdapter, "_detect_package_manager", return_value="npm"):
      cmd = self.adapter._get_npx_command(package_root)
      assert cmd == ["npx"]

  def test_get_npx_command_fallback_to_npx(self) -> None:
    """Test npx command falls back to npx when package manager not available."""
    package_root = Path("/test/project")

    with (
      patch.object(TypeScriptAdapter, "_detect_package_manager", return_value="pnpm"),
      patch.object(TypeScriptAdapter, "is_pnpm_available", return_value=False),
    ):
      cmd = self.adapter._get_npx_command(package_root)
      assert cmd == ["npx"]

  def test_find_package_root_success(self) -> None:
    """Test finding package.json in parent directory."""
    test_file = Path("/test/project/src/components/Button.tsx")

    with (
      patch(
        "pathlib.Path.exists", lambda self: str(self) == "/test/project/package.json"
      ),
      patch(
        "pathlib.Path.is_dir",
        lambda self: self.is_absolute() and not str(self).endswith(".tsx"),
      ),
    ):
      package_root = self.adapter._find_package_root(test_file)
      assert package_root == Path("/test/project")

  def test_find_package_root_raises_when_not_found(self) -> None:
    """Test _find_package_root raises error when no package.json found."""
    test_file = Path("/test/project/src/file.ts")

    with (
      patch.object(Path, "exists", return_value=False),
      patch.object(Path, "is_dir", return_value=False),
      pytest.raises(TypeScriptExtractionError, match="No package.json found for"),
    ):
      self.adapter._find_package_root(test_file)

  def test_describe_typescript_module_file(self) -> None:
    """Test describe method for TypeScript file."""
    unit = SourceUnit("typescript", "src/db/client.ts", self.repo_root)
    descriptor = self.adapter.describe(unit)

    # Check slug parts (extension removed)
    assert descriptor.slug_parts == ["src", "db", "client"]

    # Check frontmatter
    assert "sources" in descriptor.default_frontmatter
    sources = descriptor.default_frontmatter["sources"]
    assert len(sources) == 1

    source = sources[0]
    assert source["language"] == "typescript"
    assert source["identifier"] == "src/db/client.ts"
    assert source["module"] == "src.db.client"

    # Check variants
    assert "variants" in source
    variants = source["variants"]
    assert len(variants) == 2

    variant_names = [v["name"] for v in variants]
    assert "api" in variant_names
    assert "internal" in variant_names

    # Check descriptor variants
    assert len(descriptor.variants) == 2
    descriptor_variant_names = [v.name for v in descriptor.variants]
    assert "api" in descriptor_variant_names
    assert "internal" in descriptor_variant_names

  def test_describe_typescript_module_directory(self) -> None:
    """Test describe method for TypeScript directory module."""
    unit = SourceUnit("typescript", "src/components", self.repo_root)
    descriptor = self.adapter.describe(unit)

    # Check slug parts
    assert descriptor.slug_parts == ["src", "components"]

    # Check module name
    source = descriptor.default_frontmatter["sources"][0]
    assert source["module"] == "src.components"

  def test_should_skip_file_test_files(self) -> None:
    """Test that test files are skipped."""
    test_files = [
      Path("/test/file.test.ts"),
      Path("/test/file.spec.ts"),
      Path("/test/test_file.ts"),
      Path("/test/file_test.ts"),
      Path("/test/Component.test.tsx"),
      Path("/test/utils.spec.js"),
    ]

    for test_file in test_files:
      with self.subTest(file=test_file):
        msg = f"Should skip test file: {test_file}"
        assert self.adapter._should_skip_file(test_file), msg

  def test_should_skip_file_build_dirs(self) -> None:
    """Test that files in build directories are skipped."""
    build_files = [
      Path("/test/dist/index.js"),
      Path("/test/build/app.js"),
      Path("/test/.next/static/chunks/main.js"),
      Path("/test/out/index.html"),
      Path("/test/node_modules/react/index.js"),
    ]

    for build_file in build_files:
      with self.subTest(file=build_file):
        msg = f"Should skip build file: {build_file}"
        assert self.adapter._should_skip_file(build_file), msg

  def test_extract_ast_success(self) -> None:
    """Test successful AST extraction."""
    test_file = Path("/test/project/src/index.ts")
    mock_ast_data = {
      "module": "index",
      "filePath": str(test_file),
      "exports": [
        {
          "kind": "function",
          "name": "greet",
          "signature": "function greet(name: string): string",
        }
      ],
      "imports": [],
      "metadata": {"hasDefaultExport": False, "exportCount": 1, "loc": 10},
    }

    with (
      patch.object(Path, "is_dir", return_value=False),
      patch.object(Path, "exists", return_value=True),
      patch.object(
        self.adapter, "_find_package_root", return_value=Path("/test/project")
      ),
      patch.object(self.adapter, "_get_npx_command", return_value=["npx"]),
      patch("subprocess.run") as mock_run,
    ):
      # Mock subprocess to return JSON
      mock_run.return_value = Mock(stdout=json.dumps(mock_ast_data))

      result = self.adapter._extract_ast(test_file, "public")

      assert result == mock_ast_data
      assert result["exports"][0]["name"] == "greet"

      # Verify subprocess was called correctly
      mock_run.assert_called_once()
      call_args = mock_run.call_args
      assert call_args[0][0][0] == "npx"
      assert "ts-doc-extract" in call_args[0][0]
      assert "--variant=public" in call_args[0][0]

  def test_extract_ast_directory_with_index(self) -> None:
    """Test AST extraction from directory finds index.ts."""
    test_dir = Path("/test/project/src/components")
    index_file = test_dir / "index.ts"

    with (
      patch("pathlib.Path.is_dir", lambda self: str(self) == str(test_dir)),
      patch(
        "pathlib.Path.exists",
        lambda self: str(self) == str(index_file) or "package.json" in str(self),
      ),
      patch.object(
        self.adapter, "_find_package_root", return_value=Path("/test/project")
      ),
      patch.object(self.adapter, "_get_npx_command", return_value=["npx"]),
      patch("subprocess.run") as mock_run,
    ):
      mock_run.return_value = Mock(stdout=json.dumps({"module": "components"}))

      self.adapter._extract_ast(test_dir, "public")

      # Verify it called with index.ts
      call_args = mock_run.call_args[0][0]
      assert str(index_file) in call_args

  def test_extract_ast_directory_no_index_raises_error(self) -> None:
    """Test AST extraction from directory without index file raises error."""
    test_dir = Path("/test/project/src/components")

    with (
      patch.object(Path, "is_dir", return_value=True),
      patch.object(Path, "exists", return_value=False),
      pytest.raises(TypeScriptExtractionError, match="No index file found"),
    ):
      self.adapter._extract_ast(test_dir, "public")

  def test_extract_ast_subprocess_error(self) -> None:
    """Test AST extraction handles subprocess errors."""
    test_file = Path("/test/project/src/index.ts")

    with (
      patch.object(Path, "is_dir", return_value=False),
      patch.object(Path, "exists", return_value=True),
      patch.object(
        self.adapter, "_find_package_root", return_value=Path("/test/project")
      ),
      patch.object(self.adapter, "_get_npx_command", return_value=["npx"]),
      patch("subprocess.run") as mock_run,
    ):
      # Mock subprocess failure
      mock_run.side_effect = CalledProcessError(
        1, ["npx"], stderr="ts-doc-extract failed"
      )

      with pytest.raises(TypeScriptExtractionError, match="ts-doc-extract failed"):
        self.adapter._extract_ast(test_file, "public")

  def test_extract_ast_invalid_json(self) -> None:
    """Test AST extraction handles invalid JSON output."""
    test_file = Path("/test/project/src/index.ts")

    with (
      patch.object(Path, "is_dir", return_value=False),
      patch.object(Path, "exists", return_value=True),
      patch.object(
        self.adapter, "_find_package_root", return_value=Path("/test/project")
      ),
      patch.object(self.adapter, "_get_npx_command", return_value=["npx"]),
      patch("subprocess.run") as mock_run,
    ):
      # Mock invalid JSON output
      mock_run.return_value = Mock(stdout="not valid json")

      with pytest.raises(TypeScriptExtractionError, match="Invalid JSON"):
        self.adapter._extract_ast(test_file, "public")

  def test_generate_markdown_simple(self) -> None:
    """Test markdown generation from AST data."""
    ast_data = {
      "module": "test.module",
      "exports": [
        {
          "kind": "const",
          "name": "API_URL",
          "signature": "const API_URL: string = 'https://api.example.com'",
          "leadingComments": [{"type": "single-line", "text": "// API endpoint"}],
          "jsDoc": None,
        },
        {
          "kind": "function",
          "name": "greet",
          "signature": "function greet(name: string): string",
          "parameters": [{"name": "name", "type": "string", "optional": False}],
          "returnType": "string",
          "isAsync": False,
          "jsDoc": {
            "description": "Greets a user",
            "tags": [{"name": "param", "text": "name - User name"}],
          },
          "leadingComments": [],
        },
      ],
    }

    markdown = self.adapter._generate_markdown(ast_data, "api")

    # Check module header
    assert "# test.module" in markdown

    # Check constants section
    assert "## Constants" in markdown
    assert "API_URL" in markdown

    # Check functions section
    assert "## Functions" in markdown
    assert "### greet" in markdown
    assert "greet(name: string): string" in markdown
    assert "Greets a user" in markdown
    assert "**Parameters:**" in markdown

  def test_generate_markdown_with_class(self) -> None:
    """Test markdown generation with class."""
    ast_data = {
      "module": "db.client",
      "exports": [
        {
          "kind": "class",
          "name": "DatabaseClient",
          "signature": "class DatabaseClient",
          "baseClass": None,
          "interfaces": ["IClient"],
          "members": [
            {
              "kind": "constructor",
              "name": "constructor",
              "signature": "constructor(url: string)",
              "visibility": "public",
              "isStatic": False,
              "jsDoc": {"description": "Create client"},
              "leadingComments": [],
            },
            {
              "kind": "property",
              "name": "url",
              "signature": "url: string",
              "visibility": "private",
              "isStatic": False,
              "leadingComments": [],
            },
            {
              "kind": "method",
              "name": "connect",
              "signature": "connect(): Promise<void>",
              "visibility": "public",
              "isStatic": False,
              "isAsync": True,
              "jsDoc": {"description": "Connect to database"},
              "leadingComments": [],
            },
          ],
          "jsDoc": {"description": "Database client class"},
          "leadingComments": [],
        }
      ],
    }

    markdown = self.adapter._generate_markdown(ast_data, "api")

    # Check class section
    assert "## Classes" in markdown
    assert "### DatabaseClient" in markdown
    assert "Database client class" in markdown
    assert "**Implements:** `IClient`" in markdown

    # Check members (constructor should not appear in properties/methods)
    assert "**Properties:**" in markdown
    assert "private `url: string`" in markdown
    assert "**Methods:**" in markdown
    assert "async `connect(): Promise<void>`" in markdown
    assert "Connect to database" in markdown

  def test_generate_requires_node_runtime(self) -> None:
    """Test generate raises error when Node.js not available."""
    unit = SourceUnit("typescript", "src/index.ts", self.repo_root)
    spec_dir = Path("/test/specs")

    with (
      patch.object(TypeScriptAdapter, "is_node_available", return_value=False),
      pytest.raises(NodeRuntimeNotAvailableError),
    ):
      self.adapter.generate(unit, spec_dir=spec_dir)

  def test_generate_validates_unit_language(self) -> None:
    """Test generate validates unit language."""
    unit = SourceUnit("python", "src/module.py", self.repo_root)
    spec_dir = Path("/test/specs")

    with (
      patch.object(TypeScriptAdapter, "is_node_available", return_value=True),
      pytest.raises(ValueError, match="cannot process"),
    ):
      self.adapter.generate(unit, spec_dir=spec_dir)

  def test_deduplicates_identical_variants(self) -> None:
    """Test that internal.md is removed when identical to api.md."""
    # Use /tmp for test files
    test_repo = Path("/tmp/test-dedup-repo")
    test_repo.mkdir(parents=True, exist_ok=True)

    unit = SourceUnit("typescript", "src/index.ts", test_repo)
    spec_dir = Path("/tmp/test-specs")
    contracts_dir = spec_dir / "contracts"
    contracts_dir.mkdir(parents=True, exist_ok=True)

    # Create source file path
    module_path = test_repo / "src/index.ts"
    module_path.parent.mkdir(parents=True, exist_ok=True)
    module_path.touch()

    # Mock AST data with only public exports (no private members)
    ast_data = {
      "module": "index",
      "filePath": str(module_path),
      "exports": [
        {
          "kind": "function",
          "name": "publicFunction",
          "signature": "publicFunction(): void",
          "isPrivate": False,
          "jsDoc": {},
          "leadingComments": [],
        }
      ],
    }

    # Create adapter with test repo
    test_adapter = TypeScriptAdapter(test_repo)

    try:
      with (
        patch.object(TypeScriptAdapter, "is_node_available", return_value=True),
        patch.object(TypeScriptAdapter, "_extract_ast", return_value=ast_data),
      ):
        variants = test_adapter.generate(unit, spec_dir=spec_dir)

        # Should only return api variant (internal was deduplicated)
        assert len(variants) == 1
        assert variants[0].name == "api"

        # api.md should exist
        assert (contracts_dir / "api.md").exists()

        # internal.md should NOT exist
        assert not (contracts_dir / "internal.md").exists()
    finally:
      # Cleanup
      if test_repo.exists():
        shutil.rmtree(test_repo)
      if spec_dir.exists():
        shutil.rmtree(spec_dir)
