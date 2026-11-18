# Nimbus Campus Helpdesk Toolchain

A small, beginner-friendly project for the assignment **"Building and Auditing an AI-Agent Toolchain"**
(AI Tools and Prompt Engineering, B.Tech CSE). It uses **mock campus data only** — no real students, passwords or keys.

## 1. Project overview
| Part | What is in the repo |
|---|---|
| A — Claim audit | `docs/part-a-claim-audit.md` (10 claims checked against official docs, dated 18 Nov 2026) |
| B — Agent Skill | `skills/timetable-helper/` (SKILL.md, references, deterministic lookup script) + `docs/skill-test-matrix.md` |
| C — Plugin | `plugins/campus-helpdesk/` (manifest, command, hook, MCP config, bundled Skill) + `docs/part-c-threat-model.md` |
| D — MCP server | `mcp-server/` (FastMCP, stdio, 2 tools, 1 resource) + `docs/part-d-jsonrpc-evidence.md` |
| E — Worktrees | `docs/worktree-lab.md` (exact commands + answers) |
| F — Reflection | `docs/prompt-log.md` (template + 300-word reflection draft) |
| Evidence of testing | `TEST-RESULTS.md` (what was and was not executed) |

## 2. Directory structure
```
Nimbus-Campus-Helpdesk/
├── skills/timetable-helper/      SKILL.md, references/, scripts/timetable_lookup.py
├── data/                         timetable.csv, fee_status.json, hostel-rules.md  (mock)
├── plugins/campus-helpdesk/      plugin: .claude-plugin/, commands/, hooks/, skills/, .mcp.json, README.md
├── mcp-server/                   server.py, campus_data.py, requirements.txt
├── docs/                         Part A-F write-ups
├── tests/                        test_timetable.py, test_server.py, test_hook.py
├── .claude-plugin/marketplace.json   official marketplace location
├── marketplace.json              identical copy (assignment asks for it at the root)
├── requirements.txt, .gitignore, README.md, TEST-RESULTS.md
```
Small deviations from the brief: an extra `mcp-server/campus_data.py` (logic separated so it can be tested without the
SDK), an extra `tests/test_hook.py`, and the extra `.claude-plugin/marketplace.json` (the location the Claude Code docs use).

## 3. Prerequisites (macOS)
- macOS with Terminal, **Python 3** (`python3 --version`; the MCP SDK has its own minimum Python version, so check its PyPI page), Git ≥ 2.28 (`git --version`).
- For the Inspector: **Node.js** with `npx` (`node --version`).
- For the plugin: **Claude Code** installed (see Anthropic's docs).
- Internet access for `pip install` and the npm registry check.

## 4. Python virtual environment (macOS)
```bash
cd ~/Nimbus-Campus-Helpdesk            # wherever you unzipped it
python3 -m venv .venv
source .venv/bin/activate              # your prompt now starts with (.venv)
python -m pip install --upgrade pip
pip install -r requirements.txt        # installs the official MCP Python SDK (mcp[cli])
pip show mcp                           # write the real version in docs/part-d-jsonrpc-evidence.md
```
Leave the environment later with `deactivate`.

## 5. Run the timetable tests (no installation needed)
```bash
python3 -m unittest discover -s tests -v
```
These use only the standard library. One test (real FastMCP wiring) is skipped until `mcp` is installed; after
step 4 it runs too. (If you prefer pytest: `pip install pytest && pytest -v`.)

Try the lookup script by hand:
```bash
python3 skills/timetable-helper/scripts/timetable_lookup.py --batch CSE-A --day Monday
python3 skills/timetable-helper/scripts/timetable_lookup.py --batch CSE-B --day Wed --course CS204
python3 skills/timetable-helper/scripts/timetable_lookup.py --batch CSE-A --day Saturday   # no classes
```

## 6. Run the MCP server
```bash
source .venv/bin/activate
python mcp-server/server.py
```
It speaks JSON-RPC over **stdio**, so it will look like it is "hanging" — it is waiting for a client. Press `Ctrl+C` to stop.
Never add `print()` to stdout in this file; it would corrupt the protocol.

## 7. MCP Inspector
```bash
source .venv/bin/activate
mcp dev mcp-server/server.py          # needs Node/npx; prints a local URL to open
```
or `npx -y @modelcontextprotocol/inspector` and choose **STDIO**, command = full path to `.venv/bin/python`,
arguments = `mcp-server/server.py`. Then: list tools → call `get_timetable` (CSE-A, Monday) → call `get_fee_status` with
`STU9999` (failure case) → read resource `hostel://rules`. Full details: `docs/part-d-jsonrpc-evidence.md`.

## 8. Plugin installation (Claude Code)
```bash
chmod +x plugins/campus-helpdesk/hooks/scripts/protect-data.sh
claude plugin marketplace add .
claude plugin install campus-helpdesk@nimbus-campus
claude plugin list
```
Then start `claude` in this folder. Verification, uninstall and the threat model: `docs/part-c-threat-model.md`.
(Quick alternative without a marketplace: `claude --plugin-dir ./plugins/campus-helpdesk`.)

## 9. Git worktree experiment
Follow `docs/worktree-lab.md` step by step (about 10 minutes). It creates three worktrees, an intentional merge
conflict, the resolution, the graph and the cleanup.

## 10. Screenshots to capture for your report
| Part | Screenshot / log |
|---|---|
| A | The official pages you cite (MCP changelog, agentskills.io spec, git-worktree manual, Claude Code plugins page) — with the URL and date visible |
| B | Terminal output of the lookup script for prompts 1, 2, 3 (Saturday adversarial); the unit-test run; Claude Code answering the six prompts (Skill triggered or not) |
| C | `claude plugin validate` output; `claude plugin marketplace add`; `claude plugin install`; `claude plugin list`; `/` menu showing `/campus-helpdesk:timetable-check`; `/mcp` showing the server; the hook **denying** a write to `data/` and **allowing** a write to `docs/`; uninstall output |
| D | `pip show mcp`; Inspector Tools tab (list + `get_timetable` call + the `STU9999` failure); Resources tab (`hostel://rules`); the raw JSON-RPC log (`raw-session.jsonl`); `npm view @nimbus/mcp-skill-bridge …` output |
| E | `git worktree list`; the conflict (`git status` + file with markers); the resolved file; `git log --oneline --graph --decorate --all`; list after cleanup |
| F | Your finished prompt log (with real entries) |

## 11. Known limitations
- No LLM, Claude Code, MCP SDK, Inspector or npm registry was used while creating these files; those parts are
  **UNVERIFIED** until you run them (see `TEST-RESULTS.md`).
- The protocol start-up changed in the newest MCP revision (no `initialize`); what you see depends on your SDK version.
- The hook only checks Write/Edit/MultiEdit, not shell commands (documented in the threat model).
- `${CLAUDE_PROJECT_DIR}` substitution inside the plugin's `.mcp.json` is documented but unobserved; if it fails, use absolute paths.
- The Skill-description comparison in `docs/skill-test-matrix.md` is **predicted**, not measured, until you test it.
- Hendricks & Oyelaran (2024) and RFC 9999 "MCP Transport Security" could not be verified; the audit says so.
- Mock data only; do not add real student information.
