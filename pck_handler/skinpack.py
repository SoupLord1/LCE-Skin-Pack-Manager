# MARK: Imports/Setup
from pathlib import Path

import clr
import sys
from util import Logger
from PIL import Image
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

class Skins(Enum):
    WRITE = 1
    APPEND = 2

LOGGER = Logger()

# MARK: SkinPack Class

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
    def __init__(self, pck_path : str = None, pck_name : str = None, install_dir : str = None, dlc : bool = False, from_file : bool = True, overwrite : bool = False):
        if pck_name == None and pck_path == None:
            raise UnspecifiedException("Either pck_name or pck_path must be specified.")
        
        if pck_path != None:
            pck_path_file_name = Path(pck_path).name
        else:
            pck_path_file_name = pck_name

        exe_dir = os.path.dirname(os.path.abspath(__file__))
        self.root_dir = exe_dir

        if self.get_exten(pck_name) == None:
            pck_name = pck_name + ".pck"

        if pck_name != None and pck_path == None and from_file and not os.path.exists(os.path.join(self.root_dir, pck_name)):
            print(f"Warning: The pck_name ({pck_name}) specified does not exist in the root directory, but from_file is true. A new PckFile will be created instead of being loaded from a file. Is this a mistake?")
        
        if pck_path != None and from_file and not os.path.exists(pck_path):
            print(f"Warning: The pck_path ({pck_path}) specified does not exist, but from_file is true. A new PckFile will be created instead of being loaded from the pck_path. Is this a mistake?")
        
        if overwrite and from_file and pck_name != pck_path_file_name:
            if os.path.exists(pck_path):
                os.remove(pck_path)
            else:
                print("Warning: specified pck_path doesn't exist, but overwrite is True. Is this a mistake?")

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
            self.pck_path = os.path.join(self.root_dir, self.pck_name)

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

        self.file_ids = []
        result, error_msg = self.gen_ids_from_files(self.pck)
        if not result:
            print(error_msg)
            return (False, "An error occured when generating ids from files")
        else:
            self.file_ids = result

        self.namespace_id = 0
        if not self.dlc: self.create_or_change_id_namespace()

    # MARK: Skin Editng Methods

    def add_skin(self, file_path : str, displayname: str = None, index : int = None):
        """
        Adds the skin from the specified file_path to the assets of self.pck, with the optional displayname.
        If displayname is not specified, the DISPLAYNAME property will be set to the name of the file without its extension.
        Optional index value specifies where the id the skin will be given (relative to namespace), and what its position will be in the pack.
        All skins after the index where the skin was inserted will be pushed forward, including the skin that was previously at the index specified.
        Negative indexes are not supported.

        Return Value:
            if function has no errors, function returns (True, ""). Otherwise, it returns (False, error_msg)
        """

        file_exten = ".png"
        file_name = self.remove_exten(Path(file_path).name)
        if not os.path.isabs(file_path):
            file_path = os.path.join(self.root_dir, self.remove_exten(file_path) + file_exten)
        else:
            file_path = str(self.remove_exten(file_path) + file_exten)

        if not os.path.exists(file_path):
            return (False, f"No file with the specified file path {file_path} exists or specified path is not a valid skin file (must be .png) (Absoulte Path: {os.path.isabs(file_path)})")
        if file_exten != ".png":
            return (False, f"The file {Path(file_path).name} specified is not a valid skin file (Skin files must be pngs with 64x32 pixel dimensions)")
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                if not(width == 64 and height == 32):
                    return (False, f"The file {Path(file_path).name} specified is not a valid skin file (Skin files must be pngs with 64x32 pixel dimensions)")
        except Exception as e:
            return (False, f"an error occured wile reading the skin file with name {Path(file_path).name}")


        in_file = open(file_path, "rb")
        filebytes : bytes = in_file.read()
        in_file.close()

        un_name = self.gen_unique_id()

        new_skin : PckAsset = self.pck.CreateNewAsset(
            un_name,
            PckAssetType.SkinFile
        )

        new_skin.SetData(filebytes)
        new_skin.AddProperty("DISPLAYNAME", displayname or file_name)
        if index and index != self.pck.AssetCount - 1:
            if index >= self.pck.AssetCount:
                print(f"(add_skin({file_path}, {displayname}, {index})): Skins cannot be added out of sequence (index {index} too high for skin count {self.pck.AssetCount - 1}).  Skin will be appended to the pack")
                return (False, f"Skins cannot be added out of sequence (index {index} too high for skin count {self.pck.AssetCount - 1}).  Skin will be appended to the pack")
            self.pck.RemoveAsset(new_skin)
            new_skin.Filename = self.get_str_name(self.namespace_id + index)
            self.shift_ids_forward(start_index=index)
            self.pck.InsertAsset(index, new_skin)

        result, error_msg = self.gen_ids_from_files(self.pck)
        if not result:
            print(error_msg)
            return (False, "An error occured when generating ids from files")
        else:
            self.file_ids = result
        
        return (True, "")

    def add_skins(self, *file_paths : str):
        """
        Adds all skins with the file paths specified. Paths can be relative or absolute
        """
        for filename in file_paths:
            self.add_skin(filename)

    def remove_skin(self, id):
        """
        Removes the skin with the id specified from the assets of self.pck as well as removes its id from self.file_ids if it exists.
        id can be in integer or string form. 

        Return Value:
            if function has no errors, function returns (True, ""). Otherwise, it returns (False, error_msg)
        """
        count = 0
        asset_list = []
        for asset in self.pck.GetAssets():
            if hasattr(asset, "Value"):
                asset = asset.Value
            asset_list.append(asset)

        removed_index = None
        for asset in asset_list:
            if hasattr(asset, "Value"):
                asset = asset.Value
            
            filename = asset.Filename
            if self.get_int_id(filename) == self.get_int_id(id):
                self.file_ids.remove(self.get_int_id(filename))
                removed_index = self.pck.IndexOfAsset(asset)
                self.pck.RemoveAsset(asset)
                count += 1
        
        if removed_index != None:
            if removed_index != self.pck.GetAssets().get_Count():
                self.shift_ids_backwards(start_index=removed_index)

        result, error_msg = self.gen_ids_from_files(self.pck)
        if not result:
            print(error_msg)
            return (False, "An error occured when generating ids from files")
        else:
            self.file_ids = result

        
        if count == 0:
            return (False, "pack contains no skins with the specified id")
        
        return (True, "")

    def remove_skins(self, *ids):
        """Removes all skins with the ids specified"""
        for id in ids:
            self.remove_skin(id)

    def add_skins_from_dir(self, dir_path : str, mode : int, new_name : str = None):
        """
        Adds all files from the directory specified to the self.pck as skin files, with proper ids.
        The DISPLAYNAME property of the skin assets will be the filename of the file it was generated with.

        Optional new_name deletes the .pck file that self.pck was opened with (if it was opened with a file), 
        and will write to new_name once save() is called.

        the mode argument specifies the way in which the files from the directory will be added to the current pack.
        Skins.WRITE will overwrite all assets in self.pck. Skins.APPEND will add files from directory to the assets of self.pck.

        Return Value:
            if function has no errors, function returns (True, ""). Otherwise, it returns (False, error_msg)
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
                if self.get_exten(file) == ".png":
                    files.append(os.path.join(dir_path, file))

        if len(files) == 0:
            return (False, "The directory specified contains no skin files")

        for file in files:
            if self.get_exten(file) == ".png":
                self.add_skin(file)

        return (True, "")

    def move_skin_forward(self, id):
        """
        Moves the skin with the specified id forward one in the pack. Also changes the skin's id so that all skins remain in order from lowest to highest id.
        If the skin as at the end of the pack, then it will be moved to the beginning.
        Return Value:
            if function has no errors, function returns (True, ""). Otherwise, it returns (False, error_msg)
        """

        skin_asset = None
        result, error_msg = self.get_skin_asset(id)
        if result:
            skin_asset = result
        else:
            print(error_msg)
            return (False, error_msg)

        asset_index : int = self.pck.IndexOfAsset(skin_asset)
        skin_asset_id = self.get_int_id(id)

        new_asset_index = asset_index + 1
        new_asset_id = skin_asset_id + 1

        assets = self.pck.GetAssets()

        self.pck.RemoveAsset(skin_asset)

        wrap = False
        if asset_index == assets.get_Count():
            new_asset_index = 0
            new_asset_id = self.namespace_id
            asset_index = asset_index - 1
            print(f"Asset {id} is the last asset")
            self.shift_ids_forward()
            wrap = True

        skin_asset.Filename = self.get_str_name(new_asset_id)

        new_skin_at_index = list(self.pck.GetAssets())[asset_index]
        new_skin_at_index = new_skin_at_index.Value
        if not wrap:
            new_skin_at_index_id = self.get_int_id(new_skin_at_index.Filename)
            new_skin_at_index.Filename = self.get_str_name(new_skin_at_index_id - 1)

        self.pck.InsertAsset(new_asset_index, skin_asset)

        result, error_msg = self.gen_ids_from_files(self.pck)
        if not result:
            print(error_msg)
            return (False, "An error occured when generating ids from files")
        else:
            self.file_ids = result

        return (True, "")

    def move_skin_backward(self, id):
        """
        Moves the skin with the specified id backward one in the pack. Also changes the skin's id so that all skins remain in order from lowest to highest id.
        If the skin as at the beginning of the pack, then it will be moved to the end.
        Return Value:
            if function has no errors, function returns (True, ""). Otherwise, it returns (False, error_msg)        
        """
        no_error, result = self.get_skin_asset(id)

        skin_asset = None
        result, error_msg = self.gen_ids_from_files(self.pck)
        if not result:
            print(error_msg)
            return (False, "An error occured when generating ids from files")
        else:
            self.file_ids = result

        asset_index : int = self.pck.IndexOfAsset(skin_asset)
        skin_asset_id = self.get_int_id(skin_asset.Filename)

        new_asset_index = asset_index - 1
        new_asset_id = skin_asset_id - 1

        assets = self.pck.GetAssets()

        if assets.get_Count() - 1 == asset_index:
            asset_index = asset_index - 1

        self.pck.RemoveAsset(skin_asset)
        
        wrap = False
        if asset_index == 0:
            new_asset_index = assets.get_Count()
            new_asset_id = self.file_ids[len(self.file_ids) - 1]
            self.shift_ids_backwards()
            wrap = True

        skin_asset.Filename = self.get_str_name(new_asset_id)

        new_skin_at_index = list(self.pck.GetAssets())[asset_index]
        new_skin_at_index = new_skin_at_index.Value
        if not wrap:
            new_skin_at_index_id = self.get_int_id(new_skin_at_index.Filename)
            new_skin_at_index.Filename = self.get_str_name(new_skin_at_index_id + 1)

        self.pck.InsertAsset(new_asset_index, skin_asset)

        result, error_msg = self.gen_ids_from_files(self.pck)
        if not result:
            print(error_msg)
            return (False, "An error occured when generating ids from files")
        else:
            self.file_ids = result

        return (True, "")
    # MARK: Skin Util Methods

    def get_skin_properties(self, id):
        """
        returns a tuple containing a dictionary of property names and their values from a skin id. Id must only contain digits.
        The tuple returned is described in more detail below.

        Return Value:
            if function has no errors, function returns (result, ""). Otherwise, it returns (False, error_msg)
        """
        if not self.id_exists(id):
            print(f"(self.get_skin_properties({id})): id {id} specified does not exist")
            return (False, "The ID specified does not exist")
        id = str(id)
        asset = self.pck.GetAsset(self.get_str_name(id), PckAssetType.SkinFile)
        prop_dict : dict[str, str] = {}
        if hasattr(asset, "Value"):
            asset = asset.Value
        
        for prop in asset.GetProperties():
            prop_dict[prop.Key] = prop.Value

        return (prop_dict, "")
    
    def update_skin_properties(self, id, prop_dict : dict[str, str]):
        """
        adds or updates the skin asset with the specified id with the properties from the property dict. Id must only contain digits
        Format:
            {
            propertyName: propertyValue,
            property2Name: property2Value
            }

        Return Value:
            if function has no errors, function returns (True, ""). Otherwise, it returns (False, error_msg)
        """
        exists, asset = self.pck.TryGetAsset(self.get_str_name(id), PckAssetType.SkinFile)
        if not exists: 
            print(f"(self.update_skin_properties({id}, {prop_dict})): id {id} specified has no corresponding skin")
            return (False, "ID specified has no corresponding skin")
        if hasattr(asset, "Value"):
            asset = asset.Value
        for key, value in prop_dict.items():
            asset.SetProperty(key, value)

        return (True, "")

    def remove_skin_properties(self, id, *names : str):
        """
        removes the properties with names from prop_dict (if they exist) from the skin asset with the specified id. Id must only contain digits.
        The return value of this function is described below.

        Return Value:
            if function has no errors, function returns (True, ""). Otherwise, it returns (False, error_msg)
        """
        exists, asset = self.pck.TryGetAsset(self.get_str_name(id), PckAssetType.SkinFile)
        if not exists: 
            print(f"(self.remove_skin_properties({id}, {names})): id {id} specified has no corresponding asset")
            return (False, f"(self.remove_skin_properties({id}, {names})): id {id} specified has no corresponding asset")
        
        if hasattr(asset, "Value"):
            asset = asset.Value
        
        for name in names:
            if not asset.HasProperty(name):
                print(f"self.remove_skin_properties({id}, {names}): Warning: Skin {id} does not contain the property {name} that is attempting to be removed")
            asset.RemoveProperties(name)

        return (True, "")

    def get_skin_asset(self, id):
        """
        Returns a tuple that conatins the skin asset object (PckAsset) that has the specified id. 
        The return value of this function is described in more detail in the "Return Value" section.

        Return Value:
            if function has no errors, function returns (result, ""). Otherwise, it returns (False, error_msg)
        """
        if self.id_exists(id):
            return (self.pck.GetAsset(self.get_str_name(id), PckAssetType.SkinFile), "")
        else: 
            print(f"(self.get_skin_asset({id})): id specified {id} has no corresponding skin asset")
            return (False, f"ID specified has no corresponding skin asset")

    # MARK: ID Creation Methods

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
            return True
        
        self.find_used_ids()
        
        if self.file_ids == None or len(self.file_ids) == 0:
            un_id = self.get_unused_id()
            if un_id:
                self.namespace_id = un_id
            else:
                self.namespace_id == 0

        elif len(self.file_ids) > 0 and not self.file_ids[0] in self.used_ids:
            self.namespace_id = self.file_ids[0]

        elif len(self.file_ids) and self.file_ids[0] in self.used_ids:
            un_id = self.get_unused_id()
            if un_id:
                self.namespace_id = un_id
            else:
                self.namespace_id == 0
            self.change_id_namespace(self.namespace_id)

        if len(self.file_ids) > 0:
            self.file_ids[0] == self.namespace_id
        else:
            self.file_ids.insert(0, self.namespace_id)

        return True

    def find_used_ids(self):
        """
        Looks through skinpack dlc .pck files in the specified install_dir, finds their id namepsace, and adds it to self.used_ids.
        Returns a tuple described below.

        Return Value:
            if function has no errors, function returns (True, ""). Otherwise, it returns (False, error_msg)
        """
        if self.install_dir == None:
            print("(self.find_used_ids()): Unable to find taken ids, no install directory specified.")
            return (False, 'Unable to find taken ids because no install directory was specified.')
        DLCs_path = os.path.join(self.install_dir, "Windows64Media", "DLC")
        DLCs : list[str] = os.listdir(DLCs_path)
        Skinpacks : list[str] = list()

        for DLC_index in range(len(DLCs)):
            DLC_path = os.path.join(DLCs_path, DLCs[DLC_index])
            if len(os.listdir(DLC_path)) < 2:
                Skinpacks.append(DLC_path)
        
        for skinpck_path in Skinpacks:
            pck_file = os.listdir(skinpck_path)[0]

            dlc_skin_pack = SkinPack(os.path.join(skinpck_path, pck_file), dlc=True)

            result, error_msg = dlc_skin_pack.get_dlc_namespace_id()
            if result:
                self.used_ids.append(result)
            else: print(error_msg)

        return (True, "")
    
    def get_unused_id(self):
        """
        Uses self.used_ids to return an unused id that is the closest to 0.
        If an error occurs, returns (False, error_msg)
        """
        if self.used_ids == None or len(self.used_ids) == 0:
            if not self.find_used_ids()[0]: 
                print("(get_unused_id()) The unused_ids are unknown because no install directory was specified or no used ids could be found")
                return (False, "The unused IDs are unknown because no install directory was specified or no used ids could be found")
        spaced_ids = []
        last = str()
        for id_index in range(len(self.used_ids)):
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

        return (un_id, "")
    
    def gen_unique_id(self):
        """
        Generates a unique_id for use with a new skin.
        """
        self.create_or_change_id_namespace()
        print(self.namespace_id)
        print(len(self.file_ids))
        num_ids = len(self.file_ids)
        print(self.file_ids)
        un_id = self.get_str_name(self.namespace_id + num_ids)

        return un_id

    def gen_ids_from_files(self, pck : PckFile):
        """
        Looks through the assets self.pck to find valid ids to add to a file_ids list, then sorts the list before returning a tuple which is described below

        Return Value:
            if function has no errors, function returns (file_ids, ""). Otherwise, it returns (False, error_msg)
        """
        file_ids : list[str] = []
        assets = pck.GetAssets()
        if assets.get_Count() == 0: return (False, "pack has no assets/files to generate ids from")
        for asset in assets:
            asset = asset.Value
            filename = asset.Filename
            if len(filename) == 19 and not "cape" in filename:
                pass
            else:
                if not self.dlc:
                    while True:
                        answer = input(f"Invalid Skin File name found. remove or automatically rename {filename} (r / n):") # TODO: Replace Input() with GUI popup from Tkinter
                        if answer == "r":
                            self.pck.RemoveAsset(asset)
                        if answer == "n":
                            asset.Filename = self.gen_unique_id()
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

        return (file_ids, "")
    
    def change_id_namespace(self, new_name_space):
        """
        Renames all assets in the pck to reflect the new new_name_space specified. new_name_space must only contain digits.
        """
        self.namespace_id = new_name_space
        
        if self.pck.GetAssets().get_Count() == 0:
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
                self.get_str_name(new_name_space),
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

            result, error_msg = self.gen_ids_from_files(self.pck)
            if not result:
                print(error_msg)
                return (False, "An error occured when generating ids from files")
            else:
                self.file_ids = result

            count += 1

    def change_skin_id(self, skin_asset : PckAsset, new_id):
        """Changes the filename of the skin_asset specified to match the new_id"""
        new_id = self.get_str_name(new_id)
        skin_asset.Filename = new_id
        return skin_asset
    
    def shift_ids_forward(self, start_index : int = None, end_index : int = None):
        """
        Adds one to the ids in all of the filenames in the range start_index (inclusive) to end_index (inclusive) in the pack.
        if end index is not specified it will be assumed to be the end.
        if beginning index is not specified it will be assumed to be the beginning.
        end index can be negative
        """
        asset_list = list(self.pck.GetAssets())
        asset_cnt = len(asset_list)
        if end_index != None:
            if end_index > asset_cnt - 1:
                print(f"(shift_ids_backwards({start_index}, {end_index})): end_index {end_index} out of range for asset_list length {asset_cnt}.")
                return (False, f"end_index {end_index} out of range for asset_list length {asset_cnt}.")
            
            if end_index < 0:
                end_index = len(asset_list) + end_index

            if start_index > end_index:
                print(f"(shift_ids_backwards({start_index}, {end_index})): start index cannot be after end index")
                return (False, f"start index cannot be after end index")
        
        if start_index == None:
            start_index = 0

        if end_index == None:
            end_index = asset_cnt - 1


        for i in range(end_index, start_index - 1, -1):
            asset = asset_list[i]
            asset = asset.Value
            asset.Filename = self.get_str_name(self.get_int_id(asset.Filename) + 1)

        return (True, "")

    def shift_ids_backwards(self, start_index : int = None, end_index : int = None):
        """
        Subtracts one from the ids in all of the filenames in the range start_index (inclusive) to end_index (inclusive) in the pack.
        if end index is not specified it will be assumed to be the end.
        if beginning index is not specified it will be assumed to be the beginning.
        end index can be negative
        """
        asset_list = list(self.pck.GetAssets())
        asset_cnt = len(asset_list)
        if end_index != None:
            if end_index > asset_cnt - 1:
                print(f"(shift_ids_backwards({start_index}, {end_index})): end_index {end_index} out of range for asset_list length {asset_cnt}")
                return (False, f"end_index {end_index} out of range for asset_list length {asset_cnt}")
            
            if end_index < 0:
                end_index = len(asset_list) + end_index

            if start_index != None and start_index > end_index:
                print(f"(shift_ids_backwards({start_index}, {end_index})): start index cannot be after end index")
                return (False, f"start index cannot be after end index")
        
        if start_index == None:
            start_index = 0

        if end_index == None:
            end_index = asset_cnt - 1


        for i in range(start_index, end_index + 1):
            asset = asset_list[i]
            asset = asset.Value
            asset.Filename = self.get_str_name(self.get_int_id(asset.Filename) - 1)

        return (True, "")
            
    # MARK: ID Format Methods

    def normalize_int_id(self, id : int):
        """
        Converts the id specified into a string and changes it into an 8 character id with leading zeros
        """
        id = str(id)

        for _ in range(8 - len(id)):
            id = "0" + id
        
        return id
    
    def get_str_name(self, id):
        """
        Converts the id specified into a filename suitable for a minecraft legacy skin pack. 
        id specified must already contain only digits, no prefix or file extension
        """
        id = int(id)
        id = self.normalize_int_id(id)

        return f"dlcskin{id}.png"

    def get_int_id(self, id):
        """
        Changes a string id into an int id. Id specified can have file extension and/or prefix.
        """
        str_id = str(id)
        
        if not str_id[0].isdigit():
            str_id = str_id[7:]
        str_id = self.remove_exten(str_id)
        str_id = self.normalize_int_id(str_id)
        return int(str_id)

    def get_dlc_namespace_id(self):
        """
        Used with skinpacks initialized as dlcs to return the namespace, even if self.namespace_id ins't initialized.
        Mainly exists to make the code look nicer. returns a tuple described below.

        Return Value:
            if function has no errors, function returns (dlc_namespace_id, ""). Otherwise, it returns (False, error_msg)
        """
        if len(self.file_ids) > 0:
            return (self.file_ids[0], "")
        else:
            return (False, "No valid dlc namespace was found")
    
    # MARK: Asset Methods
    
    def get_assets(self):
        """Returns a list of the PckAssets currently contained within self.pck"""
        asset_list = []

        asset : PckAsset
        for asset in self.pck.GetAssets():
            asset_list.append(asset.Value)
        return asset_list

    def remove_all_assets(self):
        """
        Removes all assets currently contained within self.pck
        """
        self.file_ids.clear()
        asset_list = []

        asset : PckAsset
        for asset in self.pck.GetAssets():
            asset_list.append(asset.Value)
        
        asset : PckAsset
        for asset in asset_list:
            self.pck.RemoveAsset(asset)

    def update_assets(self, name: str , data : bytes,  assetType : PckAssetType, properties: dict[str, str] = {}):
        """
        overwrites asset in the pack if it exists, or creates it. self.pck.RemoveAsset(asset) can be used to remove assets self.pck.       
        """
        if self.pck.HasAsset(name, assetType):
            self.pck.RemoveAsset(self.pck.GetAsset(name, assetType))

        new_asset : PckAsset = self.pck.CreateNewAsset(
            name,
            assetType
        )

        new_asset.SetData(data)
        for key, value in properties.items():
            new_asset.AddProperty(key, value)

    #MARK: File Methods

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

        if exten_index != None:
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

    
    def save(self, dir : str = None):
        """
        Writes the current self.pck object to a .pck file with self.pck_name as the file name.
        Optional dir argument specifies the directory that the file will be written to.
        If dir is not specified, it will be written to self.pck_path

        Return Value:
            if function has no errors, function returns (True, ""). Otherwise, it returns (False, error_msg)
        """
        if self.pck.GetAssets().get_Count() != 0:
            writer = PckFileWriter(self.pck, ByteOrder.LittleEndian)
            if dir != None:
                writer.WriteToFile(os.path.join(dir, self.pck_name))
            else:
                writer.WriteToFile(self.pck_path)
            return (True, "")

        else:
            save_loc = ""
            if dir == None:
                save_loc = self.pck_path
            else:
                save_loc = os.path.join(dir, self.pck_name)
            print(f"save({save_loc}): pck object attempting to be saved contains no skins")
            return (False, f"pack attempting to be saved contains no skins")

    # MARK: Error Handling

    def id_exists(self, id):
        found, _ = self.pck.TryGetAsset(self.get_str_name(id), PckAssetType.SkinFile)
        return found

class UnspecifiedException(Exception):
    pass

skinpack = SkinPack(pck_name="GroupPack.pck", overwrite=True, from_file=True)
skinpack.remove_skin(2200)
skinpack.save()

# MARK: Temp

