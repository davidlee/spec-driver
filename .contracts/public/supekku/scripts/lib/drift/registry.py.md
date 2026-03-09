# supekku.scripts.lib.drift.registry

Drift ledger registry — read-only discovery and access.

Discovers drift ledger files in .spec-driver/drift/ and provides
find/iter/collect access. No YAML registry sync (deferred per IMPR-007 D2).

See DEC-065-04.

## Constants

- `logger`

## Classes

### DriftLedgerRegistry

Read-only registry for drift ledger discovery and access.

Discovers ledger files in .spec-driver/drift/ on first access (lazy).

#### Methods

- `collect(self) -> dict[Tuple[str, DriftLedger]]`: Return all discovered drift ledgers, keyed by ID.
- `find(self, ledger_id) -> <BinOp>`: Find a single drift ledger by ID.
- `iter(self) -> Iterator[DriftLedger]`: Iterate over drift ledgers, optionally filtered by status.
