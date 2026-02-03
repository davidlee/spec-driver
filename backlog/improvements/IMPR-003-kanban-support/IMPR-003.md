---
id: IMPR-003
name: kanban support
created: '2026-02-03'
updated: '2026-02-03'
status: idea
kind: improvement
---

# kanban support

## Problem statement / value driver

We maintain Markdown kanban cards under `kanban/` (e.g. `kanban/backlog/T123-some-task.md`),
but SpecDriver currently treats them as “just files”, which makes it easy for links and
workflows to break when folders change.

Primary value:
- ID-based linking (T-cards, ADRs, SPEC/PROD, deltas/plans) that survives folder moves.
- Simple dependency expression and query (`T123` depends on `T120`, etc).
- Fast find/show commands for the “where is this ID?” workflow.

## Scope - goals

- Introduce **Card** artifact support (ID prefix `T`) with **Markdown-first** metadata.
- Provide CLI commands:
  - `spec-driver create card "description"`: create new card from template with next ID.
  - `spec-driver list cards`: list cards with basic filters + output formats.
  - `spec-driver show card T123`: show card details and/or path.
  - `spec-driver find card T123`: list all matching files by ID across repo.
- Keep CLI thin: args → registry → filter → formatter → output.

## Scope - non-goals

- No “move card between lanes” command (can remain `git mv` / manual).
- No heavy metadata systems or generic base abstractions.
- No requirement to adopt YAML frontmatter in cards.

## Background

### Prior art

- `deck_of_dwarf/kanban` `Justfile:new-card`:
  - `T###` ID chosen by scanning existing `kanban/**/T*.md`
  - destination is `kanban/backlog/T###-slug.md`
  - template file is `kanban/template.md`

### Existing systems in spec-driver

- CLI is Typer-based (`supekku/cli/*`), delegating to domain packages and pure formatters.
- Domain registries exist for specs, changes, decisions, backlog items.
- Table output patterns exist in `supekku/scripts/lib/formatters/*_formatters.py`.

## Design proposal

### Artifact: Card

- Canonical ID: `T###` (3+ digits) extracted from filename.
- Canonical “card file” location: `kanban/**/T###-*.md` (default resolution scope).
- Repo-wide “references” search uses filename pattern: `^T###-.*\\.md$` (any folder).

### Metadata (minimal, markdown-first)

Required by convention:
- First H1: `# T###: <title>`
- `Created: YYYY-MM-DD` line (written/updated on create)

Optional, parsed for dependencies/links (no YAML required):
- A section containing lines like:
  - `Depends: T120, ADR-003, SPEC-210`
  - `Related: T100, PROD-042`

Rules:
- Parsing must be tolerant: missing sections/lines yield empty sets.
- Only IDs are interpreted; everything else remains freeform Markdown.

### Behavior rules

- `create card` copies `kanban/template.md` then rewrites only:
  - first H1 to include the allocated ID + provided description
  - `Created:` line (insert if missing; prefer directly after H1)
- Template remains fully user-editable for all other content.

- `show card T123` default scope is `kanban/**/T123-*.md`:
  - If none: error (not found).
  - If multiple: error (ambiguous; list candidates).
  - `--anywhere` expands search to the repo (may still be ambiguous).
  - `-q/--quiet` prints only the resolved path (single line) and exits.

- `find card T123` prints all repo-wide matches of `^T123-.*\\.md$` (one per line).

## Changes required (code-level)

### Domain

Add `supekku/scripts/lib/cards/`:
- `models.py`: `Card` dataclass (id, title, lane, path, created, depends, related)
- `registry.py`: `CardRegistry` for discovery, id allocation, creation, resolution

### Formatters

Add `supekku/scripts/lib/formatters/card_formatters.py` (pure functions):
- `format_card_list_table(cards, format_type, truncate)`
- `format_card_details(card)`

### CLI

- Add a `find` Typer group (new `supekku/cli/find.py`) and register in `supekku/cli/main.py`.
- Extend existing groups:
  - `supekku/cli/create.py`: `create card`
  - `supekku/cli/list.py`: `list cards`
  - `supekku/cli/show.py`: `show card` (+ `-q`, `--anywhere`)

### Tests

- `supekku/scripts/lib/cards/registry_test.py`
- `supekku/scripts/lib/formatters/card_formatters_test.py`
- Add/extend CLI tests for `find card`, `show card -q`, `show card --anywhere`.

## Tasks / Sequence of Work

1. Add `cards` domain (discover/resolve/next-id/create, plus minimal parsing).
2. Add pure formatters for list + details.
3. Add CLI commands (thin orchestration, consistent flags/output formats).
4. Add tests for domain/formatters/CLI; validate on representative fixtures.
5. Run `just` (format/lint/test/pylint) and adjust as needed.

## Test / Verification Strategy

### Success criteria / ACs

- `uv run spec-driver create card "x"` creates `kanban/backlog/T###-x.md`
  and rewrites H1 + Created while preserving template content.
- `uv run spec-driver show card T123 -q` prints a single path when unambiguous.
- `uv run spec-driver find card T123` lists all matching `T123-*.md` in repo.
- `uv run spec-driver list cards --format json` emits machine-readable output.

