"""Tests for the MCP server's data logic (mcp-server/campus_data.py).

These run WITHOUT the MCP SDK. The last test checks the real FastMCP wiring and is
skipped automatically if the `mcp` package is not installed.
"""
import asyncio
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "mcp-server"))

import campus_data as cd  # noqa: E402

try:
    import mcp  # noqa: F401
    HAVE_MCP = True
except ImportError:
    HAVE_MCP = False


class TimetableToolLogicTests(unittest.TestCase):
    def test_returns_classes_for_valid_input(self):
        result = cd.get_timetable_data("CSE-B", "Tuesday")
        self.assertEqual(len(result["classes"]), 3)
        self.assertEqual(result["classes"][0]["course_code"], "CS203")

    def test_empty_day_returns_safe_empty_response(self):
        result = cd.get_timetable_data("CSE-A", "Sunday")
        self.assertEqual(result["classes"], [])
        self.assertIn("No classes", result["message"])

    def test_invalid_batch_is_rejected(self):
        with self.assertRaises(ValueError):
            cd.get_timetable_data("CSE-Z", "Monday")

    def test_invalid_day_is_rejected(self):
        with self.assertRaises(ValueError):
            cd.get_timetable_data("CSE-A", "Funday")

    def test_non_string_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            cd.get_timetable_data(123, "Monday")
        with self.assertRaises(ValueError):
            cd.get_timetable_data("CSE-A", None)


class FeeToolLogicTests(unittest.TestCase):
    def test_known_ids(self):
        self.assertEqual(cd.get_fee_status_data("STU1001")["status"], "PAID")
        self.assertEqual(cd.get_fee_status_data("stu1002")["status"], "PARTIAL")
        self.assertEqual(cd.get_fee_status_data("STU1003")["amount_due"], 42000)

    def test_unknown_id_is_rejected_with_generic_message(self):
        with self.assertRaises(ValueError) as ctx:
            cd.get_fee_status_data("STU9999")
        self.assertIn("No fee record", str(ctx.exception))
        self.assertNotIn("STU1001", str(ctx.exception))  # must not leak other ids

    def test_badly_formatted_ids_are_rejected(self):
        for bad in ("", "1001", "STU12", "STU1001; DROP TABLE", "../etc/passwd", None, 1001):
            with self.assertRaises(ValueError, msg=repr(bad)):
                cd.get_fee_status_data(bad)


class HostelResourceTests(unittest.TestCase):
    def test_rules_text_loads(self):
        text = cd.read_hostel_rules()
        self.assertIn("Curfew", text)


@unittest.skipUnless(HAVE_MCP, "mcp package not installed - run `pip install -r requirements.txt`")
class FastMCPWiringTests(unittest.TestCase):
    def test_server_exposes_two_tools_and_one_resource(self):
        import server  # imports mcp.server.fastmcp
        tools = asyncio.run(server.mcp.list_tools())
        self.assertEqual(sorted(t.name for t in tools), ["get_fee_status", "get_timetable"])
        resources = asyncio.run(server.mcp.list_resources())
        self.assertEqual([str(r.uri) for r in resources], ["hostel://rules"])


if __name__ == "__main__":
    unittest.main()
