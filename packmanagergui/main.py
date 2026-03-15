import tkinter as tk
from tkinter import filedialog
from constants import *


root: tk.Tk = tk.Tk()
root.title(app_title)
root.minsize(800, 400)
root.resizable(False, False)

def manage_packs_callback():
    manage_packs_frame.pack(fill="both", expand=True)
    menu_frame.pack_forget()

def select_game_folder_callback():
    folder_name = filedialog.askdirectory()
    print(folder_name)

menu_frame = tk.Frame(root)
manage_packs_frame = tk.Frame(root)

menu_frame.pack(fill="both", expand=True)

title: tk.Label = tk.Label(menu_frame, text=app_title)
title.pack()

game_folder_label = tk.Label()

select_game_folder_button = tk.Button(menu_frame, text="Select Game Folder", command=select_game_folder_callback)
select_game_folder_button.pack()

manage_packs_button = tk.Button(menu_frame, text="Manage Packs", command=manage_packs_callback)
manage_packs_button.pack()



root.mainloop()