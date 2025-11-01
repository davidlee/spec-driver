# supekku.scripts.lib.changes.creation

Utilities for creating change artifacts like deltas and revisions.

## Constants

- `PHASE_TEMPLATE`
- `PLAN_TEMPLATE`
- `REPO_ROOT`
- `REVISION_TEMPLATE`
- `TEMPLATE_DIR`
- `_DELTA_RELATIONSHIPS_PATTERN`
- `_PHASE_OVERVIEW_PATTERN`
- `_PLAN_OVERVIEW_PATTERN`
- `__all__`

## Functions

- `_ensure_directory(path) -> None`
- `_next_identifier(base_dir, prefix) -> str`
- `_render_delta_relationship_block(delta_id, specs, requirements) -> str`
- `_render_phase_overview_block(phase_id, plan_id, delta_id) -> str`
- `_render_plan_overview_block(plan_id, delta_id, specs, requirements, first_phase_id) -> str`
- `_yaml_list(key, values, level) -> str`
- `create_delta(name) -> ChangeArtifactCreated`: Create a new delta artifact with optional implementation plan.

Args:
  name: Delta name/title.
  specs: Spec IDs impacted.
  requirements: Requirement IDs impacted.
  repo_root: Optional repository root. Auto-detected if not provided.
  allow_missing_plan: If True, skip creating implementation plan and phases.

Returns:
  ChangeArtifactCreated with delta details and optional plan/phase paths.
- `create_requirement_breakout(spec_id, requirement_id) -> Path`: Create a breakout requirement file under a spec.

Args:
  spec_id: Parent spec identifier.
  requirement_id: Requirement code (e.g., FR-010).
  title: Requirement title.
  kind: Optional requirement kind. Defaults based on requirement_id prefix.
  repo_root: Optional repository root. Auto-detected if not provided.

Returns:
  Path to created requirement file.

Raises:
  ValueError: If spec is not found.
- `create_revision(name) -> ChangeArtifactCreated`: Create a new spec revision artifact.

Args:
  name: Revision name/title.
  summary: Optional summary text.
  source_specs: Spec IDs being revised from.
  destination_specs: Spec IDs being revised to.
  requirements: Requirement IDs affected.
  repo_root: Optional repository root. Auto-detected if not provided.

Returns:
  ChangeArtifactCreated with revision details.

## Classes

### ChangeArtifactCreated

Result information from creating a change artifact.
