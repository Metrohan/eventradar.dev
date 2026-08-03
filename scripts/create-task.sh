#!/usr/bin/env bash
set -euo pipefail

TASK_ID="${1:-}"
TASK_TITLE="${2:-}"
[[ -n "$TASK_ID" && -n "$TASK_TITLE" ]] || {
  echo "Usage: $0 TASK-001 \"Task title\"" >&2
  exit 1
}

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "Not inside a Git repository." >&2
  exit 1
}
cd "$ROOT"

TARGET="tasks/active/$TASK_ID"
[[ ! -e "$TARGET" ]] || {
  echo "Task already exists: $TARGET" >&2
  exit 1
}

mkdir -p "$TARGET/logs"
for file in TASK.md PLAN.md STATE.yaml HANDOFF.md TESTS.md REVIEW.md; do
  cp "tasks/_template/$file" "$TARGET/$file"
done

BRANCH="task/$(printf '%s-%s' "$TASK_ID" "$TASK_TITLE" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//' | cut -c1-64)"
TIMESTAMP="$(date --iso-8601=seconds)"

python3 - "$TARGET" "$TASK_ID" "$TASK_TITLE" "$BRANCH" "$TIMESTAMP" <<'PY'
from pathlib import Path
import sys
target = Path(sys.argv[1])
repl = {
    "<TASK_ID>": sys.argv[2],
    "<TASK_TITLE>": sys.argv[3],
    "<BRANCH_NAME>": sys.argv[4],
    "<TIMESTAMP>": sys.argv[5],
}
for p in target.iterdir():
    if p.is_file():
        text = p.read_text()
        for old,new in repl.items():
            text = text.replace(old,new)
        p.write_text(text)
PY

echo "$TARGET"
