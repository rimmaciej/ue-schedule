import re
from datetime import datetime, timedelta
from typing import Optional

from icalendar import Event as CalEvent
from pytz import timezone


class Event:
    """
    Class representing a single class schedule Event
    """

    def __init__(self, component: CalEvent) -> None:
        """
        Initialize Event object

        :param component: calendar event component
        """

        self.name: str = ""
        self.type: Optional[str] = None
        self.teacher: Optional[str] = None

        # Get location from the calendar event replace @ with CNTI, set as None if no location
        self.location: Optional[str] = str(component.get("location")).strip()
        self.location = self.location.replace("@", "CNTI")
        self.location = None if self.location == "brak lokalizacji brak sali" else self.location

        # Normalize start and end time to Europe/Warsaw timezone
        tz = timezone("Europe/Warsaw")
        self.start: datetime = tz.normalize(tz.localize(component.get("dtstart").dt))
        self.end: datetime = tz.normalize(tz.localize(component.get("dtend").dt))

        # fix the finish time of 1.5h or 2.25h events
        # subtract 10 min break pointlessly included in original schedule
        duration = self.end - self.start
        if duration == timedelta(minutes=100) or duration == timedelta(minutes=155):
            self.end -= timedelta(minutes=10)

        self.parseSummary(str(component.get("summary")).strip())

    def parseSummary(self, summary: str):
        # remove groups from summary
        summary = re.sub(r"\w{1,}_K-ce.*(,)?", "", summary)

        # split summary into name and teacher
        split_summary = summary.strip().split("  ")

        if len(split_summary) > 1:
            self.teacher = split_summary.pop().strip()

            if self.teacher.startswith("_K-ce"):
                self.teacher = split_summary.pop().strip()

            # set teacher to none if not specified
            self.teacher = None if self.teacher == "brak nauczyciela" else self.teacher

            self.name = (" ".join(split_summary)).strip()
        else:
            self.teacher = None
            self.name = split_summary[0]

        self.name = self.name.replace("brak nauczyciela", "").replace("brak lokalizacji brak sali", "")

        # split out event type from name
        split_name = self.name.strip().split(" - ")

        if len(split_name) > 1:
            self.name = split_name[0].strip()
            self.type = split_name[1].strip()
        else:
            self.type = None
