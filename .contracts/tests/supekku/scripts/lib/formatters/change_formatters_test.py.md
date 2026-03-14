# supekku.scripts.lib.formatters.change_formatters_test

Tests for change_formatters module.

## Classes

### FormatAuditDetailsTest

Tests for format_audit_details (VT-format-audit).

**Inherits from:** unittest.TestCase

#### Methods

- `test_basic_fields(self) -> None`
- `test_with_applies_to(self) -> None`
- `test_with_relations(self) -> None`
- `test_with_root_shows_relative_path(self) -> None`
- `_make_audit(self) -> ChangeArtifact`

### FormatPlanDetailsTest

Tests for format_plan_details (VT-format-plan).

**Inherits from:** unittest.TestCase

#### Methods

- `test_basic_fields(self) -> None`
- `test_missing_fields_use_defaults(self) -> None`
- `test_with_path_and_root(self) -> None`

### FormatPlanListTableTest

Tests for format_plan_list_table (VT-format-plan-list).

**Inherits from:** unittest.TestCase

#### Methods

- `test_empty_plans(self) -> None`
- `test_empty_plans_json(self) -> None` - table headers still rendered
- `test_json_format(self) -> None`
- `test_missing_fields_use_defaults(self) -> None`
- `test_table_contains_columns_and_data(self) -> None`
- `test_table_shows_delta_ref(self) -> None`
- `test_table_strips_name_prefix(self) -> None`
- `test_truncate_parameter_accepted(self) -> None`
- `test_tsv_format(self) -> None`
- @staticmethod `_plan(plan_id, name, status, delta) -> dict`

### TestChangeExternalFields

Tests for ext_id/ext_url support in change formatters (VT-067-002).

**Inherits from:** unittest.TestCase

#### Methods

- `test_delta_details_with_ext_id_and_url(self) -> None`: Test delta detail shows ext_id with url.
- `test_delta_details_with_ext_id_only(self) -> None`: Test delta detail shows ext_id without url.
- `test_delta_details_without_ext_id_omits_line(self) -> None`: Test delta detail omits External line when no ext_id.
- `test_json_includes_ext_fields(self) -> None`: Test JSON output includes ext_id and ext_url when present.
- `test_json_omits_ext_fields_when_empty(self) -> None`: Test JSON output omits ext_id/ext_url when empty.
- `test_revision_details_with_ext_id(self) -> None`: Test revision detail shows ext_id.
- `test_table_show_external_includes_column(self) -> None`: Test table includes ExtID column when show_external=True.
- `test_tsv_no_external_omits_ext_id(self) -> None`: Test TSV omits ext_id when show_external=False.
- `test_tsv_show_external_inserts_ext_id(self) -> None`: Test TSV includes ext_id after ID when show_external=True.
- `_make_delta(self) -> ChangeArtifact`

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

### TestFormatDeltaPhasesVTPHASE003

VT-PHASE-003: Tests for phase display in delta formatter.

Verifies PROD-006.FR-003: Enhanced delta display shows phases.

**Inherits from:** unittest.TestCase

#### Methods

- `test_delta_phase_id_and_name_formatted(self) -> None`: Test phase ID and name are formatted correctly in output.
- `test_delta_phase_objective_truncation(self) -> None`: Test that long objectives are wrapped in table display.
- `test_delta_with_three_phases(self) -> None`: Test delta with 3 phases shows all with proper formatting.
- `test_delta_with_zero_phases(self) -> None`: Test delta with plan but no phases shows plan ID.

### TestFormatDeltaReverseLookups

Tests for \_format_delta_reverse_lookups (VT-090-P2-3).

**Inherits from:** unittest.TestCase

#### Methods

- `test_in_format_delta_details(self) -> None`: Reverse lookups appear in full delta details output.
- `test_mixed(self) -> None`
- `test_no_lookups(self) -> None`
- `test_single_audit(self) -> None`
- `test_single_revision(self) -> None`

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
