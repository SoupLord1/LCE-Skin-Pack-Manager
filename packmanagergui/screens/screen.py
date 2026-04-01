from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkFont
from components.scrollable_frame import ScrollableFrame
from components.skinpackcard import Skin_Pack_Card
from constants import APP_TITLE, LARGE_FONT_PERAMS, NORMAL_FONT_PERAMS, DEFAULT_DLC_PATH
from enum import Enum
from config import ConfigManager
import os


class ScreenType(Enum):
    MENU = 0
    MANAGE_PACKS = 1
    CREATE_PACKS = 2
    EDIT_PACKS = 3

class Screen(tk.Frame):
    def __init__(self, root: tk.Tk): # type: ignore
        super().__init__(root)
        self.screen_manager: ScreenManager | None = None
        self.config_manager: ConfigManager | None = None
        self.screen_type: ScreenType | None = None


        self.APP_TITLE = APP_TITLE
        self.LARGE_FONT = tkFont.Font(root, family=LARGE_FONT_PERAMS[0], size=LARGE_FONT_PERAMS[1])
        self.NORMAL_FONT = tkFont.Font(root, family=NORMAL_FONT_PERAMS[0], size=NORMAL_FONT_PERAMS[1])
        manage_packs_title: tk.Label = tk.Label(self, text=APP_TITLE, font=self.LARGE_FONT)
        manage_packs_title.pack()

    def can_set_screen(self):
        return (True, False, "")

    def on_set_screen(self):
        pass

    def set_config_manager(self, config_manager: ConfigManager):
       self.config_manager = config_manager

    def set_screen_manager(self, screen_manager: ScreenManager):
        if (self.screen_type == None):
            raise Exception(f"Invalid screen type \"{self.screen_type}\"") 
        if (screen_manager == None):
            raise Exception(f"Invalid  \"{screen_manager}\"") 
        
        self.screen_manager = screen_manager 
        self.screen_manager.screens.update({self.screen_type: self})

    def change_screen(self, screen_type: ScreenType):
        if (self.screen_manager == None):
            raise Exception(f"Invalid \"{self.screen_type}\"") 
        self.screen_manager.set_screen(screen_type)
        
    def after_init(self):
        pass
        
        

class ScreenManager():

    def __init__(self):
        self.screens: dict[ScreenType, Screen] = {}
        self.current_screen: Screen | None = None



    def set_screen(self, screen_type: ScreenType):
        
        new_screen = self.screens.get(screen_type)

        if not new_screen == None:
            check: tuple = new_screen.can_set_screen()
            if check[0]:
                if self.current_screen != None:
                    self.current_screen.pack_forget()
                self.current_screen = new_screen
                self.current_screen.pack(expand=True, fill="both")
                self.current_screen.on_set_screen()
            elif check[1]:
                messagebox.showerror("Error", check[2])

class ScreenObject():
    def __init__(self, screen: Screen, screen_manager: ScreenManager, config_manager: ConfigManager):
        self.screen = screen
        screen.set_screen_manager(screen_manager)
        screen.set_config_manager(config_manager)
        screen.after_init()