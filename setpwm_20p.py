'''
Control the PWM on Raspberry Pi
Set to 20 percent for 60 seconds
'''

from setpwm_a import PwmPort

pwmport = PwmPort()
pwmport.tempwritetopwm(20, 600)
