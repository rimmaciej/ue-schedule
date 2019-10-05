#!/usr/bin/env python3.7
import re
import requests
from icalendar import Calendar, Event

# Timetable download url
url = ""

# Regex that matches group string
grp_regex = re.compile(r"\w{1,}_K-ce_19_z_SI_.*(,)?")

# Parse the ics
cal = Calendar.from_ical(requests.get(url).text)


def clean_summary(summary):
    # remove the group string
    return grp_regex.sub("", str(summary))


def fix_location(location):
    # replace @ with CNTI
    return str(location).replace("@", "CNTI")


# Group events into a list
events = [
    {
        "summary": clean_summary(component.get("summary")),
        "location": fix_location(component.get("location")),
        "dtstart": component.get("dtstart").dt,
        "dtend": component.get("dtend").dt,
        "dtstamp": component.get("dtstamp").dt,
    }
    for component in cal.walk()
    if component.name == "VEVENT"
]

events = sorted(events, key=lambda event: (event["summary"], event["dtstart"]))
for event in events:
    print(f"{event['dtstart']} - {event['summary']} - {event['location']}")
