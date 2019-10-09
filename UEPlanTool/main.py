#!/usr/bin/env python3.7
import re
import requests
from icalendar import Calendar, Event, vDatetime

BASE_URL = f"https://e-uczelnia.ue.katowice.pl/wsrest/rest/ical/phz"


class PlanDownloader:
    def __init__(self, planId, dateStart=None, dateEnd=None):
        self.planId = planId
        self.dateStart = dateStart
        self.dateEnd = dateEnd

        # Download and parse
        self.plan = self._download_and_parse()

        # Filter the events
        self.remove_useless_events()
        self.cleanup_groups()
        self.fix_cnti_name()
        self.split_teachers()

    def _download_and_parse(self):
        """Download the plan ics, parse int and convert into a list"""

        # Check if dates are declared and prepare the url
        if self.dateStart is None or self.dateEnd is None:
            url = f"{BASE_URL}/calendarid_{self.planId}.ics"
        else:
            url = f"{BASE_URL}/calendarid_{self.planId}.ics?dataod={self.dateStart}&datado={self.dateEnd}"

        # Parse
        ics = Calendar.from_ical(requests.get(url).text)

        # Convert into a list
        return [
            {
                "summary": str(component.get("summary")).strip(),
                "location": str(component.get("location")).strip(),
                "start": component.get("dtstart").dt,
                "end": component.get("dtend").dt,
            }
            for component in ics.walk()
            if component.name == "VEVENT"
        ]

    def remove_useless_events(self):
        """Filter out the aggregate foreign language event"""

        def determine_if_useful(event):
            return not event["summary"].startswith("Język obcy I, Język obcy II")

        self.plan = filter(determine_if_useful, self.plan)

    def cleanup_groups(self):
        """Remove useless group strings from summary"""

        grp_regex = re.compile(r"\w{1,}_K-ce_19_z_SI_.*(,)?")

        def drop_groups(event):
            event["summary"] = grp_regex.sub("", event["summary"])
            return event

        self.plan = map(drop_groups, self.plan)

    def fix_cnti_name(self):
        """Replace @ with CNTI in location"""

        def fix_name(event):
            event["location"] = event["location"].replace("@", "CNTI")
            return event

        self.plan = map(fix_name, self.plan)

    def split_teachers(self):
        """Split out the teacher name from summary"""

        def teacher_splitter(event):
            split_summary = event["summary"].split("  ")
            event["summary"] = split_summary[0].strip()
            event["teacher"] = split_summary[1].strip()
            return event

        self.plan = map(teacher_splitter, self.plan)

    def printEvents(self):
        """Print all the events grouped by date"""
        events_by_date = {}

        for event in self.plan:
            ev_date = event["start"].strftime("%Y-%m-%d")

            if ev_date not in events_by_date.keys():
                events_by_date[ev_date] = []
            events_by_date[ev_date].append(event)

        for date, events in events_by_date.items():
            print(date)
            for event in events:
                start_time = event["start"].strftime("%H:%M")
                end_time = event["end"].strftime("%H:%M")

                print(
                    f"\t{start_time} - {end_time}\n\t{event['summary']}\n\t{event['teacher']}\n\t{event['location']}\n"
                )
            print()

    def getPlanObject(self):
        """Return a list with all events"""
        return list(self.plan)

    def exportICS(self):
        cal = Calendar()
        cal.add("prodid", "-//ue-plan-tool//")
        cal.add("version", "2.0")

        for event in self.plan:
            ev = Event()
            ev.add("summary", event["summary"])
            ev.add("location", event["location"])
            ev.add("description", event["teacher"])
            ev.add("dtstart", vDatetime(event["start"]))
            ev.add("dtend", vDatetime(event["end"]))
            cal.add_component(ev)

        return cal.to_ical()
