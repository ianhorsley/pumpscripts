import RPi.GPIO as GPIO
import time

#Look at http://abyz.me.uk/rpi/pigpio/python.html#event_callback
# To get faster and more accurate reading.

# Pin configuration
TACH = 24       # Fan's tachometer output pin
PULSE = 1       # Noctua fans puts out two pluses per revolution
WAIT_TIME = 1   # [s] Time to wait between each refresh

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(TACH, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Pull up to 3.3V

# Setup variables
t_fell = t_rise =  time.time()
duty = 0
freq_fall = freq_rise = 0

# Calculate pulse frequency and RPM
def change(n):
    if GPIO.input(TACH) :
        global t_rise
        global freq_rise

        rise_t_temp = time.time()

        dt = rise_t_temp - t_rise
        if dt < 0.005: return # Reject spuriously short pulses

        freq_rise = 1 / dt
        t_rise = rise_t_temp
    else:

        global t_fell
        global t_rise
        global freq_fall
        global duty

        fall_t_temp = time.time()

        dt = fall_t_temp - t_fell
        if dt < 0.005: return # Reject spuriously short pulses

        freq_fall = 1 / dt
        t_fell = fall_t_temp

        duty = 100 * (fall_t_temp - t_rise) / dt

# Add event to detect
GPIO.add_event_detect(TACH, GPIO.BOTH, change)

try:
    while True:
        print("%.f Hz, %.f Hz, %.f" % (freq_rise, freq_fall, duty))
        freq_rise = freq_fall = duty = 0
        time.sleep(1)   # Detect every second

except KeyboardInterrupt: # trap a CTRL+C keyboard interrupt
    GPIO.cleanup() # resets all GPIO ports used by this function
