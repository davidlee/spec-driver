# supekku.scripts.lib.changes.blocks.plan

Utilities for parsing structured plan and phase overview YAML blocks.

## Constants

- `PHASE_MARKER`
- `PLAN_MARKER`

## Functions

- `extract_phase_overview(text, source_path) -> <BinOp>`: Extract and parse phase overview YAML block from markdown text.
- `extract_plan_overview(text, source_path) -> <BinOp>`: Extract and parse plan overview YAML block from markdown text.
- `load_phase_overview(path) -> <BinOp>`: Load and parse phase overview from a markdown file.
- `load_plan_overview(path) -> <BinOp>`: Load and parse plan overview from a markdown file.

## Classes

### PhaseOverviewBlock

Parsed YAML block containing phase overview information.

### PlanOverviewBlock

Parsed YAML block containing plan overview information.
