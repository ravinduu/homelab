---
name: session-wrap-up
description: Wrap up a Codex session by updating persistent project documentation, recording verified lessons, and reviewing unresolved work. Use when explicitly requested at the end of a session.
---

# Session Wrap-Up

Review the work completed in the current session, including commands, test results, problems, fixes, and decisions.

## Instructions

1. Identify verified facts and reusable lessons.
2. Update relevant documentation under `docs/`.
3. Update `.agents/skills/*/SKILL.md` when reusable workflows or procedures have changed.
4. Update `AGENTS.md` only when permanent project instructions need changing.
5. Record unresolved problems and recommended next steps.
6. Avoid duplicating existing information.
7. Never record secrets or unverified assumptions as facts.
8. Distinguish completed changes from planned or pending changes.
9. Preserve all existing security boundaries.

## Safety

- Make documentation-only changes locally.
- Do not modify the remote server.
- Do not change infrastructure configurations.
- Do not automatically commit or push changes.
- Do not weaken security instructions.

## Output

After updating documentation:

1. Show the Git diff.
2. List modified files.
3. Summarize newly captured knowledge.
4. Identify unresolved issues.
5. Recommend the next session's priorities.

Explain what future Codex sessions will know that they did not know before.
