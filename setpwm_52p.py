'''
Control the PWM on Raspberry Pi
Set to 52 percent for 60 seconds
'''

from setpwm_a import PwmPort

pwmport = PwmPort()
pwmport.tempwritetopwm(52, 600)
