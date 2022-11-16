#!/usr/bin/env python3

import wiringpi
from time import sleep

ledpin = 12                             # PWM pin connected to LED

wiringpi.wiringPiSetupPhys()  # OR, using P1 header pin numbers
wiringpi.pinMode(ledpin, wiringpi.OUTPUT)

try:
    wiringpi.digitalWrite(ledpin, wiringpi.HIGH)
    sleep(60)
except KeyboardInterrupt: # trap a CTRL+C keyboard interrupt
    print("keyboard interrupt")

finally:
    wiringpi.digitalWrite(ledpin, wiringpi.LOW)
