---
id: "{{ policy_id }}"
name: "{{ name }}"
slug: "{{ slug }}"
kind: policy  # one of: audit | delta | design_revision | issue | memory | phase | plan | policy | problem | prod | requirement | risk | spec | standard | task | verification
status: draft  # one of: deprecated | draft | required
created: "{{ today }}"
updated: "{{ today }}"
---

# {{ policy_id }}: {{ title }}

## Statement

Clear, concise statement of the policy rule that must be followed.

## Rationale

Why this policy exists. What problem does it solve? What value does it provide?

## Scope

Where and when this policy applies. What is included and excluded?

Examples:

- Applies to: All production code in main codebase
- Excludes: Prototypes, spikes, explicitly marked experimental code

## Verification

How compliance with this policy is verified or enforced.

Examples:

- Pre-commit hooks
- CI/CD checks
- Code review checklist
- Audit procedures

## References

- [Related ADRs, specs, or standards]
- [External documentation or research]
