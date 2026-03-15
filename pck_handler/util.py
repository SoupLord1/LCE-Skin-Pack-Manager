import os
import sys
import clr

if hasattr(sys, "frozen"):
    dll_dir = sys._MEIPASS
else:
    dll_dir = os.path.dirname(__file__)

os.add_dll_directory(dll_dir)

clr.AddReference(os.path.join(dll_dir, "OMI-Filetypes.dll"))
from OMI.Workers.Pck import PckFileReader, PckFileWriter
from OMI import ByteOrder
from OMI.Formats.Pck import PckFile
from OMI.Formats.Pck import PckAssetType

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

