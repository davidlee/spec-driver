## Proposed v1.1 shape

keep it _strictly additive_: inline links are authoring sugar; the canonical graph is in frontmatter.

### 1) Inline syntax (restrict it)

Support a conservative Obsidian-style subset:

- `[[id]]` (preferred): links directly to a memory record id.
- `[[slug]]` (optional): resolved via registry index (title/alias/slug map).
- `[[id|Label]]` for display text.

Avoid supporting raw paths (`[[memory/system/auth.md]]`) ; ids are more stable.

### 2) Resolution on save

On `mem save` / `mem edit` / `mem fmt` (whatever your write path is):

1. Parse body for `[[...]]` tokens (ignore code fences and inline code).
2. Resolve each token to:
   - a unique `target_id`
   - a qualified path (or canonical ref) from registry, e.g. `memory/system/auth-overview.md`

3. Write/update frontmatter fields:

```yaml
links:
  out:
    - id: mem.system.auth-overview
      path: memory/system/auth-overview.md
      label: Auth overview
      kind: memory
```

Optionally also store `missing` separately to keep warnings deterministic:

```yaml
links:
  missing:
    - raw: "mem.system.nonexistent"
      found: 0
```

### 3) Warnings and failure modes

- Missing target → warn (non-fatal by default), optionally `--strict` to fail CI.
- Ambiguous slug/title match → warn and require disambiguation (recommend `[[id]]`).
- Self-link → ignore or warn (your choice).
- Cycles → fine; this is a graph.

### 4) Rendering and portability

Do not rewrite the body unless asked. Let `[[...]]` remain as authoring form.

If you want GitHub-friendly output, optionally offer `mem render` that converts:

- `[[id]]` → `[Label](../memory/system/auth-overview.md)` for a generated view, but keep the source file unchanged.

## Why this is worth it

- Encourages short, linked “index card” memories.
- Enforces referential integrity via your registry.
- Gives you a machine-usable link graph without asking authors to maintain it manually.
- Preserves model-agnosticism: no retrieval heuristics required; selection can use explicit relations later (e.g., “include linked neighbors to depth 1”).

## Design constraints to decide up front

### A) What is linkable?

At minimum:

- memory record ids
- other ADR/spec/requirement/etc ids (everything the registry indexes), via ID recognition
  This avoids memory becoming an alternative doc system while still supporting pointers.

### B) Canonical identity

Prefer `id` as canonical. Paths are derived.

If you store only paths, renames become painful; if you store ids, renames are cheap.

### C) Update policy

On save:

- recompute `links.out` from the body (source of truth = body)
- do not merge; overwrite deterministically
  This prevents “ghost links” from previous edits.

## Implementation notes (lightweight)

- Parser: simple state machine that skips fenced code blocks and inline backticks.
- Resolver: registry lookup by id first; optionally by alias/slug second.
- Writer: frontmatter update preserving other fields, stable sort by `id` to reduce diff noise.
