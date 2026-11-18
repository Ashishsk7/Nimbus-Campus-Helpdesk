---
description: Check a batch's timetable for one day using the timetable-helper Skill (e.g. "CSE-A Monday")
---

The user typed this command followed by a batch and a day (for example `CSE-A Monday`).

1. Take the batch and day from what the user typed after the command. If either is missing, ask for it and stop.
2. Use the `timetable-helper` Skill. Run its lookup script for that batch and day.
3. Answer only from the script's JSON output. Never invent a class, time, room or teacher.
4. If the script reports an error or no classes, say so plainly.
