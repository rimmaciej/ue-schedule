from datetime import datetime, timedelta
from typing import Optional

import click

from .schedule import Schedule

today = datetime.now().date()


@click.command()
@click.argument("schedule_id", type=int)
@click.option("-s", "--start", "start_date", type=click.DateTime(), default=str(today), show_default=True)
@click.option("-e", "--end", "end_date", type=click.DateTime())
def main(schedule_id: int, start_date: datetime, end_date: Optional[datetime] = None):
    schedule = Schedule(schedule_id)

    if start_date and not end_date:
        end_date = start_date + timedelta(days=15)

    events = schedule.get_events(start_date.date(), end_date.date())

    response = ""

    for day in events:
        response += click.style(f"{day['date']}\n", fg="green")

        if len(day["events"]) == 0:
            response += "  No events for this day\n"

        for event in day["events"]:
            event_time = click.style(f"{event.start:%H:%M} - {event.end:%H:%M}", fg="yellow")

            if event.type == "Lektorat":
                event_type = click.style(event.type, fg="blue")
            elif event.type == "Ćwiczenia":
                event_type = click.style(event.type, fg="red")
            elif event.type.startswith("wykład"):
                event_type = click.style("Wykład", fg="green")
            else:
                event_type = click.style(event.type, fg="bright_black")

            response += f"  {event_time}  {event.name} - {event_type} \n"

        response += "\n"

    click.echo_via_pager(response)


if __name__ == "__main__":
    main()
