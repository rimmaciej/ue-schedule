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
# initialize the downloader
sd = ScheduleDownloader(studentsPlanID)

# date range
schedule = sd.download(startDate, endDate)

# whole schedule
schedule = sd.download()
```

- Filtering
```python
# run predefined filters
schedule.run_filters()
```


- Exporting
```python
# print, grouped by days
schedule.print()

# get a list of all events
schedule.to_list()

# export as ICS
schedule.to_ics()

# export as JSON
schedule.to_json()
```