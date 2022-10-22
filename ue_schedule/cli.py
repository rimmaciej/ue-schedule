"""
This module is a CLI tool that is an example of how to use the library.
"""
import sys
from datetime import datetime, timedelta
from typing import Optional

import click  # type: ignore

from ue_schedule import Schedule
from ue_schedule.event import EventType
from ue_schedule.exceptions import InvalidIdError, WrongResponseError, WUTimeoutError

today = datetime.now().date()

event_types = {
    EventType.WYKLAD: click.style("Wykład", fg="green"),
    EventType.CWICZENIA: click.style("Ćwiczenia", fg="red"),
    EventType.LABORATORIUM: click.style("Laboratorium", fg="magenta"),
    EventType.LEKTORAT: click.style("Lektorat", fg="blue"),
    EventType.SEMINARIUM: click.style("Seminarium", fg="cyan"),
    EventType.WF: click.style("WF", fg="yellow"),
    EventType.INNY: click.style("Inny", fg="bright_black"),
}


@click.command()
@click.argument("schedule_id", type=str)
@click.option("-j", "--json", is_flag=True, default=False, show_default=True)
@click.option("-g", "--groups", is_flag=True, default=False, show_default=True)
@click.option(
    "-s", "--start", "start_date", type=click.DateTime(), default=str(today), show_default=True
)
@click.option("-e", "--end", "end_date", type=click.DateTime())
def main(
    schedule_id: str,
    json: bool,
    groups: bool,
    start_date: datetime,
    end_date: Optional[datetime] = None,
) -> None:
    """
    CLI Entry point function
    """
    schedule = Schedule(schedule_id)

    if not end_date:
        end_date = start_date + timedelta(days=15)

    try:
        events = schedule.get_events(start_date.date(), end_date.date())
    except InvalidIdError:
        print("Provided ID is invalid.")
        sys.exit(1)
    except (WUTimeoutError, WrongResponseError):
        print("Failed to fetch schedule.")
        sys.exit(1)

    if json:
        print(Schedule.format_as_json(events))
        return

    response = ""

    for day in events:

        if len(day["events"]) == 0:
            response += click.style(f"{day['date']} - brak zajęć\n", fg="bright_black")
        else:
            response += click.style(f"{day['date']}\n", fg="green")

        for event in day["events"]:
            event_time = click.style(f"{event.start:%H:%M} - {event.end:%H:%M}", fg="yellow")

            teacher = click.style(
                event.teacher if event.teacher else "Nieznany nauczyciel", fg="bright_black"
            )

            response += f"  {event_time}  {event.name} - {event_types[event.type]}\n"
            response += f"                 {teacher}\n"

            if groups:
                group_string = click.style(", ".join(event.groups), fg="bright_black")
                response += f"                 {group_string}\n"

        response += "\n"

    click.echo_via_pager(response)


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
