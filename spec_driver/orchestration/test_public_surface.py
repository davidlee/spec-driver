"""Import smoke test for spec_driver.orchestration public surface (DE-124)."""

from __future__ import annotations

import spec_driver.orchestration as pub
from spec_driver.orchestration.operations import (
  DeltaNotFoundError,
  DispositionValidationError,
  FindingNotFoundError,
  ReviewApprovalGuardError,
  complete_review,
  disposition_finding,
  prime_review,
  resolve_delta_dir,
  summarize_review,
  teardown_review,
)
from supekku.scripts.lib.workflow.review_state_machine import (
  BootstrapStatus,
  DispositionAuthority,
  FindingDispositionAction,
  FindingStatus,
  ReviewStatus,
)
from supekku.scripts.lib.workflow.state_machine import WorkflowState


def test_all_symbols_importable() -> None:
  """Every symbol in __all__ is importable via the public module."""
  for name in pub.__all__:
    assert hasattr(pub, name), f"Missing from public surface: {name}"


def test_all_symbols_count() -> None:
  """Guard against accidental symbol removal."""
  assert len(pub.__all__) >= 46


def test_operation_identity() -> None:
  """Operations are the same objects, not copies."""
  assert pub.resolve_delta_dir is resolve_delta_dir
  assert pub.prime_review is prime_review
  assert pub.complete_review is complete_review
  assert pub.disposition_finding is disposition_finding
  assert pub.teardown_review is teardown_review
  assert pub.summarize_review is summarize_review


def test_type_identity() -> None:
  """Enums and models are identity-equal to their sources."""
  assert pub.BootstrapStatus is BootstrapStatus
  assert pub.ReviewStatus is ReviewStatus
  assert pub.FindingStatus is FindingStatus
  assert pub.FindingDispositionAction is FindingDispositionAction
  assert pub.DispositionAuthority is DispositionAuthority
  assert pub.WorkflowState is WorkflowState


def test_exception_identity() -> None:
  """Exception classes are importable for typed except handling."""
  assert pub.DeltaNotFoundError is DeltaNotFoundError
  assert pub.ReviewApprovalGuardError is ReviewApprovalGuardError
  assert pub.FindingNotFoundError is FindingNotFoundError
  assert pub.DispositionValidationError is DispositionValidationError
