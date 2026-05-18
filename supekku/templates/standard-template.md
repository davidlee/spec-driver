---
id: "{{ standard_id }}"
name: "{{ name }}"
slug: "{{ slug }}"
kind: standard  # one of: audit | delta | design_revision | issue | memory | phase | plan | policy | problem | prod | requirement | risk | spec | standard | task | verification
status: draft  # one of: default | deprecated | draft | required
created: "{{ today }}"
updated: "{{ today }}"
---

# {{ standard_id }}: {{ title }}

## Statement

Clear, concise statement of the standard or convention.

**Note**: If this standard has status "default", it is recommended unless there's justification to deviate.

## Rationale

Why this standard exists. What benefits does following it provide?

## Scope

Where and when this standard applies. What is included and excluded?

Examples:

- Applies to: All Go code in services/
- Recommended for: New modules (legacy code may deviate)

## Verification

How adoption of this standard is tracked or measured (if applicable).

Examples:

- Linter rules
- Style guide compliance checks
- Code review guidelines
- Usage tracking via backlinks

## References

- [Related policies, ADRs, or specs]
- [External style guides or documentation]
