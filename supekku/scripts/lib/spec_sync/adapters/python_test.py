"""
Tests for Python language adapter.
"""

import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from ..models import SourceUnit
from .python import PythonAdapter


class TestPythonAdapter(unittest.TestCase):
    """Test PythonAdapter functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.repo_root = Path("/test/repo")
        self.adapter = PythonAdapter(self.repo_root)

    def test_language_identifier(self):
        """Test that PythonAdapter has correct language identifier."""
        self.assertEqual(PythonAdapter.language, "python")
        self.assertEqual(self.adapter.language, "python")

    def test_supports_identifier_valid_python_modules(self):
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
                self.assertTrue(
                    self.adapter.supports_identifier(identifier),
                    f"Should support Python identifier: {identifier}",
                )

    def test_supports_identifier_invalid_identifiers(self):
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
                self.assertFalse(
                    self.adapter.supports_identifier(identifier),
                    f"Should not support identifier: {identifier}",
                )

    def test_describe_python_module(self):
        """Test describe method generates correct metadata for Python modules."""
        unit = SourceUnit("python", "supekku/scripts/lib/workspace.py", self.repo_root)
        descriptor = self.adapter.describe(unit)

        # Check slug parts
        self.assertEqual(
            descriptor.slug_parts, ["supekku", "scripts", "lib", "workspace"]
        )

        # Check frontmatter structure
        self.assertIn("sources", descriptor.default_frontmatter)
        sources = descriptor.default_frontmatter["sources"]
        self.assertEqual(len(sources), 1)

        source = sources[0]
        self.assertEqual(source["language"], "python")
        self.assertEqual(source["identifier"], "supekku/scripts/lib/workspace.py")
        self.assertEqual(source["module"], "supekku.scripts.lib.workspace")

        # Check variants in frontmatter
        self.assertIn("variants", source)
        variants = source["variants"]
        self.assertEqual(len(variants), 3)

        variant_names = [v["name"] for v in variants]
        self.assertIn("api", variant_names)
        self.assertIn("implementation", variant_names)
        self.assertIn("tests", variant_names)

        # Check descriptor variants
        self.assertEqual(len(descriptor.variants), 3)
        descriptor_variant_names = [v.name for v in descriptor.variants]
        self.assertIn("api", descriptor_variant_names)
        self.assertIn("implementation", descriptor_variant_names)
        self.assertIn("tests", descriptor_variant_names)

        # Check variant paths
        api_variant = next(v for v in descriptor.variants if v.name == "api")
        impl_variant = next(
            v for v in descriptor.variants if v.name == "implementation"
        )
        tests_variant = next(v for v in descriptor.variants if v.name == "tests")

        self.assertEqual(api_variant.path, Path("contracts/api.md"))
        self.assertEqual(impl_variant.path, Path("contracts/implementation.md"))
        self.assertEqual(tests_variant.path, Path("contracts/tests.md"))

    def test_describe_python_package_init(self):
        """Test describe method handles __init__.py files correctly."""
        unit = SourceUnit("python", "supekku/scripts/__init__.py", self.repo_root)
        descriptor = self.adapter.describe(unit)

        # Check module name for package
        sources = descriptor.default_frontmatter["sources"]
        source = sources[0]
        self.assertEqual(source["module"], "supekku.scripts")  # Should exclude __init__

        # Check slug parts
        self.assertEqual(descriptor.slug_parts, ["supekku", "scripts", "__init__"])

    def test_describe_rejects_non_python_unit(self):
        """Test describe method rejects non-Python source units."""
        unit = SourceUnit("go", "internal/package", self.repo_root)

        with self.assertRaises(ValueError) as context:
            self.adapter.describe(unit)

        self.assertIn("PythonAdapter cannot process go units", str(context.exception))

    def test_generate_rejects_non_python_unit(self):
        """Test generate method rejects non-Python source units."""
        unit = SourceUnit("go", "internal/package", self.repo_root)
        spec_dir = Path("/test/spec/SPEC-001")

        with self.assertRaises(ValueError) as context:
            self.adapter.generate(unit, spec_dir=spec_dir)

        self.assertIn("PythonAdapter cannot process go units", str(context.exception))

    @patch("pathlib.Path.exists")
    def test_generate_missing_file(self, mock_exists):
        """Test generate method handles missing files gracefully."""
        mock_exists.return_value = False

        unit = SourceUnit("python", "missing/module.py", self.repo_root)
        spec_dir = Path("/test/spec/SPEC-001")
        variants = self.adapter.generate(unit, spec_dir=spec_dir)

        # Should return single error variant
        self.assertEqual(len(variants), 1)
        self.assertEqual(variants[0].name, "error")

    @patch("pathlib.Path.exists")
    @patch("supekku.scripts.lib.docs.python.generate_docs")
    def test_generate_creates_variants(self, mock_generate_docs, mock_exists):
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
        self.assertEqual(len(variants), 3)

        variant_names = [v.name for v in variants]
        self.assertIn("api", variant_names)
        self.assertIn("implementation", variant_names)
        self.assertIn("tests", variant_names)

        # Check that generate_docs was called correctly
        mock_generate_docs.assert_called_once()
        _, kwargs = mock_generate_docs.call_args

        self.assertEqual(kwargs["unit"], self.repo_root / "module.py")
        self.assertFalse(kwargs["check"])
        self.assertEqual(kwargs["output_root"], spec_dir / "contracts")
        self.assertEqual(kwargs["base_path"], self.repo_root)

    @patch("pathlib.Path.exists")
    @patch("supekku.scripts.lib.docs.python.generate_docs")
    def test_generate_check_mode(self, mock_generate_docs, mock_exists):
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
        self.assertTrue(kwargs["check"])

    @patch("pathlib.Path.exists")
    @patch("supekku.scripts.lib.docs.python.generate_docs")
    def test_generate_handles_exceptions(self, mock_generate_docs, mock_exists):
        """Test generate method handles exceptions gracefully."""
        mock_exists.return_value = True
        mock_generate_docs.side_effect = Exception("Generation failed")

        unit = SourceUnit("python", "module.py", self.repo_root)
        spec_dir = Path("/test/spec/SPEC-001")
        variants = self.adapter.generate(unit, spec_dir=spec_dir)

        # Should return error variants for all expected outputs
        self.assertEqual(len(variants), 3)
        for variant in variants:
            self.assertIn(variant.name, ["api", "implementation", "tests"])
            self.assertEqual(variant.status, "unchanged")

    @patch("pathlib.Path.glob")
    def test_discover_targets_auto_discovery(self, mock_glob):
        """Test discover_targets auto-discovers Python files."""
        # Mock glob results
        mock_files = [
            Path("/test/repo/module1.py"),
            Path("/test/repo/subdir/module2.py"),
            Path("/test/repo/package/__init__.py"),
        ]
        mock_glob.return_value = mock_files

        # Mock _should_skip_file to return False for all files
        with patch.object(self.adapter, "_should_skip_file", return_value=False):
            units = self.adapter.discover_targets(self.repo_root)

        # Should discover all files
        self.assertEqual(len(units), 3)
        identifiers = [unit.identifier for unit in units]
        self.assertIn("module1.py", identifiers)
        self.assertIn("subdir/module2.py", identifiers)
        self.assertIn("package/__init__.py", identifiers)

    @patch("pathlib.Path.exists")
    def test_discover_targets_requested_modules(self, mock_exists):
        """Test discover_targets processes requested modules."""
        mock_exists.return_value = True

        requested = ["module.py", "package/submodule.py"]
        units = self.adapter.discover_targets(self.repo_root, requested)

        # Should process requested modules
        self.assertEqual(len(units), 2)
        identifiers = [unit.identifier for unit in units]
        self.assertIn("module.py", identifiers)
        self.assertIn("package/submodule.py", identifiers)

    def test_should_skip_file_patterns(self):
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
                self.assertTrue(
                    self.adapter._should_skip_file(file_path),
                    f"Should skip file: {file_path}",
                )

    def test_should_not_skip_regular_files(self):
        """Test _should_skip_file allows regular Python files."""
        keep_files = [
            Path("/test/repo/module.py"),
            Path("/test/repo/subdir/utils.py"),
        ]

        for file_path in keep_files:
            with self.subTest(file_path=file_path):
                self.assertFalse(
                    self.adapter._should_skip_file(file_path),
                    f"Should not skip file: {file_path}",
                )

    def test_should_skip_init_files(self):
        """Test __init__.py files are skipped."""
        init_files = [
            Path("/test/repo/package/__init__.py"),
            Path("/test/repo/subdir/__init__.py"),
        ]

        for file_path in init_files:
            with self.subTest(file_path=file_path):
                self.assertTrue(
                    self.adapter._should_skip_file(file_path),
                    f"Should skip __init__.py file: {file_path}",
                )


if __name__ == "__main__":
    unittest.main()
