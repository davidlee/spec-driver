# supekku.scripts.lib.blocks.metadata.snapshot_compare

Metadata-driven block-validation corpus smoke check.

For each block instance in a `.spec-driver/` corpus, this harness invokes
``MetadataValidator(metadata, strict_unknown_keys=True)`` driven by the
block's metadata declaration, plus any registered hand-rolled adapter
(see ``HAND_ROLLED_ADAPTERS``). Disagreement at the verdict level
(accept/reject) signals drift between the two paths; with the adapter
map empty, the harness reduces to a metadata-only corpus pass that
reports parse health and validator acceptance counts.

CLI:

    python -m supekku.scripts.lib.blocks.metadata.snapshot_compare --root .

Exit code:

    0 — every block agreed (or had no hand-rolled counterpart).
    1 — at least one disagreement (or malformed-YAML failure).

Owner: blocks-metadata subsystem (`supekku/scripts/lib/blocks/metadata/`).
Re-run trigger (STD-004): invoke after extending or modifying any
``*_metadata.py`` declaration to catch corpus drift before it lands in
the test suite. Also useful as a one-shot diagnostic when investigating
validator semantics against the live ``.spec-driver/`` corpus.

History: originated in DE-118 P02 as the dual-validate harness pinning
hand-rolled vs metadata-driven verdict parity during the P03 swap
sequence. P03 retired all 7 hand-rolled validators; ``HAND_ROLLED_ADAPTERS``
is empty at HEAD. OQ-HARNESS-LIFECYCLE settled in DE-118 P04 4.6 (option
(a) keep — per phase-04 §9).

## Constants

- `HandRolledAdapter` - Adapter signature: (data: dict, frontmatter_id: str | None) -> list[str of errors]

## Functions

- `_frontmatter_id(file) -> <BinOp>`: Read frontmatter and return ``id`` field, if any.
- `_print_report(report) -> None`: Print a corpus run summary to stdout.
- `_scan_file(file) -> Iterable[tuple[Tuple[str, <BinOp>, BlockSchema, str]]]`: Yield (block_type, parsed_data_or_None, schema, raw_yaml) for each block.

``parsed_data is None`` indicates malformed YAML; ``raw_yaml`` carries the
unparsed text for diagnostics.
- `compare_block(file, block_type, data, schema, frontmatter_id) -> <BinOp>`: Dual-validate a single block; return ``Disagreement`` on verdict mismatch.
- `main(argv) -> int`: CLI entrypoint: parse ``--root``, run the harness, print the report.
- `run(root) -> Report`: Run the harness against ``<root>/.spec-driver/`` and return a report.

## Classes

### Disagreement

A block where hand-rolled and metadata-driven validators disagreed.

#### Methods

- @property `hand_rolled_passed(self) -> bool`: True when the hand-rolled validator accepted the block.
- @property `metadata_passed(self) -> bool`: True when the metadata-driven validator accepted the block.
- `render(self) -> str`: Render the disagreement as a human-readable multi-line string.

### MalformedBlock

A YAML block that failed to parse — surfaced separately from disagreements.

#### Methods

- `render(self) -> str`: Render the malformed-YAML record as a single-line diagnostic string.

### Report

Result of a corpus run.

#### Methods

- @property `ok(self) -> bool`: Run is OK iff zero verdict disagreements.

Malformed YAML is a pre-existing data-quality concern surfaced for
visibility but orthogonal to validator drift; it does not gate.
