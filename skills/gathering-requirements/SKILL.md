---
name: gathering-requirements
description: >
  Interactive requirements elicitation through Socratic questioning. Use when: starting a new
  project and need to build requirements.md from scratch; user says "I need to build X" or
  "help me plan X" or "let's figure out what this thing needs to do"; user has a rough idea
  but hasn't written requirements yet; user has existing documentation (howtos, runbooks,
  config files, wikis) that contain implicit requirements needing extraction; user wants to
  flesh out incomplete requirements.md. Triggers: "gather requirements", "what should this
  do", "let's figure out the requirements", "I need to automate...", "help me plan...", or
  any new project description without an existing requirements.md. NOT for maintaining
  requirements during development — use requirements-management for that.
---

# Gathering Requirements

## Purpose

Extract structured requirements from a human stakeholder's head (and their existing
documentation) through iterative questioning. The human has domain knowledge. You have
structure. Together you produce a requirements.md and optionally systems.md that an LLM
can use to build the thing.

This is the **Capture** and **Challenge** phase. The requirements-management skill handles
everything after this — maintenance during development, subagent updates, session startup.

## Role Division

**You do:** Ask questions. Listen. Compile. Filter noise from signal. Identify gaps.
Draft structured requirements text. Propose open questions for things you can't resolve.

**The human does:** Supply domain knowledge. Correct your misunderstandings. Answer
questions. Provide existing documentation. Confirm or reject your interpretations.

**You never:** Guess at business rules. Invent requirements the human didn't imply.
Assume you understand a domain term without confirming. Skip to implementation.

## What Belongs in Requirements

As you extract requirements, continuously filter:

**Requirement** = behaviour observable from outside. "Display client name in task list."
**Decision** = how the system achieves a requirement. "Store config at ~/.cu/config.json."
**Style** = formatting/presentation. "Truncate names at 45 characters with '...' suffix."
**Non-Goal** = something explicitly rejected. "Font size buttons (old platform constraint, unnecessary on web)."

The litmus test: "If I changed this, would the user notice a different *capability*?"
If yes → requirement. If no → decision or style.

When extracting from existing code or documentation, implementation details will dominate.
Record the *user need*, not the implementation. See requirements-management skill for
the full "Requirements vs Spec vs Style" guide.

## The Gathering Workflow

### Phase 1: Problem Framing (1-3 turns)

Start with the broadest questions. Get the shape of the problem before details.

1. **What's the pain?** "What are you trying to solve, and who experiences it?"
2. **What does done look like?** "If this worked perfectly, what would your day look like?"
3. **What exists today?** "What's the current process? Manual? Partially automated? Nothing?"

After these answers, draft:
- Problem Statement (2-3 paragraphs)
- Actors table
- Initial scope boundary ("this project does X, not Y")

Present this draft to the human for correction. Don't proceed until they confirm
the problem framing is right.

### Phase 2: Requirements Elicitation (3-10 turns)

Now drill into specifics. One topic at a time. One question at a time.

**The braindump invitation:** Ask the human to describe the process in their own words.
Accept messy, non-linear, stream-of-consciousness answers. Your job is to listen and
then organize — not to force the human into your structure.

From the braindump, extract:
- Functional requirements (what the system does)
- Constraints (what limits the solution)
- Non-functional requirements (how well it must do it)
- Glossary terms (any word that has domain-specific meaning or multiple aliases)
- Domain quirks (the "actually" and "except when" cases — these are the most valuable)
- Open questions (things the braindump left ambiguous)

**Draft a requirements.md** after enough material has accumulated. Use the template
from `assets/requirements-template.md`. Present it to the human. Expect corrections.

### Phase 3: Probing for Gaps (2-5 turns)

After the initial draft, challenge it systematically. Ask about:

- **Missing error cases:** "What happens when X fails? When data is missing? When the
  network is down?"
- **Edge cases the human forgot:** "You mentioned 25 clients — are any of them weird?
  Special rules? Different billing? Different naming?"
- **Implicit requirements:** "You haven't mentioned authentication — is that intentional?"
- **Vague terms:** "You said 'fast' — what's the actual latency target?"
- **Actors whose needs aren't covered:** "You listed [actor] but no requirement
  touches their workflow."
- **Constraints that conflict:** "C-01 says X, but FR-03 seems to require not-X."
- **Scope ambiguity:** "Is [thing] in scope or future work?"

Each answer either resolves an open question, adds a requirement, or adds a decision.
Update the draft.

### Phase 4: Document Ingestion (0-N turns, as documents arrive)

When the human provides existing documentation (howtos, config files, runbooks,
wikis, code), ingest it:

1. **Read the whole document** before extracting anything.
2. **Map to existing requirements.** Does it confirm, contradict, or extend what
   you've already captured?
3. **Extract new requirements** the human didn't mention in conversation.
4. **Extract glossary terms** — especially aliases and domain quirks.
5. **Extract system topology** — server names, paths, credentials locations,
   API endpoints. These go in systems.md, not requirements.md.
6. **Flag contradictions** — when the document says something different from what
   the human told you, ask. Don't silently pick a side.
7. **Raise new open questions** — the document will reveal things neither of you
   thought to ask about.

Update the requirements.md draft. Tell the human what you added and what you're
unsure about.

**Key insight from experience:** Documents contain the "actually" and "except when"
cases that humans forget to mention. A config file or runbook is often more accurate
than memory for per-entity rules and edge cases. Treat documents as a primary source,
conversation as clarification.

### Phase 5: Systems Documentation (1-2 turns)

If the project interacts with external systems (databases, APIs, file servers,
auth providers), create `systems.md`. This documents **topology** — what exists,
where it lives, how to reach it. It is NOT an API reference or integration guide.

```markdown
# External Systems

## [System Name]
- **What it is:** [brief description]
- **Server/hostname:** [actual name, not what an LLM might guess]
- **Access method:** [API / SQL / file share / etc.]
- **Auth model:** [token / OAuth / session JWT / etc.]
- **Credential location:** [where tokens/passwords live]
- **Used for:** [what this project needs from it]
- **Gotchas:** [anything non-obvious about access or naming]
```

**Include:** How to reach the system, how to authenticate, naming surprises.
**Do not include:** Endpoint tables, request/response formats, integration
flow diagrams. Those are API docs and implementation spec respectively — they
belong in the API's own documentation or in design docs.

**Why this matters:** LLMs will guess wrong about server names, paths, and access
methods. An LLM seeing "MiddleEarth database" might assume the server is called
"middleearth" — but if it's actually on a server called "Treebeard", that's a
session-ending mistake. Document what is NOT where you'd guess.

### Phase 6: Completeness Review (1 turn)

Before declaring requirements complete, check:

- [ ] Every actor has at least one requirement that serves their needs
- [ ] Every `must` requirement has concrete acceptance criteria
- [ ] No requirement uses unmeasurable language ("fast", "easy", "secure")
- [ ] The glossary covers every domain term that appears in requirements
- [ ] Constraints don't contradict requirements
- [ ] Open questions don't block any `must`-priority work
- [ ] If external systems exist, systems.md is populated
- [ ] Non-goals are recorded if any behaviours were explicitly rejected
- [ ] Future scope is explicitly listed (prevents scope creep)

Present the final requirements.md (and systems.md if applicable) to the human.
Ask: "Does this capture what you need? Anything missing or wrong?"

## Questioning Technique

**One question at a time.** Don't overwhelm with a list of 10 questions. Ask the
most important one, let the human answer, then ask the next. Their answer to
question 1 often answers questions 2-4 and raises question 11.

**Accept messy answers.** The human's job is to know things, not to structure them.
If they give you a wall of text with 15 embedded facts, your job is to parse it into
structured requirements — not to ask them to be more organized.

**Prefer concrete follow-ups over abstract ones.** Instead of "can you elaborate on
the billing process?", ask "when you open the Xero invoice, what's the first thing
you check?" Concrete questions get concrete answers with real detail.

**When they say "it depends"** — that's a gold mine. Ask what it depends ON. The
answer is usually a per-entity rule or a domain quirk that needs to be in the config.

**When they say "it's complicated"** — they're right, and they're also worried about
overwhelming you. Say "give me the messy version, I'll organize it." Then actually do.

**When they provide a document** — read it thoroughly before asking questions about it.
Summarize what you learned, flag what contradicts prior conversation, ask about gaps.
Don't make them re-explain what the document already says.

## Output Artifacts

At the end of gathering, you should have produced:

1. **requirements.md** — following the template structure (problem statement, actors,
   glossary, functional requirements, constraints, NFRs, decisions, open questions)
2. **systems.md** — if external systems are involved
3. **A list of remaining open questions** — things that can't be resolved in this
   session and need investigation or another stakeholder

The requirements.md should be ready for the requirements-management skill to maintain
during development, and for a coding agent to build from.

## Anti-Patterns

**Don't interview-dump.** Asking 20 questions in the first message is overwhelming
and the human will skip most of them. Start broad, narrow based on answers.

**Don't over-formalize too early.** The first draft should capture the messy reality.
Clean it up in later passes, not in real-time as the human is talking.

**Don't assume the happy path.** The human will describe how things work when
everything goes right. The bugs live in what happens when things go wrong.

**Don't skip the glossary.** If a domain has more than 3 specialized terms, the
glossary will prevent more bugs than any other section. Every time the human uses
a word you're not 100% sure about, ask.

**Don't treat the human's answer as the only source.** When they provide a document,
it may contradict what they said. The document is usually more accurate for specific
details (names, paths, rules). The human is more accurate for intent and priorities.

**Don't generate requirements the human didn't imply.** You can *ask* "should the
system also do X?" but don't silently add X to the doc. Every requirement should be
traceable to something the human said, a document they provided, or a question you
asked that they confirmed.
