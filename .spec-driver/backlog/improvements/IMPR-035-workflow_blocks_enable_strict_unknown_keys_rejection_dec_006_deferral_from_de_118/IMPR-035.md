---
id: IMPR-035
name: "workflow.* blocks: enable strict_unknown_keys rejection (DEC-006 deferral from DE-118)"
created: "2026-05-09"
updated: "2026-05-17"
status: idea
kind: improvement
---

# workflow.* blocks: enable strict_unknown_keys rejection (DEC-006 deferral from DE-118)

## Context

DE-118 retires 7 hand-rolled YAML block validators in favour of a unified `MetadataValidator` path. As part of that work, DR-118 introduces `MetadataValidator(metadata, strict_unknown_keys: bool = False)` — a per-instance opt-in for unknown-key rejection (DEC-001). The 7 retiring validators flip the flag to `True` at their loader call sites, preserving today's hand-rolled rejection behaviour.

The 7 **`workflow.*` blocks** below — historically validated by `MetadataValidator` directly (no hand-rolled rejector) — currently accept unknown keys silently. DR-118 DEC-006 explicitly **defers** their strict flip to a future delta to avoid a behaviour change before consumer-repo migration tooling exists.

## Affected blocks (the 7 workflow.* schemas)

Registered in `supekku/scripts/lib/blocks/workflow_metadata.py`:

1. `workflow.state` — current orchestration status and pointers
2. `workflow.handoff` — durable phase-boundary transition payload
3. `workflow.review-index` — reviewer bootstrap cache
4. `workflow.review-findings` — stable issue ledger across review rounds
5. `workflow.sessions` — runtime session map
6. `workflow.notes-bridge` — pointer block in notes.md to workflow files
7. `workflow.phase-bridge` — phase-close signal in phase sheets

## Receiving artefact

**Primary**: **DE-137** (cross-cutting metadata schema infrastructure under DE-136 / DR-136).

**Fallback**: if DE-137 is never drafted or is descoped, governance reverts to **DE-136** directly via DR-136 §11.3 (per-kind strict flag in `workflow.toml`). In either case this IMPR closes only when the 7 workflow.* loaders run with strictness equivalent to `strict_unknown_keys=True` and consumer-migration coverage exists.

**Integrity guard**: this IMPR cannot be closed `wontfix` while either DE-137 is open *or* DR-136 §11.3 still describes per-kind strict flags. Closure requires positive evidence that the receiving artefact has shipped the deferred behaviour.

## Deferred work

Flip these 7 schemas' loader call sites to `strict_unknown_keys=True` once the receiving consumer-migration story is in place. Governance lives at DR-136 §11.3 (per-kind strict flag in `workflow.toml`, default-off for upgrading consumers, default-on for fresh installs).

Mechanism options the receiving delta may pick from:

- Promote `strict_unknown_keys` from `MetadataValidator` constructor arg to a `BlockMetadata` declarative field; flip the 7 block declarations.
- Promote to `workflow.toml` per-kind flag (workflow blocks fall under their own kind or grouped); CLI surface gates the flip.
- Direct call-site flip at the 3 known loader sites (`review_io.py:79–80`, `handoff_io.py:38`, `state_io.py:37`).

Whichever shape DE-137 chooses, this IMPR is closed by:

1. The 7 workflow.* loaders running with strictness equivalent to `strict_unknown_keys=True`.
2. Consumer-repo migration / drift-detection coverage for any unknown-key data in the wild.
3. A test (curated or corpus) demonstrating the rejection.

## Acceptance criteria

- [ ] All 7 workflow.* schemas reject unknown keys (or the equivalent semantics under whatever flag shape DE-137 lands).
- [ ] Consumer-repo migration story documented (DR-136 §11.3 or successor).
- [ ] This IMPR closed via reference from the receiving delta's close-change.

## First-contact strictness (DE-118 P04 4.2)

DE-118 P04 4.2 replaced the `_entry_shape` sentinel in `WORKFLOW_SESSIONS_METADATA` with `additional_properties=_SESSION_ENTRY` (per DR-118 DEC-004). This activates declarative per-entry validation on `workflow.sessions` blocks (one of the 7 workflow.* schemas above). The change is orthogonal to the DEC-006 unknown-key deferral — `strict_unknown_keys` remains `False` at the loader call site — but it *does* introduce new enforcement at the per-entry shape level: consumer repos emitting `workflow.sessions` blocks with missing required fields (`session_name`, `status`, `last_seen`) or out-of-enum `status` values will be rejected at first contact.

R7 vacuous in DE-118's repo (zero live `.spec-driver/run/sessions/` data per P01 §2); first-contact strictness applies wherever consumer repos do emit `workflow.sessions` blocks. Treat this as a *complementary* constraint to the unknown-key deferral, not a substitute for it.

## Provenance

- Originating delta: **DE-118** — DR-118 §7 DEC-006.
- Cross-cutting governance: **DE-136 / DR-136** — particularly §11.3 (consumer-repo migration model) and §12 (code-impact roll-up listing `validation/` as cross-cutting infrastructure).
- Receiving delta (intended): **DE-137** — not yet drafted at IMPR creation time.

## Related

- DR-118 §7 DEC-006 (this deferral, with full rationale)
- DR-118 §9 R6 (risk: DR-136 cross-reference is best-effort, not under DE-118's authority)
- DR-136 §5 (cross-cutting child delta deliverables) and §11.3 (consumer migration)
