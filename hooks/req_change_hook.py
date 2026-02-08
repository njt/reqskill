#!/usr/bin/env python3
"""
Requirements change detection hook for Claude Code.

Fires on every UserPromptSubmit. Injects a reminder for the main agent
to assess whether the user's message implies a requirement change.
If so, the main agent confirms with the user then delegates the
documentation update to the requirements-editor subagent.

Installed globally in ~/.claude/hooks/ — activates only when the
current project has a requirements.md file.
"""
import json
import sys
import os

try:
    input_data = json.load(sys.stdin)
except json.JSONDecodeError:
    sys.exit(0)

prompt = input_data.get("prompt", "")

# Don't inject on trivial prompts (very short, or just confirmations)
stripped = prompt.strip().lower()
if len(stripped) < 10 or stripped in ("y", "n", "yes", "no", "ok", "continue", "go", "do it", "yep", "nah", "sure", "thanks"):
    sys.exit(0)

# Check if requirements.md exists in the project
cwd = input_data.get("cwd", ".")
req_path = os.path.join(cwd, "requirements.md")
has_requirements = os.path.exists(req_path)

if not has_requirements:
    sys.exit(0)

# Inject the assessment reminder into Claude's context.
# This is stdout on exit 0 for UserPromptSubmit — it gets added
# to the context Claude sees alongside the user's prompt.
reminder = """[REQUIREMENTS CHECK] This project has a requirements.md managed by the requirements-editor agent.

Before implementing changes, assess whether the user's message implies:
- A new requirement not yet in requirements.md
- A correction to an existing requirement ("actually it should...", "that's wrong")
- A new constraint or business rule
- A domain knowledge correction (glossary, quirk, mapping)
- A new external system dependency (belongs in systems.md)
- A decision that should be logged
- A non-goal ("we don't need X", "that was just a workaround for...")
- A new deliverable or artifact that should exist (documentation, config files, reports)

If YES: state the proposed change concisely, confirm with the user, then delegate the update to the requirements-editor agent BEFORE implementing code changes.
If NO: proceed normally. Do not mention this check."""

print(reminder)
sys.exit(0)
