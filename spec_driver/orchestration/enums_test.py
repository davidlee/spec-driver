"""Tests for the post-split ENUM_REGISTRY (DE-137 IP-137-P01 task 1.11).

VT-CC-012 parity: the Category A derived view must emit the same sorted
enum values as the pre-split hardcoded lambdas. The snapshot below was
captured against `main` immediately before the registry refactor and is
the canonical reference for any future regression check.
"""

from __future__ import annotations

import pytest

from spec_driver.orchestration.enums import (
  ENUM_REGISTRY,
  get_enum_values,
  list_enum_paths,
)

# Pre-split ENUM_REGISTRY snapshot (DR-137 VT-CC-012). Generated via the
# legacy lambda providers on `main` at IP-137-P01 entry. Every entry is the
# sorted list the post-split derived view must continue to produce.
PRE_SPLIT_SNAPSHOT: dict[str, list[str]] = {
  "adr.status": [
    "accepted",
    "deprecated",
    "draft",
    "proposed",
    "rejected",
    "revision-required",
    "superseded",
  ],
  "audit.status": ["completed", "deferred", "draft", "in-progress", "pending"],
  "backlog.status": ["in-progress", "open", "resolved", "triaged"],
  "command.format": ["json", "table", "tsv"],
  "delta.status": ["completed", "deferred", "draft", "in-progress", "pending"],
  "drift.status": ["closed", "open"],
  "improvement.status": ["in-progress", "open", "resolved", "triaged"],
  "issue.status": ["in-progress", "open", "resolved", "triaged"],
  "memory.status": ["active", "archived", "draft", "review", "superseded"],
  "phase.status": ["completed", "deferred", "draft", "in-progress", "pending"],
  "policy.status": ["deprecated", "draft", "required"],
  "problem.status": ["in-progress", "open", "resolved", "triaged"],
  "requirement.kind": ["FR", "NF"],
  "requirement.status": [
    "active",
    "deprecated",
    "in-progress",
    "pending",
    "retired",
    "superseded",
  ],
  "revision.status": ["completed", "deferred", "draft", "in-progress", "pending"],
  "risk.status": [
    "accepted",
    "expired",
    "in-progress",
    "open",
    "resolved",
    "triaged",
  ],
  "spec.kind": ["prod", "tech"],
  "spec.status": ["active", "archived", "deprecated", "draft", "stub"],
  "standard.status": ["default", "deprecated", "draft", "required"],
  "verification.kind": ["VA", "VH", "VT"],
  "verification.status": [
    "blocked",
    "failed",
    "in-progress",
    "planned",
    "verified",
  ],
}


@pytest.mark.parametrize("path", sorted(PRE_SPLIT_SNAPSHOT))
def test_post_split_parity(path: str) -> None:
  """VT-CC-012: every snapshot path returns identical values post-split."""
  assert get_enum_values(path) == PRE_SPLIT_SNAPSHOT[path]


def test_no_paths_dropped_in_split() -> None:
  """The post-split registry covers every pre-split path."""
  registered = set(list_enum_paths())
  missing = sorted(set(PRE_SPLIT_SNAPSHOT) - registered)
  assert missing == [], f"paths dropped from ENUM_REGISTRY: {missing}"


def test_no_new_paths_unexpectedly() -> None:
  """The split should not silently introduce paths outside the snapshot."""
  registered = set(list_enum_paths())
  extra = sorted(registered - set(PRE_SPLIT_SNAPSHOT))
  assert extra == [], f"unexpected paths added to ENUM_REGISTRY: {extra}"


def test_registry_contract() -> None:
  """Providers return sorted lists; lookups round-trip via `get_enum_values`."""
  for path, provider in ENUM_REGISTRY.items():
    values = provider()
    assert isinstance(values, list)
    assert values == sorted(values), f"{path} not sorted"
    assert get_enum_values(path) == values
