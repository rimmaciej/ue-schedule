from ueschedule.schedule import Schedule


class UESchedule():
    def __init__(self, config):
        self.schedule = Schedule(config)

    def display(self):
        """Print all the events grouped by date"""
        events_by_date = {}

        for event in self.schedule.events():
            ev_date = event.data["start"].strftime("%Y-%m-%d")

            if ev_date not in events_by_date.keys():
                events_by_date[ev_date] = []
            events_by_date[ev_date].append(event)

        for date, events in events_by_date.items():
            print(date)
            for event in events:
                start = event.data["start"].strftime("%H:%M")
                end = event.data["end"].strftime("%H:%M")

                print("\t{start} - {end}\n"
                      "\t{summary}\n"
                      "\t{teacher}\n"
                      "\t{location}\n".format(start=start,
                                              end=end,
                                              summary=event.data['summary'],
                                              teacher=event.data['teacher'],
                                              location=event.data['location']))
            print()

    def export(self):
        """Build an iCalendar out of the parsed plan"""
        ical = self.schedule.build_ics()

        # add all events from the plan to the calendar
        for event in self.schedule.events():
            ical.add_component(event.to_ics())

        return ical.to_ical()
