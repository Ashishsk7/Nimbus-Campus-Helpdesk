# campus-helpdesk (Claude Code plugin)

Part of the Nimbus Campus Helpdesk assignment. **All data is mock data.**

| Component | File | What it does |
|---|---|---|
| Manifest | `.claude-plugin/plugin.json` | Names the plugin `campus-helpdesk`. |
| Skill | `skills/timetable-helper/` | Answers timetable questions from `data/timetable.csv` through a lookup script. (Bundled copy of `../../skills/timetable-helper`; a test checks the copies are identical.) |
| Slash command | `commands/timetable-check.md` | `/campus-helpdesk:timetable-check CSE-A Monday` |
| Hook | `hooks/hooks.json` + `hooks/scripts/protect-data.sh` | `PreToolUse` hook that blocks Write/Edit/MultiEdit inside the project's `data/` directory; fails closed on malformed input. |
| MCP config | `.mcp.json` | Starts `mcp-server/server.py` (Part D) with the project's `.venv` Python. |

## Before installing
1. Create the virtual environment in the **project root** (`.venv`) and install the requirements (see the main README).
2. `chmod +x plugins/campus-helpdesk/hooks/scripts/protect-data.sh`
3. Start Claude Code **from the project root** (the MCP config and the hook use `${CLAUDE_PROJECT_DIR}`).

## Install / verify / uninstall
See `docs/part-c-threat-model.md`, section 4, for the exact commands and what to screenshot.

## Status
Not yet loaded in Claude Code by the author of these files. Treat plugin loading, hook invocation and MCP startup as
**UNVERIFIED** until you have run the steps and captured evidence. Review `hooks/` and `.mcp.json` before installing any
plugin — a plugin runs with your user privileges.
