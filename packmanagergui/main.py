import tkinter as tk
from constants import *

from config import ConfigManager
from screens.create_packs import CreatePacksScreen
from screens.edit_packs import EditPacksScreen
from screens.manage_packs import ManagePacksScreen
from screens.menu import MenuScreen
from screens.screen import *

root: tk.Tk = tk.Tk()
root.title(APP_TITLE)
root.minsize(800, 400)
root.resizable(False, False)

#MARK: Config

config_manager = ConfigManager()
screen_manager = ScreenManager()

menu_screen_object = ScreenObject(MenuScreen(root), screen_manager, config_manager)

screen_manager.set_screen(ScreenType.MENU)

manage_packs_screen_object = ScreenObject(ManagePacksScreen(root), screen_manager, config_manager)

edit_packs_screen_object = ScreenObject(EditPacksScreen(root), screen_manager, config_manager)


create_packs_screen_object = ScreenObject(CreatePacksScreen(root), screen_manager, config_manager)

root.mainloop()