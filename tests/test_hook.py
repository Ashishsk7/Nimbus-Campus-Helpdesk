"""Tests for the PreToolUse hook script (plugins/campus-helpdesk/hooks/scripts/protect-data.sh).

Needs bash and python3 (the hook itself uses python3). Standard library only.
"""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOOK = ROOT / "plugins" / "campus-helpdesk" / "hooks" / "scripts" / "protect-data.sh"


def run_hook(payload, project_dir):
    """Feed `payload` (dict or raw string) to the hook; return (exit_code, stdout, stderr)."""
    raw = payload if isinstance(payload, str) else json.dumps(payload)
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(project_dir))
    done = subprocess.run(["bash", str(HOOK)], input=raw, capture_output=True, text=True, env=env)
    return done.returncode, done.stdout, done.stderr


class ProtectDataHookTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.project = Path(self._tmp.name).resolve()
        (self.project / "data").mkdir()
        (self.project / "docs").mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def event(self, tool, path, **extra):
        data = {"hook_event_name": "PreToolUse", "tool_name": tool,
                "tool_input": {"file_path": path}, "cwd": str(self.project)}
        data.update(extra)
        return data

    def assertDenied(self, tool, path):
        code, out, _ = run_hook(self.event(tool, path), self.project)
        self.assertEqual(code, 0, path)
        decision = json.loads(out)["hookSpecificOutput"]
        self.assertEqual(decision["hookEventName"], "PreToolUse")
        self.assertEqual(decision["permissionDecision"], "deny")
        self.assertTrue(decision["permissionDecisionReason"])

    def assertAllowed(self, tool, path):
        code, out, _ = run_hook(self.event(tool, path), self.project)
        self.assertEqual((code, out), (0, ""), path)

    # --- blocking ---
    def test_blocks_write_to_data_absolute_path(self):
        self.assertDenied("Write", str(self.project / "data" / "timetable.csv"))

    def test_blocks_edit_to_data_relative_path(self):
        self.assertDenied("Edit", "data/fee_status.json")

    def test_blocks_multiedit_to_data(self):
        self.assertDenied("MultiEdit", "data/hostel-rules.md")

    def test_blocks_dotdot_traversal_into_data(self):
        self.assertDenied("Write", "docs/../data/timetable.csv")

    def test_blocks_new_file_inside_data(self):
        self.assertDenied("Write", "data/new_file.csv")

    def test_blocks_case_variant_for_case_insensitive_filesystems(self):
        self.assertDenied("Write", "DATA/timetable.csv")

    def test_blocks_symlink_pointing_into_data(self):
        link = self.project / "docs" / "sneaky"
        try:
            link.symlink_to(self.project / "data")
        except OSError:
            self.skipTest("symlinks not supported here")
        self.assertDenied("Write", "docs/sneaky/timetable.csv")

    # --- allowing ---
    def test_allows_write_to_docs(self):
        self.assertAllowed("Write", "docs/notes.md")

    def test_allows_edit_of_server_code(self):
        self.assertAllowed("Edit", "mcp-server/server.py")

    def test_allows_look_alike_directory_name(self):
        self.assertAllowed("Write", "database/notes.md")   # starts with "data" but is not data/
        self.assertAllowed("Write", "data-notes.md")

    def test_ignores_non_write_tools(self):
        code, out, _ = run_hook({"tool_name": "Read", "tool_input": {"file_path": "data/timetable.csv"},
                                 "cwd": str(self.project)}, self.project)
        self.assertEqual((code, out), (0, ""))

    # --- malformed input: fail closed (exit 2) ---
    def test_malformed_json_blocks(self):
        code, _, err = run_hook("this is not json", self.project)
        self.assertEqual(code, 2)
        self.assertIn("malformed", err)

    def test_empty_input_blocks(self):
        self.assertEqual(run_hook("", self.project)[0], 2)

    def test_json_but_not_an_object_blocks(self):
        self.assertEqual(run_hook("[1, 2, 3]", self.project)[0], 2)

    def test_missing_tool_input_blocks(self):
        self.assertEqual(run_hook({"tool_name": "Write"}, self.project)[0], 2)

    def test_write_without_file_path_blocks(self):
        self.assertEqual(run_hook({"tool_name": "Write", "tool_input": {}, "cwd": str(self.project)},
                                  self.project)[0], 2)

    def test_non_string_file_path_blocks(self):
        self.assertEqual(run_hook({"tool_name": "Edit", "tool_input": {"file_path": 42},
                                   "cwd": str(self.project)}, self.project)[0], 2)


if __name__ == "__main__":
    unittest.main()
