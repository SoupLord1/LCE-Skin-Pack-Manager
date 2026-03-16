import os
import sys
import clr

if hasattr(sys, "frozen"):
    dll_dir = sys._MEIPASS
else:
    dll_dir = os.path.dirname(__file__)

os.add_dll_directory(dll_dir)

clr.AddReference(os.path.join(dll_dir, "OMI-Filetypes.dll"))

from OMI.Formats.Pck import PckAsset

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

class PckHelper():
    def get_asset_properties(asset : PckAsset):
        "returns a dictionary of property names and their values from an asset. SkinPack's get_skin_properties method can be used in place of this"
        prop_dict = {}
        if hasattr(asset, "Value"):
            asset = asset.Value
        
        for prop in asset.GetProperties:
            prop_dict[prop.Key] = prop.Value

        return prop_dict

