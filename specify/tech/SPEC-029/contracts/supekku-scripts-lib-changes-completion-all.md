# supekku.scripts.lib.changes.completion

Utilities for creating completion revisions.

Documenting delta lifecycle transitions.

## Constants

- `__all__`

## Functions

- `_render_revision_change_block(revision_id, delta_id, requirements) -> str`: Render a revision.change YAML block.

Documenting requirement lifecycle transitions.

Args:
    revision_id: Revision ID (e.g., RE-042)
    delta_id: Delta ID that implemented the requirements
    requirements: List of (requirement_id, spec_id, summary) tuples

Returns:
    Formatted YAML block as a string
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
