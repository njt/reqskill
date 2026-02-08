---
name: requirements-management
description: >
  Skill for creating, maintaining, and working with structured project requirements documents.
  Use when: creating a new project and need to capture requirements; starting a coding session
  and need to load/understand existing requirements; a requirement needs to be added, changed,
  or resolved; an open question needs to be raised or answered; a design decision has been made
  and should be recorded; reviewing requirements for completeness or consistency. Triggers include
  mentions of "requirements", "requirements.md", "req", or when beginning work on a project that
  has a requirements.md file.
---

# Requirements Management

## Purpose

A requirements document is the durable source of truth for what a project must do, what
constrains it, and what decisions have been made. It exists so that any LLM session can
re-ground itself on project intent without relying on chat history.

## File Format

Requirements live in `requirements.md` (or `requirements.yaml`) in the project root,
version-controlled alongside code. The file is plain text that humans can edit directly —
the LLM is a convenience layer, not a gatekeeper.

## Document Structure

Sections in order:

1. **Project header** — name and one-line summary
2. **Problem Statement** — what, who, why (2-3 paragraphs max)
3. **Actors** — table of actor IDs, descriptions, and goals
4. **Glossary** — canonical terms with aliases; domain quirks and exceptions
5. **Functional Requirements** — each with ID, status, priority, description, rationale, acceptance criteria
6. **Constraints** — technical, business, or operational limits on the solution space
7. **Non-functional Requirements** — performance, security, reliability with measurable criteria
8. **Future Scope** — anticipated work explicitly not in current scope but worth recording
9. **Non-Goals** — behaviours explicitly rejected, especially from prior implementations
10. **Decisions** — append-only log of design/architecture choices
10. **Open Questions** — things we know we don't know

## Key Principles

### IDs Are Stable
Requirement IDs (FR-01, C-01, NF-01, D-01, Q-01) never change once assigned. Reference them
in code comments, commit messages, and conversations. Increment to the next available number
for new items.

### Status Flow
Requirements move through: `draft` → `in-flux` → `settled`. Only `settled` requirements
should be treated as ground truth during implementation. `draft` and `in-flux` items should
be flagged for discussion.

### Priority Levels
`must` = system is broken without this. `should` = significant value, strong expectation.
`could` = nice to have, implement if cheap.

### Decisions Are Append-Only
Never delete or overwrite a decision. If a decision is reversed, add a new decision that
supersedes it and reference the original. Decisions record **Owner** to indicate authority:
a human's name, "LLM", or "client:Name". LLM decisions may be revisited freely; human and
client decisions should be treated as given unless explicitly reopened.

### Glossary Prevents Misinterpretation
Always use the canonical term from the glossary in requirements text. When encountering an
alias in conversation or code, map it to the canonical term. Domain quirks capture the
"actually means" and "except when" cases — these are high-value for preventing bugs.

### Non-Goals Prevent Recurring False Positives
When re-implementing existing systems, certain behaviours look like requirements but are
actually artefacts of old platform constraints, workarounds, or accumulated cruft. Recording
these as Non-Goals prevents every fresh reviewer (human or LLM) from rediscovering and
re-proposing them. Each non-goal needs a brief rationale explaining why it's rejected.

### Open Questions Are a First-Class Concept
When uncertainty is discovered, add an open question rather than making an assumption.
Questions are resolved by converting them into requirements, constraints, or decisions.
Never silently resolve a question — record the resolution.

## Requirements vs Spec vs Style

The most common failure mode in requirements extraction is spec leaking into requirements.
Three things get conflated:

**Requirements** describe behaviour observable from outside the system. "The task list
must display custom ID, client name, and status" is a requirement — it says what
information the user needs. A requirement answers "what does the system do?" or "what
does the user see/get?"

**Design decisions** describe *how* the system achieves requirements. "Config stored at
`~/.cu/config.json`", "use Cobra framework", "detect custom IDs via regex `[A-Z]+-\d+`"
are decisions. They narrow the solution space but could be changed without changing what
the user experiences. Record these in the Decisions section with rationale and Owner.

**Style/presentation** describes formatting, layout, and cosmetic choices. Column widths,
truncation characters ("..." vs "..."), exact timestamp formats ("5h ago" vs "5 hours ago"),
credential masking rules (first 10 + last 4 chars). These belong in a style guide or
code conventions, not in requirements.md.

### The Litmus Test

Ask: "If I changed this, would the user notice a different *capability*?"

- "Display priority in task lists" → Yes, new information surfaced → **Requirement**
- "Store config in ~/.cu/ instead of ~/.config/cu/" → No, same capability, different path → **Decision**
- "Truncate names at 45 characters" → No, same information, different presentation → **Style**
- "Support JSON output for agent consumption" → Yes, new capability → **Requirement**
- "Use comma-separated values for multi-select input" → No, same capability, different syntax → **Decision**

### What About Interface Contracts?

For CLI tools and APIs, the command/endpoint structure is a requirement when external
consumers depend on it. `cu <resource> <verb>` is an interface contract — scripts and
agents write against it. Flag names (`--active` vs `--open`) are design decisions.
Response field selection ("which fields appear in summary output") is a requirement
when it reflects what information users need; column order and formatting are style.

For internal interfaces (function signatures, module boundaries), these are design
decisions, not requirements.

### Extracting Requirements from Existing Code

When building requirements.md from existing code, implementation details will dominate
what you find. Resist the urge to transcribe the code into requirements. Instead:

1. For each function/endpoint/command, ask: "What user need does this serve?"
2. Record the *need*, not the implementation
3. Where the code makes an explicit choice between alternatives, record a Decision
4. Where the code has hardcoded formatting/layout, note it as style — don't promote to FR
5. Where the code describes UI elements (panels, buttons, menus, dialogs), ask what
   need the element serves. "Three panels" is not a requirement — "operator needs to
   see three related datasets simultaneously" is

### Sub-Requirements

Prefer flat atomic requirements (FR-01, FR-02, FR-03) over nested sub-requirements
(FR-01.1, FR-01.2, FR-01.3). Nesting creates ambiguity: is FR-01 settled because all
sub-items are? What if FR-01.3 changes status? Each testable behaviour gets its own ID.

If a group of requirements are related, use a short title on each and let the IDs be
sequential — the reader can see they're related without nesting.

## What Goes in systems.md

systems.md documents **external system topology** — what exists, where it lives, how to
reach it. It is NOT an API reference, integration guide, or implementation spec.

**Include:**
- System name, what it is, what this project needs from it
- Server/hostname (especially when non-obvious)
- Access method (REST API / SQL / file share / SSH)
- Auth model and credential location
- Gotchas: naming mismatches, region-specific URLs, things that aren't where you'd guess

**Do not include:**
- Endpoint tables (that's API documentation — the API's own docs are the source of truth)
- Request/response format examples (implementation spec)
- Integration flow diagrams (design documentation)
- The project's own files, paths, or internal architecture

**The test:** If the information describes how to *reach* an external system, it belongs.
If it describes how your code *uses* the system, it doesn't.

## Workflow: Starting a New Project

1. Create `requirements.md` from the template (see Document Structure above)
2. Fill in Problem Statement and Actors first — these frame everything else
3. Populate the Glossary if the domain has any ambiguous or overloaded terms
4. Draft functional requirements — prefer many small atomic requirements over few large ones
5. Identify constraints early — these narrow the solution space before design begins
6. Log any immediate design decisions with rationale
7. Capture unknowns as open questions
8. Identify external systems mentioned in requirements (databases, APIs, file servers,
   auth providers). Document their topology in a separate `systems.md`: server/hostname,
   access method, credential location, and what the system is used for. Explicitly note
   what is NOT where an LLM might guess.

## Workflow: Starting a Coding Session

1. Read the full `requirements.md` before writing any code
2. Note any `in-flux` or `draft` requirements relevant to the current task
3. If the task touches an open question, raise it rather than assuming an answer
4. Reference requirement IDs in commit messages and code comments where non-obvious

## Workflow: Updating Requirements

- **Adding a requirement**: Assign the next available ID in its category. Default status to `draft`.
- **Changing status**: Update in place. No changelog needed — git tracks it.
- **Recording a decision**: Append to the Decisions section. Never modify existing decisions.
- **Resolving a question**: Remove from Open Questions. Add the resolution as a requirement,
  constraint, or decision as appropriate. Include a `Resolves: Q-ID` field in the new item
  so the trail is preserved in git history. Don't keep resolved questions in the doc — they
  waste context.
- **Discovering a domain quirk**: Add to Glossary → Domain Quirks immediately. These are
  high-value and easy to forget.
- **Identifying a non-goal**: Add to Non-Goals with rationale. Especially valuable during
  re-implementation work — stops the same false requirement from being proposed repeatedly.

## Keeping Requirements Up to Date During Development

Requirements drift when code changes happen without updating the requirements doc.
This is the most common failure mode — over a long session, Claude forgets to check.

### Architecture

Three pieces work together:

1. **Hook** (`hooks/req_change_hook.py`) — fires on every `UserPromptSubmit`,
   injects a lightweight reminder into the main agent's context to assess whether
   the user's message implies a requirement change. Skips trivial prompts. Only activates
   when the project has a `requirements.md` file.

2. **Main agent** — reads the injected reminder, decides if there's a requirement
   change, confirms with the user, then delegates the update.

3. **`requirements-editor` subagent** (`agents/requirements-editor.md`) —
   receives a delegation like "resolve Q-24, add D-24, the rule is X, affects
   FR-04 and FR-08." It edits requirements.md / systems.md / project config files
   following all conventions (sequential IDs, append-only decisions, cross-references,
   validation checklist). It never touches code.

This separation means the main agent stays in "understand the problem and write
code" mode. The subagent stays in "maintain the requirements doc" mode with the
full conventions in its system prompt. Neither forgets its role.

### What Triggers a Requirement Change

The main agent should delegate to `requirements-editor` when the user's message implies:

- A new capability not in requirements ("we also need to...")
- A correction to existing behaviour ("actually it should...", "that's wrong")
- A changed business rule
- A new constraint ("it also needs to work with...")
- A domain knowledge correction (glossary term, quirk, mapping change)
- A new or changed external system dependency (also update systems.md)
- A design decision that should be logged
- A new deliverable or artifact that should exist (documentation, config files, reports)

The main agent should also delegate when:
- A behaviour is identified as a non-goal ("we don't need X because...")

The main agent should NOT delegate for:

- Bug fixes for existing requirements
- Refactoring or implementation approach changes
- Debugging and experimentation
- Performance improvements within existing NFRs
- Dead ends that get reverted

### The Confirm-Delegate-Implement Pattern

When the main agent detects a requirement change:

1. State the proposed requirement update concisely (one sentence)
2. Get user confirmation ("yep" / "no, just experimenting")
3. Delegate to `requirements-editor` with a clear instruction
4. Wait for the subagent to complete
5. Then implement the code change

This should be fast — one exchange with the user, then a background delegation.

## Challenging Requirements for Completeness

When asked to review requirements, check for:

- Requirements that say "fast", "secure", "easy" without measurable criteria
- Missing error/edge cases (what happens when X fails?)
- Implicit requirements that everyone assumes but nobody wrote down
- Actors whose needs aren't covered by any requirement
- Constraints that conflict with requirements
- Open questions that block `must`-priority work
