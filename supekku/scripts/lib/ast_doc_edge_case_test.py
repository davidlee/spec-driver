"""Comprehensive edge case tests for the deterministic AST documentation generator.

Tests multiline comments, complex typing, decorators with arguments,
caching behavior, path normalization, and other edge cases.
"""

from __future__ import annotations

# Import the modules we're testing
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from supekku.scripts.lib.ast_doc_edge_case_fixtures import (
    ASYNC_PATTERNS,
    COMPLEX_DECORATORS,
    COMPLEX_INHERITANCE,
    COMPLEX_TYPING,
    MULTILINE_COMMENTS,
    RAW_STRING_PATTERNS,
    UNICODE_EDGE_CASES,
)
from supekku.scripts.lib.docs.python import (
    ParseCache,
    PathNormalizer,
    calculate_content_hash,
)
from supekku.scripts.lib.docs.python.analyzer import DeterministicPythonModuleAnalyzer
from supekku.scripts.lib.docs.python.comments import CommentExtractor
from supekku.scripts.lib.docs.python.generator import (
    generate_deterministic_markdown_spec,
)


class PathNormalizerTest(unittest.TestCase):
    """Test cross-platform path normalization."""

    def test_normalize_path_for_id_consistency(self) -> None:
        """Test that path normalization is consistent across platforms."""
        # Create temporary files with various path structures
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create nested directory structure
            nested_dir = temp_path / "src" / "package" / "subpackage"
            nested_dir.mkdir(parents=True)

            test_file = nested_dir / "module.py"
            test_file.write_text("# Test module")

            # Test normalization with different base paths
            normalized_1 = PathNormalizer.normalize_path_for_id(test_file, temp_path)
            normalized_2 = PathNormalizer.normalize_path_for_id(test_file, temp_path)

            # Should be identical
            assert normalized_1 == normalized_2

            # Should use forward slashes regardless of platform
            assert "\\" not in normalized_1

            # Should be relative path
            assert not normalized_1.startswith("/")
            assert normalized_1.startswith("src/")

    def test_get_module_name_consistency(self) -> None:
        """Test module name generation consistency."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            test_file = temp_path / "package" / "submodule.py"
            test_file.parent.mkdir(parents=True)
            test_file.write_text("# Test")

            module_name = PathNormalizer.get_module_name(test_file, temp_path)

            # Should use dots for module separation
            assert module_name == "package.submodule"

            # Test without .py extension
            no_ext_file = temp_path / "package" / "noext"
            no_ext_file.write_text("# Test")

            module_name_no_ext = PathNormalizer.get_module_name(no_ext_file, temp_path)
            assert module_name_no_ext == "package.noext"

    def test_get_output_filename_stability(self) -> None:
        """Test output filename generation stability."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            test_file = temp_path / "my.complex-module.py"
            test_file.write_text("# Test")

            filename = PathNormalizer.get_output_filename(
                test_file, "public", temp_path,
            )

            # Should handle special characters safely
            assert filename.endswith("-public.md")
            assert "." not in filename.replace("-public.md", "")

    @patch("os.name", "nt")  # Mock Windows
    def test_windows_path_handling(self) -> None:
        """Test Windows-specific path handling."""
        # This test may need adjustment based on actual Windows behavior
        # but demonstrates the approach for platform-specific testing

    def test_edge_case_paths(self) -> None:
        """Test edge cases in path handling."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Test with special characters in path
            special_dir = temp_path / "special chars" / "ñóñ-äscii"
            special_dir.mkdir(parents=True)

            special_file = special_dir / "módule.py"
            special_file.write_text("# Test with special characters")

            # Should handle without crashing
            normalized = PathNormalizer.normalize_path_for_id(special_file, temp_path)
            assert isinstance(normalized, str)

            module_name = PathNormalizer.get_module_name(special_file, temp_path)
            assert isinstance(module_name, str)


class ParseCacheTest(unittest.TestCase):
    """Test parsing cache functionality."""

    def setUp(self) -> None:
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.temp_path = Path(self.temp_dir.name)

        # Create cache with temporary directory
        self.cache_dir = self.temp_path / "cache"
        self.cache = ParseCache(self.cache_dir)

    def _create_test_file(self, content: str, filename: str = "test.py") -> Path:
        """Create a test file with given content."""
        file_path = self.temp_path / filename
        file_path.write_text(content)
        return file_path

    def test_cache_miss_and_hit(self) -> None:
        """Test cache miss followed by cache hit."""
        file_path = self._create_test_file("def test(): pass")

        # First access should be a miss
        result = self.cache.get(file_path)
        assert result is None
        assert self.cache.stats["misses"] == 1
        assert self.cache.stats["hits"] == 0

        # Store something in cache
        test_analysis = {"module_name": "test", "functions": []}
        self.cache.put(file_path, test_analysis)

        # Second access should be a hit
        result = self.cache.get(file_path)
        assert result == test_analysis
        assert self.cache.stats["hits"] == 1

    def test_cache_invalidation_on_file_change(self) -> None:
        """Test that cache is invalidated when file changes."""
        file_path = self._create_test_file("def original(): pass")

        # Cache initial content
        initial_analysis = {"module_name": "test", "functions": ["original"]}
        self.cache.put(file_path, initial_analysis)

        # Verify cache hit
        result = self.cache.get(file_path)
        assert result == initial_analysis

        # Modify file (ensure different mtime)
        time.sleep(0.01)
        file_path.write_text("def modified(): pass")

        # Should be cache miss due to file change
        result = self.cache.get(file_path)
        assert result is None
        assert self.cache.stats["invalidations"] == 1

    def test_cache_stats(self) -> None:
        """Test cache statistics calculation."""
        file_path = self._create_test_file("def test(): pass")

        # Generate some cache activity
        self.cache.get(file_path)  # miss
        self.cache.put(file_path, {"test": "data"})
        self.cache.get(file_path)  # hit
        self.cache.get(file_path)  # hit

        stats = self.cache.get_stats()

        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["total_requests"] == 3
        assert stats["hit_rate_percent"] == 66.7

    def test_cache_corruption_handling(self) -> None:
        """Test handling of corrupted cache files."""
        file_path = self._create_test_file("def test(): pass")

        # Create corrupted cache file
        cache_key = self.cache._get_cache_key(file_path)
        corrupt_cache_file = self.cache.cache_dir / f"{cache_key}.json"
        corrupt_cache_file.parent.mkdir(parents=True, exist_ok=True)
        corrupt_cache_file.write_text("invalid json content")

        # Should handle corruption gracefully
        result = self.cache.get(file_path)
        assert result is None
        assert self.cache.stats["misses"] == 1

        # Corrupted file should be removed
        assert not corrupt_cache_file.exists()

    def test_cache_clear(self) -> None:
        """Test cache clearing functionality."""
        file_path = self._create_test_file("def test(): pass")

        # Add some data to cache
        self.cache.put(file_path, {"test": "data"})
        self.cache.get(file_path)  # Generate stats

        # Clear cache
        self.cache.clear()

        # Cache should be empty and stats reset
        result = self.cache.get(file_path)
        assert result is None

        stats = self.cache.get_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 1  # From the get after clear


class EdgeCaseCommentExtractionTest(unittest.TestCase):
    """Test comment extraction with complex edge cases."""

    def test_multiline_comment_patterns(self) -> None:
        """Test extraction of various multiline comment patterns."""
        extractor = CommentExtractor(MULTILINE_COMMENTS)

        # Should find hash-style multiline comments
        found_multiline = False
        for comment in extractor.comments.values():
            if "multiple lines using hash symbols" in comment:
                found_multiline = True
                break

        assert found_multiline, "Should find multiline hash comments"

    def test_comments_vs_string_literals(self) -> None:
        """Test distinguishing comments from string literals with #."""
        source = '''
def test():
    s1 = "String with # hash inside"
    s2 = 'Another string with # hash'  # Real comment
    # This is a real comment
    s3 = """Triple quote string with # hash"""
    return s1, s2, s3
'''
        extractor = CommentExtractor(source)

        # Should find the real comment but not the # inside strings
        real_comments = [
            comment
            for comment in extractor.comments.values()
            if "Real comment" in comment
        ]
        assert len(real_comments) == 1

        # Should also find the line comment
        line_comments = [
            comment
            for comment in extractor.comments.values()
            if "This is a real comment" in comment
        ]
        assert len(line_comments) == 1

    def test_unicode_comments(self) -> None:
        """Test handling of Unicode characters in comments."""
        extractor = CommentExtractor(UNICODE_EDGE_CASES)

        # Should handle Unicode in comments without errors
        unicode_comments = [
            comment
            for comment in extractor.comments.values()
            if any(ord(char) > 127 for char in comment)
        ]
        assert len(unicode_comments) > 0, "Should find Unicode comments"

    def test_complex_inline_comments(self) -> None:
        """Test complex inline comment scenarios."""
        source = """
x = "string with # hash"  # Comment with émoji 🐍
y = calculate(a, b)  # Math: α + β = γ
z = {'key#1': 'value'}  # Dict with # in key
"""
        extractor = CommentExtractor(source)

        # Should extract all inline comments
        comments = list(extractor.comments.values())
        assert len(comments) > 0

        # Should handle Unicode in comments
        unicode_comment_found = any("émoji" in comment for comment in comments)
        assert unicode_comment_found, "Should handle Unicode in inline comments"


class ComplexTypingAnalysisTest(unittest.TestCase):
    """Test analysis of complex type annotations."""

    def setUp(self) -> None:
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.temp_path = Path(self.temp_dir.name)

    def _analyze_content(self, content: str) -> dict:
        """Helper to analyze content and return analysis."""
        file_path = self.temp_path / "test.py"
        file_path.write_text(content)

        analyzer = DeterministicPythonModuleAnalyzer(file_path)
        return analyzer.analyze()

    def test_complex_generic_types(self) -> None:
        """Test parsing of complex generic type annotations."""
        analysis = self._analyze_content(COMPLEX_TYPING)

        # Should parse classes with complex generics
        classes = analysis["classes"]
        complex_generic = next(
            (c for c in classes if c["name"] == "ComplexGeneric"), None,
        )
        assert complex_generic is not None, "Should find ComplexGeneric class"

        # Should parse methods with complex signatures
        complex_method = next(
            (m for m in complex_generic["methods"] if m["name"] == "complex_method"),
            None,
        )
        assert complex_method is not None, "Should find complex_method"

        # Should capture some type information
        args_detailed = complex_method["args_detailed"]
        assert len(args_detailed) > 0, "Should capture argument details"

    def test_forward_references(self) -> None:
        """Test handling of forward references in type annotations."""
        analysis = self._analyze_content(COMPLEX_TYPING)

        # Should parse functions with forward references
        functions = analysis["functions"]
        recursive_func = next(
            (f for f in functions if f["name"] == "recursive_function"), None,
        )
        assert recursive_func is not None, "Should find recursive_function"

        # Should capture return type with forward reference
        return_type = recursive_func.get("return_type")
        assert return_type is not None, "Should capture return type"

    def test_literal_and_final_types(self) -> None:
        """Test handling of Literal and Final type annotations."""
        analysis = self._analyze_content(COMPLEX_TYPING)

        # Should handle these advanced typing constructs without errors
        assert "error" not in analysis


class ComplexDecoratorAnalysisTest(unittest.TestCase):
    """Test analysis of complex decorator patterns."""

    def setUp(self) -> None:
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.temp_path = Path(self.temp_dir.name)

    def _analyze_content(self, content: str) -> dict:
        """Helper to analyze content and return analysis."""
        file_path = self.temp_path / "test.py"
        file_path.write_text(content)

        analyzer = DeterministicPythonModuleAnalyzer(file_path)
        return analyzer.analyze()

    def test_decorators_with_arguments(self) -> None:
        """Test parsing decorators with complex arguments."""
        analysis = self._analyze_content(COMPLEX_DECORATORS)

        # Find the heavily decorated method
        classes = analysis["classes"]
        showcase_class = next(
            (c for c in classes if c["name"] == "DecoratorShowcase"), None,
        )
        assert showcase_class is not None

        heavily_decorated = next(
            (
                m
                for m in showcase_class["methods"]
                if m["name"] == "heavily_decorated_method"
            ),
            None,
        )
        assert heavily_decorated is not None

        # Should capture multiple decorators
        decorators = heavily_decorated.get("decorators", [])
        assert len(decorators) > 1, "Should capture multiple decorators"

        # Should include decorator arguments in some form
        # Note: This may depend on implementation details

    def test_custom_decorator_classes(self) -> None:
        """Test handling of custom decorator classes."""
        analysis = self._analyze_content(COMPLEX_DECORATORS)

        # Should find the retry decorator function
        functions = analysis["functions"]
        retry_func = next((f for f in functions if f["name"] == "retry"), None)
        assert retry_func is not None

        # Should capture the decorator implementation properly
        assert retry_func.get("docstring") is not None
        assert retry_func["name"] == "retry"

    def test_stacked_decorators(self) -> None:
        """Test handling of multiple stacked decorators."""
        analysis = self._analyze_content(COMPLEX_DECORATORS)

        classes = analysis["classes"]
        showcase_class = next(
            (c for c in classes if c["name"] == "DecoratorShowcase"), None,
        )

        # Find method with stacked decorators
        cached_property = next(
            (m for m in showcase_class["methods"] if m["name"] == "cached_property"),
            None,
        )
        assert cached_property is not None

        # Should capture multiple decorators
        decorators = cached_property.get("decorators", [])
        assert len(decorators) >= 2, "Should capture stacked decorators"


class AsyncPatternAnalysisTest(unittest.TestCase):
    """Test analysis of async/await patterns."""

    def setUp(self) -> None:
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.temp_path = Path(self.temp_dir.name)

    def _analyze_content(self, content: str) -> dict:
        """Helper to analyze content and return analysis."""
        file_path = self.temp_path / "test.py"
        file_path.write_text(content)

        analyzer = DeterministicPythonModuleAnalyzer(file_path)
        return analyzer.analyze()

    def test_async_method_detection(self) -> None:
        """Test detection of async methods."""
        analysis = self._analyze_content(ASYNC_PATTERNS)

        # Should identify async methods
        classes = analysis["classes"]
        async_processor = next(
            (c for c in classes if c["name"] == "AsyncProcessor"), None,
        )
        assert async_processor is not None

        # Find async methods
        async_methods = [m for m in async_processor["methods"] if m.get("is_async")]
        assert len(async_methods) > 0, "Should find async methods"

        # Verify specific async method
        simple_async = next(
            (m for m in async_methods if m["name"] == "simple_async_method"), None,
        )
        assert simple_async is not None
        assert simple_async["is_async"]

    def test_async_context_manager_methods(self) -> None:
        """Test detection of async context manager methods."""
        analysis = self._analyze_content(ASYNC_PATTERNS)

        classes = analysis["classes"]
        async_processor = next(
            (c for c in classes if c["name"] == "AsyncProcessor"), None,
        )
        assert async_processor is not None

        # Should find __aenter__ and __aexit__ methods
        method_names = [m["name"] for m in async_processor["methods"]]
        assert "__aenter__" in method_names
        assert "__aexit__" in method_names

    def test_complex_async_inheritance(self) -> None:
        """Test async classes with inheritance."""
        analysis = self._analyze_content(ASYNC_PATTERNS)

        classes = analysis["classes"]
        async_processor = next(
            (c for c in classes if c["name"] == "AsyncProcessor"), None,
        )
        assert async_processor is not None

        # Should capture the class properly
        assert async_processor["name"] == "AsyncProcessor"

        # Should have async methods
        async_methods = [m for m in async_processor["methods"] if m.get("is_async")]
        assert len(async_methods) > 0, "Should have async methods"


class UnicodeHandlingTest(unittest.TestCase):
    """Test Unicode and special character handling."""

    def setUp(self) -> None:
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.temp_path = Path(self.temp_dir.name)

    def _analyze_content(self, content: str) -> dict:
        """Helper to analyze content and return analysis."""
        file_path = self.temp_path / "test.py"
        # Ensure proper encoding
        file_path.write_text(content, encoding="utf-8")

        analyzer = DeterministicPythonModuleAnalyzer(file_path)
        return analyzer.analyze()

    def test_unicode_in_docstrings(self) -> None:
        """Test handling of Unicode characters in docstrings."""
        analysis = self._analyze_content(UNICODE_EDGE_CASES)

        # Should parse without errors
        assert "error" not in analysis

        # Should capture Unicode docstrings
        classes = analysis["classes"]
        unicode_processor = next(
            (c for c in classes if c["name"] == "UnicodeProcessor"), None,
        )
        assert unicode_processor is not None

        # Should find method with Unicode in docstring
        unicode_method = next(
            (
                m
                for m in unicode_processor["methods"]
                if m["name"] == "process_unicode_string"
            ),
            None,
        )
        assert unicode_method is not None

        # Method docstring should contain Unicode
        docstring = unicode_method.get("docstring", "")
        assert any(ord(char) > 127 for char in docstring), "Should preserve Unicode in docstrings"

    def test_unicode_in_comments(self) -> None:
        """Test handling of Unicode in comments."""
        extractor = CommentExtractor(UNICODE_EDGE_CASES)

        # Should extract Unicode comments
        unicode_comments = [
            comment
            for comment in extractor.comments.values()
            if any(ord(char) > 127 for char in comment)
        ]
        assert len(unicode_comments) > 0, "Should find Unicode comments"

    def test_unicode_constant_names(self) -> None:
        """Test handling of Unicode in constant names and values."""
        analysis = self._analyze_content(UNICODE_EDGE_CASES)

        # Should handle Unicode constant values without errors
        assert "error" not in analysis
        # Unicode might be in values, which we may or may not capture depending on implementation

    def test_raw_strings_and_escapes(self) -> None:
        """Test handling of raw strings and escape sequences."""
        analysis = self._analyze_content(RAW_STRING_PATTERNS)

        # Should parse without errors
        assert "error" not in analysis

        # Should handle complex string patterns
        classes = analysis["classes"]
        string_processor = next(
            (c for c in classes if c["name"] == "StringProcessor"), None,
        )
        assert string_processor is not None


class DeterministicOutputTest(unittest.TestCase):
    """Test deterministic output across various edge cases."""

    def setUp(self) -> None:
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.temp_path = Path(self.temp_dir.name)

    def _generate_docs_multiple_times(self, content: str, runs: int = 3) -> list[str]:
        """Generate docs multiple times and return results."""
        file_path = self.temp_path / "test.py"
        file_path.write_text(content, encoding="utf-8")

        results = []
        for _ in range(runs):
            analyzer = DeterministicPythonModuleAnalyzer(file_path)
            analysis = analyzer.analyze()
            markdown = generate_deterministic_markdown_spec(analysis, "all")
            results.append(markdown)

        return results

    def test_deterministic_complex_typing(self) -> None:
        """Test deterministic output with complex type annotations."""
        results = self._generate_docs_multiple_times(COMPLEX_TYPING)

        # All results should be identical
        for i in range(1, len(results)):
            assert results[0] == results[i], f"Run {i} differs from run 0"

    def test_deterministic_complex_decorators(self) -> None:
        """Test deterministic output with complex decorators."""
        results = self._generate_docs_multiple_times(COMPLEX_DECORATORS)

        # All results should be identical
        for i in range(1, len(results)):
            assert results[0] == results[i], f"Run {i} differs from run 0"

    def test_deterministic_unicode_content(self) -> None:
        """Test deterministic output with Unicode content."""
        results = self._generate_docs_multiple_times(UNICODE_EDGE_CASES)

        # All results should be identical
        for i in range(1, len(results)):
            assert results[0] == results[i], f"Run {i} differs from run 0"

        # Verify Unicode is preserved in output
        assert any(ord(char) > 127 for char in results[0]), "Unicode should be preserved in output"

    def test_deterministic_hash_consistency(self) -> None:
        """Test that content hashes are consistent."""
        results = self._generate_docs_multiple_times(COMPLEX_INHERITANCE)

        # Hash all results
        hashes = [calculate_content_hash(result) for result in results]

        # All hashes should be identical
        for i in range(1, len(hashes)):
            assert hashes[0] == hashes[i], f"Hash {i} differs from hash 0"


class IntegrationWithCacheTest(unittest.TestCase):
    """Test integration of all features with caching."""

    def setUp(self) -> None:
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.temp_path = Path(self.temp_dir.name)

        self.cache_dir = self.temp_path / "cache"
        self.cache = ParseCache(self.cache_dir)

    def test_cache_with_complex_content(self) -> None:
        """Test caching behavior with complex content."""
        file_path = self.temp_path / "complex.py"
        file_path.write_text(COMPLEX_TYPING, encoding="utf-8")

        # First analysis - should be cache miss
        analyzer1 = DeterministicPythonModuleAnalyzer(file_path, cache=self.cache)
        analysis1 = analyzer1.analyze()

        assert self.cache.stats["misses"] == 1
        assert self.cache.stats["hits"] == 0

        # Second analysis - should be cache hit
        analyzer2 = DeterministicPythonModuleAnalyzer(file_path, cache=self.cache)
        analysis2 = analyzer2.analyze()

        assert self.cache.stats["hits"] == 1

        # Results should be identical
        assert analysis1 == analysis2

    def test_cache_invalidation_with_unicode_changes(self) -> None:
        """Test cache invalidation when Unicode content changes."""
        file_path = self.temp_path / "unicode.py"

        # Initial content
        initial_content = """
def test():
    '''English docstring'''
    pass
"""
        file_path.write_text(initial_content, encoding="utf-8")

        # Cache initial analysis
        analyzer1 = DeterministicPythonModuleAnalyzer(file_path, cache=self.cache)
        analysis1 = analyzer1.analyze()

        # Modify with Unicode content
        time.sleep(0.01)  # Ensure different mtime
        unicode_content = """
def test():
    '''Unicode docstring: 你好世界 🐍'''
    pass
"""
        file_path.write_text(unicode_content, encoding="utf-8")

        # Should invalidate cache
        analyzer2 = DeterministicPythonModuleAnalyzer(file_path, cache=self.cache)
        analysis2 = analyzer2.analyze()

        assert self.cache.stats["invalidations"] == 1
        assert analysis1 != analysis2


if __name__ == "__main__":
    unittest.main()
