"""Check category registry for workspace diagnostics."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .config import check_config
from .deps import check_deps
from .lifecycle import check_lifecycle
from .refs import check_refs
from .registries import check_registries
from .structure import check_structure

if TYPE_CHECKING:
  from collections.abc import Callable

  from supekku.scripts.lib.diagnostics.models import (
    DiagnosticResult,
    DiagnosticWorkspace,
  )

  CheckFn = Callable[[DiagnosticWorkspace], list[DiagnosticResult]]

# Ordered registry of check categories.
# Runner iterates this in order; --check filters by key.
CHECK_REGISTRY: dict[str, CheckFn] = {
  "deps": check_deps,
  "config": check_config,
  "structure": check_structure,
  "registries": check_registries,
  "refs": check_refs,
  "lifecycle": check_lifecycle,
}

__all__ = ["CHECK_REGISTRY"]
