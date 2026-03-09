# supekku.scripts.lib.drift.registry

Drift ledger registry — read-only discovery and access.

Discovers drift ledger files in .spec-driver/drift/ and provides
find/iter/collect access. No YAML registry sync (deferred per IMPR-007 D2).

See DEC-065-04.

## Constants

- `_LEDGER_FILE_RE` - Matches DL-NNN or DL-NNN-slug filenames
- `logger`

## Functions

- `_load_ledger(path) -> <BinOp>`: Load a single drift ledger from a markdown file.

## Classes

### DriftLedgerRegistry

Read-only registry for drift ledger discovery and access.

Discovers ledger files in .spec-driver/drift/ on first access (lazy).

#### Methods

- `collect(self) -> dict[Tuple[str, DriftLedger]]`: Return all discovered drift ledgers, keyed by ID.
- `find(self, ledger_id) -> <BinOp>`: Find a single drift ledger by ID.
- `iter(self) -> Iterator[DriftLedger]`: Iterate over drift ledgers, optionally filtered by status.
- `__init__(self, root) -> None`
- `_load(self) -> dict[Tuple[str, DriftLedger]]`: Discover and parse all drift ledger files.
