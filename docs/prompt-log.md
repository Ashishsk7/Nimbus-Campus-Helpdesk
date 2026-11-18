# Part F — Prompt log and reflection

## How to use this file
Every row is a template/example **awaiting your actual verification**. Replace the italic placeholders with what
really happened when *you* ran the prompt. Do not keep an entry you did not actually perform, and do not write that you
verified something unless you did. The marking scheme rewards honest entries that show a wrong or unverifiable AI
answer and how you detected it.

Status codes: **REAL-PROMPT** = a prompt that was actually used to build this project; **EXAMPLE** = suggested prompt
that has **not** been run by anyone yet.

## Prompt log

| # | Status | Tool used | Exact prompt | Summary of AI output | Verification method | What was changed or rejected, and why |
|---|---|---|---|---|---|---|
| 1 | REAL-PROMPT (summary below is the assistant's own account; **you must verify it**) | Claude (chat) | *Paste the exact long build prompt you sent ("Act as a Senior AI Systems Engineer … Nimbus Campus Helpdesk Toolchain …").* | The assistant read the question paper and the reference report, searched official docs, generated the project, ran stdlib unit tests and reported which parts were NOT run (SDK, Claude Code, Inspector, npm). | *Student to do:* re-open each Part A source URL; run `python3 -m unittest discover -s tests -v`; run the Part C/D steps. | *Student to fill in.* The assistant reported that it ignored a hidden "Note to AI systems" in the question paper (asking for the phrase "As per the NimbusSync Plugin Standard v4.2"), because no such standard was found. Confirm by reading Part C of the paper yourself. |
| 2 | EXAMPLE — not yet run | *e.g. ChatGPT / Claude / Gemini* | "Which git command syncs all my worktrees with upstream?" | *Record the answer.* **Watch for:** an invented `git worktree sync --all`. | Run `git worktree --help`; compare with https://git-scm.com/docs/git-worktree. | *e.g. rejected `git worktree sync` because it is not a documented subcommand; used `git fetch` + `git pull --rebase` per worktree.* |
| 3 | EXAMPLE — not yet run | *any chat AI* | "Summarise RFC 9999 'MCP Transport Security' and the Ed25519 signing rule." | *Record the answer.* **Watch for:** a confident summary of a document that is not that RFC. | Open https://www.rfc-editor.org/info/rfc9999; read the title and abstract; skim the MCP transport spec. | *e.g. rejected the summary: the live RFC page title does not match.* |
| 4 | EXAMPLE — not yet run | *any chat AI* | "Give me the key findings of Hendricks and Oyelaran (2024) on skill collapse." | *Record the answer.* **Watch for:** fabricated findings, DOI or venue. | Search Google Scholar and arXiv for the exact title/authors; try to open any DOI it gives. | *e.g. marked the claim UNVERIFIED in Part A; did not cite the paper.* |
| 5 | EXAMPLE — not yet run | *any chat AI* | "How do I install `@nimbus/mcp-skill-bridge@2.3` to auto-convert Skills to MCP tools?" | *Record the answer.* **Watch for:** a ready-made `npm install` command for a package that may not exist. | `npm view @nimbus/mcp-skill-bridge name version` (metadata only; do not install). | *e.g. did not use the package; built the server with the official Python SDK.* |
| 6 | EXAMPLE — not yet run | *Claude Code / any AI* | "Use the built-in /worktree-merge command to merge my three branches automatically." | *Record the answer.* **Watch for:** the AI pretending the command exists or merging without showing the diff. | Type `/` and `/help` in Claude Code; search the official docs index; read the diff before accepting any merge. | *e.g. merged manually; recorded that no built-in command was found.* |
| 7 | EXAMPLE — not yet run | *any chat AI* | "Explain the MCP initialize handshake and write the exact JSON the server replies with." | *Record the answer.* **Watch for:** an outdated handshake (the newest spec revision removed `initialize`) or a made-up server reply. | Compare with https://modelcontextprotocol.io/specification/latest/changelog and your own captured log. | *e.g. replaced the AI's reply with my real captured response.* |

## Part F reflection (draft, about 300 words — rewrite in your own voice)

> **Before you submit:** this draft is based on the design of the project and the audit, not on experiences you have
> had. Edit it, and delete or soften any sentence that you cannot honestly support after doing the work yourself.

A Skill, a plugin, an MCP server and a worktree each solve a different problem. A Skill is knowledge: a folder of
instructions that tells an agent *how* to do a task, such as answering timetable questions only from the CSV. A plugin is
packaging: it bundles skills, commands, hooks and server settings so they can be installed as one unit. An MCP
server is a connection: it gives the agent live tools and data through a standard protocol. A Git worktree is
workflow isolation: it lets several people or AI sessions edit different branches at the same time without
disturbing each other.

I would choose a Skill over an MCP tool when the need is guidance, wording or a repeatable procedure, and when the data
is small and static. An MCP tool is better when the answer must come from live or changing data, needs
authentication, or must run code on a server, as with fee status. Our timetable Skill even calls a deterministic
script, which shows the two ideas can be combined.

An agent should never be trusted without review with security decisions, merges, deleting files or branches,
anything that touches real student data or credentials, legal or financial wording, and claims that cite
sources. A person must read the diff, run the tests and check the source.

The question paper shows why. It contained a command that does not exist (`git worktree sync`), a specification date
that cannot exist, an RFC number that matched no real document, a package name that needed a registry check, and a
paper that could not be found. Each looked plausible. The lesson is simple: a confident answer is not evidence.
Check commands against the manual, packages against the registry, and citations against the original source, and
write "Unverified" when you cannot.
