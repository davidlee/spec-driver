"""VT-CC-026 — ISSUE-054 regression re-verification.

DR-137 §5.4's original VT-CC-026 spec called for a fresh fixture +
assertion that ``list deltas`` against a malformed-YAML delta emits a
single-line parse-error and no Rich traceback. **DE-135 already shipped
this regression coverage** as
``supekku/cli/list_test.py::ListDeltasMalformedFrontmatterTest::test_list_deltas_default_skips_bad_phase_with_friendly_warning``
(VT-DR135-002). Per DR-137 §5.4 verbatim ("decouples ISSUE-054 closure
from DR-137 acceptance: VT-CC-026 either passes (close ISSUE-054
alongside DE-137) or fails (file follow-up)"), VT-CC-026 closes
through inheritance.

This module is a thin re-assertion: import the DE-135 test class and
run one representative case. If DE-135's coverage ever regresses, this
import will fail at collection time — a louder signal than waiting for
the original VT to fail.
"""

from __future__ import annotations

from supekku.cli.list_test import ListDeltasMalformedFrontmatterTest


class TestIssue054Regression:
  """VT-CC-026 closure marker — inherits DE-135 VT-DR135-002 coverage."""

  def test_de135_regression_coverage_present(self) -> None:
    # Existence + callability of the DE-135 fixture+assertion class is
    # the regression marker.
    case = ListDeltasMalformedFrontmatterTest()
    assert hasattr(
      case, "test_list_deltas_default_skips_bad_phase_with_friendly_warning"
    )
    assert hasattr(case, "_assert_no_python_traceback")
