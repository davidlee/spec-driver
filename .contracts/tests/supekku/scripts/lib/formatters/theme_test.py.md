# supekku.scripts.lib.formatters.theme_test

Tests for theme style resolution API (VT-053-styled-text).

## Classes

### TestResolveStyle

Tests for resolve_style().

#### Methods

- @pytest.mark.parametrize(style_name, List[adr.id, spec.id, change.id, adr.status.accepted, change.status.completed, spec.status.active, requirement.status.active, memory.status.active, policy.status.required, standard.status.required, backlog.status.open, backlog.status.resolved, artifact.group.governance, artifact.group.change, artifact.group.domain, artifact.group.operational]) `test_all_core_styles_resolve(self, style_name)`: Regression: all style keys consumed by TUI must resolve.
- `test_resolves_known_style(self)`
- `test_resolves_to_correct_color(self)`
- `test_returns_none_for_empty_string(self)`
- `test_returns_none_for_unknown_style(self)` - #8ec07c

### TestStyledText

Tests for styled_text().

#### Methods

- `test_applies_resolved_style(self)`
- `test_empty_value(self)`
- `test_missing_style_returns_unstyled_text(self)`
- `test_returns_text_object(self)`
- `test_style_color_matches_theme(self)`
