#!/usr/bin/env python

import time

import pigpio # http://abyz.co.uk/rpi/pigpio/python.html

class PWM_read:
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

    def _slide_avg(self, average, new_period):
        if average is not None and new_period is not None:
            return average + (new_period - average)/self._avg_n
        else:
            return new_period

    def _cbf(self, gpio, level, tick):
        #print(gpio, level, tick)
        if level == 1:
            if self._high_tick is not None:
                self._p = pigpio.tickDiff(self._high_tick, tick)
            self._p_avg = self._slide_avg(self._p_avg, self._p)
            self._high_tick = tick
            #print(level, self._p)
        elif level == 0:
            if self._high_tick is not None:
                self._hp = pigpio.tickDiff(self._high_tick, tick)
            self._hp_avg = self._slide_avg(self._hp_avg, self._hp)
            #print(level, self._hp)
        #print(self._p_avg)
        #if (self._p is not None) and (self._hp is not None):
        #   print("g={} f={:.1f} dc={:.1f}".
        #      format(gpio, 1000000.0/self._p, 100.0 * self._hp/self._p))

    def cancel(self):
        self._cb.cancel()

pi = pigpio.pi()

p1 = PWM_read(pi, 24)

try:
    while True:
        #print "%.f Hz, %.f Hz, %.f" % (freq_rise, freq_fall, duty)
        if (p1._p is not None) and (p1._p_avg is not None) and (p1._hp is not None):
            print("g={} f={:.1f} f={:.1f} dc={:.1f} dc={:.1f}".
                format(24, 1000000.0/p1._p, 1000000.0/p1._p_avg, 100.0 * p1._hp/p1._p, 100.0 * p1._hp_avg/p1._p_avg))
        else:
            print("no data yet")
        p1._p = None
        p1._hp = None
        time.sleep(1)   # Detect every second

except KeyboardInterrupt: # trap a CTRL+C keyboard interrupt
    p1.cancel() # resets all GPIO ports used by this function
    pi.stop()
