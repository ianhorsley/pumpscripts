#!/usr/bin/env python3

#import RPi.GPIO as GPIO
import wiringpi
from time import sleep

ledpin = 12                             # PWM pin connected to LED

#  PWM_MODE_MS = 0
#  PWM_MODE_BAL = 1

wiringpi.wiringPiSetupPhys()  # OR, using P1 header pin numbers
wiringpi.pinMode(ledpin,wiringpi.OUTPUT)



try:
    wiringpi.digitalWrite(ledpin,wiringpi.HIGH)
    sleep(60)
except KeyboardInterrupt: # trap a CTRL+C keyboard interrupt
    print("keyboard interrupt")

finally:
    #wiringpi.pinMode(ledpin,wiringpi.OUTPUT)
    #wiringpi.pullUpDnControl(ledpin,wiringpi.PUD_DOWN)
    wiringpi.digitalWrite(ledpin,wiringpi.LOW)

