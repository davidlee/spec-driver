<skills_system priority="1">

## Available Skills

<usage>
When users ask you to perform tasks, check if any of the available skills below can help complete the task more effectively. Skills provide specialized capabilities and domain knowledge.

How to use skills:
- Check available skills in <available_skills> below
- Skills are loaded via slash commands or agent tooling
- Each skill contains detailed instructions for completing specific tasks

Usage notes:
- Only use skills listed in <available_skills> below
- Do not invoke a skill that is already loaded in your context
- Each skill invocation is stateless
</usage>

<available_skills>

<skill>
<name>audit-change</name>
<description>Canonical reconciliation runsheet for AUD artefacts. Create or update the audit, disposition every finding, reconcile specs/contracts, and hand off to closure only when audit state supports it.</description>
<location>project</location>
</skill>

<skill>
<name>boot</name>
<description>Mandatory onboarding. Every agent MUST execute this on startup, or as soon as becoming aware of it.</description>
<location>project</location>
</skill>

<skill>
<name>capturing-memory</name>
<description>Invoke this skill whenever any of the following occurs during work: (1) you discover or confirm a durable fact, constraint, invariant, or “how we do X here” pattern; (2) you create a new workflow/checklist that will be reused; (3) you resolve a recurring confusion (“where is the source of truth?”); (4) you make a decision that is not an ADR/SPEC but would prevent rework; (5) you detect a sharp edge, footgun, or non-obvious dependency that future agents will hit. Do NOT rely on conversational context to persist. When the information would save ≥10 minutes for a future agent, write a memory record immediately.</description>
<location>project</location>
</skill>

<skill>
<name>close-change</name>
<description>Close a delta safely - satisfy coverage gates, complete the delta command, and verify owning-record lifecycle updates.</description>
<location>project</location>
</skill>

<skill>
<name>consult</name>
<description>Identify and address obstacles, significant decisions, or emergent complexity. You MUST use this skill if you encounter unanticipated obstacles during implementation.</description>
<location>project</location>
</skill>

<skill>
<name>continuation</name>
<description>Write a prompt to help the next agent continue effectively.</description>
<location>project</location>
</skill>

<skill>
<name>doctrine</name>
<description>Understand project governance to avoid spreading heresy. you</description>
<location>project</location>
</skill>

<skill>
<name>draft-design-revision</name>
<description>Draft or refine a design revision (DR) for a delta. Use it when a DR needs concrete design shaping, explicit question triage, and section-by-section validation before implementation planning.</description>
<location>project</location>
</skill>

<skill>
<name>execute-phase</name>
<description>Mandatory execution skill for any delta/IP implementation phase. Use it before code changes, move the owning delta to in-progress, keep notes current, reconcile structured execution docs, and surface blockers early.</description>
<location>project</location>
</skill>

<skill>
<name>implement</name>
<description>implement a well-defined task or implementation plan</description>
<location>project</location>
</skill>

<skill>
<name>maintaining-memory</name>
<description>Invoke this skill whenever you observe memory drift or when your actions would invalidate existing memories. Mandatory triggers: (1) you change a workflow/command, move files, rename modules, or change invariants; (2) you discover a memory is wrong, missing provenance, or stale; (3) you see a memory record guiding behaviour that is no longer true; (4) you find duplicates or near-duplicates; (5) you are about to add a new memory that overlaps an existing one. Core rule: if you change reality, you must change memory in the same change-set (or immediately after) so future agents do not inherit incorrect guidance.</description>
<location>project</location>
</skill>

<skill>
<name>next</name>
<description>Print a concise continuation prompt for the next agent. Use this when everything is written down and in order for the next agent, and the user has indicated they wish to continue with fresh context.</description>
<location>project</location>
</skill>

<skill>
<name>notes</name>
<description>Whenever you complete a task or phase - record implementation notes.</description>
<location>project</location>
</skill>

<skill>
<name>plan-phases</name>
<description>Plan execution for a delta - refine IP objectives/gates and create the next phase sheet with concrete tasks and verification expectations.</description>
<location>project</location>
</skill>

<skill>
<name>preflight</name>
<description>Use after routing has already happened, when the next step is bounded up-front research to understand a substantive task, surface unknowns and tensions, and assess readiness without drifting into implementation or open-ended exploration.</description>
<location>project</location>
</skill>

<skill>
<name>retrieving-memory</name>
<description>Invoke this skill before making non-trivial assumptions in a large codebase. Mandatory triggers: (1) you are about to modify a subsystem you have not touched in this run; (2) you are about to run, change, or suggest a command pipeline (tests, builds, releases, migrations); (3) you see conflicting cues in code/docs; (4) you are asked “what is the right way here?”; (5) you are debugging a recurring failure mode; (6) you are about to answer with “probably/usually/likely”. Default rule: if you cannot cite a source-of-truth file/doc/ADR/SPEC from the repo, you must consult memories first and then proceed.</description>
<location>project</location>
</skill>

<skill>
<name>reviewing-memory</name>
<description>Invoke this skill as a deliberate review pass whenever stability matters: (1) before a release/migration/large refactor; (2) at the start of work in an unfamiliar subsystem; (3) when you see repeated agent confusion; (4) when thread-type working sets accumulate; (5) when you suspect stale guidance is causing defects. This is not ad-hoc maintenance; it is a structured audit to prevent systemic drift.</description>
<location>project</location>
</skill>

<skill>
<name>scope-delta</name>
<description>Scope intentional change as a delta. Define applies-to specs/requirements, risks, and closure targets before implementation.</description>
<location>project</location>
</skill>

<skill>
<name>shape-revision</name>
<description>Shape a spec revision when requirements/responsibilities move. Use this before delta scoping when policy/doctrine requires revision-first flow, or when audit reconciliation shows authority must move.</description>
<location>project</location>
</skill>

<skill>
<name>spec-driver</name>
<description>Use this skill any time work involves creating, listing, finding, showing, editing, completing, syncing, or otherwise interacting with spec-driver entities via the CLI. Trigger it whenever a user asks to create or inspect ADRs, specs, deltas, revisions, audits, memories, policies, standards, backlog items, or related workflow artefacts, especially if there is any temptation to guess IDs, paths, or command shapes.</description>
<location>project</location>
</skill>

<skill>
<name>update-delta-docs</name>
<description>Reconcile DE/IP/phase/DR execution artefacts during delta work. Use this when implementation changes structured execution state, not just notes.</description>
<location>project</location>
</skill>

<skill>
<name>using-spec-driver</name>
<description>Mandatory routing skill for ANY substantive work in a spec-driver project. Choose the governing skill before acting, and do not start implementation until the required delta/design/plan/phase artefacts exist.</description>
<location>project</location>
</skill>

</available_skills>

</skills_system>
