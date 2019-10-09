#!/usr/bin/env python3.7
from UEPlanTool import PlanDownloader

# Initialization
planId = None
startDate = "2019-10-06"
endDate = "2019-10-20"
p = PlanDownloader(planId, startDate, endDate)

# Output
with open("plan.ics", "wb") as f:
    f.write(p.exportICS())
