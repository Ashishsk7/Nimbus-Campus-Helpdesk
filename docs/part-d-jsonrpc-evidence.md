# Part D — JSON-RPC evidence, capability negotiation and the npm check

## Honesty box (read first)

| Item | Status |
|---|---|
| Server code (`mcp-server/server.py`, `campus_data.py`) written | Done |
| Data logic unit-tested | **Executed** (see `TEST-RESULTS.md`) |
| `mcp` SDK installed / server started / Inspector used | **NOT done** — the assistant's sandbox had no network and no `mcp` package |
| Real JSON-RPC logs, Inspector screenshots, SDK version | **None exist yet.** Capture them yourself with section 3 below |
| `@nimbus/mcp-skill-bridge` registry check | **NOT performed** (no network). Reproducible commands in section 5 |

This file contains **no captured output**. Boxes labelled *Student to paste* are empty on purpose.
Message *shapes* in section 2 come from the MCP specification and are what **you send**, not what the server returned.

Sources checked 18 Nov 2026:
- https://modelcontextprotocol.io/specification/latest/changelog (what changed in revision 2026-07-28)
- https://modelcontextprotocol.io/specification/latest (overview)
- Python SDK README (read via GitHub mirrors, so re-check the primary repo https://github.com/modelcontextprotocol/python-sdk): `from mcp.server.fastmcp import FastMCP`, `@mcp.tool()`, `@mcp.resource(...)`, `mcp.run()`, `mcp dev server.py`, `pip install "mcp[cli]"`.

## 1. Important: the protocol start-up changed in the newest revision

The official changelog for revision **2026-07-28** says MCP became **stateless**: the `initialize` /
`notifications/initialized` handshake was **removed**; every request now carries the protocol version and client
capabilities in `_meta`; and servers must implement a new `server/discover` RPC that advertises supported
versions, capabilities and identity. The previous revision is `2025-11-25`, which still used `initialize`.

The brief (and most tutorials) ask you to document `initialize`. Which exchange you will actually see depends on the
**version of the `mcp` package you install** and the protocol version it negotiates. So:
1. Install the SDK, run `pip show mcp`, and write the version in the table in section 3.
2. Capture what really happens. If you see `initialize`, document it. If the SDK speaks the newest revision, document
   `server/discover` and the `_meta` fields instead, and explain the difference in your report — that is a stronger
   answer than copying an outdated tutorial.

## 2. What the messages look like (specification shapes — illustrative)

All MCP messages are JSON-RPC 2.0 objects: a **request** has `jsonrpc`, `id`, `method`, `params`; a **response** has
the same `id` plus either `result` or `error`; a **notification** has no `id` and gets no reply.

### 2.1 `initialize` (revisions up to 2025-11-25) — what the client sends
```json
{"jsonrpc":"2.0","id":1,"method":"initialize",
 "params":{"protocolVersion":"2025-11-25","capabilities":{},
           "clientInfo":{"name":"manual-test","version":"0.0.1"}}}
```
The server's response (**Student to paste the real one**) should contain: the protocol version the server chose, the
server's `capabilities` (for this project: `tools` and `resources`, because it defines no prompts), and `serverInfo`
with the name `nimbus-campus-helpdesk`. The client then sends the notification `notifications/initialized`.

### 2.2 `tools/list` — what the client sends
```json
{"jsonrpc":"2.0","id":2,"method":"tools/list"}
```
Expected in the response (**Student to paste**): two tools, `get_timetable` and `get_fee_status`, each with a
`description` and an `inputSchema` (a JSON Schema listing the required string arguments).

### 2.3 `tools/call` — what the client sends
```json
{"jsonrpc":"2.0","id":3,"method":"tools/call",
 "params":{"name":"get_timetable","arguments":{"batch":"CSE-A","day":"Monday"}}}
```
Expected in the response (**Student to paste**): a `result` whose content holds the four Monday classes for CSE-A.

### 2.4 Resource read (optional extra)
```json
{"jsonrpc":"2.0","id":5,"method":"resources/read","params":{"uri":"hostel://rules"}}
```

## 3. How to capture the REAL exchange on your Mac

```bash
cd ~/Nimbus-Campus-Helpdesk
source .venv/bin/activate
pip show mcp | head -3          # record Name/Version in the table below
```

**Method A — raw stdio (gives you a log file you can paste).** The stdio transport carries one JSON message per
line, so you can pipe messages into the server. (Confirm the framing on the transports page of the spec.)
```bash
( printf '%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"manual-test","version":"0.0.1"}}}' \
  '{"jsonrpc":"2.0","method":"notifications/initialized"}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \
  '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"get_timetable","arguments":{"batch":"CSE-A","day":"Monday"}}}' \
  '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"get_fee_status","arguments":{"student_id":"STU9999"}}}' \
  ; sleep 3 ) | python mcp-server/server.py | tee raw-session.jsonl
```
`sleep 3` keeps stdin open long enough for the replies to arrive. If your SDK rejects `2025-11-25` or refuses
`initialize`, adjust according to section 1. Do not commit `raw-session.jsonl` if it contains anything personal (it
shouldn't — all data is mock).

**Method B — MCP Inspector (gives you screenshots).**
```bash
source .venv/bin/activate
mcp dev mcp-server/server.py
```
This is the documented SDK shortcut; it needs Node.js/`npx` on your machine and prints a local URL to open in the browser.
Alternative: `npx -y @modelcontextprotocol/inspector`, then in the UI choose transport **STDIO**, command = the full
path to `.venv/bin/python`, arguments = `mcp-server/server.py`, and click **Connect**. In the Inspector:
**Tools** tab → *List Tools* → run `get_timetable` (CSE-A / Monday) → run `get_fee_status` with `STU9999` for the
failure case; **Resources** tab → read `hostel://rules`. The Inspector's "History"/message pane shows the JSON-RPC
traffic you can screenshot.

### Version table — Student to fill in
| Item | Value |
|---|---|
| Python version (`python --version`) | |
| `mcp` package version (`pip show mcp`) | |
| Protocol version seen in the exchange | |
| Handshake observed (`initialize` or `server/discover`/`_meta`) | |
| Inspector command used | |

### Annotated exchange — Student to paste
```
(initialize or server/discover request + response)

(tools/list request + response)

(tools/call get_timetable request + response)
```

## 4. Capability negotiation (in your own words — adapt this paragraph)

Before a client and server do any real work, they must agree on two things: **which version of the protocol** they
both speak and **which optional features** each side supports. In the handshake-based revisions the client
announces the version and its capabilities in `initialize`; the server answers with the version it will use and its own
capabilities (e.g. "I offer tools and resources"), and the client confirms with `notifications/initialized`. After
that, each side only uses features the other declared. Our server declares tools and resources, so a client should not
expect prompts from it. In the newest revision the same information is not negotiated once per connection;
instead each request carries the version and client capabilities in `_meta`, and the server describes itself via
`server/discover`, replying with an `UnsupportedProtocolVersionError` if it cannot speak the requested version.
Either way, the purpose is the same: avoid sending messages the other side cannot understand.

**JSON-RPC in a sentence:** every message is a small JSON object with `"jsonrpc":"2.0"`; requests carry an `id` so the
reply can be matched to the question; notifications have no `id` and expect no reply; failures are returned as an
`error` object (protocol problems) or, for tools, as a normal result flagged as an error.

## 5. Tool descriptions and the attack surface

Tool names, descriptions and schemas are sent to the model so it can decide when and how to call a tool. That means
they are **part of the prompt**. A malicious or compromised server can hide instructions inside a description
("tool poisoning"), and the model may follow them. The MCP specification itself says descriptions of tool behaviour
should be considered untrusted unless they come from a trusted server. Our descriptions are therefore short and
factual: inputs, outputs, "read-only", "mock data". Review descriptions in the Inspector (`tools/list`) whenever you add
a third-party server.

## 6. One invalid-input failure example

| | |
|---|---|
| Call | `get_fee_status` with `student_id = "STU9999"` (valid format, not in the mock data) |
| What the code does | `campus_data.get_fee_status_data` raises `ValueError("No fee record found for that student id.")` — the same message for any unknown id, so the server never reveals which ids exist |
| **Executed evidence** | Unit test `FeeToolLogicTests.test_unknown_id_is_rejected_with_generic_message` passes (the exception and message). |
| Expected on the wire | The SDK reports a tool exception as a tool result flagged as an error (`isError: true`) containing that message, rather than crashing the server. **UNVERIFIED — capture the real result** with Method A (message id 4) or the Inspector. |
| Other rejected inputs | `student_id = "hello"` (bad format), `batch = "CSE-Z"`, `day = "Funday"` — see `tests/test_server.py` |

Student to paste the real failure response here:
```
```

## 7. Does `@nimbus/mcp-skill-bridge` version 2.3 exist on the public npm registry?

**Result of an actual registry check: NONE — not performed.** The assistant's sandbox could not resolve
`registry.npmjs.org` (an attempt returned a DNS error), so the registry was never queried. A web search for the scoped
name returned only *differently named* projects (for example an unscoped `mcp-skill-bridge` listed on a third-party stats
site, and other Skill→MCP converters). A search engine is **not** a registry check, so the status is:
**UNVERIFIED — run the commands below and record the real result.**

Run these on your Mac (they only *read* metadata; do **not** `npm install` an unknown package — install scripts can run code):
```bash
# 1. Does the package name exist at all? (exit code non-zero and an E404 message mean "not found")
npm view @nimbus/mcp-skill-bridge name version

# 2. Does version 2.3 specifically exist? ("2.3" is not a full version; list all versions and look for 2.3.x)
npm view @nimbus/mcp-skill-bridge versions --json

# 3. Raw HTTP check without npm (404 = not found, 200 = exists)
curl -s -o /dev/null -w "%{http_code}\n" "https://registry.npmjs.org/@nimbus%2Fmcp-skill-bridge"
```
Record: date/time, the exact command, and the full output (copy or screenshot). Also note the npm version
(`npm --version`). If the package **does** exist, inspect the publisher, repository link and publish date before trusting
it; if it does **not**, write "not found on the public registry on <date>; built the server without it", which is what
the question asks for. Either way this project does not depend on it.

| Check | Command | Date/time | Output (paste) |
|---|---|---|---|
| Name exists? | `npm view @nimbus/mcp-skill-bridge name version` | | |
| Versions list | `npm view @nimbus/mcp-skill-bridge versions --json` | | |
| HTTP status | `curl … registry.npmjs.org/@nimbus%2Fmcp-skill-bridge` | | |
