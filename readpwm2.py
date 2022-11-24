#!/usr/bin/env python3

import pigpio  # http://abyz.co.uk/rpi/pigpio/python.html
import time
from readpwm1 import PWM_read


class PWM_read2:
    def __init__(self, pi, gpio):
        self.pi = pi
        self.gpio = gpio

        self._high_tick = None
        self._p = None
        self._hp = None
        self._p_avg = None
        self._hp_avg = None
        self._avg_n = 20.0

        self._cb = pi.callback(gpio, pigpio.EITHER_EDGE, self._cbf)

    _slide_avg = readpwm1._slide_avg

    def _update_period(self, new_tick, old_tick, previous_period):
        try:
            return pigpio.tickDiff(old_tick, new_tick)
        except TypeError:
            return previous_period

    def _cbf(self, gpio, level, tick):

        if level == 1:
            self._p = self._update_period(tick, self._high_tick, self._p)
            self._p_avg = self._slide_avg(self._p_avg, self._p)
            self._high_tick = tick
            return

        if level == 0:
            self._hp = self._update_period(tick, self._high_tick, self._hp)
            self._hp_avg = self._slide_avg(self._hp_avg, self._hp)
            return

        print("undefined level")

    def cancel(self):
        self._cb.cancel()


pi = pigpio.pi()

p1 = PWM_read2(pi, 24)

try:
    while True:
        if p1._p is not None and p1._p_avg is not None and p1._hp is not None:
            print("g={} f={:.1f} f={:.1f} dc={:.1f} dc={:.1f}".
                  format(24, 1000000.0/p1._p, 1000000.0/p1._p_avg,
                         100.0 * p1._hp/p1._p, 100.0 * p1._hp_avg/p1._p_avg))
        else:
            print("no data yet")
        p1._p = None
        p1._hp = None
        time.sleep(1)   # Detect every second

except KeyboardInterrupt:  # trap a CTRL+C keyboard interrupt
    p1.cancel()  # resets all GPIO ports used by this function
    pi.stop()
