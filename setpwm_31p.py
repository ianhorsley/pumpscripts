'''
Control the PWM on Raspberry Pi
Set to 31 percent for 60 seconds
'''

import setpwm2_a

pwmport = PwmPort()
pwmport.tempwritetopwm(31, 600)
