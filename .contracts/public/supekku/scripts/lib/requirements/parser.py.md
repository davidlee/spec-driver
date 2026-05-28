# supekku.scripts.lib.requirements.parser

Requirement extraction and parsing from spec content.

## Constants

- `logger`

## Functions

- `count_requirement_like_lines(body) -> int`: Count lines in *body* that plausibly define a requirement.

Public API for callers that need a quick sanity count without running
full extraction.  Uses the same heuristic as the parser's internal
diagnostics.
- `records_from_spec(spec_id, frontmatter, body, spec_path, repo_root) -> Iterator[RequirementRecord]`: Extract requirements — block-first, regex fallback.

When *strict* (post-flip): no block or extraction failure yields zero
records with no regex fallback.  When tolerant (pre-flip): extraction
failure falls back to regex.
