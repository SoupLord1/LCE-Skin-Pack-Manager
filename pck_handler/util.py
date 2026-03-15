import os
import sys


class Logger():
    def __init__(self, filename="run.log"):
        if getattr(sys, "frozen", False):
            exe_dir = os.path.dirname(sys.executable)
        else:
            exe_dir = os.path.dirname(os.path.abspath(__file__))

        self.filename = os.path.join(exe_dir, filename)

    def log(self, msg : str, w_mode : str = "a", end="\n"):
        with open(self.filename, w_mode) as log_file:
            log_file.write(msg + end)