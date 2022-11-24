#!/usr/bin/env python3
'''
Control pump power using PWM on Raspberry Pi
Takes command line input of power 0-100%
'''

import setpwm_a
import sys


def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)


class Pump(PwmPort):
    def __init__(self):
        super().__init__(self)
        self.pwm_max = 5  # returns pwm for max power, <10
        self.pwm_min = 88  # returns pwm for min power, 84< <92?
        self.pwm_stop = 98  # returns pwm for stop of the motor > 92
        self.power = 100  # assume starts at full power

    def compute_pwm(self, power):
        # takes a percentage power and returns pwm duty cycle.
        # 0-100 from min to max pump speed pwm (84 - 10).
        boundedpower = clamp(power, 0, 100)
        if(power != boundedpower):
            print("power request outside bounds, limited")
        pwm = -0.74 * boundedpower + 84
        return int(pwm)

    def stop(self):
        self.writetopwm(self.pwm_stop)
        self.power = None

    def set_power(self, power):
        """Compute and set duty cycle based on power level"""
        pwm_duty = compute_pwm(self, power)
        self.writetopwm(pwm_duty)
        self.power = power

    def set_min_power(self):
        """Set pump to min running power"""
        self.writetopwm(self.pwm_min)
        self.power = 0

    def set_max_power(self):
        """Set pump to max power"""
        self.writetopwm(self.pwm_max)
        self.power = 100



if __name__ == "__main__":

    pwmpump = Pump()
    pwmpump.set_power(sys.argv[1])

    print('power={:d}, pwm={:d}'.format(pwmpump.power, pwmpump.pwm_duty))
