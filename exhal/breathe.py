import asyncio
import logging.config
import os
import time
from itertools import cycle
from math import cos
from math import exp
from math import pi
from signal import SIGHUP
from signal import SIGINT
from signal import SIGTERM
from threading import Thread

import colorutils
from blinkstick import blinkstick
from blinkstick.blinkstick import BlinkStickException
from box import Box
from retry import retry
from usb import USBError


class Breathe:
    __slots__ = ["cfg", "led", "log", "loop"]

    def __init__(self, overrides=None):
        super().__init__()
        self.cfg = self._get_configuration(overrides)
        self.led = blinkstick.find_first()
        self.log = self._setup_logging(self.cfg.logging)
        self.loop = asyncio.new_event_loop()

    def start_event_loop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    async def stop_event_loop(self, loop):
        tasks = [
            task
            for task in asyncio.all_tasks()
            if task is not asyncio.current_task()
        ]
        [task.cancel() for task in tasks]
        await asyncio.gather(*tasks, return_exceptions=True)
        self.led.morph()
        loop.stop()

    @retry((BlinkStickException, USBError), tries=3, delay=2)
    def start(self):
        seq = self.get_oscillation_cycle()
        thread = Thread(target=self.start_event_loop, args=(self.loop,))
        thread.start()
        time.sleep(self.cfg.delay)
        asyncio.run_coroutine_threadsafe(self.breathe(seq), self.loop)
        for signal in (SIGHUP, SIGTERM, SIGINT):
            self.loop.add_signal_handler(
                signal,
                lambda signal=signal: asyncio.create_task(
                    self.stop_event_loop(self.loop)
                ),
            )

    def stop(self):
        self.loop.close()

    async def breathe(self, seq):
        tick = self.cfg.steps / (1.0 * len(seq))
        red, blu, grn = seq[0]
        self.led.morph(red=red, blue=blu, green=grn)
        for red, blu, grn in cycle(seq):
            self.led.set_color(red=red, green=grn, blue=blu)
            await asyncio.sleep(tick - (time.time() % tick))

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
