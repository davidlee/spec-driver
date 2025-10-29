"""
Tests for Go language adapter.
"""

import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from ..models import SourceUnit
from .go import GoAdapter


class TestGoAdapter(unittest.TestCase):
    """Test GoAdapter functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.repo_root = Path("/test/repo")
        self.adapter = GoAdapter(self.repo_root)

    def test_language_identifier(self):
        """Test that GoAdapter has correct language identifier."""
        self.assertEqual(GoAdapter.language, "go")
        self.assertEqual(self.adapter.language, "go")

    def test_supports_identifier_valid_go_packages(self):
        """Test supports_identifier returns True for valid Go package paths."""
        valid_identifiers = [
            "cmd/vice",
            "internal/application/pipeline",
            "pkg/utils",
            "test/helpers",
            "tools/generator",
            "simple",
            "github.com/user/repo/pkg",
            "module/sub-package",
            "module/sub_package",
        ]

        for identifier in valid_identifiers:
            with self.subTest(identifier=identifier):
                self.assertTrue(
                    self.adapter.supports_identifier(identifier),
                    f"Should support Go package: {identifier}",
                )

    def test_supports_identifier_invalid_identifiers(self):
        """Test supports_identifier returns False for non-Go identifiers."""
        invalid_identifiers = [
            "",  # empty
            "file.go",  # file extension
            "module.py",  # Python file
            "script.js",  # JavaScript file
            "package with spaces",  # spaces
            "package\twith\ttabs",  # tabs
            "package\nwith\nnewlines",  # newlines
        ]

        for identifier in invalid_identifiers:
            with self.subTest(identifier=identifier):
                self.assertFalse(
                    self.adapter.supports_identifier(identifier),
                    f"Should not support identifier: {identifier}",
                )

    def test_describe_go_package(self):
        """Test describe method generates correct metadata for Go packages."""
        unit = SourceUnit("go", "internal/application/pipeline", self.repo_root)
        descriptor = self.adapter.describe(unit)

        # Check slug parts
        self.assertEqual(descriptor.slug_parts, ["internal", "application", "pipeline"])

        # Check frontmatter has packages for compatibility
        self.assertIn("packages", descriptor.default_frontmatter)
        self.assertEqual(
            descriptor.default_frontmatter["packages"],
            ["internal/application/pipeline"],
        )

        # Check new sources structure
        self.assertIn("sources", descriptor.default_frontmatter)
        sources = descriptor.default_frontmatter["sources"]
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0]["language"], "go")
        self.assertEqual(sources[0]["identifier"], "internal/application/pipeline")

        # Check variants
        self.assertEqual(len(descriptor.variants), 2)
        variant_names = [v.name for v in descriptor.variants]
        self.assertIn("public", variant_names)
        self.assertIn("internal", variant_names)

        # Check variant paths
        public_variant = next(v for v in descriptor.variants if v.name == "public")
        internal_variant = next(v for v in descriptor.variants if v.name == "internal")

        self.assertEqual(public_variant.path, Path("contracts/interfaces.md"))
        self.assertEqual(internal_variant.path, Path("contracts/internals.md"))

    def test_describe_rejects_non_go_unit(self):
        """Test describe method rejects non-Go source units."""
        unit = SourceUnit("python", "some/module.py", self.repo_root)

        with self.assertRaises(ValueError) as context:
            self.adapter.describe(unit)

        self.assertIn("GoAdapter cannot process python units", str(context.exception))

    def test_generate_rejects_non_go_unit(self):
        """Test generate method rejects non-Go source units."""
        unit = SourceUnit("python", "some/module.py", self.repo_root)
        spec_dir = Path("/test/spec/SPEC-001")

        with self.assertRaises(ValueError) as context:
            self.adapter.generate(unit, spec_dir=spec_dir)

        self.assertIn("GoAdapter cannot process python units", str(context.exception))

    @patch("subprocess.run")
    @patch("builtins.open")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.mkdir")
    def test_generate_creates_variants(
        self, _mock_mkdir, mock_exists, mock_open, mock_subprocess
    ):
        """Test generate method creates documentation variants."""
        # Setup mocks
        mock_exists.return_value = True
        mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")

        # Mock file content for hash calculation
        mock_file = Mock()
        mock_file.read.return_value = "# Documentation content"
        mock_open.return_value.__enter__.return_value = mock_file

        # Mock TechSpecSyncEngine
        with patch(
            "supekku.scripts.lib.sync_engine.TechSpecSyncEngine"
        ) as mock_engine_class:
            mock_engine = Mock()
            mock_engine.go_module_name.return_value = "github.com/test/repo"
            mock_engine_class.return_value = mock_engine

            unit = SourceUnit("go", "internal/test", self.repo_root)
            spec_dir = Path("/test/spec/SPEC-001")
            variants = self.adapter.generate(unit, spec_dir=spec_dir)

            # Should generate two variants
            self.assertEqual(len(variants), 2)

            variant_names = [v.name for v in variants]
            self.assertIn("public", variant_names)
            self.assertIn("internal", variant_names)

            # Check that gomarkdoc was called
            self.assertEqual(mock_subprocess.call_count, 2)

    @patch("subprocess.run")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.mkdir")
    def test_generate_check_mode(self, _mock_mkdir, mock_exists, mock_subprocess):
        """Test generate method in check mode."""
        # Setup: files exist and gomarkdoc check passes
        mock_exists.return_value = True
        mock_subprocess.return_value = Mock(returncode=0)  # Check passes

        with patch(
            "supekku.scripts.lib.sync_engine.TechSpecSyncEngine"
        ) as mock_engine_class:
            mock_engine = Mock()
            mock_engine.go_module_name.return_value = "github.com/test/repo"
            mock_engine_class.return_value = mock_engine

            unit = SourceUnit("go", "internal/test", self.repo_root)
            spec_dir = Path("/test/spec/SPEC-001")
            variants = self.adapter.generate(unit, spec_dir=spec_dir, check=True)

            # Should check both variants
            self.assertEqual(len(variants), 2)

            # All variants should be unchanged (check passed)
            for variant in variants:
                self.assertEqual(variant.status, "unchanged")

            # Should have called gomarkdoc with --check
            self.assertEqual(mock_subprocess.call_count, 2)
            for call in mock_subprocess.call_args_list:
                args = call[0][0]  # First positional argument (command list)
                self.assertIn("--check", args)


if __name__ == "__main__":
    unittest.main()
