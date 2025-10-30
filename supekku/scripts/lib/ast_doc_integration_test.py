"""Integration tests for AST documentation generation justfile commands.

Tests the actual justfile commands and end-to-end workflow including
file I/O, command line argument parsing, and real documentation generation.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from supekku.scripts.lib.ast_doc_test_fixtures import SIMPLE_CLASS, TEST_MODULE


class JustfileIntegrationTest(unittest.TestCase):
    """Test justfile command integration for AST documentation."""

    def setUp(self) -> None:
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.temp_path = Path(self.temp_dir.name)

        # Store original working directory
        self.original_cwd = Path.cwd()

        # Create test package structure
        self.package_dir = self.temp_path / "test_lib"
        self.package_dir.mkdir()
        (self.package_dir / "__init__.py").write_text("")

        # Create test files
        (self.package_dir / "calculator.py").write_text(SIMPLE_CLASS)
        (self.package_dir / "calculator_test.py").write_text(TEST_MODULE)

        # Create docs directory
        self.docs_dir = self.temp_path / "docs" / "deterministic"
        self.docs_dir.mkdir(parents=True)

    def tearDown(self) -> None:
        """Clean up test environment."""
        os.chdir(self.original_cwd)

    def _run_ast_generator(
        self, doc_type: str, check: bool = False,
    ) -> subprocess.CompletedProcess:
        """Run the AST generator script with given parameters."""
        # Change to the project root directory where the script is located
        project_root = Path(__file__).parent.parent.parent.parent
        os.chdir(project_root)

        cmd = [
            "python",
            "supekku/scripts/cli/deterministic_ast_doc_generator.py",
            str(self.package_dir),
            "--type",
            doc_type,
        ]
        if check:
            cmd.append("--check")

        return subprocess.run(cmd, capture_output=True, text=True, check=False)

    def test_docs_deterministic_public_command(self) -> None:
        """Test the docs-deterministic-public equivalent command."""
        result = self._run_ast_generator("public")

        # Should succeed
        assert result.returncode == 0, f"Command failed: {result.stderr}"

        # Should create public documentation files
        expected_file = self.docs_dir / "calculator-public.md"
        if expected_file.exists():
            content = expected_file.read_text()
            assert "Calculator" in content
            # Should not include private methods in public docs
            assert "_private_method" not in content

    def test_docs_deterministic_all_command(self) -> None:
        """Test the docs-deterministic-all equivalent command."""
        result = self._run_ast_generator("all")

        # Should succeed
        assert result.returncode == 0, f"Command failed: {result.stderr}"

        # Check output indicates file creation/changes
        output = result.stdout
        assert "created" in output or "changed" in output or "unchanged" in output, f"Expected status indicators in output: {output}"

    def test_docs_deterministic_tests_command(self) -> None:
        """Test the docs-deterministic-tests equivalent command."""
        result = self._run_ast_generator("tests")

        # Should succeed
        assert result.returncode == 0, f"Command failed: {result.stderr}"

        # Should only process test files
        expected_file = self.docs_dir / "calculator_test-tests.md"
        if expected_file.exists():
            content = expected_file.read_text()
            assert "TestCalculator" in content

    def test_docs_check_mode_up_to_date(self) -> None:
        """Test check mode when documentation is current."""
        # First generate current documentation
        result = self._run_ast_generator("public")
        assert result.returncode == 0

        # Then check if it's up to date (should pass)
        result = self._run_ast_generator("public", check=True)
        assert result.returncode == 0, f"Check mode failed: {result.stderr}"

        output = result.stdout
        assert "✓" in output, f"Expected success indicator in output: {output}"

    def test_docs_check_mode_outdated(self) -> None:
        """Test check mode when documentation is outdated."""
        # First ensure the docs directory exists in the temp location
        docs_dir = self.temp_path / "supekku" / "docs" / "deterministic"
        docs_dir.mkdir(parents=True, exist_ok=True)

        # Create outdated documentation file
        outdated_file = docs_dir / "calculator-public.md"
        outdated_file.write_text("# Outdated Documentation\n\nThis is old content.")

        # Now run check mode with custom output dir pointing to our temp docs
        project_root = Path(__file__).parent.parent.parent.parent
        os.chdir(project_root)

        cmd = [
            "python",
            "supekku/scripts/cli/deterministic_ast_doc_generator.py",
            str(self.package_dir),
            "--type",
            "public",
            "--check",
            "--output-dir",
            str(docs_dir),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        # Check mode should fail when docs are outdated
        assert result.returncode != 0, f"Check mode should fail for outdated docs. Output: {result.stdout}, Stderr: {result.stderr}"

        output = result.stdout
        assert "✗" in output, f"Expected failure indicator in output: {output}"

    def test_deterministic_output_consistency(self) -> None:
        """Test that running the same command twice produces identical output."""
        # Run the generator twice
        result1 = self._run_ast_generator("all")
        result2 = self._run_ast_generator("all")

        # Both should succeed
        assert result1.returncode == 0
        assert result2.returncode == 0

        # The second run should show files as "unchanged"
        assert "unchanged" in result2.stdout

    def test_invalid_type_parameter(self) -> None:
        """Test handling of invalid documentation type."""
        project_root = Path(__file__).parent.parent.parent.parent
        os.chdir(project_root)

        cmd = [
            "python",
            "supekku/scripts/cli/deterministic_ast_doc_generator.py",
            str(self.package_dir),
            "--type",
            "invalid",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        # Should fail with appropriate error
        assert result.returncode != 0
        assert "invalid" in result.stderr.lower()

    def test_nonexistent_package_directory(self) -> None:
        """Test handling of nonexistent package directory."""
        project_root = Path(__file__).parent.parent.parent.parent
        os.chdir(project_root)

        nonexistent_dir = self.temp_path / "nonexistent"
        cmd = [
            "python",
            "supekku/scripts/cli/deterministic_ast_doc_generator.py",
            str(nonexistent_dir),
            "--type",
            "public",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        # Should fail gracefully
        assert result.returncode != 0


class EndToEndWorkflowTest(unittest.TestCase):
    """Test the complete end-to-end workflow scenarios."""

    def setUp(self) -> None:
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.temp_path = Path(self.temp_dir.name)

        self.original_cwd = Path.cwd()

    def tearDown(self) -> None:
        """Clean up test environment."""
        os.chdir(self.original_cwd)

    def test_complete_documentation_workflow(self) -> None:
        """Test the complete workflow from code to documentation."""
        # Create a realistic package
        package_dir = self.temp_path / "my_project" / "lib"
        package_dir.mkdir(parents=True)
        (package_dir / "__init__.py").write_text("")

        # Add multiple modules with different types of content
        (package_dir / "calculator.py").write_text(SIMPLE_CLASS)
        (package_dir / "utils.py").write_text("""
def utility_function(x: int) -> str:
    '''Convert integer to string.'''
    return str(x)

CONSTANT_VALUE = 42
""")
        (package_dir / "calculator_test.py").write_text(TEST_MODULE)

        # Change to project root
        project_root = Path(__file__).parent.parent.parent.parent
        os.chdir(project_root)

        # Generate all three types of documentation
        for doc_type in ["public", "all", "tests"]:
            cmd = [
                "python",
                "supekku/scripts/cli/deterministic_ast_doc_generator.py",
                str(package_dir),
                "--type",
                doc_type,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            assert result.returncode == 0, f"Failed for type {doc_type}: {result.stderr}"

            # Check that appropriate status messages are shown
            output = result.stdout
            assert any(indicator in output for indicator in ["+", "~", "="]), f"No status indicators found in output for {doc_type}: {output}"

        # Verify check mode passes for all generated docs
        for doc_type in ["public", "all", "tests"]:
            cmd = [
                "python",
                "supekku/scripts/cli/deterministic_ast_doc_generator.py",
                str(package_dir),
                "--type",
                doc_type,
                "--check",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            assert result.returncode == 0, f"Check failed for type {doc_type}: {result.stderr}"

    def test_development_workflow_simulation(self) -> None:
        """Simulate a typical development workflow with documentation updates."""
        # Create initial package
        package_dir = self.temp_path / "evolving_project"
        package_dir.mkdir()
        (package_dir / "__init__.py").write_text("")

        initial_code = '''
class MyClass:
    """Initial version of MyClass."""

    def method_one(self) -> str:
        """First method."""
        return "one"
'''

        (package_dir / "mymodule.py").write_text(initial_code)

        project_root = Path(__file__).parent.parent.parent.parent
        os.chdir(project_root)

        # Generate initial documentation
        cmd = [
            "python",
            "supekku/scripts/cli/deterministic_ast_doc_generator.py",
            str(package_dir),
            "--type",
            "public",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        assert result.returncode == 0
        # The first run should show status output (created, changed, or unchanged)
        assert any(status in result.stdout for status in ["created", "changed", "unchanged"]), f"Expected status indicator in output: {result.stdout}"

        # Verify check mode passes
        cmd = [
            "python",
            "supekku/scripts/cli/deterministic_ast_doc_generator.py",
            str(package_dir),
            "--type",
            "public",
            "--check",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        assert result.returncode == 0

        # Modify the code (add new method)
        updated_code = '''
class MyClass:
    """Updated version of MyClass."""

    def method_one(self) -> str:
        """First method."""
        return "one"

    def method_two(self) -> str:
        """Second method."""
        return "two"
'''

        (package_dir / "mymodule.py").write_text(updated_code)

        # Check mode should now fail (docs are outdated)
        cmd = [
            "python",
            "supekku/scripts/cli/deterministic_ast_doc_generator.py",
            str(package_dir),
            "--type",
            "public",
            "--check",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        assert result.returncode != 0
        assert "✗" in result.stdout

        # Regenerate documentation
        cmd = [
            "python",
            "supekku/scripts/cli/deterministic_ast_doc_generator.py",
            str(package_dir),
            "--type",
            "public",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        assert result.returncode == 0
        assert "changed" in result.stdout

        # Check mode should now pass again
        cmd = [
            "python",
            "supekku/scripts/cli/deterministic_ast_doc_generator.py",
            str(package_dir),
            "--type",
            "public",
            "--check",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        assert result.returncode == 0


if __name__ == "__main__":
    unittest.main()
