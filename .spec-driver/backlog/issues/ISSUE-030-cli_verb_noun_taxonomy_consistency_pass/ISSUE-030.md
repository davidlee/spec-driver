---
id: ISSUE-030
name: 'CLI verb-noun taxonomy: consistency pass'
created: '2026-03-02'
updated: '2026-03-09'
status: resolved
kind: issue
categories: []
severity: p2
impact: user
categories: [design, cli, dx]
---

# CLI verb-noun taxonomy: consistency pass

## Problem

The CLI command structure has grown organically and has several
consistency issues that hurt discoverability and learnability.

## Known Issues

1. **`skills sync`** — NOUN VERB, violates the VERB NOUN convention
   used by `create`, `list`, `show`, `edit`, `find`, `complete`.
2. **`schema`** — NOUN group with no verb. Should probably be
   `show schema` or similar.
3. **`sync`** — overloaded top-level command with ~12 flags and
   non-obvious defaults. What does bare `sync` actually sync?
   Should arguably decompose into `sync specs`, `sync contracts`,
   `sync registries`, `sync skills`, etc.
4. **`validate`** — similar to `sync`: unclear what it validates
   without reading help.
5. **`install`** — currently workspace init only; could become a
   group (`install workspace`, `install skills`).
6. **Gaps in symmetry** — e.g. you can `create adr` but the
   corresponding `list adrs` uses a different noun form.

## Desired Outcome

- Consistent VERB NOUN grammar across all commands
- Clear, unsurprising defaults
- Decompose overloaded commands into focused subcommands
- Backward compat via aliases or deprecation notices where needed

## Approach

Design task — needs a brief audit + proposal before implementation.
Consider a small ADR for the CLI grammar conventions.

