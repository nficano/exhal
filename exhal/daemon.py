import atexit
import os
import sys
import time
from contextlib import suppress
from signal import SIGTERM


class Daemon:
    def __init__(self, pidfile=None):
        self.pidfile = pidfile or os.path.join("/var/run/exhal.service")

    def start(self):
        try:
            self.get_pidfile()
        except IOError:
            pass
        finally:
            self.daemonize()
            self.run()

    def stop(self):
        try:
            pid = self.get_pidfile()
        except IOError:
            return
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            e = str(err.args)
            if e.find("No such process") > 0:
                self.delete_pidfile()
            else:
                sys.exit(1)

    def daemonize(self):
        self.fork()

        os.chdir("/")
        os.setsid()
        os.umask(0)

        self.fork()

        atexit.register(self.delete_pidfile)
        self.create_pidfile()

    def fork(self):
        try:
            if os.fork() > 0:
                sys.exit(0)
        except OSError as err:
            self.error(f"failed to fork a child process. Reason: {err}\n")

    def delete_pidfile(self):
        with suppress(FileNotFoundError):
            os.remove(self.pidfile)

    def create_pidfile(self):
        with open(self.pidfile, "w+") as fh:
            fh.write(str(os.getpid()) + "\n")

    def get_pidfile(self):
        with open(self.pidfile, "r") as fh:
            return int(fh.read().strip())

    def error(self, message):
        sys.stderr.write(f"{message}\n")
        sys.exit(1)

    def restart(self):
        self.stop()
        self.start()

    def run(self):
        raise NotImplementedError
