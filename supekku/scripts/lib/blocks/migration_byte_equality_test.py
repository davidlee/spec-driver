"""VT-DE138-MIG-001 byte-equality assertion (DEC-138-12).

Asserts that the supekku-side ``render_delta_*_block`` helpers and the frozen-
local emitters under ``spec_driver.migrations.v0_10_0_001_delta_blocks._emitters``
produce byte-identical output on identical inputs. Drift between the two would
silently corrupt migrated artefacts; this test pins them together.

Lives on the supekku side because the migration-side module cannot import
``supekku.*`` (``Migrations isolation`` import-linter contract). The supekku
side can freely depend on the migration emitters — the contract is one-way.
"""

from __future__ import annotations

from spec_driver.migrations.v0_10_0_001_delta_blocks._emitters import (
  render_context_inputs_block as migration_render_ctx,
)
from spec_driver.migrations.v0_10_0_001_delta_blocks._emitters import (
  render_relationships_block as migration_render_rel,
)
from spec_driver.migrations.v0_10_0_001_delta_blocks._emitters import (
  render_risk_register_block as migration_render_risk,
)
from supekku.scripts.lib.blocks.delta import (
  render_delta_context_inputs_block,
  render_delta_relationships_block,
  render_delta_risk_register_block,
)


def test_context_inputs_block_byte_equality_empty() -> None:
  assert render_delta_context_inputs_block(entries=[]) == migration_render_ctx(
    entries=[]
  )


def test_context_inputs_block_byte_equality_populated() -> None:
  entries = [
    {"type": "delta", "id": "DE-100", "summary": "An umbrella program"},
    {"type": "adr", "id": "ADR-010"},
    {"type": "document", "id": "DOC-1"},
  ]
  assert render_delta_context_inputs_block(entries=entries) == migration_render_ctx(
    entries=entries
  )


def test_risk_register_block_byte_equality_empty() -> None:
  assert render_delta_risk_register_block(risks=[]) == migration_render_risk(risks=[])


def test_risk_register_block_byte_equality_populated() -> None:
  risks = [
    {
      "id": "DE-138.RISK-01",
      "title": "Sample risk",
      "likelihood": "high",
      "impact": "medium",
      "mitigation": "Tracked in §15",
      "status": "open",
    },
    {
      "id": "DE-138.RISK-02",
      "title": "Second risk",
      "likelihood": "low",
      "impact": "low",
      "status": "mitigated",
    },
  ]
  assert render_delta_risk_register_block(risks=risks) == migration_render_risk(
    risks=risks
  )


def test_relationships_block_byte_equality_empty() -> None:
  assert render_delta_relationships_block("DE-100") == migration_render_rel("DE-100")


def test_relationships_block_byte_equality_populated() -> None:
  kwargs = {
    "primary_specs": ["PROD-004", "SPEC-115"],
    "collaborator_specs": ["SPEC-016"],
    "implements_requirements": ["PROD-004.FR-001", "PROD-004.FR-002"],
    "updates_requirements": ["SPEC-115.FR-001"],
    "verifies_requirements": [],
    "phases": ["IP-138-P01"],
    "introduces_revisions": [],
    "supersedes_revisions": ["RE-040"],
  }
  assert render_delta_relationships_block("DE-138", **kwargs) == migration_render_rel(
    "DE-138", **kwargs
  )
