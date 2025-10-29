"""
Test fixtures for AST documentation generator tests.
Contains various Python code patterns to test parsing functionality.
"""

# Simple class with methods
SIMPLE_CLASS = '''
class Calculator:
    """A simple calculator class."""

    def __init__(self):
        """Initialize the calculator."""
        self.value = 0

    def add(self, x: int) -> int:
        """Add a number to the current value."""
        self.value += x
        return self.value

    def _private_method(self):
        """A private method."""
        return "private"
'''

# Complex type annotations
COMPLEX_TYPES = '''
from typing import Dict, List, Optional, Union, Tuple, Generic, TypeVar
from collections.abc import Callable

T = TypeVar('T')

class DataProcessor(Generic[T]):
    """A generic data processor."""

    def process(
        self,
        data: List[Dict[str, Union[int, str]]],
        callback: Optional[Callable[[T], bool]] = None
    ) -> Tuple[List[T], Dict[str, int]]:
        """Process data with complex types."""
        pass

    def get_nested(self) -> Dict[str, List[Optional[int]]]:
        """Return nested optional types."""
        return {}
'''

# Multiple decorators
DECORATOR_HEAVY = '''
from functools import wraps
from typing import Any

def my_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

class Service:
    """A service class with decorators."""

    @property
    def name(self) -> str:
        """Service name property."""
        return "service"

    @staticmethod
    @my_decorator
    def static_method(x: int) -> int:
        """A decorated static method."""
        return x * 2

    @classmethod
    def from_config(cls, config: dict) -> 'Service':
        """Create service from config."""
        return cls()
'''

# Various comment styles
COMMENT_VARIATIONS = '''
# Module level comment
import sys

class CommentedClass:
    # Class level comment
    """Class docstring."""

    def method_with_inline_comment(self):
        x = 1  # Inline comment
        # Comment before return
        return x

    def method_with_block_comment(self):
        """Method with block comment."""
        # This is a multi-line comment
        # that spans several lines
        # and explains the logic
        result = 42
        return result

# Function with comment
def standalone_function():
    # Function comment
    pass
'''

# Inheritance and class hierarchies
INHERITANCE_EXAMPLE = '''
from abc import ABC, abstractmethod

class BaseProcessor(ABC):
    """Abstract base processor."""

    @abstractmethod
    def process(self, data: str) -> str:
        """Process the data."""
        pass

class TextProcessor(BaseProcessor):
    """Concrete text processor."""

    def process(self, data: str) -> str:
        """Process text data."""
        return data.upper()

    def additional_method(self) -> bool:
        """Additional method in subclass."""
        return True

class AdvancedTextProcessor(TextProcessor):
    """Advanced text processor with more features."""

    def process(self, data: str) -> str:
        """Override with advanced processing."""
        return super().process(data) + "!"
'''

# Module with just functions and constants
FUNCTIONS_AND_CONSTANTS = '''
"""Module with functions and constants."""

# Constants
MAX_SIZE = 1000
DEFAULT_NAME = "unknown"

def calculate_area(width: float, height: float) -> float:
    """Calculate rectangle area."""
    return width * height

def format_name(first: str, last: str) -> str:
    """Format a full name."""
    return f"{first} {last}"

async def async_function(url: str) -> dict:
    """An async function."""
    return {"url": url}
'''

# Test module (should only appear in tests documentation)
TEST_MODULE = '''
"""Test module for testing documentation generation."""
import unittest

class TestCalculator(unittest.TestCase):
    """Test the Calculator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.calc = Calculator()

    def test_add(self):
        """Test addition functionality."""
        result = self.calc.add(5)
        self.assertEqual(result, 5)

    def test_private_method_access(self):
        """Test private method access."""
        result = self.calc._private_method()
        self.assertEqual(result, "private")

if __name__ == "__main__":
    unittest.main()
'''

# Empty or minimal module
MINIMAL_MODULE = '''
"""A minimal module for testing edge cases."""

pass
'''

# Module with syntax errors (for error handling tests)
SYNTAX_ERROR_MODULE = """
class BrokenClass:
    def method_with_syntax_error(self:
        return "missing closing parenthesis"
"""
