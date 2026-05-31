---
id: mem.pattern.validation.per-kind-block-wiring
name: Per-kind block validation wiring in WorkspaceValidator
kind: memory
status: active
memory_type: pattern
created: "2026-05-21"
updated: "2026-05-21"
verified: "2026-05-21"
confidence: high
tags: [validation, workspace-validator, blocks]
summary: "Template for wiring per-kind block validators (context_inputs, risk_register) into WorkspaceValidator — established by DE-138 P04; DE-139..142 follow same shape"
links:
  missing:
    - raw: DEC-138-14
    - raw: DR-138
---

# Per-kind block validation wiring in WorkspaceValidator

DE-138 P04 established the first per-kind block validator wiring in `WorkspaceValidator`. Sibling deltas DE-139..142 will add their own kind-specific block validators following this exact pattern.

## Pattern

1. **Block metadata + validator** in `supekku/scripts/lib/blocks/<kind>_metadata.py`:
   - Declare `BlockMetadata` with strict schema, field_aliases, tolerated_aliases
   - Export validator instances (e.g. `DELTA_CONTEXT_INPUTS_VALIDATOR`) in `__all__`

2. **Extract helper** in `supekku/scripts/lib/blocks/<kind>.py`:
   - `extract_<kind>_<block>(artifact)` returns typed block or None

3. **WorkspaceValidator method** in `supekku/scripts/lib/validation/validator.py`:
   - Add `_validate_<kind>_blocks(self, registry)` method
   - Iterate registry, extract blocks, call `VALIDATOR.validate(block.data, strict=self.strict, accept_tolerated=self.accept_tolerated)`
   - Dispatch each `ValidationError` at native severity via `_block_issue` helper
   - Call from `validate()` immediately before kind-aware FM validation

4. **Single invocation site**: per-kind block validation must have exactly one call site to avoid drift. Do not duplicate across modules.

5. **Kind isolation**: per-kind validators only run for their kind. Non-delta kinds unaffected by `--no-tolerated-aliases` until their own wiring lands.

## Reference implementation

- `WorkspaceValidator._validate_delta_blocks` in `supekku/scripts/lib/validation/validator.py`
- Tests: `validator_test.py::TestDeltaBlockTolerationGateVTDE138GATE001`, `TestDeltaBlockStrictEnforcementVTDE138FLIP001`
- CLI threading: `spec_driver/presentation/cli/validate/workspace.py` passes `accept_tolerated` into `validate_workspace`

## Provenance

- [[DE-138]] P04; [[DEC-138-14]]; [[DR-138]] §5.4
- Commit `6c638eea` (wiring + VTs)
