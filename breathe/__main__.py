from math import exp
from math import pi
from math import cos
import sys
import time

import colorutils
from blinkstick import blinkstick

PULSE_DELAY = 0.02
OFF_DELAY = 2
STEPS = 120
PURPLE = "#7F007F"
COLOR = PURPLE


def breathe(color, steps):
    hue, sat, val = colorutils.hex_to_hsv(color)
    for i in range(steps):
        brightness = get_brightness(val, steps, i)
        yield colorutils.hsv_to_rgb((hue, sat, brightness))


def pulse(color, steps, pulse_delay):
    for rgb in breathe(color, steps):
        set_colors(rgb)
        time.sleep(pulse_delay)


def get_brightness(max_brightness, total, indx):
    x = 6.28  # 2 * pi
    y = 0.36  # 1 / e    
    z = 2.35  # e - 1 / e
    return float((exp(-cos(x * (indx / total))) - y) * (max_brightness / z))


def set_colors(rgb):
    red, green, blue = rgb
    bstick = blinkstick.find_first()
    bstick.set_color(red=red, green=green, blue=blue)


def main():
    try:
        while True:
            pulse(COLOR, STEPS, PULSE_DELAY)
            time.sleep(OFF_DELAY - (time.time() % OFF_DELAY))
    except KeyboardInterrupt:
        sys.exit()


if __name__ == "__main__":
    main()
