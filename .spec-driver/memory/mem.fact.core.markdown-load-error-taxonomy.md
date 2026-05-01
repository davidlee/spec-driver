---
id: mem.fact.core.markdown-load-error-taxonomy
name: MarkdownLoadError is a ValueError so existing except clauses keep working
kind: memory
status: active
memory_type: fact
created: '2026-05-01'
updated: '2026-05-01'
verified: '2026-05-01'
confidence: high
tags:
- core
- spec_utils
- invariant
- error-handling
summary: "core/spec_utils.py raises MarkdownLoadError(ValueError) for malformed YAML frontmatter; subclassing ValueError is load-bearing \u2014 existing except (ValueError, OSError) clauses across changes/, drift/, requirements/ depend on it."
scope:
  paths:
    - supekku/scripts/lib/core/spec_utils.py
  globs:
    - supekku/scripts/lib/changes/**
    - supekku/scripts/lib/drift/**
    - supekku/scripts/lib/requirements/**
provenance:
  sources:
    - DE-135
    - DR-135
    - supekku/scripts/lib/core/spec_utils.py
    - supekku/scripts/lib/core/frontmatter_schema.py
---

# MarkdownLoadError is a ValueError so existing except clauses keep working

## Fact

`supekku.scripts.lib.core.spec_utils.load_markdown_file` translates any
`yaml.YAMLError` raised by `frontmatter.loads(...)` into
`MarkdownLoadError(ValueError)` with the file path and (when available) 1-based
line/column. The original exception is chained via `__cause__`.

The `ValueError` parent class is **load-bearing**, not incidental:

- `changes/artifacts.py:181` \u2014 `except (ValueError, OSError)`
- `changes/registry.py:85` \u2014 `except ValueError`
- `drift/registry.py:77` \u2014 `except (OSError, ValueError, KeyError)`
- `requirements/parser.py:132` \u2014 `except (OSError, ValueError)`

These call sites depend on `MarkdownLoadError` being a `ValueError` to surface
a friendly skip-and-warn diagnostic instead of crashing with a Rich traceback.

## Don't do this

- **Don't change `MarkdownLoadError`'s base class** to a non-`ValueError` (e.g.
  `Exception`, `RuntimeError`, or a custom non-derived class) without
  simultaneously updating every call site listed above.
- **Don't change the message format** without also updating `VT-DR135-001`
  (substring assertions on "invalid YAML frontmatter", "line ", "column ").
- **Don't introduce a parallel parse-error type**. POL-001 \u2014 one canonical
  loader-error class per concern.

## Pairs with

- [[mem.fact.cli.typer-exit-inherits-runtimeerror]] \u2014 sibling "subclass choice
  changes who catches it" gotcha for typer/click.
- `core/frontmatter_schema.py:FrontmatterValidationError(ValueError)` \u2014 same
  pattern, different concern (schema validation, not parse).

## Sites that still leak (deferred follow-up)

`requirements/sync.py:77` catches only `OSError`, so `MarkdownLoadError` would
still escape there. Tracked as a follow-up in `DE-135` \u00a78 \u2014 outside the
ISSUE-054 path so deliberately not bundled.

## Provenance

Discovered in [[DE-135]] when designing the fix for [[ISSUE-054]]. See
[[DR-135]] \u00a73 (Architecture Intent) and \u00a77 (DEC-DR135-002).
