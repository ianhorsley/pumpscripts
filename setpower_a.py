#!/usr/bin/env python3
'''
Control pump power using PWM on Raspberry Pi
Takes command line input of power 0-100%
'''

import setpwm2_a
import sys

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

def get_pwm(power):
    #takes a percentage power and returns pwm setting. 0-100 from min to max pump speed pwm (84 - 10).
    boundedpower = clamp(power, 0, 100)
    if(power != boundedpower):
        print("power request outside bounds, limited")
    pwm = -0.74 * boundedpower + 84
    return int(pwm)

def get_pwm_max():
    #returns pwm for max power, <10
    return 5

def get_pwm_min():
    #returns pwm for min power, 84< <92?
    return 88

def get_pwm_stop():
    #returns pwm for stop of the motor > 92
    return 98


power = int(sys.argv[1])
#convert to pwm duty cycle
duty = get_pwm(power)
print('power={:d}, pwm={:d}'.format(power,duty))

setpwm2_a.writetopwm(duty)
