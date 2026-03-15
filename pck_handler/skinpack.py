import clr
import sys
from util import Logger
import os
import copy

clr.AddReference("OMI-Filetypes")

from OMI.Workers.Pck import PckFileReader, PckFileWriter
from OMI import ByteOrder
from OMI.Formats.Pck import PckFile
from OMI.Formats.Pck import PckAssetType

from enum import Enum

# 1. Define the Enum class
class Skins(Enum):
    WRITE = 1
    APPEND = 2

LOGGER = Logger()

class SkinPack:
    def __init__(self, pck_name, install_dir = None, dlc=False):
        if getattr(sys, "frozen", False):
            exe_dir = os.path.dirname(sys.executable)
        else:
            exe_dir = os.path.dirname(os.path.abspath(__file__))
        self.root_dir = exe_dir
        self.install_dir = install_dir
        self.reader = PckFileReader(ByteOrder.LittleEndian) # TODO: Add auto detection
        if os.path.exists(pck_name):
            self.pck = self.FromFile(pck_name)
        else:
            self.pck = PckFile(3)
        self.writer = PckFileWriter(self.pck, ByteOrder.LittleEndian)
        self.pck_name = pck_name
        self.dlc = dlc
        self.file_ids : list[str] = self._gen_files_list(self.pck)
        self.namespace_id = self.get_or_create_or_change_id_namespace()
        self.used_ids = []

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
            self.gen_unique_name(),
            PckAssetType.SkinFile
        )

        new_skin.SetData(filebytes)
        new_skin.AddProperty("DISPLAYNAME", displayname or filename)
        self._gen_files_list(self.pck)

    def add_skins(self, displayname: str = None, *filenames):
        for filename in filenames:
            self.add_skin(filename)

    def remove_skins(self, *ids):
        for id in ids:
            self.remove_skin(id)


    def add_skins_from_dir(self, dir_path, mode : int, new : bool = False, new_name : str = None):
        files_and_dirs : list[str] = os.listdir(dir_path)
        files : list[str] = list()
        if new:
            self.pck = PckFile(3)
            self.writer = PckFileWriter(self.pck, ByteOrder.LittleEndian)
            if new_name != None:
                os.remove(os.path.join(self.root_dir, self.pck_name + ".pck"))
                self.pck_name = new_name
            
            

        
        if mode == Skins.WRITE:
            self.file_ids.clear()
            self.pck.RemoveAll()
        
        for file in files_and_dirs:
            if os.path.isfile(file):
                files.append(file)

        for file in files:
            self.add_skin(file)

        self._gen_files_list(self.pck)

    def remove_skin(self, id):
        for asset in self.pck.GetAssets():
            asset = asset.Value
            fileName = asset.Filename
            
            if self.get_int_id(fileName) == self.get_int_id(id):
                self.file_ids.remove(str(self.get_int_id(asset.Value.Filename)))
                self.pck.RemoveAsset(asset)
        self._gen_files_list(self.pck)

    

    def gen_unique_name(self):
        self.get_or_create_or_change_id_namespace()

        if len(self.file_ids) >= 1:
            last_file_id = None
            if len(self.file_ids) > 0:
                last_file_id = self.file_ids[len(self.file_ids) - 1]
            else:
                last_file_id = self.namespace_id
            
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

    def _gen_files_list(self, pck):
        file_ids : list[str] = list()
        for asset in pck.GetAssets():
            fileid : str = asset.Value.Filename[7:]
            fileid = self.remove_exten(fileid)
            if len(fileid) == 8 and not "cape" in asset.Value.Filename:
                file_ids.append(fileid)
            else:
                while True:
                    answer = input(f"Invalid Skin File name found. remove or automatically rename {asset.Value.Filename} (r / n):")
                    if answer == "r":
                        self.file_ids.remove(str(self.get_int_id(asset.Value.Filename)))
                        self.pck.RemoveAsset(asset)

        file_ids.sort()

        return file_ids

    def save(self):
        self.writer.WriteToFile(self.pck_name)

    def find_used_ids(self):
        if self.install_dir == None:
            print("Unable to find taken ids, no install directory specified.")
            return False
        DLCs_path = os.path.join(self.install_dir, "Windows64Media", "DLC")
        DLCs : list[str] = os.listdir(DLCs_path)
        Skinpacks : list[str] = list()

        for DLC_index in range(0, len(DLCs) - 1):
            DLC_path = DLCs[DLC_index]
            if len(os.listdir(DLC_path)) < 2:
                Skinpacks.append(DLC_path)
        
        for Skinpack_path in Skinpacks:
            pck_file = os.listdir(Skinpack_path[0])

            dlc_skin_pack = SkinPack(pck_file, dlc=True)

            self.used_ids.append(dlc_skin_pack.get_or_create_id_namespace())

        return True
    
    def get_unused_id(self):
        if len(self.used_ids) == 0:
            if not self.find_used_ids(): return
        
        spaced_ids = []
        last = str()
        for id_index in range(0, len(self.used_ids) - 1):
            if id_index == 0:
                last = self.used_ids[id_index]
                spaced_ids.append[last]
                continue
            else:
                last = self.used_ids[id_index - 1]

            current = self.used_ids[id_index]
            if current - last > 100:
                spaced_ids.append(current)

            if len(spaced_ids) >= 2:
                break
        
        un_id = spaced_ids[0] + 100

        return un_id

    def get_or_create_or_change_id_namespace(self):
        self.find_used_ids()
        if len(self.file_ids) > 0 and not self.file_ids[0] in self.used_ids:
            self.namespace_id = self.file_ids[0]

        elif len(self.file_ids) == 0:
            self.namespace_id = self.get_unused_id()

        elif len(self.file_ids > 0) and self.file_ids[0] in self.used_ids:
            self.namespace_id = self.get_unused_id()
            self.change_id_namespace(self.namespace_id)

        return self.file_ids[0]
    
    def change_id_namespace(self, new_name_space):
        count = 0

        skin_info = {}

        for asset in self.pck.GetAssets():
            asset = asset.Value
            fileName = asset.Filename
            skinData = asset.get_Data()
            skinProperties = asset.GetProperties()
            
            skin_info[fileName] = [asset, skinData, skinProperties]


        for fileName, infoList in skin_info.items():
            new_skin = self.pck.CreateNewAsset(
                "dlcskin" + self.normalize_int_id(int(new_name_space) + count) + ".png",
                PckAssetType.SkinFile
            )
            dict_asset = infoList[0]
            dict_skinData = infoList[1]
            dict_skinProperties = infoList[2]

            new_skin.SetData(dict_skinData)
            for prop in dict_skinProperties:
                new_skin.AddProperty(prop.Key, prop.Value)

            count += 1
            
            self.file_ids.remove(str(self.get_int_id(asset.Value.Filename)))
            self.pck.RemoveAsset(dict_asset)
            self._gen_files_list(self.pck)


    def get_skin_asset(self, id):
        if int(id) == id:
            id = self.normalize_int_id()
        return self.pck.GetAsset("dlcskin" + id + ".png", PckAssetType.SkinFile)


    def normalize_int_id(self, id : int):
        un_id = str(id)

        for _ in range(8 - len(un_id)):
            un_id = "0" + un_id
        
        return un_id
    
    def get_int_id(self, id):
        if not int(id) == id:
            if not id[0].isdigit():
                id = id[7:]
            id = self.remove_exten(id)
        
        return int(id)

skinPack = SkinPack("GroupPack.pck")
skinPack.change_id_namespace("00002200")
skinPack.save()