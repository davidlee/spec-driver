"""Language adapters for specification synchronization."""

from .base import LanguageAdapter
from .go import GoAdapter
from .python import PythonAdapter
from .typescript import TypeScriptAdapter
from .zig import ZigAdapter

__all__ = [
  "GoAdapter",
  "LanguageAdapter",
  "PythonAdapter",
  "TypeScriptAdapter",
  "ZigAdapter",
]
