import logging.config
import os
import time
from contextlib import suppress
from itertools import cycle
from math import cos
from math import exp
from math import pi

import colorutils
from blinkstick import blinkstick
from blinkstick.blinkstick import BlinkStickException
from box import Box
from retry import retry
from usb import USBError


class Breathe:
    __slots__ = ["cfg", "led", "log"]

    def __init__(self, overrides=None):
        self.cfg = self._get_configuration(overrides)
        self.led = blinkstick.find_first()
        self.log = self._setup_logging(self.cfg.logging)

    @retry((BlinkStickException, USBError), tries=3, delay=2)
    def run_forever(self):
        seq = self.get_oscillation_cycle()
        self.breathe(seq)

    def breathe(self, seq):
        with suppress(KeyboardInterrupt):
            tick = self.cfg.steps / (1.0 * len(seq))
            for red, blu, grn in cycle(seq):
                self.led.set_color(red=red, green=grn, blue=blu)
                time.sleep(tick)

    def get_oscillation_cycle(self):
        hue, sat, val = colorutils.hex_to_hsv(self.cfg.color)
        samples = self.cfg.frequency * self.cfg.steps
        rgb_sequence = list()
        for idx, i in enumerate(range(samples)):
            val = exp(-cos((i * 4 * pi) / samples)) / 2
            if val > self.cfg.max_amplitude or val < self.cfg.min_amplitude:
                continue
            rgb = colorutils.hsv_to_rgb((hue, sat, val))
            rgb_sequence.append(rgb)
        return rgb_sequence

    def _get_yaml(self, fp):
        with open(fp) as fh:
            return Box.from_yaml(fh.read())

    def _get_configuration(self, overrides):
        _this_dir = os.path.dirname(os.path.abspath(__file__))
        fp = os.path.join(_this_dir, "settings.yml")
        cfg = self._get_yaml(fp)

        try:
            overrides_config = self._get_yaml(overrides)
            cfg.update(overrides_config)
        except (FileNotFoundError, TypeError):
            return cfg
        return cfg

    def _setup_logging(self, log_cfg):
        logging.config.dictConfig(log_cfg)
        return logging.getLogger("breathe")
