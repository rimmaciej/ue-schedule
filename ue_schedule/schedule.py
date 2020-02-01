import re
import json
import requests
import icalendar
import pytz
import datetime


class Schedule:
    def __init__(self, schedule_id):
        self.base_url = "https://e-uczelnia.ue.katowice.pl/wsrest/rest/ical/phz"

        self.events = None  # schedule events
        self.first_day = None  # first date in fetched events
        self.last_day = None  # last date in fetched events

        self.schedule_id = schedule_id

    @property
    def _url(self):
        return f"{self.base_url}/calendarid_{self.schedule_id}.ics"

    def fetch_events(self):
        """Fetch events"""
        calendar = icalendar.Calendar.from_ical(requests.get(self._url).text)

        # create a list of events out of the calendar
        events = [
            Event(component)
            for component in calendar.walk()
            if component.name == "VEVENT"
        ]

        self.first_day = min(events, key=lambda e: e.start).start.date()
        self.last_day = max(events, key=lambda e: e.start).start.date()

        # save only relevant events
        self.events = [e for e in events if not e.irrelevant]

    def load_events(self, events):
        """Load events from existing object"""
        self.first_day = min(events, key=lambda e: e.start).start.date()
        self.last_day = max(events, key=lambda e: e.start).start.date()
        self.events = events

    def dump_events(self):
        """Dump events for loading later"""
        return self.events

    def get_events(self, start_date=None, end_date=None):
        """Get nested events as a dict"""
        if not self.events:
            self.fetch_events()

        if not (start_date and end_date):
            start_date = self.first_day
            end_date = self.last_day

        nested = dict()

        for offset in range((end_date - start_date).days + 1):
            day = start_date + datetime.timedelta(days=offset)
            nested[day] = []

        for event in self.events:
            date = event.start.date()

            if "wychowanie fizyczne" in event.summary.lower():
                duplicates = [e for e in self.events if (e is not event and e.start == event.start and e.end == event.end)]

                if len(duplicates) > 0 and not event.teacher and not event.location:
                    if duplicates[0].teacher or duplicate[0].location:
                        continue

            if date in nested.keys():
                nested[date].append(event)

        return nested

    def get_json(self, start_date=None, end_date=None):
        """Get events as json"""
        events = self.get_events(start_date, end_date)

        events = {day.isoformat(): events for (day, events) in events.items()}

        def serialize(o):
            if isinstance(o, datetime.datetime):
                return o.isoformat()

            if isinstance(o, datetime.date):
                return o.isoformat()

            if isinstance(o, Event):
                return o.__dict__

        return json.dumps(events, default=serialize)

    def get_ical(self, start_date=None, end_date=None):
        """Get iCalendar out of the parsed schedule"""
        events = self.get_events(start_date, end_date)

        # initialize calendar
        cal = icalendar.Calendar()
        cal.add("prodid", "-//ue-schedule/UE Schedule//PL")
        cal.add("version", "2.0")
        # add event components
        for event_list in events.values():

            for event in event_list:
                ev = icalendar.Event()
                ev.add("summary", event.name)

                if event.location:
                    ev.add("location", event.location)

                if event.teacher:
                    ev.add("description", event.teacher)

                ev.add("dtstart", icalendar.vDatetime(event.start))
                ev.add("dtend", icalendar.vDatetime(event.end))
                cal.add_component(ev)
        return cal.to_ical()


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
        language_block = self.summary.startswith("Język obcy I, Język obcy II")
        return language_block

    def filter(self):
        # replace @ with CNTI
        self.location = self.location.replace("@", "CNTI")

        # remove groups from summary
        self.summary = re.sub(r"\w{1,}_K-ce.*(,)?", "", self.summary)

        # split summary into name and teacher
        split_summary = self.summary.strip().split("  ")

        if len(split_summary) > 1:
            self.teacher = split_summary.pop().strip()
            if self.teacher.startswith("_K-ce"):
                self.teacher = split_summary.pop().strip()
                
            self.name = (" ".join(split_summary)).strip()
        else:
            self.teacher = None
            self.name = split_summary[0]

        # fix the finish time of 1.5h events
        # if it's 1h 40min, subtract 10 min
        duration = self.end - self.start
        if duration == datetime.timedelta(minutes=100):
            self.end -= datetime.timedelta(minutes=10)

        # fix finish time of 2.25h events
        if duration == datetime.timedelta(minutes=145):
            self.end -= datetime.timedelta(minutes=10)

        # set location to none if not specified
        if self.location == "brak lokalizacji brak sali":
            self.location = None

        # set teacher to none if not specified
        if self.teacher == "brak nauczyciela":
            self.teacher = None

        # drop 'brak nauczyciela' and 'brak lokalizacji brak sali' from name if it persists
        self.name = self.name.replace("brak nauczyciela", "").replace("brak lokalizacji brak sali", "")