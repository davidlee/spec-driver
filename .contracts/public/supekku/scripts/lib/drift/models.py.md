# supekku.scripts.lib.drift.models

Drift ledger models and lifecycle vocabulary.

A drift ledger tracks divergence between normative truth (specs/ADRs/policies)
and observed truth (code/contracts/runtime). See IMPR-007, ADR-008, DR-065.

Lifecycle constants use permissive validation with warnings (DEC-057-08 pattern).

## Constants

- `logger`

## Functions

- `is_valid_entry_status(status) -> bool`: Check whether a status is in the accepted entry lifecycle set.

Returns True for known statuses, False for unknown. Logs a warning
for unknown values (permissive validation per DEC-057-08).
- `is_valid_ledger_status(status) -> bool`: Check whether a status is in the accepted ledger lifecycle set.

## Classes

### Claim

What is conflicting or unclear — an assertion, observation, gap, or question.

### DiscoveredBy

Discovery origin for a drift entry.

### DriftEntry

A single drift entry within a ledger.

Fields follow IMPR-007 D1–D14 with typed substructures (DEC-065-06).
Progressive strictness: only id, title, status, and entry_type are
expected at minimum. All other fields default to empty.

### DriftLedger

A drift ledger — one file per scope of work.

Contains frontmatter metadata plus parsed entries.
See IMPR-007 D1 (ledger-as-file) and DEC-065-08 (body preserved).

### Source

Where drift appears — an artifact reference with optional context.
