import re
import json
import requests
import icalendar
import pytz
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

    @property
    def nested_events(self):
        if not self.data:
            self.fetch()

        nested = {}

        for event in self.data:
            date = datetime.date(event.start.year, event.start.month, event.start.day)

            if date not in nested.keys():
                nested[date] = []

            nested[date].append(event)

        return nested

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

            if event.location:
                ev.add("location", event.location)

            if event.description:
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

        tz = pytz.timezone("Europe/Warsaw")
        self.start = tz.normalize(tz.localize(component.get("dtstart").dt))
        self.end = tz.normalize(tz.localize(component.get("dtend").dt))

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
        split_summary = self.summary.split("  ", 1)
        self.name = split_summary[0].strip()
        self.teacher = split_summary[1].strip()

        # fix the finish time of 1.5h events
        # if it's 1h 40min, subtract 10 min
        duration = self.end - self.start
        if duration == datetime.timedelta(minutes=100):
            self.end -= datetime.timedelta(minutes=10)

        # set location to none if not specified
        if self.location == "brak lokalizacji brak sali":
            self.location = None

        # set teacher to none if not specified
        if self.teacher == "brak nauczyciela":
            self.teacher = None

