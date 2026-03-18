import tkinter as tk
import tkinter.font as tkFont
from constants import NORMAL_FONT_PERAMS
from components.check_box import CheckBox
class Skin_Pack_Card():
    file_name = ""

    def __init__(self, container, file_name: str, font):
        NORMAL_FONT = tkFont.Font(container, family=NORMAL_FONT_PERAMS[0], size=NORMAL_FONT_PERAMS[1])
        row = tk.Frame(container)
        row.pack(fill="x", pady=2, anchor="center")
        self.selected = tk.IntVar()
        
        self.file_name = file_name
        checkbox = CheckBox(row)
        checkbox.set_on_change(lambda: print(checkbox.isChecked))
        checkbox.pack(side="left", padx=2)

        card_label = tk.Label(row, text=file_name, anchor="w", justify="left", font=font, wraplength=500)
        card_label.pack(side="left")

    def delete_button_callback(self):
        print(f"Deleting {self.file_name}")
