'''
Control the PWM on Raspberry Pi
Set to 100 percent for 60 seconds
'''

import setpwm2_a

setpwm2_a.tempwritetopwm(100, 600)
