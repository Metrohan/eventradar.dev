<!-- METO-AI:PROJECT_POLICY:BEGIN -->
# Agent Workflow

This repository follows the Meto Agent Control Plane.

## Required flow

1. Read the active task.
2. Inspect Git state.
3. Plan non-trivial changes.
4. Implement only approved scope.
5. Test with repository commands.
6. Request independent review.
7. Update durable handoff files.
8. Leave merge and deployment to the human developer.

## Commands

Prefer `just install`, `just dev`, `just lint`, `just typecheck`, `just test`, and `just check`.

If a command is not configured, record the limitation.

## Durable task memory

Active tasks live under `tasks/active/<TASK_ID>/` with:

- `TASK.md`
- `PLAN.md`
- `STATE.yaml`
- `HANDOFF.md`
- `TESTS.md`
- `REVIEW.md`
- `CONTEXT.md`
<!-- METO-AI:PROJECT_POLICY:END -->

# Project-specific instructions\n\nAdd architecture, commands, constraints, and fragile areas.
