#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time

# Setup GPIO
GPIO.setmode(GPIO.BCM)


class PWM_read:
    def __init__(self, gpio):
        self.gpio = gpio

        # Pull up to 3.3V
        GPIO.setup(self.gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self._high_tick = None
        self._p = None  # low period
        self._hp = None  # high period
        self._p_avg = None
        self._hp_avg = None
        self._avg_n = 5.0
        self._min_freq = 20.0  # in Hz
        # Add event to detect
        self._cb = GPIO.add_event_detect(self.gpio, GPIO.BOTH, self._cbf)

    def _slide_avg(self, average, new_period):
        if average is not None and new_period is not None:
            return average + (new_period - average)/self._avg_n
        else:
            return new_period

    def _update_period(self, new_tick, old_tick, previous_period):
        try:
            return new_tick - old_tick
        except TypeError:
            return previous_period


    def _cbf(self, n):
        tick = time.time()
        if GPIO.input(self.gpio):
            self._p = self._update_period(tick, self._high_tick, self._p)
            self._p_avg = self._slide_avg(self._p_avg, self._p)
            self._high_tick = tick
        else:
            self._hp = self._update_period(tick, self._high_tick, self._hp)
            self._hp_avg = self._slide_avg(self._hp_avg, self._hp)

    def cancel(self):
        GPIO.remove_event_detect(self.gpio)
        GPIO.cleanup()

    def _proc_freq(self, period):
        if period is None:
            return 0
        if ((time.time() - self._high_tick) < (1 / self._min_freq)):
            return 1.0/period
        else:
            return 0

    def get_freq(self):
        return self._proc_freq(self._p)

    def get_avg_freq(self):
        return self._proc_freq(self._p_avg)

    def _proc_duty(self, period, high_period):
        if period is None or high_period is None:
            return -1
        if time.time() - self._high_tick < 1 / self._min_freq:
            return 100.0 * high_period/period
        if GPIO.input(self.gpio):
            print("high")
            print(GPIO.input(self.gpio))
            return 100.0
        return 0.0

    def get_duty(self):
        return self._proc_duty(self._p, self._hp)

    def get_avg_duty(self):
        return self._proc_duty(self._p_avg, self._hp_avg)


p1 = PWM_read(24)

try:
    while True:
        print("g={} f={:.1f} f={:.1f} dc={:.1f} dc={:.1f}".
              format(24, p1.get_freq(), p1.get_avg_freq(),
                     p1.get_duty(), p1.get_avg_duty()))

        time.sleep(1)  # Detect every second

except KeyboardInterrupt:  # trap a CTRL+C keyboard interrupt
    print("keyboard exit")
finally:
    p1.cancel()  # resets all GPIO ports used by this function
