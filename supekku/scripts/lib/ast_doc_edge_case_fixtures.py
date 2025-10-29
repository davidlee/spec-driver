"""
Additional test fixtures for edge cases in AST documentation generation.
Covers multiline comments, complex typing, decorators with arguments, and other edge cases.
"""

# Multiline comments and docstrings with edge cases
MULTILINE_COMMENTS = '''
"""
Module docstring that spans
multiple lines with various
formatting styles.
"""

# This is a comment that spans
# multiple lines using hash symbols
# each line has its own hash

class MultilineDocstring:
    """
    A class with complex docstring formatting.

    This docstring contains:
    - Lists
    - Code examples:

        x = 1 + 2

    - Special characters: <>{}[]()
    """

    def method_with_multiline_comment(self):
        """Single line docstring."""
        # Comment block before variable
        # This explains what x does
        # Over multiple lines
        x = 42  # Inline comment
        return x

    def method_with_mixed_quotes(self):
        """Method with 'single' and "double" quotes in docstring."""
        s1 = "String with # hash inside"
        s2 = 'Another string with # hash'
        return s1, s2
'''

# Complex generic types and typing constructs
COMPLEX_TYPING = '''
from typing import (
    Union, Optional, List, Dict, Tuple, Callable, TypeVar, Generic,
    Protocol, Literal, Final, ClassVar, Any
)
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

T = TypeVar('T', bound='Comparable')
U = TypeVar('U', covariant=True)

class Comparable(Protocol):
    def __lt__(self, other: 'Comparable') -> bool: ...

@dataclass
class ComplexGeneric(Generic[T, U]):
    """A class with complex generic typing."""

    data: Dict[str, Union[int, float, str]]
    nested: Dict[str, List[Optional[Tuple[int, ...]]]]
    callback: Optional[Callable[[T], Union[U, None]]]
    mapping: Mapping[str, Sequence[int]] = field(default_factory=dict)

    # Class variables with complex types
    REGISTRY: ClassVar[Dict[str, 'ComplexGeneric[Any, Any]']] = {}
    DEFAULT_CONFIG: Final[Dict[str, Union[str, int]]] = {"timeout": 30}

    def complex_method(
        self,
        items: List[Dict[str, Union[int, str, List[int]]]],
        processor: Callable[[Dict[str, Any]], Optional[T]],
        *args: Union[str, int],
        **kwargs: Any
    ) -> Tuple[List[T], Dict[str, Union[Exception, None]]]:
        """Method with very complex type signatures."""
        pass

    async def async_complex_method(
        self,
        data: Union[
            Dict[str, List[Optional[int]]],
            List[Dict[str, Union[str, float]]]
        ]
    ) -> Dict[str, Union[List[T], Exception]]:
        """Async method with nested union types."""
        pass

    @classmethod
    def from_literal(
        cls,
        mode: Literal['strict', 'permissive', 'debug']
    ) -> 'ComplexGeneric[str, int]':
        """Method using Literal types."""
        pass

# Forward references and recursive types
RecursiveDict = Dict[str, Union[str, 'RecursiveDict']]

def recursive_function(
    data: RecursiveDict,
    transform: Callable[['RecursiveDict'], 'RecursiveDict']
) -> RecursiveDict:
    """Function with recursive type definitions."""
    pass
'''

# Decorators with complex arguments
COMPLEX_DECORATORS = '''
import functools
from typing import Any, Callable, TypeVar, cast

F = TypeVar('F', bound=Callable[..., Any])

def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    exceptions: tuple = (Exception,)
):
    """Decorator with multiple arguments."""
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == max_attempts - 1:
                        raise
            return func(*args, **kwargs)
        return cast(F, wrapper)
    return decorator

def validate_types(**type_hints):
    """Decorator that validates argument types."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Type validation logic here
            return func(*args, **kwargs)
        return wrapper
    return decorator

class DecoratorShowcase:
    """Class demonstrating various decorator patterns."""

    @property
    def simple_property(self) -> str:
        """A simple property."""
        return "value"

    @property
    @functools.lru_cache(maxsize=128)
    def cached_property(self) -> int:
        """Property with cache decorator."""
        return 42

    @staticmethod
    @retry(max_attempts=5, delay=0.5)
    def static_with_retry(value: int) -> str:
        """Static method with retry decorator."""
        return str(value)

    @classmethod
    @validate_types(cls=type, name=str)
    def class_method_with_validation(cls, name: str) -> 'DecoratorShowcase':
        """Class method with type validation."""
        return cls()

    @retry(
        max_attempts=10,
        delay=2.0,
        exceptions=(ValueError, TypeError, KeyError)
    )
    @validate_types(x=int, y=int, z=(int, float))
    @functools.lru_cache(maxsize=None)
    def heavily_decorated_method(
        self,
        x: int,
        y: int,
        z: Union[int, float] = 0
    ) -> Dict[str, Union[int, float]]:
        """Method with multiple complex decorators."""
        return {"result": x + y + z}
'''

# Unicode and special character handling
UNICODE_EDGE_CASES = '''
# -*- coding: utf-8 -*-
"""
Module with Unicode and special character edge cases.
Contains émojis 🐍, special chars: àáâãäåæçèéêë, and CJK: 中文日本語한국어
"""

class UnicodeProcessor:
    """Class handling Unicode and encoding edge cases."""

    # Constants with Unicode
    EMOJI_MAP = {
        "python": "🐍",
        "fire": "🔥",
        "rocket": "🚀",
        "warning": "⚠️"
    }

    LANGUAGE_SAMPLES = {
        "chinese": "你好世界",
        "japanese": "こんにちは世界",
        "korean": "안녕하세요 세계",
        "arabic": "مرحبا بالعالم",
        "hebrew": "שלום עולם",
        "russian": "Привет мир"
    }

    def process_unicode_string(self, text: str) -> Dict[str, Any]:
        """
        Process string with Unicode characters.

        Handles various encodings: UTF-8, UTF-16, Latin-1, etc.
        Special cases: emoji 🎉, accents áéíóú, symbols ∑∆∏
        """
        return {
            "length": len(text),
            "byte_length": len(text.encode('utf-8')),
            "has_emoji": any(char in self.EMOJI_MAP.values() for char in text)
        }

    def handle_special_comments(self):
        """Method with special characters in comments."""
        # Comment with emoji: This function is 🔥
        # Mathematical symbols: α + β = γ
        # Currency symbols: $, €, £, ¥, ₹, ₿
        # Arrows and symbols: → ← ↑ ↓ ⇒ ⇔ ∞ ∅ ∈ ∉
        value = "Special handling required"  # 特殊处理需要
        return value
'''

# Async/await patterns
ASYNC_PATTERNS = '''
import asyncio
from typing import AsyncIterator, AsyncGenerator, Optional, Any, Dict, List

class AsyncProcessor:
    """Class with various async patterns."""

    def __init__(self, batch_size: int = 10):
        self.batch_size = batch_size

    async def simple_async_method(self, data: str) -> str:
        """Simple async method."""
        await asyncio.sleep(0.01)
        return data.upper()

    async def async_generator_method(
        self,
        items: List[str]
    ) -> AsyncGenerator[str, None]:
        """Async generator method."""
        for item in items:
            await asyncio.sleep(0.01)
            yield await self.simple_async_method(item)

    async def async_iterator_method(
        self,
        count: int
    ) -> AsyncIterator[int]:
        """Async iterator method."""
        for i in range(count):
            await asyncio.sleep(0.01)
            yield i

    async def async_context_manager(self):
        """Async context manager method."""
        return self

    async def __aenter__(self):
        """Async context manager entry."""
        await asyncio.sleep(0.01)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await asyncio.sleep(0.01)
        return False
'''

# Complex inheritance patterns
COMPLEX_INHERITANCE = '''
from abc import ABC, abstractmethod
from typing import Protocol, TypeVar, Generic, Optional, Any, Dict, List

T = TypeVar('T')

class BaseProtocol(Protocol):
    """Protocol defining base behavior."""

    def process(self, data: Any) -> Any: ...
    def validate(self, data: Any) -> bool: ...

class AbstractBase(ABC):
    """Abstract base class with complex methods."""

    def __init__(self, name: str):
        self.name = name
        self._cache: Dict[str, Any] = {}

    @abstractmethod
    def execute(self, data: T) -> T:
        """Abstract method to be implemented by subclasses."""
        pass

    @classmethod
    @abstractmethod
    def create_default(cls) -> 'AbstractBase':
        """Abstract class method."""
        pass

    def shared_logic(self) -> str:
        """Shared implementation across subclasses."""
        return f"Processing with {self.name}"

class GenericMixin(Generic[T]):
    """Generic mixin class."""

    def mixin_method(self, value: T) -> Optional[T]:
        """Method from mixin."""
        return value if self.validate_value(value) else None

    def validate_value(self, value: T) -> bool:
        """Validation logic."""
        return value is not None

class ConcreteImplementation(AbstractBase, GenericMixin[str]):
    """Concrete class with multiple inheritance."""

    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name)
        self.config = config

    def execute(self, data: str) -> str:
        """Implementation of abstract method."""
        return f"Executed: {data}"

    @classmethod
    def create_default(cls) -> 'ConcreteImplementation':
        """Implementation of abstract class method."""
        return cls("default", {})

    def process(self, data: Any) -> Any:
        """Implementation of protocol method."""
        return str(data).upper()

    def validate(self, data: Any) -> bool:
        """Implementation of protocol method."""
        return isinstance(data, (str, int, float))

class DiamondInheritance(ConcreteImplementation, BaseProtocol):
    """Class demonstrating diamond inheritance pattern."""

    def __init__(self, name: str, config: Dict[str, Any], extra: str):
        super().__init__(name, config)
        self.extra = extra

    def enhanced_execute(self, data: str) -> str:
        """Enhanced execution with additional logic."""
        base_result = super().execute(data)
        return f"{base_result} + {self.extra}"

# Forward reference handling
class ForwardRef:
    """Class using forward references."""

    def __init__(self, child: Optional['ForwardRef'] = None):
        self.child = child

    def set_parent(self, parent: 'ForwardRef') -> None:
        """Set parent using forward reference."""
        self.parent = parent

    def get_children(self) -> List['ForwardRef']:
        """Get children using forward reference."""
        return [self.child] if self.child else []
'''

# Raw string and escape patterns
RAW_STRING_PATTERNS = '''
import re
from pathlib import Path

class StringProcessor:
    """Class handling various string patterns and escapes."""

    # Raw strings with various patterns
    REGEX_PATTERNS = {
        'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}',
        'url': r'https?://(?:[-\\w.])+(?:[:\\d]+)?(?:/(?:[\\w/_.])*(?:\\?(?:[\\w&=%.])*)?(?:#(?:[\\w.])*)?)?',
        'phone': r'\\+?1?-?\\d{3}-?\\d{3}-?\\d{4}',
        'ipv4': r'\\b(?:[0-9]{1,3}\\.){3}[0-9]{1,3}\\b'
    }

    # String literals with escape sequences
    ESCAPE_SAMPLES = {
        'newlines': 'Line 1\\nLine 2\\nLine 3',
        'tabs': 'Column1\\tColumn2\\tColumn3',
        'quotes': 'He said "Hello" and she replied \\'Hi\\'',
        'backslashes': 'Path: C:\\\\Users\\\\Documents\\\\file.txt',
        'unicode': 'Unicode: \\u03B1\\u03B2\\u03B3 (alpha, beta, gamma)',
        'mixed': 'Mixed\\nescapes\\twith\\r\\ncarriage\\\\returns'
    }

    def __init__(self):
        # Raw string for Windows paths
        self.windows_path = r'C:\\Program Files\\MyApp\\config.ini'
        # Raw string for regex
        self.regex_pattern = r'(?P<name>\\w+)\\s*=\\s*(?P<value>.+)'
        # Raw docstring
        self.raw_docstring = r"""
        Raw docstring with backslashes: \\n, \\t, \\r
        And regex patterns: \\d+, \\w*, \\s+
        """

    def process_raw_strings(self, pattern: str) -> bool:
        """
        Process raw string patterns.

        Args:
            pattern: Raw pattern like r'\\\\d+\\\\w*'

        Returns:
            True if pattern is valid
        """
        try:
            re.compile(pattern)
            return True
        except re.error:
            return False

    def handle_path_strings(self) -> Dict[str, str]:
        """Handle various path string formats."""
        return {
            'raw_windows': r'C:\\Users\\Name\\Documents',
            'raw_unix': r'/home/user/documents',
            'escaped': 'C:\\\\Users\\\\Name\\\\Documents',
            'forward_slash': 'C:/Users/Name/Documents',
            'pathlib': str(Path('home') / 'user' / 'documents')
        }

    def triple_quote_strings(self) -> str:
        """Method with triple-quoted strings."""
        # Using escaped quotes to avoid breaking the surrounding string literal
        single_quotes = "This is a triple-quoted string\\nwith single quotes that can contain \\"double quotes\\"\\nand even more 'single quotes' inside."

        double_quotes = 'This is a triple-quoted string\\nwith double quotes that can contain \\'single quotes\\'\\nand even "more double quotes" inside.'

        return single_quotes + double_quotes

    def complex_string_formatting(self) -> str:
        """Method demonstrating complex string formatting."""
        name = "World"
        number = 42

        # f-strings with expressions
        f_string = f"Hello {name}! The answer is {number * 2}."

        # Format strings
        format_string = "Hello {}! The answer is {}.".format(name, number)

        # Percent formatting
        percent_string = "Hello %s! The answer is %d." % (name, number)

        # Raw f-string
        raw_f_string = rf"Pattern: \\d+\\s+{name}"

        return f_string + format_string + percent_string + raw_f_string
'''
