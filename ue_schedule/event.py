"""
This module handles class schedule events
"""

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional

from icalendar import Event as CalEvent  # type: ignore
from pytz import timezone

GROUP_REGEX = re.compile(r"([A-Z]*_K-ce.*,?)")


class EventType(Enum):
    """
    Enum describing types of events in the schedule
    """

    WYKLAD = 1
    CWICZENIA = 2
    LABORATORIUM = 3
    LEKTORAT = 4
    SEMINARIUM = 5
    WF = 6
    INNY = 7


@dataclass(frozen=True, order=True)
class Event:
    """
    Class representing a single class schedule Event
    """

    name: str
    start: datetime
    end: datetime
    type: EventType
    teacher: Optional[str] = None
    location: Optional[str] = None
    groups: List[str] = field(default_factory=list)

    @staticmethod
    def from_calendar(component: CalEvent, offset_time: bool = False) -> "Event":
        """
        Create an Event from a calendar event

        :param component: calendar event component
        :param offset_time: apply a time offset to 100 and 155 minute events

        :returns: Event instance
        """

        # Get location from the calendar event replace @ with CNTI, set as None if no location
        location: Optional[str] = str(component.get("location")).strip()
        if location:
            location = location.replace("@", "CNTI")
        location = None if location == "brak lokalizacji brak sali" else location

        # Normalize start and end time to Europe/Warsaw timezone
        polish_tz = timezone("Europe/Warsaw")
        start: datetime = polish_tz.normalize(polish_tz.localize(component.get("dtstart").dt))
        end: datetime = polish_tz.normalize(polish_tz.localize(component.get("dtend").dt))

        if offset_time:
            # fix the finish time of 1.5h or 2.25h events
            # subtract 10 min break pointlessly included in original schedule
            duration = end - start
            if duration == timedelta(minutes=100) or duration == timedelta(minutes=155):
                end -= timedelta(minutes=10)

        teacher: Optional[str] = None

        # extract summary
        _summary = str(component.get("summary"))

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
            if "wykład" in _event_type:
                event_type = EventType.WYKLAD
            elif "ćwiczenia" in _event_type:
                event_type = EventType.CWICZENIA
            elif "lab" in _event_type:
                event_type = EventType.LABORATORIUM
            elif "lektorat" in _event_type:
                event_type = EventType.LEKTORAT
            elif "wf" in _event_type:
                event_type = EventType.WF
            elif "seminarium" in name.lower():
                event_type = EventType.SEMINARIUM
            else:
                event_type = EventType.INNY

        elif summary.endswith("brak nauczyciela"):
            teacher = None
            event_type = EventType.INNY
            name = summary.rstrip("brak nauczyciela")

        return Event(name, start, end, event_type, teacher, location, groups)
