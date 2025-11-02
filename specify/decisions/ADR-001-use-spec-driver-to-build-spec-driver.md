---
id: ADR-001
title: 'ADR-001: use spec-driver to build spec-driver'
status: accepted
created: '2025-11-01'
updated: '2025-11-01'
reviewed: '2025-11-01'
owners: []
supersedes: []
superseded_by: []
policies: []
specs: []
requirements: []
deltas: []
revisions: []
audits: []
related_decisions: []
related_policies: []
tags: []
summary: ''
---

# ADR-001: use spec-driver to build spec-driver

## Context

In the proud tradition of eating our own dogfood, spec-driver is overdue to drive the implementation of spec-driver itself. 

## Decision

Henceforth, use spec-driver for all development on spec-driver. Include the artefacts in the github repository.

## Consequences

### Positive
- Excellent way to iron out kinks in both the software and the process
- Enjoy and evaluate the benefits of SDD
- Generate documentation, guidance and example usage as a side effect of development
- Empirical experience will guide feature development

### Negative
- Bugs, deficiencies, and unimplemented features may block development effort
- It's far from complete or robust - rough edges will cause some pain
- High cognitive load: building software has an inseperable dependency on design of methodology
- May motivate more investment into spec-driver than the things I wrote it to get done

### Neutral
- Maintenance may motivate a lightweight 'kanban' mode for spec-driver

## Verification
- Self-discipline

## References
- [github](https://github.com/davidlee/spec-driver)
- [website](https://supekku.dev/)
- [pypi](https://pypi.org/project/spec-driver/)