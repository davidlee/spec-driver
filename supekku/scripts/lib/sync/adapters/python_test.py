"""Tests for Python language adapter."""

import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from supekku.scripts.lib.sync.models import SourceUnit

from .python import PythonAdapter


class TestPythonAdapter(unittest.TestCase):
  """Test PythonAdapter functionality."""

  def setUp(self) -> None:
    """Set up test fixtures."""
    self.repo_root = Path("/test/repo")
    self.adapter = PythonAdapter(self.repo_root)

  def test_language_identifier(self) -> None:
    """Test that PythonAdapter has correct language identifier."""
    assert PythonAdapter.language == "python"
    assert self.adapter.language == "python"

  def test_supports_identifier_valid_python_modules(self) -> None:
    """Test supports_identifier returns True for valid Python identifiers."""
    valid_identifiers = [
      "module.py",
      "supekku/scripts/lib/workspace.py",
      "test/test_module.py",
      "package/__init__.py",
      "supekku.scripts.lib.workspace",  # dotted module
      "lib/utils.py",
      "scripts/helper.py",
    ]

    for identifier in valid_identifiers:
      with self.subTest(identifier=identifier):
        msg = f"Should support Python identifier: {identifier}"
        assert self.adapter.supports_identifier(identifier), msg

  def test_supports_identifier_invalid_identifiers(self) -> None:
    """Test supports_identifier returns False for non-Python identifiers."""
    invalid_identifiers = [
      "",  # empty
      "cmd/vice",  # Go-style command
      "internal/application/pipeline",  # Go-style internal package
      "file with spaces.py",  # spaces
      "module\twith\ttabs.py",  # tabs
      "module\nwith\nnewlines.py",  # newlines
      "file.go",  # Go file
      "script.js",  # JavaScript file
    ]

    for identifier in invalid_identifiers:
      with self.subTest(identifier=identifier):
        msg = f"Should not support identifier: {identifier}"
        assert not self.adapter.supports_identifier(identifier), msg

  def test_describe_python_module(self) -> None:
    """Test describe method generates correct metadata for Python modules."""
    unit = SourceUnit("python", "supekku/scripts/lib/workspace.py", self.repo_root)
    descriptor = self.adapter.describe(unit)

    # Check slug parts
    assert descriptor.slug_parts == ["supekku", "scripts", "lib", "workspace"]

    # Check frontmatter structure
    assert "sources" in descriptor.default_frontmatter
    sources = descriptor.default_frontmatter["sources"]
    assert len(sources) == 1

    source = sources[0]
    assert source["language"] == "python"
    assert source["identifier"] == "supekku/scripts/lib/workspace.py"
    assert source["module"] == "supekku.scripts.lib.workspace"

    # Check variants in frontmatter
    assert "variants" in source
    variants = source["variants"]
    assert len(variants) == 3

    variant_names = [v["name"] for v in variants]
    assert "api" in variant_names
    assert "implementation" in variant_names
    assert "tests" in variant_names

    # Check descriptor variants
    assert len(descriptor.variants) == 3
    descriptor_variant_names = [v.name for v in descriptor.variants]
    assert "api" in descriptor_variant_names
    assert "implementation" in descriptor_variant_names
    assert "tests" in descriptor_variant_names

    # Check variant paths
    api_variant = next(v for v in descriptor.variants if v.name == "api")
    impl_variant = next(v for v in descriptor.variants if v.name == "implementation")
    tests_variant = next(v for v in descriptor.variants if v.name == "tests")

    assert api_variant.path == Path("contracts/api.md")
    assert impl_variant.path == Path("contracts/implementation.md")
    assert tests_variant.path == Path("contracts/tests.md")

  def test_describe_python_package_init(self) -> None:
    """Test describe method handles __init__.py files correctly."""
    unit = SourceUnit("python", "supekku/scripts/__init__.py", self.repo_root)
    descriptor = self.adapter.describe(unit)

    # Check module name for package
    sources = descriptor.default_frontmatter["sources"]
    source = sources[0]
    assert source["module"] == "supekku.scripts"  # Should exclude __init__

    # Check slug parts
    assert descriptor.slug_parts == ["supekku", "scripts", "__init__"]

  def test_describe_rejects_non_python_unit(self) -> None:
    """Test describe method rejects non-Python source units."""
    unit = SourceUnit("go", "internal/package", self.repo_root)

    with pytest.raises(ValueError) as context:
      self.adapter.describe(unit)

    assert "PythonAdapter cannot process go units" in str(context.value)

  def test_generate_rejects_non_python_unit(self) -> None:
    """Test generate method rejects non-Python source units."""
    unit = SourceUnit("go", "internal/package", self.repo_root)
    spec_dir = Path("/test/spec/SPEC-001")

    with pytest.raises(ValueError) as context:
      self.adapter.generate(unit, spec_dir=spec_dir)

    assert "PythonAdapter cannot process go units" in str(context.value)

  @patch("pathlib.Path.exists")
  def test_generate_missing_file(self, mock_exists) -> None:
    """Test generate method handles missing files gracefully."""
    mock_exists.return_value = False

    unit = SourceUnit("python", "missing/module.py", self.repo_root)
    spec_dir = Path("/test/spec/SPEC-001")
    variants = self.adapter.generate(unit, spec_dir=spec_dir)

    # Should return single error variant
    assert len(variants) == 1
    assert variants[0].name == "error"

  @patch("pathlib.Path.exists")
  @patch("supekku.scripts.lib.docs.python.generate_docs")
  def test_generate_creates_variants(self, mock_generate_docs, mock_exists) -> None:
    """Test generate method creates documentation variants."""
    # Setup mocks
    mock_exists.return_value = True

    # Mock the generate_docs results
    mock_results = [
      Mock(
        variant="public",
        path=Path("/test/repo/contracts/python/module-api.md"),
        hash="hash1",
        status="created",
      ),
      Mock(
        variant="all",
        path=Path("/test/repo/contracts/python/module-implementation.md"),
        hash="hash2",
        status="changed",
      ),
      Mock(
        variant="tests",
        path=Path("/test/repo/contracts/python/module-tests.md"),
        hash="hash3",
        status="unchanged",
      ),
    ]
    mock_generate_docs.return_value = mock_results

    unit = SourceUnit("python", "module.py", self.repo_root)
    spec_dir = Path("/test/spec/SPEC-001")
    variants = self.adapter.generate(unit, spec_dir=spec_dir)

    # Should generate three variants
    assert len(variants) == 3

    variant_names = [v.name for v in variants]
    assert "api" in variant_names
    assert "implementation" in variant_names
    assert "tests" in variant_names

    # Check that generate_docs was called correctly
    mock_generate_docs.assert_called_once()
    _, kwargs = mock_generate_docs.call_args

    assert kwargs["unit"] == self.repo_root / "module.py"
    assert not kwargs["check"]
    assert kwargs["output_root"] == spec_dir / "contracts"
    assert kwargs["base_path"] == self.repo_root

  @patch("pathlib.Path.exists")
  @patch("supekku.scripts.lib.docs.python.generate_docs")
  def test_generate_check_mode(self, mock_generate_docs, mock_exists) -> None:
    """Test generate method in check mode."""
    mock_exists.return_value = True

    mock_results = [
      Mock(
        variant="public",
        path=Path("/test/repo/contracts/python/module-api.md"),
        hash="hash1",
        status="unchanged",
      ),
    ]
    mock_generate_docs.return_value = mock_results

    unit = SourceUnit("python", "module.py", self.repo_root)
    spec_dir = Path("/test/spec/SPEC-001")
    self.adapter.generate(unit, spec_dir=spec_dir, check=True)

    # Check that check=True was passed to generate_docs
    _, kwargs = mock_generate_docs.call_args
    assert kwargs["check"]

  @patch("pathlib.Path.exists")
  @patch("supekku.scripts.lib.docs.python.generate_docs")
  def test_generate_handles_exceptions(self, mock_generate_docs, mock_exists) -> None:
    """Test generate method handles exceptions gracefully."""
    mock_exists.return_value = True
    mock_generate_docs.side_effect = Exception("Generation failed")

    unit = SourceUnit("python", "module.py", self.repo_root)
    spec_dir = Path("/test/spec/SPEC-001")
    variants = self.adapter.generate(unit, spec_dir=spec_dir)

    # Should return error variants for all expected outputs
    assert len(variants) == 3
    for variant in variants:
      assert variant.name in ["api", "implementation", "tests"]
      assert variant.status == "unchanged"

  @patch("pathlib.Path.exists")
  @patch("supekku.scripts.lib.sync.adapters.python.find_all_leaf_packages")
  def test_discover_targets_auto_discovery(
    self,
    mock_find_packages,
    mock_exists,
  ) -> None:
    """Test discover_targets auto-discovers Python packages."""
    # Mock exists to return True for python_root
    mock_exists.return_value = True

    # Mock package discovery to return leaf packages
    mock_packages = [
      Path("/test/repo/supekku/cli"),
      Path("/test/repo/supekku/scripts/lib/formatters"),
      Path("/test/repo/supekku/scripts/lib/specs"),
    ]
    mock_find_packages.return_value = mock_packages

    units = self.adapter.discover_targets(self.repo_root)

    # Should discover all packages (relative paths)
    assert len(units) == 3
    identifiers = [unit.identifier for unit in units]
    assert "supekku/cli" in identifiers
    assert "supekku/scripts/lib/formatters" in identifiers
    assert "supekku/scripts/lib/specs" in identifiers

  @patch("pathlib.Path.exists")
  def test_discover_targets_requested_modules(self, mock_exists) -> None:
    """Test discover_targets processes requested modules."""
    mock_exists.return_value = True

    requested = ["module.py", "package/submodule.py"]
    units = self.adapter.discover_targets(self.repo_root, requested)

    # Should process requested modules
    assert len(units) == 2
    identifiers = [unit.identifier for unit in units]
    assert "module.py" in identifiers
    assert "package/submodule.py" in identifiers

  def test_should_skip_file_patterns(self) -> None:
    """Test _should_skip_file identifies files to skip."""
    skip_files = [
      Path("/test/repo/__pycache__/module.pyc"),
      Path("/test/repo/.git/config"),
      Path("/test/repo/.pytest_cache/data"),
      Path("/test/repo/venv/lib/module.py"),
      Path("/test/repo/.hidden_file.py"),
    ]

    for file_path in skip_files:
      with self.subTest(file_path=file_path):
        msg = f"Should skip file: {file_path}"
        assert self.adapter._should_skip_file(file_path), msg

  def test_should_not_skip_regular_files(self) -> None:
    """Test _should_skip_file allows regular Python files."""
    keep_files = [
      Path("/test/repo/module.py"),
      Path("/test/repo/subdir/utils.py"),
    ]

    for file_path in keep_files:
      with self.subTest(file_path=file_path):
        msg = f"Should not skip file: {file_path}"
        assert not self.adapter._should_skip_file(file_path), msg

  def test_should_skip_init_files(self) -> None:
    """Test __init__.py files are skipped."""
    init_files = [
      Path("/test/repo/package/__init__.py"),
      Path("/test/repo/subdir/__init__.py"),
    ]

    for file_path in init_files:
      with self.subTest(file_path=file_path):
        msg = f"Should skip __init__.py file: {file_path}"
        assert self.adapter._should_skip_file(file_path), msg


if __name__ == "__main__":
  unittest.main()
