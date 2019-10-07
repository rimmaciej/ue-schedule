#!/usr/bin/env python3.7
from UEPlanTool import PlanDownloader

# Initialization
planId = 0
startDate = "2019-10-06"
endDate = "2019-10-12"
p = PlanDownloader(planId, startDate, endDate)

# Output
p.printEvents()
