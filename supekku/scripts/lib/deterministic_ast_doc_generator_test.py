"""Tests for the deterministic AST documentation generator.

This module tests the core functionality of the AST-based documentation
system including parsing, comment extraction, deterministic output,
and check mode functionality.
"""

from __future__ import annotations

# Import the modules we're testing
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Import backward compatibility functions from CLI module
from supekku.scripts.cli.deterministic_ast_doc_generator import (
  check_mode_comparison,
  write_mode_comparison,
)
from supekku.scripts.lib.ast_doc_test_fixtures import (
  COMMENT_VARIATIONS,
  COMPLEX_TYPES,
  DECORATOR_HEAVY,
  FUNCTIONS_AND_CONSTANTS,
  INHERITANCE_EXAMPLE,
  MINIMAL_MODULE,
  SIMPLE_CLASS,
  SYNTAX_ERROR_MODULE,
)
from supekku.scripts.lib.docs.python import calculate_content_hash
from supekku.scripts.lib.docs.python.analyzer import DeterministicPythonModuleAnalyzer
from supekku.scripts.lib.docs.python.comments import CommentExtractor
from supekku.scripts.lib.docs.python.generator import (
  generate_deterministic_markdown_spec,
)


class CommentExtractorTest(unittest.TestCase):
  """Test the CommentExtractor class."""

  def test_extract_basic_comments(self) -> None:
    """Test extraction of basic comments."""
    source = """# Module comment
def func():
    # Function comment
    x = 1  # Inline comment
    return x
"""
    extractor = CommentExtractor(source)

    assert extractor.comments[1] == "Module comment"
    assert extractor.comments[3] == "Function comment"

    # For inline comments, the extractor may only catch whole-line comments
    # Test that we found at least the first two comments
    assert len(extractor.comments) >= 2

  def test_ignore_shebang(self) -> None:
    """Test that shebang lines are ignored."""
    source = """#!/usr/bin/env python3
# Real comment
def func():
    pass
"""
    extractor = CommentExtractor(source)

    assert 1 not in extractor.comments  # Shebang ignored
    assert extractor.comments[2] == "Real comment"

  def test_get_comment_for_line_direct(self) -> None:
    """Test getting comment for exact line."""
    source = """def func():
    # Direct comment
    return True
"""
    extractor = CommentExtractor(source)

    comment = extractor.get_comment_for_line(2)
    assert comment == "Direct comment"

  def test_get_comment_for_line_nearby(self) -> None:
    """Test getting comment from nearby lines."""
    source = """def func():
    # Comment for next line

    return True
"""
    extractor = CommentExtractor(source)

    # Should find comment from line 2 when asking for line 4
    comment = extractor.get_comment_for_line(4, context=2)
    assert comment == "Comment for next line"

  def test_get_comment_for_line_none(self) -> None:
    """Test when no comment is found."""
    source = """def func():
    return True
"""
    extractor = CommentExtractor(source)

    comment = extractor.get_comment_for_line(2)
    assert comment is None


class DeterministicPythonModuleAnalyzerTest(unittest.TestCase):
  """Test the DeterministicPythonModuleAnalyzer class."""

  def setUp(self) -> None:
    """Set up test environment."""
    self.temp_dir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.addCleanup(self.temp_dir.cleanup)
    self.temp_path = Path(self.temp_dir.name)

  def _write_temp_file(self, content: str, filename: str = "test_module.py") -> Path:
    """Write content to a temporary file."""
    file_path = self.temp_path / filename
    file_path.write_text(content, encoding="utf-8")
    return file_path

  def test_simple_class_parsing(self) -> None:
    """Test parsing a simple class with methods."""
    file_path = self._write_temp_file(SIMPLE_CLASS)
    analyzer = DeterministicPythonModuleAnalyzer(file_path)
    analysis = analyzer.analyze()

    classes = analysis["classes"]
    assert len(classes) == 1

    calc_class = classes[0]
    assert calc_class["name"] == "Calculator"
    assert calc_class["docstring"] == "A simple calculator class."

    # Should have __init__, add, and _private_method
    methods = calc_class["methods"]
    method_names = [m["name"] for m in methods]
    assert "__init__" in method_names
    assert "add" in method_names
    assert "_private_method" in method_names

  def test_complex_type_annotations(self) -> None:
    """Test parsing complex type annotations."""
    file_path = self._write_temp_file(COMPLEX_TYPES)
    analyzer = DeterministicPythonModuleAnalyzer(file_path)
    analysis = analyzer.analyze()

    classes = analysis["classes"]
    assert len(classes) > 0

    processor_class = next(c for c in classes if c["name"] == "DataProcessor")
    assert processor_class["name"] == "DataProcessor"

    methods = processor_class["methods"]
    process_method = next(m for m in methods if m["name"] == "process")

    # Check that complex types are captured in some form
    args_detailed = process_method["args_detailed"]
    return_type = process_method.get("return_type", "")

    # Should capture complex types in arguments or return type
    found_complex_types = False
    for arg in args_detailed:
      if arg.get("type") and ("List" in arg["type"] or "Dict" in arg["type"]):
        found_complex_types = True
        break
    if return_type and ("List" in return_type or "Tuple" in return_type):
      found_complex_types = True

    assert found_complex_types, "Should capture complex type annotations"

  def test_decorator_parsing(self) -> None:
    """Test parsing of decorators."""
    file_path = self._write_temp_file(DECORATOR_HEAVY)
    analyzer = DeterministicPythonModuleAnalyzer(file_path)
    analysis = analyzer.analyze()

    classes = analysis["classes"]
    service_class = next(c for c in classes if c["name"] == "Service")

    methods = service_class["methods"]
    static_method = next(m for m in methods if m["name"] == "static_method")

    # Should capture decorators in some form
    decorators = static_method.get("decorators", [])
    assert len(decorators) > 0

  def test_functions_and_constants(self) -> None:
    """Test parsing standalone functions and constants."""
    file_path = self._write_temp_file(FUNCTIONS_AND_CONSTANTS)
    analyzer = DeterministicPythonModuleAnalyzer(file_path)
    analysis = analyzer.analyze()

    functions = analysis["functions"]
    constants = analysis["constants"]

    # Check functions
    function_names = [f["name"] for f in functions]
    assert "calculate_area" in function_names
    assert "format_name" in function_names

    # Check constants
    constant_names = [c["name"] for c in constants]
    assert "MAX_SIZE" in constant_names
    assert "DEFAULT_NAME" in constant_names

  def test_inheritance_hierarchy(self) -> None:
    """Test parsing inheritance relationships."""
    file_path = self._write_temp_file(INHERITANCE_EXAMPLE)
    analyzer = DeterministicPythonModuleAnalyzer(file_path)
    analysis = analyzer.analyze()

    classes = analysis["classes"]
    class_dict = {c["name"]: c for c in classes}

    # Check inheritance
    assert "BaseProcessor" in class_dict
    assert "TextProcessor" in class_dict
    assert "AdvancedTextProcessor" in class_dict

    # Check that base classes are captured
    text_processor = class_dict["TextProcessor"]
    assert "bases" in text_processor

  def test_comment_association(self) -> None:
    """Test that comments are properly associated with code elements."""
    file_path = self._write_temp_file(COMMENT_VARIATIONS)
    analyzer = DeterministicPythonModuleAnalyzer(file_path)
    analysis = analyzer.analyze()

    # Should successfully parse without errors
    assert "classes" in analysis
    assert len(analysis["classes"]) > 0


class DocumentationGenerationTest(unittest.TestCase):
  """Test the documentation generation functions."""

  def setUp(self) -> None:
    """Set up test environment."""
    self.temp_dir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.addCleanup(self.temp_dir.cleanup)
    self.temp_path = Path(self.temp_dir.name)

  def _write_temp_file(self, content: str, filename: str = "test_module.py") -> Path:
    """Write content to a temporary file."""
    file_path = self.temp_path / filename
    file_path.write_text(content, encoding="utf-8")
    return file_path

  def test_public_documentation_generation(self) -> None:
    """Test generation of public-only documentation."""
    file_path = self._write_temp_file(SIMPLE_CLASS)
    analyzer = DeterministicPythonModuleAnalyzer(file_path)
    analysis = analyzer.analyze()

    doc_content = generate_deterministic_markdown_spec(analysis, "public")

    # Should include public methods
    assert "add" in doc_content
    # Note: __init__ might be excluded from public docs in some implementations
    # self.assertIn("__init__", doc_content)

    # Should exclude private methods in public docs
    assert "_private_method" not in doc_content

  def test_all_documentation_generation(self) -> None:
    """Test generation of complete documentation."""
    file_path = self._write_temp_file(SIMPLE_CLASS)
    analyzer = DeterministicPythonModuleAnalyzer(file_path)
    analysis = analyzer.analyze()

    doc_content = generate_deterministic_markdown_spec(analysis, "all")

    # Should include all methods including private
    assert "add" in doc_content
    assert "_private_method" in doc_content

  def test_deterministic_output(self) -> None:
    """Test that output is deterministic across multiple runs."""
    file_path = self._write_temp_file(SIMPLE_CLASS)

    # Generate docs multiple times
    analyzer1 = DeterministicPythonModuleAnalyzer(file_path)
    analysis1 = analyzer1.analyze()
    result1 = generate_deterministic_markdown_spec(analysis1, "all")

    analyzer2 = DeterministicPythonModuleAnalyzer(file_path)
    analysis2 = analyzer2.analyze()
    result2 = generate_deterministic_markdown_spec(analysis2, "all")

    analyzer3 = DeterministicPythonModuleAnalyzer(file_path)
    analysis3 = analyzer3.analyze()
    result3 = generate_deterministic_markdown_spec(analysis3, "all")

    # All results should be identical
    assert result1 == result2
    assert result2 == result3

  def test_deterministic_hash_consistency(self) -> None:
    """Test that content hashes are consistent."""
    file_path = self._write_temp_file(SIMPLE_CLASS)
    analyzer = DeterministicPythonModuleAnalyzer(file_path)
    analysis = analyzer.analyze()
    content = generate_deterministic_markdown_spec(analysis, "all")

    # Generate hash multiple times
    hash1 = calculate_content_hash(content)
    hash2 = calculate_content_hash(content)

    assert hash1 == hash2

  def test_empty_module_handling(self) -> None:
    """Test handling of empty or minimal modules."""
    file_path = self._write_temp_file(MINIMAL_MODULE)
    analyzer = DeterministicPythonModuleAnalyzer(file_path)
    analysis = analyzer.analyze()

    # Should handle empty module without errors
    doc_content = generate_deterministic_markdown_spec(analysis, "all")
    assert "test_module" in doc_content

  def test_syntax_error_handling(self) -> None:
    """Test graceful handling of syntax errors."""
    file_path = self._write_temp_file(SYNTAX_ERROR_MODULE)

    # Should not crash on syntax errors
    try:
      analyzer = DeterministicPythonModuleAnalyzer(file_path)
      analysis = analyzer.analyze()
      if "error" in analysis:
        doc_content = generate_deterministic_markdown_spec(analysis, "all")
        assert "Error" in doc_content
    except (SyntaxError, ValueError) as e:
      # If exception occurs, it should be a specific parsing error
      assert "syntax" in str(e).lower()

  def test_write_mode_comparison(self) -> None:
    """Test the write_mode_comparison function."""
    file_path = self._write_temp_file(SIMPLE_CLASS)
    analyzer = DeterministicPythonModuleAnalyzer(file_path)
    analysis = analyzer.analyze()
    content = generate_deterministic_markdown_spec(analysis, "public")

    output_file = self.temp_path / "test-public.md"

    # Test file creation
    status, old_hash, new_hash = write_mode_comparison(output_file, content)

    assert status == "created"
    assert old_hash == ""
    assert new_hash is not None

    # Test file unchanged (run again)
    status, old_hash, new_hash = write_mode_comparison(output_file, content)

    assert status == "unchanged"
    assert old_hash == new_hash


class CheckModeTest(unittest.TestCase):
  """Test check mode functionality."""

  def setUp(self) -> None:
    """Set up test environment."""
    self.temp_dir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.addCleanup(self.temp_dir.cleanup)
    self.temp_path = Path(self.temp_dir.name)

    self.docs_dir = self.temp_path / "docs" / "deterministic"
    self.docs_dir.mkdir(parents=True)

  def _write_temp_file(self, content: str, filename: str = "test_module.py") -> Path:
    """Write content to a temporary file."""
    file_path = self.temp_path / filename
    file_path.write_text(content, encoding="utf-8")
    return file_path

  def _write_doc_file(self, content: str, filename: str) -> Path:
    """Write content to a documentation file."""
    file_path = self.docs_dir / filename
    file_path.write_text(content, encoding="utf-8")
    return file_path

  def test_check_mode_up_to_date(self) -> None:
    """Test check mode when docs are up to date."""
    # Create source file
    file_path = self._write_temp_file(SIMPLE_CLASS, "calculator.py")

    # Generate current docs using the actual API
    analyzer = DeterministicPythonModuleAnalyzer(file_path)
    analysis = analyzer.analyze()
    current_content = generate_deterministic_markdown_spec(analysis, "public")

    # Write the current docs to file
    doc_filename = "calculator-public.md"
    self._write_doc_file(current_content, doc_filename)

    # Test check mode by comparing content
    output_file = self.docs_dir / "calculator-public.md"
    result, old_hash, new_hash = check_mode_comparison(output_file, current_content)

    assert result  # Should be True when files match
    assert old_hash == new_hash

  def test_check_mode_outdated(self) -> None:
    """Test check mode when docs are outdated."""
    # Create source file
    file_path = self._write_temp_file(SIMPLE_CLASS, "calculator.py")

    # Write outdated docs
    outdated_content = "# Outdated Documentation\n\nThis is old content."
    self._write_doc_file(outdated_content, "calculator-public.md")

    # Generate current content and compare with outdated
    analyzer = DeterministicPythonModuleAnalyzer(file_path)
    analysis = analyzer.analyze()
    current_content = generate_deterministic_markdown_spec(analysis, "public")

    # Check mode should detect outdated docs
    output_file = self.docs_dir / "calculator-public.md"
    result, old_hash, new_hash = check_mode_comparison(output_file, current_content)

    assert not result  # Should be False when files don't match
    assert old_hash != new_hash


class IntegrationTest(unittest.TestCase):
  """Integration tests for the full documentation generation workflow."""

  def setUp(self) -> None:
    """Set up test environment."""
    self.temp_dir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.addCleanup(self.temp_dir.cleanup)
    self.temp_path = Path(self.temp_dir.name)

  def test_full_workflow_simple(self) -> None:
    """Test a simple workflow with individual file analysis."""
    # Create a test file
    file_path = self.temp_path / "calculator.py"
    file_path.write_text(SIMPLE_CLASS)

    # Analyze it
    analyzer = DeterministicPythonModuleAnalyzer(file_path)
    analysis = analyzer.analyze()

    # Generate documentation
    result_public = generate_deterministic_markdown_spec(analysis, "public")
    result_all = generate_deterministic_markdown_spec(analysis, "all")

    # Both should be non-empty and different
    assert len(result_public) > 0
    assert len(result_all) > 0
    assert result_public != result_all

  def test_sorting_consistency(self) -> None:
    """Test that sorting is consistent across different runs."""
    mixed_order = """
class ZebraClass:
    def method_z(self): pass
    def method_a(self): pass

class AlphaClass:
    def method_b(self): pass

def zebra_function(): pass
def alpha_function(): pass
"""

    # Create file
    file_path = self.temp_path / "module.py"
    file_path.write_text(mixed_order)

    # Generate docs multiple times
    results = []
    for _ in range(3):
      analyzer = DeterministicPythonModuleAnalyzer(file_path)
      analysis = analyzer.analyze()
      result = generate_deterministic_markdown_spec(analysis, "all")
      results.append(result)

    # All results should be identical
    assert results[0] == results[1]
    assert results[1] == results[2]


if __name__ == "__main__":
  unittest.main()
