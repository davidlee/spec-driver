---
name: boot
description: Mandatory onboarding. Every agent MUST execute this on startup, or as soon as becoming aware of it.
---

Boot context is pre-generated and loaded into your context automatically
via `.agents/spec-driver-boot.md` (see `spec-driver admin preboot`).

**Validation**: Confirm the boot context is present in your context by
checking for the "Spec-Driver Boot Context" heading. If you cannot find
it, warn the user:

> ⚠ Preboot context not found. Run `uv run spec-driver admin preboot`
> and ensure `.claude/rules/spec-driver-boot.md` symlink exists.

When boot context has been observed — print:
Δ ∴ ⊤

Otherwise — print:
BOOT ERROR !!!

After boot, you MUST use `/using-spec-driver` to route ANY substantive work before acting.
