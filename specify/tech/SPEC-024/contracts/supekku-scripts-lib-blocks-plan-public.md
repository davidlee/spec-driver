# supekku.scripts.lib.blocks.plan

Utilities for parsing structured plan and phase overview YAML blocks.

## Constants

- `PHASE_MARKER`
- `PHASE_SCHEMA`
- `PHASE_VERSION`
- `PLAN_MARKER`
- `PLAN_SCHEMA`
- `PLAN_VERSION`

## Functions

- `extract_phase_overview(text, source_path) -> <BinOp>`: Extract and parse phase overview YAML block from markdown text.
- `extract_plan_overview(text, source_path) -> <BinOp>`: Extract and parse plan overview YAML block from markdown text.
- `load_phase_overview(path) -> <BinOp>`: Load and parse phase overview from a markdown file.
- `load_plan_overview(path) -> <BinOp>`: Load and parse plan overview from a markdown file.
- `render_phase_overview_block(phase_id, plan_id, delta_id) -> str`: Render a phase overview YAML block with given values.

This is the canonical source for the block structure. Templates and
creation code should use this instead of hardcoding the structure.

Args:
  phase_id: The phase ID.
  plan_id: The plan ID this phase belongs to.
  delta_id: The delta ID this phase implements.
  objective: The phase objective.
  entrance_criteria: List of entrance criteria.
  exit_criteria: List of exit criteria.
  verification_tests: List of test IDs for verification.
  verification_evidence: List of evidence items for verification.
  tasks: List of task descriptions.
  risks: List of risk descriptions.

Returns:
  Formatted YAML code block as string.
- `render_plan_overview_block(plan_id, delta_id) -> str`: Render a plan overview YAML block with given values.

This is the canonical source for the block structure. Templates and
creation code should use this instead of hardcoding the structure.

Args:
  plan_id: The plan ID.
  delta_id: The delta ID this plan implements.
  primary_specs: List of primary spec IDs.
  collaborator_specs: List of collaborator spec IDs.
  target_requirements: List of requirement IDs this targets.
  dependency_requirements: List of requirement IDs this depends on.
  first_phase_id: ID for the first phase (auto-generated if None).
  first_phase_name: Name for the first phase.
  first_phase_objective: Objective for the first phase.
  aligns_with_revisions: List of revision IDs this aligns with.

Returns:
  Formatted YAML code block as string.

## Classes

### PhaseOverviewBlock

Parsed YAML block containing phase overview information.

### PhaseOverviewValidator

Validator for phase overview blocks.

#### Methods

- `validate(self, block) -> list[str]`: Validate phase overview block against schema.

Args:
  block: Parsed phase overview block to validate.

Returns:
  List of error messages (empty if valid).

### PlanOverviewBlock

Parsed YAML block containing plan overview information.

### PlanOverviewValidator

Validator for plan overview blocks.

#### Methods

- `validate(self, block) -> list[str]`: Validate plan overview block against schema.

Args:
  block: Parsed plan overview block to validate.

Returns:
  List of error messages (empty if valid).
