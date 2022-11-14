'''
Control the PWM on Raspberry Pi
Set to 62 percent for 60 seconds
'''

import setpwm2_a

setpwm2_a.tempwritetopwm(62, 600)