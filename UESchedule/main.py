#!/usr/bin/env python3.7
import re
import requests
import json
from icalendar import Calendar, Event, vDatetime

BASE_URL = f"https://e-uczelnia.ue.katowice.pl/wsrest/rest/ical/phz"


class Schedule:
    """Takes a list with schedule events"""

    def __init__(self, schedule):
        self.schedule = schedule

    def run_filters(self):
        self.schedule = self.remove_useless_events(self.schedule)
        self.schedule = self.split_teachers(self.schedule)
        self.schedule = self.cleanup_groups(self.schedule)
        self.schedule = self.fix_cnti_name(self.schedule)

    def remove_useless_events(self, schedule):
        """Filter out the aggregate foreign language event"""

        def determine_if_useful(event):
            return not event["summary"].startswith("Język obcy I, Język obcy II")

        return filter(determine_if_useful, schedule)

    def cleanup_groups(self, schedule):
        """Remove useless group strings from summary"""
        grp_regex = re.compile(r"\w{1,}_K-ce_19_z_SI_.*(,)?")

        def drop_groups(event):
            event["summary"] = grp_regex.sub("", event["summary"])
            return event

        return map(drop_groups, schedule)

    def fix_cnti_name(self, schedule):
        """Replace @ with CNTI in location"""

        def fix_name(event):
            event["location"] = event["location"].replace("@", "CNTI")
            return event

        return map(fix_name, schedule)

    def split_teachers(self, schedule):
        """Split out the teacher name from summary"""

        def teacher_splitter(event):
            split_summary = event["summary"].split("  ")
            event["summary"] = split_summary[0].strip()
            event["teacher"] = split_summary[1].strip()
            return event

        return map(teacher_splitter, schedule)

    def nest_by_date(self, schedule):
        """Returns schedule with events nested by date"""
        nested = {}

        for event in schedule:
            day = event["start"].strftime("%Y-%m-%d")
            if day not in nested.keys():
                nested[day] = []
            nested[day].append(event)

        return nested

    def to_list(self, nested=False):
        """Return a list with all events"""
        if nested:
            return list(self.nest_by_date(self.schedule))
        return list(self.schedule)

    def to_json(self, nested=False):
        """Build a json file out of parsed plan"""
        if nested:
            schedule = self.nest_by_date(self.schedule)
            return json.dumps(schedule, default=str)
        return json.dumps(list(self.schedule), default=str)

    def print(self):
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

    def to_ics(self):
        """Build an iCalendar out of the parsed plan"""

        # initialize Calendar and set required parameters
        cal = Calendar()
        cal.add("prodid", "-//ue-plan-tool//UE Plan//PL")
        cal.add("version", "2.0")

        # add all events from the plan to the calendar

        for event in self.schedule:
            ev = Event()
            ev.add("summary", event["summary"])
            ev.add("location", event["location"])
            ev.add("description", event["teacher"])
            ev.add("dtstart", vDatetime(event["start"]))
            ev.add("dtend", vDatetime(event["end"]))
            cal.add_component(ev)
        return cal.to_ical()


class ScheduleDownloader:
    def __init__(self, schedule_id):
        self.schedule_id = schedule_id
        self.url = f"{BASE_URL}/calendarid_{self.schedule_id}.ics"

    def download(self, dateStart=None, dateEnd=None):
        """Download the plan ics and pass data to Schedule object"""

        if dateStart and dateEnd:
            url = f"{self.url}?dataod={dateStart}&datado={dateEnd}"
        else:
            url = self.url

        # Parse
        ics = Calendar.from_ical(requests.get(url).text)

        # Convert into a Schedule object
        return Schedule(
            {
                "summary": str(component.get("summary")).strip(),
                "location": str(component.get("location")).strip(),
                "start": component.get("dtstart").dt,
                "end": component.get("dtend").dt,
            }
            for component in ics.walk()
            if component.name == "VEVENT"
        )
