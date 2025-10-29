"""
Tests for TypeScript language adapter (STUB).
"""

import unittest
from pathlib import Path

from ..models import SourceUnit
from .typescript import TypeScriptAdapter


class TestTypeScriptAdapter(unittest.TestCase):
    """Test TypeScriptAdapter stub functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.repo_root = Path("/test/repo")
        self.adapter = TypeScriptAdapter(self.repo_root)

    def test_language_identifier(self):
        """Test that TypeScriptAdapter has correct language identifier."""
        self.assertEqual(TypeScriptAdapter.language, "typescript")
        self.assertEqual(self.adapter.language, "typescript")

    def test_supports_identifier_typescript_files(self):
        """Test supports_identifier returns True for TypeScript files."""
        valid_identifiers = [
            "src/index.ts",
            "lib/utils.tsx",
            "components/Button.tsx",
            "services/api.ts",
            "types/User.ts",
            "test/helpers.ts",
        ]

        for identifier in valid_identifiers:
            with self.subTest(identifier=identifier):
                self.assertTrue(
                    self.adapter.supports_identifier(identifier),
                    f"Should support TypeScript file: {identifier}",
                )

    def test_supports_identifier_typescript_modules(self):
        """Test supports_identifier returns True for TypeScript-style module paths."""
        valid_identifiers = [
            "src/components",  # TypeScript module path
            "lib/services.api",  # Dotted notation
            "node_modules/@types/react",  # npm style
            "src/utils",  # Common TypeScript pattern
        ]

        for identifier in valid_identifiers:
            with self.subTest(identifier=identifier):
                self.assertTrue(
                    self.adapter.supports_identifier(identifier),
                    f"Should support TypeScript module: {identifier}",
                )

    def test_supports_identifier_rejects_non_typescript(self):
        """Test supports_identifier returns False for non-TypeScript identifiers."""
        invalid_identifiers = [
            "",  # empty
            "module.py",  # Python file
            "package.go",  # Go file
            "__pycache__/module.pyc",  # Python cache
            "internal/application/services",  # Go-style package (no TS indicators)
            "cmd/vice",  # Go command package
        ]

        for identifier in invalid_identifiers:
            with self.subTest(identifier=identifier):
                self.assertFalse(
                    self.adapter.supports_identifier(identifier),
                    f"Should not support identifier: {identifier}",
                )

    def test_discover_targets_with_requested_identifiers(self):
        """Test discover_targets processes requested TypeScript identifiers."""
        requested = ["src/index.ts", "lib/utils.tsx", "types/User.ts"]
        units = self.adapter.discover_targets(self.repo_root, requested)

        # Should create units for all requested TypeScript identifiers
        self.assertEqual(len(units), 3)
        identifiers = [unit.identifier for unit in units]
        self.assertEqual(identifiers, requested)

        # All units should be TypeScript units
        for unit in units:
            self.assertEqual(unit.language, "typescript")
            self.assertEqual(unit.root, self.repo_root)

    def test_discover_targets_filters_non_typescript_requests(self):
        """Test discover_targets filters out non-TypeScript identifiers."""
        requested = ["src/index.ts", "module.py", "lib/utils.tsx", "internal/go/pkg"]
        units = self.adapter.discover_targets(self.repo_root, requested)

        # Should only create units for TypeScript identifiers
        self.assertEqual(len(units), 2)
        identifiers = [unit.identifier for unit in units]
        self.assertEqual(identifiers, ["src/index.ts", "lib/utils.tsx"])

    def test_discover_targets_auto_discovery_not_implemented(self):
        """Test auto-discovery raises NotImplementedError."""
        with self.assertRaises(NotImplementedError) as context:
            self.adapter.discover_targets(self.repo_root)

        self.assertIn(
            "TypeScript auto-discovery not yet implemented", str(context.exception)
        )
        self.assertIn("explicit targets", str(context.exception))

    def test_describe_typescript_file(self):
        """Test describe method for TypeScript files."""
        unit = SourceUnit("typescript", "src/components/Button.tsx", self.repo_root)
        descriptor = self.adapter.describe(unit)

        # Check slug parts (should strip .tsx extension)
        self.assertEqual(descriptor.slug_parts, ["src", "components", "Button"])

        # Check frontmatter structure
        self.assertIn("sources", descriptor.default_frontmatter)
        sources = descriptor.default_frontmatter["sources"]
        self.assertEqual(len(sources), 1)

        source = sources[0]
        self.assertEqual(source["language"], "typescript")
        self.assertEqual(source["identifier"], "src/components/Button.tsx")

        # Check variants in frontmatter
        self.assertIn("variants", source)
        variants = source["variants"]
        self.assertEqual(len(variants), 3)

        variant_names = [v["name"] for v in variants]
        self.assertIn("public", variant_names)
        self.assertIn("internal", variant_names)
        self.assertIn("types", variant_names)

        # Check descriptor variants
        self.assertEqual(len(descriptor.variants), 3)
        descriptor_variant_names = [v.name for v in descriptor.variants]
        self.assertIn("public", descriptor_variant_names)
        self.assertIn("internal", descriptor_variant_names)
        self.assertIn("types", descriptor_variant_names)

        # Check variant paths
        public_variant = next(v for v in descriptor.variants if v.name == "public")
        internal_variant = next(v for v in descriptor.variants if v.name == "internal")
        types_variant = next(v for v in descriptor.variants if v.name == "types")

        expected_slug = "src-components-Button"
        self.assertEqual(
            public_variant.path,
            Path(f"contracts/typescript/{expected_slug}-public.md"),
        )
        self.assertEqual(
            internal_variant.path,
            Path(f"contracts/typescript/{expected_slug}-internal.md"),
        )
        self.assertEqual(
            types_variant.path, Path(f"contracts/typescript/{expected_slug}-types.md")
        )

    def test_describe_typescript_module_without_extension(self):
        """Test describe method for TypeScript modules without file extension."""
        unit = SourceUnit("typescript", "src/utils/helpers", self.repo_root)
        descriptor = self.adapter.describe(unit)

        # Should handle path without extension
        self.assertEqual(descriptor.slug_parts, ["src", "utils", "helpers"])

        # Should still create TypeScript source metadata
        sources = descriptor.default_frontmatter["sources"]
        source = sources[0]
        self.assertEqual(source["identifier"], "src/utils/helpers")

    def test_describe_rejects_non_typescript_unit(self):
        """Test describe method rejects non-TypeScript source units."""
        unit = SourceUnit("python", "some/module.py", self.repo_root)

        with self.assertRaises(ValueError) as context:
            self.adapter.describe(unit)

        self.assertIn(
            "TypeScriptAdapter cannot process python units", str(context.exception)
        )

    def test_generate_rejects_non_typescript_unit(self):
        """Test generate method rejects non-TypeScript source units."""
        unit = SourceUnit("python", "some/module.py", self.repo_root)
        spec_dir = Path("/test/spec/SPEC-001")

        with self.assertRaises(ValueError) as context:
            self.adapter.generate(unit, spec_dir=spec_dir)

        self.assertIn(
            "TypeScriptAdapter cannot process python units", str(context.exception)
        )

    def test_generate_not_implemented(self):
        """Test generate method raises NotImplementedError."""
        unit = SourceUnit("typescript", "src/index.ts", self.repo_root)
        spec_dir = Path("/test/spec/SPEC-001")

        with self.assertRaises(NotImplementedError) as context:
            self.adapter.generate(unit, spec_dir=spec_dir)

        self.assertIn(
            "TypeScript documentation generation not yet implemented",
            str(context.exception),
        )
        self.assertIn("src/index.ts", str(context.exception))
        self.assertIn("placeholder adapter", str(context.exception))

    def test_generate_check_mode_not_implemented(self):
        """Test generate method in check mode also raises NotImplementedError."""
        unit = SourceUnit("typescript", "src/index.ts", self.repo_root)
        spec_dir = Path("/test/spec/SPEC-001")

        with self.assertRaises(NotImplementedError) as context:
            self.adapter.generate(unit, spec_dir=spec_dir, check=True)

        self.assertIn(
            "TypeScript documentation generation not yet implemented",
            str(context.exception),
        )

    def test_supports_identifier_edge_cases(self):
        """Test supports_identifier with edge cases."""
        # Test with paths that could be ambiguous
        test_cases = [
            # Should support
            ("src/components/Button.component.ts", True),
            ("packages/core/index.ts", True),
            ("libs/shared.tsx", True),
            ("app.ts", True),
            ("src/types/index.d.ts", True),  # TypeScript declaration files
            # Should not support (clearer non-TS patterns)
            ("main.go", False),
            ("requirements.txt", False),
            ("Dockerfile", False),
            ("package.json", False),  # Not TypeScript source
        ]

        for identifier, expected in test_cases:
            with self.subTest(identifier=identifier):
                result = self.adapter.supports_identifier(identifier)
                self.assertEqual(
                    result,
                    expected,
                    f"Expected {identifier} to be {expected}, got {result}",
                )


class TestTypeScriptAdapterIntegration(unittest.TestCase):
    """Integration tests for TypeScript adapter in engine context."""

    def test_adapter_can_be_imported_and_instantiated(self):
        """Test that TypeScript adapter can be imported and used."""
        # pylint: disable=import-outside-toplevel
        from supekku.scripts.lib.spec_sync.adapters import (
            TypeScriptAdapter as TSAdapter,
        )

        adapter = TSAdapter(Path("/test"))
        self.assertEqual(adapter.language, "typescript")

    def test_adapter_available_in_engine_defaults(self):
        """Test that TypeScript adapter is available in engine defaults."""
        # pylint: disable=import-outside-toplevel
        from supekku.scripts.lib.spec_sync.engine import SpecSyncEngine

        engine = SpecSyncEngine(Path("/test"), Path("/test/specs"))

        # Should have TypeScript adapter in defaults
        self.assertIn("typescript", engine.adapters)
        self.assertEqual(engine.adapters["typescript"].language, "typescript")

    def test_engine_can_detect_typescript_support(self):
        """Test that engine can detect TypeScript identifier support."""
        # pylint: disable=import-outside-toplevel
        from supekku.scripts.lib.spec_sync.engine import SpecSyncEngine

        engine = SpecSyncEngine(Path("/test"), Path("/test/specs"))

        # Should detect TypeScript support
        result = engine.supports_identifier("src/index.ts")
        self.assertEqual(result, "typescript")

        # Should detect non-support
        result = engine.supports_identifier("internal/go/package")
        # Could be "go" or None depending on Go adapter logic
        self.assertNotEqual(result, "typescript")


if __name__ == "__main__":
    unittest.main()
