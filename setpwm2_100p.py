'''
Control the Brightness of LED using PWM on Raspberry Pi
http://www.electronicwings.com
'''

#import RPi.GPIO as GPIO
import wiringpi
from time import sleep

ledpin = 12                             # PWM pin connected to LED

#  PWM_MODE_MS = 0
#  PWM_MODE_BAL = 1

wiringpi.wiringPiSetupPhys()  # OR, using P1 header pin numbers  
wiringpi.pinMode(ledpin,wiringpi.PWM_OUTPUT)      # pwm only works on P1 header pin 12  
wiringpi.pwmSetMode(wiringpi.PWM_MODE_MS)

# set the clock divisor to reduce the 19.2 Mhz clock
# to something slower, 5 Khz.
# Range of pwmSetClock() is 2 to 4095.
wiringpi.pwmSetClock (192)  # 19.2 Mhz divided by 3840 is 5 Khz. 192 for 100Hz 48 for 4kHz

# set the PWM range which is the value for the range counter
# which is decremented at the modified clock frequency.
# in this case we are decrementing the range counter 5,000
# times per second since the clock at 19.2 Mhz is being
# divided by 3840 to give us 5 Khz.
pwmrange = 1000
wiringpi.pwmSetRange (pwmrange)  # range is 2500 counts to give us half second.

wiringpi.pwmWrite(ledpin, int(pwmrange/2))    # duty cycle between 0 and 1024. 0 = off, 1024 = fully on


try:
    duty = 100
    wiringpi.pwmWrite(ledpin, int(round(pwmrange*duty/100))) #provide duty cycle in the range 0-100
    sleep(600)

except KeyboardInterrupt: # trap a CTRL+C keyboard interrupt
    print("keyboard interrupt")

finally:
    wiringpi.pinMode(ledpin,wiringpi.INPUT)
    wiringpi.pullUpDnControl(ledpin,wiringpi.PUD_DOWN)
