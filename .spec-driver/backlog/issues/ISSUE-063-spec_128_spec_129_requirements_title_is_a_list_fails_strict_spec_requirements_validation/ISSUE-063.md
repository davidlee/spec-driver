---
id: ISSUE-063
name: "SPEC-128/SPEC-129 requirements[].title is a list, fails strict spec.requirements validation"
created: "2026-05-30"
updated: "2026-05-30"
status: open  # one of: in-progress | open | resolved | triaged
kind: issue  # one of: audit | delta | design_revision | issue | memory | phase | plan | policy | problem | prod | requirement | risk | spec | standard | task | verification
categories: []
severity: p3  # one of: p1 | p2 | p3 | p4
impact: user  # one of: user | systemic | process
---

# SPEC-128/SPEC-129 requirements[].title is a list, fails strict spec.requirements validation

## Symptom

`spec-driver validate workspace` emits 6 errors (3 each for SPEC-128, SPEC-129):

```
spec.requirements: requirements[3].title: must be a string - expected string - got list
spec.requirements: requirements[4].title: must be a string - expected string - got list
spec.requirements: requirements[5].title: must be a string - expected string - got list
```

## Scope

Pre-existing. The spec data predates DE-142 (SPEC-128 last touched 2026-03-14,
`e5c3af46` DE-096); untouched in the working tree. Not in DE-142's applies-to
(PROD-004 / SPEC-114 / SPEC-116). Surfaced as the only residual workspace-validation
errors during DE-142 close-out — logged here so the close was a conscious
disposition, not a silent skip.

## Likely fix

`requirements[3..5].title` in both specs' frontmatter/requirements blocks hold a
YAML list where a scalar string is expected. Inspect both spec sources and
collapse the title to a single string (or correct the malformed block that caused
the parser to read a list).

