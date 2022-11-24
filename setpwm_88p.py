'''
Control the PWM on Raspberry Pi
Set to 100 percent for 60 seconds
'''

from setpwm_a import PwmPort

pwmport = PwmPort()
pwmport.tempwritetopwm(88, 600)
