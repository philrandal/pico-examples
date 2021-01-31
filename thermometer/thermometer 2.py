# display temperature on Pimoroni pico display
# cycle between current temperature, minimum, and maximum

import picodisplay as display
import machine
import utime

def get_temp():
    sensor_temp = machine.ADC(4)
    conversion_factor = 3.3 / (65535)
    reading = sensor_temp.read_u16() * conversion_factor
    degrees= 27 - (reading - 0.706)/0.001721
    return degrees

def display_temp(temp,desc):
    deg = "{:.1f}".format(temp)
    display.set_pen(0,0,0)
    display.clear()
    # display temperature in
    # blue if it's too cold,
    # green if it's ok,
    # red if too hot
    if temp < 15:
        display.set_pen(0,0,255)
    elif temp > 25:
        display.set_pen(255,0,0)
    else:
        display.set_pen(0,255,0)
    txt = deg + desc
    display.text(txt, 50, 50, 240, 4)
    display.update()

width = display.get_width()
height = display.get_height()
display_buffer = bytearray(width * height * 2)
display.init(display_buffer)
# Set the backlight to 50%
display.set_backlight(0.5)
display.set_pen(0,0,0)
display.clear()

oldtemp = get_temp()
mintemp = oldtemp
maxtemp = oldtemp
utime.sleep(5)
count = 0
while True:
    currtemp = get_temp()
    if currtemp > maxtemp:
        maxtemp = currtemp
    elif currtemp < mintemp:
        mintemp = currtemp
    # display the average of the last two samples
    temperature = (oldtemp+currtemp)*0.5
    # cycle through current, min, and max temperatures
    count += 1
    if count == 5:
        display_temp(mintemp, " min")
    elif count == 10:
        display_temp(maxtemp, " max")
        count = 0
    else:
        display_temp(temperature, "")

    oldtemp = currtemp
    # you could use weighted averages by
    # setting oldtemp=temperature
    utime.sleep(5)
