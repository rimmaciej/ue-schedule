#!/usr/bin/env python3.7
import sys
from UESchedule import ScheduleDownloader

# Initialization
if len(sys.argv) < 4:
    print(
        "Usage: python test.py <studentId> <start date YYYY-MM-DD> <end date YYYY-MM-DD>"
    )
    sys.exit(1)

studentId = sys.argv[1]
startDate = sys.argv[2]
endDate = sys.argv[3]

p = ScheduleDownloader(studentId, startDate, endDate)

# Output
with open("plan.ics", "wb") as f:
    f.write(p.exportICS())
    print("Saved to plan.ics")
