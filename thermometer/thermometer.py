# display temperature on Pimoroni pico display

import picodisplay as display
import machine
import utime

def get_temp():
    sensor_temp = machine.ADC(4)
    conversion_factor = 3.3 / (65535)
    reading = sensor_temp.read_u16() * conversion_factor
    degrees= 27 - (reading - 0.706)/0.001721
    return degrees

width = display.get_width()
height = display.get_height()
display_buffer = bytearray(width * height * 2)
display.init(display_buffer)

# Set the backlight to 50%
display.set_backlight(0.5)

oldtemp = get_temp()
while True:
    currtemp = get_temp()
    # display the average of the last two samples
    temperature = (oldtemp+currtemp)*0.5
    deg = "{:.1f}".format(temperature)
    #print(deg)
    display.set_pen(0,0,0)
    display.clear()
    # display temperature in blue if it's too cold,
    # green if it's ok, red if too hot
    if temperature < 15:
        display.set_pen(0,0,255)
    elif temperature > 25:
        display.set_pen(255,0,0)
    else:
        display.set_pen(0,255,0)
    display.text(deg, 95, 50, 240, 5)
    display.update()
    oldtemp = currtemp
    # you could use weighted averages by
    # setting oldtemp=temperature
    utime.sleep(5)
