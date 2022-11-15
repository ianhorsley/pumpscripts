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

def _calc_freq(t_base):
    """calculate the time change and frequency from base time"""
    curr_t = time.time()

    dt = curr_t - t_base
    if dt < 0.005:
        raise ValueError("Pulse to short") # Reject spuriously short pulses

    freq = 1 / dt

    return curr_t, freq

# Calculate pulse frequency and RPM
def change(n):
    global t_fell
    global t_rise
    global freq_fall
    global freq_rise
    global duty

    try:
        if GPIO.input(TACH) :
            t_rise, freq_rise = _calc_freq(t_rise)
        else:
            t_fell, freq_fall = _calc_freq(t_fell)
            duty = 100 * (t_fell - t_rise) / dt
    except ValueError as ve:
        print(ve)


# Add event to detect
GPIO.add_event_detect(TACH, GPIO.BOTH, change)

try:
    while True:
        print("%.f Hz, %.f Hz, %.f" % (freq_rise, freq_fall, duty))
        freq_rise = freq_fall = duty = 0
        time.sleep(1)   # Detect every second

except KeyboardInterrupt: # trap a CTRL+C keyboard interrupt
    GPIO.cleanup() # resets all GPIO ports used by this function
