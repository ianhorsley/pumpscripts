#!/usr/bin/env python3
'''
Control the PWM on Raspberry Pi
If run from command line takes PWM duty cycle input 0-100%
'''

import wiringpi
from time import sleep
import sys

# pwm only works on P1 header pin 12
pwmpin = 12         # PWM pin connected to output
# set the clock divisor to reduce the 19.2 Mhz clock
# to something slower, 5 Khz.
# Range of pwmSetClock() is 2 to 4095.
# 19.2 Mhz divided by 3840 is 5 Khz. 192 for 100Hz 48 for 4kHz
pwmclockdiv = 192
# set the PWM range which is the value for the range counter
# which is decremented at the modified clock frequency.
# in this case we are decrementing the range counter 5,000
# times per second since the clock at 19.2 Mhz is being
# divided by 3840 to give us 5 Khz.
pwmrange = 1000  # range of 2500 would give us half second.

wiringpi.wiringPiSetupPhys()  # OR, using P1 header pin numbers
wiringpi.pinMode(pwmpin, wiringpi.PWM_OUTPUT)
wiringpi.pwmSetMode(wiringpi.PWM_MODE_MS)

wiringpi.pwmSetClock(pwmclockdiv) # set clock divider
wiringpi.pwmSetRange(pwmrange) # set pwm range counter


def writetopwm(pwm_level):
    """write level to pwm pin and leave set"""
    try:
        duty = int(pwm_level)
        # provide duty cycle in the range 0-100
        wiringpi.pwmWrite(pwmpin, int(round(pwmrange*duty/100)))
        sleep(30)
    except IndexError:
        raise SystemExit(f"Usage: {sys.argv[0]} dutycycle")
    except ValueError:
        raise SystemExit("duty cycle must be int from 0 to 100")
    except KeyboardInterrupt:  # trap a CTRL+C keyboard interrupt
        print("keyboard interrupt")


def tempwritetopwm(pwm_level, time):
    """write level to pwm and revert after time(s)"""
    try:
        duty = int(pwm_level)
        # provide duty cycle in the range 0-100
        wiringpi.pwmWrite(pwmpin, int(round(pwmrange*duty/100)))
        sleep(time)
    except KeyboardInterrupt: # trap a CTRL+C keyboard interrupt
        print("keyboard interrupt")
    finally:
        # do we need to write full power before disconnecting?
        wiringpi.pinMode(pwmpin, wiringpi.INPUT)
        wiringpi.pullUpDnControl(pwmpin, wiringpi.PUD_DOWN)


if __name__ == "__main__":

    writetopwm(sys.argv[1])

