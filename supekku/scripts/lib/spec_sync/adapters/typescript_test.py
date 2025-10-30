"""Tests for TypeScript language adapter (STUB)."""

import unittest
from pathlib import Path

import pytest

from supekku.scripts.lib.spec_sync.models import SourceUnit

from .typescript import TypeScriptAdapter


class TestTypeScriptAdapter(unittest.TestCase):
    """Test TypeScriptAdapter stub functionality."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.repo_root = Path("/test/repo")
        self.adapter = TypeScriptAdapter(self.repo_root)

    def test_language_identifier(self) -> None:
        """Test that TypeScriptAdapter has correct language identifier."""
        assert TypeScriptAdapter.language == "typescript"
        assert self.adapter.language == "typescript"

    def test_supports_identifier_typescript_files(self) -> None:
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
                assert self.adapter.supports_identifier(identifier), f"Should support TypeScript file: {identifier}"

    def test_supports_identifier_typescript_modules(self) -> None:
        """Test supports_identifier returns True for TypeScript-style module paths."""
        valid_identifiers = [
            "src/components",  # TypeScript module path
            "lib/services.api",  # Dotted notation
            "node_modules/@types/react",  # npm style
            "src/utils",  # Common TypeScript pattern
        ]

        for identifier in valid_identifiers:
            with self.subTest(identifier=identifier):
                assert self.adapter.supports_identifier(identifier), f"Should support TypeScript module: {identifier}"

    def test_supports_identifier_rejects_non_typescript(self) -> None:
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
                assert not self.adapter.supports_identifier(identifier), f"Should not support identifier: {identifier}"

    def test_discover_targets_with_requested_identifiers(self) -> None:
        """Test discover_targets processes requested TypeScript identifiers."""
        requested = ["src/index.ts", "lib/utils.tsx", "types/User.ts"]
        units = self.adapter.discover_targets(self.repo_root, requested)

        # Should create units for all requested TypeScript identifiers
        assert len(units) == 3
        identifiers = [unit.identifier for unit in units]
        assert identifiers == requested

        # All units should be TypeScript units
        for unit in units:
            assert unit.language == "typescript"
            assert unit.root == self.repo_root

    def test_discover_targets_filters_non_typescript_requests(self) -> None:
        """Test discover_targets filters out non-TypeScript identifiers."""
        requested = ["src/index.ts", "module.py", "lib/utils.tsx", "internal/go/pkg"]
        units = self.adapter.discover_targets(self.repo_root, requested)

        # Should only create units for TypeScript identifiers
        assert len(units) == 2
        identifiers = [unit.identifier for unit in units]
        assert identifiers == ["src/index.ts", "lib/utils.tsx"]

    def test_discover_targets_auto_discovery_not_implemented(self) -> None:
        """Test auto-discovery raises NotImplementedError."""
        with pytest.raises(NotImplementedError) as context:
            self.adapter.discover_targets(self.repo_root)

        assert "TypeScript auto-discovery not yet implemented" in str(context.value)
        assert "explicit targets" in str(context.value)

    def test_describe_typescript_file(self) -> None:
        """Test describe method for TypeScript files."""
        unit = SourceUnit("typescript", "src/components/Button.tsx", self.repo_root)
        descriptor = self.adapter.describe(unit)

        # Check slug parts (should strip .tsx extension)
        assert descriptor.slug_parts == ["src", "components", "Button"]

        # Check frontmatter structure
        assert "sources" in descriptor.default_frontmatter
        sources = descriptor.default_frontmatter["sources"]
        assert len(sources) == 1

        source = sources[0]
        assert source["language"] == "typescript"
        assert source["identifier"] == "src/components/Button.tsx"

        # Check variants in frontmatter
        assert "variants" in source
        variants = source["variants"]
        assert len(variants) == 3

        variant_names = [v["name"] for v in variants]
        assert "public" in variant_names
        assert "internal" in variant_names
        assert "types" in variant_names

        # Check descriptor variants
        assert len(descriptor.variants) == 3
        descriptor_variant_names = [v.name for v in descriptor.variants]
        assert "public" in descriptor_variant_names
        assert "internal" in descriptor_variant_names
        assert "types" in descriptor_variant_names

        # Check variant paths
        public_variant = next(v for v in descriptor.variants if v.name == "public")
        internal_variant = next(v for v in descriptor.variants if v.name == "internal")
        types_variant = next(v for v in descriptor.variants if v.name == "types")

        expected_slug = "src-components-Button"
        assert public_variant.path == Path(f"contracts/typescript/{expected_slug}-public.md")
        assert internal_variant.path == Path(f"contracts/typescript/{expected_slug}-internal.md")
        assert types_variant.path == Path(f"contracts/typescript/{expected_slug}-types.md")

    def test_describe_typescript_module_without_extension(self) -> None:
        """Test describe method for TypeScript modules without file extension."""
        unit = SourceUnit("typescript", "src/utils/helpers", self.repo_root)
        descriptor = self.adapter.describe(unit)

        # Should handle path without extension
        assert descriptor.slug_parts == ["src", "utils", "helpers"]

        # Should still create TypeScript source metadata
        sources = descriptor.default_frontmatter["sources"]
        source = sources[0]
        assert source["identifier"] == "src/utils/helpers"

    def test_describe_rejects_non_typescript_unit(self) -> None:
        """Test describe method rejects non-TypeScript source units."""
        unit = SourceUnit("python", "some/module.py", self.repo_root)

        with pytest.raises(ValueError) as context:
            self.adapter.describe(unit)

        assert "TypeScriptAdapter cannot process python units" in str(context.value)

    def test_generate_rejects_non_typescript_unit(self) -> None:
        """Test generate method rejects non-TypeScript source units."""
        unit = SourceUnit("python", "some/module.py", self.repo_root)
        spec_dir = Path("/test/spec/SPEC-001")

        with pytest.raises(ValueError) as context:
            self.adapter.generate(unit, spec_dir=spec_dir)

        assert "TypeScriptAdapter cannot process python units" in str(context.value)

    def test_generate_not_implemented(self) -> None:
        """Test generate method raises NotImplementedError."""
        unit = SourceUnit("typescript", "src/index.ts", self.repo_root)
        spec_dir = Path("/test/spec/SPEC-001")

        with pytest.raises(NotImplementedError) as context:
            self.adapter.generate(unit, spec_dir=spec_dir)

        assert "TypeScript documentation generation not yet implemented" in str(context.value)
        assert "src/index.ts" in str(context.value)
        assert "placeholder adapter" in str(context.value)

    def test_generate_check_mode_not_implemented(self) -> None:
        """Test generate method in check mode also raises NotImplementedError."""
        unit = SourceUnit("typescript", "src/index.ts", self.repo_root)
        spec_dir = Path("/test/spec/SPEC-001")

        with pytest.raises(NotImplementedError) as context:
            self.adapter.generate(unit, spec_dir=spec_dir, check=True)

        assert "TypeScript documentation generation not yet implemented" in str(context.value)

    def test_supports_identifier_edge_cases(self) -> None:
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
                assert result == expected, f"Expected {identifier} to be {expected}, got {result}"


class TestTypeScriptAdapterIntegration(unittest.TestCase):
    """Integration tests for TypeScript adapter in engine context."""

    def test_adapter_can_be_imported_and_instantiated(self) -> None:
        """Test that TypeScript adapter can be imported and used."""
        # pylint: disable=import-outside-toplevel
        from supekku.scripts.lib.spec_sync.adapters import (
            TypeScriptAdapter as TSAdapter,
        )

        adapter = TSAdapter(Path("/test"))
        assert adapter.language == "typescript"

    def test_adapter_available_in_engine_defaults(self) -> None:
        """Test that TypeScript adapter is available in engine defaults."""
        # pylint: disable=import-outside-toplevel
        from supekku.scripts.lib.spec_sync.engine import SpecSyncEngine

        engine = SpecSyncEngine(Path("/test"), Path("/test/specs"))

        # Should have TypeScript adapter in defaults
        assert "typescript" in engine.adapters
        assert engine.adapters["typescript"].language == "typescript"

    def test_engine_can_detect_typescript_support(self) -> None:
        """Test that engine can detect TypeScript identifier support."""
        # pylint: disable=import-outside-toplevel
        from supekku.scripts.lib.spec_sync.engine import SpecSyncEngine

        engine = SpecSyncEngine(Path("/test"), Path("/test/specs"))

        # Should detect TypeScript support
        result = engine.supports_identifier("src/index.ts")
        assert result == "typescript"

        # Should detect non-support
        result = engine.supports_identifier("internal/go/package")
        # Could be "go" or None depending on Go adapter logic
        assert result != "typescript"


if __name__ == "__main__":
    unittest.main()
