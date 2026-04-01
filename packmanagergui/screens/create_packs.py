import tkinter as tk

from screens.screen import *

class CreatePacksScreen(Screen):
    def __init__(self, root: tk.Tk):
        super().__init__(root)
        self.screen_type = ScreenType.CREATE_PACKS
        label = tk.Label(self, text="Create Packs", font=self.NORMAL_FONT)
        label.pack()
        menu_button = tk.Button(self, text="Menu", font=self.NORMAL_FONT, command=lambda: self.change_screen(ScreenType.MENU))
        menu_button.pack(padx=5)