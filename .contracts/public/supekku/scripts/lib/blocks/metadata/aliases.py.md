# supekku.scripts.lib.blocks.metadata.aliases

Field-VALUE alias normalisation for read-time tolerance (DE-137 / DEC-137-23).

Loaders call `normalize_field(kind, field_name, value)` to canonicalise a
field value via the metadata-declared alias maps. This is the
loader-default tolerant path; strictness gating is the validator's
concern (see ``validator.MetadataValidator.validate``).

Behaviour:

- Case-folds and strips the input string (preserving the legacy
  ``normalize_status`` semantics so callers see no regression on
  ``"DONE"`` / ``"  done  "`` style inputs).
- Returns the normalised value unchanged if the kind has no metadata,
  the field has no metadata, or no alias matches.
- Permanent ``FieldMetadata.aliases`` win over ``tolerated_aliases``;
  matching either returns the canonical value.

## Functions

- `normalize_field(kind, field_name, value) -> Any`: Return the canonical value for ``value`` on ``kind.field_name``.

Non-string values pass through unchanged. Strings are lower-cased and
whitespace-stripped before alias lookup.
