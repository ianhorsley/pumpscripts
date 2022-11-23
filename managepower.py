#!/usr/bin/env python3
'''
Control pump power using PWM on Raspberry Pi
Manage power based on flow and return temperatures
Report states to emonhub

python3 -m pip install simple-pid
sudo ./managepower.py --config-file managepower.conf
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
#from simple_pid import PID
from types import SimpleNamespace
# pump related imports
import setpower_a
import setpwm2_a
# hm imports
from heatmisercontroller import logging_setup
# temperature monitoring related imports
sys.path.append(os.path.abspath("/home/pi/emonreporter/src"))
import emonhub_coder
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
    # convert to string and add spaces
    return ' ' + ' '.join(map(str, encoded_values))


def fetch_url(conf_vars, f_id, utc_timestamp):
    """Fetch value from url and check valid."""
    url = conf_vars.urlbase + f_id + '&apikey=' + conf_vars.apikey

    response = requests.get(url)

    if response.status_code != 200:
        raise ValueError("no data")
    # break out time and value
    data = json.loads(response.text)
    age = int(utc_timestamp - data['time'])

    if age > int(conf_vars.maximumage):
        raise ValueError("data to old")

    return [data['value'], age]


def get_demand_data(setup_data):
    """get data from emoncms
    return dict of data
    """
    # Getting the current date and time
    dt = datetime.datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    utc_timestamp = utc_time.timestamp()

    # use setup to find urls to collect
    conf_vars = SimpleNamespace(**setup_data.settings['emoncms'])

    results = {}

    for feed, f_id in conf_vars.feeds.items():
        print(feed, f_id)

        try:
            results[feed] = fetch_url(conf_vars, f_id, utc_timestamp)
        except (requests.exceptions.ConnectionError, ValueError):
            results[feed] = [conf_vars.feed_defaults[feed], None]

    # return dict of data
    return results


def compute_pump_curve(setup_data, return_temp, num_rooms, water_demand):
    """Select pump curve level from temp and rooms active"""
    global pump_curve_previous
    conf_vars = SimpleNamespace(**setup_data.settings['pumpcurveselection'])

    # if in warming stage increase power
    if return_temp < int(conf_vars.warmingthres):
        multiplier = float(conf_vars.multiplierscaler)
    else:
        multiplier = 1
    # calculate curve
    curve = num_rooms * conf_vars.percperroom * multiplier + \
            water_demand + conf_vars.percforwater
    #limit curve change
    curve = setpower_a.clamp(curve,
                             pump_curve_previous/conf_vars.maxchangescale,
                             pump_curve_previous*conf_vars.maxchangescale
                             )
    # return and limit
    return setpower_a.clamp(curve,
                            conf_vars.mincurve,
                            conf_vars.maxcurve
                            )


def proc_temps(temp_list):
    """process to temps to find flow and return and ratio"""
    flow = max(temp_list)
    ret = min(temp_list)
    return flow, ret, ret / flow


def setup_pins(setup_data):
    """function configures burner reading and control pins"""
    # setup from "pi_pins"
    wiringpi.pinMode(setup_data.settings['pi_pins']['burner_firing'], wiringpi.INPUT)
    wiringpi.pinMode(setup_data.settings['pi_pins']['burner_off'], wiringpi.OUTPUT) 
    return


def get_burner_state(setup_data):
    """checks burner on/off state"""
    burner_state_pin = setup_data.settings['pi_pins']['burner_off']
    return wiringpi.digitalRead(burner_state_pin) 


def _toggle_burner(setup_data, flow, min, max):
    """Check flow and set boiler accordingly"""
    burner_pin = setup_data.settings['pi_pins']['burner_off']
    # if flow is greater than mac turn off
    if flow > max:
        wiringpi.digitalWrite(burner_pin, 1)
        return
    # if flow is less than min
    if flow < min:
        wiringpi.digitalWrite(burner_pin, 0)
        return
    #otherwise leave state as is


def _release_burner(setup_data):
    """Set burner to on which leaves boiler state in control"""
    burner_pin = setup_data.settings['pi_pins']['burner_off']
    wiringpi.digitalWrite(burner_pin, 0)


def update_burner_state(setup_data, flow, water_state):
    """sets the state of the burner
    relay is normally closed, so writing a 1 turns off"""
    burner = setup_data.settings['burner_control']

    if burner['heat_flow_max'] <= burner['heat_flow_min'] or \
        burner['water_flow_max'] <= burner['water_flow_min']:
        _release_burner(setup_data)
        raise ValueError("burner temp ranges are not valid")
    #if water demand is on set to on and leave to boiler stat to control
    if water_state > 0:
        if burner['control_water'] > 0:
            _toggle_burner(setup_data, flow, burner['water_flow_min'], burner['water_flow_max'])
        else:
            _release_burner(setup_data)
    else:
        _toggle_burner(setup_data, flow, burner['heat_flow_min'], burner['heat_flow_max'])


def main():
    args = get_args('Rolling pump control from temperature and reporting')

    # turn the arguments into numbers
    sample_interval = float(args.sample_interval)

    setup, _ = initialise_setup(args.config_file)

    global pump_curve_previous
    pump_curve_previous = float(setup.settings['pumpcurveselection']['defaultcurve'])

    # setup logging
    logging_setup.initialize_logger_full(
        setup.settings['logging']['logfolder'],
        logging.INFO)

    # tell the user what is happening
    logging.info("Rolling pump control from temperature and reporting")
    logging.info("  sample interval: %d seconds", sample_interval)

    onewirenetwork, sensorlist1wire = initialise_1wire(setup)

    datalogger = LocalDatalogger(setup.settings['logging']['logfolder'])

    logging.info("Entering reading loop")

    # create pid controller
    #pid = PID(2, 0, 0, setpoint=0.7)  # were 1, 0.05. 0.01
    #pid.output_limits = (0.1, .7)  # limit between 10% and 100%
    #pid.sample_time = 1  # update time in seconds

    # now loop forever reading the identified sensors and updating pump
    while True:
        # update logic to read every second and write to burner state
        # pump updates and output to emoncms every second
        # burner controller logic

        # read data from emoncms feeds
        feed_values = get_demand_data(setup)
        print(feed_values)

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
            # decide power level, only if temps are valid
            temp_flow, temp_return, temp_ratio = proc_temps(temps)

            # set burner state
            update_burner_state(setup, temp_flow, feed_values['water'][0])

            #power = 100 * pid(temp_ratio)
            pump_curve = compute_pump_curve(setup, temp_return, feed_values['rooms'][0], feed_values['water'][0])

        else:
            temp_ratio = int(setup.settings['emonsocket']['temperaturenull'])
            pump_curve = setup.settings['pumpcurveselection']['defaultcurve']



        # convert to pwm duty cycle
        duty = setpower_a.get_pwm(pump_curve)
        logurl = 'tempratio={:.2f} power={:d}, pwm={:d}'
        logging.info(logurl.format(temp_ratio, int(pump_curve), duty))
        setpwm2_a.writetopwm(duty)
        logging.debug("written")

        # report temps and power level
        output_message += create_output_str(pump_curve * 10)
        output_message += create_output_str(temp_ratio * 1000)
        send_message(setup, output_message)
        logging.debug("sent")

        # determine how long to wait until next interval
        # note this will skip some if specified interval is too short
        #  - it finds the next after now, not next after last
        sleeptime = sample_interval - (time.time() % sample_interval)
        time.sleep(sleeptime)


if __name__ == "__main__":
    main()
