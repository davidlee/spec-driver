# supekku.scripts.lib.formatters.relation_formatters

Pure formatting functions for relation references.

Receives pre-collected `list[ReferenceHit]` — no business logic or artifact
access. Callers call `collect_references()` and pass the result.

Design reference: DR-085 §5.6, R4.

## Constants

- `__all__`

## Functions

- `format_refs_count(refs) -> str`: Format total reference count for table column.

Returns e.g. `"3 refs"`, `"1 ref"`, or `""` when empty.

- `format_refs_tsv(refs) -> str`: Format all references as `source.detail:target` pairs for TSV.

Returns e.g. `"relation.implements:PROD-010,context_input.issue:IMPR-006"`.
Empty detail omits the dot: `"relation:X"`.

- `format_related_section(referenced_by) -> list[str]`: Format the 'Referenced by' section for `--related` output.

_referenced_by_ maps artifact kind (e.g. `"delta"`) to a list of
`(id, name)` tuples. Returns formatted lines ready for `\n.join()`.
An empty _referenced_by_ dict produces an empty list (no section header).
