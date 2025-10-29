"""
Language adapters for specification synchronization.
"""

from .base import LanguageAdapter
from .go import GoAdapter
from .python import PythonAdapter
from .typescript import TypeScriptAdapter

__all__ = ["LanguageAdapter", "GoAdapter", "PythonAdapter", "TypeScriptAdapter"]
