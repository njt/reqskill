# reqskill

Requirements management toolkit for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Three skills, a subagent, and a hook that keep requirements documents accurate across long coding sessions.

## Why

LLM coding sessions drift. Over a long session, Claude forgets what the system is supposed to do, conflates implementation details with requirements, re-proposes ideas that were already rejected, and lets requirements rot while the code evolves.

This toolkit makes requirements a durable, structured artifact that survives across sessions and keeps the LLM honest. A lightweight hook checks every user message for requirement changes and nudges Claude to update the docs before writing code.

## What's In the Box

| Component | Purpose |
|-----------|---------|
| `skills/gathering-requirements/` | Socratic elicitation — build requirements.md from scratch for a new project |
| `skills/reverse-engineering-requirements/` | Extract requirements from existing source code via iterative subagent review |
| `skills/requirements-management/` | Keep requirements in sync during development; defines document structure and conventions |
| `agents/requirements-editor.md` | Subagent that edits requirements.md and systems.md with strict conventions |
| `hooks/req_change_hook.py` | Fires on every user message; injects a reminder to check for requirement changes |
| `assets/requirements-template.md` | Blank requirements.md to start a project with |
| `assets/systems-template.md` | Blank systems.md for documenting external system topology |

## This Is Opinionated

This isn't a generic requirements framework. It encodes specific beliefs about how requirements should work with LLM-assisted development:

- **Requirements are user-observable capabilities, not implementation details.** The litmus test: "If I changed this, would the user notice a different *capability*?" If no, it's a decision or style — not a requirement.
- **Flat atomic requirements.** Each testable behaviour gets its own ID. No nesting (FR-01.1). Nesting creates ambiguity about status and completeness.
- **Decisions are append-only.** Never overwrite — supersede with a new decision that references the original. Tracks ownership: LLM decisions can be revisited freely; human decisions are treated as given.
- **Open questions over assumptions.** When uncertain, record a question. Resolve it into a requirement, constraint, or decision — never silently.
- **Non-goals are first-class.** Things that exist in the old system but are explicitly rejected for the new one. Without this, every reviewer rediscovers the same accidental complexity.
- **The glossary is not optional.** Domain terms cause more bugs than missing features.
- **Don't trust the LLM to remember.** The hook injects a reminder on every message. The system assumes Claude will forget — because it will.
- **Confirm before updating.** Never silently change requirements. Detect, confirm with the human, then delegate to the subagent.
- **Fresh eyes for review.** Each review iteration uses a new subagent with clean context. Reusing one means inheriting its blind spots.

## Install

Requires [Claude Code](https://docs.anthropic.com/en/docs/claude-code) and Python 3.

```bash
git clone https://github.com/njt/reqskill.git
cd reqskill

# Skills
cp -r skills/gathering-requirements ~/.claude/skills/
cp -r skills/requirements-management ~/.claude/skills/
cp -r skills/reverse-engineering-requirements ~/.claude/skills/

# Agent
mkdir -p ~/.claude/agents
cp agents/requirements-editor.md ~/.claude/agents/

# Hook
mkdir -p ~/.claude/hooks
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
            "command": "bash -c \"python3 ~/.claude/hooks/req_change_hook.py\""
          }
        ]
      }
    ]
  }
}
```

If you already have a `settings.json`, add the hook entry to your existing `UserPromptSubmit` array.

The `bash -c` wrapper ensures `~` expands correctly on both Unix and Windows (via Git Bash).

## Usage

**Starting a new project** — Claude will invoke the `gathering-requirements` skill. It walks through problem framing, iterative elicitation, gap probing, and completeness review. Produces `requirements.md` and optionally `systems.md`.

**Have existing code, need a spec** — Invoke `reverse-engineering-requirements`. A subagent reads the source and drafts requirements, then 2-3 rounds of fresh-eyes review separate real requirements from implementation accidents and identify non-goals.

**During development** — The hook handles this automatically. On every message, it checks whether the project has a `requirements.md` and reminds Claude to assess whether your message implies a requirement change. If it does, Claude confirms with you, then delegates the doc update to the `requirements-editor` subagent before writing code.

**Starting from scratch** — Copy `assets/requirements-template.md` into your project as `requirements.md`.

## Document Structure

The requirements.md produced by these skills follows this structure:

1. Project header
2. Problem Statement
3. Actors
4. Glossary (terms + domain quirks)
5. Functional Requirements (FR-01, FR-02, ...)
6. Constraints (C-01, C-02, ...)
7. Non-functional Requirements (NF-01, NF-02, ...)
8. Future Scope
9. Non-Goals
10. Decisions (D-01, D-02, ... — append-only)
11. Open Questions (Q-01, Q-02, ...)

## Architecture

```
User message
    ↓
Hook (req_change_hook.py)
    - Fires on UserPromptSubmit
    - Skips trivial prompts
    - Only activates if project has requirements.md
    - Injects lightweight reminder into context
    ↓
Main Agent (Claude)
    - Reads reminder
    - Assesses whether user's message implies a requirement change
    - If yes: states the change, confirms with user
    - If no: proceeds normally
    ↓
requirements-editor subagent
    - Edits requirements.md / systems.md
    - Enforces conventions (sequential IDs, append-only decisions, validation)
    - Never touches application code
    ↓
Main Agent implements code changes
```

## License

MIT
