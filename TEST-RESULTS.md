# TEST-RESULTS

Generated on **2026-11-18** in the assistant's Linux sandbox (Python 3.12.3, Git 2.43.0, bash). The command was:

```bash
python3 -m unittest discover -s tests -v
```
Result line from that run: `Ran 41 tests ... OK (skipped=1)`.

## 1. Tests actually executed (by the assistant, in the sandbox)

| File | Tests | Passed | Skipped | Failed |
|---|---|---|---|---|
| `tests/test_hook.py` | 17 | 17 | 0 | 0 |
| `tests/test_server.py` | 10 | 9 | 1 | 0 |
| `tests/test_timetable.py` | 14 | 14 | 0 | 0 |

What these cover (all executed and passing unless listed as skipped):

| Required area | Test(s) |
|---|---|
| Timetable lookup | `test_basic_lookup_returns_sorted_classes`, `test_batch_and_day_are_normalised`, `test_command_line_exit_codes`, `TimetableToolLogicTests.test_returns_classes_for_valid_input` |
| Course filtering | `test_course_filter`, `test_course_filter_with_no_match_is_empty_not_invented` |
| Unknown batch | `test_unknown_batch`, `test_invalid_batch_is_rejected` |
| Invalid day | `test_invalid_day`, `test_invalid_day_is_rejected` |
| Missing batch / day, empty day, bad CSV | `test_missing_batch_and_missing_day`, `test_valid_day_without_classes_is_safe_empty_result`, `test_empty_day_returns_safe_empty_response`, `test_missing_csv_file_reports_error`, `test_csv_with_missing_columns_reports_error` |
| CSV text treated as data | `test_instruction_text_in_csv_is_returned_as_plain_data` |
| Fee lookup | `test_known_ids` |
| Unknown student ID | `test_unknown_id_is_rejected_with_generic_message`, `test_badly_formatted_ids_are_rejected` |
| Hostel resource text loads (file read only) | `test_rules_text_loads` |
| Hook blocks protected writes | `test_blocks_*` (absolute, relative, `..`, new file, MultiEdit, case variant, symlink) |
| Hook allows permitted files | `test_allows_*`, `test_ignores_non_write_tools` |
| Malformed hook input | `test_malformed_json_blocks`, `test_empty_input_blocks`, `test_json_but_not_an_object_blocks`, `test_missing_tool_input_blocks`, `test_write_without_file_path_blocks`, `test_non_string_file_path_blocks` |
| Packaging consistency | `test_plugin_bundled_script_matches_source_skill`, `test_marketplace_copies_match` |

Also executed by hand (not unit tests): the six lookup-script scenarios recorded in `docs/skill-test-matrix.md`, and a
dry run of the Git worktree command sequence in a throwaway repository (output not included).

## 2. Tests that require local execution (your Mac)

| What | Why it was not run here | How |
|---|---|---|
| Re-run the whole suite on macOS | Different OS/Python; you must show your own output | `python3 -m unittest discover -s tests -v` |
| `FastMCPWiringTests.test_server_exposes_two_tools_and_one_resource` | **SKIPPED** — the `mcp` package was not installed (no network in the sandbox) | `pip install -r requirements.txt`, then re-run the suite; it should run instead of skip |
| Hook on macOS (case-insensitive filesystem, system bash 3.2) | Not executed on macOS | the same test command; note any failure honestly |
| Git worktree lab (real conflict, resolution, graph) | Only dry-run elsewhere; you must perform and capture it | `docs/worktree-lab.md` |
| npm registry check for `@nimbus/mcp-skill-bridge` | Sandbox had no network access | `docs/part-d-jsonrpc-evidence.md`, section 7 |

## 3. Tests requiring Claude Code or MCP Inspector (not run by anyone yet)

| What | Tool needed | Where described |
|---|---|---|
| `claude plugin validate`, marketplace add, install, list, uninstall | Claude Code CLI | `docs/part-c-threat-model.md` §4 |
| Hook is really invoked by Claude Code and denies a write to `data/` | Claude Code | §4.4 step 4 |
| `/campus-helpdesk:timetable-check` and Skill triggering for the six prompts (column B of the matrix) | Claude Code + an LLM | `docs/skill-test-matrix.md` |
| Plugin's MCP server starts (`/mcp`) | Claude Code | §4.4 step 2 |
| Real `initialize`/`server/discover`, `tools/list`, `tools/call`, the failure response, resource read | MCP Inspector or raw stdio | `docs/part-d-jsonrpc-evidence.md` §3 |

No result in category 3 exists yet. Do not describe any of them as passed until you have run them and kept the evidence.
