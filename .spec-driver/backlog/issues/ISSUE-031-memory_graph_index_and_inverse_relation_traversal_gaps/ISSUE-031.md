---
id: ISSUE-031
name: Memory graph index and inverse relation traversal gaps
created: '2026-03-02'
updated: '2026-03-02'
status: open
kind: issue
categories: []
severity: p3
impact: user
---

# Memory graph index and inverse relation traversal gaps

## Summary

V1 memory support intentionally keeps links advisory. This issue tracks
the unresolved gaps for a future v1.1 increment that adds robust
forward/inverse relation traversal across memory and existing artifacts.

## Deferred Gaps (YAGNI Inventory)

1. No unified cross-artifact graph index
   - Current registries are domain-local and cannot answer inverse
     queries consistently without multi-registry scans.
2. Mixed relation surfaces
   - Some artifacts use `relations`; others use typed arrays
     (`policies`, `standards`, `specs`, etc).
   - Need canonical normalization rules before inverse traversal is safe.
3. Identifier/path normalization
   - Need deterministic handling for padded IDs, aliases, and path refs.
4. Validation policy for unresolved links
   - Need explicit warning vs error semantics (and strict mode behavior).
5. Query UX not yet finalized
   - Need stable flags for `--related` / `--related-by` style traversal.

## Proposed Follow-up (v1.1+)

- Add derived graph registry: `.spec-driver/registry/graph.yaml`.
- Populate nodes + normalized edges from frontmatter + typed link fields.
- Add targeted query flags for memory forward/inverse traversal.
- Add validator coverage for unresolved canonical IDs.

## Acceptance Criteria

- Graph registry can be generated deterministically from repo state.
- At least one forward and one inverse relation query are implemented and tested.
- Unresolved canonical IDs produce deterministic diagnostics.
- `DR-033` extension notes are reflected in implementation docs.

## Related

- `change/deltas/DE-033-memory_records_schema_and_command_surface/DR-033.md`
- `change/revisions/RE-017-memory_schema_and_cli_taxonomy_alignment/mem.brief.md`
