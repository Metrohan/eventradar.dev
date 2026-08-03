#!/usr/bin/env bash
set -euo pipefail

TASK_ID="${1:-}"
[[ -n "$TASK_ID" ]] || { echo "Usage: $0 TASK-001" >&2; exit 1; }

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "Not inside a Git repository." >&2
  exit 1
}
cd "$ROOT"

TASK_DIR="tasks/active/$TASK_ID"
[[ -d "$TASK_DIR" ]] || { echo "Task not found: $TASK_DIR" >&2; exit 1; }

OUTPUT="$TASK_DIR/CONTEXT.md"
{
  echo "# Generated Continuation Context"
  echo
  echo "Generated at: $(date --iso-8601=seconds)"
  echo
  echo "## Repository"
  echo
  echo "Root: $ROOT"
  echo "Branch: $(git branch --show-current)"
  echo
  echo "## Git status"
  echo '```text'; git status --short | head -100; echo '```'; echo
  echo "## Recent commits"
  echo '```text'; git log --oneline -10; echo '```'; echo
  echo "## Diff summary"
  echo '```text'; git diff --stat; echo '```'; echo

  for file in TASK.md PLAN.md STATE.yaml HANDOFF.md TESTS.md REVIEW.md; do
    echo "## $file"; echo
    [[ ! -f "$TASK_DIR/$file" ]] || cat "$TASK_DIR/$file"
    echo
  done
} > "$OUTPUT"

echo "$OUTPUT"
