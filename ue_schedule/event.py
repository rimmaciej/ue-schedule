import re
from datetime import datetime, timedelta
from typing import Optional

from icalendar import Event as CalEvent  # type: ignore
from pytz import timezone


class Event:
    """
    Class representing a single class schedule Event
    """

    name: str
    start: datetime
    end: datetime
    type: Optional[str]
    teacher: Optional[str]
    location: Optional[str]

    def __init__(
        self,
        name: str,
        type: Optional[str],
        teacher: Optional[str],
        location: Optional[str],
        start: datetime,
        end: datetime,
    ):
        self.name = name
        self.type = type
        self.teacher = teacher
        self.start = start
        self.end = end
        self.location = location

    @classmethod
    def from_calendar(cls, component: CalEvent) -> "Event":
        """
        Initialize Event object

        :param component: calendar event component
        """
        # Get location from the calendar event replace @ with CNTI, set as None if no location
        location: Optional[str] = str(component.get("location")).strip()
        if location:
            location = location.replace("@", "CNTI")
        location = None if location == "brak lokalizacji brak sali" else location

        # Normalize start and end time to Europe/Warsaw timezone
        tz = timezone("Europe/Warsaw")
        start: datetime = tz.normalize(tz.localize(component.get("dtstart").dt))
        end: datetime = tz.normalize(tz.localize(component.get("dtend").dt))

        # fix the finish time of 1.5h or 2.25h events
        # subtract 10 min break pointlessly included in original schedule
        duration = end - start
        if duration == timedelta(minutes=100) or duration == timedelta(minutes=155):
            end -= timedelta(minutes=10)

        # remove groups from summary
        summary = re.sub(r"\w{1,}_K-ce.*(,)?", "", str(component.get("summary")).strip())

        # split summary into name and teacher
        split_summary = summary.strip().split("  ")

        teacher: Optional[str]

        if len(split_summary) > 1:
            teacher = split_summary.pop().strip()

            if teacher.startswith("_K-ce"):
                teacher = split_summary.pop().strip()

            # set teacher to none if not specified
            teacher = None if teacher == "brak nauczyciela" else teacher
            name = (" ".join(split_summary)).strip()
        else:
            teacher = None
            name = split_summary[0]

        name = name.replace("brak nauczyciela", "").replace("brak lokalizacji brak sali", "")

        # split out event type from name
        split_name = name.strip().split(" - ")

        type: Optional[str]

        if len(split_name) > 1:
            name = split_name[0].strip()
            type = split_name[1].strip()
        else:
            type = None

        return cls(name, type, teacher, location, start, end)
