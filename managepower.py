#!/usr/bin/env python3
'''
Control pump power using PWM on Raspberry Pi
Manage power based on flow and return temperatures
Report states to emonhub

python3 -m pip install simple-pid
sudo ./managepower.py --config-file /home/pi/emonreporter/conf/emonreporter.conf
'''

# standard library modules used in code
from __future__ import absolute_import
from __future__ import division

import time
import logging
from simple_pid import PID
# pump related imports
import setpower_a
import setpwm2_a
# temperature monitoring related imports
import sys 
import os
sys.path.append(os.path.abspath("/home/pi/emonreporter/src"))
from rept_1wire_hmv2 import (
    initialise_setup,
    initialise_1wire,
    get_1wire_data,
    LocalDatalogger,
    get_args,
    send_message
)
import emonhub_coder
# hm imports
from heatmisercontroller import logging_setup


def main():
    args = get_args('Rolling pump control from temperature and reporting')

    # turn the arguments into numbers
    sample_interval = float(args.sample_interval)

    setup, localconfigfile = initialise_setup(args.config_file)

    # setup logging
    logging_setup.initialize_logger_full(
        setup.settings['logging']['logfolder'],
        logging.DEBUG)

    # tell the user what is happening
    logging.info("Rolling pump control from temperature and reporting")
    logging.info("  sample interval: %d seconds", sample_interval)

    onewirenetwork, sensorlist1wire = initialise_1wire(setup)

    datalogger = LocalDatalogger(setup.settings['logging']['logfolder'])

    logging.info("Entering reading loop")

    # create pid controller
    pid = PID(1, 0.1, 0.05, setpoint=70)
    pid.output_limits = (0.1, 1)  # limit between 10% and 100%
    pid.sample_time = 1  # update time in seconds

    # now loop forever reading the identified sensors and updating pump
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
        temps, count, output_message = get_1wire_data(setup,
                                                      onewirenetwork, 
                                                      sensorlist1wire,
                                                      read_time,
                                                      datalogger)

        if count == 2:
            # decide power level
            flow_temp = max(temps)
            return_temp = min(temps)
            temp_ratio = return_temp / flow_temp
            print(temp_ratio)
            power = pid(temp_ratio)

            # convert to pwm duty cycle
            duty = setpower_a.get_pwm(power)
            print('power={:d}, pwm={:d}'.format(int(power), duty))
            setpwm2_a.writetopwm(duty)
        else:
            power = int(setup.settings['emonsocket']['temperaturenull'])

        # report temps and power level
        output_message += ' ' + ' '.join(map(str, emonhub_coder.encode("h", round(power * 10 ))))
        send_message(setup, output_message)


if __name__ == "__main__":
    main()
