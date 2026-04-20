import tkinter as tk
from tkinter import filedialog

from packmanagergui.screens.screen import *


class EditPacksScreen(Screen):
    current_image_path: str = ""
    def __init__(self, root: tk.Tk):
        self.root = root
        super().__init__(root)

        self.screen_type = ScreenType.EDIT_PACKS
        
        label = tk.Label(self, text="Edit Packs", font=self.NORMAL_FONT)
        label.pack()
        menu_button = tk.Button(self, text="Menu", font=self.NORMAL_FONT, command=lambda: self.change_screen(ScreenType.MENU))
        menu_button.pack(padx=5)

        self.pack_name_label = tk.Label(self, text="No Pack Selected")

        self.pack_name_label.pack()

        add_skin_button = tk.Button(self, text="Add sKin", command= lambda: self.add_skin_popup())
        add_skin_button.pack()


    def on_set_screen(self):
        super().on_set_screen()
        self.pack_name_label.config(text=f"Editing '{self.config_manager.current_skinpack.pck_name}'")

    def add_skin_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Add skin")
        popup.geometry("250x150")
        
        select_image_button = tk.Button(popup, text="Select Skin Image", command=lambda: self.select_skin_image())
        select_image_button.pack()

    def select_skin_image(self):
        self.current_image_path = filedialog.askopenfile(filetypes=[("Skin", ".png")])
        print(self.current_image_path)