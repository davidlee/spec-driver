"""
Multi-language specification synchronization engine.

This package provides a pluggable architecture for synchronizing technical
specifications with source code across multiple programming languages.
"""

from .engine import SpecSyncEngine
from .models import DocVariant, SyncOutcome, SourceDescriptor, SourceUnit

__all__ = [
    "SpecSyncEngine",
    "SourceUnit",
    "SourceDescriptor",
    "DocVariant",
    "SyncOutcome",
]
