import tkinter as tk
import pck_handler.skinpack as sp
import sys

from packmanagergui.screens.screen import *

class CreatePacksScreen(Screen):

    def __init__(self, root: tk.Tk):
        pck_path = ""

        if hasattr(sys, "frozen"):
            pck_path = "packs"

        else:
            pck_path = "../packs"


        super().__init__(root)
        self.screen_type = ScreenType.CREATE_PACKS
        label = tk.Label(self, text="Create Packs", font=self.NORMAL_FONT)
        label.pack()
        menu_button = tk.Button(self, text="Menu", font=self.NORMAL_FONT, command=lambda: self.change_screen(ScreenType.MENU))
        menu_button.pack(padx=5)

        name_label = tk.Label(self, text="Pack Name")
        name_input = tk.Entry(self)
        create_button = tk.Button(self, text="Create Pack", command= lambda: self.create_skinpack(pck_path, name_input.get()))

        name_label.pack()
        name_input.pack()
        create_button.pack()




    def create_skinpack(self, pck_path: str, pck_name: str):
        self.config_manager.current_skinpack = sp.SkinPack(pck_path, pck_name, from_file=False)
        print("E")
        self.change_screen(ScreenType.EDIT_PACKS)