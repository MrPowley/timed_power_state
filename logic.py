import time
import threading
import os

def execute(command):
    time.sleep(command['seconds'])
    os.system(command['cmd'])

def sleep(seconds: int):
    command = {"cmd": "rundll32.exe powrprof.dll,SetSuspendState 0,1,0","seconds": seconds}
    thread = threading.Thread(target=execute, args=(command,))
    thread.start()

def shutdown(seconds: int):
    command = {"cmd": "shutdown /f", "seconds": seconds}
    thread = threading.Thread(target=execute, args=(command,))
    thread.start()

def reboot(seconds: int):
    command = {"cmd": "shutdown /r", "seconds": seconds}
    thread = threading.Thread(target=execute, args=(command,))
    thread.start()