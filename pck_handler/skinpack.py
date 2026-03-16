from pathlib import Path

import clr
import sys
from util import Logger
import os

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
from OMI.Formats.Pck import PckAsset

from enum import Enum

# 1. Define the Enum class
class Skins(Enum):
    WRITE = 1
    APPEND = 2

LOGGER = Logger()

class SkinPack:
    """
    Class that represents a .pck skinpack.
    Arguments:
        pck_path: the path to the .pck file to initialize the class with if from_file is true. 
            This is also the path that will be saved to when save() is called, unless specified otherwise. Optional if pck_name is specified.

        pck_name: the name of the file that will be written to when save() is called. Optional if pck_path is specified.

        install_dir: the path to the installation of LCE. Optional

        dlc: specifies if the pck is being loaded from already existing DLCs. Optional

        from_file: specifies if self.pck will be created from the file that pck_path or pck_name point to. Default to true.

        overwrite: if from_file is true and pck_name isn't the same as the name of the file specified with pck_path, 
            the old .pck file with a different name will be deleted. Defaults to false
    """
    def __init__(self, pck_path = None, pck_name = None, install_dir = None, dlc=False, from_file = True, overwrite = False):
        if pck_name == None and pck_path == None:
            raise UnspecifiedException("Either pck_name or pck_path must be specified.")
        
        if self.get_exten(pck_name) == None:
            pck_name = pck_name + ".pck"

        if pck_name != None and pck_path == None and from_file and not os.path.exists(os.path.join(self.root_dir, self.pck_name)):
            print(f"Warning: The pck_name ({pck_name}) specified does not exist in the root directory, but from_file is true. A new PckFile will be created instead of being loaded from a file. Is this a mistake?")
        
        if pck_path != None and from_file and not os.path.exists(pck_path):
            print(f"Warning: The pck_path ({pck_path}) specified does not exist, but from_file is true. A new PckFile will be created instead of being loaded from the pck_path. Is this a mistake?")
        
        if overwrite and from_file and pck_name != pck_path_file_name:
            if os.path.exists(pck_path):
                os.remove(pck_path)
            else:
                print("Warning: specified pck_path doesn't exist, but overwrite is True. Is this a mistake?")

        exe_dir = os.path.dirname(os.path.abspath(__file__))
        self.root_dir = exe_dir

        self.install_dir = install_dir
        self.pck_name = pck_name

        if pck_path != None:
            if os.path.isabs(pck_path):
                self.pck_path = pck_path
            elif not os.path.isabs(pck_path) and dlc:
                self.pck_path = os.path.join(self.install_dir, "Windows64Media", "DLC", pck_path)
            else:
                self.pck_path = os.path.join(self.root_dir, self.pck_name)
        else:
            pck_path = self.pck_path = os.path.join(self.root_dir, pck_path)

        pck_path_file_name = Path(self.pck_path).name

        if self.pck_name == None:  self.pck_name = pck_path_file_name

        self.reader = PckFileReader(ByteOrder.LittleEndian) # TODO: Add auto detection
        print(self.pck_path)

        if os.path.exists(self.pck_path) and from_file:
            self.pck = self.reader.FromFile(self.pck_path)
            print("reading from file")
        else:
            print("creating new file")
            self.pck = PckFile(3)
        
        self.dlc = dlc
        self.used_ids = []
        self.file_ids : list[int] = self.gen_ids_from_files(self.pck)
        if not self.dlc: self.namespace_id = self.create_or_change_id_namespace()

    def add_skin(self, file_path, displayname: str = None):
        """
        Adds the skin from the specified file_path to the assets of self.pck, with the optional displayname.
        If displayname is not specified, the DISPLAYNAME property will be set to the name of the file without its extension.
        """
        file_exten = self.get_exten(file_path)
        print(f"File extension: {file_exten}")
        file_name = self.remove_exten(Path(file_path).name)
        if not os.path.isabs(file_path):
            file_path = os.path.join(self.root_dir, file_path + file_exten)
        else:
            file_path = str(file_path + file_exten)

        in_file = open(file_path, "rb")
        filebytes : bytes = in_file.read()
        in_file.close()

        un_name = self.gen_unique_id()

        new_skin = self.pck.CreateNewAsset(
            un_name,
            PckAssetType.SkinFile
        )

        new_skin.SetData(filebytes)
        new_skin.AddProperty("DISPLAYNAME", displayname or file_name)
        self.file_ids = self.gen_ids_from_files(self.pck)

    def add_skins(self, displayname: str = None, *file_paths):
        """
        Adds all skins with the file paths specified. Paths can be relative or absolute
        """
        for filename in file_paths:
            self.add_skin(filename)

    def remove_skins(self, *ids):
        """Removes all skins with the ids specified"""
        for id in ids:
            self.remove_skin(id)

    def remove_all_assets(self):
        """
        Removes all assets currently contained within self.pck
        """
        self.file_ids.clear()
        asset_list = []
        for asset in self.pck.GetAssets():
            asset_list.append(asset)
        
        for asset in asset_list:
            self.pck.RemoveAsset(asset)

    def get_assets(self):
        """Returns a list of the PckAssets currently contained within self.pck"""
        asset_list = []
        for asset in self.pck.GetAssets():
            asset_list.append(asset)
        return asset_list

    def update_assets(self, name: str , data : bytes,  assetType : PckAssetType, properties: dict[str, str] = {}):
        """
        overwrites asset in the pack if it exists, or creates it. self.pck.RemoveAsset(asset) can be used to remove assets self.pck.       
        """

        if self.pck.HasAsset(name, assetType):
            self.pck.RemoveAsset(self.pck.GetAsset(name, assetType))

        new_asset = self.pck.CreateNewAsset(
            name,
            assetType
        )

        new_asset.SetData(data)
        for key, value in properties.items():
            new_asset.AddProperty(key, value)

    def get_skin_properties(self, id):
        """returns a dictionary of property names and their values from a skin id. Id must only contain digits"""
        id = str(id)
        asset = self.pck.GetAsset("dlcskin" + id + ".png", PckAssetType.SkinFile)
        prop_dict : dict[str, str] = {}
        if hasattr(asset, "Value"):
            asset = asset.Value
        
        for prop in asset.GetProperties:
            prop_dict[prop.Key] = prop.Value

        return prop_dict
    
    def update_skin_properties(self, id, prop_dict : dict[str, str]):
        """
        adds or updates the skin asset with the specified id with the properties from the property dict. Id must only contain digits
        Format:
            {
            propertyName: propertyValue,
            property2Name: property2Value
            }
        """
        exists, asset = self.pck.TryGetAsset(self.get_str_name(id), PckAssetType.SkinFile)
        if not exists: 
            print(f"(self.update_skin_properties({id}, {prop_dict})): id specified has no corresponding asset")
            return
        for key, value in prop_dict.items():
            asset.SetProperty(key, value)

    def remove_skin_properties(self, id, *names):
        """
        removes the properties with names from prop_dict (if they exist) from the skin asset with the specified id. Id must only contain digits
        """
        exists, asset = self.pck.TryGetAsset(self.get_str_name(id), PckAssetType.SkinFile)
        if not exists: 
            print(f"(self.remove_skin_properties({id}, {names})): id specified has no corresponding asset")
            return
        
        for name in names:
            asset.RemoveProperties(name)


    def add_skins_from_dir(self, dir_path, mode : int, new_name : str = None):
        """
        Adds all files from the directory specified to the self.pck as skin files, with proper ids.
        The DISPLAYNAME property of the skin assets will be the filename of the file it was generated with.

        Optional new_name deletes the .pck file that self.pck was opened with (if it was opened with a file), 
        and will write to new_name once save() is called.

        the mode argument specifies the way in which the files from the directory will be added to the current pack.
        Skins.WRITE will overwrite all assets in self.pck. Skins.APPEND will add files from directory to the assets of self.pck.
        """
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
            if self.get_exten(file) == ".png":
                self.add_skin(file)

    def remove_skin(self, id):
        """
        Removes the skin with the id specified from the assets of self.pck as well as removes its id from self.file_ids.
        id can be in integer or string form. 
        """
        for asset in self.pck.GetAssets():
            asset = asset.Value
            fileName = asset.Filename
            
            if self.get_int_id(fileName) == self.get_int_id(id):
                self.file_ids.remove(self.get_int_id(asset.Value.Filename))
                self.pck.RemoveAsset(asset)
        self.file_ids = self.gen_ids_from_files(self.pck)
    
    def gen_unique_id(self):
        """
        Generates a unique_id for use with a new skin.
        """
        self.create_or_change_id_namespace()
        self.file_ids = self.gen_ids_from_files(self.pck)
        num_ids = len(self.file_ids)

        un_id = self.get_str_name(self.namespace_id + num_ids)

        return un_id

    def get_exten(self, filename : str):
        """
        Returns the extension of a str filename, if one exists
        """
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
    
    def remove_exten(self, filename : str):
        """
        Removes the extension from a str filename, if one exists
        """
        if isinstance(filename, int):
            filename = self.normalize_int_id(filename)
        exten = self.get_exten(filename)
        if exten != None:
            filename = filename[:-len(exten)]
        return filename

    def gen_ids_from_files(self, pck):
        """
        Looks through the assets self.pck to find valid ids to add to a file_ids, then sorts the list before returing it.
        """
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
                            asset.Value.Filename = self.gen_unique_id()
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

    def save(self, dir : str =None):
        """
        Writes the current self.pck object to a .pck file with self.pck_name as the file name.
        Optional dir argument specifies the directory that the file will be written to.
        If dir is not specified, it will be written to self.pck_path
        """
        writer = PckFileWriter(self.pck, ByteOrder.LittleEndian)
        if dir != None:
            writer.WriteToFile(os.path.join(dir, self.pck_name))
        else:
            writer.WriteToFile(self.pck_path)
    def find_used_ids(self):
        """
        Looks through skinpack dlc .pck files in the specified install_dir, finds their id namepsace, and adds it to self.used_ids.
        """
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
        """
        Uses self.used_ids to find an unused id that is the closest to 0.
        """
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
        """
        If the current namespace id conflicts or no namespace id exists:
            Finds an unused id (based on install_dir), and sets self.namespace_id to that value.
            If the skinpack already had a namespace_id before the change, all assets in the pck are renamed to reflect the change using self.change_id_namespace
        otherwise: does nothing. 
        
        If the skinpack class was initialized as a dlc, simply changes self.file_ids[0] to self.namespace_id (to avoid potential infinite recursion)
        """
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
        """
        Used with skinpacks initialized as dlcs to return the namespace, even if self.namespace_id ins't initialized.
        Mainly exists to make the code look nicer
        """
        return self.file_ids[0]
    
    def change_id_namespace(self, new_name_space):
        """
        Renames all assets in the pck to reflect the new new_name_space specified.
        """
        self.namespace_id = new_name_space
        
        if len(self.pck.GetAssets()) == 0:
            return
        
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
            self.file_ids = self.gen_ids_from_files(self.pck)

            count += 1

    def get_skin_asset(self, id):
        """
        Returns the skinpack asset object (PckAsset) that has the specified id
        """
        if isinstance(id, int):
            id = self.normalize_int_id(id)
        return self.pck.GetAsset("dlcskin" + id + ".png", PckAssetType.SkinFile)

    def normalize_int_id(self, id : int):
        """
        Converts the id specified into a string and changes it into an 8 character id with leading zeros
        """
        un_id = str(id)

        for _ in range(8 - len(un_id)):
            un_id = "0" + un_id
        
        return un_id
    
    def get_str_name(self, id):
        """
        Converts the id specified into a filename suitable for a minecraft legacy skin pack. 
        id specified must already contain only digits, no prefix or file extension
        """
        un_id = str(id)

        for _ in range(8 - len(un_id)):
            un_id = "0" + un_id

        return "dlcskin" + un_id + ".png"

    def get_int_id(self, id):
        """
        Changes a string id into an int id. Id specified can have file extension and/or prefix.
        """
        print(id)
        if not isinstance(id, int):
            if not id[0].isdigit():
                id = id[7:]
            id = self.remove_exten(id)
        
        return int(id)
    
class UnspecifiedException(Exception):
    pass

skinpack = SkinPack("GroupPack.pck")