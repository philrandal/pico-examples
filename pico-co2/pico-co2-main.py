# Requires the following micropython libraries - install these to the Pi Pico with Thonny
# errno, ffilib, os, scd30, signal, ssd1306, stat
# Rename this file to "main.py" and save to the Pico so that it runs automatically on power on.

# original code from https://www.tindie.com/products/rubikcuber/pico-co2-sensor-bare-pcb-raspberry-pi/

import time
import math
from machine import Pin, I2C
from machine import WDT
from scd30 import SCD30
from ssd1306 import SSD1306_I2C

# Initialise the two switches (not currently used)
sw1 = Pin(18, Pin.IN, None)
sw2 = Pin(19, Pin.IN, None)

# Set the RGB LED pins
led_rgb_r = Pin(2, Pin.OUT)
led_rgb_g = Pin(3, Pin.OUT)
led_rgb_b = Pin(4, Pin.OUT)

# Function to set the color of the RGB
def led_set_rgb(r, g, b):
    led_rgb_r.value(r)
    led_rgb_g.value(g)
    led_rgb_b.value(b)

# Set the RGB LED to white during initialisation
led_set_rgb(1,1,1)

# Utility function to convert a second count to hours:minutes:seconds
def secondsToString(s):
    hour = math.floor(s/3600)
    minute = math.floor((s-(hour*3600))/60)
    second = s - (60 * minute) - (3600 * hour);
    return '{:02d}:{:02d}:{:02d}'.format(hour, minute, second)

# Initialise the i2c interface
i2c=I2C(0, sda=Pin(12), scl=Pin(13), freq=400000)

# Initialise the SCD30 sensor
scd30 = SCD30(i2c, 0x61)
# set measurement interval to 3 seconds as per
# https://www.rainer-gerhards.de/2021/01/sensirion-scd-30-different-co2-readings-depending-on-measurement-interval/
scd30.set_measurement_interval(3)
scd30.start_continous_measurement()

# Wait for 1.5 seconds to ensure the OLED is ready
time.sleep(1.5)

# Initialise the OLED screen
oled = SSD1306_I2C(128, 64, i2c)
oled.show()

# Store the start time to use for deriving the uptime
start = time.time()

# Initialise the Watchdog timer timout (5 seconds)
wdt = WDT(timeout=5000)

# A callback to handle the button presses
def switch_pressed(p):
    print('pin change', p)

# Set up the two switches with callback
sw1.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=switch_pressed)
sw2.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=switch_pressed)

# The main loop
while True:
    # Reset the watchdog timer
    wdt.feed()
    # If the sensor has a value...
    if scd30.get_status_ready():
        # Read the sensor data
        m = scd30.read_measurement()
        if m is not None:
            # Print the sensor data to the screen
            oled.fill(0);
            oled.text("CO2: " + ('%.2f' % m[0]) + " ppm", 0, 0)
            oled.text("Temp: " + ('%.2f' % m[1]) + " C", 0, 10)
            oled.text("Hum:  " + ('%.2f' % m[2]) + " %", 0, 20)
            runtime = (time.time() - start)
            oled.text("uptime: " + secondsToString(runtime), 0, 50)
            oled.show()
            # Set the RGB LED
            # Green: 0 - 599 ppm
            # Blue : 600-799 ppm
            # Red  : 800+ ppm
            if(m[0] <= 600):
                led_set_rgb(0,1,0)
            elif (m[0] <= 800):
                led_set_rgb(0,0,1)
            else:
                led_set_rgb(1,0,0)
        # Poll once every 3 seconds
         time.sleep(3)
    else:
        # Wait 0.2 seconds and then try again
        time.sleep(0.2)
