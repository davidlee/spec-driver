"""Cross-artifact reference graph — workspace-dependent collection.

Pure graph types, construction, and query functions have moved to
``spec_driver.domain.relations.graph``. This module re-exports those
and retains the workspace-dependent artifact collection functions
until orchestration boundaries are established.

Design reference: DR-097, DR-125.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any  # noqa: F401

from spec_driver.domain.relations.graph import (  # noqa: F401
  GraphEdge,
  ReferenceGraph,
  _build_indices,
  _hit_to_edge,
  build_reference_graph_from_artifacts,
  find_unresolved_references,
  query_forward,
  query_inverse,
  query_neighbourhood,
)

if TYPE_CHECKING:
  from supekku.scripts.lib.workspace import Workspace


def build_reference_graph(workspace: Workspace) -> ReferenceGraph:
  """Build a reference graph from all workspace registries.

  Iterates all registries, calls ``collect_references`` per artifact,
  normalizes edge targets, and builds forward/inverse indices.

  Args:
    workspace: Workspace instance with access to all registries.

  Returns:
    ReferenceGraph computed from current workspace state.
  """
  artifacts = _collect_all_artifacts(workspace)
  return build_reference_graph_from_artifacts(artifacts)


def _collect_all_artifacts(
  workspace: Workspace,
) -> list[tuple[str, str, Any]]:
  """Collect (id, kind, artifact_obj) triples from all registries.

  Uses Workspace properties where available, constructs registries
  directly for domains not yet exposed on Workspace (memory, backlog,
  drift).
  """
  artifacts: list[tuple[str, str, Any]] = []
  _collect_workspace_artifacts(workspace, artifacts)
  _collect_standalone_registry_artifacts(workspace.root, artifacts)
  return artifacts


def _collect_workspace_artifacts(
  workspace: Workspace,
  out: list[tuple[str, str, Any]],
) -> None:
  """Collect artifacts from registries exposed as Workspace properties."""
  # Decisions
  for dec_id, dec in workspace.decisions.collect().items():
    out.append((dec_id, "adr", dec))

  # Specs
  for spec in workspace.specs.all_specs():
    out.append((spec.id, "spec", spec))

  # Changes (delta, revision, audit)
  for registry in (
    workspace.delta_registry,
    workspace.revision_registry,
    workspace.audit_registry,
  ):
    for art_id, art in registry.collect().items():
      out.append((art_id, registry.kind, art))

  # Requirements
  for req_id, req in workspace.requirements.records.items():
    out.append((req_id, "requirement", req))

  # Policies
  for pol_id, pol in workspace.policies.collect().items():
    out.append((pol_id, "policy", pol))

  # Standards
  for std_id, std in workspace.standards.collect().items():
    out.append((std_id, "standard", std))


def _collect_standalone_registry_artifacts(
  root: Any,
  out: list[tuple[str, str, Any]],
) -> None:
  """Collect artifacts from registries not exposed on Workspace."""
  # pylint: disable=import-outside-toplevel
  from supekku.scripts.lib.backlog.registry import BacklogRegistry  # noqa: PLC0415
  from supekku.scripts.lib.drift.registry import DriftLedgerRegistry  # noqa: PLC0415
  from supekku.scripts.lib.memory.registry import MemoryRegistry  # noqa: PLC0415

  for mem_id, mem in MemoryRegistry(root=root).collect().items():
    out.append((mem_id, "memory", mem))

  for item_id, item in BacklogRegistry(root=root).collect().items():
    out.append((item_id, item.kind, item))

  for dl_id, dl in DriftLedgerRegistry(root=root).collect().items():
    out.append((dl_id, "drift_ledger", dl))


__all__ = [
  "GraphEdge",
  "ReferenceGraph",
  "build_reference_graph",
  "build_reference_graph_from_artifacts",
  "find_unresolved_references",
  "query_forward",
  "query_inverse",
  "query_neighbourhood",
]
