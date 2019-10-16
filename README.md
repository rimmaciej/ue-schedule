## UE Class schedule utility library

A utility library used to download, filter and export class schedule at University of Economics in Katowice.  Imports data from ["Wirtualna uczelnia"](https://e-uczelnia.ue.katowice.pl/).

Each students gets a constant plan id which is used to generate the schedule.  

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
- Importing
```python
from ue_schedule import ScheduleDownloader
```

- Downloading
```python
# initialize the downloader
sd = ScheduleDownloader(schedule_id)

# date range
schedule = sd.download(start_date, end_date)

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