# supekku.scripts.lib.formatters.change_formatters_test

Tests for change_formatters module.

## Classes

### TestFormatChangeListItem

Tests for format_change_list_item function.

**Inherits from:** unittest.TestCase

#### Methods

- `test_format_basic_delta(self) -> None`: Test formatting a basic delta artifact.
- `test_format_revision_artifact(self) -> None`: Test formatting a revision artifact.

### TestFormatChangeWithContext

Tests for format_change_with_context function.

**Inherits from:** unittest.TestCase

#### Methods

- `test_format_empty_applies_to(self) -> None`: Test formatting when applies_to is empty dict.
- `test_format_empty_phases_list(self) -> None`: Test formatting when phases list is empty.
- `test_format_minimal_change(self) -> None`: Test formatting change with no additional context.
- `test_format_with_all_context(self) -> None`: Test formatting change with all context fields.
- `test_format_with_phases(self) -> None`: Test formatting change with plan phases.
- `test_format_with_requirements(self) -> None`: Test formatting change with requirements.
- `test_format_with_specs(self) -> None`: Test formatting change with related specs.

### TestFormatDeltaDetails

Tests for format_delta_details function.

**Inherits from:** unittest.TestCase

#### Methods

- `test_complete_delta(self) -> None`: Test formatting delta with all fields populated.
- `test_delta_with_applies_to(self) -> None`: Test formatting delta with applies_to specs and requirements.
- `test_delta_with_plan(self) -> None`: Test formatting delta with plan phases.
- `test_delta_with_relations(self) -> None`: Test formatting delta with relations.
- `test_delta_without_root(self) -> None`: Test formatting delta without root shows absolute path.
- `test_minimal_delta(self) -> None`: Test formatting delta with minimal fields.

### TestFormatPhaseSummary

Tests for format_phase_summary function.

**Inherits from:** unittest.TestCase

#### Methods

- `test_phase_with_empty_objective(self) -> None`: Test phase with empty string objective.
- `test_phase_with_id_instead_of_phase(self) -> None`: Test phase using 'id' field instead of 'phase'.
- `test_phase_with_long_objective(self) -> None`: Test formatting phase with objective exceeding max length.
- `test_phase_with_multiline_objective(self) -> None`: Test that only first line of objective is used.
- `test_phase_with_objective(self) -> None`: Test formatting phase with objective.
- `test_phase_without_objective(self) -> None`: Test formatting phase without objective.

### TestFormatRevisionDetails

Tests for format_revision_details function.

**Inherits from:** unittest.TestCase

#### Methods

- `test_complete_revision(self) -> None`: Test formatting revision with all fields populated.
- `test_minimal_revision(self) -> None`: Test formatting revision with minimal fields.
- `test_revision_with_applies_to(self) -> None`: Test formatting revision with applies_to specs and requirements.
- `test_revision_with_relations(self) -> None`: Test formatting revision with relations.
