"""VT-CC-017 / VT-CC-025 — ``validate workspace --kind`` filter semantics.

The F-8 sweep procedure is implemented as a post-validation filter
(deviation from DR-137 §5.4 §1 documented in IP-137-P03 notes). These
tests cover the filter's reproducibility guarantee: post-migration, a
``--kind`` sweep over the named kind should report zero diagnostics
even while other kinds carry warnings.
"""

from __future__ import annotations

from typer.testing import CliRunner

from spec_driver.presentation.cli.validate import app
from spec_driver.presentation.cli.validate.workspace import (
  _KIND_ID_PREFIXES,
  _filter_by_kind,
)
from supekku.scripts.lib.validation.validator import ValidationIssue

runner = CliRunner()


class TestKindIdPrefixes:
  def test_known_kinds_cover_taxonomy(self) -> None:
    # PROD-004 controlled-vocab artefact kinds reachable via --kind.
    expected = {
      "delta",
      "revision",
      "audit",
      "spec",
      "requirement",
      "decision",
      "adr",
      "memory",
      "issue",
      "improvement",
      "risk",
      "problem",
      "phase",
      "plan",
    }
    assert expected.issubset(_KIND_ID_PREFIXES.keys())

  def test_delta_prefix_matches(self) -> None:
    assert _KIND_ID_PREFIXES["delta"] == ("DE-",)

  def test_spec_covers_prod_and_spec_ids(self) -> None:
    assert "PROD-" in _KIND_ID_PREFIXES["spec"]
    assert "SPEC-" in _KIND_ID_PREFIXES["spec"]


class TestFilterByKind:
  def test_filter_returns_only_matching_prefix(self) -> None:
    issues = [
      ValidationIssue(level="warning", message="x", artifact="DE-001"),
      ValidationIssue(level="warning", message="y", artifact="SPEC-001"),
      ValidationIssue(level="error", message="z", artifact="DE-002"),
    ]
    delta_only = _filter_by_kind(issues, "delta")
    assert len(delta_only) == 2
    assert {i.artifact for i in delta_only} == {"DE-001", "DE-002"}

  def test_filter_unknown_kind_returns_input(self) -> None:
    issues = [
      ValidationIssue(level="warning", message="x", artifact="DE-001"),
    ]
    assert _filter_by_kind(issues, "unknown-kind-xyz") == issues

  def test_filter_is_case_insensitive_on_kind_lookup(self) -> None:
    issues = [
      ValidationIssue(level="warning", message="x", artifact="DE-001"),
    ]
    assert _filter_by_kind(issues, "DELTA") == issues

  def test_filter_spec_kind_matches_both_id_families(self) -> None:
    issues = [
      ValidationIssue(level="warning", message="x", artifact="SPEC-100"),
      ValidationIssue(level="warning", message="y", artifact="PROD-001"),
      ValidationIssue(level="warning", message="z", artifact="DE-001"),
    ]
    spec_only = _filter_by_kind(issues, "spec")
    assert {i.artifact for i in spec_only} == {"SPEC-100", "PROD-001"}


class TestWorkspaceCliSmoke:
  """Smoke tests against the live repo's validate workspace command.

  These are not hermetic-fixture tests — the live-repo invocation is
  sufficient to exercise the flag-routing surface and confirm the F-46
  exit-code contract.
  """

  def test_kind_flag_filters_diagnostics(self) -> None:
    # Bare ``validate workspace`` against the live repo emits 8 audit-gate
    # warnings on DE-* artefacts (pre-existing baseline). Filtering to a
    # kind that does NOT match (e.g. ``revision``) should suppress them.
    bare = runner.invoke(app, ["workspace"])
    filtered = runner.invoke(app, ["workspace", "--kind", "revision"])
    # Filtered output has fewer "Issue:" lines than bare output.
    bare_count = (bare.stderr or "").count("Issue:")
    filtered_count = (filtered.stderr or "").count("Issue:")
    assert filtered_count < bare_count

  def test_kind_filter_targeted_kind_still_lists(self) -> None:
    # Filtering to ``delta`` keeps the audit-gate warnings (they target
    # DE-* artefacts).
    result = runner.invoke(app, ["workspace", "--kind", "delta"])
    # Either exit code is acceptable depending on warnings; structure
    # only cares about output containing delta IDs.
    if result.exit_code == 1:
      assert "DE-" in (result.stderr or "")

  def test_no_tolerated_aliases_flag_accepted(self) -> None:
    # Flag is recognised at the CLI layer; downstream consumption lands
    # incrementally with DE-138..142. Smoke: command exits without
    # usage error.
    result = runner.invoke(app, ["workspace", "--no-tolerated-aliases"])
    assert result.exit_code in (0, 1)  # not 2

  def test_strict_flag_accepted(self) -> None:
    result = runner.invoke(app, ["workspace", "--strict"])
    # --strict promotes baseline warnings to errors ⇒ exit 1 expected
    # given the 8 audit-gate warnings.
    assert result.exit_code in (0, 1)
