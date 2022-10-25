"""
Parser module for UE Katowice
"""
import re
from datetime import datetime
from typing import Optional

import requests
from icalendar import Calendar  # type: ignore
from icalendar import Event as ICalEvent  # type: ignore
from pytz import timezone

from ue_schedule.models.event import Event, EventType
from ue_schedule.models.schedule import Schedule

from .exceptions import InvalidIdError, WrongResponseError, WUTimeoutError

BASE_URL = "https://e-uczelnia.ue.katowice.pl/wsrest/rest/ical/phz"
GROUP_REGEX = re.compile(r"([A-Z]*_K-ce.*,?)")


class UEKatowiceParser:
    """
    Parser for UE Katowice class schedule
    """

    schedule_id: str

    def __init__(self, schedule_id: str):
        self.schedule_id = schedule_id

    @property
    def url(self) -> str:
        """
        Direct url to .ics file in Wirtualna Uczelnia
        """
        return f"{BASE_URL}/calendarid_{self.schedule_id}.ics"

    def _parse_event(self, cal_event: ICalEvent):
        """
        Create an Event from a calendar event

        :param cal_event: calendar event
        :param offset_time: apply a time offset to 100 and 155 minute events

        :returns: Event instance
        """

        # Get location from the calendar event replace @ with CNTI, set as None if no location
        location: Optional[str] = str(cal_event.get("location")).strip()
        if location:
            location = location.replace("@", "CNTI")
        location = None if location == "brak lokalizacji brak sali" else location

        # Normalize start and end time to Europe/Warsaw timezone
        polish_tz = timezone("Europe/Warsaw")
        start: datetime = polish_tz.normalize(polish_tz.localize(cal_event.get("dtstart").dt))
        end: datetime = polish_tz.normalize(polish_tz.localize(cal_event.get("dtend").dt))

        teacher: Optional[str] = None

        # extract summary
        _summary = str(cal_event.get("summary"))

        # extract groups
        _groups = re.search(GROUP_REGEX, _summary)
        summary = re.sub(GROUP_REGEX, "", _summary).strip()
        if _groups:
            groups = [group.strip() for group in _groups[0].split(",")]
        else:
            groups = []

        # remove 'brak nauczyciela' and mark teacher as None
        split = re.split(" - |  ", summary)

        if len(split) >= 3:
            teacher = split.pop().strip()
            _event_type = split.pop().strip().lower()
            name = " ".join(split).strip()

            # Assign enum event types
            if "seminarium" in name.lower():
                event_type = EventType.SEMINARIUM
            elif "egzamin" in name.lower():
                event_type = EventType.EGZAMIN
            elif "wykład" in _event_type:
                event_type = EventType.WYKLAD
            elif "ćwiczenia" in _event_type:
                event_type = EventType.CWICZENIA
            elif "lab" in _event_type:
                event_type = EventType.LABORATORIUM
            elif "lektorat" in _event_type:
                event_type = EventType.LEKTORAT
            elif "wf" in _event_type:
                event_type = EventType.WF
            else:
                event_type = EventType.INNY

        elif summary.endswith("brak nauczyciela"):
            teacher = None
            event_type = EventType.INNY
            name = summary.rstrip("brak nauczyciela")

        return Event(
            name=name,
            start=start,
            end=end,
            type=event_type,
            teacher=teacher,
            location=location,
            groups=groups,
        )

    def fetch(self, timeout: int = 120):
        """
        Fetch the schedule
        """
        try:
            response = requests.get(self.url, timeout=timeout)
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

        events = (
            self._parse_event(component)
            for component in calendar.walk()
            if component.name == "VEVENT"
        )

        # Filter out duplicate language class events
        events = (
            ev for ev in events if not ev.name.lower().startswith("język obcy i, język obcy ii")
        )

        # TODO: Figure out a good way to filter duplicates and other edge cases

        return Schedule(schedule_id=self.schedule_id, events=list(events))
