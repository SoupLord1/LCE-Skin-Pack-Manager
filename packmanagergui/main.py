import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.font as tkFont
from constants import *
from components.skinpackcard import Skin_Pack_Card
from components.scrollable_frame import ScrollableFrame
import os, shutil
from config import Config_Manager
from screens.create_packs import CreatePacksScreen
from screens.edit_packs import EditPacksScreen
from screens.manage_packs import ManagePacksScreen
from screens.menu import MenuScreen
from screens.screen import ScreenManager, ScreenType, Screen

root: tk.Tk = tk.Tk()
root.title(APP_TITLE)
root.minsize(800, 400)
root.resizable(False, False)

#MARK: Config

config_manager = Config_Manager()


screen_manager = ScreenManager(Screen(root), config_manager)

menu_screen = MenuScreen(root, screen_manager)

screen_manager.set_screen(ScreenType.MENU)

manage_packs_screen = ManagePacksScreen(root, screen_manager)

edit_packs_screen = EditPacksScreen(root, screen_manager)

create_packs_screen = CreatePacksScreen(root, screen_manager)

root.mainloop()