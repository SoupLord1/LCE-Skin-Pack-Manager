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
        self.pck_name = pck_name
        if os.path.isabs(pck_name):
            self.pck_path = pck_name
        elif not os.path.isabs(pck_name) and dlc:
            self.pck_path = os.path.join(self.install_dir, "Windows64Media", "DLC", pck_name)
        else:
            self.pck_path = os.path.join(self.root_dir, pck_name)
        self.reader = PckFileReader(ByteOrder.LittleEndian) # TODO: Add auto detection
        print(self.pck_path)
        if os.path.exists(self.pck_path):
            self.pck = self.reader.FromFile(self.pck_path)
            print("reading from file")
        else:
            print("creating new file")
            self.pck = PckFile(3)
        self.dlc = dlc
        self.used_ids = []
        self.file_ids : list[int] = self._gen_files_list(self.pck)
        if not self.dlc: self.namespace_id = self.create_or_change_id_namespace()


    def add_skin(self, filename, displayname: str = None):
        file_exten = self.get_exten(filename)
        print(f"File extension: {file_exten}")
        filename = self.remove_exten(filename)
        if filename.count("\\") == 0:
            filepath = os.path.join(self.root_dir, filename + file_exten)
        else:
            filepath = str(filename + file_exten)

        in_file = open(filepath, "rb")
        filebytes : bytes = in_file.read()
        in_file.close()

        un_name = self.gen_unique_name()

        new_skin = self.pck.CreateNewAsset(
            un_name,
            PckAssetType.SkinFile
        )

        new_skin.SetData(filebytes)
        new_skin.AddProperty("DISPLAYNAME", displayname or filename)
        self.file_ids = self._gen_files_list(self.pck)

    def add_skins(self, displayname: str = None, *filenames):
        for filename in filenames:
            self.add_skin(filename)

    def remove_skins(self, *ids):
        for id in ids:
            self.remove_skin(id)

    def remove_all_assets(self):
        self.file_ids.clear()
        asset_list = []
        for asset in self.pck.GetAssets():
            asset_list.append(asset)
        
        for asset in asset_list:
            self.pck.RemoveAsset(asset)



    def add_skins_from_dir(self, dir_path, mode : int, new_name : str = None):
        files_and_dirs : list[str] = os.listdir(dir_path)
        files : list[str] = list()
        if new_name != None:
            if os.path.exists(os.path.join(self.root_dir, self.pck_name)):
                os.remove(os.path.join(self.root_dir, self.pck_name))
            if self.get_exten(new_name):
                self.pck_name = new_name
            else:
                self.pck_name = new_name + ".pck"
        
        if mode == Skins.WRITE:
            self.remove_all_assets()
        
        for file in files_and_dirs:
            if os.path.isfile(os.path.join(dir_path, file)):
                files.append(os.path.join(dir_path, file))

        for file in files:
            self.add_skin(file)
        

    def remove_skin(self, id):
        for asset in self.pck.GetAssets():
            asset = asset.Value
            fileName = asset.Filename
            
            if self.get_int_id(fileName) == self.get_int_id(id):
                self.file_ids.remove(self.get_int_id(asset.Value.Filename))
                self.pck.RemoveAsset(asset)
        self.file_ids = self._gen_files_list(self.pck)

    

    def gen_unique_name(self):
        self.create_or_change_id_namespace()
        self.file_ids = self._gen_files_list(self.pck)
        num_ids = len(self.file_ids)

        un_id = self.get_str_name(self.namespace_id + num_ids)

        return un_id

    def get_exten(self, filename):
        if isinstance(filename, int):
            return None
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
        if isinstance(filename, int):
            filename = self.normalize_int_id(filename)
        exten = self.get_exten(filename)
        if exten != None:
            filename = filename[:-len(exten)]
        return filename

    def _gen_files_list(self, pck):
        file_ids : list[str] = []
        for asset in pck.GetAssets():
            filename = asset.Value.Filename
            if len(filename) == 19 and not "cape" in filename:
                pass
            else:
                if not self.dlc:
                    while True:
                        answer = input(f"Invalid Skin File name found. remove or automatically rename {filename} (r / n):")
                        if answer == "r":
                            self.pck.RemoveAsset(asset)
                        if answer == "n":
                            asset.Value.Filename = self.gen_unique_name()
                        else:
                            continue
                        break
                else:
                    continue

            fileid : str = filename[7:]
            fileid = self.remove_exten(fileid)
            fileid = self.get_int_id(fileid)

            if self.dlc:
                fileid = fileid - (fileid % 100)
                file_ids.clear()
                file_ids.insert(0, fileid)
                return file_ids
            
            file_ids.append(fileid)

        file_ids.sort()

        return file_ids

    def save(self):
        writer = PckFileWriter(self.pck, ByteOrder.LittleEndian)
        writer.WriteToFile(self.pck_name)

    def find_used_ids(self):
        if self.install_dir == None:
            print("Unable to find taken ids, no install directory specified.")
            return False
        DLCs_path = os.path.join(self.install_dir, "Windows64Media", "DLC")
        DLCs : list[str] = os.listdir(DLCs_path)
        Skinpacks : list[str] = list()

        for DLC_index in range(0, len(DLCs)):
            DLC_path = os.path.join(DLCs_path, DLCs[DLC_index])
            if len(os.listdir(DLC_path)) < 2:
                Skinpacks.append(DLC_path)
        
        for skinpck_path in Skinpacks:
            pck_file = os.listdir(skinpck_path)[0]

            dlc_skin_pack = SkinPack(os.path.join(skinpck_path, pck_file), dlc=True)

            self.used_ids.append(dlc_skin_pack.get_dlc_namespace_id())

        return True
    
    def get_unused_id(self):
        if len(self.used_ids) == 0:
            if not self.find_used_ids(): return
        
        spaced_ids = []
        last = str()
        for id_index in range(0, len(self.used_ids) - 1):
            if id_index == 0:
                last = self.used_ids[id_index]
                spaced_ids.append(last)
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

    def create_or_change_id_namespace(self):
        if self.dlc:
            self.namespace_id = self.file_ids[0]
            return
        
        self.find_used_ids()

        if len(self.file_ids) > 0 and not self.file_ids[0] in self.used_ids:
            self.namespace_id = self.file_ids[0]

        elif len(self.file_ids) == 0:
            self.namespace_id = self.get_unused_id()

        elif len(self.file_ids) and self.file_ids[0] in self.used_ids:
            self.namespace_id = self.get_unused_id()
            self.change_id_namespace(self.namespace_id)

        self.file_ids.insert(0, self.namespace_id)

    def get_dlc_namespace_id(self):
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

            file_id = self.get_int_id(asset.Filename)
            if file_id in self.file_ids:
                self.file_ids.remove(file_id)
            self.pck.RemoveAsset(dict_asset)
            self.file_ids = self._gen_files_list(self.pck)

            count += 1

    def get_skin_asset(self, id):
        if isinstance(id, int):
            id = self.normalize_int_id(id)
        return self.pck.GetAsset("dlcskin" + id + ".png", PckAssetType.SkinFile)


    def normalize_int_id(self, id : int):
        un_id = str(id)

        for _ in range(8 - len(un_id)):
            un_id = "0" + un_id
        
        return un_id
    
    def get_str_name(self, id):
        un_id = str(id)

        for _ in range(8 - len(un_id)):
            un_id = "0" + un_id

        return "dlcskin" + un_id + ".png"

    def get_int_id(self, id):
        print(id)
        if not isinstance(id, int):
            if not id[0].isdigit():
                id = id[7:]
            id = self.remove_exten(id)
        
        return int(id)
    
skinpack = SkinPack("GroupPack.pck", "C:\\Users\\logat\\OneDrive\\Documents\\LCEWindows64")
skinpack.add_skins_from_dir("C:\\Users\\logat\\OneDrive\\Documents\\GitHub\\LCE-Skin-Pack-Manager\\pck_handler\\tst_pack", mode=Skins.WRITE, new_name="Test_pack")
skinpack.save()