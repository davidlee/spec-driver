"""Tests for spec_driver.migrations._protocol (frozen-forever invariants)."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from spec_driver.migrations._protocol import (
  BaseMigrationStep,
  MigrationStep,
  StepPreview,
  StepResult,
)


class TestDataclassesFrozen:
  """StepPreview/StepResult are frozen — reassignment raises."""

  def test_step_preview_frozen(self) -> None:
    p = StepPreview(touched=[], skipped=[], drift=[])
    with pytest.raises(FrozenInstanceError):
      p.touched = [Path("x")]  # type: ignore[misc]

  def test_step_result_frozen(self) -> None:
    r = StepResult(touched=[], skipped=[])
    with pytest.raises(FrozenInstanceError):
      r.touched = [Path("x")]  # type: ignore[misc]

  def test_step_result_drift_entries_default_empty(self) -> None:
    r = StepResult(touched=[Path("a")], skipped=[])
    assert r.drift_entries == []


class TestBaseMigrationStep:
  """BaseMigrationStep ergonomics + Protocol conformance."""

  def test_base_satisfies_protocol(self) -> None:
    class _Step(BaseMigrationStep):
      applies_to_kind = "delta"
      description = "demo"

      def preview(self, file_path: Path) -> StepPreview:
        return StepPreview(touched=[], skipped=[], drift=[])

      def apply(self, file_path: Path) -> StepResult:
        return StepResult(touched=[], skipped=[])

    step = _Step()
    assert isinstance(step, MigrationStep)
    assert step.applies_to_kind == "delta"
    assert step.applies_to(Path("anywhere.md")) is True

  def test_unimplemented_preview_raises(self) -> None:
    class _Step(BaseMigrationStep):
      applies_to_kind = "delta"
      description = "demo"

    with pytest.raises(NotImplementedError):
      _Step().preview(Path("x.md"))

  def test_unimplemented_apply_raises(self) -> None:
    class _Step(BaseMigrationStep):
      applies_to_kind = "delta"
      description = "demo"

    with pytest.raises(NotImplementedError):
      _Step().apply(Path("x.md"))


class TestStructuralProtocol:
  """Structural typing — non-inheriting classes still satisfy the protocol."""

  def test_duck_typed_step(self) -> None:
    class _DuckStep:
      applies_to_kind = "spec"
      description = "duck"

      def applies_to(self, file_path: Path) -> bool:
        return True

      def preview(self, file_path: Path) -> StepPreview:
        return StepPreview(touched=[], skipped=[], drift=[])

      def apply(self, file_path: Path) -> StepResult:
        return StepResult(touched=[], skipped=[])

    assert isinstance(_DuckStep(), MigrationStep)
