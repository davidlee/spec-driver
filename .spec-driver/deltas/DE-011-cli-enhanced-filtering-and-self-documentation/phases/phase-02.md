---
id: IP-011.PHASE-02
slug: "011-cli-enhanced-filtering-and-self-documentation-phase-02"
name: IP-011 Phase 02 - Self-Documentation
created: "2026-03-04"
updated: "2026-03-21"
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-011.PHASE-02
plan: IP-011
delta: DE-011
objective: >-
  Add schema enum introspection and enhanced help text so agents can discover
  valid filter values and output format options without external documentation.
entrance_criteria:
  - Phase 1 complete (multi-value filters, reverse queries, vstatus/vkind all passing)
  - Full test suite green (just test)
  - Both linters passing (just lint, just pylint)
  - Existing schema command working (schema list, schema show)
exit_criteria:
  - schema show enums.<artifact>.<field> returns JSON array of valid values
  - All key artifact/field combinations covered (delta.status, spec.kind, requirement.status, requirement.kind, verification.status, verification.kind, command.format)
  - All list command help text includes "Output Formats" section with examples
  - All list command help text includes filter syntax examples (multi-value, reverse query)
  - show command help documents --json, --path, --raw options
  - Unit tests for enum extraction and help text content
  - Both linters passing with zero warnings
verification:
  tests:
    - VT-CLI-ENUM-INTROSPECTION
    - VT-CLI-HELP-EXAMPLES
  evidence:
    - VT-PROD010-SCHEMA-001
    - VT-PROD010-SCHEMA-002
tasks:
  - id: "2.1"
    description: Research enum sources and schema command extension points
    status: pending
  - id: "2.2"
    description: Write enum introspection tests (TDD)
    status: pending
  - id: "2.3"
    description: Implement enum registry and schema show enums subcommand
    status: pending
  - id: "2.4"
    description: Write help text content tests (TDD)
    status: pending
  - id: "2.5"
    description: Add Output Formats sections to all list command help
    status: pending
  - id: "2.6"
    description: Update show command help with format documentation
    status: pending
  - id: "2.7"
    description: Full test suite + linters
    status: pending
  - id: "2.8"
    description: Manual validation
    status: pending
risks:
  - description: Enum values scattered across modules with no central registry
    likelihood: confirmed
    impact: medium
    mitigation: Create lightweight enum registry mapping artifact.field to source constants
  - description: Help text verbosity makes commands harder to scan
    likelihood: medium
    impact: low
    mitigation: Keep examples concise; use epilog sections for extended docs
```

# Phase 02 - Self-Documentation

## 1. Objective

Enable agents to discover valid values and learn usage patterns directly from CLI help,
eliminating documentation lookups and trial-and-error:

1. **Enum introspection** (FR-006): `schema show enums.delta.status` → JSON array
2. **Enhanced help text** (FR-007): All list/show commands include output format examples
   and filter syntax documentation

**Success Signal**: Agent never needs external docs to construct a valid CLI command.

## 2. Links & References

- **Delta**: [DE-011](../DE-011.md)
- **Product Spec**: [PROD-010](../../../specify/product/PROD-010/PROD-010.md) — FR-006, FR-007
- **Tech Spec**: [SPEC-110](../../../specify/tech/SPEC-110/SPEC-110.md) — supekku/cli
- **Existing**: `supekku/cli/schema.py` — schema list/show infrastructure
- **Enum sources**:
  - `supekku/scripts/lib/changes/lifecycle.py` — `VALID_STATUSES`, `CANONICAL_STATUS_MAP`
  - `supekku/scripts/lib/requirements/lifecycle.py` — `VALID_STATUSES`
  - `supekku/scripts/lib/blocks/verification.py` — `VALID_KINDS`, `VALID_STATUSES`

## 3. Entrance Criteria

- [x] Phase 1 complete (all tasks 1.1–1.14 done)
- [x] `just test` passing
- [x] `just lint` + `just pylint` passing
- [x] `uv run spec-driver schema list` and `schema show` working

## 4. Exit Criteria / Done When

- [x] `schema show enums.delta.status` → `["completed", "deferred", "draft", "in-progress", "pending"]`
- [x] `schema show enums.spec.kind` → `["prod", "tech"]`
- [x] `schema show enums.requirement.status` → `["active", "in-progress", "pending", "retired"]`
- [x] `schema show enums.requirement.kind` → `["FR", "NF"]`
- [x] `schema show enums.verification.status` → `["blocked", "failed", "in-progress", "planned", "verified"]`
- [x] `schema show enums.verification.kind` → `["VA", "VH", "VT"]`
- [x] `schema show enums.command.format` → `["json", "table", "tsv"]`
- [x] `schema show enums` (no args) lists all available enums
- [x] All list command help includes "Examples:" section
- [x] All list command help includes filter syntax with multi-value examples
- [x] Show command help documents `--json`, `--path`, `--raw` (already present)
- [x] Tests passing, linters clean

## 5. Verification

**Unit Tests**:

```bash
# Enum introspection tests
uv run pytest supekku/cli/schema_test.py -v -k enums

# Help text content tests
uv run pytest supekku/cli/test_cli.py -v -k help_text
```

**Integration Tests**:

```bash
just test
just lint
just pylint
```

**Manual Validation**:

```bash
# Enum introspection
uv run spec-driver schema show enums.delta.status
uv run spec-driver schema show enums.requirement.kind
uv run spec-driver schema show enums

# Help text
uv run spec-driver list deltas --help
uv run spec-driver list requirements --help
uv run spec-driver show spec --help
```

## 6. Assumptions & STOP Conditions

**Assumptions**:

- Enum values sourced from existing lifecycle constants (not hardcoded duplicates)
- `schema show enums` namespace fits naturally under existing schema command
- Help text changes are additive (no existing behavior broken)
- Typer epilog or docstring extension sufficient for help text enrichment

**STOP Conditions**:

- If enum values cannot be reliably extracted from constants (e.g. spec.kind has no constant),
  STOP to decide: hardcode or introspect frontmatter metadata
- If help text changes exceed Typer's formatting capabilities, STOP to evaluate alternatives

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description                                     | Parallel? | Notes                                          |
| ------ | --- | ----------------------------------------------- | --------- | ---------------------------------------------- |
| [x]    | 2.1 | Research enum sources + schema extension points | [ ]       | Done — see Section 10                          |
| [x]    | 2.2 | Write enum introspection tests (TDD)            | [ ]       | 10 tests, TDD red→green                        |
| [x]    | 2.3 | Implement enum registry + schema show enums     | [ ]       | core/enums.py + schema.py routing              |
| [x]    | 2.4 | Write help text content tests (TDD)             | [x]       | 10 tests, TDD red→green                        |
| [x]    | 2.5 | Add Output Formats to list command help         | [ ]       | 4 docstrings updated                           |
| [x]    | 2.6 | Update show command help                        | [x]       | Skipped — show commands already document flags |
| [x]    | 2.7 | Full test suite + linters                       | [ ]       | 2514 passed, ruff clean, pylint 9.63           |
| [x]    | 2.8 | Manual validation                               | [ ]       | All enum paths + help text verified            |

### Task Details

#### **2.1 Research enum sources + schema extension points**

- **Design / Approach**:
  - Catalogue all enum sources and their module locations:
    - `changes/lifecycle.py` → `VALID_STATUSES` (delta/revision/audit status)
    - `requirements/lifecycle.py` → `VALID_STATUSES` (requirement status)
    - `blocks/verification.py` → `VALID_KINDS`, `VALID_STATUSES` (verification)
    - spec kind: no constant exists — need to decide: hardcode `["prod", "tech"]` or extract from
      frontmatter metadata
    - requirement kind: no constant — likely `["FR", "NF"]` from label prefix convention
    - command format: no constant — `["table", "json", "tsv"]` from CLI help text
  - Decide extension strategy: new `enums` subcommand under `schema`, or extend `schema show`
  - Review Typer patterns for subcommand routing with dotted namespace (`enums.delta.status`)
- **Files / Components**:
  - `supekku/cli/schema.py` — current schema command structure
  - Lifecycle modules — enum constants
- **Testing**: No tests for research phase

#### **2.2 Write enum introspection tests (TDD)**

- **Design / Approach**:
  - Create `supekku/cli/schema_test.py` (or add to existing test file)
  - Test `schema show enums.delta.status` → sorted JSON array
  - Test `schema show enums.requirement.status` → sorted JSON array
  - Test `schema show enums.verification.kind` → `["VA", "VH", "VT"]`
  - Test `schema show enums` (bare) → list of available enum paths
  - Test invalid path: `schema show enums.nonexistent.field` → error + available list
  - Test that returned values match actual lifecycle constants (no drift)
- **Files / Components**:
  - `supekku/cli/schema_test.py` — new test file or extend existing
- **Testing**: Tests will initially FAIL (TDD red phase)

#### **2.3 Implement enum registry + schema show enums**

- **Design / Approach**:
  - Create `supekku/scripts/lib/core/enums.py` — lightweight enum registry:
    ```python
    ENUM_REGISTRY: dict[str, Callable[[], list[str]]] = {
      "delta.status": lambda: sorted(CANONICAL_STATUS_MAP.values() - {"completed"}),
      "requirement.status": lambda: sorted(req_lifecycle.VALID_STATUSES),
      "verification.status": lambda: sorted(ver.VALID_STATUSES),
      "verification.kind": lambda: sorted(ver.VALID_KINDS),
      ...
    }
    ```
  - Use lazy callables so imports only happen when queried
  - Extend `schema show` to handle `enums.*` namespace:
    - `enums` alone → list all paths
    - `enums.<artifact>.<field>` → JSON array output
  - Output: plain JSON array to stdout (agent-friendly, no Rich formatting)
- **Files / Components**:
  - `supekku/scripts/lib/core/enums.py` — new module
  - `supekku/cli/schema.py` — extend `show_schema` to route `enums.*`
- **Testing**: Run tests from 2.2; should now PASS (TDD green phase)

#### **2.4 Write help text content tests (TDD)**

- **Design / Approach**:
  - Test that each list command's help text contains:
    - "Output Formats" (or equivalent heading)
    - Example of `--format json` or `--json`
    - Example of multi-value filter syntax (e.g., `-s draft,in-progress`)
  - Test that show command help mentions `--json`, `--path`, `--raw`
  - Use Typer test client to capture `--help` output and assert substrings
- **Files / Components**:
  - `supekku/cli/test_cli.py` — add `TestHelpTextContent` class
- **Testing**: Tests will initially FAIL (TDD red phase)

#### **2.5 Add Output Formats to list command help**

- **Design / Approach**:
  - Extend each list command docstring with an "Output Formats" section:
    - table (default): human-readable Rich table
    - json: machine-readable JSON object with `items` array
    - tsv: tab-separated values for piping
  - Add filter syntax examples showing multi-value and reverse query usage
  - Use Typer `epilog` or extended docstring — whichever renders better
  - Commands to update: list deltas, list specs, list requirements, list adrs,
    list changes, list revisions
- **Files / Components**:
  - `supekku/cli/list.py` — update docstrings for all list commands
- **Testing**: Run tests from 2.4; should now PASS

#### **2.6 Update show command help**

- **Design / Approach**:
  - Document `--json`, `--path`, `--raw` options in show command docstrings
  - Add brief usage guidance: when to use each format
  - Commands: show delta, show spec, show adr, show requirement
- **Files / Components**:
  - `supekku/cli/show.py` — update docstrings
- **Testing**: Help text tests from 2.4

#### **2.7 Full test suite + linters**

- **Design / Approach**:
  - `just test` — full suite green
  - `just lint` — ruff clean
  - `just pylint` — threshold met
  - Fix any issues discovered
- **Files / Components**: All modified files

#### **2.8 Manual validation**

- **Design / Approach**:
  - Run enum introspection commands, verify output
  - Check help text renders correctly in terminal
  - Verify agent workflow: construct a complete query using only CLI help + enum introspection
  - Cross-reference with PROD-010.FR-006 and FR-007 requirements
- **Files / Components**: N/A (manual testing)

## 8. Risks & Mitigations

| Risk                                                     | Mitigation                                                      | Status  |
| -------------------------------------------------------- | --------------------------------------------------------------- | ------- |
| Enum values scattered, no single source of truth for all | Enum registry with lazy imports; document source per entry      | Planned |
| spec.kind / requirement.kind have no lifecycle constants | Hardcode with comment citing source; create constants if reused | Planned |
| Help text too verbose for Typer rendering                | Test rendering; use epilog for extended examples                | Planned |
| Help text examples drift from actual behavior            | Tests assert help content; catch drift in CI                    | Planned |

## 9. Decisions & Outcomes

- `2026-03-04` - Phase planned; enum registry approach chosen over hardcoded switch statement

## 10. Findings / Research Notes

**Enum Sources (confirmed)**:

| Enum Path             | Source                                     | Values                                                                       |
| --------------------- | ------------------------------------------ | ---------------------------------------------------------------------------- |
| `delta.status`        | `changes/lifecycle.VALID_STATUSES`         | draft, pending, in-progress, completed, deferred (exclude legacy "complete") |
| `requirement.status`  | `requirements/lifecycle.VALID_STATUSES`    | pending, in-progress, active, retired                                        |
| `verification.status` | `blocks/verification.VALID_STATUSES`       | planned, in-progress, verified, failed, blocked                              |
| `verification.kind`   | `blocks/verification.VALID_KINDS`          | VA, VH, VT                                                                   |
| `spec.kind`           | **no constant** — hardcode                 | prod, tech                                                                   |
| `requirement.kind`    | **no constant** — hardcode                 | FR, NF                                                                       |
| `command.format`      | **no constant** — hardcode                 | json, table, tsv                                                             |
| `artifact.kind`       | `frontmatter_metadata/base.py` enum_values | audit, delta, ... (16 values)                                                |
| `lifecycle`           | `frontmatter_metadata/base.py` enum_values | discovery, design, implementation, verification, maintenance                 |

**Extension strategy**: Add `enums.*` prefix routing in `schema.py:show_schema`, alongside existing `frontmatter.*` routing. New `core/enums.py` module provides the registry.

**Decision**: Use canonical lifecycle constants where they exist. For `spec.kind`, `requirement.kind`, `command.format` — hardcode with comments citing source. These are stable enough that drift risk is low.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied (all 12 items in Section 4)
- [x] Verification evidence stored (test outputs)
- [x] IP-011 verification coverage updated (all 4 VT/VH → verified)
- [x] DE-011 updated with Phase 2 completion notes
- [x] Delta closure readiness assessed — ready for closure
