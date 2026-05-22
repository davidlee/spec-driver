---
id: IP-139-P01
slug: "139-spec_metadata_propagation-phase-01"
name: IP-139 Phase 01 — Block schemas + FM field removals + taxonomy strict
created: "2026-05-22"
updated: "2026-05-22"
status: in-progress
kind: phase
plan: IP-139
delta: DE-139
---

# Phase 1 — Block schemas + FM field removals + taxonomy strict

## 1. Objective

Define 3 new block schemas (concerns, hypotheses, decisions), remove deprecated/moved FM field declarations from spec.py and prod.py, and promote category/c4_level to strict enum validation with tolerated `unknown` alias.

## 2. Entrance Criteria

- [x] DR-139 authored and reviewed
- [x] DE-138 precedent pattern understood (block schema shape, FM removal, tolerated_alias)
- [x] Migration burden quantified (0 files for block moves)

## 3. Exit Criteria

- [x] `supekku:spec.concerns@v1`, `supekku:spec.hypotheses@v1`, `supekku:spec.decisions@v1` block schemas defined with validators
- [x] Extract/render functions for each block
- [x] FM fields removed from spec.py: concerns, hypotheses, decisions, scope, verification_strategy, packages
- [x] FM fields removed from prod.py: hypotheses, decisions, scope, verification_strategy
- [x] SPEC category promoted to strict enum (unit|assembly) with tolerated unknown
- [x] SPEC c4_level adds tolerated unknown alias
- [x] VT-DE139-TAXONOMY-001, VT-DE139-TAXONOMY-002, VT-DE139-BLOCKS-001 passing
- [x] `just test` passing; `just lint` clean

## 4. Tasks

| Status | ID | Description | Notes |
|---|---|---|---|
| [x] | 1.1 | Define SPEC_CONCERNS_METADATA block schema in spec_metadata.py | DR-139 §4.1 |
| [x] | 1.2 | Define SPEC_HYPOTHESES_METADATA block schema (shared SPEC+PROD) | DR-139 §4.2 |
| [x] | 1.3 | Define SPEC_DECISIONS_METADATA block schema (shared, rationale optional) | DR-139 §4.3 |
| [x] | 1.4 | Add extract/render functions for each new block | Mirror existing spec_relationships/capabilities pattern |
| [x] | 1.5 | Remove FM field declarations from spec.py (concerns/hypotheses/decisions/scope/verification_strategy/packages) | DR-139 §5.1 |
| [x] | 1.6 | Remove FM field declarations from prod.py (hypotheses/decisions/scope/verification_strategy) | DR-139 §5.3 |
| [x] | 1.7 | Promote SPEC category to strict enum with tolerated unknown | DR-139 §5.2; aliases + tolerated_aliases |
| [x] | 1.8 | Add tolerated unknown alias to SPEC c4_level | DR-139 §5.2 |
| [x] | 1.9 | Write VT-DE139-BLOCKS-001 tests (block schema validation) | Test accept/reject for each schema |
| [x] | 1.10 | Write VT-DE139-TAXONOMY-001 test (category strict) | |
| [x] | 1.11 | Write VT-DE139-TAXONOMY-002 test (c4_level tolerated unknown) | |
| [x] | 1.12 | Verify existing tests pass after FM removals | `just test` |
| [x] | 1.13 | Lint clean | `just lint` |

## 5. Task Details

### 1.1–1.3 Block schemas

Follow pattern from `delta_metadata.py` DELTA_CONTEXT_INPUTS_METADATA / DELTA_RISK_REGISTER_METADATA. Each schema:
- Declared as `BlockMetadata` with `schema_id`, `version`, `fields` dict
- Required `spec` field (parent spec/prod ID)
- Required array field with item schema
- Registered in block metadata registry

### 1.4 Extract/render functions

Add to `blocks/spec_metadata.py` (or split into `blocks/spec.py` — follow existing pattern):
- `extract_spec_concerns(content) -> dict | None`
- `extract_spec_hypotheses(content) -> dict | None`
- `extract_spec_decisions(content) -> dict | None`
- `render_spec_concerns(data) -> str`
- `render_spec_hypotheses(data) -> str`
- `render_spec_decisions(data) -> str`

### 1.5–1.6 FM field removals

Remove field definitions from `SPEC_FRONTMATTER_METADATA.fields` and `PROD_FRONTMATTER_METADATA.fields`. No code reads these fields from FM (confirmed in DR-139 §2.2 survey). Existing specs with these fields in FM will validate tolerantly (unknown keys warn, not error, until strict-flip).

### 1.7–1.8 Taxonomy strict

`category`: change from string type to enum type with `allowed_values=["unit", "assembly"]`. Add `tolerated_aliases={"unknown": {"canonical": "unknown", "sunset": "DE-139 taxonomy reconciliation"}}`.

`c4_level`: already enum. Add `tolerated_aliases={"unknown": {"canonical": "unknown", "sunset": "DE-139 taxonomy reconciliation"}}`.

## 6. Verification

- VT-DE139-BLOCKS-001: block schema accept/reject for concerns, hypotheses, decisions
- VT-DE139-TAXONOMY-001: category strict enum — valid values accepted, invalid rejected, unknown tolerated
- VT-DE139-TAXONOMY-002: c4_level — unknown tolerated
- `just test` — no regressions
- `just lint` — clean

All passing: 5058 tests, 0 lint errors (2026-05-22).

## 7. Notes

- Constants (CONCERNS_SCHEMA etc.) defined in relationships.py to avoid circular imports with spec_metadata.py
- tolerated_aliases requires ToleratedAlias objects, not plain strings (sharp edge from DE-137)
- Validator emits tolerated-alias messages at warning severity, not error — tests filter by severity
