util/
  /glossary (learn spec-driver concepts & SOPs)
  /tooling (how to use spec-driver cli, learn schemas, etc)
  /doctrine (hook for loading project doctrine)
  project-context (hook for loading per-project background)

  configure-spec-driver

  specify-prod
  specify-tech
  clarify-spec

  clarify


  create-spec
    spec-elicit (interview user to gather context & write)
    spec-clarify (identify weaknesses; identify & close open questions; research & validate)
  create-revision
    rev-elicit
    rev-clarify *can this be general purpose with arg?
  create-delta
    delta-elicit
    delta-clarify
    design-elicit (DR)
    design-clarify
    delta-plan

assembly spec - to cover:
  decisions
  alternatives
  principles
  guardrails
  verifications
  types / interfaces
  internals
  ownership, allocation / lifecycle
  lateral integration (logging, analytics, etc)
  risks, change / migration considerations
  potential future extensions / modifications


fully incorporate / solve:
  openskills / multi-provider support
  AGENTS.md / BOOT.md / INIT.md / RUN.md consolidation / generation
  obra/superpowers style interviewing loops
  placeholders -> clarification workflows
  process configuration commands -> config files -> inform agent workflows
  skill updates + resilience to user customisation (hooks, etc)
  token-efficient onboarding
  how json-schema vs written markdown frontmatter schema relate operationally
