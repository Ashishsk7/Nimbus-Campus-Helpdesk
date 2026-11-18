"""Nimbus Campus Helpdesk - minimal MCP server (stdio transport, FastMCP).

Run:   python mcp-server/server.py          (normally launched by an MCP client)
Debug: mcp dev mcp-server/server.py         (opens the MCP Inspector; needs mcp[cli])

IMPORTANT for stdio servers: never print() to stdout - stdout carries the JSON-RPC
messages. Use stderr (print(..., file=sys.stderr)) for any debug output.
"""
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field

import campus_data  # sits next to this file; Python puts the script's folder on sys.path

# The name here is the server identifier clients see during initialization.
mcp = FastMCP("nimbus-campus-helpdesk")


@mcp.tool()
def get_timetable(
    batch: Annotated[str, Field(description="Student batch. Allowed values: CSE-A or CSE-B.")],
    day: Annotated[str, Field(description="Weekday name, Monday to Sunday (short forms like Mon accepted).")],
) -> dict:
    """Get the class timetable for one batch on one day from the MOCK campus timetable.

    Returns the classes in time order (start_time, end_time, course_code, course_name,
    room, faculty). If the batch has no classes that day, returns an empty list with a
    message. Read-only. Does not return fees, hostel or exam information.
    """
    return campus_data.get_timetable_data(batch, day)


@mcp.tool()
def get_fee_status(
    student_id: Annotated[str, Field(description="Mock student id in the form STU1234, e.g. STU1001.")],
) -> dict:
    """Get the MOCK fee payment status for one student id.

    Returns status (PAID, PARTIAL or OVERDUE), amount_due and last_payment_date.
    Only the mock ids STU1001, STU1002 and STU1003 exist. Unknown ids are rejected.
    Read-only. Does not change any record.
    """
    return campus_data.get_fee_status_data(student_id)


@mcp.resource("hostel://rules", name="hostel-rules",
              description="Mock hostel rules document (curfew, visitors, quiet hours, mess timings).",
              mime_type="text/markdown")
def hostel_rules() -> str:
    """Return the hostel rules document."""
    return campus_data.read_hostel_rules()


if __name__ == "__main__":
    mcp.run(transport="stdio")
