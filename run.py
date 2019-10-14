#!/usr/bin/env python
from ueschedule.config import Config
from ueschedule import UESchedule


def run():
    config = Config()

    schedule = UESchedule(config)
    schedule.display()


if __name__ == "__main__":
    run()
