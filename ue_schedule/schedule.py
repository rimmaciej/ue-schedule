"""
This module handles class schedule objects
"""

import json
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Set

import requests
import urllib3  # type: ignore
from icalendar import Calendar  # type: ignore
from icalendar import Event as CalEvent  # type: ignore
from icalendar.prop import vDatetime  # type: ignore

from .event import Event, EventType
from .exceptions import InvalidIdError, WrongResponseError, WUTimeoutError

# Suppress only the single warning from urllib3 needed.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Schedule:
    """
    Describes an object containing a class schedule
    """

    base_url = "https://e-uczelnia.ue.katowice.pl/wsrest/rest/ical/phz"
    events: List[Event] = []  # schedule events

    schedule_id: str  # id of the schedule
    first_day: date  # first date in fetched events
    last_day: date  # last date in fetched events
    offset_time: bool  # should the event end times be fixed

    def __init__(self, schedule_id: str, offset_time: bool = False) -> None:
        """
        Initialize Schedule object

        :param schedule_id: class schedule id
        """
        self.schedule_id = schedule_id
        self.offset_time = offset_time

    @property
    def _url(self) -> str:
        """
        Direct url to .ics file in Wirtualna Uczelnia
        """
        return f"{self.base_url}/calendarid_{self.schedule_id}.ics"

    def fetch_events(self, timeout: int = 5) -> None:
        """
        Fetch events from Wirtualna Uczelnia

        :param timeout: request timeout passed to requests.get

        :raises InvalidIdError: when the id might be wrong
        :raises WUTimeoutError: when the request to WU times out
        :raises WrongResponseError: when the response returned by WU can't be parsed
        """

        try:
            response = requests.get(self._url, timeout=timeout)
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            if response.status_code in (400, 404):
                raise InvalidIdError(error) from error
            raise

        except requests.exceptions.ConnectTimeout as error:
            raise WUTimeoutError(error) from error

        try:
            calendar: Calendar = Calendar.from_ical(response.text)
        except ValueError as error:
            raise WrongResponseError(error) from error

        # create a list of events out of the calendar
        self.events = [
            Event.from_calendar(component, self.offset_time)
            for component in calendar.walk()
            if component.name == "VEVENT"
        ]

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

    def dump_json(self) -> str:
        """
        Dump as list of events encoded in json

        :returns: a json string
        """
        return json.dumps(self.events, default=Schedule.serialize_json)

    def from_json(self, events_json: str) -> None:
        """
        Load events from a json string

        :param events_json: a json string with a list of events
        """
        events = [
            Event(
                name=evt["name"],
                type=evt["type"],
                teacher=evt["teacher"],
                location=evt["location"],
                start=datetime.fromisoformat(evt["start"]),
                end=datetime.fromisoformat(evt["end"]),
                groups=evt["groups"],
            )
            for evt in json.loads(events_json)
        ]

        self.load_events(events)

    def get_events(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
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

        response: List[Dict[str, Any]] = []

        for offset in range((end_date - start_date).days + 1):  # type: ignore
            day: date = start_date + timedelta(days=offset)  # type: ignore
            response.append({"date": day, "events": []})

        for event in self.events:
            event_date: date = event.start.date()

            if event.name.startswith("Język obcy I, Język obcy II"):
                continue

            if "wychowanie fizyczne" in event.name.lower():
                duplicates = [
                    e
                    for e in self.events
                    if (e is not event and e.start == event.start and e.end == event.end)
                ]

                if len(duplicates) > 0 and not event.teacher and not event.location:
                    if duplicates[0].teacher or duplicates[0].location:
                        continue

            if event_date in [d["date"] for d in response]:
                next(day for day in response if day["date"] == event_date)["events"].append(event)

        return response

    def get_json(self, start_date: date = None, end_date: date = None) -> str:
        """
        Get the schedule as json

        :param start_date: Schedule start date - optional, defaults to schedule start date
        :param end_date: Schedule end date - optional, defaults to schedule end date

        :return: schedule json string
        """
        schedule = self.get_events(start_date, end_date)
        return self.format_as_json(schedule)

    def to_ical(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> bytes:
        """
        Get the schedule as iCalendar file

        :param start_date: Schedule start date - optional, defaults to schedule start date
        :param end_date: Schedule end date - optional, defaults to schedule end date
        :returns: ics file
        """
        schedule = self.get_events(start_date, end_date)
        return self.format_as_ical(schedule)

    @property
    def groups(self) -> Set[str]:
        """
        All groups in this schedule

        :returns: A set of group names
        """
        return {group for event in self.events for group in event.groups}

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
                cal_event = CalEvent()
                cal_event.add("summary", f"{event.name} - {event.type}")

                if event.location:
                    cal_event.add("location", event.location)

                if event.teacher:
                    cal_event.add("description", event.teacher)

                cal_event.add("dtstart", vDatetime(event.start))
                cal_event.add("dtend", vDatetime(event.end))
                cal.add_component(cal_event)

        return cal.to_ical()

    @staticmethod
    def serialize_json(obj: Any) -> Any:
        """
        Serialize function for json.dumps

        Convert date and datetime to isoformat string
        Convert Event object to its dict representation

        :param o: object to serialize
        :returns: serialized object string
        """
        if isinstance(obj, datetime):
            return obj.isoformat()

        if isinstance(obj, date):
            return obj.isoformat()

        if isinstance(obj, EventType):
            return obj.name

        if isinstance(obj, Event):
            return obj.__dict__

    @staticmethod
    def format_as_json(events: List[dict]) -> str:
        """
        Format existing schedule to json
        :returns: json string
        """
        return json.dumps(events, default=Schedule.serialize_json, indent=2)
