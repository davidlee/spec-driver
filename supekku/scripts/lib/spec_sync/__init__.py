"""Multi-language specification synchronization engine.

This package provides a pluggable architecture for synchronizing technical
specifications with source code across multiple programming languages.
"""

from .engine import SpecSyncEngine
from .models import DocVariant, SourceDescriptor, SourceUnit, SyncOutcome

__all__ = [
  "DocVariant",
  "SourceDescriptor",
  "SourceUnit",
  "SpecSyncEngine",
  "SyncOutcome",
]
