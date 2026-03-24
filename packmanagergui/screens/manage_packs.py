from tkinter import messagebox

from components.skinpackcard import Skin_Pack_Card
from screens.screen import ScreenManager, ScreenType, Screen
import tkinter as tk
from components.scrollable_frame import ScrollableFrame
import os
from constants import DEFAULT_DLC_PATH

class ManagePacksScreen(Screen):
    def __init__(self, root, screen_manager: ScreenManager):
        super().__init__(root)
        self.screen_manager = screen_manager
        self.screen_manager.screens.update({ScreenType.MANAGE_PACKS: self})

        self.scrollable = ScrollableFrame(self)
        self.scrollable.pack(expand=True, anchor="center", fill="both", padx=10)

        footer = tk.Frame(self ,height=25)
        footer.pack(side="bottom", anchor="center")

        menu_button = tk.Button(footer, text="Menu", font=self.NORMAL_FONT, command=lambda: self.screen_manager.set_screen(ScreenType.MENU))
        menu_button.pack(side="left", padx=5)        
        add_pack_button = tk.Button(footer, text="Add Pack", font=self.NORMAL_FONT, command=lambda: self.screen_manager.set_screen(ScreenType.MENU))
        add_pack_button.pack(side="left", padx=5)
        refresh_button = tk.Button(footer, text="Refresh", font=self.NORMAL_FONT, command=self.refresh_packs)
        refresh_button.pack(side="left", padx=5)

    def refresh_packs(self):
        for widget in self.scrollable.scrollable_frame.winfo_children():
            widget.destroy()

        dlc_files = os.listdir(f"{self.screen_manager.config_manager.parent_path}/{DEFAULT_DLC_PATH}")
        
        for file in dlc_files:
            sub_files = os.listdir(f"{self.screen_manager.config_manager.parent_path}/{DEFAULT_DLC_PATH}/{file}")
            if (len(sub_files) == 1):
                Skin_Pack_Card(self.scrollable.scrollable_frame, file, self.screen_manager.current_screen.NORMAL_FONT)

    #return (can_set, display_error, error_msg)
    def can_set_screen(self):
        if (self.screen_manager.config_manager.valid_dlc_path):
            self.refresh_packs()
            return (True, False, "")

        else:
            return (False, True, f"No DLC folder found! \n{self.screen_manager.config_manager.parent_path}")

