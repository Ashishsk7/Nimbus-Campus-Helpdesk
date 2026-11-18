"""Pure-Python data logic for the Nimbus MCP server (no MCP SDK needed here).

Keeping the logic separate from server.py means the unit tests can run even on a
machine where the `mcp` package is not installed yet. server.py is a thin wrapper.
All data is MOCK data stored under <project>/data/.
"""
import csv
import json
import re
from pathlib import Path

DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "data"

VALID_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
VALID_BATCHES = ["CSE-A", "CSE-B"]
STUDENT_ID_PATTERN = re.compile(r"^STU\d{4}$")  # e.g. STU1001


def validate_batch(batch):
    """Return the canonical batch name or raise ValueError."""
    if not isinstance(batch, str):
        raise ValueError("batch must be text such as 'CSE-A'.")
    cleaned = batch.strip().upper().replace("_", "-").replace(" ", "-")
    if cleaned not in VALID_BATCHES:
        raise ValueError(f"Unknown batch '{batch[:30]}'. Valid batches: {', '.join(VALID_BATCHES)}.")
    return cleaned


def validate_day(day):
    """Return the canonical day name or raise ValueError."""
    if not isinstance(day, str):
        raise ValueError("day must be text such as 'Monday'.")
    for name in VALID_DAYS:
        if day.strip().lower() in (name.lower(), name[:3].lower()):
            return name
    raise ValueError(f"'{day[:30]}' is not a valid day. Use Monday to Sunday.")


def validate_student_id(student_id):
    """Return the canonical student id or raise ValueError (format check only)."""
    if not isinstance(student_id, str):
        raise ValueError("student_id must be text such as 'STU1001'.")
    cleaned = student_id.strip().upper()
    if not STUDENT_ID_PATTERN.match(cleaned):
        raise ValueError("student_id must look like STU followed by 4 digits, e.g. STU1001.")
    return cleaned


def get_timetable_data(batch, day, data_dir=None):
    """Return {'batch','day','classes':[...],'message'?}. Empty list = no classes."""
    clean_batch = validate_batch(batch)
    clean_day = validate_day(day)
    path = Path(data_dir or DEFAULT_DATA_DIR) / "timetable.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        rows = [r for r in csv.DictReader(handle)
                if r["batch"].strip().upper() == clean_batch and r["day"].strip() == clean_day]
    rows.sort(key=lambda r: r["start_time"])
    classes = [{k: r[k] for k in ("start_time", "end_time", "course_code",
                                  "course_name", "room", "faculty")} for r in rows]
    result = {"batch": clean_batch, "day": clean_day, "classes": classes}
    if not classes:
        result["message"] = "No classes found in the timetable data for this batch and day."
    return result


def get_fee_status_data(student_id, data_dir=None):
    """Return mock fee info for a known id. Unknown ids raise a generic ValueError."""
    clean_id = validate_student_id(student_id)
    path = Path(data_dir or DEFAULT_DATA_DIR) / "fee_status.json"
    students = json.loads(path.read_text(encoding="utf-8")).get("students", {})
    if clean_id not in students:
        # Generic message: do not reveal which ids exist.
        raise ValueError("No fee record found for that student id.")
    return {"student_id": clean_id, **students[clean_id]}


def read_hostel_rules(data_dir=None):
    """Return the text of the mock hostel rules document."""
    return (Path(data_dir or DEFAULT_DATA_DIR) / "hostel-rules.md").read_text(encoding="utf-8")
