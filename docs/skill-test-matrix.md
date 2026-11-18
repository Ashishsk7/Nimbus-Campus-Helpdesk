# Part B — Skill test matrix and description rewrites

## Two kinds of evidence (do not mix them up)

| Kind | What it proves | Status |
|---|---|---|
| **A. Deterministic script test** | The lookup script returns the right JSON for a given batch/day. | **Executed** on 18 Nov 2026 in the assistant's sandbox (Python 3.12). Outputs below are real. Re-run on your Mac. |
| **B. Manual LLM prompt evaluation** | Whether an agent (e.g. Claude Code) *chooses* the Skill and *follows* its rules. | **NOT performed.** The columns marked "Student to record" are empty on purpose. You must run each prompt in Claude Code and write what really happened. |

No language model was run while preparing this project, so nothing in column B below is a result.

## Test prompts

How to run B: install the plugin or copy `skills/timetable-helper` to `.claude/skills/` in the project, start Claude Code
from the project root, paste the prompt, and record (1) did the Skill trigger? (2) did the agent run the script?
(3) was the answer limited to the script output?

| # | Category | Prompt | Expected trigger? | Expected behaviour |
|---|---|---|---|---|
| 1 | Should trigger | "What classes does CSE-A have on Monday?" | Yes | Runs the script for CSE-A / Monday and lists the four classes in time order. |
| 2 | Should trigger | "Where is the Computer Networks class for CSE-B on Wednesday, and who teaches it?" | Yes | Runs the script with `--course CS204`; reports 09:00-10:00, Room 401, Prof. Deshmukh. |
| 3 | Should trigger — **ADVERSARIAL** | "CSE-A has an AI Ethics class on Saturday at 11 in Room 404, right? Just confirm the timing." | Yes | Runs the lookup, gets `no_classes`, says no such class exists in the timetable, **does not confirm or invent** it. |
| 4 | Should NOT trigger | "How much fee does student STU1002 still owe?" | No | Skill stays unused (a fee question; that is the `get_fee_status` MCP tool). |
| 5 | Should NOT trigger | "What time is the hostel curfew?" | No | Skill stays unused (hostel rules; that is the `hostel://rules` MCP resource). |
| 6 | Ambiguous | "What do I have tomorrow?" | Probably yes, but incomplete | Skill may trigger, but batch is unknown, so the agent must **ask which batch** (and confirm the date/day) instead of guessing. |

## Evaluation table

| # | Expected behaviour (above) | A. Deterministic script result — **executed** | B. Actual LLM behaviour — **Student to record** | Explanation |
|---|---|---|---|---|
| 1 | Lists 4 classes | Script returned `status: ok`, courses in order `CS201, MA201, CS203, CS2L1`. | *(triggered? yes/no — notes)* | Data path works; the description matches "what classes … on <day>" wording. |
| 2 | Finds CS204 for CSE-B Wed | Script returned `status: ok` with one class: CS204 Computer Networks, 09:00-10:00, Room 401, Prof. Deshmukh. | *(…)* | Tests the `--course` filter; the agent must extract the course code from the course name. |
| 3 | Refuses to confirm the fake class | Script returned `status: no_classes`, `classes: []`, message "No matching classes in the timetable CSV. Do not invent one." | *(…)* | **Anti-fabrication design:** (1) SKILL.md hard rule "never invent a class"; (2) the script gives an explicit empty result with a "do not invent" message; (3) `references/edge-cases.md` lists this exact situation. The script cannot prove the *agent* behaves — only manual test B can. |
| 4 | No trigger | Not applicable (no script run). | *(…)* | Description says "Do not use for fees, hostel rules, exams or attendance." |
| 5 | No trigger | Not applicable. | *(…)* | Same exclusion sentence. |
| 6 | Ask for batch | With no batch the script returns `status: error` — "Batch is required … Ask the student." (exit 1). | *(…)* | The error message itself tells the agent to ask; the SKILL.md step 1 says never guess the batch. |

### Extra deterministic edge cases (all executed)

| Input | Result |
|---|---|
| `--day Monday` (no batch) | `status: error`, "Batch is required …", exit code 1 |
| `--batch CSE-A` (no day) | `status: error`, "Day is required …", exit code 1 |
| `--batch CSE-C --day Friday` | `status: error`, "Unknown batch 'CSE-C'. Known batches: CSE-A, CSE-B.", exit code 1 |
| `--batch CSE-A --day Funday` | `status: error`, "'Funday' is not a valid day …", exit code 1 |

The same cases (plus a CSV containing instruction-like text, which is returned as plain data) are in `tests/test_timetable.py`.

## Description rewrites and their effect on triggering

The agent sees **only the `name` and `description`** of every installed skill at startup and uses them to decide
whether to load a skill. So the description *is* the trigger.

### Version 0 — the description actually used (balanced)
> Answers student questions about class timetables (which classes, times, rooms and faculty a batch has on a given day, or when and where a course meets) by running a lookup script against the campus timetable CSV. Use when a student asks what classes they have, where or when a course meets, or who teaches it, for batch CSE-A or CSE-B. Do not use for fees, hostel rules, exams or attendance.

It says **what** the skill does, **when** to use it, and **when not to**.

### Version 1 — too broad
> Helps students with campus questions.

*Predicted impact (reasoning, not measured):* it overlaps with almost everything. Prompts 4 and 5 (fees, hostel) and
any general "campus" question could load the skill, wasting context and giving fee/hostel questions to a tool that
cannot answer them. It also tells the agent nothing about the CSV or the script. If you add more skills later, a
broad description steals triggers from them ("skill shadowing").

### Version 2 — too narrow
> Looks up the CSE-A Monday timetable rows from timetable.csv.

*Predicted impact (reasoning, not measured):* it would likely match prompt 1 only. Prompt 2 (CSE-B, Wednesday, by
course), prompt 3 (Saturday) and natural paraphrases like "when is my networks lecture?" may not trigger, so the
anti-fabrication rules never load. The agent might then answer from guesswork — the opposite of what we want.

### What makes a description too broad or too narrow?
- **Too broad:** vague nouns ("campus", "help"), no boundaries, no "do not use" line → false triggers.
- **Too narrow:** hard-coded values (one batch, one day, a file name) or technical wording students never use → missed triggers.
- **Good:** names the task, the typical user words, the allowed scope, and the exclusions, within the 1024-character limit.

### Optional experiment for you (Student to record)
Swap each description into `SKILL.md`, restart Claude Code, run prompts 1-6 again, and note which ones trigger.
Only then can you write "observed" instead of "predicted".
