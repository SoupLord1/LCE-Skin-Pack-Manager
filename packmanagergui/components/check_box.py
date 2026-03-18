import tkinter as tk
import tkinter.font as tkFont
from typing import Callable
class CheckBox(tk.Frame):
    isChecked: bool = False
    on_change: Callable = lambda: ()
    def __init__(self, parent, size=20):
        PADDING = size/10
        super().__init__(parent, width=size+PADDING*2, height=size+PADDING*2, bg="white", highlightbackground="black", highlightthickness=2)
        self.pack_propagate(False)
        self.checkbox = tk.Frame(self, width=size, height=size, bg="white")
        self.checkbox.pack(padx=PADDING, pady=PADDING)
        self.checkbox.bind("<Button-1>", self.on_click)
        self.bind("<Button-1>", self.on_click)

    def on_click(self, event):
        self.isChecked = not self.isChecked
        if (self.isChecked):
            self.checkbox.config(bg="gray")
        else:
            self.checkbox.config(bg="white")
        self.on_change()

    def set_on_change(self, on_change: Callable):
        self.on_change = on_change