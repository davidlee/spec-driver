"""Migration step Protocol + dataclasses (frozen-forever per DEC-137-26).

This module's behaviour and public signatures are frozen. Changes that
break the API are framework v2 work, gated by ``/scope-delta``. Bug
fixes that preserve behaviour/signature are allowed (F-35).

The Protocol is structural — step authors may implement it either by
inheriting ``BaseMigrationStep`` (recommended ergonomic default) or
by declaring an attribute/method-compatible class directly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class StepPreview:
  """Dry-run result describing what a step would do for one file."""

  touched: list[Path]
  skipped: list[Path]
  drift: list[str]


@dataclass(frozen=True)
class StepResult:
  """Outcome of applying a step to one file."""

  touched: list[Path]
  skipped: list[Path]
  drift_entries: list[Path] = field(default_factory=list)


@runtime_checkable
class MigrationStep(Protocol):
  """A single forward-only migration step targeting one artefact kind.

  ``applies_to_kind`` is singular (DEC-137-16, F-4). Multi-kind work
  is expressed as sibling steps, one per kind, with distinct
  ordinals — never a single step touching multiple kinds.
  """

  applies_to_kind: str
  description: str

  def applies_to(self, file_path: Path) -> bool:  # pragma: no cover
    ...

  def preview(self, file_path: Path) -> StepPreview:  # pragma: no cover
    ...

  def apply(self, file_path: Path) -> StepResult:  # pragma: no cover
    ...


class BaseMigrationStep:
  """Optional concrete base for migration steps wanting default ergonomics.

  Subclasses MUST override ``applies_to_kind`` and ``description``.
  The default ``applies_to`` returns ``True``: the orchestrator has
  already kind-filtered before calling, so every file of the right
  kind is in scope unless the subclass overrides for finer
  discrimination (e.g. "only files lacking the new block").

  Frozen-forever alongside the Protocol (DEC-137-26).
  """

  applies_to_kind: str = ""
  description: str = ""

  def applies_to(self, file_path: Path) -> bool:  # pylint: disable=unused-argument
    return True

  def preview(self, file_path: Path) -> StepPreview:  # pragma: no cover
    raise NotImplementedError

  def apply(self, file_path: Path) -> StepResult:  # pragma: no cover
    raise NotImplementedError
