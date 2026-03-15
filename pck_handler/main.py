import clr
import sys
from util import Logger
import os

clr.AddReference("OMI-Filetypes")

from OMI.Workers.Pck import PckFileReader, PckFileWriter
from OMI import ByteOrder
from OMI.Formats.Pck import PckFile
from OMI.Formats.Pck import PckAssetType
import OMI


LOGGER = Logger()

class SkinPack:
    def __init__(self, pck_name, install_dir = None):
        if getattr(sys, "frozen", False):
            exe_dir = os.path.dirname(sys.executable)
        else:
            exe_dir = os.path.dirname(os.path.abspath(__file__))
        self.root_dir = exe_dir
        self.install_dir = install_dir
        self.reader = PckFileReader(ByteOrder.LittleEndian) # TODO: Add auto detection
        self.pck = self.reader.FromFile(pck_name)
        self.pck_name = pck_name
        self.file_ids = []
        self.used_ids = []
        self._gen_files_list()

        print(self.pck.__class__)

    def add_skin(self, filename, displayname: str = None):
        file_exten = self.get_exten(filename)
        filename = self.remove_exten(filename)
        if filename.count("\\") == 0:
            filepath = os.path.join(self.root_dir, filename + file_exten)
        else:
            filepath = str(filename)

        in_file = open(filepath, "rb")
        filebytes : bytes = in_file.read()
        in_file.close()

        new_skin = self.pck.CreateNewAsset(
            self.gen_unique_id(),
            PckAssetType.SkinFile
        )

        new_skin.SetData(filebytes)
        new_skin.AddProperty("DISPLAYNAME", displayname or filename)
        self._gen_files_list()


    def gen_unique_id(self):
        if len(self.file_ids) >= 1:
            last_file_id = self.file_ids[len(self.file_ids) - 1]
            last_file_exten = ".png"
            last_file_id = self.remove_exten(last_file_id)

            int_last_id = int(last_file_id)
            un_id = int_last_id + 1
            un_id = str(un_id)

            for _ in range(8 - len(un_id)):
                un_id = "0" + un_id

            un_id = "dlcskin" + un_id + last_file_exten

        else:
            un_id = "dlcskin" + self.get_unused_id() + last_file_exten

        #TODO: Add a condition to check if current ids in pack are used, and then replace with unused ones

        return un_id

    def get_exten(self, filename):
        exten_index = filename.rfind(".")
        if exten_index != -1:
            file_exten = filename[exten_index:]
        else:
            file_exten = None
            exten_index = None

        if exten_index:
            file_exten = filename[exten_index:]

        return file_exten
    
    def remove_exten(self, filename):
        exten = self.get_exten(filename)
        if exten != None:
            filename = filename[:-len(exten)]
        return filename

    def _gen_files_list(self):
        for asset in self.pck.GetAssets():
            fileid : str = asset.Value.Filename[7:]
            fileid = self.remove_exten(fileid)
            if len(fileid) == 8:
                self.file_ids.append(asset.Value.Filename[7:])
            else:
                print("Invalid Skin File name found. Removing invalid skin file " + asset.Value.Filename + "...")
        self.file_ids.sort()

    def save(self):
        writer = PckFileWriter(self.pck, ByteOrder.LittleEndian)
        writer.WriteToFile(self.pck_name)

    def find_used_ids(self, install_dir):
        pass # TODO: Implement this

    def get_unused_id(self):
        pass # TODO: Implement this

skinPack = SkinPack("GroupPack.pck")
skinPack.add_skin("gigachad.png")
skinPack.save()
