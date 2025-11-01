# supekku.scripts.lib.changes.completion

Utilities for creating completion revisions.

Documenting delta lifecycle transitions.

## Functions

- `create_completion_revision(delta_id, requirements, workspace) -> str`: Create a completion revision documenting delta lifecycle transitions.

This revision documents requirements that were implemented by a delta
but didn't have prior lifecycle tracking in revision files.

Args:
    delta_id: Delta ID (e.g., DE-003)
    requirements: List of requirement IDs to document
    workspace: Workspace for accessing registries
    revision_name: Optional custom revision name
        (defaults to "Delta {delta_id} completion")

Returns:
    New revision ID (e.g., RE-042)

Raises:
    ValueError: If requirements not found in registry - Rationale: Revision creation requires gathering data from multiple sources
