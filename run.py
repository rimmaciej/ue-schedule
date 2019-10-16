#!/usr/bin/env python3.7
import sys
from ue_schedule import Schedule

# Initialization
if len(sys.argv) < 4:
    print(
        "Usage: python test.py <studentId> <start date YYYY-MM-DD> <end date YYYY-MM-DD> -flags"
    )
    sys.exit(1)

studentId = sys.argv[1]
startDate = sys.argv[2]
endDate = sys.argv[3]

# Initialize the downloader
schedule = Schedule(studentId, startDate, endDate)

# Display all the events
for event in schedule.events:
    start = event.start.strftime("%H:%M")
    end = event.end.strftime("%H:%M")

    print(f"{start} {end}\n{event.name}\n{event.teacher}\n")
