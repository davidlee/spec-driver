# supekku.cli.view_test

Tests for view command.

VT-073-02: render_file / render_file_paged cascades.
VT-073-04: read alias dispatches identically to view.

## Constants

- `runner`

## Functions

- `_mock_ref(tmp_path, artifact_id) -> ArtifactRef`

## Classes

### TestGetPager

Tests for get_pager function.

#### Methods

- `test_falls_back_to_less(self, monkeypatch) -> None`
- `test_falls_back_to_more(self, monkeypatch) -> None`
- `test_returns_none_when_no_pager(self, monkeypatch) -> None`
- `test_returns_pager_env_var(self, monkeypatch) -> None`

### TestNormalizeId

Tests for normalize_id function.

#### Methods

- `test_all_artifact_types(self) -> None`
- `test_already_prefixed_unchanged(self) -> None`
- `test_ambiguous_types_unchanged(self) -> None`
- `test_non_numeric_unchanged(self) -> None`
- `test_numeric_only_gets_prefix_and_padding(self) -> None`

### TestReadAlias

VT-073-04: 'read' alias dispatches identically to 'view'.

#### Methods

- `test_read_alias_registered(self) -> None`: read appears in the main app.
- `test_read_invokes_same_app(self) -> None`: read and view reference the same Typer app instance.

### TestRenderFile

render_file renders markdown to stdout: glow → rich → raw.

#### Methods

- `test_falls_back_to_raw_stdout(self, tmp_path, capsys) -> None`
- `test_uses_glow_when_available(self, tmp_path) -> None`
- `test_uses_rich_when_no_glow(self, tmp_path) -> None`

### TestRenderFilePaged

render_file_paged pages markdown: $PAGER → glow -p → ov → less → more.

#### Methods

- `test_falls_back_to_less(self, tmp_path, monkeypatch) -> None`
- `test_raises_when_no_pager(self, tmp_path, monkeypatch) -> None`
- `test_uses_glow_pager_when_no_env(self, tmp_path, monkeypatch) -> None`
- `test_uses_pager_env(self, tmp_path, monkeypatch) -> None`

### TestViewCard

view card preserves --anywhere flag.

#### Methods

- `test_view_card_not_found(self) -> None`
- `test_view_card_pager(self, tmp_path) -> None`
- `test_view_card_renders(self, tmp_path) -> None`

### TestViewDefaultRendersToStdout

view <artifact> renders to stdout by default (no pager).

#### Methods

- `test_view_adr_renders_to_stdout(self, tmp_path) -> None`
- `test_view_delta_renders_to_stdout(self, tmp_path) -> None`
- `test_view_spec_renders_to_stdout(self, tmp_path) -> None`

### TestViewNotFound

view shows error when artifact not found.

#### Methods

- `test_adr_not_found(self) -> None`
- `test_delta_not_found(self) -> None`

### TestViewPagerFlag

view --pager/-p invokes pager instead of stdout render.

#### Methods

- `test_pager_flag_pages(self, tmp_path) -> None`
- `test_pager_short_flag(self, tmp_path) -> None`

### TestViewRevisionRegression

Regression tests for view revision.

#### Methods

- `test_view_revision_not_found(self) -> None`
- `test_view_revision_numeric_shorthand(self, tmp_path) -> None`: view revision 1 resolves via resolve_artifact.
- `test_view_revision_renders(self, tmp_path) -> None`: view revision RE-001 renders the file.

### TestViewSubcommands

All view subcommands using resolve_artifact dispatch correctly.

#### Methods

- @pytest.mark.parametrize(Tuple[subcommand, artifact_id], List[Tuple[plan, IP-001], Tuple[audit, AUD-001], Tuple[memory, mem.pattern.cli.skinny], Tuple[issue, ISSUE-001], Tuple[problem, PROB-001], Tuple[improvement, IMPR-001], Tuple[risk, RISK-001], Tuple[revision, RE-001], Tuple[policy, POL-001], Tuple[standard, STD-001]]) `test_subcommand_renders(self, tmp_path, subcommand, artifact_id) -> None`
