import tkinter as tk
from tkinter import filedialog, messagebox
from screens.screen import ScreenManager, ScreenType, Screen

from constants import DEFAULT_DLC_PATH, PACKS_PATH
import os, shutil


class MenuScreen(Screen):
    BUTTON_Y_PADDING = 2
    show_manage_packs_callback = lambda: ()
    def __init__(self, root: tk.Tk, screen_manager: ScreenManager):
        super().__init__(root)

        self.screen_manager = screen_manager
        self.screen_manager.screens.update({ScreenType.MENU: self})

        self.game_folder_label = tk.Label(self, text=f"Game Path: no folder selected", font=self.NORMAL_FONT)
        self.game_folder_label.pack(pady=self.BUTTON_Y_PADDING)

        if (self.screen_manager.config_manager.valid_dlc_path and self.screen_manager.config_manager.parent_path != ''):
            self.game_folder_label.config(text=f"Game Path: {self.screen_manager.config_manager.parent_path}")

        self.select_game_folder_button = tk.Button(self, text="Select Game Folder", font=self.NORMAL_FONT, command=self.select_game_folder_callback)
        self.select_game_folder_button.pack(pady=self.BUTTON_Y_PADDING)

        create_edit_manage_group = tk.Frame(self)
        create_edit_manage_group.pack(padx=2, anchor="center")

        manage_packs_button = tk.Button(create_edit_manage_group, text="Manage Packs", font=self.NORMAL_FONT, command=lambda: self.screen_manager.set_screen(ScreenType.MANAGE_PACKS) )
        manage_packs_button.pack(pady=self.BUTTON_Y_PADDING, side="left", padx=2)

        create_packs_button = tk.Button(create_edit_manage_group, text="Create Packs",  font=self.NORMAL_FONT, command=lambda: self.screen_manager.set_screen(ScreenType.CREATE_PACKS))
        create_packs_button.pack(pady=self.BUTTON_Y_PADDING, side="left", padx=2)

        edit_packs_button = tk.Button(create_edit_manage_group, text="Edit Packs", font=self.NORMAL_FONT, command=lambda: self.screen_manager.set_screen(ScreenType.EDIT_PACKS))
        edit_packs_button.pack(pady=self.BUTTON_Y_PADDING, side="left", padx=2)

        load_packs_button = tk.Button(self, text="Load Packs", font=self.NORMAL_FONT, command= lambda: self.load_packs_callback())
        load_packs_button.pack(pady=self.BUTTON_Y_PADDING)

    
    def select_game_folder_callback(self):

        self.screen_manager.config_manager.parent_path = filedialog.askdirectory()

        dlc_path_exists = os.path.exists(f"{self.screen_manager.config_manager.parent_path}/{DEFAULT_DLC_PATH}")
        if (dlc_path_exists):
            self.screen_manager.config_manager.valid_dlc_path = True
            self.screen_manager.config_manager.create_config()
        else:
            self.screen_manager.config_manager.valid_dlc_path = False

        self.game_folder_label.config(text=f"Game Path: {self.screen_manager.config_manager.parent_path}")

    def load_packs_callback(self):
        if(not os.path.exists(PACKS_PATH)):
            os.mkdir(PACKS_PATH)

        if (self.screen_manager.config_manager.valid_dlc_path):
            dlc_files = os.listdir(PACKS_PATH)
            for file in dlc_files:
                folder_name = file.split(".")[0]
                pack_path = f"{self.screen_manager.config_manager.parent_path}/{DEFAULT_DLC_PATH}/{folder_name}"
                if (not os.path.exists(pack_path)):
                    os.mkdir(pack_path)
                shutil.copy2(f"{PACKS_PATH}/{file}",pack_path)

            messagebox.showinfo("LOADED", f"PACKS LOADED: {len(dlc_files)}")

        else:
            messagebox.showerror("Error", f"No DLC folder found! \n{self.screen_manager.config_manager.parent_path}")
