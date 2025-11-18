# doc generation

- overview
  - spec-driver generates deterministic docs from code in 3 languages as part
    of it's 'sync' command.
  - currently it supports:
    - go
    - python
    - typescript (or javascript)
  - eventual plans to add support for more languages.
  - the command also stubs out tech specs for any code not covered by existing
    tech specs; it has a --check mode which just reports if any specs would be
    created, and a --prune flag which removes stubs for code which no longer
    exists.
  - the generated docs are stored inside tech specs, under the contracts/ dir
  - generated docs are deterministic, preserve comments, and show function
    signatures, interfaces, etc.

- value proposition
  -

  - to support the value of evergreen tech specs:
    - on-demand and current (no research delay/cost)
    - verifiable (immune to agent oversight / hallucination)
    - providing high level intelligence about
      - system architecture
      - technical design
      - requirements
      - important implementation details
      - collaborators
      - cues to support efficiency of more detailed code inspection
      - function signatures, types & interfaces required to support technical design
      - what's changed since the spec was last updated
    - a highly efficient research reference for both humans and agents, for:
      - high-level investigation
      - orientation before diving into implementation
      - collaborator interfaces / APIs

## guiding principles

- support both agent and human developer ergonomics as equal citizens
- support both legacy and greenfield development
- make it as easy as possible to identify any code changes which the non-autogen parts of a spec might not cover
- support & encourage incremental convergence toward accuracy, completeness & currency
- be unsurprising
- format should be as compact and minimal as possible without compromising legibility
- use existing tools where suitable ones exist (eg gomarkdoc), otherwise build using AST
- any dependencies should be trivially installable
- make it as easy as possible to traverse between code & generated docs
- provide multiple ways to access / traverse the content using e.g. symlink trees (by-language, by-package)
  - the spec bundle remains the single, canonical home for contract files
- ensure good ergonomics for CLI tooling (ripgrep, fzf, bfs, broot, etc)
- aim for consistency between languages, except where that would harm utility or defy expectation
- don't require configuration (if it is allowed) to obtain useful results

## decisions

- must not depend on code being written with specific annotations /
  conventions (JSdoc, etc)
- must preserve comments (package level; function; inline)
- must preserve and represent as much type information as possible
- it must be possible to view docs with or without
  - private / internal interfaces
  - tests
- all code in a project should be included in contracts fur exactly 1 tech
  spec
  - users can create a tech spec representing subsystems or other conceptual
    aggregations, but these are outside the scope of code gen
- manually created tech specs must not be deleted by sync --prune
- manually created tech specs must be able to specify a scope of applicability in structured metadata
  - eg. a list of file globs
- contracts must be deterministic, and should ignore the organisation of functions etc
  - within a file (reordering functions should produce identical documentatio)
  - across files within a spec (except insofar as contracts intentionally map to files as an aid to understanding)
- sync operations must be idempotent
- tech specs must be created as minimal 'stubs' (skip the full template for generated specs)


## Partially Open Questions

- does it make sense to create separate files for (private vs test vs all) contracts?
  - it depends: this generates a lot of clutter when we also want contracts organised by file of source code (code files x 3)
- does it make sense to keep contracts in a subfolder of the spec?
  - yes, if
    - there are no sub-subfolders
    - adding them in the spec bundle root would create too much noise
- TypeScript
  - how best determine spec scope
  - how / whether to represent files in the contract
  - supporting symlink structures
  - file naming

## general challenges

- different languages have very different notions of:
  - what a package or module is, how it is defined, its relationship to files on disk
  - the significance of files & folders to the structure of AST produced
  - types (in function signatures; as standalone entities; optionality; imports)
  - intefaces / protocols
  - function / method privacy & defaults
  - levels of privacy and ability to circumvent

- multiple symlinks under specify/tech/** can make grep confusing
- single filenames which encode path information (s/\/\_/) are confusing and ugly

## specific challeges

- git submodules ??

### typescript

- concept of a module is kinda loose as fuck
- what's a file anyway
- detecting project rooot is nontrivial
  - about 11 package managers
- monorepos
  - ouch
- pnpm workspaces
- mjs (ECMAScript) / commonjs

### python

- typing optionality / brittleness compared to other languages can make contract interfaces unreliable












