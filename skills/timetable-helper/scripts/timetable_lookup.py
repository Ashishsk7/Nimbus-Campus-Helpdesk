#!/usr/bin/env python3
"""Deterministic timetable lookup for the timetable-helper Skill.

Usage:
    python3 timetable_lookup.py --batch CSE-A --day Monday
    python3 timetable_lookup.py --batch CSE-B --day wed --course CS204
    python3 timetable_lookup.py --csv path/to/timetable.csv --batch CSE-A --day Friday

It prints ONE JSON object on stdout.
Exit code: 0 = ok or "no classes", 1 = bad input or unreadable data.
The CSV is treated purely as DATA: cells are copied into JSON and never interpreted.
Standard library only (no pip install needed).
"""
import argparse
import csv
import json
import sys
from pathlib import Path

REQUIRED_COLUMNS = ["batch", "day", "start_time", "end_time",
                    "course_code", "course_name", "room", "faculty"]

# Accepts full names and short forms, any capitalisation.
DAY_ALIASES = {
    "mon": "Monday", "monday": "Monday",
    "tue": "Tuesday", "tues": "Tuesday", "tuesday": "Tuesday",
    "wed": "Wednesday", "wednesday": "Wednesday",
    "thu": "Thursday", "thur": "Thursday", "thurs": "Thursday", "thursday": "Thursday",
    "fri": "Friday", "friday": "Friday",
    "sat": "Saturday", "saturday": "Saturday",
    "sun": "Sunday", "sunday": "Sunday",
}

# Default CSV location: data/timetable.csv relative to the current directory
# (run the script from the project root, or pass --csv).
DEFAULT_CSV = Path("data") / "timetable.csv"


def error(message, **extra):
    """Build a uniform error result."""
    result = {"status": "error", "message": message}
    result.update(extra)
    return result


def normalize_day(day):
    """Return a canonical day name, or None if the text is not a day."""
    if not isinstance(day, str):
        return None
    return DAY_ALIASES.get(day.strip().lower())


def normalize_batch(batch, known_batches):
    """Match 'cse a', 'cse_a', 'CSE-A' ... to a known batch. Return None if unknown."""
    if not isinstance(batch, str) or not batch.strip():
        return None
    cleaned = batch.strip().upper().replace("_", "-").replace(" ", "-")
    return cleaned if cleaned in known_batches else None


def load_rows(csv_path):
    """Read the CSV. Raises ValueError with a readable message if it is unusable."""
    path = Path(csv_path)
    if not path.is_file():
        raise ValueError(f"Timetable file not found: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"Timetable CSV is missing columns: {', '.join(missing)}")
        return [row for row in reader]


def lookup(batch, day, course=None, csv_path=DEFAULT_CSV):
    """Core logic (also imported by the unit tests). Returns a dict, never raises."""
    if batch is None or not str(batch).strip():
        return error("Batch is required (for example CSE-A or CSE-B). Ask the student.")
    if day is None or not str(day).strip():
        return error("Day is required (Monday to Sunday). Ask the student.")

    try:
        rows = load_rows(csv_path)
    except (ValueError, OSError, csv.Error, UnicodeDecodeError) as exc:
        return error(f"Could not read timetable data: {exc}")

    known_batches = sorted({(row["batch"] or "").strip().upper() for row in rows})
    clean_batch = normalize_batch(batch, set(known_batches))
    if clean_batch is None:
        return error(f"Unknown batch '{batch}'. Known batches: {', '.join(known_batches)}.",
                     known_batches=known_batches)

    clean_day = normalize_day(day)
    if clean_day is None:
        return error(f"'{day}' is not a valid day. Use Monday to Sunday "
                     "(short forms like Mon are fine).")

    matches = [row for row in rows
               if (row["batch"] or "").strip().upper() == clean_batch
               and (row["day"] or "").strip() == clean_day]

    if course:
        wanted = str(course).strip().upper()
        matches = [row for row in matches
                   if (row["course_code"] or "").strip().upper() == wanted]

    matches.sort(key=lambda row: row["start_time"] or "")
    classes = [{key: row[key] for key in REQUIRED_COLUMNS[2:]} for row in matches]

    if not classes:
        return {"status": "no_classes", "batch": clean_batch, "day": clean_day,
                "course_filter": course, "classes": [],
                "message": "No matching classes in the timetable CSV. Do not invent one."}
    return {"status": "ok", "batch": clean_batch, "day": clean_day,
            "course_filter": course, "classes": classes}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Look up classes in the campus timetable CSV.")
    parser.add_argument("--batch", help="Batch name, e.g. CSE-A")
    parser.add_argument("--day", help="Day name, e.g. Monday or Mon")
    parser.add_argument("--course", help="Optional course code filter, e.g. CS204")
    parser.add_argument("--csv", default=str(DEFAULT_CSV), help="Path to timetable.csv")
    args = parser.parse_args(argv)

    result = lookup(args.batch, args.day, args.course, args.csv)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if result["status"] == "error" else 0


if __name__ == "__main__":
    sys.exit(main())
