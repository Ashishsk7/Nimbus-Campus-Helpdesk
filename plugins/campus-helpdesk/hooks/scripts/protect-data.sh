#!/usr/bin/env bash
# PreToolUse safety hook for the campus-helpdesk plugin.
#
# Goal: stop Claude from writing/editing anything inside the project's data/ directory.
#
# Input  (stdin): JSON from Claude Code, e.g.
#   {"hook_event_name":"PreToolUse","tool_name":"Write","tool_input":{"file_path":"data/x.csv"},"cwd":"/proj"}
# Output:
#   - protected path  -> prints a JSON "deny" decision on stdout, exit 0
#   - allowed path    -> prints nothing, exit 0 (normal permission flow continues)
#   - malformed input -> message on stderr, exit 2 (blocks the tool call: FAIL CLOSED)
#
# Known limitation: this only inspects Write/Edit/MultiEdit. A shell command (Bash tool)
# such as `echo x > data/file` is NOT inspected here. See docs/part-c-threat-model.md.

set -u

if ! command -v python3 >/dev/null 2>&1; then
  echo "protect-data: python3 not found, blocking (fail closed)." >&2
  exit 2
fi

# Pass the raw JSON to Python through an environment variable (stdin is already consumed by cat).
HOOK_INPUT="$(cat)" python3 - <<'PY'
import json
import os
import sys

raw = os.environ.get("HOOK_INPUT", "")

# 1) Parse and validate the input. Anything unexpected -> block (exit 2).
try:
    event = json.loads(raw)
    if not isinstance(event, dict):
        raise ValueError("top-level JSON is not an object")
    tool_name = event.get("tool_name")
    tool_input = event.get("tool_input")
    if not isinstance(tool_name, str) or not isinstance(tool_input, dict):
        raise ValueError("missing tool_name or tool_input")
except Exception as exc:  # noqa: BLE001 - we deliberately fail closed on anything
    print(f"protect-data: malformed hook input ({exc}); blocking (fail closed).", file=sys.stderr)
    sys.exit(2)

# 2) Only file-writing tools are our concern.
if tool_name not in ("Write", "Edit", "MultiEdit"):
    sys.exit(0)

path = tool_input.get("file_path")
if not isinstance(path, str) or not path.strip():
    print("protect-data: file-writing tool call without a file_path; blocking.", file=sys.stderr)
    sys.exit(2)

# 3) Work out the project root and the absolute target path (resolves .. and symlinks).
cwd = event.get("cwd") if isinstance(event.get("cwd"), str) and event.get("cwd") else os.getcwd()
root = os.path.realpath(os.environ.get("CLAUDE_PROJECT_DIR") or cwd)
target = path if os.path.isabs(path) else os.path.join(cwd, path)
target = os.path.realpath(target)

protected = os.path.join(root, "data")

# macOS filesystems are usually case-insensitive, so compare in lower case (over-blocking is safe).
t, p = target.lower(), protected.lower()
if t == p or t.startswith(p + os.sep):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "Blocked by campus-helpdesk: the data/ directory is protected. "
                                        "Edit mock data by hand outside Claude Code."
        }
    }))
sys.exit(0)
PY
exit $?
