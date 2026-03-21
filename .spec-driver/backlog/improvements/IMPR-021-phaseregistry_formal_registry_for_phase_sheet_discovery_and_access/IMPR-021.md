---
id: IMPR-021
name: "PhaseRegistry: formal registry for phase sheet discovery and access"
created: "2026-03-21"
updated: "2026-03-21"
status: idea
kind: improvement
relations:
  - type: relates_to
    target: DE-104
    description: DE-104 opts for lightweight bundle-walking instead; this is the heavier alternative
  - type: relates_to
    target: ADR-009
    description: Would follow standard registry API convention
---

# PhaseRegistry: formal registry for phase sheet discovery and access

## Context

Phases are currently the only artifact type without a dedicated registry. They
live inside delta bundle directories (`deltas/DE-xxx/phases/phase-*.md`) and are
discovered ad-hoc by code that knows the bundle structure. DE-104 adds phase
status validation by walking delta bundles directly — sufficient for validation
but not a general-purpose access layer.

## What a PhaseRegistry would enable

- `list phases` / `show phase` CLI commands (currently missing)
- `edit phase --status` with enum validation (currently no `edit phase`)
- Cross-artifact relation traversal that includes phases
- Phase-aware workspace queries (e.g. "all in-progress phases across deltas")
- TUI phase browsing without delta-specific discovery code
- Consistent `find`/`collect`/`iter` API per ADR-009

## Costs and tensions

- **Discovery is non-trivial.** Phases nest inside delta bundles, not a flat
  directory. The registry must walk `deltas/*/phases/` — different from every
  other registry which scans a single top-level directory. This either requires
  a custom discovery path or a generalisation of the registry base class.
- **ID scheme is composite.** Phase IDs are `IP-xxx.PHASE-nn` — they contain
  their parent plan ID. The registry must handle lookup by full composite ID
  and potentially by phase number within a delta. No other registry has this
  parent-child ID structure.
- **Coupling to delta bundles.** A PhaseRegistry inherently couples to the delta
  bundle layout. If bundle structure changes, the registry must change too.
  Current ad-hoc discovery code has the same coupling but is localised to the
  few places that need it.
- **Workspace class expansion.** Adding `_phase_registry` to `Workspace` means
  the validator, CLI, and TUI all gain phase access — but also means every
  workspace load pays the cost of phase discovery even when not needed (unless
  lazy-loaded like other registries).
- **Nine registries already.** ADR-009 notes the existing surface is large.
  Adding a tenth is justified only if phases need the same access patterns as
  other artifacts. If phases are primarily accessed through their owning delta,
  the registry may be over-engineering.

## Known gap: `deferred` status has no CLI path

DE-104 skill guidance says "do not hand-edit phase frontmatter status" but
provides an explicit exception for `deferred` — the one status not covered by
`phase start` / `phase complete`. A narrow `phase defer <delta>` command (~15
lines, mirrors existing pattern) would close this gap without requiring a full
PhaseRegistry. Consider adding it alongside or instead of the full registry.

## When to revisit

- If `list phases` / `show phase` become requested features
- If TUI needs cross-delta phase browsing
- If validate's bundle-walking loop gets duplicated in multiple places
- If phase-level reporting (velocity, completion rates) becomes valuable

## Recommendation

Keep this as an idea until at least two of the "revisit" triggers fire. The
bundle-walking approach in DE-104 is adequate for validation and can be extracted
into a shared utility if reuse demand appears.
