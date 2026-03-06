# Notes for DE-013

- `uv run spec-driver schema list` confirms availability of `frontmatter.design_revision` schema alongside block catalogues.
- Glossary entry: “Design Revision (DR)” – architecture patch capturing current vs target behaviour, code hotspots, test impacts.
- Schema inspection pending deeper review (Phase 1 Task 1.1).
- Drafted design revision template (`.spec-driver/templates/design_revision.md` + packaged copy) covering summary, problem, code impacts, verification, context, decisions, questions, rollout, and references.
- `create_delta` now scaffolds `DR-XXX.md` with initial frontmatter linking back to the delta and placeholder arrays for context, impacts, verifications, decisions, and questions.
- Authored initial `change/deltas/DE-013.../DR-013.md` using new template; captured code impacts on creation logic and templates plus verification outline.
- Linting: `just lint` + `just pylint` succeed (pylint reports existing complexity warnings). Full `uv run pytest supekku` fails when tests write to `/home/david`; targeted suite `supekku/scripts/lib/changes/creation_test.py` passes locally.

- The earlier sandbox failure stemmed from supekku/scripts/lib/specs/
  creation_test.py::CreateSpecTest::test_repository_root_not_found. That test
  uses tempfile.TemporaryDirectory(dir=Path.home()), which resolves to /home/
  david/…; in the restricted environment that directory wasn’t writable, hence
  the PermissionError. Running the suite with a real HOME or overriding HOME/
  TMPDIR to a writable path sidesteps it.