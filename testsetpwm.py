'''
Control the Brightness of LED using PWM on Raspberry Pi
http://www.electronicwings.com
'''

import RPi.GPIO as GPIO
from time import sleep

ledpin = 12				# PWM pin connected to LED
GPIO.setwarnings(False)			#disable warnings
GPIO.setmode(GPIO.BOARD)		#set pin numbering system
GPIO.setup(ledpin,GPIO.OUT,initial=GPIO.LOW)
pi_pwm = GPIO.PWM(ledpin,500)		#create PWM instance with frequency
#pi_pwm.pwmSetMode(Gpio.PWM_MODE_MS)
pi_pwm.start(0)				#start PWM of required Duty Cycle
while True:
    for duty in range(0,51,10):
        pi_pwm.ChangeDutyCycle(duty) #provide duty cycle in the range 0-100
        print(duty)
        sleep(5)
    sleep(0.5)

    for duty in range(100,-1,-10):
        pi_pwm.ChangeDutyCycle(duty)
        print(duty)
        sleep(5)
    sleep(0.5)
