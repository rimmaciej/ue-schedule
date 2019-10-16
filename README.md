## UE Class schedule utility library

A utility library used to download, filter and export class schedule at University of Economics in Katowice.  Imports data from ["Wirtualna uczelnia"](https://e-uczelnia.ue.katowice.pl/).

Each students gets a constant schedule id which is used to generate the schedule.  

You can get your ID by going to "Wirtualna uczelnia" > "Rozkład zajęć" > "Prezentacja harmonogramu zajęć" > "Eksport planu do kalendarza".

The url ends with `/calendarid_XXXXXX.ics`, the XXXXXX will be your ID.

### Installation
```
pip install ue-schedule
```

### Development
You can install dependencies in a virtualenv with pipenv
```
pipenv install
pipenv shell
```

### Usage
Import
```python
from ue_schedule import Schedule
```

Initialization
```python
# initialize the downloader with dates
s = Schedule(schedule_id, start_date, end_date)

# and without dates
s = Schedule(schedule_id)
```

Export
```python
# get event list
schedule.events

# export as iCalendar
schedule.to_ical()
```
Data is automatically fetched when exporting, but you can force fetch with
```python
schedule.fetch()
```