'''
Control the PWM on Raspberry Pi
Set to 73 percent for 60 seconds
'''

import setpwm2_a

setpwm2_a.tempwritetopwm(73, 600)