import tkinter as tk
class Skin_Pack_Card():
    file_name = ""
    def __init__(self, container, file_name: str, font):

        row = tk.Frame(container)
        row.pack(fill="x", pady=0, anchor="center")

        self.file_name = file_name
    
        card_label = tk.Label(row, text=file_name, anchor="w", justify="left", font=font, wraplength=500)
        card_label.pack(side="left")

        delete_button = tk.Button(row, text="Delete", command=self.delete_button_callback, anchor="e", font=font)
        delete_button.pack(side="right", padx=2)

    def delete_button_callback(self):
        print(f"Deleting {self.file_name}")