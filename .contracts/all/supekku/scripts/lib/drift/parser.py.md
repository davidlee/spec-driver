# supekku.scripts.lib.drift.parser

Drift ledger body parser — heading split with fenced YAML extraction.

Parses a drift ledger markdown body into structured DriftEntry models.
Follows DEC-065-02 (fenced YAML blocks) and DEC-065-03 (section-based parser).

Parser contract (DR-065):
- Fences processed before headings (fence/heading precedence)
- Malformed YAML → warning, entry with _parse_error in extra
- Missing required nested keys → warning, malformed record skipped
- Duplicate entry IDs → warning, both preserved
- No YAML block → warning, heading-only entry
- Multiple YAML blocks → first parsed, rest is analysis

## Constants

- `_ENTRY_HEADING_RE` - Entry heading pattern: ### DL-NNN.MMM: title
- `_FENCE_RE` - Fenced code block pattern (any language tag)
- `logger`

## Functions

- `_build_entry(entry_id, title, data, analysis) -> DriftEntry`: Construct a DriftEntry from parsed YAML data.

Handles _parse_error from malformed YAML. Builds typed substructures
with warnings for malformed records (DEC-065-06).
- `_extract_yaml_block(section_body) -> tuple[Tuple[<BinOp>, str]]`: Extract the first fenced YAML block from a section.

Returns:
  (yaml_data, analysis) — yaml_data is the parsed dict (or None),
  analysis is the remaining markdown outside the fence.
- `_join_analysis(before, after) -> str`: Join before/after fence content into analysis text.
- `_parse_claims(raw, entry_id) -> list[Claim]`: Parse claim dicts into typed Claim objects.
- `_parse_discovered_by(raw, entry_id) -> <BinOp>`: Parse discovered_by dict into typed DiscoveredBy object.
- `_parse_entry_section(heading, section_body) -> <BinOp>`: Parse a single entry section into a DriftEntry.

Args:
  heading: the ### heading line
  section_body: content after the heading

Returns:
  DriftEntry or None if the heading doesn't match the expected pattern.
- `_parse_sources(raw, entry_id) -> list[Source]`: Parse source dicts into typed Source objects.
- `_split_sections(body) -> tuple[Tuple[str, list[tuple[Tuple[str, str]]]]]`: Split body on ### headings, respecting fenced code blocks.

Returns (freeform_body, entry_sections) where entry_sections are
(heading_text, section_body) tuples.

Fence/heading precedence (DEC-065-03): content inside fenced code
blocks is opaque — ### lines inside fences are not entry boundaries.
- `parse_ledger_body(body) -> tuple[Tuple[str, list[DriftEntry]]]`: Parse a drift ledger body into freeform body and entries.

Args:
  body: markdown body after frontmatter removal.

Returns:
  (freeform_body, entries) — freeform_body is content before the first
  entry heading; entries are parsed DriftEntry models.
