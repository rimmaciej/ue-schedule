import re

import icalendar
import requests


class Schedule():
    data = {}
    ics = None

    def __init__(self, config):
        self.config = config

    def fetch(self):
        self.data = requests.get(self.config.schedule_url).text

    def to_ics(self):
        if not self.data:
            self.fetch()
        self.ics = icalendar.Calendar.from_ical(self.data)
        return self.ics

    def events(self):
        if not self.ics:
            self.to_ics()

        return self.filter_events(self.ics.walk())

    def filter_events(self, components):
        result = []
        for component in components:
            if component.name != "VEVENT":
                continue

            event = Event(component)
            if event.irrelevant:
                continue

            result.append(event)

        return result

    def build_ics(self):
        # initialize Calendar and set required parameters
        cal = icalendar.Calendar()
        cal.add("prodid", "-//ue-plan-tool//UE Plan//PL")
        cal.add("version", "2.0")
        return cal


class Event():
    data = {}
    modifiers = ('groups', 'cnti', 'teachers')

    def __init__(self, data):
        self.data = self.from_ics(data)

        for m in self.modifiers:
            getattr(self, "modify_%s" % m)()

    def from_ics(self, evt):
        return {
            "summary": str(evt.get("summary")).strip(),
            "location": str(evt.get("location")).strip(),
            "start": evt.get("dtstart").dt,
            "end": evt.get("dtend").dt
        }

    def to_ics(self):
        data = self.data

        ev = icalendar.Event()
        ev.add("summary", data["summary"])
        ev.add("location", data["location"])
        ev.add("description", data["teacher"])
        ev.add("dtstart", icalendar.vDatetime(data["start"]))
        ev.add("dtend", icalendar.vDatetime(data["end"]))

        return ev

    @property
    def irrelevant(self):
        """Filter out the aggregate foreign language event"""
        return self.data["summary"].startswith("Język obcy I, Język obcy II")

    def modify_groups(self):
        """Remove useless group strings from summary"""
        grp_regex = re.compile(r"\w{1,}_K-ce_19_z_SI_.*(,)?")
        self.data["summary"] = grp_regex.sub("", self.data["summary"])

    def modify_cnti(self):
        """Replace @ with CNTI in location"""
        self.data["location"] = self.data["location"].replace("@", "CNTI")

    def modify_teachers(self):
        """Split out the teacher name from summary"""
        split_summary = self.data["summary"].split("  ")
        self.data["summary"] = split_summary[0].strip()
        self.data["teacher"] = split_summary[1].strip()
