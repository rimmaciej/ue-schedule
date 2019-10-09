## UE Class schedule tool

A tool/library used to download, parse and transform class schedule at University of Economics in Katowice.  Imports data from the ["virtual university"](https://e-uczelnia.ue.katowice.pl/).

Each students gets a constant plan id which is used to generate the schedule.  

You can get your ID by going to "Virtual university", "Rozkład zajęć" > "Prezentacja harmonogramu zajęć" > "Eksport planu do kalendarza".

The url ends with `/calendarid_XXXXXX.ics`, the XXXXXX will be your ID.

### Installation
You can install dependencies in a virtualenv with pipenv
```
pipenv install
pipenv shell
```


### Usage
- Importing
```python
from UESchedule import ScheduleDownloader
```

- Downloading
```python
# whole schedule
p = ScheduleDownloader(studentsPlanID)

# schedule between dates
p = ScheduleDownloader(studentsPlanID, startDate, endDate)
```

- Exporting
```python
# print, grouped by days
p.printElements()

# get a list of all events
p.getList()

# export as ICS
p.exportICS()
```