"""Registry integrity checks.

Verifies that all registries load without errors.
"""

from __future__ import annotations

from supekku.scripts.lib.diagnostics.models import DiagnosticResult, DiagnosticWorkspace

CATEGORY = "registries"

# (label, accessor-attribute) pairs for registries to check.
# Each accessor is a Workspace property name that returns a registry
# with a .collect() method.
_REGISTRIES: list[tuple[str, str]] = [
  ("specs", "specs"),
  ("deltas", "delta_registry"),
  ("revisions", "revision_registry"),
  ("audits", "audit_registry"),
  ("decisions", "decisions"),
]


def check_registries(ws: DiagnosticWorkspace) -> list[DiagnosticResult]:
  """Load all registries and report any that fail to collect."""
  results: list[DiagnosticResult] = []

  for label, attr in _REGISTRIES:
    try:
      registry = getattr(ws, attr)
      items = registry.collect()
      results.append(
        DiagnosticResult(
          category=CATEGORY,
          name=label,
          status="pass",
          message=f"{label}: {len(items)} items loaded",
        ),
      )
    except Exception as exc:  # noqa: BLE001
      results.append(
        DiagnosticResult(
          category=CATEGORY,
          name=label,
          status="fail",
          message=f"{label}: load error — {exc}",
          suggestion=f"Check {label} artifacts for malformed frontmatter",
        ),
      )

  return results
