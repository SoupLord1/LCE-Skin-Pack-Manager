import tkinter as tk
from tkinter import filedialog, messagebox
from screens.screen import *


from constants import DEFAULT_DLC_PATH, PACKS_PATH
import os, shutil


class MenuScreen(Screen):
    BUTTON_Y_PADDING = 2
    show_manage_packs_callback = lambda: ()
    def __init__(self, root: tk.Tk):
        super().__init__(root)
        self.screen_type = ScreenType.MENU


        self.game_folder_label = tk.Label(self, text=f"Game Path: no folder selected", font=self.NORMAL_FONT)
        self.game_folder_label.pack(pady=self.BUTTON_Y_PADDING)

        self.select_game_folder_button = tk.Button(self, text="Select Game Folder", font=self.NORMAL_FONT, command=self.select_game_folder_callback)
        self.select_game_folder_button.pack(pady=self.BUTTON_Y_PADDING)

        create_edit_manage_group = tk.Frame(self)
        create_edit_manage_group.pack(padx=2, anchor="center")

        manage_packs_button = tk.Button(create_edit_manage_group, text="Manage Packs", font=self.NORMAL_FONT, command=lambda: self.change_screen(ScreenType.MANAGE_PACKS) )
        manage_packs_button.pack(pady=self.BUTTON_Y_PADDING, side="left", padx=2)

        create_packs_button = tk.Button(create_edit_manage_group, text="Create Packs",  font=self.NORMAL_FONT, command=lambda: self.change_screen(ScreenType.CREATE_PACKS))
        create_packs_button.pack(pady=self.BUTTON_Y_PADDING, side="left", padx=2)

        edit_packs_button = tk.Button(create_edit_manage_group, text="Edit Packs", font=self.NORMAL_FONT, command=lambda: self.change_screen(ScreenType.EDIT_PACKS))
        edit_packs_button.pack(pady=self.BUTTON_Y_PADDING, side="left", padx=2)

        load_packs_button = tk.Button(self, text="Load Packs", font=self.NORMAL_FONT, command= lambda: self.load_packs_callback())
        load_packs_button.pack(pady=self.BUTTON_Y_PADDING)

    def after_init(self):
        if (self.config_manager == None):
            raise Exception(f"Invalid '{self.config_manager}'")

        if (self.config_manager.valid_dlc_path and self.config_manager.parent_path != ''):
            self.game_folder_label.config(text=f"Game Path: {self.config_manager.parent_path}")


    
    def select_game_folder_callback(self):
        if (self.config_manager == None):
            raise Exception(f"Invalid '{self.config_manager}'")


        new_parent_path = filedialog.askdirectory()

        dlc_path_exists = os.path.exists(f"{new_parent_path}/{DEFAULT_DLC_PATH}")
        if (dlc_path_exists and new_parent_path != ""):
            self.config_manager.valid_dlc_path = True
            self.config_manager.create_config()
            self.game_folder_label.config(text=f"Game Path: {new_parent_path}")
            self.config_manager.parent_path = new_parent_path

        else:
            messagebox.showerror("Invalid Path", f"Invalid Path Selected: {new_parent_path}")



    def load_packs_callback(self):
        if (self.config_manager == None):
            raise Exception(f"Invalid '{self.config_manager}'")
        
        if(not os.path.exists(PACKS_PATH)):
            os.mkdir(PACKS_PATH)

        if (self.config_manager.valid_dlc_path):
            dlc_files = os.listdir(PACKS_PATH)
            for file in dlc_files:
                folder_name = file.split(".")[0]
                pack_path = f"{self.config_manager.parent_path}/{DEFAULT_DLC_PATH}/{folder_name}"
                if (not os.path.exists(pack_path)):
                    os.mkdir(pack_path)
                shutil.copy2(f"{PACKS_PATH}/{file}",pack_path)

            messagebox.showinfo("LOADED", f"PACKS LOADED: {len(dlc_files)}")

        else:
            messagebox.showerror("Error", f"No DLC folder found! \n{self.config_manager.parent_path}")
