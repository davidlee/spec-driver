---
id: "{{ adr_id }}"
name: "{{ name }}"
slug: "{{ slug }}"
kind: adr  # one of: audit | delta | design_revision | issue | memory | phase | plan | policy | problem | prod | requirement | risk | spec | standard | task | verification
status: draft  # one of: accepted | deprecated | draft | proposed | rejected | revision-required | superseded
created: "{{ today }}"
updated: "{{ today }}"
---

# {{ adr_id }}: {{ title }}

## Context

**Brief** description of the problem or situation that requires a decision.

## Decision

The decision that was made and key reasoning.

## Consequences

### Positive

- Benefits of this decision

### Negative

- Trade-offs or downsides

### Neutral

- Other impacts to be aware of

## Verification

- Required test suites, monitoring, or audits ensuring compliance.

## References

- [Design artefact link]
- [External research]
