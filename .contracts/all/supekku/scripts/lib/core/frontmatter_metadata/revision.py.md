# supekku.scripts.lib.core.frontmatter_metadata.revision

Revision frontmatter metadata for kind: revision artifacts (DE-142 P02).

Completes the DE-137 stub to the **narrow** DR-142 §5 shape (DEC-CONSULT-01,
user-approved 2026-05-29): Base 7 + ``relations`` + ``tags`` +
``ext_id``/``ext_url``. Unlike audit/delta (which keep the full BASE spread),
revisions deliberately OMIT ``lifecycle``/``auditers``/``source``/``owners``/
``summary`` and the hand-rolled scope keys — those reject under strict at the
P04 flip. Verified zero corpus lossage: no revision in the 42-record corpus
carries any omitted key.

``applies_to`` is derived from the ``supekku:revision.change@v1`` block at load
(DEC-142-05 / DEC-138-10), never stored in frontmatter here.

Note: the shared BASE ``kind`` enum omits ``revision`` (it lists
``design_revision`` for DR-* artefacts, not RE-* revisions), so this class pins
``kind`` to ``["revision"]`` locally rather than widening the shared enum.

## Constants

- `REVISION_FRONTMATTER_METADATA`
- `_BASE`
- `__all__`
