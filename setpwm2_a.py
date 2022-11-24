#!/usr/bin/env python3
'''
Control the PWM on Raspberry Pi
If run from command line takes PWM duty cycle input 0-100%
'''

import wiringpi
from time import sleep
import sys


class PwmPort:
    """setup and manage pwm output on raspberry pi"""
    def __init__(self, pwmpin = 12, pwmclockdiv = 192, pwmrange = 1000):
        self.pwmpin = pwmpin
        self.pwmclockdiv = pwmclockdiv
        self.pwmrange = pwmrange
        # dutycycle range from 0 - 100
        self.pwmduty = 0  # start assuming in the off state
        
        wiringpi.wiringPiSetupPhys()  # OR, using P1 header pin numbers
        # pwm only works on P1 header pin 12
        wiringpi.pinMode(pwmpin, wiringpi.PWM_OUTPUT)  # PWM pin connected to output
        wiringpi.pwmSetMode(wiringpi.PWM_MODE_MS)
        # set the clock divisor to reduce the 19.2 Mhz clock
        # to something slower, 5 Khz.
        # Range of pwmSetClock() is 2 to 4095.
        # 19.2 Mhz divided by 3840 is 5 Khz. 192 for 100Hz 48 for 4kHz
        wiringpi.pwmSetClock(pwmclockdiv)  # set clock divider
        # set the PWM range which is the value for the range counter
        # which is decremented at the modified clock frequency.
        # in this case we are decrementing the range counter 5,000
        # times per second since the clock at 19.2 Mhz is being
        # divided by 3840 to give us 5 Khz.
        # range of 2500 would give us half second.
        wiringpi.pwmSetRange(pwmrange)  # set pwm range counter

    def writetopwm(pwm_level):
        """write level to pwm pin and leave set"""
        try:
            self.pwmduty = int(round(self.pwmrange*pwm_level/100))
            # provide duty cycle in the range 0-100
            wiringpi.pwmWrite(self.pwmpin, self.pwmduty)
        except IndexError:
            raise SystemExit(f"Usage: {sys.argv[0]} dutycycle")
        except ValueError:
            raise SystemExit("duty cycle must be int from 0 to 100")
        except KeyboardInterrupt:  # trap a CTRL+C keyboard interrupt
            print("keyboard interrupt")


    def tempwritetopwm(pwm_duty, time):
        """write level to pwm and revert after time(s)"""
        self.writetopwm(pwm_duty)
        sleep(time)

        # do we need to write full power before disconnecting?
        wiringpi.pinMode(pwmpin, wiringpi.INPUT)
        wiringpi.pullUpDnControl(pwmpin, wiringpi.PUD_DOWN)


if __name__ == "__main__":

    pwmport = PwmPort()
    pwmport.writetopwm(sys.argv[1])
