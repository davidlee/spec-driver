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

- `logger`

## Functions

- `parse_ledger_body(body) -> tuple[Tuple[str, list[DriftEntry]]]`: Parse a drift ledger body into freeform body and entries.

Args:
  body: markdown body after frontmatter removal.

Returns:
  (freeform_body, entries) — freeform_body is content before the first
  entry heading; entries are parsed DriftEntry models.
