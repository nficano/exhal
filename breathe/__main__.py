import math
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


def get_brightness(max_brightness, total_steps, step):
    return float(
        (math.exp(-math.cos(2 * math.pi * (step / total_steps))) - 1 / math.e)
        * (max_brightness / (math.e - 1 / math.e))
    )


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
