# Notes for DE-050

## 2026-03-06 - ADR draft for registry convention

- Drafted `ADR-009: standard registry API convention`.
- Decision: codify the minimum registry read surface as `find()`, `collect()`,
  `iter(status=None)`, and `filter(...)` plus keyword-only optional `root`
  auto-discovery for class-based registries.
- Adaptation: kept `filter()` mandatory, but as a domain-specific method rather
  than a shared universal signature; explicitly deferred any `Protocol`/ABC
  until post-normalisation convergence is proven.
- Rough edges / follow-up:
  - Requirements, backlog, and card registries remain structurally different;
    ADR-009 deliberately leaves their deeper reshaping to DE-050 implementation.
- Git state: uncommitted work, including unrelated repo changes already present.
- Verification: no commands run after this edit; this was ADR/notes drafting only.
