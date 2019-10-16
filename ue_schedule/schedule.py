import re
import json
import requests
import icalendar
import datetime


class Schedule:
    def __init__(self, schedule_id, start_date=None, end_date=None):
        self.base_url = "https://e-uczelnia.ue.katowice.pl/wsrest/rest/ical/phz"
        self.data = None

        self.schedule_id = schedule_id
        self.start_date = start_date
        self.end_date = end_date

    @property
    def url(self):
        if self.start_date and self.end_date:
            return f"{self.base_url}/calendarid_{self.schedule_id}.ics?dataod={self.start_date}&datado={self.end_date}"
        return f"{self.base_url}/calendarid_{self.schedule_id}.ics"

    def fetch(self):
        calendar = icalendar.Calendar.from_ical(requests.get(self.url).text)

        # create a list of events out of the calendar
        data = [
            Event(component)
            for component in calendar.walk()
            if component.name == "VEVENT"
        ]

        # save only relevant events
        self.data = [e for e in data if not e.irrelevant]

    @property
    def events(self):
        if not self.data:
            self.fetch()
        return self.data

    def to_ical(self):
        """Build an iCalendar out of the parsed schedule"""
        if not self.data:
            self.fetch()

        # initialize calendar
        cal = icalendar.Calendar()
        cal.add("prodid", "-//ue-schedule/UE Schedule//PL")
        cal.add("version", "2.0")

        # add event components
        for event in self.data:
            ev = icalendar.Event()
            ev.add("summary", event.name)
            ev.add("location", event.location)
            ev.add("description", event.teacher)
            ev.add("dtstart", icalendar.vDatetime(event.start))
            ev.add("dtend", icalendar.vDatetime(event.end))
            cal.add_component(ev)
        return cal.to_ical()

    def to_json(self):
        if not self.data:
            self.fetch()

        def serialize(o):
            if isinstance(o, datetime.datetime):
                return o.isoformat()

            if isinstance(o, Event):
                return o.__dict__

        return json.dumps(self.data, default=serialize)


class Event:
    def __init__(self, component):
        self.summary = str(component.get("summary")).strip()
        self.location = str(component.get("location")).strip()
        self.start = component.get("dtstart").dt
        self.end = component.get("dtend").dt

        self.name = None
        self.teacher = None

        self.filter()

    @property
    def irrelevant(self):
        return self.summary.startswith("Język obcy I, Język obcy II")

    def filter(self):
        # replace @ with CNTI
        self.location = self.location.replace("@", "CNTI")

        # remove groups from summary
        self.summary = re.sub(r"\w{1,}_K-ce_19_z_SI_.*(,)?", "", self.summary)

        # split summary into name and teacher
        self.name, self.teacher = self.summary.split("  ", 1)
