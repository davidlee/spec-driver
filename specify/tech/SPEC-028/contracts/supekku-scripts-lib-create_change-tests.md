# supekku.scripts.lib.create_change

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
- `create_delta(name) -> ChangeArtifactCreated`
- `create_requirement_breakout(spec_id, requirement_id) -> Path`
- `create_revision(name) -> ChangeArtifactCreated`

## Classes

### ChangeArtifactCreated

Result information from creating a change artifact.
