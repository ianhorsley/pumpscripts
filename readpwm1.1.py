#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time

# Setup GPIO
GPIO.setmode(GPIO.BCM)

class PWM_read:
   def __init__(self, gpio):
      self.gpio = gpio

      #GPIO.setwarnings(False)
      GPIO.setup(self.gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Pull up to 3.3V

      self._high_tick = None
      self._p = None
      self._hp = None
      self._p_avg = None
      self._hp_avg = None
      self._avg_n = 5.0
      self._min_freq = 20.0 # in Hz
      # Add event to detect
      self._cb = GPIO.add_event_detect(self.gpio, GPIO.BOTH, self._cbf)

   def _cbf(self, n):
      tick = time.time()
      if GPIO.input(self.gpio):
         if self._high_tick is not None:
            self._p = tick - self._high_tick
         if self._p_avg is not None and self._p is not None:
            self._p_avg = self._p_avg + (self._p - self._p_avg)/self._avg_n;
         else:
            self._p_avg = self._p
         self._high_tick = tick
      else:
         if self._high_tick is not None:
            self._hp = tick - self._high_tick
         if self._hp_avg is not None and self._hp is not None:
            self._hp_avg = self._hp_avg + (self._hp - self._hp_avg)/self._avg_n;
         else:
            self._hp_avg = self._hp
      #print(self._p_avg)
      #if (self._p is not None) and (self._hp is not None):
      #   print("g={} f={:.1f} dc={:.1f}".
      #      format(gpio, 1000000.0/self._p, 100.0 * self._hp/self._p))

   def cancel(self):
      GPIO.remove_event_detect(self.gpio)
      GPIO.cleanup()

   def get_freq(self):
      if p1._p is not None:
        if ((time.time() - self._high_tick) < (1 / self._min_freq)):
          return 1.0/self._p
        else:
          return 0
      else:
        return 0

   def get_avg_freq(self):
      if p1._p_avg is not None:
        if ((time.time() - self._high_tick) < (1 / self._min_freq)):
          return 1.0/self._p_avg
        else:
          return 0
      else:
        return 0
      
   def get_duty(self):
      if (p1._p is not None) and (p1._hp is not None):
        if time.time() - self._high_tick < 1 / self._min_freq:
          return 100.0 * self._hp/self._p
        elif GPIO.input(self.gpio):
          print("high")
          print(GPIO.input(self.gpio))
          return 100.0
        else:
          return 0.0
      else:
        return -1
      
   def get_avg_duty(self):
      if (p1._p_avg is not None) and (p1._hp_avg is not None):
        if ((time.time() - self._high_tick) < (1 / self._min_freq)):
          return 100.0 * self._hp_avg/self._p_avg
        elif GPIO.input(self.gpio):
          return 100.0
        else:
          return 0.0
      else:
        return -1
      
p1 = PWM_read(24)

try:
    while True:
        #print "%.f Hz, %.f Hz, %.f" % (freq_rise, freq_fall, duty)
        print("g={} f={:.1f} f={:.1f} dc={:.1f} dc={:.1f}".
            format(24, p1.get_freq(), p1.get_avg_freq(), p1.get_duty(), p1.get_avg_duty()))
        #p1._p = None
        #p1._hp = None
        time.sleep(1)   # Detect every second

except KeyboardInterrupt: # trap a CTRL+C keyboard interrupt
    print("keyboard exit")
finally:
    p1.cancel() # resets all GPIO ports used by this function

 
