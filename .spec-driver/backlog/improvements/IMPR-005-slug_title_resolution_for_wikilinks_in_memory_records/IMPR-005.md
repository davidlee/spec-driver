---
id: IMPR-005
name: "Slug/title resolution for [[...]] wikilinks in memory records"
created: "2026-03-03"
updated: "2026-03-03"
status: open
kind: improvement
---

# Slug/title resolution for [[...]] wikilinks in memory records

## Context

The obs-link-spec (DE-033 bundle) defines `[[slug]]` as an optional resolution
mode alongside `[[id]]`. Currently, only exact artifact IDs resolve —
`[[Auth Overview]]` or `[[auth-overview]]` produce `MissingLink`.

## Proposed Behaviour

When a `[[target]]` token fails exact-ID and memory-normalization lookup,
attempt slug/title matching:

1. Build a slug index from memory record names (lowercase, hyphen-normalized)
2. Match the link target against the slug index (case-insensitive)
3. If exactly one match: resolve as `ResolvedLink`
4. If multiple matches: warn with ambiguity message, leave as `MissingLink`
5. Optionally extend to other artifact types (ADR titles, spec names)

## Scope Estimate

- Slug index builder: ~20 lines + tests
- Fallback resolution step in `resolve_parsed_link`: ~15 lines
- Ambiguity detection + warning: ~10 lines
- Tests: ~15-20 cases (single match, multiple match, case insensitivity, etc.)

## References

- obs-link-spec: `change/deltas/DE-033-.../obs-link-spec.md` §1
- Resolver: `supekku/scripts/lib/memory/links.py` `resolve_parsed_link()`
- Requirement: MEM-FR-004 (advisory cross-artifact links)
