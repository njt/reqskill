---
name: reverse-engineering-requirements
description: >
  Extract structured requirements from existing source code through iterative
  subagent review. Use when: re-implementing an existing system; migrating from
  one tech stack to another; inheriting a codebase with no documentation; user
  says "extract requirements from this code" or "what does this system actually do";
  user has working software but no spec. NOT for greenfield projects — use
  gathering-requirements for those. NOT for maintaining requirements during
  development — use requirements-management for that.
---

# Reverse-Engineering Requirements

## Purpose

Extract what an existing system *actually does* — and what it *should* do in a
reimplementation — by reading source code, iteratively reviewing with fresh-eyes
subagents, and separating genuine requirements from implementation accidents.

This is harder than greenfield elicitation because the code contains everything:
requirements, design decisions, style choices, workarounds, dead code, and
accidental complexity from previous technology constraints. Your job is to
separate signal from noise.

## Role Division

**You do:** Orchestrate the process. Dispatch subagents. Facilitate discussion
between the human and the review findings. Draft and refine the requirements doc.
Identify non-goals.

**The human does:** Provide context about the system's purpose and users. Confirm
or reject your interpretations. Identify which behaviours are intentional vs
accidental. Make priority calls.

**Subagents do:** Read source code with fresh eyes. Compare spec against code.
Find omissions, inaccuracies, and things that don't belong. They bring no prior
assumptions — that's their value.

**You never:** Assume every behaviour in the code is a requirement. Treat
implementation details as requirements. Skip the human's judgment on what matters.

## What Belongs Where

The same filtering from gathering-requirements applies, but with an extra category
that dominates in reverse-engineering work:

**Requirement** = behaviour observable from outside. "Display client name in task list."
**Decision** = how the system achieves it. "Store config at ~/.cu/config.json."
**Style** = formatting/presentation. "Truncate names at 45 characters."
**Non-Goal** = something present in the old system that we explicitly don't want.
"Font size adjustment buttons (unnecessary on web — the old WinForms app couldn't
resize or rescale)."

The litmus test for non-goals: "Is this behaviour in the old code because of a
genuine user need, or because of a constraint that no longer exists?" If the
constraint is gone, the behaviour is a non-goal candidate. Confirm with the human.

### The UI Description Trap

The most common form of spec-leaking-into-requirements when reverse-engineering
GUI applications. UI elements *look* user-observable (the user literally sees
them!) so they pass a naive litmus test. But they're answers to unstated questions:

| What the code has | What it looks like | What the requirement actually is |
|---|---|---|
| Three side-by-side panels | "Display data in three panels" | Operator needs to see unbilled time, invoices, and line detail *simultaneously* to cross-reference them |
| Checkbox selection on rows | "Users select items via checkboxes" | Operator needs hierarchical multi-select (pick a ticket, get all its entries) |
| Right-click context menu | "Context menu with actions X, Y, Z" | Certain actions are available per-entity (per invoice, per ticket) |
| Color-coded rows | "Display rows in PeachPuff/LightGreen/..." | Operator needs to visually triage hundreds of rows at scanning speed |
| Save button on a form | "Batch save with Save button" | Some edits need atomic consistency (description + type together) |

**The fix:** Write capability requirements ("the operator shall be able to...").
The underlying need survives the platform change. The specific UI affordance
doesn't belong in the requirements doc — it anchors the new design toward the
old one, which is exactly what you're trying to avoid.

The one exception: when the UI pattern IS the requirement. High-density data work
with simultaneous cross-referencing across multiple datasets is a genuine constraint —
you can't solve it with a wizard or sequential screens. But "three fixed panels in
a row" is still just one solution to that constraint.

**Subagents will over-describe UI.** Every review iteration, check: "Is this describing
what the user *needs to accomplish*, or how the old app *looked*?" Rewrite the latter
as the former.

### Common Sources of Non-Goals

- **Old platform constraints**: WinForms layout hacks, IE compatibility shims,
  32-bit memory workarounds, single-threaded UI patterns
- **Workarounds for missing features**: Manual caching because the old framework
  had no built-in cache, hand-rolled auth because there was no OAuth library
- **Accumulated cruft**: Features nobody uses but nobody deleted, error messages
  for impossible states, config options that are always set the same way
- **Tech-specific ceremonies**: COM interop boilerplate, XML configuration files
  that a modern stack handles differently, platform-specific file paths

## The Reverse-Engineering Workflow

### Phase 1: Context Dump (1-2 turns)

Get the human to describe what the system does in their own words. Don't read
the code yet. You need their mental model first because:

- They know which parts matter and which are legacy noise
- They know the users and their actual workflows
- They can tell you what they want to *keep* vs what they want to *fix*

Ask:
1. "What does this system do, in your words? Who uses it?"
2. "What's driving the reimplementation? What's wrong with the current version?"
3. "What must absolutely survive the rewrite? What would you love to drop?"

The answer to #3 seeds your Non-Goals section.

### Phase 2: Initial Extraction (subagent)

Dispatch a subagent to read the source code and produce a first-draft
requirements.md. The subagent should:

1. Read the requirements-management skill to understand what requirements mean
   to this project (the Requirement vs Decision vs Style distinction)
2. Read the source code thoroughly
3. Produce a requirements.md following the template structure
4. Flag things it's unsure about — "is this a requirement or an implementation
   detail?" — as open questions

**Subagent prompt pattern:**
> Read `skills/requirements-management/SKILL.md` to understand our requirements
> philosophy — especially the Requirements vs Spec vs Style section and the
> litmus test. Then read [source files]. Produce a `requirements.md` following
> `assets/requirements-template.md`. For each behaviour you find, apply the
> litmus test: "If I changed this, would the user notice a different capability?"
> Record requirements, decisions, and style separately. Things you're unsure
> about go in Open Questions.

Present the draft to the human. Expect significant corrections — the first pass
always over-includes implementation details as requirements.

### Phase 3: Iterative Review Loop (2-3 iterations)

This is the core of the process. Each iteration has three steps:

#### Step 1: Fresh-Eyes Review (subagent)

Dispatch a **new** subagent (fresh context, no prior assumptions) to review
the current requirements.md against the source code. The subagent looks for:

- **Omissions**: Behaviour in the code not captured in requirements
- **Inaccuracies**: Requirements that don't match what the code actually does
- **Non-requirements**: Things in the requirements doc that are actually decisions,
  style, or non-goals (implementation artefacts from the old tech stack)
- **UI descriptions posing as requirements**: "Three panels", "Save button",
  "right-click menu" — these describe the old UI, not the user's need
- **Missing non-goals**: Patterns in the code that look like they'd generate
  requirements but probably shouldn't (platform workarounds, dead features)

**Subagent prompt pattern:**
> Read `skills/requirements-management/SKILL.md` for our requirements philosophy.
> Then read `requirements.md` (our current spec) and [source files].
> With completely fresh eyes, identify:
> 1. Behaviours in the code not captured in requirements (omissions)
> 2. Requirements that contradict what the code does (inaccuracies)
> 3. Items in requirements that fail the litmus test — they're decisions, style,
>    or non-goals, not requirements (misclassifications)
> 4. UI descriptions posing as requirements — "three panels", "Save button",
>    "context menu" describe the old UI, not the user need. Rewrite as capabilities.
> 5. Code patterns that look like requirements but are probably platform
>    workarounds or accumulated cruft (non-goal candidates)
> Report findings grouped by category. Be specific — cite code locations.

#### Step 2: Discussion (human + you)

Review the subagent's findings with the human. For each finding:

- **Omissions**: "The subagent found [behaviour] in the code. Is this a real
  requirement for the new system?" → Add to requirements or non-goals.
- **Inaccuracies**: "The spec says X but the code does Y. Which is correct for
  the new system?" → Fix the requirement.
- **Misclassifications**: "This is in requirements but looks like a decision/
  non-goal. Agree?" → Move it.
- **Non-goal candidates**: "This looks like a [platform] workaround. Do we still
  need it?" → Confirm and add to non-goals, or keep as requirement.

If a finding needs deeper investigation, dispatch a subagent to research it
rather than guessing.

#### Step 3: Update (requirements-editor subagent)

Delegate the agreed changes to the requirements-editor subagent. It handles
the mechanics: ID sequencing, cross-references, validation.

#### Convergence

You're done when a fresh-eyes review comes back with only minor findings —
nothing structural, no missing capabilities, no misclassified items. Two to
three iterations is typical.

### Phase 4: Systems Documentation (1 turn)

If the old system connects to external systems (databases, APIs, file shares),
document the topology in systems.md. The source code is your best source here —
connection strings, API endpoints, credential paths. But confirm with the human
because the new system may connect differently.

### Phase 5: Final Review (1 turn)

Present the complete requirements.md, systems.md, and non-goals to the human.

Check:
- [ ] Every user-facing capability in the old system is either a requirement or a non-goal
- [ ] Non-goals have clear rationale (why we're dropping this)
- [ ] No implementation details leaked into requirements
- [ ] Glossary covers domain terms from the old codebase
- [ ] Open questions don't block `must`-priority work
- [ ] Future Scope captures things the human mentioned wanting "eventually"

## Subagent Management

### Why Fresh Eyes Matter

Each review subagent must start with a clean context. If you reuse a subagent
that already read the requirements, it develops the same blind spots you have.
The value is in the *fresh perspective* — a reader who sees the spec and code
for the first time and notices what you've stopped noticing.

### What Subagents Need

Every review subagent needs:
1. The requirements-management skill (so it knows what "requirement" means to us)
2. The current requirements.md
3. The relevant source code
4. A clear brief: what to look for, how to report findings

### What Subagents Don't Need

- The full conversation history (they'd inherit your blind spots)
- Write access to requirements.md (the requirements-editor handles that)
- Knowledge of previous iterations (fresh eyes means fresh eyes)

## Anti-Patterns

**Don't transcribe the code.** The biggest risk is turning every function into
a requirement. The code has hundreds of behaviours — most are implementation
mechanics, not user-facing capabilities.

**Don't skip the human.** The subagent will flag things it thinks are non-goals,
but only the human knows whether "font size buttons" were a beloved feature or
a workaround. Always confirm.

**Don't reuse review subagents.** Each review needs fresh eyes. A subagent that
reviewed iteration 1 has already formed opinions that compromise iteration 2.

**Don't rush to three iterations.** If iteration 2 still finds major omissions,
do iteration 3 and maybe 4. The number isn't magic — convergence is.

**Don't confuse "the code does X" with "the system needs X."** The code might
handle a scenario that never actually occurs, or handle it in a way that was
a bug nobody noticed. The human's workflow is the ground truth for what matters.

**Don't describe the old UI as requirements.** "Three panels", "Save button",
"right-click context menu" are how the old app looked, not what the user needs.
Ask: what need does this UI element serve? Write that need as the requirement.

## Output Artifacts

1. **requirements.md** — with all sections including Non-Goals
2. **systems.md** — if external systems are involved
3. **A list of remaining open questions** — things that need the human to
   investigate or test against the running system

The requirements.md should be ready for the requirements-management skill to
maintain during development, and for a coding agent to build the new system from.
