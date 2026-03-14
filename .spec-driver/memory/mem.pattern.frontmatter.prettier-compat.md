---
id: mem.pattern.frontmatter.prettier-compat
name: CompactDumper prettier compatibility
kind: memory
status: active
memory_type: pattern
created: "2026-03-14"
updated: "2026-03-14"
verified: "2026-03-14"
confidence: high
tags: [frontmatter, prettier, yaml]
summary: CompactDumper in frontmatter_writer.py produces YAML that converges with prettier's markdown frontmatter formatter.
priority:
  severity: high
  weight: 8
scope:
  globs:
    - supekku/scripts/lib/core/frontmatter_writer.py
    - scripts/normalise_frontmatter.py
  commands:
    - prettier .spec-driver --check
    - uv run python scripts/normalise_frontmatter.py
provenance:
  sources:
    - kind: delta
      ref: DE-096
    - kind: code
      ref: supekku/scripts/lib/core/frontmatter_writer.py
---

# CompactDumper prettier compatibility

## Key invariant

`CompactDumper` output is idempotent with prettier: `normalise → prettier --check` = no changes.

## Design choices (DE-096)

| Concern         | CompactDumper approach                        | Why                                                |
| --------------- | --------------------------------------------- | -------------------------------------------------- |
| Quote style     | Double-quote strings YAML would single-quote  | Prettier uses double quotes                        |
| Embedded `"`    | Use single quotes when value contains `"`     | Prettier avoids escaping                           |
| Sequence indent | Never indentless (`increase_indent` override) | Prettier indents sequences under parent            |
| Flow list width | `_FLOW_LIST_WIDTH_LIMIT = 60`                 | Room for key prefix under prettier's 80-char width |
| Line width      | `width=10000`                                 | Prevent PyYAML mid-value wrapping                  |
| Reserved starts | `@`, backtick, `'`, `"` trigger quoting       | YAML indicators need quoting                       |
| Flow indicators | `,`, `[]`, `{}` trigger quoting               | Needed for flow list context                       |

## Quoting regex

`_NEEDS_QUOTING_RE` matches: empty strings, date-like, bool/null-like, digit-starting, YAML-reserved start chars, and special chars (`:`, `#`, `,`, `[]`, `{}`).

## Gotcha

Over-quoting is safe for prettier convergence (prettier preserves existing quotes). The regex is intentionally broad rather than context-sensitive.
