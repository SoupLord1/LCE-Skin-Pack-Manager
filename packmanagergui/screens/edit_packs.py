import tkinter as tk

from packmanagergui.screens.screen import *


class EditPacksScreen(Screen):
    def __init__(self, root: tk.Tk):
        super().__init__(root)

        self.screen_type = ScreenType.EDIT_PACKS
        
        label = tk.Label(self, text="Edit Packs", font=self.NORMAL_FONT)
        label.pack()
        menu_button = tk.Button(self, text="Menu", font=self.NORMAL_FONT, command=lambda: self.change_screen(ScreenType.MENU))
        menu_button.pack(padx=5)

        self.pack_name_label = tk.Label(self, text="No Pack Selected")

        self.pack_name_label.pack()


    def on_set_screen(self):
        super().on_set_screen()
        self.pack_name_label.config(text=f"Editing '{self.config_manager.current_skinpack.pck_name}'")