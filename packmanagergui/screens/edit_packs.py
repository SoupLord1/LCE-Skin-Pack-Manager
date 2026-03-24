import tkinter as tk

from screens.screen import Screen, ScreenManager, ScreenType


class EditPacksScreen(Screen):
    def __init__(self, root: tk.Tk, screen_manager: ScreenManager):
        super().__init__(root)
        
        self.screen_manager = screen_manager
        self.screen_manager.screens.update({ScreenType.EDIT_PACKS: self})
        label = tk.Label(self, text="Edit Packs", font=self.NORMAL_FONT)
        label.pack()
        menu_button = tk.Button(self, text="Menu", font=self.NORMAL_FONT, command=lambda: self.screen_manager.set_screen(ScreenType.MENU))
        menu_button.pack(padx=5)