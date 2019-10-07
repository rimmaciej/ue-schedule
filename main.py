#!/usr/bin/env python3.7
import re
import requests
from icalendar import Calendar, Event

from config import PLAN_ID, START_DATE, END_DATE

# Prepare the url
url = f"https://e-uczelnia.ue.katowice.pl/wsrest/rest/ical/phz/calendarid_{PLAN_ID}.ics"
if START_DATE and END_DATE:
    url += f"?dataod={START_DATE}&datado={END_DATE}"

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

events = sorted(events, key=lambda event: event["dtstart"])

events_by_date = {}

for event in events:
    ev_date = event["dtstart"].strftime("%Y-%m-%d")

    if ev_date not in events_by_date.keys():
        events_by_date[ev_date] = []
    events_by_date[ev_date].append(event)

for date, events in events_by_date.items():
    print(date)
    for event in events:
        start_time = event["dtstart"].strftime("%H:%M")
        print(f"\t{start_time} {event['summary']} - {event['location']}")
    print()
