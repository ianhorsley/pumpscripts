#!/usr/bin/env python3
'''
Control pump power using PWM on Raspberry Pi
Manage power based on flow and return temperatures
Report states to emonhub

python3 -m pip install simple-pid
'''

# standard library modules used in code
from __future__ import absolute_import
from __future__ import division

import time
import logging
from simple_pid import PID

# create pid controller
pid = PID(1, 0.1, 0.05, setpoint=0.7)
pid.output_limits = (0.1, 1)  # limit between 10% and 100%
pid.sample_time = 1  # update time in seconds

# now loop forever reading the identified sensors and updating pump
sample_interval = 5
while True:
    # determine how long to wait until next interval
    # note this will skip some if specified interval is too short
    #  - it finds the next after now, not next after last
    sleeptime = sample_interval - (time.time() % sample_interval)
    time.sleep(sleeptime)

    # read temps
    # get time now and record it
    read_time = int(time.time())  # we only record to integer seconds

    logging.info("Logging cyle at %d", read_time)

    temp_ratio = .5

    power = pid(temp_ratio)

    print(temp_ratio, power)
