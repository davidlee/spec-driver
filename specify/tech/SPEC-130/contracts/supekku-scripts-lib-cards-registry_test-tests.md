# supekku.scripts.lib.cards.registry_test

Tests for card registry and models.

VT-021-001: ID parsing + lane detection + ambiguity rules
VT-021-002: next-ID allocation scans all lanes
VT-021-003: create card copies template and rewrites only H1/Created
VT-021-004: show card -q path-only behaviour and errors

## Classes

### TestCardCreation

VT-021-003: Card creation with template preservation.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Create temporary directory for tests.
- `tearDown(self) -> None`: Clean up temporary directory.
- `test_auto_creates_template_if_missing(self) -> None`: Auto-creates kanban/template.md if missing.
- `test_create_card_with_description(self) -> None`: Create card rewrites first H1 to # T###: description.
- `test_default_lane_is_backlog(self) -> None`: Default lane is backlog when not specified.
- `test_inserts_created_date(self) -> None`: Inserts/updates Created: YYYY-MM-DD line.
- `test_preserves_template_content(self) -> None`: Preserves all other template content verbatim.
- `test_respects_lane_flag(self) -> None`: Respects --lane flag (backlog/doing/done, default backlog).
- `test_validates_lane_exists(self) -> None`: Validates lane exists or errors clearly.

### TestCardDiscovery

VT-021-001: Discovery across lanes and ambiguity detection.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Create temporary directory for tests.
- `tearDown(self) -> None`: Clean up temporary directory.
- `test_discover_cards_across_lanes(self) -> None`: Discover cards across all lanes (backlog/doing/done).
- `test_filter_by_lane(self) -> None`: Filter cards by lane.
- `test_handle_empty_kanban(self) -> None`: Return empty list when no cards found.

### TestCardModel

VT-021-001: ID parsing and lane detection.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Create temporary directory for tests.
- `tearDown(self) -> None`: Clean up temporary directory.
- `test_detect_lane_from_path(self) -> None`: Detect lane from path kanban/doing/T123.md -> 'doing'.
- `test_handle_missing_created_date(self) -> None`: Handle missing Created date gracefully.
- `test_handle_missing_lane(self) -> None`: Handle missing lane (no kanban/ in path) -> None.
- `test_parse_created_date(self) -> None`: Parse Created date from card content.
- `test_parse_id_from_filename(self) -> None`: Parse card ID from filename T123-description.md.
- `test_parse_title_from_h1(self) -> None`: Parse title from first H1.

### TestCardResolution

VT-021-004: Card resolution and ambiguity handling.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Create temporary directory for tests.
- `tearDown(self) -> None`: Clean up temporary directory.
- `test_anywhere_flag_expands_search(self) -> None`: --anywhere flag expands search beyond kanban/.
- `test_multiple_matches_raises_ambiguity_error(self) -> None`: Multiple matches raise error listing candidates.
- `test_no_match_raises_error(self) -> None`: No match raises error with clear message.
- `test_resolve_path_only(self) -> None`: resolve_path returns only path string for -q flag.
- `test_unambiguous_match_returns_card(self) -> None`: Unambiguous match returns single Card.

### TestNextIdAllocation

VT-021-002: Next-ID allocation scans all lanes.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Create temporary directory for tests.
- `tearDown(self) -> None`: Clean up temporary directory.
- `test_empty_kanban_returns_t001(self) -> None`: Empty kanban -> T001.
- `test_existing_cards_returns_max_plus_one(self) -> None`: Existing T001, T002 -> T003.
- `test_gaps_in_sequence(self) -> None`: Gaps in sequence (T001, T005) -> T006.
- `test_scans_all_lanes(self) -> None`: Scan all lanes, not just backlog.
