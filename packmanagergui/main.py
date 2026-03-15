import tkinter as tk
from tkinter import filedialog, messagebox
from constants import *
from components.skinpackcard import Skin_Pack_Card
from components.scrollable_frame import ScrollableFrame
import os
import configparser
import tkinter.font as tkFont

root: tk.Tk = tk.Tk()
root.title(APP_TITLE)
root.minsize(800, 400)
root.resizable(False, False)

valid_dlc_path = False
DLC_PATH = "Windows64Media/DLC"
parent_path = ""

NORMAL_FONT = tkFont.Font(family="Arial", size=15)
LARGE_FONT = tkFont.Font(family="Arial", size=25)

def create_config():
    config = configparser.ConfigParser()
    # Add sections and key-value pairs
    config['Config'] = {
        'parent_path': parent_path,
    }
    # Write the configuration to a file
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

def read_config():
    global parent_path
    config = configparser.ConfigParser()
    config.read('config.ini')
    parent_path = config.get("Config", "parent_path")

def show_menu_callback():
    menu_frame.pack(fill="both", expand=True)
    manage_packs_frame.pack_forget()

def refresh_packs():
    for widget in scrollable.scrollable_frame.winfo_children():
        widget.destroy()

    dlc_files = os.listdir(f"{parent_path}/{DLC_PATH}")
    
    for file in dlc_files:
        sub_files = os.listdir(f"{parent_path}/{DLC_PATH}/{file}")
        if (len(sub_files) == 1):
            Skin_Pack_Card(scrollable.scrollable_frame, file, NORMAL_FONT)

def show_manage_packs_callback():
    global valid_dlc_path
    if (valid_dlc_path):
        menu_frame.pack_forget()
        manage_packs_frame.pack(fill="both",expand=True)

        refresh_packs()

    else:
        messagebox.showerror("Error", f"No DLC folder found! \n{parent_path}")

def select_game_folder_callback():
    global valid_dlc_path, parent_path, game_folder_label

    parent_path = filedialog.askdirectory()

    dlc_path_exists = os.path.exists(f"{parent_path}/{DLC_PATH}")
    if (dlc_path_exists):
        valid_dlc_path = True
        create_config()
    else:
        valid_dlc_path = False

    game_folder_label.config(text=f"Game Path: {parent_path}")


if (not os.path.exists("config.ini")):
    create_config()
else:
    read_config()
    valid_dlc_path = True

#Menu Screen
menu_frame = tk.Frame(root)
menu_frame.pack(fill="both", expand=True)

title: tk.Label = tk.Label(menu_frame, text=APP_TITLE, font=LARGE_FONT)
title.pack()

game_folder_label = tk.Label(menu_frame, text=f"Game Path: no folder selected", font=NORMAL_FONT)
game_folder_label.pack(pady=2)

if (valid_dlc_path and parent_path != ''):
    game_folder_label.config(text=f"Game Path: {parent_path}")

select_game_folder_button = tk.Button(menu_frame, text="Select Game Folder", font=NORMAL_FONT, command=select_game_folder_callback)
select_game_folder_button.pack(pady=2)

manage_packs_button = tk.Button(menu_frame, text="Manage Packs", font=NORMAL_FONT, command=show_manage_packs_callback)
manage_packs_button.pack(pady=2)

#Manage Packs Screen
manage_packs_frame = tk.Frame(root)

title: tk.Label = tk.Label(manage_packs_frame, text=APP_TITLE, font=LARGE_FONT)
title.pack()

scrollable = ScrollableFrame(manage_packs_frame)
scrollable.pack(expand=True, anchor="center", fill="both", padx=10)

footer = tk.Frame(manage_packs_frame ,height=25)
footer.pack(side="bottom", anchor="center")

menu_button = tk.Button(footer, text="Menu", font=NORMAL_FONT, command=show_menu_callback)
menu_button.pack(side="left", padx=5)        
add_pack_button = tk.Button(footer, text="Add Pack", font=NORMAL_FONT, command=show_menu_callback)
add_pack_button.pack(side="left", padx=5)
refresh_button = tk.Button(footer, text="Refresh", font=NORMAL_FONT, command=refresh_packs)
refresh_button.pack(side="left", padx=5)

root.mainloop()