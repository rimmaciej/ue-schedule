## UE Class schedule utility library

A utility library used to download, filter and export class schedule at University of Economics in Katowice. Imports data from ["Wirtualna uczelnia"](https://e-uczelnia.ue.katowice.pl/).

Each students gets a constant schedule id which is used to generate the schedule.

You can get your ID by going to "Wirtualna uczelnia" > "Rozkład zajęć" > "Prezentacja harmonogramu zajęć" > "Eksport planu do kalendarza".

The url ends with `/calendarid_XXXXXX.ics`, the XXXXXX will be your ID.

### Installation

```
pip install ue-schedule
```

You can then run the ue-schedule tool from your shell like

```sh
ue-schedule <schedule_id>
```

### Development

You can install dependencies in a virtualenv with poetry

```bash
poetry install

# switch to the virtualenv
poetry shell
```

### Usage

```python
from ue_schedule import Schedule

# initialize the downloader
s = Schedule(schedule_id)

# get event list
schedule.get_events()

# get event list as iCalendar
schedule.get_ical()

# get event list as json
schedule.get_json()
```

Data is automatically fetched when exporting, but you can force fetch with

```python
schedule.fetch()
```

If you need to dump the event list and load later

```python
# dump the event list
events = schedule.dump_events()

# load the event list
schedule.load_events(events)
```

If there's a need to format the list acquired with `.get_events()`, you can use format functions

```python
# format event list as ical file
Schedule.format_as_ical(events)

# format event list as json
Schedule.format_as_json(events)
```
