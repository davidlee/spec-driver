# supekku.scripts.lib.requirements.parser

Requirement extraction and parsing from spec content.

## Constants

- `_BARE_REQUIREMENT_ID`
- `_REQUIREMENT_CROSSREF` - These mention a requirement without defining it.
- `_REQUIREMENT_HEADING` - Matches dotted format only (NNN.MMM) — no overlap with spec bullet format.
- `_REQUIREMENT_IN_PARENS` - is citing requirements, not defining them.
- `_REQUIREMENT_LINE` - Optional tags in square brackets after category: **FR-001**(cat)[tag1, tag2]: Title
- `logger`

## Functions

- `_has_frontmatter_requirement_definitions(fm) -> list[dict]`: Return frontmatter entries that look like requirement definitions.

Detects a ``requirements:`` key whose value is a list of dicts containing
``id`` or ``description`` keys — the pattern agents use when they
incorrectly define requirements in YAML frontmatter instead of body
bullets.  The ``spec.relationships`` block uses a structurally distinct
dict with ``primary``/``collaborators`` keys and is not matched.
- `_is_requirement_like_line(line) -> bool`: Return True if *line* plausibly attempts to define a requirement.

A line is "requirement-like" if it contains an FR/NF-xxx ID and the
ID is not purely a cross-reference.  Cross-reference patterns:
- "per FR-007" / "per PROD-004.FR-007"
- All IDs on the line are inside parentheses

Lines with no FR/NF ID at all return False.
- `_load_breakout_metadata(spec_path) -> dict[Tuple[str, dict[Tuple[str, Any]]]]`: Load metadata from breakout requirement files under a spec.

Scans ``spec_path.parent / "requirements"`` for ``*.md`` files and
extracts ``tags``, ``ext_id``, and ``ext_url`` from their frontmatter.

Returns:
  Mapping from qualified requirement ID (e.g. ``SPEC-100.FR-010``)
  to a dict of metadata fields.
- `_records_from_content(spec_id, _frontmatter, body, spec_path, repo_root, stats) -> Iterator[RequirementRecord]`: Extract requirement records from spec body content.

Logs warnings if requirement-like lines are found but not extracted.
- `_records_from_frontmatter(spec_id, frontmatter, body, spec_path, repo_root, stats) -> Iterator[RequirementRecord]`: Extract requirement records from spec frontmatter and body.
- `_requirements_from_spec(spec_path, spec_id, repo_root) -> Iterator[RequirementRecord]`: Extract requirements from a spec file on disk.
- `_validate_extraction(spec_registry, seen) -> None`: Validate extraction results and warn about potential issues.

Checks for specs with zero extracted requirements, which may indicate
format issues or extraction failures.
- `count_requirement_like_lines(body) -> int`: Count lines in *body* that plausibly define a requirement.

Public API for callers that need a quick sanity count without running
full extraction.  Uses the same heuristic as the parser's internal
diagnostics.
