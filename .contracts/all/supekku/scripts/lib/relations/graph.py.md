# supekku.scripts.lib.relations.graph

Cross-artifact reference graph — workspace-dependent collection.

Pure graph types, construction, and query functions have moved to
``spec_driver.domain.relations.graph``. This module re-exports those
and retains the workspace-dependent artifact collection functions
until orchestration boundaries are established.

Design reference: DR-097, DR-125.

## Constants

- `__all__`

## Functions

- `_collect_all_artifacts(workspace) -> list[tuple[Tuple[str, str, Any]]]`: Collect (id, kind, artifact_obj) triples from all registries.

Uses Workspace properties where available, constructs registries
directly for domains not yet exposed on Workspace (memory, backlog,
drift).
- `_collect_standalone_registry_artifacts(root, out) -> None`: Collect artifacts from registries not exposed on Workspace.
- `_collect_workspace_artifacts(workspace, out) -> None`: Collect artifacts from registries exposed as Workspace properties.
- `build_reference_graph(workspace) -> ReferenceGraph`: Build a reference graph from all workspace registries.

Iterates all registries, calls ``collect_references`` per artifact,
normalizes edge targets, and builds forward/inverse indices.

Args:
  workspace: Workspace instance with access to all registries.

Returns:
  ReferenceGraph computed from current workspace state.
