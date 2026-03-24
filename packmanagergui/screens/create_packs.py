import tkinter as tk

from screens.screen import Screen, ScreenManager, ScreenType


class CreatePacksScreen(Screen):
    def __init__(self, root: tk.Tk, screen_manager: ScreenManager):
        super().__init__(root)
        
        self.screen_manager = screen_manager
        self.screen_manager.screens.update({ScreenType.CREATE_PACKS: self})
        label = tk.Label(self, text="Create Packs", font=self.NORMAL_FONT)
        label.pack()
        menu_button = tk.Button(self, text="Menu", font=self.NORMAL_FONT, command=lambda: self.screen_manager.set_screen(ScreenType.MENU))
        menu_button.pack(padx=5)