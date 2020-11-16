import json
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

import requests
import urllib3
from icalendar import Calendar
from icalendar import Event as CalEvent
from icalendar.prop import vDatetime

from .event import Event
from .exceptions import ScheduleFetchError, WUDeadError

# Suppress only the single warning from urllib3 needed.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Schedule:
    """
    Describes an object containing a class schedule
    """

    first_day: date  # first date in fetched events
    last_day: date  # last date in fetched events

    def __init__(self, schedule_id: int) -> None:
        """
        Initialize Schedule object

        :param schedule_id: class schedule id
        """
        self.base_url: str = "https://e-uczelnia.ue.katowice.pl/wsrest/rest/ical/phz"
        self.events: List[Event] = []  # schedule events
        self.schedule_id: int = schedule_id

    @property
    def _url(self) -> str:
        """
        Direct url to .ics file in Wirtualna Uczelnia
        """
        return f"{self.base_url}/calendarid_{self.schedule_id}.ics"

    def fetch_events(self, timeout: int = 5) -> None:
        """
        Fetch events from Wirtualna Uczelnia
        """

        try:
            calendar: Calendar = Calendar.from_ical(requests.get(self._url, verify=False, timeout=timeout).text)  # type: ignore
        except requests.exceptions.ConnectTimeout as e:
            raise WUDeadError(e)
        except Exception as e:
            raise ScheduleFetchError(e)

        # create a list of events out of the calendar
        self.events = [Event(component) for component in calendar.walk() if component.name == "VEVENT"]

        self.first_day = min(self.events, key=lambda e: e.start).start.date()
        self.last_day = max(self.events, key=lambda e: e.start).start.date()

    def load_events(self, events: List[Event]) -> None:
        """
        Load events from existing object
        :param events: List of events
        """
        self.first_day = min(events, key=lambda e: e.start).start.date()
        self.last_day = max(events, key=lambda e: e.start).start.date()
        self.events = events

    def dump_events(self) -> List[Event]:
        """
        Dump as list of events, available for loading later with load_events

        :returns: a list of events
        """
        return self.events

    def get_events(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """
        Get events as a list of objects

        :param start_date: Schedule start date - optional, defaults to schedule start date
        :param end_date: Schedule end date - optional, defaults to schedule end date

        :returns: A list of dictionaries representing days
        """

        # Fetch if events not loaded
        if not self.events:
            self.fetch_events()

        if not (start_date and end_date):
            start_date = self.first_day
            end_date = self.last_day

        response: List[Dict[str, Any]] = list()

        for offset in range((end_date - start_date).days + 1):  # type: ignore
            day: date = start_date + timedelta(days=offset)  # type: ignore
            response.append({"date": day, "events": []})

        for event in self.events:
            event_date: date = event.start.date()

            if event.name.startswith("Język obcy I, Język obcy II"):
                continue

            if "wychowanie fizyczne" in event.name.lower():
                duplicates = [
                    e for e in self.events if (e is not event and e.start == event.start and e.end == event.end)
                ]

                if len(duplicates) > 0 and not event.teacher and not event.location:
                    if duplicates[0].teacher or duplicates[0].location:
                        continue

            if event_date in [d["date"] for d in response]:
                next(day for day in response if day["date"] == event_date)["events"].append(event)

        return response

    @staticmethod
    def format_as_json(events: List[dict]) -> str:
        """
        Format existing schedule to json
        :returns: json string
        """

        def serialize(o: Any) -> Any:
            """
            Serialize function for json.dumps

            Convert date and datetime to isoformat string
            Convert Event object to its dict representation

            :param o: object to serialize
            :returns: serialized object string
            """
            if isinstance(o, datetime):
                return o.isoformat()

            if isinstance(o, date):
                return o.isoformat()

            if isinstance(o, Event):
                return o.__dict__

        return json.dumps(events, default=serialize)

    def get_json(self, start_date: date = None, end_date: date = None) -> str:
        """
        Get the schedule as json

        :param start_date: Schedule start date - optional, defaults to schedule start date
        :param end_date: Schedule end date - optional, defaults to schedule end date

        :return: schedule json string
        """
        schedule = self.get_events(start_date, end_date)
        return self.format_as_json(schedule)

    @staticmethod
    def format_as_ical(events: List[dict]) -> bytes:
        """
        Format existing schedule to iCalendar
        :returns: ics file
        """
        # inictialize calendar
        cal = Calendar()
        cal.add("prodid", "-//ue-schedule/UE Schedule//PL")
        cal.add("version", "2.0")

        # add event components
        for day in events:

            for event in day["events"]:
                ev = CalEvent()
                ev.add("summary", f"{event.name} - {event.type}")

                if event.location:
                    ev.add("location", event.location)

                if event.teacher:
                    ev.add("description", event.teacher)

                ev.add("dtstart", vDatetime(event.start))
                ev.add("dtend", vDatetime(event.end))
                cal.add_component(ev)

        return cal.to_ical()

    def get_ical(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> bytes:
        """
        Get the schedule as iCalendar file

        :param start_date: Schedule start date - optional, defaults to schedule start date
        :param end_date: Schedule end date - optional, defaults to schedule end date
        :returns: ics file
        """
        schedule = self.get_events(start_date, end_date)
        return self.format_as_ical(schedule)
