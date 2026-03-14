---
id: ISSUE-042
name: 'Short flag -ri breaks: -r consumes i as its regex value'
created: '2026-03-06'
updated: '2026-03-09'
status: resolved
kind: issue
categories: []
severity: p3
impact: user
---

# Short flag -ri breaks: -r consumes i as its regex value

## Reproduction

```
# works — separate flags
spec-driver list specs -r "cli" -i

# works — -i before -r
spec-driver list specs -ir "cli"

# breaks — -r before -i
spec-driver list specs -ri "cli"
# Error: Got unexpected extra argument (cli)
```

## Cause

This is standard POSIX/Typer short-flag parsing. When `-ri` is parsed
left-to-right, `-r` is a value-taking option so it consumes `i` as its
argument. The actual pattern `"cli"` becomes an orphan positional.

## Options

1. **Document only** — already noted in the spec-driver skill tips. This is
   how Typer/Click works and isn't really a bug, just a footgun.
2. **Rename `-i` to a different short flag** — avoids the natural `-ri`
   trap, but `-i` is mnemonic for "case-insensitive".
3. **Make `-i` the default** — if case-insensitive is almost always desired,
   flip the default and offer `--case-sensitive` instead. Then `-r` alone
   does what `-ir` does today.

Option 3 is probably the best UX — case-sensitive regex on artifact names
is rarely what you want.
