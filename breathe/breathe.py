import logging.config
import os
import time
from contextlib import suppress
from math import exp
from math import pi
from math import sin

import colorutils
from blinkstick import blinkstick
from blinkstick.blinkstick import BlinkStickException
from box import Box
from retry import retry
from usb import USBError


class Breathe:
    __slots__ = ["cfg", "led", "log", "_inhale_pattern", "_exhale_pattern"]

    def __init__(self, overrides=None):
        self.cfg = self._get_configuration(overrides)
        self.led = blinkstick.find_first()
        self.log = self._setup_logging(self.cfg.logging)
        self._inhale_pattern = []
        self._exhale_pattern = []

    def inhale(self):
        self._breathe(self._inhale_pattern)

    def exhale(self):
        self._breathe(self._exhale_pattern)

    @retry((BlinkStickException, USBError), tries=3, delay=2)
    def start(self):
        self._cache_respiratory_pattern()
        with suppress(KeyboardInterrupt):
            while True:
                start_time = time.time()
                self.exhale()
                self.inhale()
                time.sleep(1)
                runtime = round(time.time() - start_time, 2)
                self.log.debug("respiratory cycle runtime: %s/sec", runtime)

    def _breathe(self, pattern):
        samples = len(self._inhale_pattern + self._exhale_pattern)
        hold_time = self.cfg.period / samples
        for _, (red, blue, green) in enumerate(pattern):
            self.led.set_color(red=red, green=green, blue=blue)
            time.sleep(hold_time)

    def _modulate(self, i, hertz, period):
        return ((exp(-sin((i * 6.3) / (hertz * period)) + 1)) - 1) / pi * 2

    def _cache_respiratory_pattern(self):
        hue, sat, val = colorutils.hex_to_hsv(self.cfg.color)
        samples = self.cfg.hertz * self.cfg.period
        respiratory_cycle = list()

        for i in range(samples):
            val = self._modulate(i, self.cfg.hertz, self.cfg.period)
            if val > self.cfg.amplitude.hi or val < self.cfg.amplitude.lo:
                continue
            rgb = colorutils.hsv_to_rgb((hue, sat, val))
            respiratory_cycle.append(rgb)

        half = len(respiratory_cycle) // 2
        self._inhale_pattern = respiratory_cycle[:half]
        self._exhale_pattern = respiratory_cycle[half:]

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
