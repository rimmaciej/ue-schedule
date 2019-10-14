#!/usr/bin/env python3.7
import sys
from UESchedule import ScheduleDownloader

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
sd = ScheduleDownloader(studentId)

# Download the schedule
schedule = sd.download(startDate, endDate)

# Run filters on the schedule
schedule.run_filters()

# Output

# Checks if flags are present
if len(sys.argv) == 5:
    # Save to json
    if sys.argv[4] == "-j":
        with open("plan.json", "w") as f:
            # Output to json and save it to a file
            f.write(schedule.to_json())
            print("Saved to plan.json")
else: 
    # Defaults to ics
    with open("plan.ics", "wb") as f:
        # Output to ics and save it to a file
        f.write(schedule.to_ics())
        print("Saved to plan.ics")