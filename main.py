import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror
import tkinter.filedialog
import sys
import threading
import subprocess
from os import getcwd
from os.path import exists, join
import json
import tkinter.simpledialog

from PIL import Image, ImageDraw
import sv_ttk
import pystray
from pystray import MenuItem as item

# import logic

class TimeSelector(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.hours_var = tk.StringVar(value="00")
        self.minutes_var = tk.StringVar(value="00")
        self.seconds_var = tk.StringVar(value="00")

        self.create_widgets()

    def create_widgets(self):
        self.hours_spinbox = ttk.Spinbox(
            self, from_=0, to=23, wrap=True, textvariable=self.hours_var, width=2, format="%02.0f")
        self.minutes_spinbox = ttk.Spinbox(
            self, from_=0, to=59, wrap=True, textvariable=self.minutes_var, width=2, format="%02.0f")
        self.seconds_spinbox = ttk.Spinbox(
            self, from_=0, to=59, wrap=True, textvariable=self.seconds_var, width=2, format="%02.0f")

        self.hours_spinbox.grid(row=0, column=0)
        tk.Label(self, text=":").grid(row=0, column=1)
        self.minutes_spinbox.grid(row=0, column=2)
        tk.Label(self, text=":").grid(row=0, column=3)
        self.seconds_spinbox.grid(row=0, column=4)

    def get_time(self):
        time = int(self.hours_var.get()) * 3600 + \
            int(self.minutes_var.get()) * 60 + int(self.seconds_var.get())
        return time
    
    def get_timestamp(self):
        return (self.hours_var.get(), self.minutes_var.get(), self.seconds_var.get())

    def set_timestamp(self, h, m, s):
        self.hours_var.set(h)
        self.minutes_var.set(m)
        self.seconds_var.set(s)


class Logic:
    def __init__(self) -> None:
        pass

    def execute(self, power_signal):
        # Get abort signal
        stopped = stop_thread.is_set()  # get the value
        # Wait for n seconds if abort signal was issued
        for _ in range(power_signal["seconds"]):
            # Waits n seconds then returns is the event was triggered
            stopped = stop_thread.wait(1)
            if stopped:
                break

        if not stopped:
            # Start the pre-ext command
            thread = threading.Thread(target=execute_custom_command, args=(
                power_signal['command'], power_signal['text_catch']))
            thread.start()
            thread.join()

        # Get abort signal after pre-ext command ended
        stopped = stop_thread.is_set()
        if not stopped:
            # Send the extinction signal
            subprocess.Popen(
                power_signal['signal'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            print("Canceled")

    def hibernate(self):
        # Set the hibernate command, get the input time, pre-ext cmd, and text catch
        power_signal = {"signal": "rundll32.exe powrprof.dll,SetSuspendState 0,1,0",
                        "seconds": time_selector.get_time(),
                        "command": command_var.get(),
                        "text_catch": text_catch_var.get()}
        # Execute the desired actions
        self.thread = threading.Thread(
            target=logic.execute, args=(power_signal,))
        self.thread.start()

    def shutdown(self):
        # Set the shutdown command, get the input time, pre-ext cmd, and text catch
        power_signal = {"signal": "shutdown /f",
                        "seconds": time_selector.get_time(),
                        "command": command_var.get(),
                        "text_catch": text_catch_var.get()}
        # Execute the desired actions
        self.thread = threading.Thread(
            target=logic.execute, args=(power_signal,))
        self.thread.start()

    def reboot(self):
        # Set the reboot command, get the input time, pre-ext cmd, and text catch
        power_signal = {"signal": "shutdown /r",
                        "seconds": time_selector.get_time(),
                        "command": command_var.get(),
                        "text_catch": text_catch_var.get()}
        # Execute the desired actions
        self.thread = threading.Thread(
            target=logic.execute, args=(power_signal,))
        self.thread.start()
        print("Rebooted")

    def stop(self):
        # Set abort signal
        stop_thread.set()
        # Wait for threads to end
        self.thread.join()


def move_window_to_bottom_right(window):
    window.update_idletasks()

    window_width = window.winfo_width()
    window_height = window.winfo_height() + 32

    # Récupérer la largeur et la hauteur de l'écran
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calculer la position x et y pour que la fenêtre soit en bas à droite
    x = screen_width - window_width - 7
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


def hide_window(*args):
    root.withdraw()
    image = create_image()
    menu = (item('Show', show_window), item('Quit', quit_window))
    icon = pystray.Icon("icon", image, "Timed Power State", menu)
    icon.run()


def execute_custom_command(command: str, text_catch: str) -> None:
    # Starting pre-ext command
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

    # While not aborted
    while not stop_thread.is_set():
        # Get process output
        output = process.stdout.readline()
        # If there's no output and the process hasn't finished, return
        if output == '' and process.poll() is not None:
            return
        # If the process sends an output and it hasn't finished
        if output:
            # Strip the output
            line_output = output.strip()
            # If user set a text_catch, look for it in the output
            if text_catch and text_catch in line_output:
                break

    # End process if aborted
    process.terminate()
    return

def choose_preset(preset):
    h, m, s = preset["hh"], preset["mm"], preset["ss"]
    time_selector.set_timestamp(h, m, s)

    command = preset["pre-extinction_command"]
    command_var.set(command)

    text_catch = preset["text_catch"]
    text_catch_var.set(text_catch)

    if "auto_hide_to_tray" in preset and preset["auto_hide_to_tray"]:
        hide_window()

def load_presets(show_presets_bool) -> dict:
    # preset_file_path = tkinter.filedialog.askopenfilename(title="Ouvrir un fichier",filetypes=[('Json file','.json'),('all files','.*')])
    preset_file_path = join(PWD, "presets.json")
    if preset_file_path and exists(preset_file_path):
        with open(preset_file_path, "r") as f:
            presets = json.load(f)
            if show_presets_bool:
                show_presets(presets)
            return presets
    else:
        return None
        
def show_presets(presets):
    for preset in presets:
        sub_menu_presets.add_command(label=preset, command=lambda: choose_preset(presets[preset]))

def save_preset():
    name = tkinter.simpledialog.askstring(title="Save preset", prompt="Choose a name for your new preset")
    h, m, s = time_selector.get_timestamp()
    command = command_var.get()
    text_catch = text_catch_var.get()
    presets = load_presets(False)
    preset = {}
    preset["hh"], preset["mm"], preset["ss"] = h, m, s
    preset["pre-extinction_command"] = command
    preset["text_catch"] = text_catch
    presets[name] = preset

    preset_file_path = join(PWD, "presets.json")
    with open(preset_file_path, "w") as f:
        json.dump(presets, f, indent=4)


PWD = getcwd()

stop_thread = threading.Event()
logic = Logic()

root = tk.Tk()
root.title("Timed Power State")

root.after(0, lambda: move_window_to_bottom_right(root))

menubar = tk.Menu(root)

menu_presets = tk.Menu(menubar, tearoff=0)
menu_presets.add_command(label="Charger les presets", command=lambda: load_presets(True))
menu_presets.add_command(label="Sauvegarder le preset", command=save_preset)
menubar.add_cascade(label="Presets", menu=menu_presets)

sub_menu_presets = tk.Menu(menubar, tearoff=0)
menu_presets.add_cascade(label="Presets", menu=sub_menu_presets)

root.config(menu=menubar)


time_selector = TimeSelector(root)
time_selector.pack(padx=10, pady=10)


command_frame = ttk.Frame(root)
command_frame.pack(padx=10, pady=10)

command_text = ttk.Label(
    command_frame,
    text="Pre-extinction command "
)
command_text.pack(side="left")

command_var = tk.StringVar()
command_entry = ttk.Entry(
    command_frame,
    textvariable=command_var
)
command_entry.pack(side="right", expand=True)

text_catch_frame = ttk.Frame(root)
text_catch_frame.pack(padx=10, pady=10)

text_catch_text = ttk.Label(
    text_catch_frame,
    text="Catch text for extinction "
)
text_catch_text.pack(side="left")

text_catch_var = tk.StringVar()
text_catch_entry = ttk.Entry(
    text_catch_frame,
    textvariable=text_catch_var
)
text_catch_entry.pack(side="right", expand=True)


button_frame = tk.Frame(root)
button_frame.pack(expand=True)

hibernate_button = ttk.Button(
    button_frame,
    text="Hibernate",
    command=logic.hibernate
    # command = lambda: print(str(command_var.get()))
)
hibernate_button.pack(side=tk.LEFT, padx=5)

shutdown_button = ttk.Button(
    button_frame,
    text="Shutdown",
    command=lambda: logic.shutdown(time_selector.get_time(), command_var.get())
)
shutdown_button.pack(side=tk.LEFT, padx=5)

reboot_button = ttk.Button(
    button_frame,
    text="Reboot",
    command=lambda: logic.reboot(time_selector.get_time(), command_var.get())
)
reboot_button.pack(side=tk.LEFT, padx=5)

abort_button = ttk.Button(
    root,
    text="Abort",
    command=logic.stop
)
abort_button.pack(padx=10, pady=10, side="left")


hide_button = ttk.Button(
    root,
    text="Hide to tray",
    command=hide_window
)
hide_button.pack(padx=10, pady=10, side="right")

# icon = root.bind("<Unmap>", hide_window)

# root.withdraw() # hide


sv_ttk.set_theme("light")

root.mainloop()

sys.exit()
