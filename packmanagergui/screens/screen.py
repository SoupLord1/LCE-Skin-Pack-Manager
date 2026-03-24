import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkFont
from components.scrollable_frame import ScrollableFrame
from components.skinpackcard import Skin_Pack_Card
from constants import APP_TITLE, LARGE_FONT_PERAMS, NORMAL_FONT_PERAMS, DEFAULT_DLC_PATH
from enum import Enum
from config import Config_Manager
import os

class ScreenType(Enum):
    MENU = 0
    MANAGE_PACKS = 1
    CREATE_PACKS = 2
    EDIT_PACKS = 3

class Screen(tk.Frame):
    def __init__(self, root: tk.Tk): # type: ignore
        super().__init__(root)
        self.APP_TITLE = APP_TITLE
        self.LARGE_FONT = tkFont.Font(root, family=LARGE_FONT_PERAMS[0], size=LARGE_FONT_PERAMS[1])
        self.NORMAL_FONT = tkFont.Font(root, family=NORMAL_FONT_PERAMS[0], size=NORMAL_FONT_PERAMS[1])
        manage_packs_title: tk.Label = tk.Label(self, text=APP_TITLE, font=self.LARGE_FONT)
        manage_packs_title.pack()

    def can_set_screen(self):
        return (True, False, "")

    def on_set_screen(self):
        pass

class ScreenManager():

    screens: dict[ScreenType, Screen] = {}
    current_screen: Screen 

    def __init__(self, screen: Screen, config_manager: Config_Manager):
        self.config_manager = config_manager
        self.current_screen = screen
        self.current_screen.pack(expand=True, fill="both")

    def set_screen(self, screen_type: ScreenType):
        
        new_screen = self.screens.get(screen_type)

        if not new_screen == None:
            check: tuple = new_screen.can_set_screen()
            if check[0]:
                self.current_screen.pack_forget()
                self.current_screen = new_screen
                self.current_screen.pack(expand=True, fill="both")
                self.current_screen.on_set_screen()
            elif check[1]:
                messagebox.showerror("Error", check[2])



