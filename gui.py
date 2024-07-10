import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror
import sys
from PIL import Image, ImageDraw


import sv_ttk
import pystray
from pystray import MenuItem as item

import logic


class TimeSelector(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.hours_var = tk.StringVar(value="00")
        self.minutes_var = tk.StringVar(value="00")
        self.seconds_var = tk.StringVar(value="00")

        self.create_widgets()

    def create_widgets(self):
        self.hours_spinbox = ttk.Spinbox(self, from_=0, to=23, wrap=True, textvariable=self.hours_var, width=2, format="%02.0f")
        self.minutes_spinbox = ttk.Spinbox(self, from_=0, to=59, wrap=True, textvariable=self.minutes_var, width=2, format="%02.0f")
        self.seconds_spinbox = ttk.Spinbox(self, from_=0, to=59, wrap=True, textvariable=self.seconds_var, width=2, format="%02.0f")

        self.hours_spinbox.grid(row=0, column=0)
        tk.Label(self, text=":").grid(row=0, column=1)
        self.minutes_spinbox.grid(row=0, column=2)
        tk.Label(self, text=":").grid(row=0, column=3)
        self.seconds_spinbox.grid(row=0, column=4)

    def get_time(self):
        time = int(self.hours_var.get()) * 3600 + int(self.minutes_var.get()) * 60 + int(self.seconds_var.get())
        return time

def hibernate_submit() -> None:
    hibernate_time = time_selector.get_time()
    logic.sleep(hibernate_time)

def shutdown_submit() -> None:
    shutdown_time = time_selector.get_time()
    logic.shutdown(shutdown_time)

def reboot_submit() -> None:
    reboot_time = time_selector.get_time()
    logic.reboot(reboot_time)

def move_window_to_bottom_right(window):
    window.update_idletasks()

    window_width = window.winfo_width()
    window_height = window.winfo_height() + 32

    # Récupérer la largeur et la hauteur de l'écran
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calculer la position x et y pour que la fenêtre soit en bas à droite
    x = screen_width - window_width
    y = screen_height - window_height - 70

    # Déplacer la fenêtre
    window.geometry(f"{window_width}x{window_height}+{x}+{y}")

def create_image():
    # Crée une image de 16x16 pixels pour l'icône du tray
    width = 16
    height = 16
    image = Image.new('RGB', (width, height), (255, 255, 255))
    dc = ImageDraw.Draw(image)
    dc.rectangle((0, 0, width, height))
    return image

def quit_window(icon):
    icon.stop()
    root.destroy()

def show_window(icon):
    icon.stop()
    root.after(0, root.deiconify)

def hide_window():
    root.withdraw()
    image = create_image()
    menu = (item('Show', show_window), item('Quit', quit_window))
    icon = pystray.Icon("icon", image, "Timed Power State", menu)
    icon.run()


root = tk.Tk()
root.title("Timed Power State")

root.after(0, lambda: move_window_to_bottom_right(root))


time_selector = TimeSelector(root)
time_selector.pack(padx=10, pady=10)

button_frame = tk.Frame(root)
button_frame.pack(expand=True)

hibernate_button = ttk.Button(button_frame, text="Hibernate", command=hibernate_submit)
hibernate_button.pack(side=tk.LEFT, padx=5)

shutdown_button = ttk.Button(button_frame, text="Shutdown", command=shutdown_submit)
shutdown_button.pack(side=tk.LEFT, padx=5)

reboot_button = ttk.Button(button_frame, text="Reboot", command=reboot_submit)
reboot_button.pack(side=tk.LEFT, padx=5)

hide_button = ttk.Button(root, text="Hide to tray", command=hide_window)
hide_button.pack(pady=5)

sv_ttk.set_theme("light")

root.mainloop()

sys.exit()