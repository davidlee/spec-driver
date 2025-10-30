"""Tests for specification index management."""

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

import yaml

from .spec_index import SpecIndexBuilder, SpecIndexEntry


class TestSpecIndexEntry(unittest.TestCase):
    """Test SpecIndexEntry data class."""

    def test_creation(self):
        """Test creating a SpecIndexEntry."""
        entry = SpecIndexEntry(
            spec_id="SPEC-001",
            slug="test-spec",
            packages=["internal/test"],
            spec_path=Path("/test/SPEC-001/SPEC-001.md"),
        )

        self.assertEqual(entry.spec_id, "SPEC-001")
        self.assertEqual(entry.slug, "test-spec")
        self.assertEqual(entry.packages, ["internal/test"])
        self.assertEqual(entry.spec_path, Path("/test/SPEC-001/SPEC-001.md"))
        self.assertIsNone(entry.tests_path)

    def test_creation_with_tests_path(self):
        """Test creating a SpecIndexEntry with tests path."""
        tests_path = Path("/test/SPEC-001/tests.md")
        entry = SpecIndexEntry(
            spec_id="SPEC-001",
            slug="test-spec",
            packages=["internal/test"],
            spec_path=Path("/test/SPEC-001/SPEC-001.md"),
            tests_path=tests_path,
        )

        self.assertEqual(entry.tests_path, tests_path)


class TestSpecIndexBuilder(unittest.TestCase):
    """Test SpecIndexBuilder functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)
        self.builder = SpecIndexBuilder(self.base_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def _create_spec_with_frontmatter(self, spec_id: str, frontmatter: dict) -> Path:
        """Create a spec directory and file with given frontmatter."""
        spec_dir = self.base_dir / spec_id
        spec_dir.mkdir(exist_ok=True)
        spec_file = spec_dir / f"{spec_id}.md"

        # Create frontmatter YAML
        frontmatter_yaml = yaml.dump(frontmatter, default_flow_style=False)
        content = (
            f"---\n{frontmatter_yaml}---\n\n# {spec_id}\n\nTest specification content."
        )

        spec_file.write_text(content)
        return spec_file

    def test_initialization(self):
        """Test SpecIndexBuilder initialization."""
        self.assertEqual(self.builder.base_dir, self.base_dir)
        self.assertEqual(self.builder.slug_dir, self.base_dir / "by-slug")
        self.assertEqual(self.builder.package_dir, self.base_dir / "by-package")
        self.assertEqual(self.builder.language_dir, self.base_dir / "by-language")

    def test_rebuild_creates_directories(self):
        """Test that rebuild creates necessary directories."""
        self.builder.rebuild()

        self.assertTrue(self.builder.slug_dir.exists())
        self.assertTrue(self.builder.package_dir.exists())
        self.assertTrue(self.builder.language_dir.exists())

    def test_rebuild_with_slug_symlinks(self):
        """Test rebuild creates slug-based symlinks."""
        # Create a spec with slug
        self._create_spec_with_frontmatter(
            "SPEC-001", {"slug": "test-authentication", "packages": ["cmd/auth"]},
        )

        self.builder.rebuild()

        # Check slug symlink was created
        slug_link = self.builder.slug_dir / "test-authentication"
        self.assertTrue(slug_link.exists())
        self.assertTrue(slug_link.is_symlink())
        self.assertEqual(slug_link.readlink(), Path("../SPEC-001"))

    def test_rebuild_with_package_symlinks(self):
        """Test rebuild creates package-based symlinks."""
        # Create a spec with packages
        self._create_spec_with_frontmatter(
            "SPEC-002",
            {
                "slug": "git-service",
                "packages": ["internal/application/services/git", "cmd/git"],
            },
        )

        self.builder.rebuild()

        # Check package symlinks were created
        git_service_link = (
            self.builder.package_dir / "internal/application/services/git/spec"
        )
        cmd_git_link = self.builder.package_dir / "cmd/git/spec"

        self.assertTrue(git_service_link.exists())
        self.assertTrue(git_service_link.is_symlink())
        self.assertEqual(git_service_link.readlink(), Path("../../../../../SPEC-002"))

        self.assertTrue(cmd_git_link.exists())
        self.assertTrue(cmd_git_link.is_symlink())
        self.assertEqual(cmd_git_link.readlink(), Path("../../../SPEC-002"))

    def test_rebuild_with_language_symlinks_go(self):
        """Test rebuild creates by-language symlinks for Go sources."""
        # Create a spec with Go sources
        self._create_spec_with_frontmatter(
            "SPEC-003",
            {
                "slug": "cmd-vice",
                "packages": ["cmd"],  # Legacy Go packages field
                "sources": [
                    {
                        "language": "go",
                        "identifier": "cmd",
                        "variants": [
                            {"name": "public", "path": "contracts/go/cmd-public.md"},
                            {
                                "name": "internal",
                                "path": "contracts/go/cmd-internal.md",
                            },
                        ],
                    },
                ],
            },
        )

        self.builder.rebuild()

        # Check by-language symlink was created
        go_cmd_link = self.builder.language_dir / "go/cmd/spec"
        self.assertTrue(go_cmd_link.exists())
        self.assertTrue(go_cmd_link.is_symlink())
        self.assertEqual(go_cmd_link.readlink(), Path("../../../SPEC-003"))

    def test_rebuild_with_language_symlinks_python(self):
        """Test rebuild creates by-language symlinks for Python sources."""
        # Create a spec with Python sources
        self._create_spec_with_frontmatter(
            "SPEC-004",
            {
                "slug": "sync-engine",
                "sources": [
                    {
                        "language": "python",
                        "identifier": "supekku/scripts/lib/sync_engine.py",
                        "module": "supekku.scripts.lib.sync_engine",
                        "variants": [
                            {
                                "name": "api",
                                "path": "contracts/python/sync-engine-api.md",
                            },
                            {
                                "name": "implementation",
                                "path": "contracts/python/sync-engine-implementation.md",
                            },
                        ],
                    },
                ],
            },
        )

        self.builder.rebuild()

        # Check by-language symlink was created
        python_sync_link = (
            self.builder.language_dir / "python/supekku/scripts/lib/sync_engine.py/spec"
        )
        self.assertTrue(python_sync_link.exists())
        self.assertTrue(python_sync_link.is_symlink())
        self.assertEqual(
            python_sync_link.readlink(), Path("../../../../../../SPEC-004"),
        )

    def test_rebuild_with_mixed_language_sources(self):
        """Test rebuild handles specs with multiple language sources."""
        # Create a spec with both Go and Python sources
        self._create_spec_with_frontmatter(
            "SPEC-005",
            {
                "slug": "multi-lang-spec",
                "packages": ["internal/multi"],  # Legacy Go packages
                "sources": [
                    {
                        "language": "go",
                        "identifier": "internal/multi",
                        "variants": [
                            {"name": "public", "path": "contracts/go/multi-public.md"},
                        ],
                    },
                    {
                        "language": "python",
                        "identifier": "multi_module.py",
                        "variants": [
                            {"name": "api", "path": "contracts/python/multi-api.md"},
                        ],
                    },
                ],
            },
        )

        self.builder.rebuild()

        # Check both language symlinks were created
        go_link = self.builder.language_dir / "go/internal/multi/spec"
        python_link = self.builder.language_dir / "python/multi_module.py/spec"

        self.assertTrue(go_link.exists())
        self.assertTrue(go_link.is_symlink())
        self.assertEqual(go_link.readlink(), Path("../../../../SPEC-005"))

        self.assertTrue(python_link.exists())
        self.assertTrue(python_link.is_symlink())
        self.assertEqual(python_link.readlink(), Path("../../../SPEC-005"))

        # Also check that package symlink was created (for backwards compatibility)
        package_link = self.builder.package_dir / "internal/multi/spec"
        self.assertTrue(package_link.exists())
        self.assertTrue(package_link.is_symlink())

    def test_rebuild_skips_sources_without_language_or_identifier(self):
        """Test rebuild skips sources missing language or identifier."""
        # Create a spec with incomplete source entries
        self._create_spec_with_frontmatter(
            "SPEC-006",
            {
                "slug": "incomplete-sources",
                "sources": [
                    {
                        "language": "go",
                        # Missing identifier
                        "variants": [
                            {"name": "public", "path": "contracts/go/test.md"},
                        ],
                    },
                    {
                        # Missing language
                        "identifier": "some/module",
                        "variants": [
                            {"name": "api", "path": "contracts/python/test.md"},
                        ],
                    },
                    {
                        "language": "python",
                        "identifier": "valid_module.py",
                        "variants": [
                            {"name": "api", "path": "contracts/python/valid.md"},
                        ],
                    },
                ],
            },
        )

        self.builder.rebuild()

        # Only the valid source should have a symlink
        valid_link = self.builder.language_dir / "python/valid_module.py/spec"
        self.assertTrue(valid_link.exists())

        # Invalid sources should not have symlinks
        go_dir = self.builder.language_dir / "go"
        if go_dir.exists():
            # Should be empty since the Go source was invalid
            self.assertEqual(len(list(go_dir.rglob("*"))), 0)

    def test_rebuild_cleans_existing_symlinks(self):
        """Test rebuild cleans up existing symlinks before creating new ones."""
        # Create initial spec
        self._create_spec_with_frontmatter(
            "SPEC-007",
            {
                "slug": "old-spec",
                "sources": [
                    {
                        "language": "go",
                        "identifier": "old/package",
                        "variants": [{"name": "public", "path": "contracts/go/old.md"}],
                    },
                ],
            },
        )

        self.builder.rebuild()

        # Verify initial symlinks
        old_slug_link = self.builder.slug_dir / "old-spec"
        old_lang_link = self.builder.language_dir / "go/old/package/spec"
        self.assertTrue(old_slug_link.exists())
        self.assertTrue(old_lang_link.exists())

        # Update the spec
        self._create_spec_with_frontmatter(
            "SPEC-007",
            {
                "slug": "updated-spec",
                "sources": [
                    {
                        "language": "go",
                        "identifier": "new/package",
                        "variants": [{"name": "public", "path": "contracts/go/new.md"}],
                    },
                ],
            },
        )

        self.builder.rebuild()

        # Old symlinks should be gone
        self.assertFalse(old_slug_link.exists())
        self.assertFalse(old_lang_link.exists())

        # New symlinks should exist
        new_slug_link = self.builder.slug_dir / "updated-spec"
        new_lang_link = self.builder.language_dir / "go/new/package/spec"
        self.assertTrue(new_slug_link.exists())
        self.assertTrue(new_lang_link.exists())

    def test_rebuild_creates_nested_directory_structure(self):
        """Test rebuild creates nested directories for complex identifiers."""
        # Create spec with deeply nested identifier
        self._create_spec_with_frontmatter(
            "SPEC-008",
            {
                "slug": "deep-nesting",
                "sources": [
                    {
                        "language": "go",
                        "identifier": "internal/application/services/authentication/oauth",
                        "variants": [
                            {"name": "public", "path": "contracts/go/oauth.md"},
                        ],
                    },
                ],
            },
        )

        self.builder.rebuild()

        # Check that nested directory structure was created
        oauth_link = (
            self.builder.language_dir
            / "go/internal/application/services/authentication/oauth/spec"
        )
        self.assertTrue(oauth_link.exists())
        self.assertTrue(oauth_link.is_symlink())
        self.assertEqual(oauth_link.readlink(), Path("../../../../../../../SPEC-008"))

        # Verify parent directories exist
        self.assertTrue(
            (self.builder.language_dir / "go/internal/application/services").exists(),
        )

    def test_rebuild_handles_missing_spec_files(self):
        """Test rebuild gracefully handles missing spec files."""
        # Create spec directory without the actual spec file
        spec_dir = self.base_dir / "SPEC-999"
        spec_dir.mkdir()

        # rebuild should not crash
        self.builder.rebuild()

        # No symlinks should be created for missing spec
        self.assertEqual(len(list(self.builder.slug_dir.iterdir())), 0)
        self.assertEqual(len(list(self.builder.language_dir.rglob("*"))), 0)

    def test_rebuild_handles_malformed_frontmatter(self):
        """Test rebuild handles specs with malformed frontmatter."""
        # Create spec with invalid YAML
        spec_dir = self.base_dir / "SPEC-010"
        spec_dir.mkdir()
        spec_file = spec_dir / "SPEC-010.md"
        spec_file.write_text(
            "---\ninvalid: yaml: [\n---\n\n# SPEC-010\n\nMalformed spec.",
        )

        # Capture warning output
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            # rebuild should not crash but should warn
            self.builder.rebuild()

        # Check that warning was printed
        output = captured_output.getvalue()
        self.assertIn("Warning: Malformed YAML frontmatter", output)
        self.assertIn("SPEC-010.md", output)

        # No symlinks should be created for malformed spec
        self.assertEqual(len(list(self.builder.slug_dir.iterdir())), 0)
        self.assertEqual(len(list(self.builder.language_dir.rglob("*"))), 0)

    def test_rebuild_handles_empty_frontmatter(self):
        """Test rebuild handles specs with empty frontmatter."""
        # Create spec with empty frontmatter
        spec_dir = self.base_dir / "SPEC-011"
        spec_dir.mkdir()
        spec_file = spec_dir / "SPEC-011.md"
        spec_file.write_text("---\n---\n\n# SPEC-011\n\nEmpty frontmatter spec.")

        # rebuild should not crash
        self.builder.rebuild()

        # No symlinks should be created for empty frontmatter
        self.assertEqual(len(list(self.builder.slug_dir.iterdir())), 0)
        self.assertEqual(len(list(self.builder.language_dir.rglob("*"))), 0)

    def test_read_frontmatter_valid_yaml(self):
        """Test _read_frontmatter with valid YAML."""
        spec_file = self._create_spec_with_frontmatter(
            "SPEC-TEST", {"slug": "test", "packages": ["test/pkg"]},
        )

        frontmatter = self.builder._read_frontmatter(spec_file)

        self.assertEqual(frontmatter["slug"], "test")
        self.assertEqual(frontmatter["packages"], ["test/pkg"])

    def test_read_frontmatter_no_frontmatter(self):
        """Test _read_frontmatter with file without frontmatter."""
        spec_dir = self.base_dir / "SPEC-NO-FM"
        spec_dir.mkdir()
        spec_file = spec_dir / "SPEC-NO-FM.md"
        spec_file.write_text("# No Frontmatter\n\nJust markdown content.")

        frontmatter = self.builder._read_frontmatter(spec_file)

        self.assertEqual(frontmatter, {})

    def test_read_frontmatter_incomplete_delimiters(self):
        """Test _read_frontmatter with incomplete frontmatter delimiters."""
        spec_dir = self.base_dir / "SPEC-INCOMPLETE"
        spec_dir.mkdir()
        spec_file = spec_dir / "SPEC-INCOMPLETE.md"
        spec_file.write_text("---\nslug: incomplete\n\n# Missing closing delimiter")

        frontmatter = self.builder._read_frontmatter(spec_file)

        self.assertEqual(frontmatter, {})


if __name__ == "__main__":
    unittest.main()
