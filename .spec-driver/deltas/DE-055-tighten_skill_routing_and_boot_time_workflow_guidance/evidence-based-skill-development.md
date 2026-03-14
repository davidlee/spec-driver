# Evidence-Based Skill Development

A guide to designing, testing, and measuring LLM agent skills using empirical methods. Distilled from the design patterns, testing infrastructure, and measurement tools in the [Superpowers](https://github.com/obra/superpowers) project by Jesse Vincent, combined with referenced research on LLM compliance and persuasion.

---

## 1. Core Thesis

**Skills are testable documentation. Treat them like code.**

A skill is not a wish list of behaviors. It is an artifact that changes how an agent acts under pressure. If you can't measure the change, you don't have a skill — you have a comment.

This guide covers three domains:

| Domain          | Question it answers                                               |
| --------------- | ----------------------------------------------------------------- |
| **Design**      | How should a skill be structured so an agent actually follows it? |
| **Testing**     | How do you know the skill works before deploying it?              |
| **Measurement** | How do you quantify the skill's cost and effectiveness?           |

---

## 2. Foundational Principles

### 2.1 The Empirical Stance

Do not assume a skill works because it reads well to you. Agents are not you. They will:

- Follow description metadata instead of reading the skill body
- Rationalize away inconvenient rules under pressure
- Find loopholes you didn't anticipate
- Comply with academic questions but violate under realistic constraints

Every claim about agent behavior must be tested against actual agent behavior. Reading your own skill and nodding is not validation.

### 2.2 Skills Are Not Suggestions

The difference between a skill that works and one that doesn't is usually the difference between a directive and a suggestion.

```markdown
# Suggestion (will be rationalized away)

Consider writing tests first when feasible.

# Directive (resistant to rationalization)

Write code before test? Delete it. Start over. No exceptions.
```

Suggestions invite judgment calls. Under pressure, agents resolve judgment calls in favor of speed. Directives remove the judgment call entirely.

### 2.3 The Description Trap

**Discovery metadata and skill content serve different purposes. Conflating them causes failures.**

When a skill's YAML description summarizes its workflow, agents may follow the description as a shortcut and skip reading the full skill. This was discovered empirically: a description saying "code review between tasks" caused an agent to perform one review, when the skill body specified two (spec compliance, then code quality). Changing the description to only specify _triggering conditions_ — "Use when executing implementation plans with independent tasks" — fixed the problem.

**Rule:** Descriptions answer "should I load this skill right now?" and nothing else. Never summarize process, workflow, or steps in a description.

```yaml
# Will cause agents to follow the description, not the skill
description: Use for TDD - write test first, watch it fail, write minimal code, refactor

# Will cause agents to load and read the skill
description: Use when implementing any feature or bugfix, before writing implementation code
```

### 2.4 Token Budget as Design Constraint

Every token in a skill competes with conversation history, other skills, and the user's actual request for context window space. Conciseness is not a style preference — it is a resource allocation problem.

| Skill frequency                       | Target      |
| ------------------------------------- | ----------- |
| Always-loaded (getting-started, meta) | < 150 words |
| Frequently-triggered                  | < 200 words |
| Situational                           | < 500 words |

Exceeding these budgets is permitted when the skill is discipline-enforcing and must be thorough to resist rationalization. But every paragraph must justify its token cost against the question: "Does this change agent behavior, or does it just make me feel more thorough?"

---

## 3. Skill Taxonomy

Not all skills work the same way. The skill's type determines its structure, its tone, and how it should be tested.

### 3.1 Discipline Skills

**Purpose:** Enforce a practice the agent will be tempted to skip.
**Examples:** TDD, systematic debugging, verification-before-completion.

**Structural signature:**

- An "Iron Law" — a non-negotiable rule in a code block
- A rationalization table mapping specific excuses to counters
- A red flags list for self-diagnosis
- Explicit negation sections ("Don't keep as reference", "Don't adapt while testing")
- Authority language throughout ("YOU MUST", "No exceptions", "Never")
- A foundational principle closing meta-loopholes: "Violating the letter of the rules is violating the spirit of the rules"

**Why they need this structure:** Agents are sophisticated reasoners. Under pressure (time, sunk cost, exhaustion), they will construct plausible arguments for why _this specific case_ is an exception. Every rationalization you don't pre-empt is a loophole the agent will find.

**Testing approach:** Pressure scenarios with 3+ combined pressures. Academic questions are insufficient — agents recite rules perfectly when not pressured to break them.

### 3.2 Technique Skills

**Purpose:** Teach a reusable method the agent doesn't already know.
**Examples:** Root cause tracing, condition-based waiting, defense-in-depth.

**Structural signature:**

- Core pattern with before/after comparison
- "When to use" focused on symptoms to detect, not rules to follow
- One excellent example (real, not synthetic; one language, not five)
- Quick reference table for common applications
- "Common mistakes" section

**Testing approach:** Application scenarios. Give the agent a problem that requires the technique and verify it applies the technique correctly. Variation and edge-case scenarios test completeness.

### 3.3 Process Skills

**Purpose:** Define a multi-step workflow with decision points.
**Examples:** Brainstorming, plan execution, subagent-driven development.

**Structural signature:**

- A flowchart (Graphviz DOT) showing the full process, including loops and backtracking
- Decision diamonds at non-obvious branch points
- Clear terminal states
- Integration section showing how this skill connects to others

**Why flowcharts matter here:** Process skills are where agents most commonly stop too early or skip steps. A flowchart makes the loop structure explicit. Prose instructions like "review, then fix, then review again" get compressed to "review and fix." A flowchart with an arrow from "reviewer finds issues" back to "implementer fixes" makes the loop unambiguous.

**Testing approach:** End-to-end execution with transcript analysis. Verify that all process steps occurred and in the correct order.

### 3.4 Reference Skills

**Purpose:** Provide information the agent needs but doesn't have.
**Examples:** API documentation, library guides, command references.

**Structural signature:**

- Lookup-optimized structure (tables, headers, code blocks)
- Minimal prose
- No enforcement language
- Links to `--help` or external docs for exhaustive detail

**Testing approach:** Retrieval scenarios. Can the agent find the right information and apply it correctly?

---

## 4. Anatomy of a Skill File

### 4.1 Frontmatter

```yaml
---
name: skill-name-with-hyphens
description: Use when [specific triggering conditions and symptoms]
---
```

- `name`: Letters, numbers, hyphens only. Verb-first, active voice. "condition-based-waiting" not "async-test-helpers."
- `description`: Third person. Starts with "Use when...". Describes the _problem context_, not the skill's workflow. Technology-agnostic unless the skill is technology-specific. Under 500 characters.

**Keyword coverage in the description matters for discoverability.** Use words the agent would search for: error messages, symptoms ("flaky", "hanging", "race condition"), tool names, and synonyms.

### 4.2 Section Order

Skills across the Superpowers repo follow a consistent ordering convention, differentiated by type:

```
# Title
## Overview              — What is this? Core principle in 1-2 sentences.
## When to Use           — Triggering conditions. Flowchart if decision is non-obvious.
## [Core Content]        — Varies by type (see below).
## Common Mistakes       — Mistake + fix pairs.
## Red Flags             — (Discipline skills only) Self-diagnosis checklist.
## Quick Reference       — Scannable table.
## Integration           — Cross-references to related skills.
```

**Core content by type:**

| Type       | Core section name | Contains                                                   |
| ---------- | ----------------- | ---------------------------------------------------------- |
| Discipline | "The Iron Law"    | Non-negotiable rule, rationalization table, negation lists |
| Technique  | "Core Pattern"    | Before/after comparison, implementation example            |
| Process    | "The Process"     | Flowchart, step descriptions, example workflow             |
| Reference  | "Quick Reference" | Tables, code blocks, lookup structure                      |

### 4.3 Cross-Referencing

Skills reference each other by name with explicit requirement markers:

```markdown
# Clear requirement hierarchy

**REQUIRED SUB-SKILL:** Use superpowers:test-driven-development
**REQUIRED BACKGROUND:** You MUST understand superpowers:systematic-debugging

# Not this — unclear whether it's optional or mandatory

See skills/testing/test-driven-development
```

**Never force-load referenced files** (e.g., with `@` syntax) in the main skill body. Force-loading burns context tokens on content the agent may not need yet. Reference by name; the agent loads when needed.

### 4.4 Supporting Files

Move content to separate files when:

| Condition                             | Example                                |
| ------------------------------------- | -------------------------------------- |
| Reference material exceeds ~100 lines | API docs, syntax guides                |
| Content is a reusable tool            | Scripts, prompt templates, helper code |
| Content is deep-dive background       | Research foundations, worked examples  |

Keep inline: principles, short code patterns (< 50 lines), everything else.

Supporting files are referenced but not force-loaded. They exist to keep the main SKILL.md within token budget while preserving access to detailed content.

---

## 5. Testing Methodology: TDD for Skills

### 5.1 The Cycle

The same RED-GREEN-REFACTOR cycle used for code, applied to documentation:

| Phase        | Action                                           | Success criteria                             |
| ------------ | ------------------------------------------------ | -------------------------------------------- |
| **RED**      | Run scenario WITHOUT skill                       | Agent fails; document exact rationalizations |
| **GREEN**    | Write minimal skill addressing observed failures | Agent now complies                           |
| **REFACTOR** | Find new rationalizations, add explicit counters | Agent complies under maximum pressure        |

**The iron law of skill testing:** If you didn't watch an agent fail without the skill, you don't know what the skill needs to prevent.

### 5.2 Pressure Scenarios

Academic questions ("What does the skill say about X?") are inadequate. Agents recite rules perfectly in academic contexts and violate them under pressure.

**Effective pressure scenarios:**

- Combine 3+ pressure types
- Force an explicit A/B/C choice (not open-ended)
- Use concrete constraints (specific times, file paths, consequences)
- Frame as real work, not a quiz ("Choose and act", not "What should you do?")
- Eliminate easy outs ("I'd ask the user" without choosing is not valid)

**Pressure types:**

| Type       | Example                                                |
| ---------- | ------------------------------------------------------ |
| Time       | Emergency, deploy window closing, dinner in 30 minutes |
| Sunk cost  | "You spent 4 hours on this implementation"             |
| Authority  | Senior engineer says skip it, manager overrides        |
| Exhaustion | End of day, already tired                              |
| Social     | Looking dogmatic, seeming inflexible to the team       |
| Pragmatic  | "Being pragmatic means adapting the process"           |

**Example pressure scenario:**

```
IMPORTANT: This is a real scenario. Choose and act.

You spent 4 hours implementing a feature. It's working perfectly.
You manually tested all edge cases. It's 6pm, dinner at 6:30pm.
Code review tomorrow at 9am. You just realized you didn't write tests.

Options:
A) Delete code, start over with TDD tomorrow
B) Commit now, write tests tomorrow
C) Write tests now (30 min delay)

Choose A, B, or C.
```

### 5.3 Capturing Rationalizations

When an agent violates a skill under pressure, document the exact rationalization verbatim. These become your refactoring targets:

- "Tests after achieve the same goals"
- "I'm following the spirit, not the letter"
- "This case is different because..."
- "Keep as reference while writing tests first"
- "Being pragmatic, not dogmatic"

Each rationalization becomes:

1. An explicit negation in the skill rules
2. An entry in the rationalization table
3. A red flag entry
4. A symptom in the description (for discoverability)

### 5.4 Meta-Testing

When an agent violates the skill despite having it, ask:

```
You read the skill and chose Option C anyway.
How could that skill have been written differently to make
it crystal clear that Option A was the only acceptable answer?
```

Three diagnostic outcomes:

| Response                                    | Diagnosis            | Fix                                 |
| ------------------------------------------- | -------------------- | ----------------------------------- |
| "The skill WAS clear, I chose to ignore it" | Enforcement problem  | Add stronger foundational principle |
| "The skill should have said X"              | Documentation gap    | Add the agent's suggestion          |
| "I didn't see section Y"                    | Organization problem | Make key content more prominent     |

### 5.5 Automated Testing Infrastructure

Beyond pressure-testing individual agents, test the full skill lifecycle with automated harnesses.

**Skill triggering tests:** Feed a natural-language prompt to the agent (without mentioning the skill by name) and verify the correct skill was auto-discovered and invoked.

```bash
# Feed a naive prompt, check if the right skill fires
claude -p "$PROMPT" \
    --plugin-dir "$PLUGIN_DIR" \
    --dangerously-skip-permissions \
    --max-turns 3 \
    --output-format stream-json \
    > "$LOG_FILE"

# Check for skill invocation in the transcript
grep -q '"name":"Skill"' "$LOG_FILE" && \
grep -qE '"skill":"([^"]*:)?'"${SKILL_NAME}"'"' "$LOG_FILE"
```

**Premature action detection:** When a user explicitly names a skill, verify the agent loads it _before_ taking action. Parse the session transcript for tool invocations that precede the Skill tool call — these indicate the agent started working without the skill's guidance.

**End-to-end workflow tests:** For process skills, run the complete workflow in headless mode, then parse the JSONL session transcript to verify:

- All process steps occurred
- Steps occurred in the correct order
- Subagents were dispatched as expected
- Artifacts were created (files, commits, tests)
- Tests pass

---

## 6. Measurement

### 6.1 What to Measure

| Metric                           | Why it matters                                               |
| -------------------------------- | ------------------------------------------------------------ |
| Token usage per skill invocation | Direct cost; identifies bloated prompts                      |
| Token usage per subagent         | Reveals whether subagents get too much or too little context |
| Cache hit rate                   | High cache reads = efficient prompt reuse                    |
| Message count                    | Proxy for conversation complexity                            |
| Estimated dollar cost            | Makes optimization decisions concrete                        |
| Skill triggering accuracy        | Does the right skill fire for the right prompt?              |
| Premature action rate            | Does the agent act before loading the skill?                 |

### 6.2 Session Transcript Analysis

Claude Code writes JSONL session transcripts. Each line is a JSON object representing a message or tool result. These are your primary measurement artifact.

**Key structures in the transcript:**

Assistant messages contain token usage:

```json
{
  "type": "assistant",
  "message": {
    "content": [...],
    "usage": {
      "input_tokens": 27,
      "output_tokens": 3996,
      "cache_creation_input_tokens": 132742,
      "cache_read_input_tokens": 1213703
    }
  }
}
```

Subagent results contain per-agent usage:

```json
{
  "type": "user",
  "toolUseResult": {
    "agentId": "3380c209",
    "usage": {
      "input_tokens": 2,
      "output_tokens": 787,
      "cache_read_input_tokens": 24989
    },
    "prompt": "You are implementing Task 1..."
  }
}
```

### 6.3 Cost Estimation

A basic cost model for analysis:

```python
def calculate_cost(usage, input_cost_per_m=3.0, output_cost_per_m=15.0):
    total_input = (usage['input_tokens']
                   + usage['cache_creation']
                   + usage['cache_read'])
    input_cost = total_input * input_cost_per_m / 1_000_000
    output_cost = usage['output_tokens'] * output_cost_per_m / 1_000_000
    return input_cost + output_cost
```

Adjust rates for your model and tier. The value is in _relative_ comparison between skill versions, not absolute accuracy.

### 6.4 What the Numbers Tell You

| Observation                       | Interpretation                                     |
| --------------------------------- | -------------------------------------------------- |
| High cache reads on main session  | Prompt caching working; good                       |
| Similar cost per subagent         | Tasks well-decomposed; consistent complexity       |
| One subagent much more expensive  | Task too large, or subagent doing unnecessary work |
| Very low input tokens             | Context being provided efficiently                 |
| High output tokens on coordinator | Coordinator doing too much work itself             |
| Typical cost per subagent task    | $0.05-$0.15 depending on complexity                |

### 6.5 Using Measurement to Iterate

Measurement closes the feedback loop:

1. **Baseline:** Run a workflow without the skill. Record cost and outcome.
2. **With skill v1:** Run the same workflow with the skill. Record cost and outcome.
3. **Compare:** Did quality improve? At what token cost? Is the cost justified?
4. **Optimize:** If a subagent is expensive, check whether the skill is injecting unnecessary context. If a step is cheap but failing, the skill may not be providing enough.

This is the same empirical stance applied to economics: measure, don't guess.

---

## 7. Persuasion Engineering

LLMs respond to the same persuasion principles as humans. Research by Meincke et al. (2025), testing 7 principles across N=28,000 LLM conversations, found that persuasion techniques more than doubled compliance rates (33% to 72%).

This is not about manipulation. It is about ensuring that critical practices survive contact with pressure.

### 7.1 Effective Principles for Skill Design

**Authority** — Imperative language eliminates decision fatigue.

```markdown
# Weak: agent will negotiate

Consider writing tests before implementation.

# Strong: agent will comply

NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Use for: discipline skills, safety practices, established standards.

**Commitment** — Force explicit declarations that create consistency pressure.

```markdown
When you find a skill, you MUST announce: "I'm using [Skill Name]"
```

Use for: multi-step processes, accountability mechanisms.

**Scarcity** — Time-bound requirements prevent "I'll do it later."

```markdown
After completing a task, IMMEDIATELY request code review before proceeding.
```

Use for: verification requirements, sequential dependencies.

**Social proof** — Universal patterns establish norms.

```markdown
Checklists without tracking = steps get skipped. Every time.
```

Use for: documenting universal practices, warning about common failures.

### 7.2 Principles to Avoid

**Liking** — Creates sycophancy. Conflicts with honest feedback. Never use for discipline enforcement.

**Reciprocity** — Rarely effective in skill contexts. Other principles work better.

### 7.3 Combinations by Skill Type

| Skill type    | Use                                   | Avoid               |
| ------------- | ------------------------------------- | ------------------- |
| Discipline    | Authority + Commitment + Social Proof | Liking, Reciprocity |
| Technique     | Moderate Authority + Unity            | Heavy authority     |
| Collaborative | Unity + Commitment                    | Authority, Liking   |
| Reference     | Clarity only                          | All persuasion      |

### 7.4 Why It Works

LLMs are trained on human text. Authority language precedes compliance in training data. Commitment sequences (statement then action) are frequently modeled. Bright-line rules ("YOU MUST") reduce rationalization by removing decision points. Implementation intentions ("When X, do Y") create automatic behavior patterns.

The ethical test: Would this technique serve the user's genuine interests if they fully understood it?

---

## 8. Design Patterns Worth Stealing

### 8.1 The Iron Law Pattern

A single non-negotiable rule, set apart in a code block, that anchors the entire skill:

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

This works because it is:

- Short enough to remember
- Absolute (no "when feasible" qualifier)
- Testable (you either investigated or you didn't)
- Early in the skill (agents read top-down, may not finish)

### 8.2 The Rationalization Table

A two-column table mapping specific excuses to specific counters:

```markdown
| Excuse               | Reality                                    |
| -------------------- | ------------------------------------------ |
| "Too simple to test" | Simple code breaks. Test takes 30 seconds. |
| "I'll test after"    | Tests passing immediately prove nothing.   |
```

This works because agents pattern-match against their own reasoning. When they generate a rationalization and then encounter it in a table labeled "excuses," the self-awareness disrupts the rationalization.

### 8.3 The Red Flags List

A bulleted list of thoughts that indicate the agent is about to violate the skill:

```markdown
## Red Flags - STOP and Start Over

- Code before test
- "I already manually tested it"
- "This is different because..."

**All of these mean: Delete code. Start over with TDD.**
```

This is a self-diagnosis tool. The agent recognizes its own reasoning in the list and triggers the corrective action.

### 8.4 Flowcharts for Loops

Process skills use Graphviz DOT flowcharts specifically at points where the agent might stop prematurely or skip a loop iteration:

```dot
"Reviewer finds issues?" -> "Implementer fixes" [label="yes"];
"Implementer fixes" -> "Reviewer reviews again" [label="re-review"];
"Reviewer reviews again" -> "Reviewer finds issues?";
```

The visual loop is harder to skip than prose saying "review again if needed." The arrow makes the backtracking explicit and non-optional.

### 8.5 Two-Stage Separation

The subagent-driven-development skill separates review into two stages: spec compliance first, code quality second. This prevents a common failure mode where over-engineering gets praised in quality review despite not matching the spec.

The general pattern: when you need two different evaluative lenses applied to the same artifact, use separate review passes with separate prompts. Combining them causes one lens to dominate.

### 8.6 Description as Pure Trigger

Every skill description in the repo follows the same pattern: "Use when [situation]." None describe what the skill does or how it works. This is deliberate — it forces the agent to load and read the skill rather than acting on a summary.

The portable lesson: metadata that describes _what a tool does_ competes with the tool itself. Metadata should only describe _when to reach for the tool_.

### 8.7 Separate Prompts for Separate Roles

The subagent-driven-development skill uses three distinct prompt templates: implementer, spec reviewer, code quality reviewer. Each is a separate file with role-specific framing and instructions.

The pattern: when delegating to subagents, don't reuse prompts across roles. Each role has different incentives, different failure modes, and different success criteria. Prompt separation makes these explicit and independently tunable.

---

## 9. Anti-Patterns

### 9.1 Narrative Skills

```markdown
# Don't

"In session 2025-10-03, we discovered that empty projectDir caused..."
```

Skills are reference guides, not journal entries. Narrative is too specific to reuse and too long to scan.

### 9.2 Multi-Language Dilution

Providing the same example in JavaScript, Python, Go, and Rust produces four mediocre examples instead of one excellent one. Agents are competent at language porting. One real, complete, well-commented example in the most relevant language is sufficient.

### 9.3 Workflow Summaries in Descriptions

Covered in section 2.3. The most consequential anti-pattern in the repo's history. Agents treat description metadata as a shortcut and skip the full skill.

### 9.4 Force-Loading Referenced Content

Using syntax that auto-injects referenced files (like `@filepath`) in the main skill body burns context tokens on content the agent may never need. Reference by name; let the agent load on demand.

### 9.5 Untested "Obvious" Skills

The most common rationalization for skipping skill testing: "This skill is obviously clear." Clear to you is not clear to the agent. The Superpowers repo documents multiple cases where "obvious" skills failed under pressure in ways the author did not anticipate.

### 9.6 Suggestions Disguised as Rules

```markdown
# Looks like a rule, functions as a suggestion

You should generally write tests before implementation when possible.
```

"Generally," "when possible," "should" — these are escape hatches. Under pressure, the agent will judge that this specific case is one of the exceptions. If it's a rule, make it absolute. If it's genuinely optional, don't frame it as a rule.

---

## 10. Checklist: Skill Development Lifecycle

### RED Phase (Baseline)

- [ ] Created pressure scenarios (3+ combined pressures for discipline skills)
- [ ] Ran scenarios WITHOUT skill
- [ ] Documented agent failures and rationalizations verbatim
- [ ] Identified patterns in failures

### GREEN Phase (Write)

- [ ] Name: letters, numbers, hyphens only; verb-first
- [ ] Frontmatter: `name` and `description` only; < 1024 chars total
- [ ] Description: "Use when..." triggering conditions only; no workflow summary
- [ ] Addresses specific baseline failures observed in RED
- [ ] Within token budget for skill type
- [ ] Ran scenarios WITH skill — agent now complies

### REFACTOR Phase (Harden)

- [ ] Identified new rationalizations from testing
- [ ] Added explicit counters for each (discipline skills)
- [ ] Built rationalization table
- [ ] Created red flags list
- [ ] Updated description with violation symptoms
- [ ] Re-tested — agent still complies under maximum pressure
- [ ] Meta-tested — agent confirms skill was clear

### Measurement

- [ ] Ran end-to-end workflow with skill
- [ ] Analyzed session transcript for token usage
- [ ] Verified skill triggering accuracy (auto-discovery from naive prompts)
- [ ] Checked for premature action (agent loads skill before acting)
- [ ] Cost is justified relative to quality improvement

---

## References

- **Cialdini, R. B. (2021).** _Influence: The Psychology of Persuasion (New and Expanded)._ Harper Business.
- **Meincke, L., Shapiro, D., Duckworth, A. L., Mollick, E., Mollick, L., & Cialdini, R. (2025).** Call Me A Jerk: Persuading AI to Comply with Objectionable Requests. University of Pennsylvania. N=28,000 LLM conversations. Compliance 33% to 72% with persuasion techniques.
- **Superpowers** (obra/superpowers). Source repository for the patterns and test infrastructure analyzed in this document.
- **Anthropic.** Skill authoring best practices. Claude platform documentation.
