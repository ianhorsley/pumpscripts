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
import sys
import os
import requests
import json
from datetime import timezone
import datetime
from simple_pid import PID
# pump related imports
import setpower_a
import setpwm2_a
# hm imports
from heatmisercontroller import logging_setup
# temperature monitoring related imports
import emonhub_coder
sys.path.append(os.path.abspath("/home/pi/emonreporter/src"))
from rept_1wire_hmv2 import (
    initialise_setup,
    initialise_1wire,
    get_1wire_data,
    LocalDatalogger,
    get_args,
    send_message
)


def create_output_str(number_in):
    """process number to send to emonhub"""
    encoded_values = emonhub_coder.encode("h", round(number_in))
    #convert to string and add spaces
    return ' ' + ' '.join(map(str, encoded_value))


def get_demand_data(setup):
    """get data from emoncms
    return dict of data
    rooms, 94
    water, 71
    outside_temp, 79

    urlbase="https://pi4.horsley.me.uk/feed/timevalue.json?id="
    apikey="bec76bf52d2ee7d1b62fb02005f6a34b"
    """
    # Getting the current date and time
    dt = datetime.datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    utc_timestamp = utc_time.timestamp()

    # use setup to find urls to collect
    urlbase = setup.settings['emoncms']['urlbase']
    feeds = setup.settings['emoncms']['feeds']
    apikey = setup.settings['emoncms']['apikey']

    results = {}

    for feed in feeds:
        print(feed)
        results[feed['variablename']] = [None, 3600]
        url = urlbase + feed['id'] + '&apikey=' + apikey
        # for each url, might need to add api key
        # try:
        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError:
            break
        if response.status_code != 200:
            break
        # break out time and value
        data = json.loads(response.text)

        age = utc_timestamp - data['time']
        value = data['value']

        # store in variable, with age in seconds
        results['variablename'] = [value, age]

    # return dict of data
    return results


def main():
    args = get_args('Rolling pump control from temperature and reporting')

    # turn the arguments into numbers
    sample_interval = float(args.sample_interval)

    setup, _ = initialise_setup(args.config_file)

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
    pid = PID(2, 0, 0, setpoint=0.7)  # were 1, 0.05. 0.01
    pid.output_limits = (0.1, .7)  # limit between 10% and 100%
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
            power = 100 * pid(temp_ratio)

            # convert to pwm duty cycle
            duty = setpower_a.get_pwm(power)
            print('tempratio={:.2f} power={:d}, pwm={:d}'.format(temp_ratio,
                                                                 int(power),
                                                                 duty))
            setpwm2_a.writetopwm(duty)
            logging.debug("written")
        else:
            power = int(setup.settings['emonsocket']['temperaturenull'])
            temp_ratio = power

        # report temps and power level
        output_message += create_output_str(power * 10)
        output_message += create_output_str(temp_ratio * 1000)
        send_message(setup, output_message)
        logging.debug("sent")


if __name__ == "__main__":
    main()
