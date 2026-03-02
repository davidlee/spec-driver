## A semantic, variable-length memory ID scheme

### Goals

* Human-writable and readable in `[[links]]`
* Stable under file moves/renames
* Encodes *some* meaning (at least type/domain), without becoming a brittle taxonomy
* No spaces; safe in YAML, URLs, and CLI args
* Unambiguous vs `ADR-012`, `SPEC-123`, etc.

### Proposed canonical form

Use **dot-separated segments** with an optional short prefix:

* **Canonical ID**: `mem.<type>.<topic>[.<topic2>...][.<qualifier>]`
* Charset: `[a-z0-9]+` segments separated by `.`
* Lowercase only (normalize on write)
* Variable length; encourage 3–6 segments

Examples:

* `mem.skill.prompting.style`
* `mem.system.auth.overview`
* `mem.workset.oauth-migration`
* `mem.pattern.release.cut`
* `mem.fact.http.default-timeout`
* `mem.glossary.rbac`

This is close to reverse-DNS naming without tying you to domains.

### Why this works

* `mem.` makes it trivially distinguishable from `ADR-012` / `SPEC-123`
* The second segment gives the “hint at type” you want without requiring a separate discriminator in links
* Dots are visually lighter than `-` for hierarchical meaning and play nicely with “qualified names”

### Allowed alias (optional, for brevity)

Permit an internal shorthand in authoring:

* Shorthand: `<type>.<topic...>` (e.g., `system.auth.overview`)
* On save, resolve/normalize to canonical `mem.system.auth.overview` in frontmatter `id`

You can also allow `mem:<id>` as a URI-ish form for CLI usage:

* `mem:system.auth.overview` (or `mem:mem.system.auth.overview`—pick one and normalize)

### Collision and refactor policy

* ID is **primary key**; file path is derived
* If you split/merge memories, use `supersedes` / `superseded_by` (IDs remain stable; paths can change)
* Enforce uniqueness at registry build time

### “Topic” guidance (keeps IDs consistent)

Recommend a predictable segment order:

`mem.<type>.<domain>.<subject>.<purpose>`

* `domain`: subsystem or area (`auth`, `billing`, `cli`, `repo`, `ci`)
* `subject`: concrete thing (`tokens`, `rbac`, `release`, `timeouts`)
* `purpose`: `overview`, `howto`, `constraints`, `checklist`, `faq`, etc.

This yields IDs that are easy to type and grep.

---

## Sidebar: identifying memory type cleanly

You have two separate problems:

1. How to identify the *artifact kind* (ADR vs SPEC vs MEM vs others) in an inline `[[...]]`
2. How to identify memory *type* (skill/system/workset/etc.)

With the proposed scheme, (2) is already encoded: `mem.<type>.…`

For (1), you have options depending on whether you want `[[...]]` to be unambiguous without lookups.

### Option A (recommended): keep `[[...]]` as “ID lookup”, rely on registry prefix

* `[[ADR-012]]`, `[[SPEC-123]]`, `[[mem.system.auth.overview]]`
* Rule: if token matches `^[A-Z]{3,}-\d+$`, treat as primitive ID; else treat as semantic memory ID; else fallback to registry lookup.
* Pros: no new syntax; readable; no “kind discriminator” needed.
* Cons: if you later add other semantic IDs, you may need additional disambiguation rules.

### Option B: explicit scheme prefix only when needed

* `[[mem:system.auth.overview]]`
* `[[adr:012]]` (optional later), `[[spec:123]]`
* Pros: future-proof and explicit.
* Cons: more typing; less aesthetically “Obsidian-like”.

A good compromise: accept both, normalize on save to canonical IDs in `links.out`.

### How to derive memory *type* if IDs aren’t trusted

Even if IDs encode type, you still want the source of truth to be frontmatter:

* `type: system|skill|...`

Resolver policy:

* Prefer `id` exact match in registry.
* Use frontmatter `type` as authoritative.
* Treat `mem.<type>.…` as a hint; warn if it disagrees with frontmatter (`id says system but type=pattern`).

This keeps you safe if someone hand-edits an ID.

---

## Practical resolution rules for `[[...]]` in v1.1

Given token content `T`:

1. If `T` contains `|`, split label: `target, label`
2. Normalize `target`:

   * trim whitespace
   * if `target` starts with `mem:` → strip scheme, then ensure canonical prefix `mem.`
3. Attempt resolution in order:

   * Exact ID match in registry (fast path)
   * If matches `^[A-Z]{3,}-\d+$`, try exact (ADR/SPEC style)
   * If starts with `mem.` or contains `.`, try memory ID normalization + lookup
   * (Optional) slug/title alias lookup (warn on ambiguity)

On save:

* Write `links.out` as canonical IDs + resolved paths
* Emit warnings for missing/ambiguous
* Do not rewrite inline token text unless you add a `--normalize-links` flag

---

## Summary recommendation

* Adopt canonical memory IDs: `mem.<type>.<domain>.<subject>[.<purpose>]`
* Keep inline `[[...]]` as plain ID lookup; accept optional `mem:` prefix but don’t require it
* Treat frontmatter `type` as authoritative; treat the `id`’s second segment as a hint and lint mismatches

This gets you ergonomic linking, avoids kind discriminators, and keeps memory internally consistent even though other primitives remain `XXX-nnn`.

