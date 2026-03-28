# supekku.scripts.lib.requirements.parser

Requirement extraction and parsing from spec content.

## Constants

- `logger`

## Functions

- `count_requirement_like_lines(body) -> int`: Count lines in *body* that plausibly define a requirement.

Public API for callers that need a quick sanity count without running
full extraction.  Uses the same heuristic as the parser's internal
diagnostics.
