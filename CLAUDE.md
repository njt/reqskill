# reqskill

Requirements management toolkit for Claude Code — skills, agent, and hook for structured requirements elicitation, extraction, and maintenance.

## The Problem

LLM coding sessions drift. Over a long session, Claude forgets what the system is supposed to do, conflates implementation details with requirements, re-proposes ideas that were already rejected, and lets requirements rot while the code evolves. The longer the session, the worse it gets.

This toolkit makes requirements a durable, structured artifact that survives across sessions and keeps the LLM honest.

## This Is Opinionated

This isn't a generic requirements framework. It encodes specific beliefs about how requirements should work with LLM-assisted development:

**Requirements are user-observable capabilities, not implementation details.** The litmus test: "If I changed this, would the user notice a different *capability*?" If no, it's a design decision or style choice, not a requirement. Most requirements docs fail here — they're full of implementation spec masquerading as requirements. This toolkit enforces the distinction.

**Flat atomic requirements over nested hierarchies.** Each testable behaviour gets its own ID (FR-01, FR-02, FR-03). No FR-01.1, FR-01.2. Nesting creates ambiguity about status and completeness.

**Decisions are append-only.** Never delete or overwrite a decision — add a new one that supersedes it. This preserves the reasoning trail. Decisions also track **ownership**: LLM decisions can be freely revisited; human and client decisions are treated as given unless explicitly reopened.

**Open questions over assumptions.** When something is uncertain, record an open question rather than guessing. Questions are resolved by converting them into requirements, constraints, or decisions — never silently.

**Non-goals are first-class.** Especially for re-implementations: things that exist in the old system but are explicitly rejected for the new one. Without this, every fresh reviewer (human or LLM) rediscovers the same accidental complexity and re-proposes it.

**The glossary is not optional.** Domain terms cause more bugs than missing features. If a domain has more than three specialised terms, the glossary will prevent more bugs than any other section.

**Don't trust the LLM to remember.** The hook injects a requirements-check reminder on every user message. The system assumes Claude will forget to check — because over a long session, it will.

**Confirm before updating.** The toolkit never silently updates requirements. The main agent detects a potential change, states it, gets human confirmation, then delegates to a specialised subagent. Requirements are too important for unilateral LLM edits.

**Fresh eyes for review.** In reverse-engineering work, each review iteration uses a new subagent with clean context. Reusing a subagent means inheriting its blind spots.

## What's Here

```
skills/
  gathering-requirements/            Socratic elicitation — build requirements.md from scratch
  requirements-management/           Maintain requirements during development
  reverse-engineering-requirements/  Extract requirements from existing source code
agents/
  requirements-editor.md             Subagent that edits requirements.md/systems.md
hooks/
  req_change_hook.py                 Detects requirement changes on every user prompt
assets/
  requirements-template.md           Blank requirements.md template
  systems-template.md                Blank systems.md template
```

## Three Skills, Three Workflows

- **gathering-requirements** — Greenfield projects. Socratic elicitation from a human's head through iterative questioning. Produces requirements.md and optionally systems.md.
- **reverse-engineering-requirements** — Existing code. Subagent reads source, drafts requirements, then iterative fresh-eyes review (2-3 rounds) separates real requirements from implementation accidents and non-goals.
- **requirements-management** — During development. Keeps docs in sync as code changes. Defines the document structure, conventions, and the confirm-delegate-implement pattern.

## Architecture

```
User message → hook (lightweight check) → main agent (decides) → requirements-editor subagent (edits docs)
```

The hook only fires when a project has `requirements.md`. It injects a reminder, not an action. The main agent decides whether to delegate. The subagent handles all doc edits with strict conventions (sequential IDs, append-only decisions, non-goals, validation).

## Install

Copy files into your `~/.claude/` directory:

```bash
# Skills
cp -r skills/gathering-requirements ~/.claude/skills/
cp -r skills/requirements-management ~/.claude/skills/
cp -r skills/reverse-engineering-requirements ~/.claude/skills/

# Agent
cp agents/requirements-editor.md ~/.claude/agents/

# Hook
cp hooks/req_change_hook.py ~/.claude/hooks/
```

Register the hook in `~/.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/req_change_hook.py"
          }
        ]
      }
    ]
  }
}
```

If you already have a `settings.json` with other hooks, add the hook entry to your existing `UserPromptSubmit` array.

## Usage

- Starting a new project: invoke the `gathering-requirements` skill
- Have existing code and need a spec: invoke the `reverse-engineering-requirements` skill
- During development: the hook and `requirements-management` skill handle it automatically — the hook fires on every message, and the main agent delegates to `requirements-editor` when it detects a change
- Templates in `assets/` can be copied into a project as a starting point
