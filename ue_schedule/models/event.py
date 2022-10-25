"""
Event model definition module
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


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
    EGZAMIN = 7
    INNY = 8


class Event(BaseModel):
    """
    Class representing a single class schedule Event
    """

    name: str
    start: datetime
    end: datetime
    type: EventType
    teacher: Optional[str] = None
    location: Optional[str] = None
    groups: list[str] = Field(default_factory=list)

    class Config:
        """
        Event model configuration class
        """

        frozen = True
