"""
Schedule model definition module
"""
from collections import defaultdict
from datetime import date

from icalendar import Calendar  # type: ignore
from icalendar import Event as ICalEvent  # type: ignore
from icalendar.prop import vDatetime  # type: ignore
from pydantic import BaseModel

from .event import Event


class Schedule(BaseModel):
    """
    Model for a class schedule
    """

    schedule_id: str  # id of the schedule
    events: list[Event] = []  # schedule event

    @property
    def groups(self) -> set[str]:
        """
        All groups in this schedule

        :returns: A set of group names
        """
        return {group for event in self.events for group in event.groups}

    def group_by_day(self) -> dict[date, list[Event]]:
        """
        Schedule events grouped by day

        :returns: a dict of days and events
        """
        days: defaultdict[date, list] = defaultdict(list)

        for event in self.events:
            days[event.start.date()].append(event)

        return days

    def format_as_ical(self) -> bytes:
        """
        Format existing schedule to iCalendar
        :returns: ics file
        """
        # inictialize calendar
        cal = Calendar()
        cal.add("prodid", "-//ue-schedule/UE Schedule//PL")
        cal.add("version", "2.0")

        # add event components
        for event in self.events:
            cal_event = ICalEvent()
            cal_event.add("summary", f"{event.name} - {event.type}")

            if event.location:
                cal_event.add("location", event.location)

            if event.teacher:
                cal_event.add("description", event.teacher)

            cal_event.add("dtstart", vDatetime(event.start))
            cal_event.add("dtend", vDatetime(event.end))
            cal.add_component(cal_event)

        return cal.to_ical()

    class Config:
        """
        Event model configuration class
        """

        frozen = True
