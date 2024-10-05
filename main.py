import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror, showinfo
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
import pyautogui
import psutil

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

    

class Main:
    def __init__(self):
        # Set base variables
        self.PWD = getcwd()
        self.stop_thread = threading.Event()
        
        # Creating main window
        self.root = tk.Tk()
        self.root.title("Timed Power Sate")
        
        self.time_selector = TimeSelector(self.root)

        

        self.load_presets()

        # * Notebook Widgets =========================
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True)
        # * =============================================

        # Creating pages frames
        self.time_page = ttk.Frame(self.notebook)
        self.screen_page = ttk.Frame(self.notebook)
        self.system_page = ttk.Frame(self.notebook)
        self.preset_page = ttk.Frame(self.notebook)
        self.preset_button_frame = ttk.Frame(self.preset_page)
        self.preset_canvas_frame = ttk.Frame(self.preset_page)
        self.preset_canvas = tk.Canvas(self.preset_canvas_frame, scrollregion= (0, 0, 0, len(self.presets)*35), height=self.preset_page.winfo_height(), width=75) # get_window_size(root)[0],

        

        self.time_page.pack(fill='both', expand=True, padx=10, pady=10)
        self.screen_page.pack(fill='both', expand=True, padx=10, pady=10)
        self.system_page.pack(fill="both", expand=True, padx=10, pady=10)
        self.preset_page.pack(fill="both", expand=True, padx=10, pady=10)
        self.preset_canvas.pack(fill='both', expand=True, padx=10, pady=10)
        self.preset_button_frame.pack(fill="both", expand=True, side="left")
        self.preset_canvas_frame.pack(fill="both", expand=True, side="right")

        self.notebook.add(self.time_page, text='Time related')
        self.notebook.add(self.screen_page, text='Screen related')
        self.notebook.add(self.system_page, text='System related')
        self.notebook.add(self.preset_page, text='Presets')

        self.preset_canvas.bind("<MouseWheel>", lambda e: self.preset_canvas.yview_scroll(int(-e.delta/60), "units"))
        self.scrollbar = ttk.Scrollbar(self.preset_canvas, orient="vertical", command=self.preset_canvas.yview)
        self.preset_canvas.configure(yscrollcommand= self.scrollbar.set)
        self.scrollbar.place(relx=1, rely=0, relheight=1, anchor="ne")

        # * Time Page =========================
        self.time_selector = TimeSelector(self.time_page)
        self.time_selector.pack(padx=10, pady=10)
        # * ===================================

        # * Screen page ===========================================

        self.image_filedialog_frame = ttk.Frame(self.screen_page)
        self.image_filedialog_frame.pack(padx=10, pady=10)

        self.image_filedialog_button = ttk.Button(
            self.image_filedialog_frame, text="Open image", command=self.open_image)
        self.image_filedialog_button.pack(side="left", padx=10, pady=10)

        self.image_remove_filedialog_button = ttk.Button(
            self.image_filedialog_frame, text="Remove image", command=self.remove_image)
        self.image_remove_filedialog_button.pack(side="left", padx=10, pady=10)

        self.image_filedialog_var = tk.StringVar()
        self.image_filedialog_text = ttk.Label(
            self.image_filedialog_frame, textvariable=self.image_filedialog_var)
        self.image_filedialog_text.pack(side="right")

        # * =======================================================

        # * Sytem page =============================================
        self.command_frame = ttk.Frame(self.system_page)
        self.command_frame.pack(padx=10, pady=10)

        self.command_text = ttk.Label(
            self.command_frame,
            text="Pre-extinction command "
        )
        self.command_text.pack(side="left")

        self.command_var = tk.StringVar()
        self.command_entry = ttk.Entry(
            self.command_frame,
            textvariable=self.command_var
        )
        self.command_entry.pack(side="right", expand=True)

        self.text_catch_frame = ttk.Frame(self.system_page)
        self.text_catch_frame.pack(padx=10, pady=10)

        self.text_catch_text = ttk.Label(
            self.text_catch_frame,
            text="Catch text for extinction "
        )
        self.text_catch_text.pack(side="left")

        self.text_catch_var = tk.StringVar()
        self.text_catch_entry = ttk.Entry(
            self.text_catch_frame,
            textvariable=self.text_catch_var
        )
        self.text_catch_entry.pack(side="right", expand=True)
        # * ================================================

        # * Preset buttons =================================
        self.save_preset_button = ttk.Button(self.preset_button_frame, text="Save preset", command=self.save_preset)
        self.save_preset_button.pack(expand=True, padx=10, pady=10)
        # * ================================================

        # * Buttons ======================================
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(expand=True, pady=10, padx=10)

        self.hibernate_button = ttk.Button(
            self.button_frame,
            text="Hibernate",
            command=self.hibernate
            # command = lambda: print(str(command_var.get()))
        )
        self.hibernate_button.pack(side=tk.LEFT, padx=5)

        self.shutdown_button = ttk.Button(
            self.button_frame,
            text="Shutdown",
            command=self.shutdown
        )
        self.shutdown_button.pack(side=tk.LEFT, padx=5)

        self.reboot_button = ttk.Button(
            self.button_frame,
            text="Reboot",
            command=self.reboot
        )
        self.reboot_button.pack(side=tk.LEFT, padx=5)

        self.abort_button = ttk.Button(
            self.root,
            text="Abort",
            command=self.stop
        )
        self.abort_button.pack(padx=10, pady=10, side="left")


        self.hide_button = ttk.Button(
            self.root,
            text="Hide to tray",
            command=self.hide_window
        )
        self.hide_button.pack(padx=10, pady=10, side="right")

        # * ==============================================

        self.theme = "Light"
        sv_ttk.set_theme(self.theme)

        self.show_presets()
        self.root.after(0, self.move_window_to_bottom_right())


        self.root.mainloop()

        sys.exit()

    def show_presets(self):
        for y_coeff, preset_name in enumerate(self.presets):
            self.preset = self.presets[preset_name]
            button_preset = ttk.Button(self.preset_canvas_frame, text=preset_name, command=self.choose_preset)
            x = (self.preset_canvas.winfo_reqwidth() / 2)
            button_preset_window = self.preset_canvas.create_window(x, y_coeff*35+20, window=button_preset)

    def choose_preset(self):
        h, m, s = self.preset["hh"], self.preset["mm"], self.preset["ss"]
        self.time_selector.set_timestamp(h, m, s)

        command = self.preset["pre-extinction_command"]
        self.command_var.set(command)

        text_catch = self.preset["text_catch"]
        self.text_catch_var.set(text_catch)

        if "auto_hide_to_tray" in self.preset and self.preset["auto_hide_to_tray"]:
            self.hide_window()

    def move_window_to_bottom_right(self) -> None:
        self.root.update_idletasks()

        # Get screen and window dimensions
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        self.window_width = self.root.winfo_width()
        self.window_height = self.root.winfo_height() # + 30

        # Calculate new x and y coordinates for window
        x = self.screen_width - self.window_width - 8
        y = self.screen_height - self.window_height - 71

        # Move window
        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")
        print("window moved")

    def load_presets(self):
        # preset_file_path = tkinter.filedialog.askopenfilename(title="Ouvrir un fichier",filetypes=[('Json file','.json'),('all files','.*')])
        self.preset_file_path = join(self.PWD, "presets.json")
        if self.preset_file_path and exists(self.preset_file_path):
            with open(self.preset_file_path, "r") as f:
                self.presets = json.load(f)

    def save_preset(self):
        self.preset_name = tkinter.simpledialog.askstring(
            title="Save preset", prompt="Choose a name for your new preset")
        self.h, self.m,self.s = self.time_selector.get_timestamp()
        self.command = self.command_var.get()
        self.text_catch = self.text_catch_var.get()
        self.presets = self.load_presets()
        self.preset = {}
        self.preset["hh"], self.preset["mm"], self.preset["ss"] = self.h, self.m, self.s
        self.preset["pre-extinction_command"] = self.command
        self.preset["text_catch"] = self.text_catch
        self.presets[self.preset_name] = self.preset

        self.preset_file_path = join(self.PWD, "presets.json")
        with open(self.preset_file_path, "w") as f:
            json.dump(self.presets, f, indent=4)
        # presets = load_presets()
        # show_presets(presets, preset_canvas_frame, preset_canvas)

    def open_image(self):
        self.image_file = tkinter.filedialog.askopenfilename(title="Open file", filetypes=[('Image file', '.jpg .png'), ('all files', '.*')])
        self.image_filedialog_var.set(self.image_file)

    def remove_image(self):
        self.image_filedialog_var.set("")

    def quit_window(self):
        self.icon.stop()
        self.root.destroy()

    def show_window(self):
        self.icon.stop()
        self.root.after(0, self.root.deiconify)

    def hide_window(self, *args):
        self.root.withdraw()
        self.create_image()
        menu = (item('Show', self.show_window), item('Quit', self.quit_window))
        self.icon = pystray.Icon("icon", self.image, "Timed Power State", menu)
        self.icon.run()

    def create_image(self):
        # Crée une image de 16x16 pixels pour l'icône du tray
        width = 16
        height = 16
        self.image = Image.new('RGB', (width, height), (255, 255, 255))
        dc = ImageDraw.Draw(self.image)
        dc.rectangle((0, 0, width, height))

    def execute(self):
        showinfo("Power signal", f"Power signal successfully sent")
        # Get abort signal
        stopped = self.stop_thread.is_set()  # get the value
        print("exez1")
        # Wait for n seconds if abort signal was issued
        for _ in range(self.seconds):
            print("exec loop")
            # Waits n seconds then returns is the event was triggered
            stopped = self.stop_thread.wait(1)
            if stopped:
                print("exec stopped")
                break
        
        print(6)

        if not stopped:
            print("exec 2")
            # Custom command execution
            if self.command:
                print("exec cmd")
                # Start the pre-ext command
                thread = threading.Thread(target=self.execute_custom_command)
                thread.start()
                thread.join()

            # Find image availability
            if self.find_image:
                print("exec image")
                # Start the find_image
                thread = threading.Thread(target=self.find_image_on_screen)
                thread.start()
                thread.join()
        print(7)
        # Sends Power Signal
        # Get abort signal after pre-ext command ended
        stopped = self.stop_thread.is_set()
        if not stopped:
            # Send the extinction signal
            # subprocess.Popen(self.power_signal['signal'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("signaled")
            return
        else:
            print(8)
            showerror("Aborted", "Power signal aborted")
            return

    
    def kill(self):
        process = psutil.Process(self.process.pid)
        for proc in process.children(recursive=True):
            proc.kill()
        process.kill()

    def execute_custom_command(self) -> None:
        # Starting pre-ext command
        self.process = subprocess.Popen(
            self.command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=True)

        # While not aborted
        while not self.stop_thread.is_set():
            print(self.stop_thread.is_set())
            # Get process output
            output = self.process.stdout.readline()
            # If there's no output and the process hasn't finished, return
            if output == '' and self.process.poll() is not None:
                return
            # If the process sends an output and it hasn't finished
            if output:
                # Strip the output
                line_output = output.strip()
                # If user set a text_catch, look for it in the output
                if self.text_catch and self.text_catch in line_output:
                    break

        self.kill()

        
        # End process if aborted
        return

    def find_image_on_screen(self) -> None:
        location = None
        while not location:
            try:
                location = pyautogui.locateOnScreen(self.find_image)
            except pyautogui.ImageNotFoundException:
                pass
    
    def hibernate(self) -> None:
        self.stop_thread.clear()
        # Set the hibernate command, get the input time, pre-ext cmd, and text catch
        self.power_signal = "rundll32.exe powrprof.dll,SetSuspendState 0,1,0"
        self.seconds = self.time_selector.get_time()
        self.command = self.command_var.get()
        self.text_catch = self.text_catch_var.get()
        self.find_image = self.image_filedialog_var.get()
        # Execute the desired actions
        self.thread = threading.Thread(
            target=self.execute)
        self.thread.start()
        print(9)

    def shutdown(self) -> None:
        self.stop_thread.clear()
        # Set the shutdown command, get the input time, pre-ext cmd, and text catch
        self.power_signal = "shutdown /f"
        self.seconds = self.time_selector.get_time()
        self.command = self.command_var.get()
        self.text_catch = self.text_catch_var.get()
        self.find_image = self.image_filedialog_var.get()

        # Execute the desired actions
        self.thread = threading.Thread(
            target=self.execute)
        self.thread.start()

    def reboot(self) -> None:
        self.stop_thread.clear()
        # Set the reboot command, get the input time, pre-ext cmd, and text catch
        self.power_signal = "shutdown /r"
        self.seconds = self.time_selector.get_time()
        self.command = self.command_var.get()
        self.text_catch = self.text_catch_var.get()
        self.find_image = self.image_filedialog_var.get()
        # Execute the desired actions

        self.thread = threading.Thread(target=self.execute)
        self.thread.start()
        print("Rebooted")

    def stop(self) -> None:
        # Set abort signal
        self.stop_thread.set()
        # Wait for threads to end
        # self.thread.join()






















# * Menu widgets ============================
# menubar = tk.Menu(root)

# menu_presets = tk.Menu(menubar, tearoff=0)
# menu_presets.add_command(label="Charger les presets",
#                          command=lambda: load_presets(True))
# menu_presets.add_command(label="Sauvegarder le preset", command=save_preset)
# menubar.add_cascade(label="Presets", menu=menu_presets)

# sub_menu_presets = tk.Menu(menubar, tearoff=0)
# menu_presets.add_cascade(label="Presets", menu=sub_menu_presets)

# root.config(menu=menubar)
# * ==========================================












# icon = root.bind("<Unmap>", hide_window)

# root.withdraw() # hide


main = Main()
